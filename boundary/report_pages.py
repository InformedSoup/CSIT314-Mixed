"""Boundary: Platform Management report pages - DailyReportPage (#47), WeeklyReportPage (#48), MonthlyReportPage (#49)."""
from datetime import date

from flask import Blueprint, flash, render_template, request

from boundary.access_control import roles_required
from control.daily_report_controller import DailyReportController
from control.monthly_report_controller import MonthlyReportController
from control.weekly_report_controller import WeeklyReportController
from entity.user_profile import PLATFORM_MANAGEMENT

report_bp = Blueprint("report", __name__, url_prefix="/platform/reports")


@report_bp.route("/")
@roles_required(PLATFORM_MANAGEMENT)
def displayReportForm():
    kind = request.args.get("type", "daily")
    today = date.today()
    value = request.args.get("value", "")
    if kind == "weekly":
        ok, message, report = WeeklyReportController().generateWeeklyReport(value or today.isoformat())
    elif kind == "monthly":
        ok, message, report = MonthlyReportController().generateMonthlyReport(value or today.strftime("%Y-%m"))
    else:
        kind = "daily"
        ok, message, report = DailyReportController().generateDailyReport(value or today.isoformat())
    if not ok:
        flash(message, "error")  # showError()
    return render_template("platform/report_page.html", kind=kind, report=report, value=value,
                           today=today.isoformat(), thisMonth=today.strftime("%Y-%m")), (200 if ok else 400)
