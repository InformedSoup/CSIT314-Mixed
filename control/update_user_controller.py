"""Control: UpdateUserController - user story #6 (User Admin updates a user account)."""
from entity.user_account import UserAccount
from entity.user_profile import UserProfile
from control.create_user_controller import MIN_PASSWORD_LENGTH


class UpdateUserController:
    def validateUpdate(self, userId: int, fullName: str, email: str, profileId,
                       newPassword: str | None) -> list[str]:
        errors = []
        if not (fullName or "").strip():
            errors.append("Full name is required.")
        if not UserAccount.isValidEmail((email or "").strip()):
            errors.append("A valid email is required.")
        elif UserAccount.emailExists(email, excludeUserId=userId):
            errors.append(f"Email '{email.strip()}' is already registered.")
        if newPassword and len(newPassword) < MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        try:
            if UserProfile.findById(int(profileId)) is None:
                errors.append("Please choose a valid user profile.")
        except (TypeError, ValueError):
            errors.append("Please choose a valid user profile.")
        return errors

    def handleUpdateUser(self, userId: int, fullName: str, email: str, profileId,
                         newPassword: str | None = None) -> tuple[bool, str]:
        account = UserAccount.findById(userId)
        if account is None:
            return False, "User account not found."
        errors = self.validateUpdate(userId, fullName, email, profileId, newPassword)
        if errors:
            return False, " ".join(errors)
        account.updateAccount(fullName, email, int(profileId), newPassword or None)
        return True, f"User account '{account.username}' updated."
