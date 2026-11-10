"""Boundary: User Admin account pages.

CreateUserPage (#4), ViewUserPage (#5), UpdateUserPage (#6),
SuspendUser action (#7) and SearchUserPage (#8).
"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from boundary.access_control import roles_required
from control.create_user_controller import CreateUserController
from control.search_user_controller import SearchUserController
from control.suspend_user_controller import SuspendUserController
from control.update_user_controller import UpdateUserController
from control.view_user_controller import ViewUserController
from entity.user_profile import USER_ADMIN, UserProfile

user_account_bp = Blueprint("user_account", __name__, url_prefix="/admin/accounts")


def _accountNotFound():
    flash("User account not found.", "error")
    return redirect(url_for("user_account.displayUserList"))


# ---- ViewUserPage + SearchUserPage ------------------------------------------
@user_account_bp.route("/")
@roles_required(USER_ADMIN)
def displayUserList():
    keyword = request.args.get("q", "").strip()
    if "q" in request.args and not keyword:
        flash("Please enter a search keyword.", "error")  # empty search box submitted
    accounts = SearchUserController().searchUsers(keyword)
    return render_template("user_admin/view_user_page.html", accounts=accounts, keyword=keyword)


@user_account_bp.route("/<int:userId>")
@roles_required(USER_ADMIN)
def displayUserDetails(userId):
    account = ViewUserController().getUserAccount(userId)
    if account is None:
        return _accountNotFound()
    return render_template("user_admin/view_user_details.html", account=account)


# ---- CreateUserPage ---------------------------------------------------------
@user_account_bp.route("/create", methods=["GET", "POST"])
@roles_required(USER_ADMIN)
def displayCreateForm():
    profiles = UserProfile.getActiveProfiles()
    if request.method == "POST":
        form = request.form
        success, message = CreateUserController().handleCreateUser(
            form.get("fullName", ""), form.get("username", ""), form.get("email", ""),
            form.get("password", ""), form.get("profileId"),
        )
        if success:
            flash(message, "success")  # displaySuccessMessage()
            return redirect(url_for("user_account.displayUserList"))
        flash(message, "error")  # displayErrorMessage()
        return render_template("user_admin/create_user_page.html", profiles=profiles, form=form), 400
    return render_template("user_admin/create_user_page.html", profiles=profiles, form={})


# ---- UpdateUserPage ---------------------------------------------------------
@user_account_bp.route("/<int:userId>/update", methods=["GET", "POST"])
@roles_required(USER_ADMIN)
def displayUpdateForm(userId):
    account = ViewUserController().getUserAccount(userId)
    if account is None:
        return _accountNotFound()
    profiles = UserProfile.getAllProfiles()
    if request.method == "POST":
        form = request.form
        success, message = UpdateUserController().handleUpdateUser(
            userId, form.get("fullName", ""), form.get("email", ""),
            form.get("profileId"), form.get("newPassword", ""),
        )
        if success:
            flash(message, "success")
            return redirect(url_for("user_account.displayUserDetails", userId=userId))
        flash(message, "error")
        return render_template("user_admin/update_user_page.html", account=account,
                               profiles=profiles, form=form), 400
    form = {"fullName": account.fullName, "email": account.email, "profileId": account.profileId}
    return render_template("user_admin/update_user_page.html", account=account,
                           profiles=profiles, form=form)


# ---- Suspend / reactivate ---------------------------------------------------
@user_account_bp.route("/<int:userId>/suspend", methods=["POST"])
@roles_required(USER_ADMIN)
def suspendUser(userId):
    success, message = SuspendUserController().suspendUser(userId, session.get("account_id"))
    flash(message, "success" if success else "error")
    return redirect(url_for("user_account.displayUserDetails", userId=userId))


@user_account_bp.route("/<int:userId>/reactivate", methods=["POST"])
@roles_required(USER_ADMIN)
def reactivateUser(userId):
    success, message = SuspendUserController().reactivateUser(userId)
    flash(message, "success" if success else "error")
    return redirect(url_for("user_account.displayUserDetails", userId=userId))
