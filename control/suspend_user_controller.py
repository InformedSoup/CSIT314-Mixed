"""Control: SuspendUserController - user story #7 (User Admin suspends a user account)."""
from entity.user_account import UserAccount


class SuspendUserController:
    def suspendUser(self, userId: int, actingUserId: int | None = None) -> tuple[bool, str]:
        account = UserAccount.findById(userId)
        if account is None:
            return False, "User account not found."
        if actingUserId is not None and account.userId == actingUserId:
            return False, "You cannot suspend your own account."
        if not account.isActive():
            return False, f"'{account.username}' is already suspended."
        account.setStatus("SUSPENDED")
        return True, f"'{account.username}' has been suspended."

    def reactivateUser(self, userId: int) -> tuple[bool, str]:
        account = UserAccount.findById(userId)
        if account is None:
            return False, "User account not found."
        if account.isActive():
            return False, f"'{account.username}' is already active."
        account.setStatus("ACTIVE")
        return True, f"'{account.username}' has been reactivated."
