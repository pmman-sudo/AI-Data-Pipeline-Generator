from app.llm.provider import generate
from app.security.validator import (
    extract_code_blocks,
    save_and_validate,
)


class GenerateAirflowSkill:

    def run(self, context: dict):

        table_name = context["table"]

        metadata = context.get("metadata")

        if not metadata:
            metadata = context["results"].get(
                "metadata_lookup"
            )

        if not metadata:
            raise ValueError(
                "GenerateAirflowSkill requires metadata."
            )

        columns = metadata["columns"]
        owners = metadata["owners"]
        tags = metadata["tags"]
        lineage = metadata["lineage"]

        print(
            f"Running Airflow generation for {table_name}"
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
You are a Senior Data Engineer.

Generate a production-ready Apache Airflow DAG.

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

- Create a valid Apache Airflow DAG.
- Use the table metadata above.
- Use the table name in the DAG.
- Include sensible task dependencies.
- Use modern Airflow syntax.
- Do not invent columns that are not present in the metadata.
- Return ONLY Python code.
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
        # VALIDATE + SAVE
        # ==================================================

        result = save_and_validate(
            table_name=table_name,
            generated_code=generated_code,
            iam_json=iam_json,
            artifact_type="airflow",
        )

        return result