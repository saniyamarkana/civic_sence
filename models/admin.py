"""Admin model for the Civic Sense Management System."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Admin:
    """Represents an administrator user."""
    id: int = 0
    name: str = ""
    email: str = ""
    phone: str = ""
    role: str = "admin"
    password: str = ""
    password_hash: str = ""
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @classmethod
    def from_row(cls, row):
        """Create an Admin from a database row."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            phone=row["phone"] or "",
            role=row["role"],
            password=row.get("password", "") or "",
            password_hash=row.get("password", "") or "",
            status=row["status"],
            created_at=row["created_at"],
        )
