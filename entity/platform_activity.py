"""Entity: PlatformActivity - one day of platform activity, used for the reports (#47-#49)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from db import get_connection

# Each metric: (table, timestamp column, extra condition)
_METRICS = {
    "logins": ("user_session", "login_at", ""),
    "newAccounts": ("user_account", "created_at", ""),
    "newIDPs": ("idp", "created_at", ""),
    "views": ("idp_view", "viewed_at", ""),
    "shortlists": ("favourite", "saved_at", ""),
}


@dataclass
class PlatformActivity:
    day: date
    logins: int = 0
    newAccounts: int = 0
    newIDPs: int = 0
    views: int = 0
    shortlists: int = 0

    @classmethod
    def getActivityBetween(cls, start: date, end: date) -> list["PlatformActivity"]:
        """One PlatformActivity per day from start to end (inclusive), zero-filled."""
        days = {start + timedelta(n): cls(start + timedelta(n)) for n in range((end - start).days + 1)}
        connection = get_connection()
        for metric, (table, column, _) in _METRICS.items():
            rows = connection.execute(
                f"""SELECT date({column}) AS d, COUNT(*) AS n FROM {table}
                    WHERE date({column}) BETWEEN ? AND ? GROUP BY d""",
                (start.isoformat(), end.isoformat()),
            ).fetchall()
            for row in rows:
                setattr(days[date.fromisoformat(row["d"])], metric, row["n"])
        return list(days.values())

    @classmethod
    def getActivityByDate(cls, reportDate: date) -> list["PlatformActivity"]:
        return cls.getActivityBetween(reportDate, reportDate)

    @classmethod
    def getActiveUsers(cls, start: date, end: date) -> int:
        row = get_connection().execute(
            "SELECT COUNT(DISTINCT account_id) FROM user_session WHERE date(login_at) BETWEEN ? AND ?",
            (start.isoformat(), end.isoformat()),
        ).fetchone()
        return row[0]

    @classmethod
    def getTopIDPs(cls, start: date, end: date, limit: int = 5) -> list[dict]:
        rows = get_connection().execute(
            """SELECT i.idp_id, i.title, a.full_name AS designer, COUNT(*) AS views
               FROM idp_view v JOIN idp i ON i.idp_id = v.idp_id JOIN user_account a ON a.account_id = i.designer_id
               WHERE date(v.viewed_at) BETWEEN ? AND ?
               GROUP BY i.idp_id ORDER BY views DESC, i.title LIMIT ?""",
            (start.isoformat(), end.isoformat(), limit),
        ).fetchall()
        return [dict(r) for r in rows]

    @classmethod
    def getTopCategories(cls, start: date, end: date, limit: int = 5) -> list[dict]:
        rows = get_connection().execute(
            """SELECT c.name, COUNT(*) AS views
               FROM idp_view v JOIN idp i ON i.idp_id = v.idp_id JOIN idp_category c ON c.category_id = i.category_id
               WHERE date(v.viewed_at) BETWEEN ? AND ?
               GROUP BY c.category_id ORDER BY views DESC, c.name LIMIT ?""",
            (start.isoformat(), end.isoformat(), limit),
        ).fetchall()
        return [dict(r) for r in rows]
