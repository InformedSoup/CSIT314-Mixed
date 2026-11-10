"""Control: DeleteCategoryController - user story #45 (Platform Management deletes an unused IDP category).

A category that still has IDPs filed under it cannot be deleted, so no project loses its category.
"""
from entity.idp_category import IDPCategory


class DeleteCategoryController:
    def canDelete(self, categoryId: int) -> tuple[bool, str]:
        category = IDPCategory.findById(categoryId)
        if category is None:
            return False, "Category not found."
        if category.isInUse():
            return False, (f"'{category.name}' still has {category.idpCount} project(s). "
                           "Only unused categories can be deleted.")
        return True, ""

    def deleteCategory(self, categoryId: int) -> tuple[bool, str]:
        ok, reason = self.canDelete(categoryId)
        if not ok:
            return False, reason
        category = IDPCategory.findById(categoryId)
        category.delete()
        return True, f"Category '{category.name}' deleted."
