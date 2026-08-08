from typing import Dict, Optional
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.skills.orchestrator import SkillOrchestrator
from app.planner.planner import Planner
from app.planner.executor import Executor

from app.datahub.client import MetadataService
from app.datahub.writeback import write_generation_metadata
from app.utils.package_generator import create_pipeline_package
import shutil
import time
from app.github.api import commit_generated_artifact
from app.llm.provider import generate
from app.security.validator import (
    extract_code_blocks,
    save_and_validate,
)

# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(title="AI Data Pipeline Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Request / Response Models
# ==========================================================

class GenerateRequest(BaseModel):
    task: str
    artifact_type: Optional[str] = None

    def get_inferred_type(self) -> str:
        """Infer artifact type from the user's request."""

        if self.artifact_type:
            return self.artifact_type.lower()

        task = self.task.lower()

        if "dbt" in task:
            return "dbt"

        if "sql" in task:
            return "sql"

        if "yaml" in task or "config" in task:
            return "yaml"

        if "readme" in task:
            return "readme"

        return "airflow"


class GenerateResponse(BaseModel):
    status: str
    artifact: str
    security_policy: str
    validation: Dict[str, str]
    commit: str = "pending"
    plan: list = []
    execution_results: dict = {}

# ==========================================================
# Health Endpoint
# ==========================================================

@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ==========================================================
# Metadata Endpoint
# ==========================================================

@app.get("/schema/{table}")
def get_schema(table: str):
    print(f"Received metadata request for {table}")

    metadata_service = MetadataService()

    return metadata_service.get_table_context(table)

@app.get("/download")
def download_file(path: str):

    if not os.path.exists(path):
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    return FileResponse(
        path,
        filename=os.path.basename(path)
    )

# ==========================================================
# Generate Endpoint
# ==========================================================

@app.post("/generate", response_model=GenerateResponse)
def generate_pipeline(req: GenerateRequest):

    # ------------------------------------------------------
    # Determine artifact type
    # ------------------------------------------------------

    artifact_type = req.artifact_type or "agent"


    template_map = {
        "airflow": "airflow_dag.txt",
        "dbt": "dbt_model.txt",
        "sql": "sql_query.txt",
        "yaml": "yaml_config.txt",
        "readme": "readme.txt",
    }

    all_artifacts = [
        "airflow",
        "sql",
        "dbt",
        "yaml",
        "readme",
    ]



    template_file = template_map.get(
        artifact_type,
        "airflow_dag.txt"
    )

    # ------------------------------------------------------
    # Very simple table extraction
    # ------------------------------------------------------

    table_name = "fct_users_created"

    words = req.task.split()

    if "for" in words:

        idx = words.index("for")

        if idx + 1 < len(words):

            candidate = words[idx + 1]

            if (
                candidate.lower() == "the"
                and idx + 2 < len(words)
            ):
                table_name = words[idx + 2]

            else:
                table_name = candidate

                
    # ======================================================
    # NEW AGENT PLANNER + EXECUTOR
    # ======================================================

    try:

        print("\n" + "=" * 80)
        print("AI AGENT PLANNER")
        print("=" * 80)

        # Create the planning agent
        planner = Planner()

        # Create the execution engine
        executor = Executor()

        # --------------------------------------------------
        # Create execution plan from user's request
        # --------------------------------------------------

        plan = planner.create_plan(req.task)

        print("\n========== EXECUTION PLAN ==========")

        for step in plan.steps:
            print(
                f"- {step.skill.value}: {step.reason}"
            )

        print("====================================\n")

        # --------------------------------------------------
        # Execute the plan
        # --------------------------------------------------

        results = executor.execute(
            plan,
            {
                "table": table_name,
                "task": req.task,
            }
        )

        print("\n========== AGENT EXECUTION RESULTS ==========")
        print(results)
        print("==============================================\n")

        # --------------------------------------------------
        # Find generated artifact
        # --------------------------------------------------

        artifact_path = None
        iam_path = "Not generated"
        validation = {
            "status": "unknown",
            "details": "No validation result returned"
        }
        commit_hash = "Not committed"

        # Generation skills that may produce artifacts
        generation_skills = [
            "generate_sql",
            "generate_airflow",
            "generate_dbt",
            "generate_yaml",
            "generate_readme",
            "generate_terraform",
            "generate_iam",
        ]

        for skill_name in generation_skills:

            if skill_name in results:

                generation_result = results[skill_name]

                if isinstance(generation_result, dict):

                    artifact_path = generation_result.get(
                        "artifact_path"
                    )

                    iam_path = generation_result.get(
                        "iam_path",
                        iam_path
                    )

                    generation_validation = generation_result.get(
                        "validation"
                    )

                    if generation_validation:
                        validation = generation_validation

                break

        # --------------------------------------------------
        # Get validation result from validate skill
        # --------------------------------------------------

        if "validate" in results:

            validate_result = results["validate"]

            if isinstance(validate_result, dict):

                validation = {
                    "status": validate_result.get(
                        "validation",
                        validate_result.get(
                            "status",
                            "unknown"
                        )
                    ),
                    "details": validate_result.get(
                        "details",
                        ""
                    )
                }

                if not artifact_path:
                    artifact_path = validate_result.get(
                        "artifact_path"
                    )

        # --------------------------------------------------
        # Get Git commit result
        # --------------------------------------------------

        if "git_commit" in results:

            git_result = results["git_commit"]

            if isinstance(git_result, dict):

                commit_hash = git_result.get(
                    "commit",
                    "Not committed"
                )

        # --------------------------------------------------
        # Get download result
        # --------------------------------------------------

        if "download_artifacts" in results:

            download_result = results[
                "download_artifacts"
            ]

            if isinstance(download_result, dict):

                artifacts = download_result.get(
                    "artifacts",
                    []
                )

                if artifacts and not artifact_path:
                    artifact_path = artifacts[0]

        # --------------------------------------------------
        # Safety check
        # --------------------------------------------------

        if not artifact_path:

            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Agent executed successfully but no artifact was returned.",
                    "plan": [
                        {
                            "skill": step.skill.value,
                            "reason": step.reason
                        }
                        for step in plan.steps
                    ],
                    "results": results,
                }
            )

        # --------------------------------------------------
        # Return API response
        # --------------------------------------------------

        return GenerateResponse(
            status="success",
            artifact=artifact_path,
            security_policy=iam_path,
            validation=validation,
            commit=commit_hash,
            plan=[
                {
                    "skill": step.skill.value,
                    "reason": step.reason,
                }
                for step in plan.steps
            ],
            execution_results=results,
        )

    except HTTPException:
        raise

    except Exception as e:

        print("\n========== AGENT ERROR ==========")
        print(str(e))
        print("=================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )