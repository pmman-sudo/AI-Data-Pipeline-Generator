import re
import sqlparse
import yaml
import os
from datetime import datetime


def get_file_routing(table_name: str, artifact_type: str) -> str:
    # 1. Generate today's date for unique filenames
    date_str = datetime.now().strftime("%Y%m%d")

    # 2. Map each artifact type to its file extension and output folder
    routing_map = {
        "airflow": {"ext": "py", "folder": "airflow"},
        "dbt": {"ext": "sql", "folder": "dbt"},
        "sql": {"ext": "sql", "folder": "sql"},
        "yaml": {"ext": "yaml", "folder": "configs"},
        "readme": {"ext": "md", "folder": "configs"},
        "terraform": {"ext": "tf", "folder": "terraform"},
    }

    mapping = routing_map.get(
        artifact_type,
        {"ext": "txt", "folder": "configs"}
    )

    # 3. Build the output filename
    filename = (
        f"{table_name}_{artifact_type}_{date_str}."
        f"{mapping['ext']}"
    )

    # 4. Build the full output path
    file_path = os.path.join(
        "generated",
        mapping["folder"],
        filename
    )

    # 5. Create the directory if it doesn't already exist
    os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True
    )

    return file_path


def extract_code_blocks(llm_response: str):
    """
    Extract generated code and IAM policy from the LLM response.

    Supports:
    - Python
    - SQL
    - YAML
    - Markdown
    - Generic fenced code blocks

    Falls back to the raw response if no code fences exist.
    """

    # 1. Look for any supported fenced code block
    code_match = re.search(
        r"```(?:python|sql|yaml|yml|markdown|md)?\s*(.*?)```",
        llm_response,
        re.DOTALL,
    )

    # 2. Look specifically for a JSON IAM policy
    json_match = re.search(
        r"```json\s*(.*?)```",
        llm_response,
        re.DOTALL,
    )

    # 3. If no fenced block exists, assume the entire response is code
    generated_code = (
        code_match.group(1).strip()
        if code_match
        else llm_response.strip()
    )

    # 4. Use an empty JSON object if no IAM policy was returned
    iam_json = (
        json_match.group(1).strip()
        if json_match
        else "{}"
    )

    return generated_code, iam_json


def save_and_validate(
    table_name: str,
    generated_code: str,
    iam_json: str,
    artifact_type: str = "airflow",
):
    """
    Save generated files and run artifact validation.
    """

    # 1. Determine where the generated artifact should be stored
    artifact_path = get_file_routing(
        table_name,
        artifact_type
    )

    # 2. Save the generated artifact
    with open(
        artifact_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(generated_code)

    # 3. Save the generated IAM policy
    iam_dir = "generated/iam_policies"

    os.makedirs(
        iam_dir,
        exist_ok=True
    )

    iam_path = os.path.join(
        iam_dir,
        f"{table_name}_{artifact_type}_policy.json"
    )

    with open(
        iam_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(iam_json)

    # 4. Validate the generated artifact
    validation_results = validate_artifact(
        generated_code,
        artifact_type
    )

    # 5. Return all generated file locations and validation results
    return {
        "artifact_path": artifact_path,
        "iam_path": iam_path,
        "validation": validation_results
    }


def validate_artifact(
    code_string: str,
    artifact_type: str
) -> dict:
    """
    Validate generated artifacts before presenting them to the user.
    """

    validation_result = {
        "status": "pass",
        "details": "Validation successful"
    }

    try:

        # 1. Remove unnecessary whitespace
        code_string = code_string.strip()

        # 2. Ensure the artifact isn't empty
        if not code_string:
            raise ValueError(
                "Generated artifact is empty."
            )

        # 3. Validate Python syntax
        if artifact_type == "airflow":

            compile(
                code_string,
                "<string>",
                "exec"
            )

        # 4. Validate SQL syntax
        elif artifact_type in ["sql", "dbt"]:

            parsed = sqlparse.parse(
                code_string
            )

            if len(parsed) == 0:
                raise ValueError(
                    "Could not parse SQL statements."
                )

        # 5. Validate YAML syntax
        elif artifact_type == "yaml":

            yaml.safe_load(
                code_string
            )

        # 6. Markdown files do not require syntax validation
        elif artifact_type == "readme":
            pass

        # 7. Basic Terraform validation
        elif artifact_type == "terraform":

            if (
                "resource" not in code_string
                and "terraform" not in code_string
            ):
                raise ValueError(
                    "Generated Terraform does not appear to contain "
                    "Terraform configuration."
                )


    except Exception as e:

        validation_result["status"] = "fail"
        validation_result["details"] = str(e)

    return validation_result