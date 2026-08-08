from pathlib import Path

from app.llm.provider import generate


class GenerateReadmeSkill:

    def run(self, context: dict):

        table_name = context["table"]

        # Get metadata produced by metadata_lookup
        metadata = context["results"].get(
            "metadata_lookup"
        )

        if not metadata:
            raise ValueError(
                "generate_readme requires "
                "metadata_lookup to run first."
            )

        columns = metadata["columns"]
        owners = metadata["owners"]
        tags = metadata["tags"]
        lineage = metadata["lineage"]

        print(
            f"Running README generation for {table_name}"
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
        # LOAD EXISTING README PROMPT
        # ==================================================

        prompt_template = Path(
            "app/prompts/readme.txt"
        ).read_text()

        # ==================================================
        # BUILD PROMPT
        # ==================================================

        prompt = f"""
You are a Senior Data Engineer and Technical Writer.

{prompt_template}

DATASET

Table:
{table_name}

COLUMNS

{column_text}

OWNERS

{owners}

TAGS

{tags}

LINEAGE

{lineage}

USER REQUEST

{context.get("task", "")}

REQUIREMENTS

- Generate professional Markdown documentation.
- Document the supplied dataset.
- Include Purpose.
- Include Columns.
- Include Owners.
- Include Tags.
- Include Lineage.
- Include Example Usage.
- Use only the metadata provided.
- Do not invent columns.
- Do not invent owners.
- Do not invent tags.
- Do not invent lineage.
- Return ONLY Markdown.
- Do NOT wrap the response in a Markdown code fence.
"""

        # ==================================================
        # CALL GROQ
        # ==================================================

        generated_readme = generate(prompt)

        # ==================================================
        # CLEAN RESPONSE
        # ==================================================

        generated_readme = generated_readme.strip()

        if generated_readme.startswith("```markdown"):
            generated_readme = (
                generated_readme[
                    len("```markdown"):
                ]
                .strip()
            )

        if generated_readme.endswith("```"):
            generated_readme = (
                generated_readme[:-3]
                .strip()
            )

        # ==================================================
        # SAVE README
        # ==================================================

        output_dir = Path(
            "generated/readme"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        artifact_path = (
            output_dir
            / f"{table_name}_README.md"
        )

        artifact_path.write_text(
            generated_readme,
            encoding="utf-8"
        )

        # ==================================================
        # RETURN RESULT
        # ==================================================

        return {
            "status": "success",
            "artifact_path": str(
                artifact_path
            ),
            "artifact_type": "readme",
        }