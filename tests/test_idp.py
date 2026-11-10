"""Sprint 3 - Interior Designer manages current IDPs (#21-#25) and past IDPs (#26-#30)."""
from datetime import date, timedelta

import pytest

from control.create_current_idp_controller import CreateCurrentIDPController
from control.create_past_idp_controller import CreatePastIDPController
from control.create_user_controller import CreateUserController
from control.delete_current_idp_controller import DeleteCurrentIDPController
from control.delete_past_idp_controller import DeletePastIDPController
from control.search_current_idps_controller import SearchCurrentIDPsController
from control.search_past_idps_controller import SearchPastIDPsController
from control.update_current_idp_controller import UpdateCurrentIDPController
from control.update_past_idp_controller import UpdatePastIDPController
from control.view_current_idp_controller import ViewCurrentIDPController
from control.view_past_idp_controller import ViewPastIDPController
from entity.idp import CurrentIDP, InteriorDesignProject, PastIDP
from entity.user_account import UserAccount
from tests.conftest import login

DESIGNER = 2
CURRENT = dict(title="Zeta Unique Loft", clientName="Mdm Quill", description="Open-plan loft",
               designStyle="Industrial", categoryId="4", imageUrl="", progress="40")
PAST = dict(title="Omega Unique Villa", clientName="Mr Wren", description="Tropical villa",
            designStyle="Tropical", categoryId="9", imageUrl="", completionDate="2023-06-15")


@pytest.fixture
def current_id(ctx):
    return CreateCurrentIDPController().handleCreateIDP(DESIGNER, CURRENT)[2]


@pytest.fixture
def past_id(ctx):
    return CreatePastIDPController().createPastIDP(DESIGNER, PAST)[2]


@pytest.fixture
def other_designer(ctx):
    CreateUserController().handleCreateUser("Other D", "otherd", "o@d.com", "secret1", 2)
    return UserAccount.findByUsername("otherd").userId


# ---- #21 Create current IDP ----------------------------------------------
def test_TC_CURCREATE_01_valid_current_idp(ctx):
    ok, _, idp_id = CreateCurrentIDPController().handleCreateIDP(DESIGNER, CURRENT)
    idp = CurrentIDP.findById(idp_id)
    assert ok and idp.status == "CURRENT" and idp.progress == 40 and idp.completionDate is None


def test_TC_CURCREATE_02_required_fields(ctx):
    errors = CreateCurrentIDPController().validateInput({"progress": "0"})
    assert len(errors) == 4  # title, client, description, category


@pytest.mark.parametrize("progress", ["-1", "100", "abc"])
def test_TC_CURCREATE_03_progress_range(ctx, progress):
    ok, msg, _ = CreateCurrentIDPController().handleCreateIDP(DESIGNER, {**CURRENT, "progress": progress})
    assert not ok and "Progress" in msg


def test_TC_CURCREATE_04_image_link_must_be_http(ctx):
    ok, msg, _ = CreateCurrentIDPController().handleCreateIDP(DESIGNER, {**CURRENT, "imageUrl": "file:///x.png"})
    assert not ok and "Image link" in msg


# ---- #22 View current IDP ------------------------------------------------
def test_TC_CURVIEW_01_owner_sees_details(current_id):
    assert ViewCurrentIDPController().getIDPDetails(current_id, DESIGNER).clientName == "Mdm Quill"


def test_TC_CURVIEW_02_past_idp_not_returned_as_current(past_id):
    assert ViewCurrentIDPController().getIDPDetails(past_id, DESIGNER) is None


def test_TC_CURVIEW_03_other_designer_gets_404(app, current_id, other_designer):
    client = app.test_client()
    login(client, "otherd", "secret1")
    assert client.get(f"/designer/projects/current/{current_id}").status_code == 404


# ---- #23 Search current IDPs ---------------------------------------------
@pytest.mark.parametrize("keyword", ["zeta unique", "Quill"])
def test_TC_CURSEARCH_01_by_title_or_client(current_id, keyword):
    assert [i.idpId for i in SearchCurrentIDPsController().searchCurrentIDPs(DESIGNER, keyword)] == [current_id]


def test_TC_CURSEARCH_02_past_idps_excluded(past_id):
    assert SearchCurrentIDPsController().searchCurrentIDPs(DESIGNER, "Omega Unique") == []


# ---- #24 Update current IDP ----------------------------------------------
def test_TC_CURUPDATE_01_progress_updated(current_id):
    ok, _ = UpdateCurrentIDPController().handleUpdateIDP(current_id, DESIGNER, {**CURRENT, "progress": "75"})
    assert ok and CurrentIDP.findById(current_id).progress == 75


def test_TC_CURUPDATE_02_mark_completed_moves_to_past(current_id):
    ok, _ = UpdateCurrentIDPController().markCompleted(current_id, DESIGNER, date.today().isoformat())
    assert ok and CurrentIDP.findById(current_id) is None
    past = PastIDP.findById(current_id)
    assert past.progress == 100 and past.completionDate == date.today().isoformat()


def test_TC_CURUPDATE_03_future_completion_rejected(current_id):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    ok, msg = UpdateCurrentIDPController().markCompleted(current_id, DESIGNER, tomorrow)
    assert not ok and "future" in msg


def test_TC_CURUPDATE_04_other_designer_cannot_update(current_id, other_designer):
    assert not UpdateCurrentIDPController().handleUpdateIDP(current_id, other_designer, CURRENT)[0]


# ---- #25 Delete current IDP ----------------------------------------------
def test_TC_CURDELETE_01_deleted(current_id):
    assert DeleteCurrentIDPController().deleteIDP(current_id, DESIGNER)[0]
    assert InteriorDesignProject.findById(current_id) is None


def test_TC_CURDELETE_02_other_designer_cannot_delete(current_id, other_designer):
    assert not DeleteCurrentIDPController().deleteIDP(current_id, other_designer)[0]


# ---- #26 Create past IDP -------------------------------------------------
def test_TC_PASTCREATE_01_valid_past_idp(ctx):
    ok, _, idp_id = CreatePastIDPController().createPastIDP(DESIGNER, PAST)
    idp = PastIDP.findById(idp_id)
    assert ok and idp.progress == 100 and idp.completionDate == "2023-06-15"


@pytest.mark.parametrize("value", ["", "15/06/2023", (date.today() + timedelta(days=3)).isoformat()])
def test_TC_PASTCREATE_02_completion_date_checked(ctx, value):
    ok, msg, _ = CreatePastIDPController().createPastIDP(DESIGNER, {**PAST, "completionDate": value})
    assert not ok and "Completion date" in msg


# ---- #27 View past IDP ---------------------------------------------------
def test_TC_PASTVIEW_01_owner_sees_details(past_id):
    assert ViewPastIDPController().getIDPDetails(past_id, DESIGNER).title == "Omega Unique Villa"


def test_TC_PASTVIEW_02_detail_page(client, past_id):
    login(client, "designer")
    assert b"Omega Unique Villa" in client.get(f"/designer/projects/past/{past_id}").data


# ---- #28 Search past IDPs by style category or completion year ------------
def test_TC_PASTSEARCH_01_by_category(past_id):
    ids = [i.idpId for i in SearchPastIDPsController().searchPastIDPs(DESIGNER, "9", None)]
    assert past_id in ids
    assert all(i.categoryId == 9 for i in SearchPastIDPsController().searchPastIDPs(DESIGNER, "9", None))


def test_TC_PASTSEARCH_02_by_year(past_id):
    results = SearchPastIDPsController().searchPastIDPs(DESIGNER, None, "2023")
    assert past_id in [i.idpId for i in results]
    assert all(i.completionDate.startswith("2023") for i in results)


def test_TC_PASTSEARCH_03_category_and_year_combined(past_id):
    assert past_id not in [i.idpId for i in SearchPastIDPsController().searchPastIDPs(DESIGNER, "9", "2019")]


# ---- #29 Update past IDP -------------------------------------------------
def test_TC_PASTUPDATE_01_description_updated(past_id):
    ok, _ = UpdatePastIDPController().handleUpdateIDP(past_id, DESIGNER, {**PAST, "description": "Refined"})
    assert ok and PastIDP.findById(past_id).description == "Refined"


def test_TC_PASTUPDATE_02_invalid_rejected(past_id):
    assert not UpdatePastIDPController().handleUpdateIDP(past_id, DESIGNER, {**PAST, "title": ""})[0]


# ---- #30 Delete past IDP -------------------------------------------------
def test_TC_PASTDELETE_01_deleted_via_page(client, past_id):
    login(client, "designer")
    client.post(f"/designer/projects/past/{past_id}/delete")
    assert client.get(f"/designer/projects/past/{past_id}").status_code == 404


def test_TC_PASTDELETE_02_other_designer_cannot_delete(past_id, other_designer):
    assert not DeletePastIDPController().deleteIDP(past_id, other_designer)[0]
