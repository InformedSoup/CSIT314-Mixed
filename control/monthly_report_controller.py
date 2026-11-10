"""Control: MonthlyReportController - user story #49 (Platform Management generates a monthly report)."""
import calendar
from datetime import date

from control.report_controller import ReportController


class MonthlyReportController(ReportController):
    def validateMonth(self, month: str) -> tuple[list[str], date | None]:
        """month is 'YYYY-MM'."""
        try:
            first = date.fromisoformat(f"{(month or '').strip()}-01")
        except ValueError:
            return ["Please choose a valid month."], None
        return self._notInFuture(first), first

    def generateMonthlyReport(self, month: str):
        errors, first = self.validateMonth(month)
        if errors:
            return False, " ".join(errors), None
        last = first.replace(day=calendar.monthrange(first.year, first.month)[1])
        return True, "", self._generate("monthly", f"Monthly report · {first:%B %Y}", first, last)
