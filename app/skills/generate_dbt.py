from app.llm.provider import generate
from app.security.validator import (
    extract_code_blocks,
    save_and_validate,
)


class GenerateDBTSkill:

    def run(self, context: dict):

        table_name = context["table"]

        # Get metadata produced by metadata_lookup
        metadata = context["results"].get(
            "metadata_lookup"
        )

        if not metadata:
            raise ValueError(
                "generate_dbt requires "
                "metadata_lookup to run first."
            )

        columns = metadata["columns"]
        owners = metadata["owners"]
        tags = metadata["tags"]
        lineage = metadata["lineage"]

        print(
            f"Running DBT generation for {table_name}"
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
You are a Senior Analytics Engineer.

Generate a production-ready dbt model.

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

- Generate valid SQL for a dbt model.
- Use only columns present in the metadata.
- Use the supplied table name.
- Do not invent columns.
- Use dbt-compatible SQL.
- Follow analytics engineering best practices.
- Return ONLY SQL code.
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
            artifact_type="dbt",
        )

        return result