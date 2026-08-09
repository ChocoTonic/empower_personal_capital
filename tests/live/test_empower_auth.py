import os

import pytest

from personalcapital import PersonalCapital, RequireTwoFactorException
from personalcapital.personalcapital import SUCCESS_KEY, getSpHeaderValue


@pytest.mark.live
def test_live_login_reaches_a_valid_authentication_state():
    email = os.getenv("EMPOWER_EMAIL")
    password = os.getenv("EMPOWER_PASSWORD")
    if not email or not password:
        pytest.skip("EMPOWER_EMAIL and EMPOWER_PASSWORD are not configured")

    client = PersonalCapital()
    try:
        client.login(email, password)
    except RequireTwoFactorException:
        # Reaching the explicit MFA state verifies user identification without
        # sending an SMS/email challenge or mutating account data.
        return

    response = client.fetch("/newaccount/getAccounts")
    assert response.status_code == 200
    payload = response.json()
    assert getSpHeaderValue(payload, SUCCESS_KEY) is True
    assert isinstance(payload.get("spData"), dict)
