"""Control: ViewIDPController - user story #34 (Customer views the details of an IDP).

Every customer view is recorded for the designer's view tracking (#38). Refreshing
the page within REPEAT_WINDOW_MINUTES does not count again, so counts stay honest.
"""
from entity.company import Company
from entity.idp import InteriorDesignProject
from entity.user_account import UserAccount

REPEAT_WINDOW_MINUTES = 30


class ViewIDPController:
    def getIDPDetails(self, idpId: int, customerId: int | None = None):
        """Returns (idp, companies), or (None, []) if the IDP doesn't exist or its designer is suspended."""
        idp = InteriorDesignProject.findById(idpId)
        if idp is None:
            return None, []
        designer = UserAccount.findById(idp.designerId)
        if designer is None or not designer.isActive():
            return None, []
        if customerId is not None and not idp.hasRecentView(customerId, REPEAT_WINDOW_MINUTES):
            idp.recordView(customerId)
            idp.viewCount += 1
        return idp, Company.findByDesigner(idp.designerId)
