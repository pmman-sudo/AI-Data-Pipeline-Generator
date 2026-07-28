import json
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.datahub.client import MetadataService
from app.llm.provider import generate
from app.security.validator import extract_code_blocks, save_and_validate

app = FastAPI(title="AI Data Pipeline Generator")

# --- PYDANTIC MODELS FOR API DOCS ---
class GenerateRequest(BaseModel):
    task: str

class GenerateResponse(BaseModel):
    status: str
    artifact: str
    security_policy: str
    validation: Dict[str, str]
    commit: str = "pending" # We will wire up GitHub commits on Day 7

# --- ENDPOINTS ---
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/schema/{table}")
def get_schema(table: str):
    # This now uses the real Day 4 DataHub service instead of a mock
    metadata_service = MetadataService()
    return metadata_service.get_table_context(table)

@app.post("/generate", response_model=GenerateResponse)
def generate_pipeline(req: GenerateRequest):
    # Simple extraction: look for the word after 'for' or default to fct_users_created
    words = req.task.split()
    table_name = "fct_users_created"
    if "for" in words:
        idx = words.index("for")
        if idx + 1 < len(words):
            table_name = words[idx + 1].strip()

    try:
        # 1. Fetch prompt template
        with open("app/prompts/airflow_dag.txt", "r") as f:
            template = f.read()

        # 2. Get live DataHub metadata
        metadata_service = MetadataService()
        metadata = metadata_service.get_table_context(table_name)

        # 3. Inject metadata & call LLM (Groq)
        metadata_json = json.dumps(metadata.__dict__, indent=2)
        prompt = template.format(metadata_json=metadata_json)
        raw_response = generate(prompt)

        # 4. Extract code, save artifacts, and run validation
        python_code, iam_json = extract_code_blocks(raw_response)
        result = save_and_validate(table_name, python_code, iam_json)
        
        # Add the pending commit placeholder for Day 7
        result["commit"] = "pending"

        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))