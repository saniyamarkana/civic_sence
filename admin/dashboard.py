"""
Admin Dashboard Overview.
Displays key metrics, custom canvas-drawn category charts, department workload, and recent activity.
"""

# pyrefly: ignore [missing-import]
import customtkinter as ctk
import tkinter as tk


class AdminDashboard(ctk.CTkFrame):
    """Admin Overview with stat cards, canvas charts, and recent complaints table."""

    BG_DARK = "#0a0e1a"
    CARD_BG = "#111827"
    ACCENT = "#06b6d4"
    ACCENT2 = "#3b82f6"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    PURPLE = "#a855f7"
    TEXT = "#f1f5f9"
    TEXT_DIM = "#94a3b8"
    TEXT_MUTED = "#64748b"
    INPUT_BG = "#1e293b"
    BORDER = "#334155"

    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="📊 Administrative Dashboard", font=("Segoe UI", 24, "bold"),
                     text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text="Real-time civic complaint metrics & operations overview",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(anchor="w")

        ctk.CTkButton(
            header, text="🔄 Refresh Data", font=("Segoe UI", 12, "bold"),
            fg_color=self.CARD_BG, hover_color=self.INPUT_BG, text_color=self.TEXT,
            border_width=1, border_color=self.BORDER, height=36, corner_radius=8,
            command=self._refresh
        ).pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        self._render_dashboard()

    def _refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self._render_dashboard()

    def _render_dashboard(self):
        stats = self.db.get_stats()

        # ── Row 1: Stat Cards ──
        stats_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 20))
        stats_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._create_stat_card(stats_row, 0, "Total Complaints", str(stats.get("total_complaints", 0)), self.ACCENT, "📋")
        self._create_stat_card(stats_row, 1, "Pending Action", str(stats.get("pending", 0)), self.WARNING, "⏳")
        self._create_stat_card(stats_row, 2, "In Progress", str(stats.get("in_progress", 0)), self.ACCENT2, "⚙️")
        self._create_stat_card(stats_row, 3, "Resolved", str(stats.get("resolved", 0)), self.SUCCESS, "✅")

        # ── Row 2: Secondary Stats + Category Chart ──
        chart_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        chart_row.pack(fill="x", pady=(0, 20))
        chart_row.grid_columnconfigure(0, weight=3)
        chart_row.grid_columnconfigure(1, weight=2)

        # Left: Category Distribution Chart (Drawn on Tk Canvas)
        chart_card = ctk.CTkFrame(chart_row, fg_color=self.CARD_BG, corner_radius=16,
                                  border_width=1, border_color=self.BORDER)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(chart_card, text="📊 Complaints by Category", font=("Segoe UI", 16, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=20, pady=(15, 5))

        self._draw_category_bars(chart_card, stats.get("by_category", []))

        # Right: Quick System Summary
        sum_card = ctk.CTkFrame(chart_row, fg_color=self.CARD_BG, corner_radius=16,
                                border_width=1, border_color=self.BORDER)
        sum_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(sum_card, text="🛡️ System Status", font=("Segoe UI", 16, "bold"),
                     text_color=self.TEXT).pack(anchor="w", padx=20, pady=(15, 10))

        details = [
            ("👥 Registered Citizens", str(stats.get("total_citizens", 0)), self.TEXT),
            ("🚨 High Priority Issues", str(stats.get("high_priority", 0)), self.DANGER),
            ("❌ Rejected / Closed", str(stats.get("rejected", 0)), self.TEXT_MUTED),
            ("🏛️ Active Departments", "5 Municipal Depts", self.ACCENT),
        ]
        for label, val, color in details:
            r = ctk.CTkFrame(sum_card, fg_color=self.INPUT_BG, corner_radius=8)
            r.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(r, text=label, font=("Segoe UI", 12), text_color=self.TEXT_DIM, padx=10, pady=8).pack(side="left")
            ctk.CTkLabel(r, text=val, font=("Segoe UI", 13, "bold"), text_color=color, padx=10, pady=8).pack(side="right")

        # ── Row 3: Phase 2 Binary Tree Hierarchy & Traversals Card ──
        self._render_hierarchy_binary_tree_card()

        # ── Row 4: Recent Complaints Table ──
        table_card = ctk.CTkFrame(self.scroll, fg_color=self.CARD_BG, corner_radius=16,
                                  border_width=1, border_color=self.BORDER)
        table_card.pack(fill="x", pady=(0, 20))


        top_bar = ctk.CTkFrame(table_card, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(top_bar, text="🕒 Recent Complaints Log", font=("Segoe UI", 16, "bold"),
                     text_color=self.TEXT).pack(side="left")

        # Table Header
        th = ctk.CTkFrame(table_card, fg_color=self.INPUT_BG, height=36, corner_radius=6)
        th.pack(fill="x", padx=20, pady=(0, 5))
        th.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        cols = [("ID", 0), ("Title / Issue", 1), ("Category", 2), ("Location", 3), ("Priority", 4), ("Status", 5)]
        for name, cidx in cols:
            ctk.CTkLabel(th, text=name, font=("Segoe UI", 11, "bold"), text_color=self.TEXT_DIM).grid(row=0, column=cidx, sticky="w", padx=10, pady=6)

        recent = self.db.get_all_complaints()[:8]
        if not recent:
            ctk.CTkLabel(table_card, text="No complaints recorded yet.", font=("Segoe UI", 12),
                         text_color=self.TEXT_MUTED).pack(pady=20)
        else:
            for c in recent:
                tr = ctk.CTkFrame(table_card, fg_color="transparent")
                tr.pack(fill="x", padx=20, pady=3)
                tr.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

                ctk.CTkLabel(tr, text=f"#{c['id']}", font=("Segoe UI", 12, "bold"),
                             text_color=self.ACCENT).grid(row=0, column=0, sticky="w", padx=10)
                ctk.CTkLabel(tr, text=c["title"][:24] + ("..." if len(c["title"]) > 24 else ""),
                             font=("Segoe UI", 12), text_color=self.TEXT).grid(row=0, column=1, sticky="w", padx=10)
                ctk.CTkLabel(tr, text=c["category"], font=("Segoe UI", 12),
                             text_color=self.TEXT_DIM).grid(row=0, column=2, sticky="w", padx=10)
                ctk.CTkLabel(tr, text=c["location"] or "-", font=("Segoe UI", 12),
                             text_color=self.TEXT_DIM).grid(row=0, column=3, sticky="w", padx=10)

                pr_col = self.DANGER if c["priority"] == "High" else (self.WARNING if c["priority"] == "Medium" else self.SUCCESS)
                ctk.CTkLabel(tr, text=c["priority"], font=("Segoe UI", 11, "bold"),
                             text_color=pr_col).grid(row=0, column=4, sticky="w", padx=10)

                st_col = self.WARNING if c["status"] == "Pending" else (self.SUCCESS if c["status"] == "Resolved" else self.ACCENT2)
                ctk.CTkLabel(tr, text=c["status"], font=("Segoe UI", 11, "bold"),
                             text_color=st_col).grid(row=0, column=5, sticky="w", padx=10)

        # Padding at bottom
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

    def _draw_category_bars(self, parent, data):
        if not data:
            ctk.CTkLabel(parent, text="No complaint data for chart.", text_color=self.TEXT_MUTED).pack(pady=30)
            return

        canvas = tk.Canvas(parent, height=180, bg=self.CARD_BG, highlightthickness=0)
        canvas.pack(fill="x", padx=20, pady=(5, 15))

        max_count = max([item["cnt"] for item in data], default=1) or 1
        colors = ["#06b6d4", "#3b82f6", "#10b981", "#f59e0b", "#a855f7", "#ec4899", "#14b8a6", "#6366f1"]

        bar_height = 20
        spacing = 6
        start_y = 10
        label_width = 110
        chart_width = 380

        for i, item in enumerate(data[:6]):
            cat_name = item["category"]
            cnt = item["cnt"]
            y = start_y + i * (bar_height + spacing)
            color = colors[i % len(colors)]

            # Label
            canvas.create_text(
                label_width - 10, y + bar_height / 2, text=cat_name[:14],
                anchor="e", fill=self.TEXT_DIM, font=("Segoe UI", 9, "bold")
            )

            # Bar background track
            canvas.create_rectangle(
                label_width, y, label_width + chart_width, y + bar_height,
                fill=self.INPUT_BG, outline=""
            )

            # Filled bar with rounded visual width
            fill_w = int((cnt / max_count) * chart_width)
            if fill_w > 0:
                canvas.create_rectangle(
                    label_width, y, label_width + fill_w, y + bar_height,
                    fill=color, outline=""
                )

            # Count text
            canvas.create_text(
                label_width + fill_w + 12, y + bar_height / 2, text=str(cnt),
                anchor="w", fill=self.TEXT, font=("Segoe UI", 9, "bold")
            )

    # ─────────────────────────── PHASE 2: BINARY TREE & TRAVERSALS ───────────────────────────

    def _recursive_tree_rollup(self, node):
        """Phase 1: Recursive algorithm aggregating complaint workload across tree nodes."""
        if not node:
            return 0
        left_cnt = self._recursive_tree_rollup(node.left)
        right_cnt = self._recursive_tree_rollup(node.right)
        return left_cnt + right_cnt + node.stats.get("cases", 0)

    def _render_hierarchy_binary_tree_card(self):
        """Phase 2 (CLO2 Items 1 & 2): Renders the Municipal Governance Binary Tree and Traversals."""
        tree = self.db.get_department_hierarchy_tree()
        total_recursive = self._recursive_tree_rollup(tree.root)

        card = ctk.CTkFrame(self.scroll, fg_color=self.CARD_BG, corner_radius=16,
                            border_width=1, border_color=self.BORDER)
        card.pack(fill="x", pady=(0, 20))

        # Top Bar
        top_bar = ctk.CTkFrame(card, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(15, 8))

        left = ctk.CTkFrame(top_bar, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="🏛️ Municipal Administrative Hierarchy (Binary Tree)",
                     font=("Segoe UI", 16, "bold"), text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text=f"CLO2: Binary Tree representation · Recursive Workload Rollup: {total_recursive} Cases",
                     font=("Segoe UI", 11), text_color=self.TEXT_DIM).pack(anchor="w")

        # Traversal Selector Row
        traversal_row = ctk.CTkFrame(card, fg_color="transparent")
        traversal_row.pack(fill="x", padx=20, pady=(4, 10))

        display_box = ctk.CTkTextbox(card, height=140, fg_color=self.INPUT_BG,
                                     border_color=self.BORDER, border_width=1, text_color=self.TEXT,
                                     font=("Consolas", 11))
        display_box.pack(fill="x", padx=20, pady=(0, 15))

        def show_traversal(mode):
            display_box.delete("1.0", "end")
            if mode == "preorder":
                items = tree.preorder_traversal()
                header_txt = "=== PRE-ORDER TRAVERSAL (Root ➔ Left ➔ Right) | Executive Delegation Sequence ===\n"
            elif mode == "inorder":
                items = tree.inorder_traversal()
                header_txt = "=== IN-ORDER TRAVERSAL (Left ➔ Root ➔ Right) | Symmetrical Department Audit ===\n"
            else:
                items = tree.postorder_traversal()
                header_txt = "=== POST-ORDER TRAVERSAL (Left ➔ Right ➔ Root) | Bottom-Up Workload Rollup ===\n"

            display_box.insert("end", header_txt)
            for idx, item in enumerate(items, 1):
                cases = item['stats'].get('cases', 0)
                rollup = item['stats'].get('rollup_total', cases)
                line = f"{idx}. [{item['key']}] {item['title']} ({item['role']}) ➔ Local: {cases} cases | Rollup: {rollup}\n"
                display_box.insert("end", line)

        ctk.CTkButton(
            traversal_row, text="1. Pre-Order (Delegation)", font=("Segoe UI", 11, "bold"),
            fg_color=self.ACCENT, hover_color="#0891b2", text_color="#ffffff",
            height=32, corner_radius=6, command=lambda: show_traversal("preorder")
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            traversal_row, text="2. In-Order (Audit)", font=("Segoe UI", 11, "bold"),
            fg_color=self.ACCENT2, hover_color="#2563eb", text_color="#ffffff",
            height=32, corner_radius=6, command=lambda: show_traversal("inorder")
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            traversal_row, text="3. Post-Order (Rollup)", font=("Segoe UI", 11, "bold"),
            fg_color=self.PURPLE, hover_color="#9333ea", text_color="#ffffff",
            height=32, corner_radius=6, command=lambda: show_traversal("postorder")
        ).pack(side="left")

        # Initial view: Pre-order
        show_traversal("preorder")

