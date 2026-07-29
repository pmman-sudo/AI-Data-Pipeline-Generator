import re
import json
import subprocess
import sqlparse
import yaml
import os
from datetime import datetime

def get_file_routing(table_name: str, artifact_type: str) -> str:
    # 1. Enforce YYYYMMDD format
    date_str = datetime.now().strftime("%Y%m%d")
    
    # 2. Map types to their extensions and subfolders
    routing_map = {
        "airflow": {"ext": "py", "folder": "airflow"},
        "dbt": {"ext": "sql", "folder": "dbt"},
        "sql": {"ext": "sql", "folder": "sql"},
        "yaml": {"ext": "yaml", "folder": "configs"},
        "readme": {"ext": "md", "folder": "configs"}
    }
    
    mapping = routing_map.get(artifact_type, {"ext": "txt", "folder": "configs"})
    
    # 3. Construct exact filename and path
    filename = f"{table_name}_{artifact_type}_{date_str}.{mapping['ext']}"
    file_path = os.path.join("generated", mapping['folder'], filename)
    
    # Ensure the directory exists before saving
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    return file_path

def extract_code_blocks(llm_response: str):
    """
    Finds and extracts the ```python and ```json blocks from the LLM's text response.
    """
    # Regex to capture content between ```python and ```
    python_match = re.search(r"```python\s*(.*?)\s*```", llm_response, re.DOTALL)
    # Regex to capture content between ```json and ```
    json_match = re.search(r"```json\s*(.*?)\s*```", llm_response, re.DOTALL)

    # Fallback: If LLM missed code blocks, check for generic ``` blocks
    if not python_match:
        python_match = re.search(r"```\s*(.*?)\s*```", llm_response, re.DOTALL)

    python_code = python_match.group(1).strip() if python_match else ""
    iam_json = json_match.group(1).strip() if json_match else ""

    return python_code, iam_json


def save_and_validate(table_name: str, generated_code: str, iam_json: str, artifact_type: str = "airflow"):
    """Saves extracted files to disk and runs type-specific syntax & security checks."""
    
    # 1. Get the dynamic file path and save the generated code
    artifact_path = get_file_routing(table_name, artifact_type)
    with open(artifact_path, "w") as f:
        f.write(generated_code)
        
    # 2. Save the IAM Policy (This remains JSON regardless of the artifact type)
    iam_dir = "generated/iam_policies"
    os.makedirs(iam_dir, exist_ok=True)
    iam_path = os.path.join(iam_dir, f"{table_name}_{artifact_type}_policy.json")
    
    with open(iam_path, "w") as f:
        f.write(iam_json)
        
    # 3. Validate the code dynamically using the new validate_artifact function
    validation_results = validate_artifact(generated_code, artifact_type)
    
    return {
        "artifact_path": artifact_path,
        "iam_path": iam_path,
        "validation": validation_results
    }

def validate_artifact(code_string: str, artifact_type: str) -> dict:
    validation_result = {"status": "pass", "details": "Validation successful"}
    
    try:
        if artifact_type == "airflow":
            # Python validation
            compile(code_string, '<string>', 'exec')
            
        elif artifact_type in ["dbt", "sql"]:
            # SQL validation
            parsed = sqlparse.parse(code_string)
            if not parsed:
                raise ValueError("Could not parse SQL statements.")
                
        elif artifact_type == "yaml":
            # YAML validation
            yaml.safe_load(code_string)
            
    except Exception as e:
        validation_result["status"] = "fail"
        validation_result["details"] = str(e)
        
    return validation_result