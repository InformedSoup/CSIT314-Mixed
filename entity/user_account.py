"""Entity: UserAccount - a person who can log in to the platform."""
from __future__ import annotations

import re
from dataclasses import dataclass

from werkzeug.security import check_password_hash, generate_password_hash

from db import get_connection

STATUSES = ("ACTIVE", "SUSPENDED")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_SELECT = """
    SELECT a.*, p.profile_name, p.role, p.status AS profile_status
    FROM user_account a JOIN user_profile p ON p.profile_id = a.profile_id
"""


@dataclass
class UserAccount:
    userId: int
    fullName: str
    username: str
    email: str
    passwordHash: str
    profileId: int
    profileName: str
    status: str
    createdAt: str
    profileStatus: str = "ACTIVE"
    role: str = ""

    @classmethod
    def _fromRow(cls, row) -> "UserAccount":
        return cls(
            userId=row["account_id"],
            fullName=row["full_name"],
            username=row["username"],
            email=row["email"],
            passwordHash=row["password_hash"],
            profileId=row["profile_id"],
            profileName=row["profile_name"],
            status=row["status"],
            createdAt=row["created_at"],
            profileStatus=row["profile_status"],
            role=row["role"],
        )

    # ---- validation helpers -------------------------------------------------
    @staticmethod
    def isValidEmail(email: str) -> bool:
        return bool(EMAIL_PATTERN.match(email or ""))

    def validatePassword(self, password: str) -> bool:
        return check_password_hash(self.passwordHash, password or "")

    def isActive(self) -> bool:
        return self.status == "ACTIVE"

    @classmethod
    def usernameExists(cls, username: str, excludeUserId: int | None = None) -> bool:
        row = get_connection().execute(
            "SELECT 1 FROM user_account WHERE username = ? AND account_id IS NOT ?",
            (username.strip(), excludeUserId),
        ).fetchone()
        return row is not None

    @classmethod
    def emailExists(cls, email: str, excludeUserId: int | None = None) -> bool:
        row = get_connection().execute(
            "SELECT 1 FROM user_account WHERE email = ? AND account_id IS NOT ?",
            (email.strip(), excludeUserId),
        ).fetchone()
        return row is not None

    # ---- create / read ------------------------------------------------------
    @classmethod
    def saveAccount(cls, fullName: str, username: str, email: str, password: str,
                    profileId: int) -> int:
        """Insert a new account and return its id."""
        connection = get_connection()
        cursor = connection.execute(
            """INSERT INTO user_account (full_name, username, email, password_hash, profile_id)
               VALUES (?, ?, ?, ?, ?)""",
            (fullName.strip(), username.strip(), email.strip(),
             generate_password_hash(password), profileId),
        )
        connection.commit()
        return cursor.lastrowid

    @classmethod
    def findById(cls, userId: int) -> "UserAccount | None":
        row = get_connection().execute(_SELECT + " WHERE a.account_id = ?", (userId,)).fetchone()
        return cls._fromRow(row) if row else None

    @classmethod
    def findByUsername(cls, username: str) -> "UserAccount | None":
        row = get_connection().execute(
            _SELECT + " WHERE a.username = ? COLLATE NOCASE", ((username or "").strip(),)
        ).fetchone()
        return cls._fromRow(row) if row else None

    @classmethod
    def getAllAccounts(cls) -> list["UserAccount"]:
        rows = get_connection().execute(_SELECT + " ORDER BY a.account_id").fetchall()
        return [cls._fromRow(r) for r in rows]

    @classmethod
    def searchAccounts(cls, keyword: str) -> list["UserAccount"]:
        """Match keyword against name, username, email or profile name."""
        like = f"%{keyword.strip()}%"
        rows = get_connection().execute(
            _SELECT + """ WHERE a.full_name LIKE ? OR a.username LIKE ?
                          OR a.email LIKE ? OR p.profile_name LIKE ?
                          ORDER BY a.account_id""",
            (like, like, like, like),
        ).fetchall()
        return [cls._fromRow(r) for r in rows]

    # ---- update -------------------------------------------------------------
    def updateAccount(self, fullName: str, email: str, profileId: int,
                      newPassword: str | None = None) -> bool:
        connection = get_connection()
        if newPassword:
            connection.execute(
                """UPDATE user_account SET full_name = ?, email = ?, profile_id = ?,
                   password_hash = ? WHERE account_id = ?""",
                (fullName.strip(), email.strip(), profileId,
                 generate_password_hash(newPassword), self.userId),
            )
        else:
            connection.execute(
                "UPDATE user_account SET full_name = ?, email = ?, profile_id = ? WHERE account_id = ?",
                (fullName.strip(), email.strip(), profileId, self.userId),
            )
        connection.commit()
        return True

    def setStatus(self, status: str) -> bool:
        if status not in STATUSES:
            raise ValueError("Invalid account status.")
        connection = get_connection()
        connection.execute(
            "UPDATE user_account SET status = ? WHERE account_id = ?", (status, self.userId)
        )
        connection.commit()
        self.status = status
        return True
