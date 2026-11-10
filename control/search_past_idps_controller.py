"""Control: SearchPastIDPsController - user story #28 (search past IDPs by style category or completion year)."""
from entity.idp import PastIDP


class SearchPastIDPsController:
    def searchPastIDPs(self, designerId: int, categoryId=None, year=None) -> list[PastIDP]:
        try:
            categoryId = int(categoryId) if categoryId else None
        except ValueError:
            categoryId = None
        year = year if (year or "").isdigit() and len(year) == 4 else None
        return PastIDP.searchByCategoryOrYear(designerId, categoryId, year)

    def getCompletionYears(self, designerId: int) -> list[str]:
        return PastIDP.getCompletionYears(designerId)
