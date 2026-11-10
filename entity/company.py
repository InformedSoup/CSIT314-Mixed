"""Entity: Company - business details an interior designer shows to customers."""
from __future__ import annotations

from dataclasses import dataclass

from db import get_connection


@dataclass
class Company:
    companyId: int
    designerId: int
    companyName: str
    regNumber: str
    description: str
    address: str
    contactNumber: str
    createdAt: str

    @classmethod
    def _fromRow(cls, row) -> "Company":
        return cls(row["company_id"], row["designer_id"], row["company_name"], row["reg_number"],
                   row["description"], row["address"], row["contact_number"], row["created_at"])

    @classmethod
    def regNumberExists(cls, regNumber: str, excludeCompanyId: int | None = None) -> bool:
        row = get_connection().execute(
            "SELECT 1 FROM company WHERE reg_number = ? AND company_id IS NOT ?",
            (regNumber.strip(), excludeCompanyId),
        ).fetchone()
        return row is not None

    # ---- create -------------------------------------------------------------
    @classmethod
    def save(cls, designerId: int, companyName: str, regNumber: str, description: str,
             address: str, contactNumber: str) -> int:
        connection = get_connection()
        cursor = connection.execute(
            """INSERT INTO company (designer_id, company_name, reg_number, description, address, contact_number)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (designerId, companyName.strip(), regNumber.strip().upper(), description.strip(),
             address.strip(), contactNumber.strip()),
        )
        connection.commit()
        return cursor.lastrowid

    # ---- read ---------------------------------------------------------------
    @classmethod
    def findById(cls, companyId: int) -> "Company | None":
        row = get_connection().execute("SELECT * FROM company WHERE company_id = ?", (companyId,)).fetchone()
        return cls._fromRow(row) if row else None

    @classmethod
    def findByDesigner(cls, designerId: int) -> list["Company"]:
        rows = get_connection().execute(
            "SELECT * FROM company WHERE designer_id = ? ORDER BY company_name", (designerId,)
        ).fetchall()
        return [cls._fromRow(r) for r in rows]

    @classmethod
    def searchCompanies(cls, designerId: int, keyword: str) -> list["Company"]:
        like = f"%{keyword.strip()}%"
        rows = get_connection().execute(
            """SELECT * FROM company WHERE designer_id = ?
               AND (company_name LIKE ? OR reg_number LIKE ? OR address LIKE ? OR description LIKE ?)
               ORDER BY company_name""",
            (designerId, like, like, like, like),
        ).fetchall()
        return [cls._fromRow(r) for r in rows]

    def isOwnedBy(self, designerId: int) -> bool:
        return self.designerId == designerId

    # ---- update / delete ----------------------------------------------------
    def updateCompanyDetails(self, companyName: str, regNumber: str, description: str,
                             address: str, contactNumber: str) -> bool:
        connection = get_connection()
        connection.execute(
            """UPDATE company SET company_name = ?, reg_number = ?, description = ?, address = ?,
               contact_number = ? WHERE company_id = ?""",
            (companyName.strip(), regNumber.strip().upper(), description.strip(), address.strip(),
             contactNumber.strip(), self.companyId),
        )
        connection.commit()
        return True

    def delete(self) -> bool:
        connection = get_connection()
        connection.execute("DELETE FROM company WHERE company_id = ?", (self.companyId,))
        connection.commit()
        return True
