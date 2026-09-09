"""
Admin Complaint Management Module.
Allows administrators to view, filter, assign to departments, change priority, and update resolution statuses.
"""

# pyrefly: ignore [missing-import]
import customtkinter as ctk
from database import ActionStack, ComplaintBST


class ManageComplaintsPage(ctk.CTkFrame):
    """Admin Complaint Management Panel."""

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

    def __init__(self, parent, db, user):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.user = user
        self.status_filter = ctk.StringVar(value="All")
        
        # ── Real DSA Structures (Phase 1 & Phase 2) ──
        self.undo_stack = ActionStack(max_size=30)  # Phase 1: LIFO Undo Stack
        self.complaint_bst = None                   # Phase 2: Binary Search Tree for O(log n) lookups
        
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="🛡️ Manage All Complaints", font=("Segoe UI", 24, "bold"),
                     text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text="Assign municipal departments, alter priority, approve, or resolve complaints",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(anchor="w")

        # Controls Row
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=30, pady=(10, 15))

        self.search_entry = ctk.CTkEntry(
            ctrl, placeholder_text="🔍 Search by ID (BST O(log n)), keyword, category...",
            height=38, width=320, fg_color=self.CARD_BG, border_color=self.BORDER, text_color=self.TEXT
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_complaints())

        self.status_menu = ctk.CTkOptionMenu(
            ctrl, values=["All", "Pending", "Approved", "In Progress", "Resolved", "Rejected"],
            variable=self.status_filter, height=38, width=130,
            fg_color=self.CARD_BG, button_color=self.ACCENT, text_color=self.TEXT,
            dropdown_fg_color=self.CARD_BG, command=lambda v: self.load_complaints()
        )
        self.status_menu.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            ctrl, text="🔄 Refresh", font=("Segoe UI", 12, "bold"),
            fg_color=self.INPUT_BG, hover_color="#334155", text_color=self.TEXT,
            height=38, width=80, corner_radius=8, command=self.load_complaints
        ).pack(side="left", padx=(0, 8))

        # Phase 1: Operational LIFO Undo Button
        self.undo_btn = ctk.CTkButton(
            ctrl, text="↩️ Undo (Stack: 0)", font=("Segoe UI", 11, "bold"),
            fg_color="#475569", hover_color="#334155", text_color="#ffffff",
            height=38, width=130, corner_radius=8, command=self._undo_last_action
        )
        self.undo_btn.pack(side="left", padx=(0, 8))

        # Phase 2: BST Indicator Badge
        self.bst_badge = ctk.CTkLabel(
            ctrl, text="🌳 BST Index: Active", font=("Segoe UI", 11, "bold"),
            text_color=self.ACCENT, fg_color=self.INPUT_BG, corner_radius=8, padx=10, pady=6
        )
        self.bst_badge.pack(side="right")

        # Table Card
        table_card = ctk.CTkFrame(self, fg_color=self.CARD_BG, corner_radius=16,
                                  border_width=1, border_color=self.BORDER)
        table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Table Header
        th = ctk.CTkFrame(table_card, fg_color=self.INPUT_BG, height=38, corner_radius=8)
        th.pack(fill="x", padx=15, pady=(15, 8))
        th.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        cols = [("ID", 0), ("Title / Issue", 1), ("Category", 2), ("Location", 3),
                ("Priority", 4), ("Department", 5), ("Status & Action", 6)]
        for name, cidx in cols:
            ctk.CTkLabel(th, text=name, font=("Segoe UI", 11, "bold"), text_color=self.TEXT_DIM).grid(row=0, column=cidx, sticky="w", padx=10, pady=8)

        # Scrollable Rows
        self.rows_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.rows_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.load_complaints()

    def _iterative_insertion_sort(self, items, key="id", reverse=True):
        """Phase 1: Iterative Insertion Sort algorithm to arrange complaints table."""
        arr = list(items)
        for i in range(1, len(arr)):
            key_item = arr[i]
            j = i - 1
            while j >= 0 and ((arr[j].get(key, 0) < key_item.get(key, 0)) if reverse else (arr[j].get(key, 0) > key_item.get(key, 0))):
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key_item
        return arr

    def load_complaints(self):
        for w in self.rows_scroll.winfo_children():
            w.destroy()

        filt = self.status_filter.get()
        # Build live Phase 2 Binary Search Tree of complaints
        self.complaint_bst = self.db.get_complaints_bst(status=None if filt == "All" else filt)
        self.bst_badge.configure(text=f"🌳 BST Index: {self.complaint_bst.size()} Nodes (O(log n))")

        query = self.search_entry.get().strip().lower()

        # Phase 2: If searching numeric ID, use Binary Search Tree O(log n) lookup
        if query.isdigit() or (query.startswith("#") and query[1:].isdigit()):
            cid = int(query.replace("#", ""))
            bst_result = self.complaint_bst.search(cid)
            filtered = [bst_result] if bst_result else []
        else:
            complaints = self.db.get_all_complaints(status=None if filt == "All" else filt)
            filtered = []
            for c in complaints:
                if query:
                    txt = f"{c['id']} {c['title']} {c['category']} {c.get('location','')} {c['priority']} {c.get('department','')}".lower()
                    if query not in txt:
                        continue
                filtered.append(c)

        # Phase 1: Sort complaints using Iterative Insertion Sort
        filtered = self._iterative_insertion_sort(filtered, key="id", reverse=True)


        if not filtered:
            ctk.CTkLabel(self.rows_scroll, text="No complaints found matching criteria.",
                         font=("Segoe UI", 13), text_color=self.TEXT_MUTED).pack(pady=40)
            return

        for c in filtered:
            row = ctk.CTkFrame(self.rows_scroll, fg_color=self.INPUT_BG, corner_radius=8)
            row.pack(fill="x", pady=4)
            row.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

            # ID
            ctk.CTkLabel(row, text=f"#{c['id']}", font=("Segoe UI", 12, "bold"),
                         text_color=self.ACCENT).grid(row=0, column=0, sticky="w", padx=10, pady=10)

            # Title
            ctk.CTkLabel(row, text=c["title"][:22] + ("..." if len(c["title"]) > 22 else ""),
                         font=("Segoe UI", 12, "bold"), text_color=self.TEXT).grid(row=0, column=1, sticky="w", padx=10)

            # Category
            ctk.CTkLabel(row, text=c["category"], font=("Segoe UI", 12),
                         text_color=self.TEXT_DIM).grid(row=0, column=2, sticky="w", padx=10)

            # Location
            ctk.CTkLabel(row, text=c["location"] or "-", font=("Segoe UI", 11),
                         text_color=self.TEXT_DIM).grid(row=0, column=3, sticky="w", padx=10)

            # Priority
            pr_col = self.PRIORITY_COLORS.get(c["priority"], self.TEXT)
            ctk.CTkLabel(row, text=c["priority"], font=("Segoe UI", 11, "bold"),
                         text_color=pr_col).grid(row=0, column=4, sticky="w", padx=10)

            # Department
            dept_txt = c["department"] or "Unassigned"
            dept_col = self.ACCENT if c["department"] else self.TEXT_MUTED
            ctk.CTkLabel(row, text=dept_txt, font=("Segoe UI", 11),
                         text_color=dept_col).grid(row=0, column=5, sticky="w", padx=10)

            # Action / Manage Button
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.grid(row=0, column=6, sticky="w", padx=10)

            st_col = self.STATUS_COLORS.get(c["status"], self.TEXT_MUTED)
            ctk.CTkLabel(act, text=c["status"], font=("Segoe UI", 11, "bold"), text_color=st_col).pack(side="left", padx=(0, 8))

            ctk.CTkButton(
                act, text="⚙️ Manage", font=("Segoe UI", 10, "bold"),
                fg_color=self.ACCENT, hover_color="#0891b2", text_color="#ffffff",
                height=26, width=68, corner_radius=6,
                command=lambda comp=c: self._show_manage_modal(comp)
            ).pack(side="left")

    def _show_manage_modal(self, complaint):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Manage Complaint #{complaint['id']}")
        modal.geometry("520x580")
        modal.configure(fg_color=self.BG_DARK)
        modal.grab_set()

        top = ctk.CTkFrame(modal, fg_color=self.CARD_BG, corner_radius=0)
        top.pack(fill="x")
        ctk.CTkLabel(top, text=f"Manage Complaint #{complaint['id']}", font=("Segoe UI", 16, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=20, pady=15)

        scroll = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Basic Info Card
        info = ctk.CTkFrame(scroll, fg_color=self.CARD_BG, corner_radius=10, border_width=1, border_color=self.BORDER)
        info.pack(fill="x", pady=5)
        ctk.CTkLabel(info, text=f"Title: {complaint['title']}", font=("Segoe UI", 13, "bold"),
                     text_color=self.TEXT, wraplength=440, justify="left").pack(anchor="w", padx=15, pady=(10, 4))
        ctk.CTkLabel(info, text=f"Category: {complaint['category']} | Location: {complaint['location']}",
                     font=("Segoe UI", 11), text_color=self.TEXT_DIM).pack(anchor="w", padx=15, pady=(0, 10))

        # Status Option
        ctk.CTkLabel(scroll, text="Update Status:", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(10, 2))
        status_var = ctk.StringVar(value=complaint["status"])
        status_menu = ctk.CTkOptionMenu(
            scroll, values=["Pending", "Approved", "In Progress", "Resolved", "Rejected"],
            variable=status_var, height=38, fg_color=self.INPUT_BG, button_color=self.ACCENT, text_color=self.TEXT
        )
        status_menu.pack(fill="x", pady=(0, 10))

        # Priority Option
        ctk.CTkLabel(scroll, text="Change Priority:", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(5, 2))
        priority_var = ctk.StringVar(value=complaint["priority"])
        priority_menu = ctk.CTkOptionMenu(
            scroll, values=["Low", "Medium", "High"],
            variable=priority_var, height=38, fg_color=self.INPUT_BG, button_color=self.ACCENT, text_color=self.TEXT
        )
        priority_menu.pack(fill="x", pady=(0, 10))

        # Assign Department
        ctk.CTkLabel(scroll, text="Assign Department:", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(5, 2))
        depts = [d["name"] for d in self.db.get_all_departments()]
        dept_options = ["None"] + depts
        current_dept = complaint["department"] if complaint["department"] in dept_options else "None"
        dept_var = ctk.StringVar(value=current_dept)
        dept_menu = ctk.CTkOptionMenu(
            scroll, values=dept_options,
            variable=dept_var, height=38, fg_color=self.INPUT_BG, button_color=self.ACCENT, text_color=self.TEXT
        )
        dept_menu.pack(fill="x", pady=(0, 10))

        # Admin Remarks
        ctk.CTkLabel(scroll, text="Municipal Remarks / Notes:", font=("Segoe UI", 12, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(5, 2))
        remarks_box = ctk.CTkTextbox(scroll, height=80, fg_color=self.INPUT_BG,
                                     border_color=self.BORDER, border_width=1, text_color=self.TEXT)
        if complaint.get("admin_remarks"):
            remarks_box.insert("1.0", complaint["admin_remarks"])
        remarks_box.pack(fill="x", pady=(0, 10))

        def save_changes():
            st = status_var.get()
            pr = priority_var.get()
            dp = dept_var.get()
            if dp == "None":
                dp = ""
            rem = remarks_box.get("1.0", "end-1c").strip()

            # Phase 1: Push previous state to LIFO ActionStack before applying change
            self.undo_stack.push({
                "id": complaint["id"],
                "old_status": complaint["status"],
                "old_priority": complaint["priority"],
                "old_department": complaint.get("department", ""),
                "old_admin_remarks": complaint.get("admin_remarks", "")
            })
            self.undo_btn.configure(
                text=f"↩️ Undo (Stack: {self.undo_stack.size()})",
                fg_color=self.WARNING,
                text_color="#000000"
            )

            self.db.update_complaint(
                complaint["id"],
                changed_by=self.user["id"],
                status=st,
                priority=pr,
                department=dp,
                admin_remarks=rem,
                remarks=f"Status set to {st}. Dept: {dp or 'None'}. Priority: {pr}."
            )
            modal.destroy()
            self.load_complaints()

        ctk.CTkButton(
            modal, text="💾 Save Changes", font=("Segoe UI", 13, "bold"),
            fg_color=self.ACCENT, hover_color="#0891b2", text_color="#ffffff",
            height=42, corner_radius=8, command=save_changes
        ).pack(fill="x", padx=20, pady=(10, 15))

    def _undo_last_action(self):
        """Phase 1: LIFO Stack Undo Operation to revert the most recent complaint change."""
        if self.undo_stack.is_empty():
            return
        last_action = self.undo_stack.pop()
        if last_action:
            self.db.update_complaint(
                last_action["id"],
                changed_by=self.user["id"],
                status=last_action["old_status"],
                priority=last_action["old_priority"],
                department=last_action["old_department"],
                admin_remarks=last_action["old_admin_remarks"],
                remarks=f"[LIFO UNDO] Reverted #{last_action['id']} back to {last_action['old_status']}."
            )
            stack_len = self.undo_stack.size()
            btn_color = self.WARNING if stack_len > 0 else "#475569"
            txt_color = "#000000" if stack_len > 0 else "#ffffff"
            self.undo_btn.configure(text=f"↩️ Undo (Stack: {stack_len})", fg_color=btn_color, text_color=txt_color)
            self.load_complaints()

