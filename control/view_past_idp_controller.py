"""Control: ViewPastIDPController - user story #27 (Interior Designer views a past IDP)."""
from entity.idp import PastIDP


class ViewPastIDPController:
    def getPastIDPs(self, designerId: int) -> list[PastIDP]:
        return PastIDP.findForDesigner(designerId)

    def getIDPDetails(self, idpId: int, designerId: int) -> PastIDP | None:
        idp = PastIDP.findById(idpId)
        return idp if idp and idp.isOwnedBy(designerId) else None
