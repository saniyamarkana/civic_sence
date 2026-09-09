"""
Citizen Profile View and Edit Page.
"""

# pyrefly: ignore [missing-import]
import customtkinter as ctk


class ProfilePage(ctk.CTkFrame):
    """Citizen Profile view and edit form."""

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

    def __init__(self, parent, db, user, on_update_user=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.user = user
        self.on_update_user = on_update_user
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 15))
        ctk.CTkLabel(header, text="👤 My Profile", font=("Segoe UI", 24, "bold"),
                     text_color=self.TEXT).pack(side="left")

        # Main scrollable or grid container
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=10)

        # Overview / Stats Cards Row
        stats_frame = ctk.CTkFrame(content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        complaints = self.db.get_citizen_complaints(self.user["id"])
        total_c = len(complaints)
        pending_c = sum(1 for c in complaints if c["status"] == "Pending")
        resolved_c = sum(1 for c in complaints if c["status"] == "Resolved")

        self._create_stat_card(stats_frame, 0, "Total Complaints", str(total_c), self.ACCENT, "📋")
        self._create_stat_card(stats_frame, 1, "Pending Issues", str(pending_c), self.WARNING, "⏳")
        self._create_stat_card(stats_frame, 2, "Resolved Issues", str(resolved_c), self.SUCCESS, "✅")

        # Edit Profile Card
        card = ctk.CTkFrame(content, fg_color=self.CARD_BG, corner_radius=16,
                            border_width=1, border_color=self.BORDER)
        card.pack(fill="x", pady=10)

        ctk.CTkLabel(card, text="Account Details", font=("Segoe UI", 18, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=25, pady=(20, 15))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=25, pady=(0, 20))
        form.grid_columnconfigure((0, 1), weight=1)

        # Full Name
        ctk.CTkLabel(form, text="Full Name", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 2))
        self.name_entry = ctk.CTkEntry(form, height=40, fg_color=self.INPUT_BG,
                                       border_color=self.BORDER, text_color=self.TEXT)
        self.name_entry.insert(0, self.user.get("name", ""))
        self.name_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 12))

        # Email (read-only)
        ctk.CTkLabel(form, text="Email Address (ID)", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).grid(row=0, column=1, sticky="w", padx=10, pady=(5, 2))
        self.email_entry = ctk.CTkEntry(form, height=40, fg_color=self.INPUT_BG,
                                        border_color=self.BORDER, text_color=self.TEXT_MUTED)
        self.email_entry.insert(0, self.user.get("email", ""))
        self.email_entry.configure(state="disabled")
        self.email_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 12))

        # Phone
        ctk.CTkLabel(form, text="Phone Number", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).grid(row=2, column=0, sticky="w", padx=10, pady=(5, 2))
        self.phone_entry = ctk.CTkEntry(form, height=40, fg_color=self.INPUT_BG,
                                        border_color=self.BORDER, text_color=self.TEXT)
        self.phone_entry.insert(0, self.user.get("phone", "") or "")
        self.phone_entry.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 12))

        # Address
        ctk.CTkLabel(form, text="Residential Address / Ward", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).grid(row=2, column=1, sticky="w", padx=10, pady=(5, 2))
        self.address_entry = ctk.CTkEntry(form, height=40, fg_color=self.INPUT_BG,
                                          border_color=self.BORDER, text_color=self.TEXT)
        self.address_entry.insert(0, self.user.get("address", "") or "")
        self.address_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=(0, 12))

        # Status & Msg
        self.msg_label = ctk.CTkLabel(card, text="", font=("Segoe UI", 12))
        self.msg_label.pack(padx=25, pady=(0, 5))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(anchor="e", padx=25, pady=(0, 20))

        ctk.CTkButton(btn_row, text="💾 Save Changes", font=("Segoe UI", 13, "bold"),
                      fg_color=self.ACCENT, hover_color="#0891b2", text_color="#ffffff",
                      height=40, width=150, corner_radius=8,
                      command=self._save_profile).pack(side="right")

        # Security Card (Change Password)
        sec_card = ctk.CTkFrame(content, fg_color=self.CARD_BG, corner_radius=16,
                                border_width=1, border_color=self.BORDER)
        sec_card.pack(fill="x", pady=10)

        ctk.CTkLabel(sec_card, text="🔒 Change Password", font=("Segoe UI", 18, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=25, pady=(20, 15))

        sec_form = ctk.CTkFrame(sec_card, fg_color="transparent")
        sec_form.pack(fill="x", padx=25, pady=(0, 20))
        sec_form.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(sec_form, text="New Password", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 2))
        self.new_pass_entry = ctk.CTkEntry(sec_form, height=40, show="•", fg_color=self.INPUT_BG,
                                           border_color=self.BORDER, text_color=self.TEXT)
        self.new_pass_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 12))

        ctk.CTkLabel(sec_form, text="Confirm New Password", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).grid(row=0, column=1, sticky="w", padx=10, pady=(5, 2))
        self.conf_pass_entry = ctk.CTkEntry(sec_form, height=40, show="•", fg_color=self.INPUT_BG,
                                            border_color=self.BORDER, text_color=self.TEXT)
        self.conf_pass_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 12))

        self.pass_msg_label = ctk.CTkLabel(sec_card, text="", font=("Segoe UI", 12))
        self.pass_msg_label.pack(padx=25, pady=(0, 5))

        sec_btn_row = ctk.CTkFrame(sec_card, fg_color="transparent")
        sec_btn_row.pack(anchor="e", padx=25, pady=(0, 20))

        ctk.CTkButton(sec_btn_row, text="Update Password", font=("Segoe UI", 13, "bold"),
                      fg_color=self.ACCENT2, hover_color="#2563eb", text_color="#ffffff",
                      height=40, width=160, corner_radius=8,
                      command=self._change_password).pack(side="right")

    def _create_stat_card(self, parent, col, title, value, color, icon):
        card = ctk.CTkFrame(parent, fg_color=self.CARD_BG, corner_radius=14,
                            border_width=1, border_color=self.BORDER, height=100)
        card.grid(row=0, column=col, padx=8, sticky="ew")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 4))
        ctk.CTkLabel(top, text=icon, font=("Segoe UI Emoji", 20)).pack(side="left")
        ctk.CTkLabel(top, text=title, font=("Segoe UI", 13), text_color=self.TEXT_DIM).pack(side="left", padx=8)

        ctk.CTkLabel(card, text=value, font=("Segoe UI", 26, "bold"),
                     text_color=color).pack(anchor="w", padx=18, pady=(0, 14))

    def _save_profile(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            self.msg_label.configure(text="⚠️ Name cannot be empty.", text_color=self.DANGER)
            return

        success = self.db.update_user(self.user["id"], name=name, phone=phone, address=address)
        if success:
            self.user["name"] = name
            self.user["phone"] = phone
            self.user["address"] = address
            if self.on_update_user:
                self.on_update_user(self.user)
            self.msg_label.configure(text="✓ Profile updated successfully!", text_color=self.SUCCESS)
        else:
            self.msg_label.configure(text="⚠️ Failed to update profile.", text_color=self.DANGER)

    def _change_password(self):
        new_p = self.new_pass_entry.get().strip()
        conf_p = self.conf_pass_entry.get().strip()

        if not new_p or not conf_p:
            self.pass_msg_label.configure(text="⚠️ Please fill both password fields.", text_color=self.DANGER)
            return
        if new_p != conf_p:
            self.pass_msg_label.configure(text="⚠️ Passwords do not match.", text_color=self.DANGER)
            return
        if len(new_p) < 4:
            self.pass_msg_label.configure(text="⚠️ Password must be at least 4 chars.", text_color=self.DANGER)
            return

        self.db.update_password(self.user["id"], new_p)
        self.new_pass_entry.delete(0, "end")
        self.conf_pass_entry.delete(0, "end")
        self.pass_msg_label.configure(text="✓ Password changed successfully!", text_color=self.SUCCESS)
