"""
Department Assigned Complaints Module.
Allows department officers to view, filter, accept, and start work on complaints assigned to their department.
"""

# pyrefly: ignore [missing-import]
import customtkinter as ctk


class AssignedComplaintsPage(ctk.CTkFrame):
    """View and manage assigned complaints for the logged in department."""

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

    STATUS_COLORS = {
        "Pending": "#f59e0b",
        "Approved": "#06b6d4",
        "In Progress": "#3b82f6",
        "Resolved": "#10b981",
        "Rejected": "#ef4444"
    }

    PRIORITY_COLORS = {
        "High": "#ef4444",
        "Medium": "#f59e0b",
        "Low": "#10b981"
    }

    def __init__(self, parent, db, user, on_select_update=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.user = user
        self.department_name = user.get("department", "Sanitation Department") or "Sanitation Department"
        self.on_select_update = on_select_update
        self.status_filter = ctk.StringVar(value="All")
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text=f"📋 {self.department_name} - Assigned Tasks", font=("Segoe UI", 24, "bold"),
                     text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text="Review civic complaints assigned to your jurisdiction",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(anchor="w")

        # Controls Row
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=30, pady=(10, 15))

        self.search_entry = ctk.CTkEntry(
            ctrl, placeholder_text="🔍 Search assigned tasks...",
            height=38, width=320, fg_color=self.CARD_BG, border_color=self.BORDER, text_color=self.TEXT
        )
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_complaints())

        self.status_menu = ctk.CTkOptionMenu(
            ctrl, values=["All", "Pending", "Approved", "In Progress", "Resolved"],
            variable=self.status_filter, height=38, width=140,
            fg_color=self.CARD_BG, button_color=self.ACCENT, text_color=self.TEXT,
            dropdown_fg_color=self.CARD_BG, command=lambda v: self.load_complaints()
        )
        self.status_menu.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            ctrl, text="🔄 Refresh", font=("Segoe UI", 12, "bold"),
            fg_color=self.INPUT_BG, hover_color="#334155", text_color=self.TEXT,
            height=38, width=90, corner_radius=8, command=self.load_complaints
        ).pack(side="left")

        # Table Card
        table_card = ctk.CTkFrame(self, fg_color=self.CARD_BG, corner_radius=16,
                                  border_width=1, border_color=self.BORDER)
        table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Table Header
        th = ctk.CTkFrame(table_card, fg_color=self.INPUT_BG, height=38, corner_radius=8)
        th.pack(fill="x", padx=15, pady=(15, 8))
        th.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        cols = [("ID", 0), ("Title / Issue", 1), ("Location", 2), ("Priority", 3), ("Status", 4), ("Quick Actions", 5)]
        for name, cidx in cols:
            ctk.CTkLabel(th, text=name, font=("Segoe UI", 11, "bold"), text_color=self.TEXT_DIM).grid(row=0, column=cidx, sticky="w", padx=10, pady=8)

        # Scrollable Rows
        self.rows_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.rows_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.load_complaints()

    def load_complaints(self):
        for w in self.rows_scroll.winfo_children():
            w.destroy()

        complaints = self.db.get_department_complaints(self.department_name)
        filt = self.status_filter.get()
        query = self.search_entry.get().strip().lower()

        filtered = []
        for c in complaints:
            if filt != "All" and c["status"] != filt:
                continue
            if query:
                txt = f"{c['id']} {c['title']} {c.get('location','')} {c['priority']}".lower()
                if query not in txt:
                    continue
            filtered.append(c)

        if not filtered:
            ctk.CTkLabel(self.rows_scroll, text="No complaints found for this department.",
                         font=("Segoe UI", 13), text_color=self.TEXT_MUTED).pack(pady=40)
            return

        for c in filtered:
            row = ctk.CTkFrame(self.rows_scroll, fg_color=self.INPUT_BG, corner_radius=8)
            row.pack(fill="x", pady=4)
            row.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            # ID
            ctk.CTkLabel(row, text=f"#{c['id']}", font=("Segoe UI", 12, "bold"),
                         text_color=self.ACCENT).grid(row=0, column=0, sticky="w", padx=10, pady=10)

            # Title
            ctk.CTkLabel(row, text=c["title"][:22] + ("..." if len(c["title"]) > 22 else ""),
                         font=("Segoe UI", 12, "bold"), text_color=self.TEXT).grid(row=0, column=1, sticky="w", padx=10)

            # Location
            ctk.CTkLabel(row, text=c["location"] or "-", font=("Segoe UI", 11),
                         text_color=self.TEXT_DIM).grid(row=0, column=2, sticky="w", padx=10)

            # Priority
            pr_col = self.PRIORITY_COLORS.get(c["priority"], self.TEXT)
            ctk.CTkLabel(row, text=c["priority"], font=("Segoe UI", 11, "bold"),
                         text_color=pr_col).grid(row=0, column=3, sticky="w", padx=10)

            # Status
            st_col = self.STATUS_COLORS.get(c["status"], self.TEXT_MUTED)
            ctk.CTkLabel(row, text=f"● {c['status']}", font=("Segoe UI", 11, "bold"),
                         text_color=st_col).grid(row=0, column=4, sticky="w", padx=10)

            # Action Buttons
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.grid(row=0, column=5, sticky="w", padx=10)

            if c["status"] in ("Pending", "Approved"):
                ctk.CTkButton(
                    act, text="▶ Start Work", font=("Segoe UI", 10, "bold"),
                    fg_color=self.ACCENT2, hover_color="#2563eb", text_color="#ffffff",
                    height=26, width=80, corner_radius=6,
                    command=lambda cid=c["id"]: self._quick_update(cid, "In Progress")
                ).pack(side="left", padx=2)
            elif c["status"] == "In Progress":
                ctk.CTkButton(
                    act, text="✅ Resolve", font=("Segoe UI", 10, "bold"),
                    fg_color=self.SUCCESS, hover_color="#059669", text_color="#ffffff",
                    height=26, width=75, corner_radius=6,
                    command=lambda cid=c["id"]: self._quick_update(cid, "Resolved")
                ).pack(side="left", padx=2)

    def _quick_update(self, cid, status):
        self.db.update_complaint(
            cid, changed_by=self.user["id"], status=status,
            remarks=f"Department updated status to {status}."
        )
        self.load_complaints()
