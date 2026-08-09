from unittest.mock import ANY, Mock

import pytest

from personalcapital import LoginFailedException, PersonalCapital, RequireTwoFactorException
from personalcapital.personalcapital import api_endpoint, login_url

CSRF = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def response(*, text="", payload=None, status_code=200):
    result = Mock()
    result.text = text
    result.status_code = status_code
    result.json.return_value = payload
    return result


@pytest.fixture
def session(monkeypatch):
    fake = Mock()
    monkeypatch.setattr("personalcapital.personalcapital.requests.Session", lambda: fake)
    return fake


def test_login_uses_empower_login_page_and_api(session):
    session.get.return_value = response(text=f"<script>window.csrf ='{CSRF}'</script>")
    session.post.side_effect = [
        response(payload={"spHeader": {"csrf": CSRF, "authLevel": "USER_REMEMBERED"}}),
        response(payload={"spHeader": {"success": True}}),
    ]

    PersonalCapital().login("user@example.com", "secret")

    session.get.assert_called_once_with(login_url, headers=ANY)
    assert login_url == "https://pc-api.empower-retirement.com/page/login/goHome"
    assert session.post.call_args_list[0].args[0] == api_endpoint + "/login/identifyUser"
    assert (
        session.post.call_args_list[1].args[0] == api_endpoint + "/credential/authenticatePassword"
    )


def test_login_raises_two_factor_exception_for_mfa_required(session):
    session.get.return_value = response(text=f"window.csrf ='{CSRF}'")
    session.post.return_value = response(
        payload={"spHeader": {"csrf": CSRF, "authLevel": "MFA_REQUIRED"}}
    )

    with pytest.raises(RequireTwoFactorException):
        PersonalCapital().login("user@example.com", "secret")

    assert session.post.call_count == 1


def test_login_raises_when_password_response_requires_mfa(session):
    session.get.return_value = response(text=f"window.csrf ='{CSRF}'")
    session.post.side_effect = [
        response(payload={"spHeader": {"csrf": CSRF, "authLevel": "USER_REMEMBERED"}}),
        response(payload={"spHeader": {"authLevel": "MFA_REQUIRED"}}),
    ]

    with pytest.raises(RequireTwoFactorException):
        PersonalCapital().login("user@example.com", "secret")


def test_login_reports_missing_initial_csrf(session):
    session.get.return_value = response(text="no csrf here")

    with pytest.raises(LoginFailedException, match="initial CSRF"):
        PersonalCapital().login("user@example.com", "secret")


def test_login_reports_identification_failure(session):
    session.get.return_value = response(text=f"window.csrf ='{CSRF}'")
    session.post.return_value = response(status_code=500)

    with pytest.raises(LoginFailedException, match="identify user"):
        PersonalCapital().login("user@example.com", "secret")


def test_login_failed_exception_is_exported():
    from personalcapital import LoginFailedException as PublicLoginFailedException

    assert PublicLoginFailedException is LoginFailedException
