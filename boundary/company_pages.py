"""Boundary: Interior Designer company pages.

CreateCompanyPage (#16), CompanyInfoPg (#17), UpdateCompanyPg (#18),
DeleteCompanyPage (#19) and SearchCompanyPg (#20).
A designer only ever sees and changes their own company records.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from boundary.access_control import roles_required
from control.company_info_controller import CompanyInfoController
from control.create_company_controller import CreateCompanyController
from control.delete_company_controller import DeleteCompanyController
from control.search_company_controller import SearchCompanyController
from control.update_company_controller import UpdateCompanyController
from entity.user_profile import INTERIOR_DESIGNER

company_bp = Blueprint("company", __name__, url_prefix="/designer/companies")
FIELDS = ("companyName", "regNumber", "description", "address", "contactNumber")


def _own_company_or_404(companyId):
    company = CompanyInfoController().getCompanyInfo(companyId, session["account_id"])
    if company is None:
        abort(404)
    return company


@company_bp.route("/")
@roles_required(INTERIOR_DESIGNER)
def displayMyCompanies():
    keyword = request.args.get("q", "").strip()
    if "q" in request.args and not keyword:
        flash("Please enter a search keyword.", "error")  # empty search box submitted
    companies = SearchCompanyController().handleSearchCompany(session["account_id"], keyword)
    return render_template("designer/company_list_page.html", companies=companies, keyword=keyword)


@company_bp.route("/<int:companyId>")
@roles_required(INTERIOR_DESIGNER)
def displayCompanyInfo(companyId):
    return render_template("designer/company_info_page.html", company=_own_company_or_404(companyId))


@company_bp.route("/create", methods=["GET", "POST"])
@roles_required(INTERIOR_DESIGNER)
def displayCreateForm():
    if request.method == "POST":
        form = request.form
        success, message, companyId = CreateCompanyController().createCompany(
            session["account_id"], *(form.get(f, "") for f in FIELDS))
        if success:
            flash(message, "success")  # showSuccess()
            return redirect(url_for("company.displayCompanyInfo", companyId=companyId))
        flash(message, "error")  # showError()
        return render_template("designer/company_form_page.html", form=form, company=None), 400
    return render_template("designer/company_form_page.html", form={}, company=None)


@company_bp.route("/<int:companyId>/update", methods=["GET", "POST"])
@roles_required(INTERIOR_DESIGNER)
def displayUpdateForm(companyId):
    company = _own_company_or_404(companyId)
    if request.method == "POST":
        details = {f: request.form.get(f, "") for f in FIELDS}
        success, message = UpdateCompanyController().handleUpdate(companyId, session["account_id"], details)
        if success:
            flash(message, "success")
            return redirect(url_for("company.displayCompanyInfo", companyId=companyId))
        flash(message, "error")
        return render_template("designer/company_form_page.html", form=details, company=company), 400
    form = {"companyName": company.companyName, "regNumber": company.regNumber,
            "description": company.description, "address": company.address,
            "contactNumber": company.contactNumber}
    return render_template("designer/company_form_page.html", form=form, company=company)


@company_bp.route("/<int:companyId>/delete", methods=["GET", "POST"])
@roles_required(INTERIOR_DESIGNER)
def displayDeleteConfirmation(companyId):
    company = _own_company_or_404(companyId)
    if request.method == "POST":  # confirmDelete()
        success, message = DeleteCompanyController().deleteCompany(companyId, session["account_id"])
        flash(message, "success" if success else "error")
        return redirect(url_for("company.displayMyCompanies"))
    return render_template("designer/company_delete_page.html", company=company)  # showConfirmation()
