from app.skills.orchestrator import SkillOrchestrator

workflow = [
    "search",
    "lineage",
    "enrich",
    "quality",
]

context = {
    "dataset": "sales.orders"
}

result = SkillOrchestrator().run(workflow, context)

print(result)