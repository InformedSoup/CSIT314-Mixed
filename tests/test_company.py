"""Sprint 2 - Interior Designer manages company information.

User stories: #16 create, #17 view, #18 update, #19 delete, #20 search
Demo designer is account 2; a second designer is created to test ownership.
"""
import pytest

from control.company_info_controller import CompanyInfoController
from control.create_company_controller import CreateCompanyController
from control.create_user_controller import CreateUserController
from control.delete_company_controller import DeleteCompanyController
from control.search_company_controller import SearchCompanyController
from control.update_company_controller import UpdateCompanyController
from entity.company import Company
from tests.conftest import login

DESIGNER = 2
VALID = dict(companyName="Oak Atelier", regNumber="201912345K", description="Scandinavian homes",
             address="10 Ubi Avenue 1, Singapore 408930", contactNumber="6123 4567")


@pytest.fixture
def company_id(ctx):
    _, _, cid = CreateCompanyController().createCompany(DESIGNER, **VALID)
    return cid


@pytest.fixture
def other_designer(ctx):
    CreateUserController().handleCreateUser("Other D", "otherd", "o@d.com", "secret1", 2)
    from entity.user_account import UserAccount
    return UserAccount.findByUsername("otherd").userId


@pytest.fixture
def designer_client(client):
    login(client, "designer")
    return client


# ---- #16 Create ----------------------------------------------------------
def test_TC_CCREATE_01_valid_company_saved(ctx):
    before = len(Company.findByDesigner(DESIGNER))
    ok, _, cid = CreateCompanyController().createCompany(DESIGNER, **VALID)
    assert ok and len(Company.findByDesigner(DESIGNER)) == before + 1
    assert Company.findById(cid).regNumber == "201912345K"


@pytest.mark.parametrize("uen", ["12345", "ABCDEFGHI", "2019123456"])
def test_TC_CCREATE_02_invalid_uen_rejected(ctx, uen):
    ok, msg, _ = CreateCompanyController().createCompany(DESIGNER, **{**VALID, "regNumber": uen})
    assert not ok and "UEN" in msg


def test_TC_CCREATE_03_duplicate_uen_rejected(company_id):
    ok, msg, _ = CreateCompanyController().createCompany(DESIGNER, **{**VALID, "companyName": "Other"})
    assert not ok and "already registered" in msg


@pytest.mark.parametrize("phone,valid", [("6123 4567", True), ("+65 9123 4567", True),
                                         ("81234567", True), ("1234 5678", False), ("612", False)])
def test_TC_CCREATE_04_contact_number_format(ctx, phone, valid):
    errors = CreateCompanyController().validateCompanyDetails("A", "202012345A", "d", "a", phone)
    assert (errors == []) is valid


def test_TC_CCREATE_05_create_page_flow(designer_client):
    response = designer_client.post("/designer/companies/create", data=VALID)
    assert response.status_code == 302
    assert b"Oak Atelier" in designer_client.get(response.headers["Location"]).data


# ---- #17 View ------------------------------------------------------------
def test_TC_CVIEW_01_owner_can_view(company_id):
    assert CompanyInfoController().getCompanyInfo(company_id, DESIGNER).companyName == "Oak Atelier"


def test_TC_CVIEW_02_other_designer_cannot_view(company_id, other_designer):
    assert CompanyInfoController().getCompanyInfo(company_id, other_designer) is None


def test_TC_CVIEW_03_other_designers_company_404(app, company_id, other_designer):
    client = app.test_client()
    login(client, "otherd", "secret1")
    assert client.get(f"/designer/companies/{company_id}").status_code == 404


# ---- #18 Update ----------------------------------------------------------
def test_TC_CUPDATE_01_details_updated(company_id):
    ok, _ = UpdateCompanyController().handleUpdate(company_id, DESIGNER,
                                                   {**VALID, "companyName": "Oak & Linen"})
    assert ok and Company.findById(company_id).companyName == "Oak & Linen"


def test_TC_CUPDATE_02_keep_own_uen_allowed(company_id):
    ok, _ = UpdateCompanyController().handleUpdate(company_id, DESIGNER, VALID)
    assert ok


def test_TC_CUPDATE_03_invalid_input_rejected(company_id):
    ok, msg = UpdateCompanyController().handleUpdate(company_id, DESIGNER, {**VALID, "address": ""})
    assert not ok and "Address" in msg


def test_TC_CUPDATE_04_cannot_update_others_company(company_id, other_designer):
    ok, _ = UpdateCompanyController().handleUpdate(company_id, other_designer, VALID)
    assert not ok


# ---- #19 Delete ----------------------------------------------------------
def test_TC_CDELETE_01_owner_deletes(company_id):
    ok, _ = DeleteCompanyController().deleteCompany(company_id, DESIGNER)
    assert ok and Company.findById(company_id) is None


def test_TC_CDELETE_02_cannot_delete_others_company(company_id, other_designer):
    ok, _ = DeleteCompanyController().deleteCompany(company_id, other_designer)
    assert not ok and Company.findById(company_id) is not None


def test_TC_CDELETE_03_confirmation_then_delete(designer_client, company_id):
    assert b"cannot be undone" in designer_client.get(f"/designer/companies/{company_id}/delete").data
    designer_client.post(f"/designer/companies/{company_id}/delete")
    assert designer_client.get(f"/designer/companies/{company_id}").status_code == 404


# ---- #20 Search ----------------------------------------------------------
def test_TC_CSEARCH_01_by_name_uen_or_address(company_id):
    c = SearchCompanyController()
    for keyword in ("oak", "201912345", "Ubi"):
        assert company_id in [x.companyId for x in c.handleSearchCompany(DESIGNER, keyword)]


def test_TC_CSEARCH_02_only_own_companies_returned(company_id, other_designer):
    assert SearchCompanyController().handleSearchCompany(other_designer, "Oak") == []


def test_TC_CSEARCH_03_no_match(company_id):
    assert SearchCompanyController().handleSearchCompany(DESIGNER, "zzz") == []


def test_TC_CSEARCH_04_empty_search_and_no_match_messages(designer_client):
    assert b"Please enter a search keyword." in designer_client.get("/designer/companies/?q=").data
    assert b"No matching company records found." in designer_client.get("/designer/companies/?q=zzz").data
