from .base import BaseSkill


class EnrichSkill(BaseSkill):

    name = "enrich"

    def execute(self, context):

        dataset = context.get("dataset")

        print(f"[EnrichSkill] Enriching metadata for {dataset}")

        context["description"] = (
            "Generated using AI Data Pipeline Generator"
        )

        return context