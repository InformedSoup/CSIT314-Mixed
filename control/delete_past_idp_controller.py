"""Control: DeletePastIDPController - user story #30 (Interior Designer deletes a past IDP)."""
from entity.idp import PastIDP


class DeletePastIDPController:
    def deleteIDP(self, idpId: int, designerId: int) -> tuple[bool, str]:
        idp = PastIDP.findById(idpId)
        if idp is None or not idp.isOwnedBy(designerId):
            return False, "Project not found."
        idp.delete()
        return True, f"'{idp.title}' removed from your portfolio."
