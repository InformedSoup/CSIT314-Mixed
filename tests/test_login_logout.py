"""Sprint 1 - Log in / Log out for all four roles.

User stories: #2 #3 (User Admin), #14 #15 (Interior Designer),
              #31 #32 (Customer), #40 #41 (Platform Management)
"""
import pytest

from control.login_controller import INVALID_LOGIN, LoginController
from control.logout_controller import LogoutController
from entity.user_account import UserAccount
from entity.user_session import UserSession
from tests.conftest import login

ROLES = [
    # (username, profile id, dashboard URL)
    ("admin", 1, "/admin/accounts/"),
    ("designer", 2, "/designer/projects/current/"),
    ("customer", 3, "/customer/"),
    ("platform", 4, "/platform/categories/"),
]


# ---- Unit tests: LoginController -----------------------------------------
@pytest.mark.parametrize("username,profile_id,_", ROLES)
def test_TC_LOGIN_01_valid_credentials_each_role(ctx, username, profile_id, _):
    ok, _msg, account, session = LoginController().authenticate(username, "password123")
    assert ok
    assert account.profileId == profile_id
    assert session.logoutAt is None


def test_TC_LOGIN_02_wrong_password_rejected(ctx):
    ok, msg, account, _ = LoginController().authenticate("admin", "wrongpass")
    assert not ok and account is None
    assert msg == INVALID_LOGIN


def test_TC_LOGIN_03_unknown_username_rejected(ctx):
    ok, msg, _, _ = LoginController().authenticate("nobody", "password123")
    assert not ok and msg == INVALID_LOGIN


def test_TC_LOGIN_04_blank_fields_rejected(ctx):
    ok, msg, _, _ = LoginController().authenticate("", "")
    assert not ok and "required" in msg


def test_TC_LOGIN_05_suspended_account_cannot_log_in(ctx):
    UserAccount.findByUsername("customer").setStatus("SUSPENDED")
    ok, msg, _, _ = LoginController().authenticate("customer", "password123")
    assert not ok and "suspended" in msg


def test_TC_LOGIN_06_username_is_case_insensitive(ctx):
    ok, *_ = LoginController().authenticate("ADMIN", "password123")
    assert ok


# ---- Unit tests: LogoutController ----------------------------------------
def test_TC_LOGOUT_01_logout_closes_session(ctx):
    _, _, account, session = LoginController().authenticate("designer", "password123")
    ok, _ = LogoutController().logout(session.sessionId)
    assert ok
    assert UserSession.findById(session.sessionId).logoutAt is not None


def test_TC_LOGOUT_02_logout_without_session_fails(ctx):
    ok, _ = LogoutController().logout(None)
    assert not ok


# ---- Boundary tests: full HTTP flow --------------------------------------
@pytest.mark.parametrize("username,profile_id,dashboard", ROLES)
def test_TC_LOGIN_07_login_redirects_to_role_dashboard(client, username, profile_id, dashboard):
    response = login(client, username)
    assert response.status_code == 302
    assert response.headers["Location"].endswith(dashboard)
    with client.session_transaction() as s:
        assert s["profile_id"] == profile_id


def test_TC_LOGIN_08_failed_login_shows_error(client):
    response = login(client, "admin", "nope")
    assert response.status_code == 401
    assert b"Invalid username or password" in response.data
    with client.session_transaction() as s:
        assert "account_id" not in s


@pytest.mark.parametrize("username,_,dashboard", ROLES)
def test_TC_LOGOUT_03_logout_clears_session_each_role(client, username, _, dashboard):
    login(client, username)
    response = client.post("/logout")
    assert response.headers["Location"].endswith("/login")
    with client.session_transaction() as s:
        assert "account_id" not in s
    # dashboard is no longer reachable
    assert client.get(dashboard).headers["Location"].endswith("/login")


def test_TC_ACCESS_01_role_cannot_open_other_role_pages(client):
    login(client, "customer")
    response = client.get("/admin/accounts/")
    assert response.status_code == 302
    assert not response.headers["Location"].endswith("/admin/accounts/")
