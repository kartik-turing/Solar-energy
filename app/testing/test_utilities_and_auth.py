import os
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jwt import DecodeError, ExpiredSignatureError

from app.api.routes.job_status import router
from app.api.utils.client_credentials import Oauth2ClientCredentials
from app.auth import HTTPException, verify_token
from app.config.config import SECRETS

AUTHORITY = SECRETS.AUTHORITY
CLIENT_ID_AVIGNA = SECRETS.CLIENT_ID_AVIGNA
TOKEN_URL = SECRETS.TOKEN_URL
SCOPE = SECRETS.SCOPE

client = TestClient(router)
endpoint = "/simulation/resi/v1/jobstatus"
header = {"Authorization": None}


@pytest.fixture
def mock_decode(mocker):
    return mocker.patch("app.auth.decode")


def test_client_credentials_auth_failure(mocker):
    mocker.patch.dict(os.environ, {"YOUR_ENV": "outside_testing"})
    import fastapi

    try:
        client.get(
            endpoint, params={"simulationJobID": "dc2e12cbf"}, headers=None
        )
    except HTTPException as http_err:
        assert http_err.status_code == 401


def test_client_credentials_auth_failure_by_scheme(mocker):
    mocker.patch.dict(os.environ, {"YOUR_ENV": "outside_testing"})
    import fastapi

    try:
        header["Authorization"] = "Bearered "
        client.get(
            endpoint, params={"simulationJobID": "dc2e12cbf"}, headers=header
        )
    except HTTPException as http_err:
        assert http_err.status_code == 401


def test_valid_token(mock_decode):
    valid_payload = {
        "client_id": CLIENT_ID_AVIGNA,
        "scope": SCOPE,
        "iss": AUTHORITY,
        "exp": int(
            (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
        ),
        "sub": "subject123",
    }
    mock_decode.return_value = valid_payload

    try:
        verify_token("valid_token")
    except HTTPException as e:
        pytest.fail(f"verify_token raised HTTPException unexpectedly: {e}")


def test_expired_token(mock_decode):
    mock_decode.side_effect = ExpiredSignatureError()
    with pytest.raises(HTTPException) as exc_info:
        verify_token("expired_token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token"


def test_invalid_audience(mock_decode):
    invalid_payload = {
        "client_id": "invalid_client_id",
        "scope": SCOPE,
        "iss": AUTHORITY,
        "exp": int(
            (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
        ),
        "sub": "subject123",
    }
    mock_decode.return_value = invalid_payload
    with pytest.raises(HTTPException) as exc_info:
        verify_token("invalid_audience_token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token"


def test_invalid_issuer(mock_decode):
    payload = {
        "client_id": CLIENT_ID_AVIGNA,
        "scope": SCOPE,
        "iss": "invalid_issuer",
        "exp": int(
            (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
        ),
        "sub": "subject123",
    }
    mock_decode.return_value = payload
    with pytest.raises(HTTPException) as exc_info:
        verify_token("invalid_issuer_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token"


def test_missing_subject_claim(mock_decode):
    payload = {
        "client_id": CLIENT_ID_AVIGNA,
        "scope": SCOPE,
        "iss": AUTHORITY,
        "exp": int(
            (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
        ),
    }
    mock_decode.return_value = payload
    with pytest.raises(HTTPException) as exc_info:
        verify_token("missing_subject_claim")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token"


def test_verify_token_exceptions(mock_decode):
    mock_decode.side_effect = DecodeError("Invalid Token")
    with pytest.raises(HTTPException) as exc_info:
        verify_token("invalid_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token"
    mock_decode.side_effect = Exception("Exception occurred")
    with pytest.raises(HTTPException) as exc_info:
        verify_token("generic_token_error")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token"
