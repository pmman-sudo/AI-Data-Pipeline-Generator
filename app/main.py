import json
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.datahub.client import MetadataService
from app.llm.provider import generate
from app.security.validator import extract_code_blocks, save_and_validate
from app.github.service import commit_and_push
from app.datahub.writeback import write_generation_metadata

app = FastAPI(title="AI Data Pipeline Generator")

# --- ADD THIS CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
# -----------------------------------

# --- PYDANTIC MODELS FOR API DOCS ---
class GenerateRequest(BaseModel):
    task: str
    artifact_type: Optional[str] = None

    def get_inferred_type(self) -> str:
        if self.artifact_type:
            return self.artifact_type.lower()
            
        task_lower = self.task.lower()
        if "dbt" in task_lower:
            return "dbt"
        elif "sql" in task_lower:
            return "sql"
        elif "yaml" in task_lower or "config" in task_lower:
            return "yaml"
        elif "readme" in task_lower:
            return "readme"
        else:
            return "airflow" # Default fallback

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
    # 1. Infer the artifact type using the method you added earlier
    artifact_type = req.get_inferred_type()
    
    # 2. Map the artifact type to the exact prompt template file
    template_map = {
        "airflow": "airflow_dag.txt",
        "dbt": "dbt_model.txt",
        "sql": "sql_query.txt",
        "yaml": "yaml_config.txt",
        "readme": "readme.txt"
    }
    template_file = template_map.get(artifact_type, "airflow_dag.txt")
    
    # Simple table extraction: look for the word after 'for', skipping 'the'
    words = req.task.split()
    table_name = "fct_users_created" # Default fallback
    
    if "for" in words:
        idx = words.index("for")
        if idx + 1 < len(words):
            next_word = words[idx + 1].strip()
            # If the next word is "the", grab the word after it instead
            if next_word.lower() == "the" and idx + 2 < len(words):
                table_name = words[idx + 2].strip()
            else:
                table_name = next_word
            
    try:
        # 3. Load the correct, dynamic prompt template
        with open(f"app/prompts/{template_file}", "r") as f:
            template = f.read()
            
        # Get live DataHub metadata
        metadata_service = MetadataService()
        metadata = metadata_service.get_table_context(table_name)
        
        # Inject metadata & call LLM
        metadata_json = json.dumps(metadata.__dict__, indent=2)
        prompt = template.format(metadata_json=metadata_json)
        raw_response = generate(prompt)
        
        # 4. Extract code, save, and validate WITH the artifact_type passed in
        generated_code, iam_json = extract_code_blocks(raw_response)
        
        # Call the updated save_and_validate
        result = save_and_validate(table_name, generated_code, iam_json, artifact_type)
        
        # Trigger GitHub auto-commit
        commit_hash = commit_and_push(req.task)
        
        # Trigger DataHub write-back
        write_generation_metadata(
            table_name=table_name, 
            artifact_path=result["artifact_path"], 
            prompt=prompt, 
            commit_hash=commit_hash
        )
        
        # 5. Format the final API response
        return GenerateResponse(
            status="success",
            artifact=result["artifact_path"],
            security_policy=result["iam_path"],
            validation=result["validation"],
            commit=commit_hash
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )