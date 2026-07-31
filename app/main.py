from typing import Dict, Optional
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.datahub.client import MetadataService
from app.datahub.writeback import write_generation_metadata
from app.utils.package_generator import create_pipeline_package
import shutil
import time
from app.github.service import commit_and_push
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

    artifact_type = req.get_inferred_type()


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

                
    package_dir = None

    if artifact_type == "all":
        package_dir = create_pipeline_package(table_name)

    try:

        # --------------------------------------------------
        # Load prompt template
        # --------------------------------------------------

        with open(
            f"app/prompts/{template_file}",
            "r",
            encoding="utf-8"
        ) as f:
            template = f.read()

        # --------------------------------------------------
        # Load DataHub Metadata
        # --------------------------------------------------

        start = time.time()

        metadata_service = MetadataService()
        try:
            metadata = metadata_service.get_table_context(table_name)
        except Exception:
            metadata = MetadataService().get_table_context("fct_users_created")

        print(f"Metadata lookup: {time.time() - start:.2f}s")
        
        # --------------------------------------------------
        # Format Metadata
        # --------------------------------------------------

        columns = "\n".join(
            f"- {col['name']} ({col['type']})"
            for col in metadata.columns
        ) if metadata.columns else "No columns found."

        owners = ", ".join(metadata.owners) if metadata.owners else "Unknown"

        tags = ", ".join(metadata.tags) if metadata.tags else "None"

        lineage = "\n".join(metadata.lineage) if metadata.lineage else "None"

        # --------------------------------------------------
        # Artifact Description
        # --------------------------------------------------

        artifact_description = {
            "sql": "ANSI SQL",
            "airflow": "Apache Airflow DAG",
            "dbt": "dbt Model",
            "yaml": "YAML Configuration",
            "readme": "README Documentation",
        }.get(
            artifact_type,
            artifact_type
        )

        # --------------------------------------------------
        # Build Rich Prompt
        # --------------------------------------------------

        prompt = f"""
You are a Senior Data Engineer.

Your job is to generate production-ready code.

==================================================

USER REQUEST

{req.task}

==================================================

ARTIFACT TYPE

{artifact_description}

==================================================

TABLE

{metadata.name}

==================================================

COLUMNS

{columns}

==================================================

OWNERS

{owners}

==================================================

TAGS

{tags}

==================================================

UPSTREAM LINEAGE

{lineage}

==================================================

GENERATION INSTRUCTIONS

{template}

==================================================

RULES

- Return ONLY executable code.
- Do NOT use markdown.
- Do NOT explain anything.
- Follow production best practices.
- Ensure the code is syntactically correct.
- Include no placeholder text.
"""

        # --------------------------------------------------
        # Debug Prompt
        # --------------------------------------------------

        print("\n" + "=" * 80)
        print("PROMPT SENT TO GROQ")
        print("=" * 80)
        print(prompt)
        print("=" * 80 + "\n")

        # --------------------------------------------------
        # Generate One or Multiple Artifacts
        # --------------------------------------------------

        if artifact_type == "all":

            generated_files = []

            for current_type in all_artifacts:

                current_template = template_map[current_type]

                with open(
                    f"app/prompts/{current_template}",
                    "r",
                    encoding="utf-8"
                ) as f:
                    current_template_text = f.read()

                current_description = {
                    "sql": "ANSI SQL",
                    "airflow": "Apache Airflow DAG",
                    "dbt": "dbt Model",
                    "yaml": "YAML Configuration",
                    "readme": "README Documentation",
                }[current_type]

                current_prompt = f"""
        You are a Senior Data Engineer.

        Generate production-ready code.

        USER REQUEST

        {req.task}

        ARTIFACT TYPE

        {current_description}

        TABLE

        {metadata.name}

        COLUMNS

        {columns}

        OWNERS

        {owners}

        TAGS

        {tags}

        UPSTREAM LINEAGE

        {lineage}

        GENERATION INSTRUCTIONS

        {current_template_text}

        Return ONLY executable code.
        """

                raw_response = generate(current_prompt)

                generated_code, iam_json = extract_code_blocks(raw_response)

                result = save_and_validate(
                    table_name=table_name,
                    generated_code=generated_code,
                    iam_json=iam_json,
                    artifact_type=current_type,
                )

                folder_map = {
                    "airflow": "airflow",
                    "sql": "sql",
                    "dbt": "dbt",
                    "yaml": "configs",
                    "readme": "configs",
                }

                destination = os.path.join(
                    package_dir,
                    folder_map[current_type],
                    os.path.basename(result["artifact_path"])
                )

                shutil.copy(
                    result["artifact_path"],
                    destination
                )

                iam_destination = os.path.join(
                    package_dir,
                    "iam",
                    os.path.basename(result["iam_path"])
                )

                shutil.copy(
                    result["iam_path"],
                    iam_destination
                )


                generated_files.append(result["artifact_path"])

            # --------------------------------------------
            # Create ZIP after every artifact has been copied
            # --------------------------------------------

            zip_path = shutil.make_archive(
                package_dir,
                "zip",
                package_dir
            )

            result = {
                "artifact_path": zip_path,
                "iam_path": "generated/iam_policies",
                "validation": {
                    "status": "pass",
                    "details": f"{len(generated_files)} artifacts generated successfully."
                }
            }

        else:

            start = time.time()

            raw_response = generate(prompt)

            print(f"LLM generation: {time.time() - start:.2f}s")

            generated_code, iam_json = extract_code_blocks(
                raw_response
            )

            start = time.time()

            result = save_and_validate(
                table_name=table_name,
                generated_code=generated_code,
                iam_json=iam_json,
                artifact_type=artifact_type,
            )

            print(f"Validation: {time.time() - start:.2f}s")
             
        # --------------------------------------------------
        # Commit to GitHub
        # --------------------------------------------------
        


        start = time.time()

        try:
            commit_hash = commit_and_push(req.task)
        except Exception as e:
            print(f"GitHub commit skipped: {e}")
            commit_hash = "Not committed"

        print(f"GitHub: {time.time() - start:.2f}s") 

        # --------------------------------------------------
        # Write Metadata Back to DataHub
        # --------------------------------------------------
        
        
        
        start = time.time()

        DATAHUB_GMS = os.getenv("DATAHUB_GMS")
        
        print(f"DATAHUB_GMS={DATAHUB_GMS!r}")

        if DATAHUB_GMS:
            try:
                write_generation_metadata(
                    table_name=table_name,
                    artifact_path=result["artifact_path"],
                    prompt=prompt,
                    commit_hash=commit_hash,
                )
            except Exception as e:
                print(f"DataHub writeback skipped: {e}")
        else:
            print("Skipping DataHub writeback (DATAHUB_GMS not configured).")

        print(f"Writeback: {time.time() - start:.2f}s")

        # --------------------------------------------------
        # Return Response
        # --------------------------------------------------

        return GenerateResponse(
            status="success",
            artifact=result["artifact_path"],
            security_policy=result["iam_path"],
            validation=result["validation"],
            commit=commit_hash,
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )