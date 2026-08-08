from fastapi.testclient import TestClient

from app.main import app
from app.datahub.client import TableMetadata

client = TestClient(app)


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


# ==========================================================
# Test: Airflow generation WITHOUT Git commit
# ==========================================================

def test_generate_airflow_without_commit(mocker):

    mock_metadata(mocker)

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

    # Prevent the test from performing a real Git commit
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