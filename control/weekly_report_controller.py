"""Control: WeeklyReportController - user story #48 (Platform Management generates a weekly report).

Weeks run Monday to Sunday; any date picked is moved to the Monday of its week.
"""
from datetime import date, timedelta

from control.report_controller import ReportController


class WeeklyReportController(ReportController):
    def validateWeekStartDate(self, weekStartDate: str) -> tuple[list[str], date | None]:
        try:
            day = date.fromisoformat((weekStartDate or "").strip())
        except ValueError:
            return ["Please choose a valid date."], None
        monday = day - timedelta(days=day.weekday())
        return self._notInFuture(monday), monday

    def generateWeeklyReport(self, weekStartDate: str):
        errors, monday = self.validateWeekStartDate(weekStartDate)
        if errors:
            return False, " ".join(errors), None
        sunday = monday + timedelta(days=6)
        return True, "", self._generate("weekly", f"Weekly report · {monday:%d %b} – {sunday:%d %b %Y}",
                                        monday, sunday)
