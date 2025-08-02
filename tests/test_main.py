import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Maple AI Companion API v2.0" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert "healthy" in response.json()["status"]

@pytest.mark.asyncio
async def test_guest_chat():
    response = client.post(
        "/guest/chat",
        json={"content": "Hello", "message_type": "text"}
    )
    assert response.status_code == 200
    assert "content" in response.json()
