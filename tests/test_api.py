from fastapi.testclient import TestClient
from app.api import app
from app.config import API_V1_STR

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_and_login():
    # Test Register
    user_data = {"email": "test@example.com", "password": "password123"}
    response = client.post(f"{API_V1_STR}/register", json=user_data)
    if response.status_code == 400:
        # User might already exist from previous runs
        pass
    else:
        assert response.status_code == 200
        assert response.json()["email"] == user_data["email"]

    # Test Login
    login_data = {"username": "test@example.com", "password": "password123"}
    response = client.post(f"{API_V1_STR}/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None

    # Test Protected Endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"{API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
