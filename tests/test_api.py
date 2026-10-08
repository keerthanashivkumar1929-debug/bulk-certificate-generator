import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["message"] == \
        "Bulk Certificate Generator API is running!"


def test_create_job(client):
    data = {
        "event_name": "Python Workshop",
        "date": "2026-10-08",
        "recipients": [
            {
                "name": "Keerthana",
                "email": "keerthana@example.com"
            },
            {
                "name": "Rahul",
                "email": "rahul@example.com"
            }
        ]
    }

    response = client.post("/jobs", json=data)

    assert response.status_code == 201

    result = response.get_json()

    assert result["total"] == 2
    assert result["successful"] == 2
    assert result["failed"] == 0


def test_empty_recipients(client):
    data = {
        "event_name": "Python Workshop",
        "date": "2026-10-08",
        "recipients": []
    }

    response = client.post("/jobs", json=data)

    assert response.status_code == 400


def test_missing_event_name(client):
    data = {
        "date": "2026-10-08",
        "recipients": [
            {
                "name": "Keerthana",
                "email": "keerthana@example.com"
            }
        ]
    }

    response = client.post("/jobs", json=data)

    assert response.status_code == 400