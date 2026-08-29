"""
Citizen Complaints List & Tracking Page.
Features complaint cards, status badges, timeline tracking, and live search/filter.
"""

import customtkinter as ctk


class MyComplaintsPage(ctk.CTkFrame):
    """View and track citizen's filed complaints."""

    BG_DARK = "#0a0e1a"
    CARD_BG = "#111827"
    CARD_HOVER = "#1a2332"
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

    def __init__(self, parent, db, user):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.user = user
        self.status_filter = ctk.StringVar(value="All")
        self._build_ui()

    def _build_ui(self):
        # Header + Filters
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="📋 My Complaints", font=("Segoe UI", 24, "bold"),
                     text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text="Track status, history, and municipal responses",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(anchor="w")

        # Controls Row (Search + Filter)
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=30, pady=(10, 15))

        self.search_entry = ctk.CTkEntry(
            ctrl_frame, placeholder_text="🔍 Search complaints by title, category, location or ID...",
            height=38, width=360, fg_color=self.CARD_BG, border_color=self.BORDER, text_color=self.TEXT
        )
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_complaints())

        self.filter_menu = ctk.CTkOptionMenu(
            ctrl_frame, values=["All", "Pending", "Approved", "In Progress", "Resolved", "Rejected"],
            variable=self.status_filter, height=38, width=140,
            fg_color=self.CARD_BG, button_color=self.ACCENT, text_color=self.TEXT,
            dropdown_fg_color=self.CARD_BG, command=lambda v: self.load_complaints()
        )
        self.filter_menu.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            ctrl_frame, text="🔄 Refresh", font=("Segoe UI", 12, "bold"),
            fg_color=self.INPUT_BG, hover_color="#334155", text_color=self.TEXT,
            height=38, width=100, corner_radius=8, command=self.load_complaints
        ).pack(side="left")

        # Scrollable Cards Container
        self.cards_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.cards_scroll.pack(fill="both", expand=True, padx=30, pady=(0, 15))

        self.load_complaints()

    def load_complaints(self):
        # Clear existing cards
        for w in self.cards_scroll.winfo_children():
            w.destroy()

        complaints = self.db.get_citizen_complaints(self.user["id"])
        query = self.search_entry.get().strip().lower()
        filt = self.status_filter.get()

        filtered = []
        for c in complaints:
            if filt != "All" and c["status"] != filt:
                continue
            if query:
                txt = f"{c['id']} {c['title']} {c['category']} {c['location']} {c['description']} {c['status']}".lower()
                if query not in txt:
                    continue
            filtered.append(c)

        if not filtered:
            empty = ctk.CTkFrame(self.cards_scroll, fg_color=self.CARD_BG, corner_radius=16,
                                 border_width=1, border_color=self.BORDER)
            empty.pack(fill="x", pady=40, padx=20)
            ctk.CTkLabel(empty, text="📭", font=("Segoe UI Emoji", 48)).pack(pady=(30, 10))
            ctk.CTkLabel(empty, text="No complaints found", font=("Segoe UI", 18, "bold"),
                         text_color=self.TEXT).pack()
            ctk.CTkLabel(empty, text="Submit a new complaint or adjust search filters.",
                         font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(pady=(5, 30))
            return

        for c in filtered:
            self._render_complaint_card(c)

    def _render_complaint_card(self, c):
        card = ctk.CTkFrame(self.cards_scroll, fg_color=self.CARD_BG, corner_radius=14,
                            border_width=1, border_color=self.BORDER)
        card.pack(fill="x", pady=8)

        # Header of Card (ID + Title + Badges)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(15, 8))

        id_lbl = ctk.CTkLabel(
            top, text=f"#{c['id']}", font=("Segoe UI", 12, "bold"),
            fg_color=self.INPUT_BG, text_color=self.ACCENT,
            corner_radius=6, padx=8, pady=2
        )
        id_lbl.pack(side="left")

        title_lbl = ctk.CTkLabel(
            top, text=c["title"], font=("Segoe UI", 15, "bold"),
            text_color=self.TEXT, anchor="w"
        )
        title_lbl.pack(side="left", padx=12)

        # Status badge
        st_color = self.STATUS_COLORS.get(c["status"], self.TEXT_MUTED)
        st_badge = ctk.CTkLabel(
            top, text=f"● {c['status']}", font=("Segoe UI", 11, "bold"),
            text_color=st_color, fg_color=self.INPUT_BG,
            corner_radius=6, padx=10, pady=3
        )
        st_badge.pack(side="right")

        # Priority badge
        pr_color = self.PRIORITY_COLORS.get(c["priority"], self.TEXT_MUTED)
        pr_badge = ctk.CTkLabel(
            top, text=f"{c['priority']} Priority", font=("Segoe UI", 11, "bold"),
            text_color=pr_color, fg_color=self.INPUT_BG,
            corner_radius=6, padx=8, pady=3
        )
        pr_badge.pack(side="right", padx=8)

        # Body info
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=(0, 10))

        info_text = f"📂 Category: {c['category']}   |   📍 Location: {c['location']}   |   📅 Filed: {c['created_at']}"
        if c.get("department"):
            info_text += f"   |   🏢 Assigned: {c['department']}"
        ctk.CTkLabel(body, text=info_text, font=("Segoe UI", 11), text_color=self.TEXT_DIM).pack(anchor="w")

        if c.get("description"):
            ctk.CTkLabel(
                body, text=c["description"], font=("Segoe UI", 12),
                text_color=self.TEXT, wraplength=750, justify="left"
            ).pack(anchor="w", pady=(6, 4))

        if c.get("admin_remarks"):
            rem_frame = ctk.CTkFrame(body, fg_color=self.INPUT_BG, corner_radius=8)
            rem_frame.pack(fill="x", pady=(6, 2))
            ctk.CTkLabel(
                rem_frame, text=f"💬 Municipal Remarks: {c['admin_remarks']}",
                font=("Segoe UI", 11, "italic"), text_color=self.ACCENT, padx=10, pady=6
            ).pack(anchor="w")

        # Footer Actions
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(4, 12))

        ctk.CTkButton(
            footer, text="📜 View Timeline / History", font=("Segoe UI", 11, "bold"),
            fg_color="transparent", text_color=self.ACCENT, hover_color=self.INPUT_BG,
            height=28, width=160, corner_radius=6,
            command=lambda cid=c["id"]: self._show_history_modal(cid)
        ).pack(side="left")

    def _show_history_modal(self, cid):
        history = self.db.get_complaint_history(cid)
        complaint = self.db.get_complaint(cid)

        modal = ctk.CTkToplevel(self)
        modal.title(f"Complaint #{cid} Tracking Timeline")
        modal.geometry("540x480")
        modal.configure(fg_color=self.BG_DARK)
        modal.grab_set()

        # Modal Header
        top = ctk.CTkFrame(modal, fg_color=self.CARD_BG, corner_radius=0)
        top.pack(fill="x", padx=0, pady=0)
        ctk.CTkLabel(
            top, text=f"Timeline for Complaint #{cid}", font=("Segoe UI", 16, "bold"),
            text_color=self.TEXT
        ).pack(side="left", padx=20, pady=15)

        if complaint:
            ctk.CTkLabel(
                modal, text=f"Issue: {complaint['title']}", font=("Segoe UI", 13, "bold"),
                text_color=self.ACCENT
            ).pack(anchor="w", padx=20, pady=(15, 5))

        # Timeline entries
        scroll = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        if not history:
            ctk.CTkLabel(scroll, text="No recorded history events.", text_color=self.TEXT_MUTED).pack(pady=30)
        else:
            for item in history:
                entry = ctk.CTkFrame(scroll, fg_color=self.CARD_BG, corner_radius=10,
                                     border_width=1, border_color=self.BORDER)
                entry.pack(fill="x", pady=5)

                header_row = ctk.CTkFrame(entry, fg_color="transparent")
                header_row.pack(fill="x", padx=12, pady=(8, 2))

                st_col = self.STATUS_COLORS.get(item["new_status"], self.TEXT)
                ctk.CTkLabel(
                    header_row, text=f"● {item['new_status']}", font=("Segoe UI", 12, "bold"),
                    text_color=st_col
                ).pack(side="left")

                ctk.CTkLabel(
                    header_row, text=item["changed_at"], font=("Segoe UI", 10),
                    text_color=self.TEXT_MUTED
                ).pack(side="right")

                if item.get("remarks"):
                    ctk.CTkLabel(
                        entry, text=item["remarks"], font=("Segoe UI", 11),
                        text_color=self.TEXT_DIM, wraplength=460, justify="left"
                    ).pack(anchor="w", padx=12, pady=(0, 8))

        ctk.CTkButton(
            modal, text="Close", font=("Segoe UI", 12, "bold"),
            fg_color=self.INPUT_BG, hover_color="#334155", text_color=self.TEXT,
            height=36, corner_radius=8, command=modal.destroy
        ).pack(padx=20, pady=(5, 15))
