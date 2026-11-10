"""Control: CreateCategoryController - user story #42 (Platform Management creates an IDP category)."""
from entity.idp_category import IDPCategory

MAX_NAME_LENGTH = 40


class CreateCategoryController:
    def validateCategory(self, name: str, description: str, excludeCategoryId: int | None = None) -> list[str]:
        errors = []
        name = (name or "").strip()
        existing = IDPCategory.findByName(name) if name else None
        if not name:
            errors.append("Category name is required.")
        elif len(name) > MAX_NAME_LENGTH:
            errors.append(f"Category name must be {MAX_NAME_LENGTH} characters or fewer.")
        elif existing is not None and existing.categoryId != excludeCategoryId:
            errors.append(f"Category '{name}' already exists.")
        if not (description or "").strip():
            errors.append("Description is required.")
        return errors

    def createCategory(self, name: str, description: str) -> tuple[bool, str]:
        errors = self.validateCategory(name, description)
        if errors:
            return False, " ".join(errors)
        IDPCategory.create(name, description)
        return True, f"Category '{name.strip()}' created."
