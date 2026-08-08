import json
import re

from app.llm.provider import generate
from app.planner.schemas import ExecutionPlan


class Planner:

    def create_plan(self, task: str) -> ExecutionPlan:

        prompt = f"""
You are an AI Planning Agent for an AI Data Engineering platform.

Your job is NOT to generate code.

Your job is ONLY to determine which skills should execute
and in what order.

======================================================
AVAILABLE SKILLS AND THEIR PURPOSES
======================================================

metadata_lookup
- Retrieves metadata about the requested dataset/table.
- Use this before generation skills when table metadata is required.

generate_sql
- Generates SQL queries or SQL scripts.
- Use when the user asks for SQL, database queries, SQL transformations,
  or SQL scripts.
- DO NOT use for Terraform, YAML, dbt, Airflow, or README requests.

generate_airflow
- Generates Apache Airflow DAGs.
- Use when the user asks for Airflow, DAGs, orchestration,
  scheduling, pipelines using Airflow, or workflow orchestration.

generate_dbt
- Generates dbt models.
- Use when the user explicitly asks for dbt, dbt models,
  analytics engineering models, or dbt SQL.

generate_yaml
- Generates YAML configuration files.
- Use when the user explicitly asks for YAML configuration.
- DO NOT use for Terraform or infrastructure-as-code requests.

generate_readme
- Generates README documentation.
- Use when the user asks for documentation, README files,
  dataset documentation, or project documentation.

generate_terraform
- Generates Terraform infrastructure configuration using HCL.
- Use when the user asks for Terraform, infrastructure-as-code,
  cloud infrastructure, Terraform resources, or .tf files.
- DO NOT use generate_yaml for Terraform requests.

generate_iam
- Generates IAM policies or identity/access-management configuration.
- Use when the user asks for IAM policies, permissions,
  roles, access policies, or cloud identity configuration.

validate
- Validates generated artifacts.
- Use after a generation skill.

git_commit
- Commits generated artifacts to Git.
- Use when the generated artifact should be committed to
  version control.

download_artifacts
- Makes generated artifacts available for download.
- Use when the user explicitly asks to download or retrieve
  generated artifacts.

======================================================
PLANNING RULES
======================================================

1. Select the skill that DIRECTLY matches the user's request.

2. Do not substitute one generation skill for another.

3. IMPORTANT:
   Terraform -> generate_terraform
   YAML -> generate_yaml
   SQL -> generate_sql
   dbt -> generate_dbt
   Airflow/DAG -> generate_airflow
   README/documentation -> generate_readme
   IAM/permissions -> generate_iam

4. If a generation skill requires table metadata, run:
   
   metadata_lookup

   before the generation skill.

5. After generating an artifact, normally run:

   validate

6. Only include git_commit when committing the generated artifact
   is appropriate or requested.

7. Only include download_artifacts when the user asks to download
   or retrieve the generated artifact.

8. Do not invent skills.

9. Do not generate code yourself.

10. Preserve the user's requested artifact type.

11. If the user explicitly asks to commit an artifact to Git,
    include git_commit immediately after validate.

12. Never run git_commit before validate.

13. Never run git_commit if validation failed.

======================================================
AVAILABLE SKILLS
======================================================

- metadata_lookup
- generate_sql
- generate_airflow
- generate_dbt
- generate_yaml
- generate_readme
- generate_terraform
- generate_iam
- validate
- git_commit
- download_artifacts

======================================================
EXAMPLE 1
======================================================

User request:

Generate SQL for customer_orders.

Correct plan:

{{
    "steps": [
        {{
            "skill": "metadata_lookup",
            "reason": "Need table schema"
        }},
        {{
            "skill": "generate_sql",
            "reason": "Generate SQL for customer_orders"
        }},
        {{
            "skill": "validate",
            "reason": "Validate generated SQL"
        }}
    ]
}}

======================================================
EXAMPLE 2
======================================================

User request:

Generate an Airflow DAG for customer_orders.

Correct plan:

{{
    "steps": [
        {{
            "skill": "metadata_lookup",
            "reason": "Need table schema"
        }},
        {{
            "skill": "generate_airflow",
            "reason": "Generate Airflow DAG"
        }},
        {{
            "skill": "validate",
            "reason": "Validate generated Airflow DAG"
        }}
    ]
}}

======================================================
EXAMPLE 3
======================================================

User request:

Generate a dbt model for customer_orders.

Correct plan:

{{
    "steps": [
        {{
            "skill": "metadata_lookup",
            "reason": "Need table schema"
        }},
        {{
            "skill": "generate_dbt",
            "reason": "Generate dbt model"
        }},
        {{
            "skill": "validate",
            "reason": "Validate generated dbt model"
        }}
    ]
}}

======================================================
EXAMPLE 4
======================================================

User request:

Generate YAML configuration for customer_orders.

Correct plan:

{{
    "steps": [
        {{
            "skill": "metadata_lookup",
            "reason": "Need table schema"
        }},
        {{
            "skill": "generate_yaml",
            "reason": "Generate YAML configuration"
        }},
        {{
            "skill": "validate",
            "reason": "Validate generated YAML"
        }}
    ]
}}

======================================================
EXAMPLE 5
======================================================

User request:

Generate Terraform infrastructure for customer_orders.

Correct plan:

{{
    "steps": [
        {{
            "skill": "metadata_lookup",
            "reason": "Need table schema"
        }},
        {{
            "skill": "generate_terraform",
            "reason": "Generate Terraform infrastructure configuration"
        }},
        {{
            "skill": "validate",
            "reason": "Validate generated Terraform configuration"
        }}
    ]
}}

User request:

Generate Terraform infrastructure for customer_orders and commit it to Git.

Correct plan:

{{
"steps": [
{{
"skill": "metadata_lookup",
"reason": "Need table schema"
}},
{{
"skill": "generate_terraform",
"reason": "Generate Terraform infrastructure configuration"
}},
{{
"skill": "validate",
"reason": "Validate generated Terraform configuration"
}},
{{
"skill": "git_commit",
"reason": "Commit generated Terraform configuration to Git"
}}
]
}}

======================================================
EXAMPLE 6
======================================================

User request:

Generate README documentation for customer_orders.

Correct plan:

{{
    "steps": [
        {{
            "skill": "metadata_lookup",
            "reason": "Need table schema"
        }},
        {{
            "skill": "generate_readme",
            "reason": "Generate README documentation"
        }},
        {{
            "skill": "validate",
            "reason": "Validate generated README"
        }}
    ]
}}


======================================================
USER REQUEST
======================================================

{task}

======================================================
OUTPUT FORMAT
======================================================

Return ONLY valid JSON.

The JSON must have this exact structure:

{{
    "steps": [
        {{
            "skill": "skill_name",
            "reason": "why this skill is required"
        }}
    ]
}}

Do not return Markdown.
Do not return ```json.
Do not explain your answer.
"""

        response = generate(prompt)

        print("\n========== RAW LLM RESPONSE ==========")
        print(response)
        print("======================================\n")

        response = response.strip()

        response = re.sub(r"^```json", "", response)
        response = re.sub(r"^```", "", response)
        response = re.sub(r"```$", "", response)

        match = re.search(r"\{.*\}", response, re.DOTALL)

        if not match:
            raise ValueError(
                f"Planner returned invalid JSON:\n{response}"
            )

        plan = json.loads(match.group())

        return ExecutionPlan.model_validate(plan)