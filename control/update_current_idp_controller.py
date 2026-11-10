"""Control: UpdateCurrentIDPController - user story #24 (Interior Designer updates a current IDP)."""
from control.idp_validation import validate_completion_date, validate_idp
from entity.idp import CurrentIDP


class UpdateCurrentIDPController:
    def _own(self, idpId, designerId):
        idp = CurrentIDP.findById(idpId)
        return idp if idp and idp.isOwnedBy(designerId) else None

    def handleUpdateIDP(self, idpId: int, designerId: int, idpDetails: dict) -> tuple[bool, str]:
        idp = self._own(idpId, designerId)
        if idp is None:
            return False, "Project not found."
        errors = validate_idp(idpDetails, "CURRENT")
        if errors:
            return False, " ".join(errors)
        idp.updateDetails(idpDetails)
        return True, "Project updated."

    def markCompleted(self, idpId: int, designerId: int, completionDate: str) -> tuple[bool, str]:
        """Finish an ongoing project: it moves to the past portfolio."""
        idp = self._own(idpId, designerId)
        if idp is None:
            return False, "Project not found."
        errors = validate_completion_date(completionDate)
        if errors:
            return False, " ".join(errors)
        idp.markCompleted(completionDate)
        return True, f"'{idp.title}' marked as completed and moved to past projects."
