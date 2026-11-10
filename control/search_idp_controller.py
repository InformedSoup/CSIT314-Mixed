"""Control: SearchIDPController - user story #33 (Customer searches for IDPs)."""
from entity.idp import InteriorDesignProject

MAX_QUERY_LENGTH = 100


class SearchIDPController:
    def validateQuery(self, query: str) -> bool:
        return len(query or "") <= MAX_QUERY_LENGTH

    def handleSearch(self, query: str = "", categoryId=None, status=None) -> tuple[bool, str, list]:
        """Keyword matches title, description, style, category or designer name.
        Category and current/past status narrow it further. Empty search lists everything."""
        if not self.validateQuery(query):
            return False, f"Search must be {MAX_QUERY_LENGTH} characters or fewer.", []
        try:
            categoryId = int(categoryId) if categoryId else None
        except ValueError:
            categoryId = None
        return True, "", InteriorDesignProject.searchIDPs(query or "", categoryId, status)
