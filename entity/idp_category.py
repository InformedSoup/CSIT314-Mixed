"""Entity: IDPCategory - a grouping for interior design projects (e.g. Scandinavian, Kitchen)."""
from __future__ import annotations

from dataclasses import dataclass

from db import get_connection

_SELECT = """
    SELECT c.*, (SELECT COUNT(*) FROM idp i WHERE i.category_id = c.category_id) AS idp_count
    FROM idp_category c
"""


@dataclass
class IDPCategory:
    categoryId: int
    name: str
    description: str
    createdAt: str
    idpCount: int = 0

    @classmethod
    def _fromRow(cls, row) -> "IDPCategory":
        return cls(row["category_id"], row["name"], row["description"], row["created_at"], row["idp_count"])

    @classmethod
    def findByName(cls, name: str) -> "IDPCategory | None":
        row = get_connection().execute(_SELECT + " WHERE c.name = ? COLLATE NOCASE", (name.strip(),)).fetchone()
        return cls._fromRow(row) if row else None

    @classmethod
    def findById(cls, categoryId: int) -> "IDPCategory | None":
        row = get_connection().execute(_SELECT + " WHERE c.category_id = ?", (categoryId,)).fetchone()
        return cls._fromRow(row) if row else None

    @classmethod
    def getAllCategories(cls) -> list["IDPCategory"]:
        return [cls._fromRow(r) for r in get_connection().execute(_SELECT + " ORDER BY c.name")]

    @classmethod
    def create(cls, name: str, description: str) -> int:
        connection = get_connection()
        cursor = connection.execute(
            "INSERT INTO idp_category (name, description) VALUES (?, ?)", (name.strip(), description.strip())
        )
        connection.commit()
        return cursor.lastrowid

    @classmethod
    def searchCategories(cls, keyword: str) -> list["IDPCategory"]:
        like = f"%{keyword.strip()}%"
        rows = get_connection().execute(
            _SELECT + " WHERE c.name LIKE ? OR c.description LIKE ? ORDER BY c.name", (like, like)
        ).fetchall()
        return [cls._fromRow(r) for r in rows]

    def isInUse(self) -> bool:
        return self.idpCount > 0

    def updateDetails(self, name: str, description: str) -> bool:
        connection = get_connection()
        connection.execute("UPDATE idp_category SET name = ?, description = ? WHERE category_id = ?",
                           (name.strip(), description.strip(), self.categoryId))
        connection.commit()
        return True

    def delete(self) -> bool:
        connection = get_connection()
        connection.execute("DELETE FROM idp_category WHERE category_id = ?", (self.categoryId,))
        connection.commit()
        return True
