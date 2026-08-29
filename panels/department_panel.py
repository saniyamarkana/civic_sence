"""
Department Panel Container for Civic Sense Management System.
Sidebar navigation with Dashboard, Assigned Complaints, and Update Status pages.
"""

import customtkinter as ctk
from department.dashboard import DepartmentDashboard
from department.assigned_complaints import AssignedComplaintsPage
from department.update_status import UpdateStatusPage


class DepartmentPanel(ctk.CTkFrame):
    """Main dashboard layout for municipal department officers."""

    BG_DARK = "#0a0e1a"
    SIDEBAR_BG = "#0c1529"
    CARD_BG = "#111827"
    ACCENT = "#06b6d4"
    ACCENT2 = "#3b82f6"
    TEXT = "#f1f5f9"
    TEXT_DIM = "#94a3b8"
    TEXT_MUTED = "#64748b"
    BORDER = "#1e293b"

    def __init__(self, parent, db, user, on_logout):
        super().__init__(parent, fg_color=self.BG_DARK, corner_radius=0)
        self.db = db
        self.user = user
        self.on_logout = on_logout
        self.department_name = user.get("department", "Sanitation Department") or "Sanitation Department"
        self.active_tab = "dashboard"
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──
        self.sidebar = ctk.CTkFrame(self, fg_color=self.SIDEBAR_BG, corner_radius=0, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Brand header
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=20, pady=(25, 20))

        ctk.CTkLabel(brand_frame, text="🏛️ CivicSense", font=("Segoe UI", 20, "bold"),
                     text_color=self.ACCENT).pack(anchor="w")
        ctk.CTkLabel(brand_frame, text=self.department_name, font=("Segoe UI", 11),
                     text_color=self.TEXT_MUTED).pack(anchor="w")

        # Officer chip
        user_chip = ctk.CTkFrame(self.sidebar, fg_color=self.CARD_BG, corner_radius=12,
                                 border_width=1, border_color=self.BORDER)
        user_chip.pack(fill="x", padx=15, pady=(0, 20))

        chip_inner = ctk.CTkFrame(user_chip, fg_color="transparent")
        chip_inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(chip_inner, text="🏢", font=("Segoe UI Emoji", 20)).pack(side="left", padx=(0, 10))
        chip_text = ctk.CTkFrame(chip_inner, fg_color="transparent")
        chip_text.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(chip_text, text=self.user.get("name", "Officer"),
                     font=("Segoe UI", 12, "bold"), text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(chip_text, text=self.department_name,
                     font=("Segoe UI", 10), text_color=self.ACCENT, anchor="w").pack(anchor="w")

        # Nav items
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("assigned", "📋  Assigned Tasks"),
            ("update", "⚙️  Update Status"),
        ]

        ctk.CTkLabel(self.sidebar, text="OPERATIONS", font=("Segoe UI", 10, "bold"),
                     text_color=self.TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 5))

        for key, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label, font=("Segoe UI", 13, "bold"),
                fg_color=self.ACCENT if key == self.active_tab else "transparent",
                text_color=self.TEXT if key == self.active_tab else self.TEXT_DIM,
                hover_color=self.CARD_BG, height=44, corner_radius=10, anchor="w",
                command=lambda k=key: self.switch_tab(k)
            )
            btn.pack(fill="x", padx=15, pady=4)
            self.nav_buttons[key] = btn

        # Logout at bottom
        self.sidebar.pack_propagate(False)
        logout_btn = ctk.CTkButton(
            self.sidebar, text="🚪  Log Out", font=("Segoe UI", 13, "bold"),
            fg_color="transparent", text_color="#ef4444", hover_color="#2d1518",
            height=42, corner_radius=10, anchor="w", command=self.on_logout
        )
        logout_btn.pack(side="bottom", fill="x", padx=15, pady=20)

        # ── Main Content Area ──
        self.main_content = ctk.CTkFrame(self, fg_color=self.BG_DARK, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")

        self.switch_tab(self.active_tab)

    def switch_tab(self, tab_key):
        self.active_tab = tab_key

        # Update button highlights
        for key, btn in self.nav_buttons.items():
            is_active = (key == tab_key)
            btn.configure(
                fg_color=self.ACCENT if is_active else "transparent",
                text_color=self.TEXT if is_active else self.TEXT_DIM
            )

        # Clear main content
        for w in self.main_content.winfo_children():
            w.destroy()

        if tab_key == "dashboard":
            page = DepartmentDashboard(self.main_content, self.db, self.user)
            page.pack(fill="both", expand=True)
        elif tab_key == "assigned":
            page = AssignedComplaintsPage(self.main_content, self.db, self.user)
            page.pack(fill="both", expand=True)
        elif tab_key == "update":
            page = UpdateStatusPage(self.main_content, self.db, self.user)
            page.pack(fill="both", expand=True)
