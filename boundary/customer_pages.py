"""Boundary: Customer pages.

SearchIDPPg (#33), ViewIDPPg (#34), save to favourites (#35),
ViewFavouriteListPg (#36) and viewing an IDP from the favourite list (#37).
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from boundary.access_control import roles_required
from control.favourite_list_controller import FavouriteListController
from control.save_favourite_controller import SaveFavouriteController
from control.search_idp_controller import SearchIDPController
from control.view_favourite_list_controller import ViewFavouriteListController
from control.view_idp_controller import ViewIDPController
from entity.idp_category import IDPCategory
from entity.user_profile import CUSTOMER

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")


def _me():
    return session["account_id"]


@customer_bp.route("/")
@roles_required(CUSTOMER)
def displaySearchPage():
    query = request.args.get("q", "").strip()
    categoryId = request.args.get("category", "")
    status = request.args.get("status", "")
    ok, message, idps = SearchIDPController().handleSearch(query, categoryId, status)
    if not ok:
        flash(message, "error")
    return render_template("customer/search_idp_page.html", idps=idps, query=query,
                           categories=IDPCategory.getAllCategories(),
                           selectedCategory=categoryId, selectedStatus=status)


@customer_bp.route("/idps/<int:idpId>")
@roles_required(CUSTOMER)
def displayIDP(idpId):
    idp, companies = ViewIDPController().getIDPDetails(idpId, _me())
    if idp is None:
        abort(404)
    saved = SaveFavouriteController().isSaved(_me(), idpId)
    return render_template("customer/view_idp_page.html", idp=idp, companies=companies, saved=saved,
                           fromFavourites=False)


@customer_bp.route("/idps/<int:idpId>/save", methods=["POST"])
@roles_required(CUSTOMER)
def saveToFavourites(idpId):
    ok, message = SaveFavouriteController().saveIDP(_me(), idpId)
    flash(message, "success" if ok else "error")
    return redirect(request.form.get("next") or url_for("customer.displayIDP", idpId=idpId))


@customer_bp.route("/idps/<int:idpId>/unsave", methods=["POST"])
@roles_required(CUSTOMER)
def removeFromFavourites(idpId):
    ok, message = SaveFavouriteController().removeIDP(_me(), idpId)
    flash(message, "success" if ok else "error")
    return redirect(request.form.get("next") or url_for("customer.displayFavourites"))


@customer_bp.route("/favourites/")
@roles_required(CUSTOMER)
def displayFavourites():
    favourites = ViewFavouriteListController().getFavouriteList(_me())
    return render_template("customer/favourite_list_page.html", favourites=favourites)


@customer_bp.route("/favourites/<int:idpId>")
@roles_required(CUSTOMER)
def displayFavouriteIDP(idpId):
    idp, companies = FavouriteListController().getIDPDetails(_me(), idpId)
    if idp is None:
        abort(404)
    return render_template("customer/view_idp_page.html", idp=idp, companies=companies, saved=True,
                           fromFavourites=True)
