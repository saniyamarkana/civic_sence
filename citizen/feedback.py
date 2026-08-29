"""
Citizen Feedback and Rating Module.
Allows citizens to provide feedback and star ratings on resolved complaints.
"""

import customtkinter as ctk


class FeedbackPage(ctk.CTkFrame):
    """Citizen Feedback and Rating page."""

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
        self.current_rating = 5
        self.selected_complaint_id = None
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(header, text="⭐ Service Feedback & Rating", font=("Segoe UI", 24, "bold"),
                     text_color=self.TEXT).pack(side="left")
        ctk.CTkLabel(header, text="Help municipal authorities improve resolution quality",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(side="left", padx=15, pady=(8, 0))

        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=10)

        # ── Form Card ──
        card = ctk.CTkFrame(content, fg_color=self.CARD_BG, corner_radius=16,
                            border_width=1, border_color=self.BORDER)
        card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card, text="Submit Feedback on Your Complaints", font=("Segoe UI", 16, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=25, pady=(18, 12))

        # Select complaint
        complaints = self.db.get_citizen_complaints(self.user["id"])
        options = [f"#{c['id']} - {c['title']} ({c['status']})" for c in complaints]
        if not options:
            options = ["No complaints filed yet"]

        ctk.CTkLabel(card, text="Select Complaint:", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", padx=25, pady=(5, 2))

        self.complaint_menu = ctk.CTkOptionMenu(
            card, values=options, height=40,
            fg_color=self.INPUT_BG, button_color=self.ACCENT, dropdown_fg_color=self.CARD_BG,
            text_color=self.TEXT
        )
        self.complaint_menu.pack(fill="x", padx=25, pady=(0, 15))

        # Star Rating Row
        ctk.CTkLabel(card, text="Satisfaction Rating:", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", padx=25, pady=(5, 5))

        stars_frame = ctk.CTkFrame(card, fg_color="transparent")
        stars_frame.pack(anchor="w", padx=25, pady=(0, 15))

        self.star_buttons = []
        for i in range(1, 6):
            btn = ctk.CTkButton(
                stars_frame, text="★", font=("Segoe UI", 24),
                fg_color="transparent", text_color="#fbbf24", hover_color=self.INPUT_BG,
                width=45, height=40, corner_radius=8,
                command=lambda r=i: self._set_rating(r)
            )
            btn.pack(side="left", padx=2)
            self.star_buttons.append(btn)

        self.rating_text = ctk.CTkLabel(stars_frame, text="5 / 5 - Excellent", font=("Segoe UI", 13, "bold"),
                                       text_color=self.ACCENT)
        self.rating_text.pack(side="left", padx=15)

        # Comments Textbox
        ctk.CTkLabel(card, text="Feedback Comments:", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", padx=25, pady=(5, 2))

        self.comment_box = ctk.CTkTextbox(card, height=90, fg_color=self.INPUT_BG,
                                          border_color=self.BORDER, border_width=1, text_color=self.TEXT)
        self.comment_box.pack(fill="x", padx=25, pady=(0, 12))

        self.msg_lbl = ctk.CTkLabel(card, text="", font=("Segoe UI", 12))
        self.msg_lbl.pack(padx=25, pady=(0, 5))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=25, pady=(0, 18))

        ctk.CTkButton(
            btn_row, text="Submit Feedback", font=("Segoe UI", 13, "bold"),
            fg_color=self.ACCENT, hover_color="#0891b2", text_color="#ffffff",
            height=40, corner_radius=8, command=self._submit_feedback
        ).pack(side="right")

        # ── Previous Feedback History Card ──
        hist_card = ctk.CTkFrame(content, fg_color=self.CARD_BG, corner_radius=16,
                                 border_width=1, border_color=self.BORDER)
        hist_card.pack(fill="x", pady=10)

        ctk.CTkLabel(hist_card, text="📜 My Previous Feedback", font=("Segoe UI", 16, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=25, pady=(18, 12))

        self.hist_container = ctk.CTkFrame(hist_card, fg_color="transparent")
        self.hist_container.pack(fill="x", padx=20, pady=(0, 20))

        self.load_feedback_history()

    def _set_rating(self, rating):
        self.current_rating = rating
        rating_labels = {
            1: "1 / 5 - Poor",
            2: "2 / 5 - Below Average",
            3: "3 / 5 - Average",
            4: "4 / 5 - Good",
            5: "5 / 5 - Excellent"
        }
        self.rating_text.configure(text=rating_labels.get(rating, f"{rating} / 5"))

        for i, btn in enumerate(self.star_buttons):
            if i < rating:
                btn.configure(text_color="#fbbf24")
            else:
                btn.configure(text_color=self.TEXT_MUTED)

    def _submit_feedback(self):
        selected_val = self.complaint_menu.get()
        if not selected_val.startswith("#"):
            self.msg_lbl.configure(text="⚠️ Please select a valid complaint.", text_color=self.DANGER)
            return

        cid = int(selected_val.split("-")[0].replace("#", "").strip())
        comments = self.comment_box.get("1.0", "end-1c").strip()

        fid = self.db.add_feedback(cid, self.user["id"], self.current_rating, comments)
        if fid:
            self.msg_lbl.configure(text="✓ Feedback submitted! Thank you for helping us improve.", text_color=self.SUCCESS)
            self.comment_box.delete("1.0", "end")
            self.load_feedback_history()
        else:
            self.msg_lbl.configure(text="⚠️ Failed to submit feedback.", text_color=self.DANGER)

    def load_feedback_history(self):
        for w in self.hist_container.winfo_children():
            w.destroy()

        feedbacks = self.db.get_citizen_feedback(self.user["id"])
        if not feedbacks:
            ctk.CTkLabel(self.hist_container, text="No feedback submitted yet.", font=("Segoe UI", 12),
                         text_color=self.TEXT_MUTED).pack(pady=15)
            return

        for f in feedbacks:
            row = ctk.CTkFrame(self.hist_container, fg_color=self.INPUT_BG, corner_radius=10)
            row.pack(fill="x", pady=5)

            top = ctk.CTkFrame(row, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(8, 2))

            stars = "★" * f["rating"] + "☆" * (5 - f["rating"])
            ctk.CTkLabel(top, text=stars, font=("Segoe UI", 14, "bold"), text_color="#fbbf24").pack(side="left")
            ctk.CTkLabel(top, text=f"Regarding: #{f['complaint_id']} {f['complaint_title']}",
                         font=("Segoe UI", 12, "bold"), text_color=self.TEXT).pack(side="left", padx=10)
            ctk.CTkLabel(top, text=f["created_at"], font=("Segoe UI", 10), text_color=self.TEXT_MUTED).pack(side="right")

            if f.get("comments"):
                ctk.CTkLabel(row, text=f'"{f["comments"]}"', font=("Segoe UI", 11, "italic"),
                             text_color=self.TEXT_DIM, wraplength=700, justify="left").pack(anchor="w", padx=12, pady=(0, 8))
