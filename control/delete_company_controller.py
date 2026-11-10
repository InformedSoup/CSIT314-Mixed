"""Control: DeleteCompanyController - user story #19 (Interior Designer deletes company information)."""
from entity.company import Company


class DeleteCompanyController:
    def canDelete(self, companyId: int, designerId: int) -> bool:
        company = Company.findById(companyId)
        return company is not None and company.isOwnedBy(designerId)

    def deleteCompany(self, companyId: int, designerId: int) -> tuple[bool, str]:
        if not self.canDelete(companyId, designerId):
            return False, "Company not found."
        company = Company.findById(companyId)
        company.delete()
        return True, f"'{company.companyName}' has been deleted."
