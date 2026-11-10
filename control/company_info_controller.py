"""Control: CompanyInfoController - user story #17 (Interior Designer views company information)."""
from entity.company import Company


class CompanyInfoController:
    def getCompanyInfo(self, companyId: int, designerId: int) -> Company | None:
        """Return the company only if it belongs to this designer."""
        company = Company.findById(companyId)
        if company is None or not company.isOwnedBy(designerId):
            return None
        return company

    def getMyCompanies(self, designerId: int) -> list[Company]:
        return Company.findByDesigner(designerId)
