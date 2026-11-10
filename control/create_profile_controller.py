"""Control: CreateProfileController - user story #9 (User Admin creates a user profile)."""
from entity.user_profile import ROLES, UserProfile

MAX_NAME_LENGTH = 50


class CreateProfileController:
    def validateDetail(self, profileName: str, description: str, role: str,
                       excludeProfileId: int | None = None) -> list[str]:
        errors = []
        name = (profileName or "").strip()
        if not name:
            errors.append("Profile name is required.")
        elif len(name) > MAX_NAME_LENGTH:
            errors.append(f"Profile name must be {MAX_NAME_LENGTH} characters or fewer.")
        elif UserProfile.nameExists(name, excludeProfileId):
            errors.append(f"A profile called '{name}' already exists.")
        if not (description or "").strip():
            errors.append("Description is required.")
        if role not in ROLES:
            errors.append("Please choose a valid role.")
        return errors

    def createProfile(self, profileName: str, description: str, role: str) -> tuple[bool, str]:
        errors = self.validateDetail(profileName, description, role)
        if errors:
            return False, " ".join(errors)
        UserProfile.save(profileName, description, role)
        return True, f"User profile '{profileName.strip()}' created."
