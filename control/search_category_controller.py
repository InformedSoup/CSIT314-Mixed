"""Control: SearchCategoryController - user story #46 (Platform Management searches IDP categories)."""
from entity.idp_category import IDPCategory


class SearchCategoryController:
    def searchCategories(self, keyword: str) -> list[IDPCategory]:
        if not (keyword or "").strip():
            return IDPCategory.getAllCategories()
        return IDPCategory.searchCategories(keyword)
