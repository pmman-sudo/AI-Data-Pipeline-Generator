from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.datahub.client import MetadataService
from app.datahub.writeback import write_generation_metadata
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
    metadata_service = MetadataService()
    return metadata_service.get_table_context(table)


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

        metadata_service = MetadataService()
        metadata = metadata_service.get_table_context(table_name)

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
        # Generate Code
        # --------------------------------------------------

        raw_response = generate(prompt)

        # --------------------------------------------------
        # Extract Generated Code
        # --------------------------------------------------

        generated_code, iam_json = extract_code_blocks(
            raw_response
        )

        # --------------------------------------------------
        # Save & Validate
        # --------------------------------------------------

        result = save_and_validate(
            table_name=table_name,
            generated_code=generated_code,
            iam_json=iam_json,
            artifact_type=artifact_type,
        )

        # --------------------------------------------------
        # Commit to GitHub
        # --------------------------------------------------

        commit_hash = commit_and_push(req.task)

        # --------------------------------------------------
        # Write Metadata Back to DataHub
        # --------------------------------------------------

        write_generation_metadata(
            table_name=table_name,
            artifact_path=result["artifact_path"],
            prompt=prompt,
            commit_hash=commit_hash,
        )

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