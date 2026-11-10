"""Boundary: Interior Designer project pages for current IDPs (#21-#25) and past IDPs (#26-#30).

Both kinds share templates; `kind` ('current' or 'past') switches labels and fields.
"""
from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from boundary.access_control import roles_required
from control.create_current_idp_controller import CreateCurrentIDPController
from control.create_past_idp_controller import CreatePastIDPController
from control.delete_current_idp_controller import DeleteCurrentIDPController
from control.delete_past_idp_controller import DeletePastIDPController
from control.search_current_idps_controller import SearchCurrentIDPsController
from control.search_past_idps_controller import SearchPastIDPsController
from control.update_current_idp_controller import UpdateCurrentIDPController
from control.update_past_idp_controller import UpdatePastIDPController
from control.view_current_idp_controller import ViewCurrentIDPController
from control.view_past_idp_controller import ViewPastIDPController
from entity.idp_category import IDPCategory
from entity.user_profile import INTERIOR_DESIGNER

idp_bp = Blueprint("idp", __name__, url_prefix="/designer/projects")
FIELDS = ("title", "clientName", "description", "designStyle", "categoryId", "imageUrl",
          "progress", "completionDate")


def _me():
    return session["account_id"]


def _details():
    return {f: request.form.get(f, "") for f in FIELDS}


def _render_form(kind, form, idp=None, status=200):
    return render_template("designer/idp_form_page.html", kind=kind, form=form, idp=idp,
                           categories=IDPCategory.getAllCategories(), today=date.today().isoformat()), status


# ============================== Current IDPs ===============================
@idp_bp.route("/current/")
@roles_required(INTERIOR_DESIGNER)
def displayCurrentIDPs():
    keyword = request.args.get("q", "").strip()
    idps = SearchCurrentIDPsController().searchCurrentIDPs(_me(), keyword)
    return render_template("designer/idp_list_page.html", kind="current", idps=idps, keyword=keyword)


@idp_bp.route("/current/create", methods=["GET", "POST"])
@roles_required(INTERIOR_DESIGNER)
def displayCreateCurrentForm():
    if request.method == "POST":
        ok, message, idpId = CreateCurrentIDPController().handleCreateIDP(_me(), _details())
        flash(message, "success" if ok else "error")
        if ok:
            return redirect(url_for("idp.displayCurrentIDP", idpId=idpId))
        return _render_form("current", request.form, status=400)
    return _render_form("current", {"progress": 0})


@idp_bp.route("/current/<int:idpId>")
@roles_required(INTERIOR_DESIGNER)
def displayCurrentIDP(idpId):
    idp = ViewCurrentIDPController().getIDPDetails(idpId, _me()) or abort(404)
    return render_template("designer/idp_detail_page.html", kind="current", idp=idp,
                           today=date.today().isoformat())


@idp_bp.route("/current/<int:idpId>/update", methods=["GET", "POST"])
@roles_required(INTERIOR_DESIGNER)
def displayUpdateCurrentForm(idpId):
    idp = ViewCurrentIDPController().getIDPDetails(idpId, _me()) or abort(404)
    if request.method == "POST":
        ok, message = UpdateCurrentIDPController().handleUpdateIDP(idpId, _me(), _details())
        flash(message, "success" if ok else "error")
        if ok:
            return redirect(url_for("idp.displayCurrentIDP", idpId=idpId))
        return _render_form("current", request.form, idp, 400)
    return _render_form("current", idp.getDetails(), idp)


@idp_bp.route("/current/<int:idpId>/complete", methods=["POST"])
@roles_required(INTERIOR_DESIGNER)
def markCurrentCompleted(idpId):
    ok, message = UpdateCurrentIDPController().markCompleted(idpId, _me(), request.form.get("completionDate", ""))
    flash(message, "success" if ok else "error")
    if ok:
        return redirect(url_for("idp.displayPastIDP", idpId=idpId))
    return redirect(url_for("idp.displayCurrentIDP", idpId=idpId))


@idp_bp.route("/current/<int:idpId>/delete", methods=["GET", "POST"])
@roles_required(INTERIOR_DESIGNER)
def displayDeleteCurrent(idpId):
    idp = ViewCurrentIDPController().getIDPDetails(idpId, _me()) or abort(404)
    if request.method == "POST":
        ok, message = DeleteCurrentIDPController().deleteIDP(idpId, _me())
        flash(message, "success" if ok else "error")
        return redirect(url_for("idp.displayCurrentIDPs"))
    return render_template("designer/idp_delete_page.html", kind="current", idp=idp)


# ================================ Past IDPs ================================
@idp_bp.route("/past/")
@roles_required(INTERIOR_DESIGNER)
def displayPastIDPs():
    categoryId = request.args.get("category", "")
    year = request.args.get("year", "")
    controller = SearchPastIDPsController()
    idps = controller.searchPastIDPs(_me(), categoryId, year)
    return render_template("designer/idp_list_page.html", kind="past", idps=idps,
                           categories=IDPCategory.getAllCategories(), years=controller.getCompletionYears(_me()),
                           selectedCategory=categoryId, selectedYear=year)


@idp_bp.route("/past/create", methods=["GET", "POST"])
@roles_required(INTERIOR_DESIGNER)
def displayCreatePastForm():
    if request.method == "POST":
        ok, message, idpId = CreatePastIDPController().createPastIDP(_me(), _details())
        flash(message, "success" if ok else "error")
        if ok:
            return redirect(url_for("idp.displayPastIDP", idpId=idpId))
        return _render_form("past", request.form, status=400)
    return _render_form("past", {})


@idp_bp.route("/past/<int:idpId>")
@roles_required(INTERIOR_DESIGNER)
def displayPastIDP(idpId):
    idp = ViewPastIDPController().getIDPDetails(idpId, _me()) or abort(404)
    return render_template("designer/idp_detail_page.html", kind="past", idp=idp)


@idp_bp.route("/past/<int:idpId>/update", methods=["GET", "POST"])
@roles_required(INTERIOR_DESIGNER)
def displayUpdatePastForm(idpId):
    idp = ViewPastIDPController().getIDPDetails(idpId, _me()) or abort(404)
    if request.method == "POST":
        ok, message = UpdatePastIDPController().handleUpdateIDP(idpId, _me(), _details())
        flash(message, "success" if ok else "error")
        if ok:
            return redirect(url_for("idp.displayPastIDP", idpId=idpId))
        return _render_form("past", request.form, idp, 400)
    return _render_form("past", idp.getDetails(), idp)


@idp_bp.route("/past/<int:idpId>/delete", methods=["GET", "POST"])
@roles_required(INTERIOR_DESIGNER)
def displayDeletePast(idpId):
    idp = ViewPastIDPController().getIDPDetails(idpId, _me()) or abort(404)
    if request.method == "POST":
        ok, message = DeletePastIDPController().deleteIDP(idpId, _me())
        flash(message, "success" if ok else "error")
        return redirect(url_for("idp.displayPastIDPs"))
    return render_template("designer/idp_delete_page.html", kind="past", idp=idp)
