"""Entity: UserSession - a record of one login, closed on logout."""
from __future__ import annotations

from dataclasses import dataclass

from db import get_connection


@dataclass
class UserSession:
    sessionId: int
    accountId: int
    loginAt: str
    logoutAt: str | None

    @classmethod
    def createSession(cls, accountId: int) -> "UserSession":
        connection = get_connection()
        cursor = connection.execute(
            "INSERT INTO user_session (account_id) VALUES (?)", (accountId,)
        )
        connection.commit()
        return cls.findById(cursor.lastrowid)

    @classmethod
    def findById(cls, sessionId: int) -> "UserSession | None":
        row = get_connection().execute(
            "SELECT * FROM user_session WHERE session_id = ?", (sessionId,)
        ).fetchone()
        if not row:
            return None
        return cls(row["session_id"], row["account_id"], row["login_at"], row["logout_at"])

    def endSession(self) -> bool:
        """Mark the session as logged out. Returns False if it was already closed."""
        if self.logoutAt is not None:
            return False
        connection = get_connection()
        connection.execute(
            "UPDATE user_session SET logout_at = datetime('now', 'localtime') WHERE session_id = ?",
            (self.sessionId,),
        )
        connection.commit()
        return True
