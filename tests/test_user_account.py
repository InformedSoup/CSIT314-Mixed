"""Sprint 1 - User Admin manages user accounts.

User stories: #4 create, #5 view, #6 update, #7 suspend (+ #8 search from Sprint 2)
"""
from control.create_user_controller import CreateUserController
from control.search_user_controller import SearchUserController
from control.suspend_user_controller import SuspendUserController
from control.update_user_controller import UpdateUserController
from control.view_user_controller import ViewUserController
from entity.user_account import UserAccount
from tests.conftest import login

NEW_USER = dict(fullName="Test Person", username="testperson", email="test@person.com",
                password="secret1", profileId="3")


# ---- #4 Create user account ----------------------------------------------
def test_TC_CREATE_01_valid_account_is_saved(ctx):
    ok, _ = CreateUserController().handleCreateUser(**NEW_USER)
    assert ok
    account = UserAccount.findByUsername("testperson")
    assert account.email == "test@person.com" and account.status == "ACTIVE"
    assert account.passwordHash != "secret1"  # stored hashed, never in plain text


def test_TC_CREATE_02_duplicate_username_rejected(ctx):
    ok, msg = CreateUserController().handleCreateUser(**{**NEW_USER, "username": "admin"})
    assert not ok and "already taken" in msg


def test_TC_CREATE_03_duplicate_email_rejected(ctx):
    ok, msg = CreateUserController().handleCreateUser(**{**NEW_USER, "email": "admin@idp.test"})
    assert not ok and "already registered" in msg


def test_TC_CREATE_04_invalid_fields_all_reported(ctx):
    errors = CreateUserController().validateUserDetails("", "", "not-an-email", "123", "99")
    assert len(errors) == 5


def test_TC_CREATE_05_new_user_can_log_in(client, ctx):
    CreateUserController().handleCreateUser(**NEW_USER)
    assert login(client, "testperson", "secret1").status_code == 302


def test_TC_CREATE_06_create_page_flow(admin_client):
    response = admin_client.post("/admin/accounts/create", data=NEW_USER)
    assert response.status_code == 302
    page = admin_client.get("/admin/accounts/?q=testperson")
    assert b"testperson" in page.data


# ---- #5 View user account ------------------------------------------------
def test_TC_VIEW_01_list_shows_all_accounts(ctx):
    assert len(ViewUserController().getUserAccounts()) == 14  # 4 demo + 10 generated


def test_TC_VIEW_02_details_page(admin_client):
    response = admin_client.get("/admin/accounts/1")
    assert response.status_code == 200 and b"admin@idp.test" in response.data


def test_TC_VIEW_03_unknown_account_shows_not_found_message(admin_client):
    response = admin_client.get("/admin/accounts/9999", follow_redirects=True)
    assert b"User account not found." in response.data


# ---- #6 Update user account ----------------------------------------------
def test_TC_UPDATE_01_details_updated(ctx):
    ok, _ = UpdateUserController().handleUpdateUser(3, "Cindy New", "cindy@new.com", 2)
    assert ok
    account = UserAccount.findById(3)
    assert (account.fullName, account.email, account.profileId) == ("Cindy New", "cindy@new.com", 2)


def test_TC_UPDATE_02_password_change(client, ctx):
    UpdateUserController().handleUpdateUser(3, "Cindy", "customer@idp.test", 3, "newpass9")
    assert login(client, "customer", "newpass9").status_code == 302


def test_TC_UPDATE_03_email_taken_by_other_user_rejected(ctx):
    ok, msg = UpdateUserController().handleUpdateUser(3, "Cindy", "admin@idp.test", 3)
    assert not ok and "already registered" in msg


def test_TC_UPDATE_04_keeping_own_email_allowed(ctx):
    ok, _ = UpdateUserController().handleUpdateUser(3, "Cindy C", "customer@idp.test", 3)
    assert ok


# ---- #7 Suspend user account ---------------------------------------------
def test_TC_SUSPEND_01_account_suspended(ctx):
    ok, _ = SuspendUserController().suspendUser(3, actingUserId=1)
    assert ok and UserAccount.findById(3).status == "SUSPENDED"


def test_TC_SUSPEND_02_admin_cannot_suspend_self(ctx):
    ok, msg = SuspendUserController().suspendUser(1, actingUserId=1)
    assert not ok and "own account" in msg


def test_TC_SUSPEND_03_already_suspended(ctx):
    SuspendUserController().suspendUser(3)
    ok, _ = SuspendUserController().suspendUser(3)
    assert not ok


def test_TC_SUSPEND_04_reactivate(ctx):
    SuspendUserController().suspendUser(3)
    ok, _ = SuspendUserController().reactivateUser(3)
    assert ok and UserAccount.findById(3).isActive()


def test_TC_SUSPEND_05_suspend_via_page_blocks_login(admin_client, app):
    admin_client.post("/admin/accounts/3/suspend")
    other = app.test_client()
    response = login(other, "customer")
    assert response.status_code == 401 and b"suspended" in response.data


# ---- #8 Search user account ----------------------------------------------
def test_TC_SEARCH_01_by_name_username_email_or_role(ctx):
    controller = SearchUserController()
    assert [a.username for a in controller.searchUsers("Daniel")] == ["designer"]
    assert any(a.username == "platform" for a in controller.searchUsers("Platform Management"))
    assert [a.username for a in controller.searchUsers("customer@idp")] == ["customer"]


def test_TC_SEARCH_02_no_match_returns_empty(ctx):
    assert SearchUserController().searchUsers("zzzzzz") == []


def test_TC_SEARCH_03_blank_keyword_returns_all(ctx):
    assert len(SearchUserController().searchUsers("  ")) == 14


def test_TC_SEARCH_04_empty_search_prompts_for_keyword(admin_client):
    page = admin_client.get("/admin/accounts/?q=")
    assert b"Please enter a search keyword." in page.data
    assert b"Please enter a search keyword." not in admin_client.get("/admin/accounts/").data


def test_TC_SEARCH_05_no_match_message(admin_client):
    assert b"No user accounts found." in admin_client.get("/admin/accounts/?q=zzzzzz").data
