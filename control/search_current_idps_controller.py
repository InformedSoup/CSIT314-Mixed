"""Control: SearchCurrentIDPsController - user story #23 (search current IDPs by title or client name)."""
from entity.idp import CurrentIDP


class SearchCurrentIDPsController:
    def searchCurrentIDPs(self, designerId: int, keyword: str) -> list[CurrentIDP]:
        """One keyword is matched against both the title and the client name."""
        if not (keyword or "").strip():
            return CurrentIDP.findForDesigner(designerId)
        return CurrentIDP.searchByTitleOrClient(designerId, keyword)
