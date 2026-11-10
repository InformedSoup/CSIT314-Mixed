"""Control: LoginController - user stories #2, #14, #31, #40 (log in, all four roles)."""
from __future__ import annotations

from entity.user_account import UserAccount
from entity.user_profile import UserProfile
from entity.user_session import UserSession

INVALID_LOGIN = "Invalid username or password."


class LoginController:
    def authenticate(self, username: str, password: str
                     ) -> tuple[bool, str, UserAccount | None, UserSession | None]:
        """Check credentials and account/profile status, then open a session.

        Returns (success, message, account, session).
        """
        if not (username or "").strip() or not password:
            return False, "Username and password are required.", None, None

        account = UserAccount.findByUsername(username)
        if account is None or not account.validatePassword(password):
            return False, INVALID_LOGIN, None, None
        if not account.isActive():
            return False, "This account has been suspended. Please contact the User Admin.", None, None

        profile = UserProfile.findById(account.profileId)
        if profile is None or not profile.isActive():
            return False, "Your user profile is suspended. Please contact the User Admin.", None, None

        session = UserSession.createSession(account.userId)
        return True, f"Welcome, {account.fullName}.", account, session
