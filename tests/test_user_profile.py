"""Sprint 2 - User Admin manages user profiles.

User stories: #9 create, #10 view, #11 update, #12 suspend, #13 search
"""
from control.create_profile_controller import CreateProfileController
from control.login_controller import LoginController
from control.search_profile_controller import SearchProfileController
from control.suspend_profile_controller import SuspendProfileController
from control.update_profile_controller import UpdateProfileController
from control.view_profile_controller import ViewProfileController
from control.create_user_controller import CreateUserController
from entity.user_profile import CUSTOMER, UserProfile
from tests.conftest import login


# ---- #9 Create user profile ----------------------------------------------
def test_TC_PCREATE_01_valid_profile_saved(ctx):
    ok, _ = CreateProfileController().createProfile("Premium Customer", "Paying customers", CUSTOMER)
    assert ok
    profile = UserProfile.searchProfiles("Premium")[0]
    assert profile.role == CUSTOMER and profile.status == "ACTIVE"


def test_TC_PCREATE_02_duplicate_name_rejected(ctx):
    ok, msg = CreateProfileController().createProfile("customer", "dup", CUSTOMER)
    assert not ok and "already exists" in msg


def test_TC_PCREATE_03_missing_fields_and_bad_role(ctx):
    errors = CreateProfileController().validateDetail("", "", "SUPERUSER")
    assert len(errors) == 3


def test_TC_PCREATE_04_new_profile_grants_its_role(client, ctx):
    """An account under a new profile gets that profile's role (Customer dashboard)."""
    CreateProfileController().createProfile("Premium Customer", "Paying customers", CUSTOMER)
    profile_id = UserProfile.searchProfiles("Premium")[0].profileId
    CreateUserController().handleCreateUser("Pat Lee", "patlee", "pat@lee.com", "secret1", profile_id)
    response = login(client, "patlee", "secret1")
    assert response.headers["Location"].endswith("/customer/")


# ---- #10 View user profile -----------------------------------------------
def test_TC_PVIEW_01_profile_details_with_account_count(ctx):
    profile = ViewProfileController().viewProfile(1)
    assert profile.profileName == "User Admin" and profile.accountCount >= 1


def test_TC_PVIEW_02_detail_page(admin_client):
    response = admin_client.get("/admin/profiles/2")
    assert response.status_code == 200 and b"Interior Designer" in response.data


def test_TC_PVIEW_03_unknown_profile_404(admin_client):
    assert admin_client.get("/admin/profiles/999").status_code == 404


# ---- #11 Update user profile ---------------------------------------------
def test_TC_PUPDATE_01_name_and_description_updated(ctx):
    ok, _ = UpdateProfileController().handleUpdateProfile(3, "Homeowner", "Renovation customers", CUSTOMER)
    assert ok and UserProfile.findById(3).profileName == "Homeowner"


def test_TC_PUPDATE_02_core_profile_role_locked(ctx):
    ok, msg = UpdateProfileController().handleUpdateProfile(1, "User Admin", "x", CUSTOMER)
    assert not ok and "cannot be changed" in msg


def test_TC_PUPDATE_03_name_clash_rejected(ctx):
    ok, msg = UpdateProfileController().handleUpdateProfile(3, "User Admin", "x", CUSTOMER)
    assert not ok and "already exists" in msg


# ---- #12 Suspend user profile --------------------------------------------
def test_TC_PSUSPEND_01_suspended_profile_blocks_login(ctx):
    ok, _ = SuspendProfileController().suspendProfile(3, actingProfileId=1)
    assert ok
    ok, msg, *_ = LoginController().authenticate("customer", "password123")
    assert not ok and "profile is suspended" in msg


def test_TC_PSUSPEND_02_cannot_suspend_own_profile(ctx):
    ok, msg = SuspendProfileController().suspendProfile(1, actingProfileId=1)
    assert not ok and "logged in with" in msg


def test_TC_PSUSPEND_03_no_new_accounts_under_suspended_profile(ctx):
    SuspendProfileController().suspendProfile(3)
    ok, msg = CreateUserController().handleCreateUser("A B", "abab", "a@b.com", "secret1", 3)
    assert not ok and "suspended" in msg


def test_TC_PSUSPEND_04_reactivate_restores_login(ctx):
    SuspendProfileController().suspendProfile(3)
    SuspendProfileController().reactivateProfile(3)
    ok, *_ = LoginController().authenticate("customer", "password123")
    assert ok


# ---- #13 Search user profile ---------------------------------------------
def test_TC_PSEARCH_01_by_name_description_or_role(ctx):
    c = SearchProfileController()
    assert [p.profileId for p in c.handleSearchProfile("designer")] == [2]
    assert [p.profileId for p in c.handleSearchProfile("reports")] == [4]
    assert [p.profileId for p in c.handleSearchProfile("platform management")] == [4]


def test_TC_PSEARCH_02_no_match(ctx):
    assert SearchProfileController().handleSearchProfile("xyz") == []


def test_TC_PSEARCH_03_search_page(admin_client):
    response = admin_client.get("/admin/profiles/?q=customer")
    assert b"1 profile" in response.data


def test_TC_PSEARCH_04_empty_search_and_no_match_messages(admin_client):
    assert b"Please enter a search keyword." in admin_client.get("/admin/profiles/?q=").data
    assert b"No matching user profiles found." in admin_client.get("/admin/profiles/?q=zzz").data
