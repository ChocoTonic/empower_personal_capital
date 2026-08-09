from unittest.mock import Mock

import pytest

from personalcapital import PersonalCapital, TwoFactorVerificationModeEnum
from personalcapital.personalcapital import api_endpoint


@pytest.fixture
def client_and_session(monkeypatch):
    session = Mock()
    monkeypatch.setattr("personalcapital.personalcapital.requests.Session", lambda: session)
    client = PersonalCapital()
    client._PersonalCapital__csrf = "csrf-value"
    return client, session


@pytest.mark.parametrize(
    "mode, endpoint, challenge_type",
    [
        (TwoFactorVerificationModeEnum.SMS, "/credential/challengeSms", "challengeSMS"),
        (TwoFactorVerificationModeEnum.EMAIL, "/credential/challengeEmail", "challengeEmail"),
    ],
)
def test_two_factor_challenge_uses_expected_endpoint(
    client_and_session, mode, endpoint, challenge_type
):
    client, session = client_and_session

    result = client.two_factor_challenge(mode)

    assert result is session.post.return_value
    url, payload = session.post.call_args.args[:2]
    assert url == api_endpoint + endpoint
    assert payload["challengeType"] == challenge_type
    assert payload["csrf"] == "csrf-value"


@pytest.mark.parametrize(
    "mode, endpoint",
    [
        (TwoFactorVerificationModeEnum.SMS, "/credential/authenticateSms"),
        (TwoFactorVerificationModeEnum.EMAIL, "/credential/authenticateEmailByCode"),
    ],
)
def test_two_factor_authentication_uses_expected_endpoint(client_and_session, mode, endpoint):
    client, session = client_and_session

    result = client.two_factor_authenticate(mode, "123456")

    assert result is session.post.return_value
    url, payload = session.post.call_args.args[:2]
    assert url == api_endpoint + endpoint
    assert payload["code"] == "123456"
    assert payload["csrf"] == "csrf-value"


@pytest.mark.parametrize("method", ["two_factor_challenge", "two_factor_authenticate"])
def test_unknown_two_factor_mode_is_rejected(client_and_session, method):
    client, _ = client_and_session
    arguments = (999,) if method == "two_factor_challenge" else (999, "123456")

    with pytest.raises(ValueError, match="Unsupported two-factor"):
        getattr(client, method)(*arguments)
