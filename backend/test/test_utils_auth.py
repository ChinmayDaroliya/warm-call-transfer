import pytest
import jwt
from datetime import timedelta, datetime

from app.config import settings
from utils.auth import create_access_token, verify_access_token


@pytest.fixture(autouse=True)
def set_test_settings(monkeypatch):
    """Ensure test has JWT settings configured"""
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", "testsecret")
    monkeypatch.setattr(settings, "JWT_ALGORITHM", "HS256")
    monkeypatch.setattr(settings, "JWT_EXPIRATION_HOURS", 1)
    yield


def test_create_and_verify_access_token():
    token = create_access_token("user123")
    payload = verify_access_token(token)

    assert payload is not None
    assert payload["sub"] == "user123"
    assert "exp" in payload
    assert "iat" in payload


def test_create_token_with_additional_claims():
    token = create_access_token("user456", additional_claims={"role": "admin"})
    payload = verify_access_token(token)

    assert payload["sub"] == "user456"
    assert payload["role"] == "admin"


def test_token_expiration(monkeypatch):
    # Expired token
    expired_token = create_access_token("user789", expires_delta=timedelta(seconds=-1))
    payload = verify_access_token(expired_token)

    assert payload is None


def test_invalid_signature():
    token = create_access_token("user999")

    # Tamper the token
    parts = token.split(".")
    tampered_token = ".".join(parts[:-1]) + ".invalidsignature"

    payload = verify_access_token(tampered_token)
    assert payload is None


def test_invalid_token_format():
    payload = verify_access_token("not.a.jwt")
    assert payload is None
