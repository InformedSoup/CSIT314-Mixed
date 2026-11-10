"""Control: ViewFavouriteListController - user story #36 (Customer views the favourite list)."""
from entity.favourite_list import FavouriteList


class ViewFavouriteListController:
    def getFavouriteList(self, customerId: int) -> list:
        return FavouriteList(customerId).getFavourites()
