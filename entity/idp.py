"""Entities: InteriorDesignProject and its two kinds, CurrentIDP and PastIDP.

Both kinds live in the `idp` table and are told apart by `status`.
The base class holds everything they share; each subclass adds the queries
its own user stories need (search current by title/client, past by category/year).
"""
from __future__ import annotations

from dataclasses import dataclass

from db import get_connection

_SELECT = """
    SELECT i.*, c.name AS category_name, a.full_name AS designer_name,
           (SELECT COUNT(*) FROM idp_view v WHERE v.idp_id = i.idp_id) AS view_count,
           (SELECT COUNT(*) FROM favourite f WHERE f.idp_id = i.idp_id) AS shortlist_count
    FROM idp i
    JOIN user_account a ON a.account_id = i.designer_id
    LEFT JOIN idp_category c ON c.category_id = i.category_id
"""


@dataclass
class InteriorDesignProject:
    idpId: int
    designerId: int
    designerName: str
    categoryId: int | None
    categoryName: str | None
    title: str
    clientName: str
    description: str
    designStyle: str
    imageUrl: str
    progress: int
    completionDate: str | None
    status: str
    createdAt: str
    viewCount: int = 0
    shortlistCount: int = 0

    STATUS = None  # set by subclasses

    @staticmethod
    def _fromRow(row) -> "InteriorDesignProject":
        kind = CurrentIDP if row["status"] == "CURRENT" else PastIDP
        return kind(
            idpId=row["idp_id"], designerId=row["designer_id"], designerName=row["designer_name"],
            categoryId=row["category_id"], categoryName=row["category_name"], title=row["title"],
            clientName=row["client_name"], description=row["description"],
            designStyle=row["design_style"], imageUrl=row["image_url"], progress=row["progress"],
            completionDate=row["completion_date"], status=row["status"], createdAt=row["created_at"],
            viewCount=row["view_count"], shortlistCount=row["shortlist_count"],
        )

    @classmethod
    def _query(cls, where: str = "", params: tuple = (), order: str = "i.created_at DESC") -> list:
        rows = get_connection().execute(f"{_SELECT} {where} ORDER BY {order}", params).fetchall()
        return [InteriorDesignProject._fromRow(r) for r in rows]

    # ---- shared reads -------------------------------------------------------
    @classmethod
    def findById(cls, idpId: int):
        """Find an IDP; on a subclass, only return it if it is that kind."""
        where, params = "WHERE i.idp_id = ?", (idpId,)
        if cls.STATUS:
            where, params = where + " AND i.status = ?", (idpId, cls.STATUS)
        result = cls._query(where, params)
        return result[0] if result else None

    @classmethod
    def findForDesigner(cls, designerId: int) -> list:
        return cls._query("WHERE i.designer_id = ? AND i.status = ?", (designerId, cls.STATUS))

    @classmethod
    def getAllForDesigner(cls, designerId: int, order: str = "i.created_at DESC") -> list:
        """Every IDP (current and past) of a designer - used for view/shortlist tracking."""
        return cls._query("WHERE i.designer_id = ?", (designerId,), order)

    @classmethod
    def searchIDPs(cls, keyword: str = "", categoryId: int | None = None, status: str | None = None) -> list:
        """Customer search across all IDPs of active designers."""
        clauses, params = ["a.status = 'ACTIVE'"], []
        if keyword.strip():
            like = f"%{keyword.strip()}%"
            clauses.append("(i.title LIKE ? OR i.description LIKE ? OR i.design_style LIKE ? "
                           "OR c.name LIKE ? OR a.full_name LIKE ?)")
            params += [like] * 5
        if categoryId:
            clauses.append("i.category_id = ?")
            params.append(categoryId)
        if status in ("CURRENT", "PAST"):
            clauses.append("i.status = ?")
            params.append(status)
        return cls._query("WHERE " + " AND ".join(clauses), tuple(params))

    def isOwnedBy(self, designerId: int) -> bool:
        return self.designerId == designerId

    def getDetails(self) -> dict:
        return {"title": self.title, "clientName": self.clientName, "description": self.description,
                "designStyle": self.designStyle, "categoryId": self.categoryId,
                "imageUrl": self.imageUrl, "progress": self.progress,
                "completionDate": self.completionDate}

    # ---- shared writes ------------------------------------------------------
    @classmethod
    def createIDP(cls, designerId: int, details: dict) -> int:
        connection = get_connection()
        cursor = connection.execute(
            """INSERT INTO idp (designer_id, category_id, title, client_name, description, design_style,
                                image_url, progress, completion_date, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (designerId, details.get("categoryId") or None, details["title"].strip(),
             details.get("clientName", "").strip(), details.get("description", "").strip(),
             details.get("designStyle", "").strip(), details.get("imageUrl", "").strip(),
             cls._progressFor(details), cls._completionFor(details), cls.STATUS),
        )
        connection.commit()
        return cursor.lastrowid

    def updateDetails(self, details: dict) -> bool:
        connection = get_connection()
        connection.execute(
            """UPDATE idp SET category_id = ?, title = ?, client_name = ?, description = ?, design_style = ?,
                              image_url = ?, progress = ?, completion_date = ? WHERE idp_id = ?""",
            (details.get("categoryId") or None, details["title"].strip(), details.get("clientName", "").strip(),
             details.get("description", "").strip(), details.get("designStyle", "").strip(),
             details.get("imageUrl", "").strip(), self._progressFor(details),
             self._completionFor(details), self.idpId),
        )
        connection.commit()
        return True

    def delete(self) -> bool:
        connection = get_connection()
        connection.execute("DELETE FROM idp WHERE idp_id = ?", (self.idpId,))
        connection.commit()
        return True

    def hasRecentView(self, customerId: int, minutes: int) -> bool:
        row = get_connection().execute(
            """SELECT 1 FROM idp_view WHERE idp_id = ? AND customer_id = ?
               AND viewed_at >= datetime('now', 'localtime', ?)""",
            (self.idpId, customerId, f"-{int(minutes)} minutes"),
        ).fetchone()
        return row is not None

    def recordView(self, customerId: int | None) -> None:
        connection = get_connection()
        connection.execute("INSERT INTO idp_view (idp_id, customer_id) VALUES (?, ?)", (self.idpId, customerId))
        connection.commit()

    @classmethod
    def _progressFor(cls, details) -> int:
        return int(details.get("progress") or 0)

    @classmethod
    def _completionFor(cls, details):
        return None


class CurrentIDP(InteriorDesignProject):
    """An ongoing project: has progress (0-100%), no completion date."""
    STATUS = "CURRENT"

    @classmethod
    def searchByTitleOrClient(cls, designerId: int, keyword: str) -> list:
        like = f"%{keyword.strip()}%"
        return cls._query("WHERE i.designer_id = ? AND i.status = 'CURRENT' AND (i.title LIKE ? OR i.client_name LIKE ?)",
                          (designerId, like, like))

    def markCompleted(self, completionDate: str) -> bool:
        """Move this project into the past portfolio."""
        connection = get_connection()
        connection.execute(
            "UPDATE idp SET status = 'PAST', progress = 100, completion_date = ? WHERE idp_id = ?",
            (completionDate, self.idpId),
        )
        connection.commit()
        return True


class PastIDP(InteriorDesignProject):
    """A finished project: always 100% with a completion date."""
    STATUS = "PAST"

    @classmethod
    def searchByCategoryOrYear(cls, designerId: int, categoryId: int | None, year: str | None) -> list:
        clauses, params = ["i.designer_id = ?", "i.status = 'PAST'"], [designerId]
        if categoryId:
            clauses.append("i.category_id = ?")
            params.append(categoryId)
        if year:
            clauses.append("substr(i.completion_date, 1, 4) = ?")
            params.append(str(year))
        return cls._query("WHERE " + " AND ".join(clauses), tuple(params), "i.completion_date DESC")

    @classmethod
    def getCompletionYears(cls, designerId: int) -> list[str]:
        rows = get_connection().execute(
            """SELECT DISTINCT substr(completion_date, 1, 4) AS y FROM idp
               WHERE designer_id = ? AND status = 'PAST' AND completion_date IS NOT NULL ORDER BY y DESC""",
            (designerId,)).fetchall()
        return [r["y"] for r in rows]

    @classmethod
    def _progressFor(cls, details) -> int:
        return 100

    @classmethod
    def _completionFor(cls, details):
        return details.get("completionDate") or None
