"""Control: UpdateCompanyController - user story #18 (Interior Designer updates company information)."""
from control.create_company_controller import validate_company_fields
from entity.company import Company


class UpdateCompanyController:
    def validateInput(self, companyId: int, details: dict) -> list[str]:
        return validate_company_fields(details.get("companyName"), details.get("regNumber"),
                                       details.get("description"), details.get("address"),
                                       details.get("contactNumber"), excludeCompanyId=companyId)

    def handleUpdate(self, companyId: int, designerId: int, details: dict) -> tuple[bool, str]:
        company = Company.findById(companyId)
        if company is None or not company.isOwnedBy(designerId):
            return False, "Company not found."
        errors = self.validateInput(companyId, details)
        if errors:
            return False, " ".join(errors)
        company.updateCompanyDetails(details["companyName"], details["regNumber"],
                                     details["description"], details["address"],
                                     details["contactNumber"])
        return True, "Company information updated."
