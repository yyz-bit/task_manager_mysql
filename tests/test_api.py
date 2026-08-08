from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_openapi_json_is_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200


def test_update_task_requires_title():
    response = client.put(
        "/tasks/1",
        json={"description": "只有描述没有标题"},
    )
    assert response.status_code == 422
