import os
import re
import json
import subprocess

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


def save_and_validate(table_name: str, python_code: str, iam_json: str):
    """
    Saves extracted files to disk and runs syntax & security checks.
    """
    # Create target directories if they don't exist
    os.makedirs("generated/airflow", exist_ok=True)
    os.makedirs("generated/iam_policies", exist_ok=True)

    dag_path = f"generated/airflow/{table_name}_dag.py"
    iam_path = f"generated/iam_policies/{table_name}_policy.json"

    # 1. Save the Python DAG
    with open(dag_path, "w") as f:
        f.write(python_code)

    # 2. Save the IAM Policy JSON
    if iam_json:
        with open(iam_path, "w") as f:
            f.write(iam_json)

    # 3. Syntax Check
    syntax_status = "pass"
    try:
        compile(python_code, dag_path, "exec")
    except SyntaxError as e:
        syntax_status = f"fail: {str(e)}"

    # 4. Security Scan using Bandit
    bandit_status = "pass"
    try:
        result = subprocess.run(
            ["bandit", "-r", "generated/airflow/", "-f", "json", "-o", "bandit_report.json"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            bandit_status = "issues_found"
    except Exception as e:
        bandit_status = f"error: {str(e)}"

    return {
        "status": "success" if syntax_status == "pass" else "failed",
        "artifact": dag_path,
        "security_policy": iam_path,
        "validation": {
            "syntax": syntax_status,
            "bandit": bandit_status
        }
    }