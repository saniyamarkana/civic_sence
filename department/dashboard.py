"""
Department Dashboard Overview.
Displays department-specific complaint metrics, workload distributions, and action items.
"""

# pyrefly: ignore [missing-import]
import customtkinter as ctk


class DepartmentDashboard(ctk.CTkFrame):
    """Department Officer Dashboard Overview."""

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

    def __init__(self, parent, db, user):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.user = user
        self.department_name = user.get("department", "Sanitation Department") or "Sanitation Department"
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text=f"🏢 {self.department_name} Dashboard", font=("Segoe UI", 24, "bold"),
                     text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text="Manage assigned municipal complaints and field operations",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(anchor="w")

        # Scrollable Body
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        self._render_dashboard()

    def _render_dashboard(self):
        stats = self.db.get_department_stats(self.department_name)
        complaints = self.db.get_department_complaints(self.department_name)

        # ── Stat Cards Row ──
        stats_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 20))
        stats_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._create_stat_card(stats_row, 0, "Assigned Total", str(stats.get("total", 0)), self.ACCENT, "📋")
        self._create_stat_card(stats_row, 1, "Pending Start", str(stats.get("pending", 0)), self.WARNING, "⏳")
        self._create_stat_card(stats_row, 2, "In Progress", str(stats.get("in_progress", 0)), self.ACCENT2, "⚙️")
        self._create_stat_card(stats_row, 3, "Resolved", str(stats.get("resolved", 0)), self.SUCCESS, "✅")

        # ── Priority Attention Card ──
        att_card = ctk.CTkFrame(self.scroll, fg_color=self.CARD_BG, corner_radius=16,
                                border_width=1, border_color=self.BORDER)
        att_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(att_card, text="🚨 High-Priority Urgent Assignments", font=("Segoe UI", 16, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=20, pady=(15, 10))

        high_prios = [c for c in complaints if c["priority"] == "High" and c["status"] != "Resolved"]
        if not high_prios:
            ctk.CTkLabel(att_card, text="✓ No urgent high-priority complaints pending for this department!",
                         font=("Segoe UI", 12), text_color=self.SUCCESS).pack(anchor="w", padx=20, pady=(0, 15))
        else:
            for c in high_prios[:3]:
                row = ctk.CTkFrame(att_card, fg_color=self.INPUT_BG, corner_radius=8)
                row.pack(fill="x", padx=20, pady=4)
                ctk.CTkLabel(row, text=f"#{c['id']}", font=("Segoe UI", 11, "bold"), text_color=self.DANGER, padx=10, pady=8).pack(side="left")
                ctk.CTkLabel(row, text=c["title"], font=("Segoe UI", 12, "bold"), text_color=self.TEXT).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=f"📍 {c['location']}", font=("Segoe UI", 11), text_color=self.TEXT_DIM).pack(side="left", padx=10)
                ctk.CTkLabel(row, text=f"● {c['status']}", font=("Segoe UI", 11, "bold"), text_color=self.WARNING, padx=10).pack(side="right")
            ctk.CTkFrame(att_card, height=10, fg_color="transparent").pack()

        # ── Recent Work Log ──
        table_card = ctk.CTkFrame(self.scroll, fg_color=self.CARD_BG, corner_radius=16,
                                  border_width=1, border_color=self.BORDER)
        table_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(table_card, text="📋 All Assigned Complaints", font=("Segoe UI", 16, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=20, pady=(15, 10))

        if not complaints:
            ctk.CTkLabel(table_card, text="No complaints currently assigned to this department.",
                         font=("Segoe UI", 12), text_color=self.TEXT_MUTED).pack(pady=25)
        else:
            for c in complaints[:6]:
                row = ctk.CTkFrame(table_card, fg_color=self.INPUT_BG, corner_radius=8)
                row.pack(fill="x", padx=20, pady=4)
                ctk.CTkLabel(row, text=f"#{c['id']}", font=("Segoe UI", 11, "bold"), text_color=self.ACCENT, padx=10, pady=8).pack(side="left")
                ctk.CTkLabel(row, text=c["title"], font=("Segoe UI", 12, "bold"), text_color=self.TEXT).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=c["priority"], font=("Segoe UI", 11, "bold"),
                             text_color=self.DANGER if c["priority"] == "High" else self.WARNING).pack(side="right", padx=15)
                ctk.CTkLabel(row, text=f"● {c['status']}", font=("Segoe UI", 11, "bold"), text_color=self.TEXT_DIM).pack(side="right", padx=10)
            ctk.CTkFrame(table_card, height=10, fg_color="transparent").pack()

    def _create_stat_card(self, parent, col, title, value, color, icon):
        card = ctk.CTkFrame(parent, fg_color=self.CARD_BG, corner_radius=14,
                            border_width=1, border_color=self.BORDER, height=100)
        card.grid(row=0, column=col, padx=6, sticky="ew")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 4))
        ctk.CTkLabel(top, text=icon, font=("Segoe UI Emoji", 18)).pack(side="left")
        ctk.CTkLabel(top, text=title, font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(side="left", padx=8)

        ctk.CTkLabel(card, text=value, font=("Segoe UI", 26, "bold"),
                     text_color=color).pack(anchor="w", padx=16, pady=(0, 14))
