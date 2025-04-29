"""Tests for the mock Twilio API."""

import base64

import pytest
from fastapi.testclient import TestClient

from mock_twilio.config import settings
from mock_twilio.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for the API."""
    credentials = f"{settings.ACCOUNT_SID}:{settings.AUTH_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded_credentials}"}


def test_root(client):
    """Test the root endpoint returns HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Mock Twilio API" in response.text


def test_send_message(client, auth_headers):
    """Test sending an SMS message."""
    data = {
        "To": "+15551234567",
        "From": "+15557654321",
        "Body": "Test message",
    }

    account_sid = settings.ACCOUNT_SID
    response = client.post(
        f"/v1/Accounts/{account_sid}/Messages",
        headers=auth_headers,
        data=data,
    )

    assert response.status_code == 200
    result = response.json()
    assert result["to"] == data["To"]
    assert result["from"] == data["From"]
    assert result["body"] == data["Body"]
    assert result["status"] == "queued"


def test_auth_failure(client):
    """Test authentication failure."""
    data = {
        "To": "+15551234567",
        "From": "+15557654321",
        "Body": "Test message",
    }

    account_sid = settings.ACCOUNT_SID
    response = client.post(
        f"/v1/Accounts/{account_sid}/Messages",
        # No auth headers
        data=data,
    )

    assert response.status_code == 401


def test_logs(client):
    """Test the logs endpoint."""
    response = client.get("/logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
