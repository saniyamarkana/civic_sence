"""
CivicSense - Smart Civic Complaint Management System.
Phase 1: Core Data Handling using Linear Structures (CLO1).

Main entry point initializing CustomTkinter theme, database, and panel routing.
"""

import customtkinter as ctk
from database.database import Database
from dsa.dataset import SampleDataset
from panels.login import LoginPanel
from panels.citizen_panel import CitizenPanel
from panels.admin_panel import AdminPanel
from panels.department_panel import DepartmentPanel


class CivicSenseApp(ctk.CTk):
    """Main Application Window managing root geometry and view routing."""

    BG_DARK = "#0a0e1a"

    def __init__(self):
        super().__init__()

        # Appearance Settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Window Configuration
        self.title("CivicSense — Civic Complaint Management & DSA Platform")
        self.geometry("1240x780")
        self.minsize(1050, 680)
        self.configure(fg_color=self.BG_DARK)

        # Database Singleton
        self.db = Database()
        self._seed_sample_complaints()

        # Session State
        self.current_user = None
        self.current_role = None
        self.active_panel = None

        # Start with Login Screen
        self.show_login()

    def _seed_sample_complaints(self):
        """Seed initial complaints if database is empty."""
        existing = self.db.get_all_complaints()
        if len(existing) == 0:
            # Create a sample citizen first
            c_id = self.db.add_user("Rahul Sharma", "citizen@civicsense.com", "9876543210",
                                     "Area A, Sector 4", "citizen123", "citizen")
            if not c_id:
                u = self.db.get_user_by_email("citizen@civicsense.com")
                c_id = u["id"] if u else 1

            samples = SampleDataset.get_complaints()
            for s in samples:
                # Map category to department
                dept_map = {
                    "Garbage": "Sanitation Department",
                    "Pothole": "Road Department",
                    "Water Leakage": "Water Department",
                    "Streetlight": "Electricity Department",
                    "Drainage": "Water Department",
                    "Illegal Parking": "Traffic Department",
                    "Public Cleanliness": "Sanitation Department",
                    "Damaged Road": "Road Department"
                }
                cid = self.db.add_complaint(
                    citizen_id=c_id,
                    title=s["title"],
                    description=s["description"],
                    category=s["category"],
                    location=s["location"],
                    priority=s["priority"]
                )
                dept = dept_map.get(s["category"], "Sanitation Department")
                self.db.update_complaint(cid, status=s["status"], department=dept)

    def show_login(self):
        """Display the split-screen login view."""
        self._clear_view()
        self.active_panel = LoginPanel(self, self.db, on_login_success=self._on_login_success)
        self.active_panel.pack(fill="both", expand=True)

    def _on_login_success(self, user, role):
        """Callback when authentication succeeds."""
        self.current_user = user
        self.current_role = role
        self._clear_view()

        if role == "citizen":
            self.active_panel = CitizenPanel(self, self.db, user, on_logout=self.logout)
            self.active_panel.pack(fill="both", expand=True)
        elif role == "admin":
            self.active_panel = AdminPanel(self, self.db, user, on_logout=self.logout)
            self.active_panel.pack(fill="both", expand=True)
        elif role == "department":
            self.active_panel = DepartmentPanel(self, self.db, user, on_logout=self.logout)
            self.active_panel.pack(fill="both", expand=True)

    def logout(self):
        """Log out the current user and return to login."""
        self.current_user = None
        self.current_role = None
        self.show_login()

    def _clear_view(self):
        """Destroy existing panel before mounting new one."""
        if self.active_panel:
            self.active_panel.destroy()
            self.active_panel = None


if __name__ == "__main__":
    app = CivicSenseApp()
    app.mainloop()
