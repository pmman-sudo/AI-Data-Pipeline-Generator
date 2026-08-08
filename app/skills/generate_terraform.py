from app.llm.provider import generate
from app.security.validator import (
    extract_code_blocks,
    save_and_validate,
)


class GenerateTerraformSkill:

    def run(self, context: dict):

        table_name = context["table"]

        metadata = context.get("metadata")

        if not metadata:
            metadata = context["results"].get(
                "metadata_lookup"
            )

        if not metadata:
            raise ValueError(
                "GenerateTerraformSkill requires metadata."
            )

        columns = metadata["columns"]
        owners = metadata["owners"]
        tags = metadata["tags"]
        lineage = metadata["lineage"]

        print(
            f"Running Terraform generation for {table_name}"
        )

        # ==================================================
        # FORMAT COLUMNS
        # ==================================================

        column_text = "\n".join(
            f"- {column['name']} "
            f"({column['type']}): "
            f"{column.get('description', '')}"
            for column in columns
        )

        # ==================================================
        # BUILD PROMPT
        # ==================================================

        prompt = f"""
You are a Senior Cloud/DevOps Engineer.

Generate production-ready Terraform configuration.

TABLE

{table_name}

COLUMNS

{column_text}

OWNERS

{owners}

TAGS

{tags}

UPSTREAM LINEAGE

{lineage}

USER REQUEST

{context.get("task", "")}

REQUIREMENTS

- Generate valid Terraform configuration.
- Use Terraform HCL syntax.
- Follow infrastructure-as-code best practices.
- Use the supplied metadata where relevant.
- Use the supplied table name where relevant.
- Do not invent database columns.
- Include sensible variables where appropriate.
- Include useful resource naming.
- Do not include secrets or hardcoded credentials.
- Return ONLY Terraform code.
- Do NOT use Markdown.
- Do NOT explain the code.
"""

        # ==================================================
        # CALL GROQ
        # ==================================================

        raw_response = generate(prompt)

        # ==================================================
        # EXTRACT GENERATED CODE
        # ==================================================

        generated_code, iam_json = extract_code_blocks(
            raw_response
        )

        # ==================================================
        # SAVE + VALIDATE
        # ==================================================

        result = save_and_validate(
            table_name=table_name,
            generated_code=generated_code,
            iam_json=iam_json,
            artifact_type="terraform",
        )

        return result
