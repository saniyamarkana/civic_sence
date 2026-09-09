"""
Ultra-Modern Citizen Complaint Submission Wizard.
Features 8 category visual cards, priority selector, live preview card, and step indicators.
"""

# pyrefly: ignore [missing-import]
import customtkinter as ctk
from database import (
    ComplaintLinkedList,
    ActionStack,
    ComplaintQueue,
    EmergencyPriorityQueue,
    MunicipalWardGraph
)


class SubmitComplaintPage(ctk.CTkFrame):
    """Step-by-step Complaint Reporting Wizard."""

    BG_DARK = "#070b14"
    CARD_BG = "#0f172a"
    CARD_BORDER = "#1e293b"
    ACCENT = "#06b6d4"
    ACCENT_HOVER = "#0891b2"
    ACCENT_BLUE = "#3b82f6"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    TEXT = "#f8fafc"
    TEXT_DIM = "#94a3b8"
    TEXT_MUTED = "#64748b"
    INPUT_BG = "#131f37"
    INPUT_BORDER = "#223254"

    CATEGORY_METADATA = {
        "Garbage": {"icon": "🗑️", "desc": "Waste overflow & dumping", "dept": "Sanitation Dept"},
        "Pothole": {"icon": "🕳️", "desc": "Road pits & cracks", "dept": "Road Dept"},
        "Water Leakage": {"icon": "💧", "desc": "Broken pipes & floods", "dept": "Water Dept"},
        "Streetlight": {"icon": "💡", "desc": "Dark or broken lamps", "dept": "Electricity Dept"},
        "Drainage": {"icon": "🌊", "desc": "Sewage & blockage", "dept": "Water Dept"},
        "Illegal Parking": {"icon": "🚗", "desc": "Blocked streets & driveways", "dept": "Traffic Dept"},
        "Public Cleanliness": {"icon": "🧹", "desc": "Sanitation & parks", "dept": "Sanitation Dept"},
        "Damaged Road": {"icon": "🚧", "desc": "Surface destruction", "dept": "Road Dept"}
    }

    def __init__(self, parent, db, user, on_complaint_submitted=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.user = user
        self.on_complaint_submitted = on_complaint_submitted
        
        self.selected_category = ctk.StringVar(value="Garbage")
        self.selected_priority = ctk.StringVar(value="Medium")

        # ── Real Project DSA In-Memory Structures (Phase 1 & Phase 2) ──
        self.live_queue = ComplaintQueue()               # Phase 1: FIFO Queue
        self.priority_queue = EmergencyPriorityQueue()   # Phase 1: Emergency Priority Queue
        self.live_stack = ActionStack(max_size=30)       # Phase 1: Action Stack for audit/undo
        self.live_ll = ComplaintLinkedList()             # Phase 1: Singly Linked List
        self.ward_graph = self.db.get_municipal_ward_graph()  # Phase 2: Municipal Ward Graph (Adjacency List)
        
        self._build_ui()

    def _build_ui(self):
        # Header Row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=35, pady=(25, 10))

        left_h = ctk.CTkFrame(header, fg_color="transparent")
        left_h.pack(side="left")
        ctk.CTkLabel(left_h, text="📝 Report a Civic Issue", font=("Segoe UI", 26, "bold"),
                     text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(left_h, text="Submit municipal problems with automatic DSA Priority Queue routing",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(anchor="w")

        # Scrollable Content
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=35, pady=(10, 20))

        # Main Split Row: Left (Form) & Right (Live Preview Card)
        main_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        main_grid.pack(fill="both", expand=True)
        main_grid.grid_columnconfigure(0, weight=3)
        main_grid.grid_columnconfigure(1, weight=2)

        # ── LEFT: FORM WIZARD ──
        form_card = ctk.CTkFrame(main_grid, fg_color=self.CARD_BG, corner_radius=18,
                                 border_width=1.5, border_color=self.CARD_BORDER)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        # Step 1: Category Cards Grid
        ctk.CTkLabel(form_card, text="1. Choose Category", font=("Segoe UI", 15, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=25, pady=(20, 10))

        cat_grid = ctk.CTkFrame(form_card, fg_color="transparent")
        cat_grid.pack(fill="x", padx=20, pady=(0, 15))
        for col in range(4):
            cat_grid.grid_columnconfigure(col, weight=1)

        self.cat_cards = {}
        for idx, (cat_name, meta) in enumerate(self.CATEGORY_METADATA.items()):
            r, c = divmod(idx, 4)
            is_active = (cat_name == self.selected_category.get())

            btn = ctk.CTkButton(
                cat_grid, text=f"{meta['icon']}\n{cat_name}",
                font=("Segoe UI", 11, "bold"),
                fg_color="#0d283d" if is_active else self.INPUT_BG,
                border_color=self.ACCENT if is_active else self.INPUT_BORDER,
                border_width=1.5 if is_active else 1,
                text_color=self.TEXT if is_active else self.TEXT_DIM,
                hover_color="#1a2b4a", height=65, corner_radius=12,
                command=lambda name=cat_name: self._select_category(name)
            )
            btn.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
            self.cat_cards[cat_name] = btn

        # Step 2: Issue Details
        ctk.CTkLabel(form_card, text="2. Issue Summary & Location", font=("Segoe UI", 15, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=25, pady=(10, 8))

        form_fields = ctk.CTkFrame(form_card, fg_color="transparent")
        form_fields.pack(fill="x", padx=25, pady=(0, 15))

        # Title
        ctk.CTkLabel(form_fields, text="Issue Title *", font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(2, 2))
        self.title_entry = self._create_input(form_fields, "e.g. Broken water pipe overflowing on road")
        self.title_entry.pack(fill="x", pady=(0, 10))
        self.title_entry.bind("<KeyRelease>", lambda e: self._update_preview())

        # Location & Priority Row
        loc_row = ctk.CTkFrame(form_fields, fg_color="transparent")
        loc_row.pack(fill="x", pady=(0, 10))
        loc_row.grid_columnconfigure(0, weight=2)
        loc_row.grid_columnconfigure(1, weight=1)

        loc_col = ctk.CTkFrame(loc_row, fg_color="transparent")
        loc_col.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(loc_col, text="Location / Landmark *", font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(0, 2))
        self.location_entry = self._create_input(loc_col, "e.g. Area A, Sector 4, Main Market")
        self.location_entry.pack(fill="x")
        self.location_entry.bind("<KeyRelease>", lambda e: self._update_preview())

        prio_col = ctk.CTkFrame(loc_row, fg_color="transparent")
        prio_col.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(prio_col, text="Urgency Level", font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(0, 2))
        self.prio_menu = ctk.CTkOptionMenu(
            prio_col, values=["Low", "Medium", "High"],
            variable=self.selected_priority, height=42,
            fg_color=self.INPUT_BG, button_color=self.ACCENT, text_color=self.TEXT,
            dropdown_fg_color=self.CARD_BG, corner_radius=10,
            command=lambda v: self._update_preview()
        )
        self.prio_menu.pack(fill="x")

        # Description
        ctk.CTkLabel(form_fields, text="Detailed Remarks & Context", font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(5, 2))
        self.desc_box = ctk.CTkTextbox(
            form_fields, height=90, fg_color=self.INPUT_BG,
            border_color=self.INPUT_BORDER, border_width=1.5,
            corner_radius=10, text_color=self.TEXT, font=("Segoe UI", 12)
        )
        self.desc_box.pack(fill="x", pady=(0, 10))
        self.desc_box.bind("<KeyRelease>", lambda e: self._update_preview())

        # Submit Action Row
        self.status_msg = ctk.CTkLabel(form_card, text="", font=("Segoe UI", 12, "bold"))
        self.status_msg.pack(pady=(0, 6))

        action_row = ctk.CTkFrame(form_card, fg_color="transparent")
        action_row.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkButton(
            action_row, text="🚀  Submit Complaint", font=("Segoe UI", 14, "bold"),
            fg_color=self.ACCENT, hover_color=self.ACCENT_HOVER, text_color="#ffffff",
            height=46, corner_radius=12, command=self._submit_complaint
        ).pack(side="right")

        # ── RIGHT: LIVE TICKET PREVIEW CARD ──
        preview_panel = ctk.CTkFrame(main_grid, fg_color=self.CARD_BG, corner_radius=18,
                                     border_width=1.5, border_color=self.CARD_BORDER)
        preview_panel.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        ctk.CTkLabel(preview_panel, text="👁️ Live Ticket Preview", font=("Segoe UI", 15, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=20, pady=(20, 10))

        self.ticket_card = ctk.CTkFrame(preview_panel, fg_color="#121b30", corner_radius=14,
                                        border_width=1.5, border_color=self.ACCENT)
        self.ticket_card.pack(fill="x", padx=20, pady=(0, 15))

        top_ticket = ctk.CTkFrame(self.ticket_card, fg_color="transparent")
        top_ticket.pack(fill="x", padx=15, pady=(14, 6))

        self.prev_id_lbl = ctk.CTkLabel(top_ticket, text="TICKET #PREVIEW", font=("Segoe UI", 11, "bold"),
                                        fg_color=self.INPUT_BG, text_color=self.ACCENT, corner_radius=6, padx=8, pady=2)
        self.prev_id_lbl.pack(side="left")

        self.prev_prio_lbl = ctk.CTkLabel(top_ticket, text="● Medium", font=("Segoe UI", 11, "bold"),
                                          text_color=self.WARNING)
        self.prev_prio_lbl.pack(side="right")

        self.prev_title_lbl = ctk.CTkLabel(self.ticket_card, text="Complaint Title Appears Here",
                                           font=("Segoe UI", 15, "bold"), text_color=self.TEXT,
                                           wraplength=260, justify="left")
        self.prev_title_lbl.pack(anchor="w", padx=15, pady=(4, 6))

        self.prev_meta_lbl = ctk.CTkLabel(self.ticket_card, text="🗑️ Garbage  |  📍 Location",
                                          font=("Segoe UI", 11), text_color=self.TEXT_DIM)
        self.prev_meta_lbl.pack(anchor="w", padx=15, pady=(0, 6))

        self.prev_dept_lbl = ctk.CTkLabel(self.ticket_card, text="🏢 Route: Sanitation Dept",
                                          font=("Segoe UI", 11, "bold"), text_color=self.ACCENT_BLUE)
        self.prev_dept_lbl.pack(anchor="w", padx=15, pady=(0, 14))

        # Workflow Explanation Card
        dsa_info = ctk.CTkFrame(preview_panel, fg_color=self.INPUT_BG, corner_radius=12, border_width=1, border_color=self.INPUT_BORDER)
        dsa_info.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(dsa_info, text="💡 How it gets processed:", font=("Segoe UI", 12, "bold"),
                     text_color=self.ACCENT).pack(anchor="w", padx=14, pady=(10, 4))
        steps_text = (
            "1. Inserted into Complaint Linked List (O(1) Head)\n"
            "2. Enqueued to FIFO Queue & Emergency Heap\n"
            "3. Stack Action record generated for audit\n"
            "4. Auto-assigned to jurisdiction Department"
        )
        ctk.CTkLabel(dsa_info, text=steps_text, font=("Segoe UI", 11), text_color=self.TEXT_DIM,
                     justify="left").pack(anchor="w", padx=14, pady=(0, 12))

    def _create_input(self, parent, placeholder):
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            font=("Segoe UI", 12), height=42,
            fg_color=self.INPUT_BG, border_color=self.INPUT_BORDER,
            border_width=1.5, corner_radius=10, text_color=self.TEXT
        )
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=self.ACCENT))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=self.INPUT_BORDER))
        return entry

    def _select_category(self, cat_name):
        self.selected_category.set(cat_name)
        for name, btn in self.cat_cards.items():
            is_active = (name == cat_name)
            btn.configure(
                fg_color="#0d283d" if is_active else self.INPUT_BG,
                border_color=self.ACCENT if is_active else self.INPUT_BORDER,
                border_width=1.5 if is_active else 1,
                text_color=self.TEXT if is_active else self.TEXT_DIM
            )
        self._update_preview()

    def _calc_urgency_infix_postfix(self, priority, category):
        """
        Phase 1 (CLO1): Infix to Postfix expression conversion and Stack-based evaluation.
        Formula (Infix): ( priority_weight * 3 + category_weight * 2 ) / 5
        Converts to Postfix via Shunting-Yard (using operator stack) and evaluates via operand stack.
        """
        p_map = {"High": 5, "Medium": 3, "Low": 1}
        c_map = {
            "Drainage": 5, "Water Leakage": 4, "Pothole": 4, "Damaged Road": 4,
            "Garbage": 3, "Streetlight": 3, "Public Cleanliness": 2, "Illegal Parking": 2
        }
        p_val = p_map.get(priority, 3)
        c_val = c_map.get(category, 3)

        # Infix token sequence: ['(', str(p_val), '*', '3', '+', str(c_val), '*', '2', ')', '/', '5']
        tokens = ['(', str(p_val), '*', '3', '+', str(c_val), '*', '2', ')', '/', '5']
        ops_stack = []
        postfix = []
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

        for tok in tokens:
            if tok.isdigit():
                postfix.append(float(tok))
            elif tok == '(':
                ops_stack.append(tok)
            elif tok == ')':
                while ops_stack and ops_stack[-1] != '(':
                    postfix.append(ops_stack.pop())
                if ops_stack and ops_stack[-1] == '(':
                    ops_stack.pop()
            elif tok in precedence:
                while (ops_stack and ops_stack[-1] in precedence and
                       precedence[ops_stack[-1]] >= precedence[tok]):
                    postfix.append(ops_stack.pop())
                ops_stack.append(tok)

        while ops_stack:
            postfix.append(ops_stack.pop())

        # Postfix Evaluation using Stack
        eval_stack = []
        for tok in postfix:
            if isinstance(tok, (int, float)):
                eval_stack.append(tok)
            else:
                b = eval_stack.pop()
                a = eval_stack.pop()
                if tok == '+': eval_stack.append(a + b)
                elif tok == '-': eval_stack.append(a - b)
                elif tok == '*': eval_stack.append(a * b)
                elif tok == '/': eval_stack.append(a / b if b != 0 else 0)

        urgency_score = round(eval_stack[-1], 2) if eval_stack else 3.0
        postfix_expr = " ".join(str(int(x) if isinstance(x, float) and x.is_integer() else x) for x in postfix)
        return urgency_score, postfix_expr

    def _update_preview(self):
        cat = self.selected_category.get()
        meta = self.CATEGORY_METADATA.get(cat, {"icon": "📌", "dept": "Municipal Dept"})
        prio = self.selected_priority.get()
        title = self.title_entry.get().strip() or "Issue title will appear here..."
        loc = self.location_entry.get().strip() or "Area / Location"

        # Phase 1: Dynamic Urgency calculation via Stack (Infix -> Postfix)
        urgency_score, postfix_repr = self._calc_urgency_infix_postfix(prio, cat)

        # Phase 2: Municipal Ward Graph (Adjacency List) & BFS Shortest Route
        target_ward = "Ward 1 - Downtown" if "down" in loc.lower() or "market" in loc.lower() else "Ward 2 - Civil Lines"
        bfs_route = self.ward_graph.bfs_shortest_path("Central Depot", target_ward)
        route_str = " ➔ ".join(bfs_route) if bfs_route else "Central Depot ➔ Assigned Ward"

        self.prev_title_lbl.configure(text=title)
        self.prev_meta_lbl.configure(text=f"{meta['icon']} {cat}  |  📍 {loc}\n🎯 Urgency Score (Stack Postfix): {urgency_score}/5.0\n🛣️ BFS Dispatch: {route_str}")
        self.prev_dept_lbl.configure(text=f"🏢 Route: {meta['dept']}")

        prio_colors = {"High": self.DANGER, "Medium": self.WARNING, "Low": self.SUCCESS}
        self.prev_prio_lbl.configure(text=f"● {prio} (Score: {urgency_score})", text_color=prio_colors.get(prio, self.TEXT))

    def _submit_complaint(self):
        title = self.title_entry.get().strip()
        location = self.location_entry.get().strip()
        category = self.selected_category.get()
        priority = self.selected_priority.get()
        desc = self.desc_box.get("1.0", "end-1c").strip()

        if not title:
            self.status_msg.configure(text="⚠️ Please enter an issue title.", text_color=self.DANGER)
            return
        if not location:
            self.status_msg.configure(text="⚠️ Please specify the location/landmark.", text_color=self.DANGER)
            return

        dept = self.CATEGORY_METADATA.get(category, {}).get("dept", "Sanitation Department")

        # Phase 1: Calculate urgency score via Infix -> Postfix Stack
        urgency_score, postfix_repr = self._calc_urgency_infix_postfix(priority, category)

        cid = self.db.add_complaint(
            citizen_id=self.user["id"],
            title=title,
            description=desc,
            category=category,
            location=location,
            priority=priority
        )
        self.db.update_complaint(cid, department=dept)

        if cid:
            comp_record = {
                "id": cid, "title": title, "category": category,
                "priority": priority, "urgency_score": urgency_score,
                "location": location, "department": dept
            }

            # ── Execute Phase 1 Linear Data Structures ──
            # 1. Enqueue to FIFO ComplaintQueue
            self.live_queue.enqueue(comp_record)
            # 2. Enqueue to EmergencyPriorityQueue (Max-Heap order)
            self.priority_queue.enqueue(comp_record, priority_score=urgency_score)
            # 3. Prepend into Singly Linked List (O(1) Head insertion)
            self.live_ll.prepend(comp_record)
            # 4. Push submission event to ActionStack (LIFO Audit/Undo)
            self.live_stack.push({"action": "SUBMIT", "id": cid, "title": title, "priority": priority})

            self.status_msg.configure(
                text=f"✓ Ticket #{cid} queued! (Urgency Score: {urgency_score}) Assigned to {dept}.",
                text_color=self.SUCCESS
            )
            self.title_entry.delete(0, "end")
            self.location_entry.delete(0, "end")
            self.desc_box.delete("1.0", "end")

            if self.on_complaint_submitted:
                self.after(600, lambda: self.on_complaint_submitted(cid))
        else:
            self.status_msg.configure(text="⚠️ Failed to submit complaint.", text_color=self.DANGER)

