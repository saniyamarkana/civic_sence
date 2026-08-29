"""
Admin Panel Container for Civic Sense Management System.
Sidebar navigation with Dashboard, User/Complaint Management, and 6 DSA Visual Labs.
"""

import customtkinter as ctk
from admin.dashboard import AdminDashboard
from admin.manage_users import ManageUsersPage
from admin.manage_complaints import ManageComplaintsPage


class AdminPanel(ctk.CTkFrame):
    """Main administrative dashboard layout with DSA lab tools."""

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
        self.active_tab = "dashboard"
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0, minsize=260)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──
        self.sidebar = ctk.CTkFrame(self, fg_color=self.SIDEBAR_BG, corner_radius=0, width=260)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Scrollable inner sidebar so all DSA tools fit nicely
        sb_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        sb_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Brand header
        brand_frame = ctk.CTkFrame(sb_scroll, fg_color="transparent")
        brand_frame.pack(fill="x", padx=20, pady=(20, 15))

        ctk.CTkLabel(brand_frame, text="🛡️ CivicSense", font=("Segoe UI", 20, "bold"),
                     text_color=self.ACCENT).pack(anchor="w")
        ctk.CTkLabel(brand_frame, text="Administrator Portal & DSA Lab", font=("Segoe UI", 11),
                     text_color=self.TEXT_MUTED).pack(anchor="w")

        # User chip
        user_chip = ctk.CTkFrame(sb_scroll, fg_color=self.CARD_BG, corner_radius=12,
                                 border_width=1, border_color=self.BORDER)
        user_chip.pack(fill="x", padx=15, pady=(0, 15))

        chip_inner = ctk.CTkFrame(user_chip, fg_color="transparent")
        chip_inner.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(chip_inner, text="👑", font=("Segoe UI Emoji", 18)).pack(side="left", padx=(0, 8))
        chip_text = ctk.CTkFrame(chip_inner, fg_color="transparent")
        chip_text.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(chip_text, text=self.user.get("name", "Admin"),
                     font=("Segoe UI", 12, "bold"), text_color=self.TEXT, anchor="w").pack(anchor="w")
        ctk.CTkLabel(chip_text, text="System Administrator",
                     font=("Segoe UI", 10), text_color="#f59e0b", anchor="w").pack(anchor="w")

        # Nav Sections
        self.nav_buttons = {}

        # 1. CORE SECTION
        self._add_nav_section(sb_scroll, "MANAGEMENT", [
            ("dashboard", "📊  Dashboard"),
            ("manage_complaints", "🛡️  All Complaints"),
            ("manage_users", "👥  Manage Users"),
        ])

        # 2. DSA LAB TOOLS (Phase 1 Syllabus)
        # self._add_nav_section(sb_scroll, "PHASE 1 DSA LAB", [
        #     ("queue", "🔄  Queue (FIFO / Emergency)"),
        #     ("stack", "🥞  Stack (Undo / History)"),
        #     ("linked_list", "🔗  Linked List (Chains)"),
        #     ("expression", "🧮  Expression Parser"),
        #     ("iterative", "⚡  Iterative Algorithms"),
        #     ("recursive", "🌳  Recursive Call Tree"),
        # ])

        # Logout at bottom of sidebar
        logout_btn = ctk.CTkButton(
            self.sidebar, text="🚪  Log Out", font=("Segoe UI", 13, "bold"),
            fg_color="transparent", text_color="#ef4444", hover_color="#2d1518",
            height=42, corner_radius=10, anchor="w", command=self.on_logout
        )
        logout_btn.pack(side="bottom", fill="x", padx=15, pady=15)

        # ── Main Content Area ──
        self.main_content = ctk.CTkFrame(self, fg_color=self.BG_DARK, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")

        self.switch_tab(self.active_tab)

    def _add_nav_section(self, parent, title, items):
        ctk.CTkLabel(parent, text=title, font=("Segoe UI", 10, "bold"),
                     text_color=self.TEXT_MUTED).pack(anchor="w", padx=20, pady=(10, 4))

        for key, label in items:
            btn = ctk.CTkButton(
                parent, text=label, font=("Segoe UI", 12, "bold"),
                fg_color=self.ACCENT if key == self.active_tab else "transparent",
                text_color=self.TEXT if key == self.active_tab else self.TEXT_DIM,
                hover_color=self.CARD_BG, height=38, corner_radius=8, anchor="w",
                command=lambda k=key: self.switch_tab(k)
            )
            btn.pack(fill="x", padx=15, pady=2)
            self.nav_buttons[key] = btn

    def switch_tab(self, tab_key):
        self.active_tab = tab_key

        # Update button states
        for key, btn in self.nav_buttons.items():
            is_active = (key == tab_key)
            btn.configure(
                fg_color=self.ACCENT if is_active else "transparent",
                text_color=self.TEXT if is_active else self.TEXT_DIM
            )

        # Clear content
        for w in self.main_content.winfo_children():
            w.destroy()

        if tab_key == "dashboard":
            page = AdminDashboard(self.main_content, self.db)
            page.pack(fill="both", expand=True)
        elif tab_key == "manage_complaints":
            page = ManageComplaintsPage(self.main_content, self.db, self.user)
            page.pack(fill="both", expand=True)
        elif tab_key == "manage_users":
            page = ManageUsersPage(self.main_content, self.db)
            page.pack(fill="both", expand=True)
