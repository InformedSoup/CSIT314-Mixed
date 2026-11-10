"""Sprint 3 - IDP category view/update/delete/search (#43-#46) and reports (#47-#49).

Report tests use dates in 2020, where the seed data has no activity, so counts are exact.
"""
from datetime import date, timedelta

import pytest

from control.create_category_controller import CreateCategoryController
from control.daily_report_controller import DailyReportController
from control.delete_category_controller import DeleteCategoryController
from control.monthly_report_controller import MonthlyReportController
from control.search_category_controller import SearchCategoryController
from control.update_category_controller import UpdateCategoryController
from control.view_category_controller import ViewCategoryController
from control.weekly_report_controller import WeeklyReportController
from db import get_connection
from entity.idp_category import IDPCategory
from tests.conftest import login


@pytest.fixture
def unused_id(ctx):
    CreateCategoryController().createCategory("Coastal", "Light blues and natural textures")
    return IDPCategory.findByName("Coastal").categoryId


@pytest.fixture
def used_id(ctx):
    """A category with at least one IDP filed under it."""
    row = get_connection().execute("SELECT category_id FROM idp WHERE category_id IS NOT NULL LIMIT 1").fetchone()
    return row[0]


# ---- #43 View category ---------------------------------------------------
def test_TC_CATVIEW_01_details(unused_id):
    category = ViewCategoryController().getCategoryDetails(unused_id)
    assert category.name == "Coastal" and category.idpCount == 0


def test_TC_CATVIEW_02_detail_page(client, unused_id):
    login(client, "platform")
    assert b"Light blues" in client.get(f"/platform/categories/{unused_id}").data


# ---- #44 Update category -------------------------------------------------
def test_TC_CATUPDATE_01_updated(unused_id):
    ok, _ = UpdateCategoryController().updateCategory(unused_id, "Coastal Calm", "Sea-inspired homes")
    assert ok and IDPCategory.findById(unused_id).name == "Coastal Calm"


def test_TC_CATUPDATE_02_keep_same_name_allowed(unused_id):
    assert UpdateCategoryController().updateCategory(unused_id, "Coastal", "New description")[0]


def test_TC_CATUPDATE_03_name_clash_rejected(unused_id):
    ok, msg = UpdateCategoryController().updateCategory(unused_id, "Japandi", "x")
    assert not ok and "already exists" in msg


# ---- #45 Delete category -------------------------------------------------
def test_TC_CATDELETE_01_unused_deleted(unused_id):
    assert DeleteCategoryController().deleteCategory(unused_id)[0]
    assert IDPCategory.findById(unused_id) is None


def test_TC_CATDELETE_02_in_use_blocked(used_id):
    ok, msg = DeleteCategoryController().deleteCategory(used_id)
    assert not ok and "Only unused categories" in msg
    assert IDPCategory.findById(used_id) is not None


# ---- #46 Search category -------------------------------------------------
def test_TC_CATSEARCH_01_by_name_or_description(ctx):
    names = [c.name for c in SearchCategoryController().searchCategories("japandi kitchen")]
    assert names == ["Japandi Kitchen"]
    assert any(c.name == "Industrial" for c in SearchCategoryController().searchCategories("exposed brick"))


def test_TC_CATSEARCH_02_no_match(ctx):
    assert SearchCategoryController().searchCategories("zzz") == []


# ---- #47-#49 Reports -----------------------------------------------------
def add_activity(day: str, views: int = 0, logins: int = 0, shortlists: int = 0):
    connection = get_connection()
    idp_ids = [r[0] for r in connection.execute("SELECT idp_id FROM idp LIMIT 20")]
    connection.executemany("INSERT INTO idp_view (idp_id, customer_id, viewed_at) VALUES (?, 3, ?)",
                           [(idp_ids[0], f"{day} 10:00:00")] * views)
    connection.executemany("INSERT INTO user_session (account_id, login_at) VALUES (?, ?)",
                           [((n % 4) + 1, f"{day} 09:00:00") for n in range(logins)])
    connection.executemany("INSERT INTO favourite (customer_id, idp_id, saved_at) VALUES (3, ?, ?)",
                           [(idp_ids[n + 1], f"{day} 11:00:00") for n in range(shortlists)])
    connection.commit()


def test_TC_DAILY_01_counts_for_one_day(ctx):
    add_activity("2020-03-10", views=7, logins=5, shortlists=2)
    add_activity("2020-03-11", views=100)  # next day must not leak in
    ok, _, report = DailyReportController().generateDailyReport("2020-03-10")
    assert ok
    assert (report.totals["views"], report.totals["logins"], report.totals["shortlists"]) == (7, 5, 2)
    assert report.activeUsers == 4
    assert report.topIDPs[0]["views"] == 7


def test_TC_DAILY_02_change_vs_previous_day(ctx):
    add_activity("2020-03-09", views=4)
    add_activity("2020-03-10", views=6)
    _, _, report = DailyReportController().generateDailyReport("2020-03-10")
    assert report.change("views") == 50


@pytest.mark.parametrize("value", ["", "2020-02-30", (date.today() + timedelta(days=1)).isoformat()])
def test_TC_DAILY_03_invalid_or_future_date(ctx, value):
    assert not DailyReportController().generateDailyReport(value)[0]


def test_TC_WEEKLY_01_any_date_maps_to_its_monday_to_sunday_week(ctx):
    add_activity("2020-03-09", views=3)   # Monday
    add_activity("2020-03-15", views=2)   # Sunday
    add_activity("2020-03-16", views=50)  # next Monday - excluded
    ok, _, report = WeeklyReportController().generateWeeklyReport("2020-03-12")  # a Thursday
    assert ok and report.start == date(2020, 3, 9) and report.end == date(2020, 3, 15)
    assert len(report.days) == 7 and report.totals["views"] == 5


def test_TC_MONTHLY_01_whole_month_including_leap_day(ctx):
    add_activity("2020-02-01", views=1)
    add_activity("2020-02-29", views=2)
    add_activity("2020-03-01", views=40)
    ok, _, report = MonthlyReportController().generateMonthlyReport("2020-02")
    assert ok and len(report.days) == 29 and report.totals["views"] == 3


def test_TC_MONTHLY_02_invalid_month(ctx):
    assert not MonthlyReportController().generateMonthlyReport("2020-13")[0]


def test_TC_REPORT_01_report_page_each_type(client):
    login(client, "platform")
    for kind in ("daily", "weekly", "monthly"):
        page = client.get(f"/platform/reports/?type={kind}")
        assert page.status_code == 200 and b"Project views" in page.data
