"""Boundary: User Admin profile pages.

CreateProfileForm (#9), ViewProfileForm (#10), UpdateProfileForm (#11),
suspend action (#12) and SearchProfilePage (#13).
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from boundary.access_control import roles_required
from control.create_profile_controller import CreateProfileController
from control.search_profile_controller import SearchProfileController
from control.suspend_profile_controller import SuspendProfileController
from control.update_profile_controller import UpdateProfileController
from control.view_profile_controller import ViewProfileController
from entity.user_profile import ROLES, USER_ADMIN

user_profile_bp = Blueprint("user_profile", __name__, url_prefix="/admin/profiles")


@user_profile_bp.route("/")
@roles_required(USER_ADMIN)
def displayProfileList():
    keyword = request.args.get("q", "").strip()
    if "q" in request.args and not keyword:
        flash("Please enter a search keyword.", "error")  # empty search box submitted
    profiles = SearchProfileController().handleSearchProfile(keyword)
    return render_template("user_admin/profile_list_page.html", profiles=profiles, keyword=keyword)


@user_profile_bp.route("/<int:profileId>")
@roles_required(USER_ADMIN)
def displayProfileDetail(profileId):
    profile = ViewProfileController().viewProfile(profileId)
    if profile is None:
        abort(404)
    return render_template("user_admin/profile_detail_page.html", profile=profile)


@user_profile_bp.route("/create", methods=["GET", "POST"])
@roles_required(USER_ADMIN)
def displayCreateForm():
    form = request.form if request.method == "POST" else {}
    if request.method == "POST":
        success, message = CreateProfileController().createProfile(
            form.get("profileName", ""), form.get("description", ""), form.get("role", ""))
        if success:
            flash(message, "success")
            return redirect(url_for("user_profile.displayProfileList"))
        flash(message, "error")
        return render_template("user_admin/profile_form_page.html", form=form, roles=ROLES,
                               profile=None), 400
    return render_template("user_admin/profile_form_page.html", form=form, roles=ROLES, profile=None)


@user_profile_bp.route("/<int:profileId>/update", methods=["GET", "POST"])
@roles_required(USER_ADMIN)
def displayUpdateForm(profileId):
    profile = ViewProfileController().viewProfile(profileId)
    if profile is None:
        abort(404)
    if request.method == "POST":
        form = request.form
        success, message = UpdateProfileController().handleUpdateProfile(
            profileId, form.get("profileName", ""), form.get("description", ""),
            form.get("role", profile.role))
        if success:
            flash(message, "success")
            return redirect(url_for("user_profile.displayProfileDetail", profileId=profileId))
        flash(message, "error")
        return render_template("user_admin/profile_form_page.html", form=form, roles=ROLES,
                               profile=profile), 400
    form = {"profileName": profile.profileName, "description": profile.description, "role": profile.role}
    return render_template("user_admin/profile_form_page.html", form=form, roles=ROLES, profile=profile)


@user_profile_bp.route("/<int:profileId>/suspend", methods=["POST"])
@roles_required(USER_ADMIN)
def suspendProfile(profileId):
    success, message = SuspendProfileController().suspendProfile(profileId, session.get("profile_id"))
    flash(message, "success" if success else "error")
    return redirect(url_for("user_profile.displayProfileDetail", profileId=profileId))


@user_profile_bp.route("/<int:profileId>/reactivate", methods=["POST"])
@roles_required(USER_ADMIN)
def reactivateProfile(profileId):
    success, message = SuspendProfileController().reactivateProfile(profileId)
    flash(message, "success" if success else "error")
    return redirect(url_for("user_profile.displayProfileDetail", profileId=profileId))
