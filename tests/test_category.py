"""Sprint 2 - Platform Management creates IDP categories (#42)."""
from control.create_category_controller import CreateCategoryController
from entity.idp_category import IDPCategory
from tests.conftest import login


def test_TC_CATCREATE_01_valid_category_saved(ctx):
    ok, _ = CreateCategoryController().createCategory("Coastal", "Light blues and natural textures")
    assert ok and IDPCategory.findByName("coastal") is not None


def test_TC_CATCREATE_02_duplicate_name_rejected_case_insensitive(ctx):
    ok, msg = CreateCategoryController().createCategory("scandinavian", "dup")
    assert not ok and "already exists" in msg


def test_TC_CATCREATE_03_missing_fields(ctx):
    assert len(CreateCategoryController().validateCategory("", "")) == 2


def test_TC_CATCREATE_04_name_too_long(ctx):
    ok, msg = CreateCategoryController().createCategory("x" * 41, "desc")
    assert not ok and "40 characters" in msg


def test_TC_CATCREATE_05_page_flow_and_access(client):
    login(client, "platform")
    response = client.post("/platform/categories/create", data={"name": "Coastal", "description": "d"})
    assert response.status_code == 302
    assert b"Coastal" in client.get("/platform/categories/").data
    client.post("/logout")
    login(client, "customer")
    assert client.get("/platform/categories/create").status_code == 302  # customers are bounced
