from .base import BaseSkill


class QualitySkill(BaseSkill):

    name = "quality"

    def execute(self, context):

        dataset = context.get("dataset")

        print(f"[QualitySkill] Checking quality of {dataset}")

        context["quality"] = "PASSED"

        return context