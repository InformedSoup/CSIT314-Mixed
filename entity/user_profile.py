"""Entity: UserProfile - a named profile that grants one of four base roles.

The four core profiles (ids 1-4) always exist. User Admin can create more,
e.g. "Premium Customer" with the CUSTOMER role.
"""
from __future__ import annotations

from dataclasses import dataclass

from db import get_connection

# Base roles - access control is checked against these.
USER_ADMIN = "USER_ADMIN"
INTERIOR_DESIGNER = "INTERIOR_DESIGNER"
CUSTOMER = "CUSTOMER"
PLATFORM_MANAGEMENT = "PLATFORM_MANAGEMENT"
ROLES = {
    USER_ADMIN: "User Admin",
    INTERIOR_DESIGNER: "Interior Designer",
    CUSTOMER: "Customer",
    PLATFORM_MANAGEMENT: "Platform Management",
}
CORE_PROFILE_IDS = (1, 2, 3, 4)

_SELECT = """
    SELECT p.*, (SELECT COUNT(*) FROM user_account a WHERE a.profile_id = p.profile_id) AS account_count
    FROM user_profile p
"""


@dataclass
class UserProfile:
    profileId: int
    profileName: str
    description: str
    role: str
    status: str
    createdAt: str
    accountCount: int = 0

    @classmethod
    def _fromRow(cls, row) -> "UserProfile":
        return cls(row["profile_id"], row["profile_name"], row["description"], row["role"],
                   row["status"], row["created_at"], row["account_count"])

    @property
    def roleLabel(self) -> str:
        return ROLES.get(self.role, self.role)

    def isActive(self) -> bool:
        return self.status == "ACTIVE"

    def isCore(self) -> bool:
        return self.profileId in CORE_PROFILE_IDS

    # ---- read ---------------------------------------------------------------
    @classmethod
    def getAllProfiles(cls) -> list["UserProfile"]:
        return [cls._fromRow(r) for r in get_connection().execute(_SELECT + " ORDER BY p.profile_id")]

    @classmethod
    def getActiveProfiles(cls) -> list["UserProfile"]:
        return [p for p in cls.getAllProfiles() if p.isActive()]

    @classmethod
    def findById(cls, profileId: int) -> "UserProfile | None":
        row = get_connection().execute(_SELECT + " WHERE p.profile_id = ?", (profileId,)).fetchone()
        return cls._fromRow(row) if row else None

    @classmethod
    def nameExists(cls, profileName: str, excludeProfileId: int | None = None) -> bool:
        row = get_connection().execute(
            "SELECT 1 FROM user_profile WHERE profile_name = ? COLLATE NOCASE AND profile_id IS NOT ?",
            (profileName.strip(), excludeProfileId),
        ).fetchone()
        return row is not None

    @classmethod
    def searchProfiles(cls, keyword: str) -> list["UserProfile"]:
        like = f"%{keyword.strip()}%"
        rows = get_connection().execute(
            _SELECT + """ WHERE p.profile_name LIKE ? OR p.description LIKE ? OR p.role LIKE ?
                          ORDER BY p.profile_id""",
            (like, like, like.replace(" ", "_")),
        ).fetchall()
        return [cls._fromRow(r) for r in rows]

    # ---- create / update ----------------------------------------------------
    @classmethod
    def save(cls, profileName: str, description: str, role: str) -> int:
        connection = get_connection()
        cursor = connection.execute(
            "INSERT INTO user_profile (profile_name, description, role) VALUES (?, ?, ?)",
            (profileName.strip(), description.strip(), role),
        )
        connection.commit()
        return cursor.lastrowid

    def updateProfile(self, profileName: str, description: str, role: str) -> bool:
        connection = get_connection()
        connection.execute(
            "UPDATE user_profile SET profile_name = ?, description = ?, role = ? WHERE profile_id = ?",
            (profileName.strip(), description.strip(), role, self.profileId),
        )
        connection.commit()
        return True

    def setStatus(self, status: str) -> bool:
        if status not in ("ACTIVE", "SUSPENDED"):
            raise ValueError("Invalid profile status.")
        connection = get_connection()
        connection.execute("UPDATE user_profile SET status = ? WHERE profile_id = ?", (status, self.profileId))
        connection.commit()
        self.status = status
        return True
