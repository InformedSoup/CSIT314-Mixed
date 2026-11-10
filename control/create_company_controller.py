"""Control: CreateCompanyController - user story #16 (Interior Designer creates company information)."""
import re

from entity.company import Company

# Singapore UEN formats: 8-9 digits + letter (businesses/local companies) or T/S/R + 2 digits + 2 letters + 4 digits + letter.
UEN_PATTERN = re.compile(r"^(\d{8,9}[A-Z]|[TSR]\d{2}[A-Z]{2}\d{4}[A-Z])$")
PHONE_PATTERN = re.compile(r"^(\+65\s?)?[689]\d{3}\s?\d{4}$")


def validate_company_fields(companyName, regNumber, description, address, contactNumber,
                            excludeCompanyId=None) -> list[str]:
    """Shared by create and update so both apply exactly the same rules."""
    errors = []
    if not (companyName or "").strip():
        errors.append("Company name is required.")
    reg = (regNumber or "").strip().upper()
    if not UEN_PATTERN.match(reg):
        errors.append("Registration number must be a valid UEN (e.g. 201912345K).")
    elif Company.regNumberExists(reg, excludeCompanyId):
        errors.append(f"Registration number {reg} is already registered.")
    if not (description or "").strip():
        errors.append("Description is required.")
    if not (address or "").strip():
        errors.append("Address is required.")
    if not PHONE_PATTERN.match((contactNumber or "").strip()):
        errors.append("Contact number must be a Singapore number (e.g. 6123 4567 or +65 9123 4567).")
    return errors


class CreateCompanyController:
    def validateCompanyDetails(self, companyName, regNumber, description, address, contactNumber) -> list[str]:
        return validate_company_fields(companyName, regNumber, description, address, contactNumber)

    def createCompany(self, designerId: int, companyName: str, regNumber: str, description: str,
                      address: str, contactNumber: str) -> tuple[bool, str, int | None]:
        errors = self.validateCompanyDetails(companyName, regNumber, description, address, contactNumber)
        if errors:
            return False, " ".join(errors), None
        companyId = Company.save(designerId, companyName, regNumber, description, address, contactNumber)
        return True, "Company information created.", companyId
