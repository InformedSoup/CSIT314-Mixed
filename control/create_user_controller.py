"""Control: CreateUserController - user story #4 (User Admin creates a user account)."""
from entity.user_account import UserAccount
from entity.user_profile import UserProfile

MIN_PASSWORD_LENGTH = 6


class CreateUserController:
    def validateUserDetails(self, fullName: str, username: str, email: str,
                            password: str, profileId) -> list[str]:
        """Return a list of validation errors (empty list = valid)."""
        errors = []
        if not (fullName or "").strip():
            errors.append("Full name is required.")
        if not (username or "").strip():
            errors.append("Username is required.")
        elif UserAccount.usernameExists(username):
            errors.append(f"Username '{username.strip()}' is already taken.")
        if not UserAccount.isValidEmail((email or "").strip()):
            errors.append("A valid email is required.")
        elif UserAccount.emailExists(email):
            errors.append(f"Email '{email.strip()}' is already registered.")
        if len(password or "") < MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        try:
            profile = UserProfile.findById(int(profileId))
        except (TypeError, ValueError):
            profile = None
        if profile is None:
            errors.append("Please choose a valid user profile.")
        elif not profile.isActive():
            errors.append(f"Profile '{profile.profileName}' is suspended.")
        return errors

    def handleCreateUser(self, fullName: str, username: str, email: str,
                         password: str, profileId) -> tuple[bool, str]:
        errors = self.validateUserDetails(fullName, username, email, password, profileId)
        if errors:
            return False, " ".join(errors)
        UserAccount.saveAccount(fullName, username, email, password, int(profileId))
        return True, f"User account '{username.strip()}' created."
