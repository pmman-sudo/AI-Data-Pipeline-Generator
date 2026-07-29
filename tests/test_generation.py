import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Dummy responses to mimic the LLM
MOCK_VALID_DAG = """
```python
print("Hello Airflow")

```json
{"Statement": [{"Effect": "Allow", "Action": "s3:GetObject", "Resource": "*"}]}

```python"""

def test_generate_returns_artifact(mocker):
    # 1. Mock the LLM generation so we don't call the real API
    mocker.patch("app.main.generate", return_value=MOCK_VALID_DAG)
    
    # 2. Mock the GitHub push so we don't actually push to Git during tests
    mocker.patch("app.main.commit_and_push", return_value="mock123")
    
    # 3. Mock the DataHub write-back so we don't spam DataHub during tests
    mocker.patch("app.main.write_generation_metadata", return_value=True)

    # Execute the request
    resp = client.post('/generate', json={'task': 'Generate an Airflow DAG for the fct_users_created table'})
    
    # Assertions
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "artifact" in data
    assert data["commit"] == "mock123"
    assert data["validation"]["status"] == "pass"