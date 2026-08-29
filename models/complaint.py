"""Complaint model for the Civic Sense Management System."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Complaint:
    """Represents a civic complaint."""
    id: int = 0
    citizen_id: int = 0
    title: str = ""
    description: str = ""
    category: str = ""
    location: str = ""
    priority: str = "Medium"
    status: str = "Pending"
    department: str = ""
    admin_remarks: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Category choices
    CATEGORIES = [
        "Garbage", "Pothole", "Water Leakage", "Streetlight",
        "Drainage", "Illegal Parking", "Public Cleanliness", "Damaged Road"
    ]

    PRIORITIES = ["Low", "Medium", "High"]

    STATUSES = ["Pending", "Approved", "In Progress", "Resolved", "Rejected"]

    @classmethod
    def from_row(cls, row):
        """Create a Complaint from a database row."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            citizen_id=row["citizen_id"],
            title=row["title"],
            description=row["description"] or "",
            category=row["category"],
            location=row["location"] or "",
            priority=row["priority"],
            status=row["status"],
            department=row["department"] or "",
            admin_remarks=row["admin_remarks"] or "",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
