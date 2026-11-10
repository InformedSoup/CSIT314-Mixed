"""Control: UpdateCategoryController - user story #44 (Platform Management updates an IDP category)."""
from control.create_category_controller import CreateCategoryController
from entity.idp_category import IDPCategory


class UpdateCategoryController:
    def validateCategoryDetails(self, categoryId: int, name: str, description: str) -> list[str]:
        return CreateCategoryController().validateCategory(name, description, excludeCategoryId=categoryId)

    def updateCategory(self, categoryId: int, name: str, description: str) -> tuple[bool, str]:
        category = IDPCategory.findById(categoryId)
        if category is None:
            return False, "Category not found."
        errors = self.validateCategoryDetails(categoryId, name, description)
        if errors:
            return False, " ".join(errors)
        category.updateDetails(name, description)
        return True, f"Category '{name.strip()}' updated."
