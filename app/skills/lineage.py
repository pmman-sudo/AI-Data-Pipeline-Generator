from .base import BaseSkill


class LineageSkill(BaseSkill):

    name = "lineage"

    def execute(self, context):

        dataset = context.get("dataset")

        print(f"[LineageSkill] Building lineage for {dataset}")

        context["upstream"] = [
            "raw_orders",
            "raw_customers"
        ]

        context["downstream"] = [
            "sales_dashboard"
        ]

        return context