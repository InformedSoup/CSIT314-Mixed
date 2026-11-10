"""Shared report logic used by the daily, weekly and monthly report controllers."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from entity.platform_activity import PlatformActivity

METRICS = ("logins", "newAccounts", "newIDPs", "views", "shortlists")


@dataclass
class Report:
    kind: str
    title: str
    start: date
    end: date
    days: list
    totals: dict
    previousTotals: dict
    activeUsers: int
    topIDPs: list = field(default_factory=list)
    topCategories: list = field(default_factory=list)

    def change(self, metric: str):
        """% change against the previous period, or None if there was nothing before."""
        before = self.previousTotals.get(metric, 0)
        if not before:
            return None
        return round((self.totals[metric] - before) / before * 100)

    @property
    def peakViews(self) -> int:
        return max((d.views for d in self.days), default=0) or 1


class ReportController:
    def buildSummary(self, activities: list) -> dict:
        return {m: sum(getattr(a, m) for a in activities) for m in METRICS}

    def _generate(self, kind: str, title: str, start: date, end: date) -> Report:
        """For a period still in progress (e.g. this week), compare like with like:
        the days so far against the same number of days at the start of the previous period."""
        length = (end - start).days + 1
        prev_start = start - timedelta(days=length) if kind != "monthly" else self._previousMonthStart(start)
        counted_end = min(end, date.today())
        elapsed = (counted_end - start).days
        prev_end = min(prev_start + timedelta(days=elapsed), start - timedelta(days=1))
        if counted_end < end:
            title += " (so far)"
        days = PlatformActivity.getActivityBetween(start, end)
        return Report(
            kind=kind, title=title, start=start, end=end, days=days,
            totals=self.buildSummary(days),
            previousTotals=self.buildSummary(PlatformActivity.getActivityBetween(prev_start, prev_end)),
            activeUsers=PlatformActivity.getActiveUsers(start, end),
            topIDPs=PlatformActivity.getTopIDPs(start, end),
            topCategories=PlatformActivity.getTopCategories(start, end),
        )

    @staticmethod
    def _previousMonthStart(first: date) -> date:
        return (first - timedelta(days=1)).replace(day=1)

    @staticmethod
    def _notInFuture(day: date) -> list[str]:
        return ["Reports cannot be generated for future dates."] if day > date.today() else []
