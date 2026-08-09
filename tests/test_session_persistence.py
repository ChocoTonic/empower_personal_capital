import json
import os

import pytest

from personalcapital import PersonalCapital
from personalcapital.personalcapital import SESSION_SCHEMA_VERSION


def test_session_round_trip_restores_cookies_and_csrf(tmp_path):
    session_path = tmp_path / "session.json"
    original = PersonalCapital()
    original.set_session({"remember-me": "cookie-value"})
    original._PersonalCapital__csrf = "csrf-value"

    original.save_session(session_path)

    restored = PersonalCapital()
    restored.load_session(session_path)

    assert restored.get_session() == {"remember-me": "cookie-value"}
    assert restored._PersonalCapital__csrf == "csrf-value"
    assert json.loads(session_path.read_text()) == {
        "version": SESSION_SCHEMA_VERSION,
        "csrf": "csrf-value",
        "cookies": {"remember-me": "cookie-value"},
    }


@pytest.mark.skipif(os.name == "nt", reason="Windows does not expose POSIX mode semantics")
def test_saved_session_is_owner_only(tmp_path):
    session_path = tmp_path / "session.json"

    PersonalCapital().save_session(session_path)

    assert session_path.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize(
    "state, message",
    [
        ({"version": 999, "csrf": "token", "cookies": {}}, "version"),
        ({"version": 1, "csrf": None, "cookies": {}}, "CSRF"),
        ({"version": 1, "csrf": "token", "cookies": []}, "cookies"),
    ],
)
def test_invalid_session_state_is_rejected(tmp_path, state, message):
    session_path = tmp_path / "session.json"
    session_path.write_text(json.dumps(state))

    with pytest.raises(ValueError, match=message):
        PersonalCapital().load_session(session_path)


def test_pickle_data_is_not_accepted(tmp_path):
    session_path = tmp_path / "session.json"
    session_path.write_bytes(b"\x80\x04pickle payload")

    with pytest.raises((UnicodeDecodeError, json.JSONDecodeError)):
        PersonalCapital().load_session(session_path)
