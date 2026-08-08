from app.planner.planner import Planner
from app.planner.executor import Executor


planner = Planner()
executor = Executor()


task = (
    "Generate Terraform infrastructure "
    "for customer_orders and make it available "
    "for download."
)


plan = planner.create_plan(task)


results = executor.execute(
    plan,
    {
        "table": "customer_orders",
        "task": task,
    }
)


print("\n========== EXECUTION RESULTS ==========")

print(results)