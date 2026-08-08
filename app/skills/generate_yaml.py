from app.llm.provider import generate
from app.security.validator import (
    extract_code_blocks,
    save_and_validate,
)


class GenerateYAMLSkill:

    def run(self, context: dict):

        table_name = context["table"]

        # ==================================================
        # GET METADATA
        # ==================================================

        metadata = context["results"].get(
            "metadata_lookup"
        )

        if not metadata:
            raise ValueError(
                "generate_yaml requires "
                "metadata_lookup to run first."
            )

        columns = metadata["columns"]
        owners = metadata["owners"]
        tags = metadata["tags"]
        lineage = metadata["lineage"]

        print(
            f"Running YAML generation for {table_name}"
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

Generate a production-ready YAML configuration
for the data pipeline associated with this table.

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

- Generate valid YAML.
- Use the supplied table name.
- Use only columns present in the metadata.
- Do not invent columns.
- Include useful pipeline configuration.
- Include table metadata.
- Include owners and tags.
- Return ONLY YAML.
- Do NOT use Markdown.
- Do NOT explain the configuration.
"""

        # ==================================================
        # CALL GROQ
        # ==================================================

        raw_response = generate(prompt)

        # ==================================================
        # EXTRACT GENERATED CONTENT
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
            artifact_type="yaml",
        )

        return result