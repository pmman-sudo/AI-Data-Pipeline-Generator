# test_generation.py
from app.datahub.client import MetadataService
from app.llm.provider import generate
from app.security.validator import extract_code_blocks, save_and_validate
import json

# 1. Load prompt template
with open("app/prompts/airflow_dag.txt", "r") as f:
    template = f.read()

# 2. Get live metadata from DataHub
client = MetadataService()
metadata = client.get_table_context("fct_users_created")

# 3. Inject metadata into prompt
metadata_json = json.dumps(metadata.__dict__, indent=2)
prompt = template.format(metadata_json=metadata_json)

print("--- SENDING PROMPT TO GROQ ---")
raw_response = generate(prompt)

print("\n--- RAW RESPONSE FROM GROQ ---")
print(raw_response[:300] + "\n... [truncated]")

# 4. Extract Python & JSON
python_code, iam_json = extract_code_blocks(raw_response)

print("\n--- EXTRACTED PYTHON CODE ---")
print(python_code[:200] + "\n...")

print("\n--- EXTRACTED IAM POLICY ---")
print(iam_json)

# 5. Save files and run validation checks
results = save_and_validate("fct_users_created", python_code, iam_json)

print("\n--- FINAL VALIDATION RESULT ---")
print(json.dumps(results, indent=2))