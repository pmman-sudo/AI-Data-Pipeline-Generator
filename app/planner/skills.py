from app.datahub.client import MetadataService
from app.skills.generate_airflow import GenerateAirflowSkill
from app.skills.generate_sql import GenerateSQLSkill
from app.skills.generate_dbt import GenerateDBTSkill
from app.skills.generate_yaml import GenerateYAMLSkill
from app.skills.generate_readme import GenerateReadmeSkill
from app.skills.generate_terraform import GenerateTerraformSkill
from app.github.api import commit_generated_artifact

class SkillRegistry:

    # ======================================================
    # SKILL LOOKUP
    # ======================================================

    def get(self, skill_name: str):

        skill_map = {
            "metadata_lookup": self.metadata_lookup,
            "generate_airflow": self.generate_airflow,
            "generate_sql": self.generate_sql,
            "generate_dbt": self.generate_dbt,
            "generate_yaml": self.generate_yaml,
            "generate_readme": self.generate_readme,
            "generate_terraform": self.generate_terraform,
            "generate_iam": self.generate_iam,
            "validate": self.validate,
            "git_commit": self.git_commit,
            "download_artifacts": self.download_artifacts,
        }

        if skill_name not in skill_map:
            raise ValueError(
                f"Unknown skill: {skill_name}"
            )

        return skill_map[skill_name]

    # ======================================================
    # METADATA LOOKUP
    # ======================================================

    def metadata_lookup(self, context):

        print("Executing metadata_lookup")

        table = context["table"]

        metadata = MetadataService().get_table_context(
            table
        )

        return {
            "status": "success",
            "table": metadata.name,
            "columns": metadata.columns,
            "owners": metadata.owners,
            "tags": metadata.tags,
            "lineage": metadata.lineage,
        }

    # ======================================================
    # GENERATE AIRFLOW
    # ======================================================

    def generate_airflow(self, context):

        print("Executing generate_airflow")

        metadata = context["results"].get(
            "metadata_lookup"
        )

        if not metadata:
            raise ValueError(
                "generate_airflow requires "
                "metadata_lookup to run first."
            )

        # Pass metadata into the real Airflow skill
        skill_context = {
            **context,
            "metadata": metadata,
        }

        return GenerateAirflowSkill().run(
            skill_context
        )

    # ======================================================
    # GENERATE SQL
    # ======================================================

    def generate_sql(self, context):

        print("Executing generate_sql")

        metadata = context["results"].get(
            "metadata_lookup"
        )

        if not metadata:
            raise ValueError(
                "generate_sql requires "
                "metadata_lookup to run first."
            )

        skill_context = {
            **context,
            "metadata": metadata,
        }

        return GenerateSQLSkill().run(
            skill_context
        )

    # ======================================================
    # GENERATE DBT
    # ======================================================

    def generate_dbt(self, context):

        print("Executing generate_dbt")

        metadata = context["results"].get(
            "metadata_lookup"
        )

        if not metadata:
            raise ValueError(
                "generate_dbt requires "
                "metadata_lookup to run first."
            )

        skill_context = {
            **context,
            "metadata": metadata,
        }

        return GenerateDBTSkill().run(
            skill_context
        )

    # ======================================================
    # GENERATE YAML
    # ======================================================

    def generate_yaml(self, context):

        print("Executing generate_yaml")

        metadata = context["results"].get(
            "metadata_lookup"
        )

        if not metadata:
            raise ValueError(
                "generate_yaml requires "
                "metadata_lookup to run first."
            )

        skill_context = {
            **context,
            "metadata": metadata,
        }

        return GenerateYAMLSkill().run(
            skill_context
        )

    # ======================================================
    # GENERATE README
    # ======================================================

    def generate_readme(self, context):

        print("Executing generate_readme")

        return GenerateReadmeSkill().run(
            context
        )

    # ======================================================
    # GENERATE TERRAFORM
    # ======================================================

    def generate_terraform(self, context):

        print("Executing generate_terraform")

        metadata = context["results"].get(
            "metadata_lookup"
        )

        if not metadata:
            raise ValueError(
                "generate_terraform requires "
                "metadata_lookup to run first."
            )

        skill_context = {
            **context,
            "metadata": metadata,
        }

        return GenerateTerraformSkill().run(
            skill_context
        )

    # ======================================================
    # GENERATE IAM
    # ======================================================

    def generate_iam(self, context):

        print("Executing generate_iam")

        return {
            "status": "success",
            "artifact": "iam_policy.json",
        }

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(self, context):

        print("Executing validate")

        results = context.get("results", {})

        # Find the artifact generated by the previous skill
        artifact_result = None
        artifact_skill = None

        for skill_name, result in reversed(results.items()):

            if isinstance(result, dict) and result.get("artifact_path"):
                artifact_result = result
                artifact_skill = skill_name
                break

        if not artifact_result:
            raise ValueError(
                "validate requires a previously generated artifact."
            )

        artifact_path = artifact_result["artifact_path"]

        print(
            f"Validating artifact from {artifact_skill}: "
            f"{artifact_path}"
        )

        # Determine artifact type from the generating skill
        artifact_type_map = {
            "generate_sql": "sql",
            "generate_airflow": "airflow",
            "generate_dbt": "dbt",
            "generate_yaml": "yaml",
            "generate_readme": "readme",
            "generate_terraform": "terraform",
        }

        artifact_type = artifact_type_map.get(
            artifact_skill
        )

        if not artifact_type:
            raise ValueError(
                f"Cannot determine artifact type for "
                f"{artifact_skill}"
            )

        # Read the generated artifact
        with open(
            artifact_path,
            "r",
            encoding="utf-8"
        ) as f:
            generated_code = f.read()

            # Import the real validator
            from app.security.validator import validate_artifact

            validation_result = validate_artifact(
                generated_code,
                artifact_type
            )

            return {
                "status": "success"
                if validation_result["status"] == "pass"
                else "failed",

                "validation": validation_result["status"],

                "details": validation_result["details"],

                "artifact_path": artifact_path,

                "artifact_type": artifact_type,
            }


    # ======================================================
    # GIT COMMIT
    # ======================================================

    def git_commit(self, context):

        print("Executing git_commit")

        results = context.get("results", {})

        # Find the generated artifact
        artifact_result = None

        for skill_name, result in results.items():

            if isinstance(result, dict) and "artifact_path" in result:
                artifact_result = result
                break

        # No artifact = cannot commit
        if not artifact_result:

            return {
                "status": "failed",
                "reason": "No generated artifact found to commit."
            }

        # Check validation result
        validation_result = results.get("validate")

        if not validation_result:

            return {
                "status": "failed",
                "reason": "Artifact has not been validated."
            }

        if validation_result.get("validation") != "pass":

            return {
                "status": "failed",
                "reason": "Artifact validation failed. Git commit blocked."
            }

        artifact_path = artifact_result["artifact_path"]

        try:

            commit_hash = commit_generated_artifact(
                artifact_path=artifact_path,
                commit_message=context.get(
                    "task",
                    "Generated artifact"
                )
            )

            return {
                "status": "success",
                "commit": commit_hash,
                "artifact_path": artifact_path
            }

        except Exception as e:

            print(f"GitHub commit failed: {e}")

            return {
                "status": "failed",
                "reason": str(e),
                "artifact_path": artifact_path
            }
    # ======================================================
    # DOWNLOAD ARTIFACTS
    # ======================================================

    def download_artifacts(self, context):

        print("Executing download_artifacts")

        results = context.get("results", {})

        artifacts = []
        seen = set()

        for skill_name, result in results.items():

            if not isinstance(result, dict):
                continue

            artifact_path = result.get("artifact_path")

            if artifact_path and artifact_path not in seen:
                artifacts.append(artifact_path)
                seen.add(artifact_path)

        if not artifacts:

            return {
                "status": "failed",
                "reason": "No generated artifacts found."
        }

        return {
            "status": "success",
            "artifacts": artifacts,
            "count": len(artifacts)
        }