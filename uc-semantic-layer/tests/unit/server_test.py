from pydoc import cli
from uc_semantic_layer.backend.server import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_query_generator():
    response = client.post("/sql_query", json={"payload": "get all customers"})
    assert response.status_code == 200

def test_query_execution():
    response = client.post("/execute_sql", json={"query": "SELECT * FROM field_demos.core.customer LIMIT 10"})
    assert response.status_code == 200
    print(response.json())

