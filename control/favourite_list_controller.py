"""Control: FavouriteListController - user story #37 (Customer views an IDP from the favourite list)."""
from control.view_idp_controller import ViewIDPController
from entity.favourite_list import FavouriteList


class FavouriteListController:
    def getFavouriteIDPs(self, customerId: int) -> list:
        return FavouriteList(customerId).getFavourites()

    def getIDPDetails(self, customerId: int, idpId: int):
        """Only opens IDPs that really are in this customer's list. Returns (idp, companies)."""
        if not FavouriteList(customerId).contains(idpId):
            return None, []
        return ViewIDPController().getIDPDetails(idpId, customerId)
