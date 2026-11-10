"""Control: DailyReportController - user story #47 (Platform Management generates a daily report)."""
from datetime import date

from control.report_controller import ReportController


class DailyReportController(ReportController):
    def validateReportDate(self, reportDate: str) -> tuple[list[str], date | None]:
        try:
            day = date.fromisoformat((reportDate or "").strip())
        except ValueError:
            return ["Please choose a valid date."], None
        return self._notInFuture(day), day

    def generateDailyReport(self, reportDate: str):
        """Returns (success, message, report)."""
        errors, day = self.validateReportDate(reportDate)
        if errors:
            return False, " ".join(errors), None
        return True, "", self._generate("daily", f"Daily report · {day:%A %d %B %Y}", day, day)
