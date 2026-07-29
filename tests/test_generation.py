import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.datahub.client import TableMetadata

client = TestClient(app)

MOCK_VALID_DAG = """
print("Hello Airflow")
{"Statement": [{"Effect": "Allow", "Action": "s3:GetObject", "Resource": "*"}]}
"""


def test_generate_returns_artifact(mocker):
    # 1. Mock the LLM generation
    mocker.patch(
        "app.main.generate",
        return_value=MOCK_VALID_DAG
    )
    mocker.patch(
        "app.main.extract_code_blocks",
        return_value=(
            'print("Hello Airflow")',
            '{"Statement":[{"Effect":"Allow","Action":"s3:GetObject","Resource":"*"}]}'
        )
    )


    # 2. Mock the GitHub commit
    mocker.patch(
        "app.main.commit_and_push",
        return_value="mock123"
    )

    # 3. Mock save_and_validate
    mocker.patch(
        "app.main.save_and_validate",
        return_value={
            "artifact_path": "generated/fct_users_created.py",
            "iam_path": "generated/policy.json",
            "validation": {
                "status": "pass"
            }
        }
    )

    # 4. Mock DataHub metadata lookup
    mocker.patch(
        "app.main.MetadataService.get_table_context",
        return_value=TableMetadata(
            name="fct_users_created",
            columns=[
                {
                    "name": "id",
                    "type": "INT",
                    "description": ""
                }
            ],
            owners=["Paul"],
            tags=[],
            lineage=[]
        )
    )

    # 5. Mock DataHub write-back
    mocker.patch(
        "app.main.write_generation_metadata",
        return_value=True
    )

    # Execute request
    resp = client.post(
        "/generate",
        json={
            "task": "Generate an Airflow DAG for the fct_users_created table"
        }
    )

    # Assertions
    assert resp.status_code == 200

    data = resp.json()

    assert data["status"] == "success"
    assert "artifact" in data
    assert data["commit"] == "mock123"
    assert data["validation"]["status"] == "pass"