"""
Department Status Update Form.
Enables officers to log work updates, add field remarks, and transition complaints through resolution phases.
"""

# pyrefly: ignore [missing-import]
import customtkinter as ctk
from database import ActionStack


class UpdateStatusPage(ctk.CTkFrame):
    """Department status and resolution updater form."""

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
        self.undo_stack = ActionStack(max_size=20)  # Phase 1: Operational LIFO Undo Stack
        self._build_ui()


    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="⚙️ Work Progress & Status Updater", font=("Segoe UI", 24, "bold"),
                     text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text="Record operational updates, field progress, and completion notes",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(anchor="w")

        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=10)

        # ── Form Card ──
        card = ctk.CTkFrame(content, fg_color=self.CARD_BG, corner_radius=16,
                            border_width=1, border_color=self.BORDER)
        card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card, text="Update Complaint Record", font=("Segoe UI", 16, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=25, pady=(18, 12))

        # Select assigned complaint
        complaints = self.db.get_department_complaints(self.department_name)
        options = [f"#{c['id']} - {c['title']} ({c['status']})" for c in complaints]
        if not options:
            options = ["No complaints currently assigned"]

        ctk.CTkLabel(card, text="Select Complaint:", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", padx=25, pady=(5, 2))

        self.complaint_menu = ctk.CTkOptionMenu(
            card, values=options, height=40,
            fg_color=self.INPUT_BG, button_color=self.ACCENT, dropdown_fg_color=self.CARD_BG,
            text_color=self.TEXT
        )
        self.complaint_menu.pack(fill="x", padx=25, pady=(0, 15))

        # New Status Menu
        ctk.CTkLabel(card, text="Target Resolution Status:", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", padx=25, pady=(5, 2))

        self.status_var = ctk.StringVar(value="In Progress")
        self.status_menu = ctk.CTkOptionMenu(
            card, values=["In Progress", "Resolved", "Pending"],
            variable=self.status_var, height=40,
            fg_color=self.INPUT_BG, button_color=self.ACCENT2, dropdown_fg_color=self.CARD_BG,
            text_color=self.TEXT
        )
        self.status_menu.pack(fill="x", padx=25, pady=(0, 15))

        # Work Remarks
        ctk.CTkLabel(card, text="Work Progress & Field Remarks:", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", padx=25, pady=(5, 2))

        self.remarks_box = ctk.CTkTextbox(card, height=100, fg_color=self.INPUT_BG,
                                          border_color=self.BORDER, border_width=1, text_color=self.TEXT)
        self.remarks_box.pack(fill="x", padx=25, pady=(0, 12))

        self.msg_lbl = ctk.CTkLabel(card, text="", font=("Segoe UI", 12))
        self.msg_lbl.pack(padx=25, pady=(0, 5))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=25, pady=(0, 20))

        self.undo_btn = ctk.CTkButton(
            btn_row, text="↩️ Undo Status (Stack: 0)", font=("Segoe UI", 12, "bold"),
            fg_color="#475569", hover_color="#334155", text_color="#ffffff",
            height=42, corner_radius=8, command=self._undo_last_status
        )
        self.undo_btn.pack(side="left")

        ctk.CTkButton(
            btn_row, text="💾 Save Status Update", font=("Segoe UI", 13, "bold"),
            fg_color=self.ACCENT, hover_color="#0891b2", text_color="#ffffff",
            height=42, corner_radius=8, command=self._save_update
        ).pack(side="right")

    def _save_update(self):
        val = self.complaint_menu.get()
        if not val.startswith("#"):
            self.msg_lbl.configure(text="⚠️ Please select an assigned complaint.", text_color=self.DANGER)
            return

        cid = int(val.split("-")[0].replace("#", "").strip())
        new_status = self.status_var.get()
        remarks = self.remarks_box.get("1.0", "end-1c").strip()

        # Phase 1: Push previous state to LIFO ActionStack before changing
        old_comp = self.db.get_complaint(cid)
        if old_comp:
            self.undo_stack.push({
                "id": cid,
                "old_status": old_comp.get("status", "Pending"),
                "old_remarks": old_comp.get("admin_remarks", "")
            })
            self.undo_btn.configure(
                text=f"↩️ Undo Status (Stack: {self.undo_stack.size()})",
                fg_color=self.WARNING,
                text_color="#000000"
            )

        success = self.db.update_complaint(
            cid, changed_by=self.user["id"], status=new_status,
            admin_remarks=remarks,
            remarks=f"[{self.department_name}] Updated status to '{new_status}': {remarks}"
        )

        if success:
            self.msg_lbl.configure(text=f"✓ Complaint #{cid} updated to '{new_status}'!", text_color=self.SUCCESS)
            self.remarks_box.delete("1.0", "end")
        else:
            self.msg_lbl.configure(text="⚠️ Failed to update complaint status.", text_color=self.DANGER)

    def _undo_last_status(self):
        """Phase 1: LIFO Stack Undo mechanism to revert status update."""
        if self.undo_stack.is_empty():
            return
        last = self.undo_stack.pop()
        if last:
            self.db.update_complaint(
                last["id"],
                changed_by=self.user["id"],
                status=last["old_status"],
                admin_remarks=last["old_remarks"],
                remarks=f"[LIFO UNDO] Reverted status back to '{last['old_status']}'"
            )
            count = self.undo_stack.size()
            btn_bg = self.WARNING if count > 0 else "#475569"
            btn_fg = "#000000" if count > 0 else "#ffffff"
            self.undo_btn.configure(text=f"↩️ Undo Status (Stack: {count})", fg_color=btn_bg, text_color=btn_fg)
            self.msg_lbl.configure(text=f"↩️ Reverted Complaint #{last['id']} back to '{last['old_status']}'!", text_color=self.WARNING)

