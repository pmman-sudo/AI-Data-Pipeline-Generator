import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

MOCK_VALID_DAG = """
print("Hello Airflow")
{"Statement": [{"Effect": "Allow", "Action": "s3:GetObject", "Resource": "*"}]}
"""

def test_generate_returns_artifact(mocker):
    # 1. Mock the LLM generation
    mocker.patch("app.main.generate", return_value=MOCK_VALID_DAG)
    
    # 2. Mock the GitHub push
    mocker.patch("app.main.commit_and_push", return_value="mock123")
    
    # 3. FIX: Patch the instance variable 'emitter' directly
    mocker.patch("app.datahub.writeback.emitter")

    # Execute the request
    resp = client.post('/generate', json={'task': 'Generate an Airflow DAG for the fct_users_created table'})
    
    # Assertions
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "artifact" in data
    assert data["commit"] == "mock123"
    assert data["validation"]["status"] == "pass"