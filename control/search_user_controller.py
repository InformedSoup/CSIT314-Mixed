"""Control: SearchUserController - user story #8 (User Admin searches user accounts)."""
from entity.user_account import UserAccount


class SearchUserController:
    def searchUsers(self, keyword: str) -> list[UserAccount]:
        if not (keyword or "").strip():
            return UserAccount.getAllAccounts()
        return UserAccount.searchAccounts(keyword)
