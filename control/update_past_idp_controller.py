"""Control: UpdatePastIDPController - user story #29 (Interior Designer updates a past IDP)."""
from control.idp_validation import validate_idp
from entity.idp import PastIDP


class UpdatePastIDPController:
    def handleUpdateIDP(self, idpId: int, designerId: int, idpDetails: dict) -> tuple[bool, str]:
        idp = PastIDP.findById(idpId)
        if idp is None or not idp.isOwnedBy(designerId):
            return False, "Project not found."
        errors = validate_idp(idpDetails, "PAST")
        if errors:
            return False, " ".join(errors)
        idp.updateDetails(idpDetails)
        return True, "Project updated."
