"""Boundary: Platform Management IDP category pages.

CreateCategoryPage (#42), ViewCategoryPage (#43), UpdateCategoryPage (#44),
DeleteCategoryPage (#45) and SearchCategoryPage (#46).
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from boundary.access_control import roles_required
from control.create_category_controller import CreateCategoryController
from control.delete_category_controller import DeleteCategoryController
from control.search_category_controller import SearchCategoryController
from control.update_category_controller import UpdateCategoryController
from control.view_category_controller import ViewCategoryController
from entity.user_profile import PLATFORM_MANAGEMENT

category_bp = Blueprint("category", __name__, url_prefix="/platform/categories")


def _category_or_404(categoryId):
    return ViewCategoryController().getCategoryDetails(categoryId) or abort(404)


@category_bp.route("/")
@roles_required(PLATFORM_MANAGEMENT)
def displayCategoryList():
    keyword = request.args.get("q", "").strip()
    if "q" in request.args and not keyword:
        flash("Please enter a search keyword.", "error")  # empty search box submitted
    categories = SearchCategoryController().searchCategories(keyword)
    return render_template("platform/category_list_page.html", categories=categories, keyword=keyword)


@category_bp.route("/<int:categoryId>")
@roles_required(PLATFORM_MANAGEMENT)
def displayCategoryDetails(categoryId):
    category = _category_or_404(categoryId)
    canDelete, reason = DeleteCategoryController().canDelete(categoryId)
    return render_template("platform/category_detail_page.html", category=category,
                           canDelete=canDelete, reason=reason)


@category_bp.route("/create", methods=["GET", "POST"])
@roles_required(PLATFORM_MANAGEMENT)
def displayCreateForm():
    if request.method == "POST":
        form = request.form
        success, message = CreateCategoryController().createCategory(
            form.get("name", ""), form.get("description", ""))
        flash(message, "success" if success else "error")  # displayMessage()
        if success:
            return redirect(url_for("category.displayCategoryList"))
        return render_template("platform/category_form_page.html", form=form, category=None), 400
    return render_template("platform/category_form_page.html", form={}, category=None)


@category_bp.route("/<int:categoryId>/update", methods=["GET", "POST"])
@roles_required(PLATFORM_MANAGEMENT)
def displayUpdateForm(categoryId):
    category = _category_or_404(categoryId)
    if request.method == "POST":
        form = request.form
        success, message = UpdateCategoryController().updateCategory(
            categoryId, form.get("name", ""), form.get("description", ""))
        flash(message, "success" if success else "error")
        if success:
            return redirect(url_for("category.displayCategoryDetails", categoryId=categoryId))
        return render_template("platform/category_form_page.html", form=form, category=category), 400
    form = {"name": category.name, "description": category.description}
    return render_template("platform/category_form_page.html", form=form, category=category)


@category_bp.route("/<int:categoryId>/delete", methods=["POST"])
@roles_required(PLATFORM_MANAGEMENT)
def deleteCategory(categoryId):
    success, message = DeleteCategoryController().deleteCategory(categoryId)
    flash(message, "success" if success else "error")
    if success:
        return redirect(url_for("category.displayCategoryList"))
    return redirect(url_for("category.displayCategoryDetails", categoryId=categoryId))
