"""Sprint 3 - Customer search, view and favourites (#33-#37) and designer tracking (#38-#39)."""
import pytest

from control.create_current_idp_controller import CreateCurrentIDPController
from control.favourite_list_controller import FavouriteListController
from control.save_favourite_controller import SaveFavouriteController
from control.search_idp_controller import SearchIDPController
from control.suspend_user_controller import SuspendUserController
from control.track_idp_shortlists_controller import TrackIDPShortlistsController
from control.track_idp_views_controller import TrackIDPViewsController
from control.view_favourite_list_controller import ViewFavouriteListController
from control.view_idp_controller import ViewIDPController
from db import get_connection
from entity.idp import InteriorDesignProject
from tests.conftest import login

DESIGNER, CUSTOMER = 2, 3
IDP = dict(title="Kappa Distinct Studio", clientName="Ms Lark", description="Warm Japandi studio",
           designStyle="Japandi", categoryId="2", imageUrl="", progress="30")


@pytest.fixture
def idp_id(ctx):
    return CreateCurrentIDPController().handleCreateIDP(DESIGNER, IDP)[2]


def views_of(idp_id):
    return InteriorDesignProject.findById(idp_id).viewCount


# ---- #33 Search IDPs -----------------------------------------------------
@pytest.mark.parametrize("keyword", ["kappa distinct", "warm japandi", "Daniel Designer"])
def test_TC_ISEARCH_01_keyword_matches_title_description_designer(idp_id, keyword):
    ok, _, results = SearchIDPController().handleSearch(keyword)
    assert ok and idp_id in [i.idpId for i in results]


def test_TC_ISEARCH_02_category_and_status_filters(idp_id):
    _, _, results = SearchIDPController().handleSearch("", "2", "CURRENT")
    assert idp_id in [i.idpId for i in results]
    assert all(i.categoryId == 2 and i.status == "CURRENT" for i in results)
    _, _, past_only = SearchIDPController().handleSearch("Kappa Distinct", None, "PAST")
    assert past_only == []


def test_TC_ISEARCH_03_overlong_query_rejected(ctx):
    ok, msg, _ = SearchIDPController().handleSearch("x" * 101)
    assert not ok and "100 characters" in msg


def test_TC_ISEARCH_04_suspended_designers_hidden(idp_id):
    SuspendUserController().suspendUser(DESIGNER)
    _, _, results = SearchIDPController().handleSearch("Kappa Distinct")
    assert results == []


# ---- #34 View IDP --------------------------------------------------------
def test_TC_IVIEW_01_view_shows_idp_and_company(idp_id):
    idp, companies = ViewIDPController().getIDPDetails(idp_id, CUSTOMER)
    assert idp.title == "Kappa Distinct Studio"
    assert all(c.designerId == DESIGNER for c in companies)


def test_TC_IVIEW_02_view_is_recorded_once_per_window(idp_id):
    before = views_of(idp_id)
    ViewIDPController().getIDPDetails(idp_id, CUSTOMER)
    ViewIDPController().getIDPDetails(idp_id, CUSTOMER)  # refresh: not counted again
    assert views_of(idp_id) == before + 1


def test_TC_IVIEW_03_suspended_designer_idp_not_viewable(idp_id):
    SuspendUserController().suspendUser(DESIGNER)
    assert ViewIDPController().getIDPDetails(idp_id, CUSTOMER) == (None, [])


def test_TC_IVIEW_04_view_page(client, idp_id):
    login(client, "customer")
    page = client.get(f"/customer/idps/{idp_id}")
    assert page.status_code == 200 and b"Kappa Distinct Studio" in page.data


# ---- #35 Save to favourites ----------------------------------------------
def test_TC_FSAVE_01_saved_and_counted_as_shortlist(idp_id):
    ok, _ = SaveFavouriteController().saveIDP(CUSTOMER, idp_id)
    assert ok and InteriorDesignProject.findById(idp_id).shortlistCount == 1


def test_TC_FSAVE_02_duplicate_save_rejected(idp_id):
    SaveFavouriteController().saveIDP(CUSTOMER, idp_id)
    ok, msg = SaveFavouriteController().saveIDP(CUSTOMER, idp_id)
    assert not ok and "already" in msg


def test_TC_FSAVE_03_unknown_idp(ctx):
    assert not SaveFavouriteController().saveIDP(CUSTOMER, 99999)[0]


def test_TC_FSAVE_04_remove(idp_id):
    SaveFavouriteController().saveIDP(CUSTOMER, idp_id)
    assert SaveFavouriteController().removeIDP(CUSTOMER, idp_id)[0]
    assert not SaveFavouriteController().isSaved(CUSTOMER, idp_id)


# ---- #36 View favourite list ---------------------------------------------
def test_TC_FLIST_01_newest_saved_first(idp_id):
    SaveFavouriteController().saveIDP(CUSTOMER, idp_id)
    favourites = ViewFavouriteListController().getFavouriteList(CUSTOMER)
    assert favourites[0].idpId == idp_id


def test_TC_FLIST_02_lists_are_per_customer(idp_id):
    SaveFavouriteController().saveIDP(CUSTOMER, idp_id)
    assert idp_id not in [i.idpId for i in ViewFavouriteListController().getFavouriteList(1)]


# ---- #37 View IDP from favourite list ------------------------------------
def test_TC_FVIEW_01_saved_idp_opens(idp_id):
    SaveFavouriteController().saveIDP(CUSTOMER, idp_id)
    idp, _ = FavouriteListController().getIDPDetails(CUSTOMER, idp_id)
    assert idp.idpId == idp_id


def test_TC_FVIEW_02_unsaved_idp_404_on_favourites_route(client, idp_id):
    login(client, "customer")
    assert client.get(f"/customer/favourites/{idp_id}").status_code == 404


# ---- #38 / #39 Track views and shortlists --------------------------------
def test_TC_TRACK_01_views_sorted_most_first(idp_id):
    get_connection().executemany("INSERT INTO idp_view (idp_id, customer_id) VALUES (?, ?)", [(idp_id, CUSTOMER)] * 500)
    get_connection().commit()
    top = TrackIDPViewsController().getViewCounts(DESIGNER)[0]
    assert top.idpId == idp_id and top.viewCount == 500


def test_TC_TRACK_02_shortlists_sorted_most_first(idp_id):
    connection = get_connection()
    connection.executemany("INSERT INTO favourite (customer_id, idp_id) VALUES (?, ?)",
                           [(c, idp_id) for c in range(1, 15) if c != DESIGNER])
    connection.commit()
    top = TrackIDPShortlistsController().getShortlistCounts(DESIGNER)[0]
    assert top.idpId == idp_id and top.shortlistCount == 13


def test_TC_TRACK_03_totals_match_rows(idp_id):
    c = TrackIDPViewsController()
    assert c.getTotalViews(DESIGNER) == sum(i.viewCount for i in c.getViewCounts(DESIGNER))


def test_TC_TRACK_04_insights_page(client, idp_id):
    login(client, "designer")
    page = client.get("/designer/insights/?sort=shortlists")
    assert page.status_code == 200 and b"Most shortlisted" in page.data
