"""Validation rules shared by the create/update controllers for current and past IDPs."""
from datetime import date

from entity.idp_category import IDPCategory

MAX_TITLE = 100


def validate_idp(details: dict, kind: str) -> list[str]:
    """kind is 'CURRENT' or 'PAST'. Returns a list of error messages."""
    errors = []
    title = (details.get("title") or "").strip()
    if not title:
        errors.append("Title is required.")
    elif len(title) > MAX_TITLE:
        errors.append(f"Title must be {MAX_TITLE} characters or fewer.")
    if not (details.get("clientName") or "").strip():
        errors.append("Client name is required.")
    if not (details.get("description") or "").strip():
        errors.append("Description is required.")

    try:
        category = IDPCategory.findById(int(details.get("categoryId")))
    except (TypeError, ValueError):
        category = None
    if category is None:
        errors.append("Please choose a category.")

    image = (details.get("imageUrl") or "").strip()
    if image and not image.startswith(("http://", "https://")):
        errors.append("Image link must start with http:// or https://.")

    if kind == "CURRENT":
        try:
            progress = int(details.get("progress", 0) or 0)
            if not 0 <= progress <= 99:
                errors.append("Progress must be between 0 and 99% (mark the project completed to finish it).")
        except (TypeError, ValueError):
            errors.append("Progress must be a whole number.")
    else:
        errors += validate_completion_date(details.get("completionDate"))
    return errors


def validate_completion_date(value) -> list[str]:
    try:
        completed = date.fromisoformat((value or "").strip())
    except ValueError:
        return ["Completion date is required (YYYY-MM-DD)."]
    if completed > date.today():
        return ["Completion date cannot be in the future."]
    return []
