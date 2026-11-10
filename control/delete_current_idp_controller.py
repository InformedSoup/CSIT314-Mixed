"""Control: DeleteCurrentIDPController - user story #25 (Interior Designer deletes a current IDP)."""
from entity.idp import CurrentIDP


class DeleteCurrentIDPController:
    def deleteIDP(self, idpId: int, designerId: int) -> tuple[bool, str]:
        idp = CurrentIDP.findById(idpId)
        if idp is None or not idp.isOwnedBy(designerId):
            return False, "Project not found."
        idp.delete()
        return True, f"'{idp.title}' deleted."
