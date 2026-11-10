"""Control: CreateCurrentIDPController - user story #21 (Interior Designer creates a current IDP)."""
from control.idp_validation import validate_idp
from entity.idp import CurrentIDP


class CreateCurrentIDPController:
    def validateInput(self, idpDetails: dict) -> list[str]:
        return validate_idp(idpDetails, "CURRENT")

    def handleCreateIDP(self, designerId: int, idpDetails: dict) -> tuple[bool, str, int | None]:
        errors = self.validateInput(idpDetails)
        if errors:
            return False, " ".join(errors), None
        idpId = CurrentIDP.createIDP(designerId, idpDetails)
        return True, "Current project created.", idpId
