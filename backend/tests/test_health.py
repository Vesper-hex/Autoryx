import pytest

def test_health_check_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "Autoryx"
    assert "compilers" in data
    assert data["compilers"]["gcc"] is True
    assert data["compilers"]["g++"] is True
    assert data["compilers"]["javac"] is True
    assert data["compilers"]["python"] is True
