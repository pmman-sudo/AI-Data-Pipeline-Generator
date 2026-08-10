import json

from fastapi.testclient import TestClient

from app.main import app
from app.datahub.client import TableMetadata

client = TestClient(app, raise_server_exceptions=True)

# ==========================================================
# Shared Mock Metadata
# ==========================================================

MOCK_METADATA = TableMetadata(
    name="fct_users_created",
    columns=[
        {
            "name": "id",
            "type": "INT",
            "description": "",
        }
    ],
    owners=["Paul"],
    tags=[],
    lineage=[],
)


# ==========================================================
# Helper: Mock DataHub Metadata
# ==========================================================

def mock_metadata(mocker):
    mocker.patch(
        "app.main.MetadataService.get_table_context",
        return_value=MOCK_METADATA,
    )

def mock_planner(mocker, steps):
    return mocker.patch(
        "app.planner.planner.generate",
        return_value=json.dumps({
            "steps": steps
        }),
    )

def mock_terraform_llm(mocker):
    return mocker.patch(
        "app.skills.generate_terraform.generate",
        return_value="""
terraform {
  required_version = ">= 1.0"
}

resource "aws_s3_bucket" "fct_users_created" {
  bucket = "fct-users-created-test"
}
""",
    )

def mock_airflow_llm(mocker):
    return mocker.patch(
        "app.skills.generate_airflow.generate",
        return_value="""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "Paul",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def load_data():
    pass

def transform_data():
    pass

def validate_data():
    pass

with DAG(
    "fct_users_created_dag",
    default_args=default_args,
    description="DAG for fct_users_created",
    schedule=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=[],
) as dag:

    load_task = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )

    validate_task = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data,
    )

    load_task >> transform_task >> validate_task
""",
    )


# ==========================================================
# Test: Airflow generation WITHOUT Git commit
# ==========================================================

def test_generate_airflow_without_commit(mocker):

    mock_airflow_llm(mocker)
    mock_metadata(mocker)

    mock_planner(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_airflow",
                "reason": "Generate Airflow DAG",
            },
            {
                "skill": "validate",
                "reason": "Validate generated DAG",
            },
        ],
    )



    response = client.post(
        "/generate",
        json={
            "task": (
                "Generate an Airflow DAG "
                "for the fct_users_created table"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "artifact" in data
    assert data["validation"]["status"] == "pass"
    assert data["commit"] == "Not committed"


# ==========================================================
# Test: Airflow generation WITH Git commit
# ==========================================================

def test_generate_airflow_with_commit(mocker):

    mock_metadata(mocker)
    mock_airflow_llm(mocker)

    mock_planner(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_airflow",
                "reason": "Generate Airflow DAG",
            },
            {
                "skill": "validate",
                "reason": "Validate generated DAG",
            },
            {
                "skill": "git_commit",
                "reason": "Commit generated artifact to Git",
            },
        ],
    )

    mocker.patch(
        "app.planner.skills.commit_generated_artifact",
        return_value="mock-airflow-123",
    )

    response = client.post(
        "/generate",
        json={
            "task": (
                "Generate an Airflow DAG for the "
                "fct_users_created table and commit it to Git"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "artifact" in data
    assert data["validation"]["status"] == "pass"
    assert data["commit"] == "mock-airflow-123"

# ==========================================================
# Test: Terraform generation WITHOUT Git commit
# ==========================================================

def test_generate_terraform_without_commit(mocker):

    mock_metadata(mocker)
    mock_terraform_llm(mocker)

    mock_planner(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_terraform",
                "reason": "Generate Terraform infrastructure",
            },
            {
                "skill": "validate",
                "reason": "Validate generated Terraform",
            },
        ],
    )


    response = client.post(
        "/generate",
        json={
            "task": (
                "Generate Terraform infrastructure "
                "for the fct_users_created table"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "artifact" in data
    assert data["validation"]["status"] == "pass"
    assert data["commit"] == "Not committed"


# ==========================================================
# Test: Terraform generation WITH Git commit
# ==========================================================

def test_generate_terraform_with_commit(mocker):

    mock_metadata(mocker)
    mock_terraform_llm(mocker)

    mock_planner(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_terraform",
                "reason": "Generate Terraform infrastructure",
            },
            {
                "skill": "validate",
                "reason": "Validate generated Terraform",
            },
            {
                "skill": "git_commit",
                "reason": "Commit generated artifact to Git",
            },
        ],
    )

    # Prevent the test from performing a real Git commit
    mocker.patch(
        "app.planner.skills.commit_generated_artifact",
        return_value="mock-terraform-123",
    )

    response = client.post(
        "/generate",
        json={
            "task": (
                "Generate Terraform infrastructure "
                "for the fct_users_created table "
                "and commit it to Git"
            )
        },
    )


    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "artifact" in data
    assert data["validation"]["status"] == "pass"
    assert data["commit"] == "mock-terraform-123"

