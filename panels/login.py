"""
Login Panel for Civic Sense Management System.
Ultra-Modern Glassmorphic UI with animated left branding canvas, glowing inputs, and smooth transitions.
"""

# pyrefly: ignore [missing-import]
import customtkinter as ctk
import tkinter as tk
import math


class LoginPanel(ctk.CTkFrame):
    """Split-screen modern login & registration panel with animations."""

    # ──────────────── Theme Tokens ────────────────
    BG_DARK = "#070b14"
    LEFT_BG = "#0a1124"
    CARD_BG = "#0f172a"
    CARD_BORDER = "#1e293b"
    CARD_BORDER_GLOW = "#06b6d4"
    
    ACCENT = "#06b6d4"
    ACCENT_HOVER = "#0891b2"
    ACCENT_BLUE = "#3b82f6"
    ACCENT_PURPLE = "#8b5cf6"
    
    SUCCESS = "#10b981"
    SUCCESS_HOVER = "#059669"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    
    TEXT = "#f8fafc"
    TEXT_DIM = "#94a3b8"
    TEXT_MUTED = "#64748b"
    INPUT_BG = "#131f37"
    INPUT_BORDER = "#223254"
    INPUT_FOCUS_BORDER = "#06b6d4"

    def __init__(self, parent, db, on_login_success):
        super().__init__(parent, fg_color=self.BG_DARK, corner_radius=0)
        self.db = db
        self.on_login_success = on_login_success
        self.selected_role = tk.StringVar(value="citizen")
        
        # Animation state
        self.anim_angle = 0
        self.anim_running = True
        
        self._build_ui()
        self._start_ambient_animation()

    def destroy(self):
        self.anim_running = False
        super().destroy()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1, uniform="group1")
        self.grid_columnconfigure(1, weight=1, uniform="group1")
        self.grid_rowconfigure(0, weight=1)

        # ─── Left Animated Hero Panel ───
        self._build_hero_panel()

        # ─── Right Glassmorphic Form Panel ───
        self._build_form_panel()

    # ════════════════════════════════════════════════════════════════
    #  LEFT — HERO BRANDING WITH DYNAMIC GLOW CANVAS
    # ════════════════════════════════════════════════════════════════

    def _build_hero_panel(self):
        self.left_frame = ctk.CTkFrame(self, fg_color=self.LEFT_BG, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Canvas for animated ambient glowing orbs & grid lines
        self.hero_canvas = tk.Canvas(self.left_frame, bg=self.LEFT_BG, highlightthickness=0)
        self.hero_canvas.grid(row=0, column=0, sticky="nsew")

        # Foreground Content container overlay
        self.hero_content = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.hero_content.place(relx=0.5, rely=0.5, anchor="center")

        # Shield Logo Badge with glowing border
        badge_frame = ctk.CTkFrame(self.hero_content, fg_color="#0c1d38", corner_radius=28,
                                   border_width=2, border_color=self.ACCENT, width=96, height=96)
        badge_frame.pack(pady=(0, 15))
        badge_frame.pack_propagate(False)

        ctk.CTkLabel(badge_frame, text="🏛️", font=("Segoe UI Emoji", 44)).place(relx=0.5, rely=0.5, anchor="center")

        # App Title with cyber gradient glow
        ctk.CTkLabel(self.hero_content, text="CivicSense", font=("Segoe UI", 38, "bold"),
                     text_color=self.TEXT).pack()

        ctk.CTkLabel(self.hero_content, text="Intelligent Civic Issue Management & DSA System",
                     font=("Segoe UI", 13, "bold"), text_color=self.ACCENT).pack(pady=(4, 25))

        # Highlights Glass Card
        feats_card = ctk.CTkFrame(self.hero_content, fg_color="#0f182e", corner_radius=18,
                                  border_width=1, border_color="#1e293b")
        feats_card.pack(fill="x", padx=10, pady=(0, 20))

        features = [
            ("⚡ Instant Reporting", "Submit civic issues in 3 simple steps with live tracking", self.ACCENT),
            ("🔄 Phase 1 DSA Engine", "Queue, Stack, and Dynamic Linked List Operations", self.ACCENT_PURPLE),
            ("🛡️ Multi-Role Security", "Dedicated Citizen, Admin & Department Dashboards", self.SUCCESS),
        ]

        for title, sub, color in features:
            f = ctk.CTkFrame(feats_card, fg_color="transparent")
            f.pack(fill="x", padx=18, pady=10)

            dot = ctk.CTkFrame(f, width=8, height=8, corner_radius=4, fg_color=color)
            dot.pack(side="left", padx=(0, 12), pady=6)

            text_col = ctk.CTkFrame(f, fg_color="transparent")
            text_col.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(text_col, text=title, font=("Segoe UI", 12, "bold"),
                         text_color=self.TEXT, anchor="w").pack(anchor="w")
            ctk.CTkLabel(text_col, text=sub, font=("Segoe UI", 10),
                         text_color=self.TEXT_DIM, anchor="w").pack(anchor="w")

        # Phase Badge
        pill = ctk.CTkFrame(self.hero_content, fg_color="#131e36", corner_radius=20,
                            border_width=1, border_color=self.ACCENT_BLUE)
        pill.pack(pady=(10, 0))

        ctk.CTkLabel(pill, text="★  Phase 1 : Linear Data Structures (CLO1)  ★",
                     font=("Segoe UI", 11, "bold"), text_color=self.ACCENT, padx=16, pady=6).pack()

    def _start_ambient_animation(self):
        """Draw animated ambient energy particles in background canvas."""
        if not self.anim_running:
            return
        
        try:
            w = self.hero_canvas.winfo_width() or 550
            h = self.hero_canvas.winfo_height() or 750
            self.hero_canvas.delete("anim")

            self.anim_angle += 0.04
            cx, cy = w / 2, h / 2

            # Orbiting glowing orbs
            for i, col in enumerate(["#06b6d4", "#3b82f6", "#8b5cf6"]):
                angle = self.anim_angle + (i * 2.094) # 120 deg
                r = 160 + math.sin(self.anim_angle * 2 + i) * 30
                ox = cx + math.cos(angle) * r
                oy = cy + math.sin(angle) * (r * 0.7)

                # Draw outer glow circle
                self.hero_canvas.create_oval(
                    ox - 60, oy - 60, ox + 60, oy + 60,
                    fill="", outline=col, width=1, tags="anim"
                )
                self.hero_canvas.create_oval(
                    ox - 4, oy - 4, ox + 4, oy + 4,
                    fill=col, outline="", tags="anim"
                )

            self.after(50, self._start_ambient_animation)
        except Exception:
            pass

    # ════════════════════════════════════════════════════════════════
    #  RIGHT — MODERN GLASSMORPHIC FORM
    # ════════════════════════════════════════════════════════════════

    def _build_form_panel(self):
        self.right_frame = ctk.CTkFrame(self, fg_color=self.BG_DARK, corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self._show_login_form()

    def _clear_right(self):
        for w in self.right_frame.winfo_children():
            w.destroy()

    # ──────────────── Login Screen ────────────────

    def _show_login_form(self):
        self._clear_right()

        # Center Card Container
        self.card = ctk.CTkFrame(self.right_frame, fg_color=self.CARD_BG, corner_radius=22,
                                 border_width=1.5, border_color=self.CARD_BORDER, width=460)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)
        self.card.configure(width=460, height=600)

        pad = 32

        # Header Title
        ctk.CTkLabel(self.card, text="Welcome Back 👋", font=("Segoe UI", 26, "bold"),
                     text_color=self.TEXT).pack(pady=(pad, 4))
        ctk.CTkLabel(self.card, text="Sign in to access your civic control panel",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(pady=(0, 18))

        # Role Selector (Citizen / Admin / Department)
        role_container = ctk.CTkFrame(self.card, fg_color=self.INPUT_BG, corner_radius=12, height=44,
                                      border_width=1, border_color=self.INPUT_BORDER)
        role_container.pack(padx=pad, fill="x", pady=(0, 20))
        role_container.grid_columnconfigure((0, 1, 2), weight=1)

        self.role_buttons = {}
        roles = [("citizen", "👤 Citizen"), ("admin", "🛡️ Admin"), ("department", "🏢 Dept")]
        for i, (r, lbl) in enumerate(roles):
            is_active = (r == self.selected_role.get())
            btn = ctk.CTkButton(
                role_container, text=lbl, font=("Segoe UI", 12, "bold"),
                fg_color=self.ACCENT if is_active else "transparent",
                text_color="#ffffff" if is_active else self.TEXT_DIM,
                hover_color="#1a2947", height=36, corner_radius=9,
                command=lambda role=r: self._select_role(role)
            )
            btn.grid(row=0, column=i, padx=3, pady=4, sticky="ew")
            self.role_buttons[r] = btn

        # Form Fields
        form_inner = ctk.CTkFrame(self.card, fg_color="transparent")
        form_inner.pack(padx=pad, fill="x")

        # Email
        ctk.CTkLabel(form_inner, text="Email Address", font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(0, 4))
        self.email_entry = self._create_styled_entry(form_inner, "Enter your email e.g. citizen@civicsense.com")
        self.email_entry.pack(fill="x", pady=(0, 14))

        # Password
        ctk.CTkLabel(form_inner, text="Password", font=("Segoe UI", 11, "bold"),
                     text_color=self.TEXT_DIM).pack(anchor="w", pady=(0, 4))
        self.pass_entry = self._create_styled_entry(form_inner, "••••••••", is_password=True)
        self.pass_entry.pack(fill="x", pady=(0, 8))

        # Error / Success Message
        self.msg_label = ctk.CTkLabel(form_inner, text="", font=("Segoe UI", 11, "bold"), text_color=self.DANGER)
        self.msg_label.pack(pady=(0, 8))

        # Sign In Button
        self.sign_in_btn = ctk.CTkButton(
            form_inner, text="🚀  Sign In to Portal", font=("Segoe UI", 14, "bold"),
            fg_color=self.ACCENT, hover_color=self.ACCENT_HOVER, text_color="#ffffff",
            height=46, corner_radius=12, command=self._do_login
        )
        self.sign_in_btn.pack(fill="x", pady=(4, 15))

        # Switch to Register
        switch_row = ctk.CTkFrame(self.card, fg_color="transparent")
        switch_row.pack(pady=(0, 10))
        ctk.CTkLabel(switch_row, text="Don't have an account?", font=("Segoe UI", 12),
                     text_color=self.TEXT_DIM).pack(side="left")
        ctk.CTkButton(
            switch_row, text="Create Account", font=("Segoe UI", 12, "bold"),
            fg_color="transparent", hover_color="#18233c", text_color=self.ACCENT,
            width=100, command=self._show_register_form
        ).pack(side="left", padx=4)

        # Quick credentials pill
        cred_pill = ctk.CTkFrame(self.card, fg_color="#10192e", corner_radius=10, border_width=1, border_color=self.INPUT_BORDER)
        cred_pill.pack(padx=pad, fill="x", pady=(5, 0))
        ctk.CTkLabel(cred_pill, text="🔑 Test Logins: citizen@civicsense.com | admin@civicsense.com",
                     font=("Segoe UI", 10), text_color=self.TEXT_MUTED, pady=6).pack()

    # ──────────────── Register Screen ────────────────

    def _show_register_form(self):
        self._clear_right()

        self.card = ctk.CTkFrame(self.right_frame, fg_color=self.CARD_BG, corner_radius=22,
                                 border_width=1.5, border_color=self.CARD_BORDER, width=480)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)
        self.card.configure(width=480, height=660)

        pad = 32

        ctk.CTkLabel(self.card, text="Create Account ✨", font=("Segoe UI", 26, "bold"),
                     text_color=self.TEXT).pack(pady=(pad, 2))
        ctk.CTkLabel(self.card, text="Register as a Citizen to submit and track civic issues",
                     font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(pady=(0, 16))

        scroll = ctk.CTkScrollableFrame(self.card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=pad - 8, pady=(0, 15))

        # Fields
        fields = [
            ("Full Name *", "reg_name", "e.g. Rahul Sharma", False),
            ("Email Address *", "reg_email", "name@example.com", False),
            ("Phone Number", "reg_phone", "9876543210", False),
            ("Residential Address / Area", "reg_address", "Area A, Sector 4", False),
            ("Password *", "reg_pass", "Minimum 4 characters", True),
            ("Confirm Password *", "reg_confirm", "Re-enter password", True),
        ]

        self.reg_entries = {}
        for label, key, placeholder, is_pass in fields:
            ctk.CTkLabel(scroll, text=label, font=("Segoe UI", 11, "bold"),
                         text_color=self.TEXT_DIM).pack(anchor="w", pady=(6, 2))
            entry = self._create_styled_entry(scroll, placeholder, is_password=is_pass, height=40)
            entry.pack(fill="x", pady=(0, 6))
            self.reg_entries[key] = entry

        self.reg_msg = ctk.CTkLabel(scroll, text="", font=("Segoe UI", 11, "bold"), text_color=self.DANGER)
        self.reg_msg.pack(pady=4)

        # Submit Register Button
        ctk.CTkButton(
            scroll, text="✨  Complete Registration", font=("Segoe UI", 14, "bold"),
            fg_color=self.SUCCESS, hover_color=self.SUCCESS_HOVER, text_color="#ffffff",
            height=46, corner_radius=12, command=self._do_register
        ).pack(fill="x", pady=(6, 12))

        # Back to login
        back_row = ctk.CTkFrame(scroll, fg_color="transparent")
        back_row.pack(pady=(0, 10))
        ctk.CTkLabel(back_row, text="Already registered?", font=("Segoe UI", 12), text_color=self.TEXT_DIM).pack(side="left")
        ctk.CTkButton(
            back_row, text="Sign In Here", font=("Segoe UI", 12, "bold"),
            fg_color="transparent", text_color=self.ACCENT, hover_color="#18233c",
            width=90, command=self._show_login_form
        ).pack(side="left", padx=4)

    # ──────────────── Helpers & Input Styling ────────────────

    def _create_styled_entry(self, parent, placeholder, is_password=False, height=42):
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            font=("Segoe UI", 12), height=height,
            fg_color=self.INPUT_BG, border_color=self.INPUT_BORDER,
            border_width=1.5, corner_radius=10, text_color=self.TEXT,
            show="•" if is_password else ""
        )
        # Add glow on focus
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=self.INPUT_FOCUS_BORDER))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=self.INPUT_BORDER))
        return entry

    def _select_role(self, role):
        self.selected_role.set(role)
        for r, btn in self.role_buttons.items():
            is_active = (r == role)
            btn.configure(
                fg_color=self.ACCENT if is_active else "transparent",
                text_color="#ffffff" if is_active else self.TEXT_DIM
            )

    def _do_login(self):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get().strip()
        role = self.selected_role.get()

        if not email or not password:
            self._show_error("Please enter both email and password.")
            return

        user = self.db.authenticate(email, password, role)
        if user:
            self.msg_label.configure(text="✓ Authenticated! Loading panel...", text_color=self.SUCCESS)
            self.card.configure(border_color=self.SUCCESS)
            self.after(300, lambda: self.on_login_success(dict(user), role))
        else:
            self._show_error("Invalid email, password, or account role.")

    def _do_register(self):
        name = self.reg_entries["reg_name"].get().strip()
        email = self.reg_entries["reg_email"].get().strip()
        phone = self.reg_entries["reg_phone"].get().strip()
        address = self.reg_entries["reg_address"].get().strip()
        password = self.reg_entries["reg_pass"].get().strip()
        confirm = self.reg_entries["reg_confirm"].get().strip()

        if not name or not email or not password:
            self.reg_msg.configure(text="⚠️ Full Name, Email, and Password are required.", text_color=self.DANGER)
            return
        if password != confirm:
            self.reg_msg.configure(text="⚠️ Passwords do not match.", text_color=self.DANGER)
            return
        if len(password) < 4:
            self.reg_msg.configure(text="⚠️ Password must be at least 4 characters.", text_color=self.DANGER)
            return

        uid = self.db.add_user(name, email, phone, address, password, "citizen")
        if uid:
            self._show_login_form()
            self.email_entry.insert(0, email)
            self.msg_label.configure(text="✓ Account created successfully! Please sign in.", text_color=self.SUCCESS)
        else:
            self.reg_msg.configure(text="⚠️ Email already registered.", text_color=self.DANGER)

    def _show_error(self, message):
        self.msg_label.configure(text=f"⚠️ {message}", text_color=self.DANGER)
        self.card.configure(border_color=self.DANGER)
        self.after(1000, lambda: self.card.configure(border_color=self.CARD_BORDER))
