"""Control: SearchCompanyController - user story #20 (Interior Designer searches company information)."""
from entity.company import Company


class SearchCompanyController:
    def validateSearchInput(self, keyword: str) -> bool:
        return bool((keyword or "").strip())

    def handleSearchCompany(self, designerId: int, keyword: str) -> list[Company]:
        if not self.validateSearchInput(keyword):
            return Company.findByDesigner(designerId)
        return Company.searchCompanies(designerId, keyword)
