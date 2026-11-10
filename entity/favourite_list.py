"""Entity: FavouriteList - the IDPs a customer has saved (shortlisted)."""
from __future__ import annotations

from db import get_connection
from entity.idp import InteriorDesignProject


class FavouriteList:
    def __init__(self, customerId: int):
        self.customerId = customerId

    def contains(self, idpId: int) -> bool:
        row = get_connection().execute(
            "SELECT 1 FROM favourite WHERE customer_id = ? AND idp_id = ?", (self.customerId, idpId)
        ).fetchone()
        return row is not None

    def add(self, idpId: int) -> bool:
        """Save an IDP. Returns False if it was already saved."""
        if self.contains(idpId):
            return False
        connection = get_connection()
        connection.execute("INSERT INTO favourite (customer_id, idp_id) VALUES (?, ?)", (self.customerId, idpId))
        connection.commit()
        return True

    def remove(self, idpId: int) -> bool:
        connection = get_connection()
        cursor = connection.execute(
            "DELETE FROM favourite WHERE customer_id = ? AND idp_id = ?", (self.customerId, idpId)
        )
        connection.commit()
        return cursor.rowcount > 0

    def getFavourites(self) -> list[InteriorDesignProject]:
        return InteriorDesignProject._query(
            "JOIN favourite fav ON fav.idp_id = i.idp_id WHERE fav.customer_id = ?",
            (self.customerId,), "fav.saved_at DESC",
        )
