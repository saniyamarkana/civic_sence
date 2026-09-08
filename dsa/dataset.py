"""
Sample dataset for Civic Sense Management System.
Provides pre-built complaint and citizen data for DSA demonstrations.
"""


class SampleDataset:
    """Provides sample data for DSA operations."""

    COMPLAINTS = [
        {"id": 101, "citizen_id": 1, "title": "Garbage near market",
         "category": "Garbage", "location": "Area A", "priority": "High",
         "status": "Pending", "description": "Garbage dumped near the main road market area."},
        {"id": 102, "citizen_id": 2, "title": "Large pothole on highway",
         "category": "Pothole", "location": "Area B", "priority": "Medium",
         "status": "In Progress", "description": "Large pothole on the main highway causing accidents."},
        {"id": 103, "citizen_id": 3, "title": "Streetlight not working",
         "category": "Streetlight", "location": "Area C", "priority": "Low",
         "status": "Resolved", "description": "Streetlight at corner of 5th avenue not working."},
        {"id": 104, "citizen_id": 4, "title": "Water pipe leakage",
         "category": "Water Leakage", "location": "Area A", "priority": "High",
         "status": "Pending", "description": "Water pipe leaking near residential colony."},
        {"id": 105, "citizen_id": 5, "title": "Drainage overflow",
         "category": "Drainage", "location": "Area D", "priority": "High",
         "status": "Pending", "description": "Drainage overflowing on main street."},
        {"id": 106, "citizen_id": 1, "title": "Illegal parking at temple road",
         "category": "Illegal Parking", "location": "Area B", "priority": "Medium",
         "status": "Approved", "description": "Vehicles parked illegally blocking the road."},
        {"id": 107, "citizen_id": 2, "title": "Road damage after rain",
         "category": "Damaged Road", "location": "Area C", "priority": "Medium",
         "status": "In Progress", "description": "Road surface damaged after heavy rainfall."},
        {"id": 108, "citizen_id": 3, "title": "Public toilet unclean",
         "category": "Public Cleanliness", "location": "Area D", "priority": "Low",
         "status": "Pending", "description": "Public toilet near bus stand is very unclean."},
        {"id": 109, "citizen_id": 4, "title": "Water supply disrupted",
         "category": "Water Leakage", "location": "Area A", "priority": "High",
         "status": "Approved", "description": "Water supply disrupted for 2 days."},
        {"id": 110, "citizen_id": 5, "title": "Garbage collection delayed",
         "category": "Garbage", "location": "Area B", "priority": "Medium",
         "status": "Pending", "description": "Garbage not collected for a week."},
    ]

    CITIZENS = [
        {"id": 1, "name": "Rahul Sharma", "email": "rahul@example.com", "phone": "9876543210"},
        {"id": 2, "name": "Priya Patel", "email": "priya@example.com", "phone": "9876543211"},
        {"id": 3, "name": "Amit Kumar", "email": "amit@example.com", "phone": "9876543212"},
        {"id": 4, "name": "Sneha Gupta", "email": "sneha@example.com", "phone": "9876543213"},
        {"id": 5, "name": "Vikram Singh", "email": "vikram@example.com", "phone": "9876543214"},
    ]

    PRIORITY_VALUES = {"High": 3, "Medium": 2, "Low": 1}

    @classmethod
    def get_complaints(cls):
        """Return a copy of the sample complaints list."""
        return [c.copy() for c in cls.COMPLAINTS]

    @classmethod
    def get_priority_value(cls, priority):
        """Return numeric priority value."""
        return cls.PRIORITY_VALUES.get(priority, 0)

    @classmethod
    def get_complaint_ids(cls):
        """Return sorted list of complaint IDs."""
        return sorted(c["id"] for c in cls.COMPLAINTS)

    @classmethod
    def get_priorities_list(cls):
        """Return list of (id, priority_value) tuples for sorting demos."""
        return [(c["id"], cls.PRIORITY_VALUES.get(c["priority"], 0)) for c in cls.COMPLAINTS]

    # ──────────────────── Citizen helpers ────────────────────

    @classmethod
    def get_citizens(cls):
        """Return a copy of the sample citizens list."""
        return [c.copy() for c in cls.CITIZENS]

    @classmethod
    def get_citizen_by_id(cls, citizen_id):
        """Return a citizen record by ID, or None."""
        for c in cls.CITIZENS:
            if c["id"] == citizen_id:
                return c.copy()
        return None

    # ──────────────────── Simple record (list-of-values) format ────────────────────

    @classmethod
    def get_records(cls):
        """
        Return complaints as a list of flat value tuples (list of simple records).
        Phase 1 requirement: "Defining dataset input (list of values or simple records)".
        
        Each record is a tuple: (id, title, category, location, priority, status)
        """
        return [
            (
                c["id"],
                c["title"],
                c["category"],
                c["location"],
                c["priority"],
                c["status"],
            )
            for c in cls.COMPLAINTS
        ]

    @classmethod
    def get_record_headers(cls):
        """Return column headers for get_records()."""
        return ["id", "title", "category", "location", "priority", "status"]

    @classmethod
    def get_id_list(cls):
        """
        Return a plain list of complaint IDs (simplest possible dataset input).
        Demonstrates Phase 1: list of values.
        """
        return [c["id"] for c in cls.COMPLAINTS]

    @classmethod
    def get_priority_score_list(cls):
        """
        Return list of (complaint_id, priority_score) pairs as numeric values.
        Used with stack-based expression evaluator for score calculation.
        """
        return [(c["id"], cls.PRIORITY_VALUES.get(c["priority"], 0)) for c in cls.COMPLAINTS]
