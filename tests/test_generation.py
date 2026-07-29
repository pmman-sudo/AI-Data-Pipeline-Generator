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
    
    # 3. DOUBLE PROTECTION:
    # First, mock the function call inside main.py
    mocker.patch("app.main.write_generation_metadata", return_value=True)
    # Second, mock the DataHub class in the writeback module so the REAL code 
    # definitely cannot establish a connection even if it wanted to.
    mocker.patch("app.datahub.writeback.DatahubRestEmitter")

    # Execute the request
    resp = client.post('/generate', json={'task': 'Generate an Airflow DAG for the fct_users_created table'})
    
    # Assertions
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "artifact" in data
    assert data["commit"] == "mock123"
    assert data["validation"]["status"] == "pass"