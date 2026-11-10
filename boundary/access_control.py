"""Role-based access checks shared by all boundary pages."""
from functools import wraps

from flask import flash, redirect, session, url_for

from entity.user_profile import (CUSTOMER, INTERIOR_DESIGNER, PLATFORM_MANAGEMENT,
                                 USER_ADMIN)

DASHBOARDS = {
    USER_ADMIN: "user_account.displayUserList",
    INTERIOR_DESIGNER: "idp.displayCurrentIDPs",
    CUSTOMER: "customer.displaySearchPage",
    PLATFORM_MANAGEMENT: "category.displayCategoryList",
}


def dashboard_for(role) -> str:
    return DASHBOARDS.get(role, "login.displayLoginPage")


def roles_required(*allowed_roles):
    """Only let logged-in users whose profile grants one of the given roles reach the page."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("account_id"):
                flash("Please log in to continue.", "error")
                return redirect(url_for("login.displayLoginPage"))
            if session.get("role") not in allowed_roles:
                flash("You do not have permission to access that page.", "error")
                return redirect(url_for("home"))
            return view(*args, **kwargs)
        return wrapped
    return decorator
