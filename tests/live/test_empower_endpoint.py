import pytest
import requests

from personalcapital.personalcapital import HEADERS, csrf_regexp, login_url


@pytest.mark.live
def test_public_login_endpoint_exposes_a_csrf_token():
    response = requests.get(login_url, headers=HEADERS, timeout=20)

    assert response.status_code == 200
    assert response.url == login_url
    assert csrf_regexp.search(response.text)
