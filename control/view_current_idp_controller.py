"""Control: ViewCurrentIDPController - user story #22 (Interior Designer views a current IDP)."""
from entity.idp import CurrentIDP


class ViewCurrentIDPController:
    def getCurrentIDPs(self, designerId: int) -> list[CurrentIDP]:
        return CurrentIDP.findForDesigner(designerId)

    def getIDPDetails(self, idpId: int, designerId: int) -> CurrentIDP | None:
        idp = CurrentIDP.findById(idpId)
        return idp if idp and idp.isOwnedBy(designerId) else None
