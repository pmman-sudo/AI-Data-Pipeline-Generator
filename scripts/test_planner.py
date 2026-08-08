from app.planner.planner import Planner

planner = Planner()

plan = planner.create_plan(
    "Generate an Airflow DAG for customer_orders"
)

print(plan.model_dump_json(indent=2))