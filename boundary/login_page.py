"""Boundary: LoginPage / LogoutPage - one login page for all four roles.

After login the user is sent to the dashboard for their profile.
"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from boundary.access_control import dashboard_for
from control.login_controller import LoginController
from control.logout_controller import LogoutController

login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["GET"])
def displayLoginPage():
    if session.get("account_id"):
        return redirect(url_for(dashboard_for(session.get("role"))))
    return render_template("login_page.html")


@login_bp.route("/login", methods=["POST"])
def submitLogin():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    success, message, account, user_session = LoginController().authenticate(username, password)
    if not success:
        flash(message, "error")  # displayError()
        return render_template("login_page.html", username=username), 401

    session.clear()
    session["account_id"] = account.userId
    session["profile_id"] = account.profileId
    session["profile_name"] = account.profileName
    session["role"] = account.role
    session["full_name"] = account.fullName
    session["session_id"] = user_session.sessionId
    flash(message, "success")
    return redirect(url_for(dashboard_for(account.role)))


@login_bp.route("/logout", methods=["POST"])
def submitLogout():
    success, message = LogoutController().logout(session.get("session_id"))
    session.clear()
    flash(message, "success" if success else "error")
    return redirect(url_for("login.displayLoginPage"))
