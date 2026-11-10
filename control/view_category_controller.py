"""Control: ViewCategoryController - user story #43 (Platform Management views an IDP category)."""
from entity.idp_category import IDPCategory


class ViewCategoryController:
    def getAllCategories(self) -> list[IDPCategory]:
        return IDPCategory.getAllCategories()

    def getCategoryDetails(self, categoryId: int) -> IDPCategory | None:
        return IDPCategory.findById(categoryId)
