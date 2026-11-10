"""Control: ViewUserController - user story #5 (User Admin views user accounts)."""
from entity.user_account import UserAccount


class ViewUserController:
    def getUserAccounts(self) -> list[UserAccount]:
        return UserAccount.getAllAccounts()

    def getUserAccount(self, userId: int) -> UserAccount | None:
        return UserAccount.findById(userId)
