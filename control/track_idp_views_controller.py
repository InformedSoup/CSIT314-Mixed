"""Control: TrackIDPViewsController - user story #38 (Interior Designer tracks the number of views of IDPs)."""
from entity.idp import InteriorDesignProject


class TrackIDPViewsController:
    def getViewCounts(self, designerId: int) -> list:
        """All of the designer's IDPs, most viewed first."""
        return InteriorDesignProject.getAllForDesigner(designerId, "view_count DESC, i.title")

    def getTotalViews(self, designerId: int) -> int:
        return sum(i.viewCount for i in InteriorDesignProject.getAllForDesigner(designerId))
