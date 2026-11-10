"""Control: CreatePastIDPController - user story #26 (Interior Designer creates a past IDP)."""
from control.idp_validation import validate_idp
from entity.idp import PastIDP


class CreatePastIDPController:
    def validateInput(self, idpDetails: dict) -> list[str]:
        return validate_idp(idpDetails, "PAST")

    def createPastIDP(self, designerId: int, idpDetails: dict) -> tuple[bool, str, int | None]:
        errors = self.validateInput(idpDetails)
        if errors:
            return False, " ".join(errors), None
        idpId = PastIDP.createIDP(designerId, idpDetails)
        return True, "Past project added to your portfolio.", idpId
