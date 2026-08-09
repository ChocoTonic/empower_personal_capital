from unittest.mock import Mock

from personalcapital import PersonalCapital
from personalcapital.personalcapital import DEVICE_NAME


def test_password_authentication_registers_a_recognizable_device(monkeypatch):
    session = Mock()
    monkeypatch.setattr("personalcapital.personalcapital.requests.Session", lambda: session)

    PersonalCapital().authenticate_password("secret")

    payload = session.post.call_args.args[1]
    assert payload["bindDevice"] == "true"
    assert payload["deviceName"] == DEVICE_NAME
    assert DEVICE_NAME == "Empower Personal Capital Python API"
