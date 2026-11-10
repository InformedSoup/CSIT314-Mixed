"""Control: SaveFavouriteController - user story #35 (Customer saves an IDP to the favourite list).

Saving an IDP counts as shortlisting it for the designer's tracking (#39).
"""
from entity.favourite_list import FavouriteList
from entity.idp import InteriorDesignProject


class SaveFavouriteController:
    def saveIDP(self, customerId: int, idpId: int) -> tuple[bool, str]:
        idp = InteriorDesignProject.findById(idpId)
        if idp is None:
            return False, "Project not found."
        if not FavouriteList(customerId).add(idpId):
            return False, f"'{idp.title}' is already in your favourites."
        return True, f"'{idp.title}' saved to your favourites."

    def removeIDP(self, customerId: int, idpId: int) -> tuple[bool, str]:
        if not FavouriteList(customerId).remove(idpId):
            return False, "That project is not in your favourites."
        return True, "Removed from your favourites."

    def isSaved(self, customerId: int, idpId: int) -> bool:
        return FavouriteList(customerId).contains(idpId)
