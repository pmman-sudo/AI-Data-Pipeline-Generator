from app.llm.provider import generate
from app.security.validator import (
    extract_code_blocks,
    save_and_validate,
)


class GenerateSQLSkill:

    def run(self, context: dict):

        table_name = context["table"]

        metadata = context.get("metadata")

        if not metadata:
            metadata = context["results"].get(
                "metadata_lookup"
            )

        if not metadata:
            raise ValueError(
                "generate_sql requires metadata_lookup to run first."
            )

        columns = metadata["columns"]
        owners = metadata["owners"]
        tags = metadata["tags"]
        lineage = metadata["lineage"]

        print(
            f"Running SQL generation for {table_name}"
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

Generate production-ready ANSI SQL.

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

- Generate valid ANSI SQL.
- Use only columns present in the metadata.
- Use the supplied table name.
- Do not invent columns.
- Follow SQL best practices.
- Return ONLY SQL code.
- Do NOT use Markdown.
- Do NOT explain the SQL.
"""

        # ==================================================
        # CALL GROQ
        # ==================================================

        raw_response = generate(prompt)

        # ==================================================
        # EXTRACT CODE
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
            artifact_type="sql",
        )

        return result 