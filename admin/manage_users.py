"""
Admin User Management Module.
Allows administrators to view, search, filter, add, edit, and manage citizens and department staff.
"""

import customtkinter as ctk


class ManageUsersPage(ctk.CTkFrame):
    """User Management panel with CRUD operations and role filters."""

    BG_DARK = "#0a0e1a"
    CARD_BG = "#111827"
    ACCENT = "#06b6d4"
    ACCENT2 = "#3b82f6"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    TEXT = "#f1f5f9"
    TEXT_DIM = "#94a3b8"
    TEXT_MUTED = "#64748b"
    INPUT_BG = "#1e293b"
    BORDER = "#334155"

    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.role_filter = ctk.StringVar(value="All")
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="👥 User Management", font=("Segoe UI", 24, "bold"),
                     text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text="Manage registered citizens, department officers, and system accounts",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(anchor="w")

        ctk.CTkButton(
            header, text="➕ Add New User", font=("Segoe UI", 12, "bold"),
            fg_color=self.ACCENT, hover_color="#0891b2", text_color="#ffffff",
            height=38, corner_radius=8, command=self._show_add_user_modal
        ).pack(side="right")

        # Controls Row
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=30, pady=(10, 15))

        self.search_entry = ctk.CTkEntry(
            ctrl, placeholder_text="🔍 Search users by name, email, phone...",
            height=38, width=360, fg_color=self.CARD_BG, border_color=self.BORDER, text_color=self.TEXT
        )
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_users())

        self.role_menu = ctk.CTkOptionMenu(
            ctrl, values=["All", "citizen", "department", "admin"],
            variable=self.role_filter, height=38, width=140,
            fg_color=self.CARD_BG, button_color=self.ACCENT, text_color=self.TEXT,
            dropdown_fg_color=self.CARD_BG, command=lambda v: self.load_users()
        )
        self.role_menu.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            ctrl, text="🔄 Refresh", font=("Segoe UI", 12, "bold"),
            fg_color=self.INPUT_BG, hover_color="#334155", text_color=self.TEXT,
            height=38, width=90, corner_radius=8, command=self.load_users
        ).pack(side="left")

        # Table container
        table_card = ctk.CTkFrame(self, fg_color=self.CARD_BG, corner_radius=16,
                                  border_width=1, border_color=self.BORDER)
        table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Table Header
        th = ctk.CTkFrame(table_card, fg_color=self.INPUT_BG, height=38, corner_radius=8)
        th.pack(fill="x", padx=15, pady=(15, 8))
        th.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        cols = [("ID", 0), ("Full Name", 1), ("Email Address", 2), ("Role", 3), ("Status", 4), ("Actions", 5)]
        for name, cidx in cols:
            ctk.CTkLabel(th, text=name, font=("Segoe UI", 11, "bold"), text_color=self.TEXT_DIM).grid(row=0, column=cidx, sticky="w", padx=10, pady=8)

        # Scrollable Rows
        self.rows_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.rows_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.load_users()

    def load_users(self):
        for w in self.rows_scroll.winfo_children():
            w.destroy()

        role = self.role_filter.get()
        users = self.db.get_all_users(role=None if role == "All" else role)
        query = self.search_entry.get().strip().lower()

        filtered = []
        for u in users:
            if query:
                txt = f"{u['id']} {u['name']} {u['email']} {u.get('phone', '')} {u['role']}".lower()
                if query not in txt:
                    continue
            filtered.append(u)

        if not filtered:
            ctk.CTkLabel(self.rows_scroll, text="No users found.", font=("Segoe UI", 13),
                         text_color=self.TEXT_MUTED).pack(pady=40)
            return

        for u in filtered:
            row = ctk.CTkFrame(self.rows_scroll, fg_color=self.INPUT_BG, corner_radius=8)
            row.pack(fill="x", pady=4)
            row.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            # ID
            ctk.CTkLabel(row, text=f"#{u['id']}", font=("Segoe UI", 12, "bold"),
                         text_color=self.ACCENT).grid(row=0, column=0, sticky="w", padx=10, pady=10)

            # Name
            ctk.CTkLabel(row, text=u["name"], font=("Segoe UI", 12, "bold"),
                         text_color=self.TEXT).grid(row=0, column=1, sticky="w", padx=10)

            # Email
            ctk.CTkLabel(row, text=u["email"], font=("Segoe UI", 11),
                         text_color=self.TEXT_DIM).grid(row=0, column=2, sticky="w", padx=10)

            # Role Badge
            role_col = self.ACCENT2 if u["role"] == "citizen" else (self.PURPLE if u["role"] == "department" else self.WARNING)
            ctk.CTkLabel(row, text=u["role"].capitalize(), font=("Segoe UI", 11, "bold"),
                         text_color=role_col).grid(row=0, column=3, sticky="w", padx=10)

            # Status Badge
            st_col = self.SUCCESS if u["status"] == "active" else self.DANGER
            ctk.CTkLabel(row, text=f"● {u['status'].capitalize()}", font=("Segoe UI", 11, "bold"),
                         text_color=st_col).grid(row=0, column=4, sticky="w", padx=10)

            # Actions
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.grid(row=0, column=5, sticky="w", padx=10)

            if u["status"] == "active":
                ctk.CTkButton(
                    act, text="Block", font=("Segoe UI", 10, "bold"),
                    fg_color=self.DANGER, hover_color="#dc2626", text_color="#ffffff",
                    height=26, width=60, corner_radius=6,
                    command=lambda uid=u["id"]: self._toggle_block(uid, "blocked")
                ).pack(side="left", padx=2)
            else:
                ctk.CTkButton(
                    act, text="Unblock", font=("Segoe UI", 10, "bold"),
                    fg_color=self.SUCCESS, hover_color="#059669", text_color="#ffffff",
                    height=26, width=65, corner_radius=6,
                    command=lambda uid=u["id"]: self._toggle_block(uid, "active")
                ).pack(side="left", padx=2)

    def _toggle_block(self, uid, new_status):
        self.db.update_user(uid, status=new_status)
        self.load_users()

    def _show_add_user_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Add New User")
        modal.geometry("450x520")
        modal.configure(fg_color=self.BG_DARK)
        modal.grab_set()

        ctk.CTkLabel(modal, text="Create New User Account", font=("Segoe UI", 18, "bold"),
                     text_color=self.TEXT).pack(pady=(20, 15))

        fields = [
            ("Full Name", "name_e", False),
            ("Email", "email_e", False),
            ("Phone", "phone_e", False),
            ("Address", "address_e", False),
            ("Password", "pass_e", True),
        ]
        entries = {}
        for label, key, is_pass in fields:
            ctk.CTkLabel(modal, text=label, font=("Segoe UI", 11, "bold"),
                         text_color=self.TEXT_DIM).pack(anchor="w", padx=35, pady=(4, 2))
            e = ctk.CTkEntry(modal, height=36, fg_color=self.INPUT_BG,
                             border_color=self.BORDER, text_color=self.TEXT,
                             show="•" if is_pass else "")
            e.pack(fill="x", padx=35, pady=(0, 6))
            entries[key] = e

        # Role
        ctk.CTkLabel(modal, text="Account Role", font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", padx=35, pady=(4, 2))
        role_var = ctk.StringVar(value="citizen")
        role_opt = ctk.CTkOptionMenu(modal, values=["citizen", "department", "admin"],
                                     variable=role_var, height=36, fg_color=self.INPUT_BG,
                                     button_color=self.ACCENT, text_color=self.TEXT)
        role_opt.pack(fill="x", padx=35, pady=(0, 10))

        err_lbl = ctk.CTkLabel(modal, text="", font=("Segoe UI", 11), text_color=self.DANGER)
        err_lbl.pack(pady=4)

        def save():
            name = entries["name_e"].get().strip()
            email = entries["email_e"].get().strip()
            phone = entries["phone_e"].get().strip()
            address = entries["address_e"].get().strip()
            password = entries["pass_e"].get().strip()
            role = role_var.get()

            if not name or not email or not password:
                err_lbl.configure(text="⚠️ Name, Email, and Password are required.")
                return

            uid = self.db.add_user(name, email, phone, address, password, role)
            if uid:
                modal.destroy()
                self.load_users()
            else:
                err_lbl.configure(text="⚠️ Email already in use.")

        ctk.CTkButton(
            modal, text="Create User", font=("Segoe UI", 13, "bold"),
            fg_color=self.ACCENT, hover_color="#0891b2", text_color="#ffffff",
            height=40, corner_radius=8, command=save
        ).pack(fill="x", padx=35, pady=(10, 20))
