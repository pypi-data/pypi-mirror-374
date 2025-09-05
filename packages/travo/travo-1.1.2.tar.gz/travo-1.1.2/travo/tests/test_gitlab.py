import builtins
import getpass
import requests
import pytest
from travo import gitlab


def test_request_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    forge = gitlab.GitLab(base_url="https://gitlab.example.com")
    inputs = iter(["travo-test-etu", "aqwzsx(t1"])
    with pytest.raises(OSError, match="reading from stdin while output is captured"):
        user, passwd = gitlab.request_credentials_basic(forge)
        monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
        assert user == "travo-test-etu"
        assert passwd == "aqwzsx(t1"

    monkeypatch.setattr(getpass, "getpass", lambda _: "aqwzsx(t1")
    user, passwd = gitlab.request_credentials_basic(forge, username="travo-test-etu")
    assert user == "travo-test-etu"
    assert passwd == "aqwzsx(t1"

    username, password = gitlab.request_credentials_basic(forge, username="anonymous")
    assert username == "anonymous"
    assert password == ""


def test_token_requests(gitlab_url: str) -> None:
    forge = gitlab.GitLab(base_url=gitlab_url)
    assert not forge.set_token("*Ae", nosave=True)

    forge = gitlab.GitLab(base_url="http://gitlab.example.com")
    with pytest.raises(requests.exceptions.ConnectionError):
        forge.set_token("very_secret_token", nosave=True)


def test_login_logout(gitlab_url: str) -> None:
    forge = gitlab.GitLab(base_url=gitlab_url)
    forge.login(username="anonymous", anonymous_ok=True)
    token = forge.token
    assert token is None


def test_get_user_nousername(gitlab):
    with pytest.raises(ValueError, match="cannot be called without username;"):
        gitlab.get_user()
