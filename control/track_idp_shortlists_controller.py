"""Control: TrackIDPShortlistsController - user story #39 (Interior Designer tracks how often IDPs are shortlisted)."""
from entity.idp import InteriorDesignProject


class TrackIDPShortlistsController:
    def getShortlistCounts(self, designerId: int) -> list:
        """All of the designer's IDPs, most shortlisted first."""
        return InteriorDesignProject.getAllForDesigner(designerId, "shortlist_count DESC, i.title")

    def getTotalShortlists(self, designerId: int) -> int:
        return sum(i.shortlistCount for i in InteriorDesignProject.getAllForDesigner(designerId))
