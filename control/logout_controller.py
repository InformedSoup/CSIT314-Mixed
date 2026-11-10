"""Control: LogoutController - user stories #3, #15, #32, #41 (log out, all four roles)."""
from entity.user_session import UserSession


class LogoutController:
    def logout(self, sessionId: int | None) -> tuple[bool, str]:
        session = UserSession.findById(sessionId) if sessionId else None
        if session is None:
            return False, "No active session found."
        session.endSession()
        return True, "You have been logged out."
