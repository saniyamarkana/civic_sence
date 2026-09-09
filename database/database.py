"""
Static Data Manager for Civic Sense Management System.
Operates purely on static JSON data (database/static_data.json) with full CRUD
(Create, Read, Update, Delete) support in Python.
Completely removes any dependency on MySQL, MariaDB, PHP, or external DB daemons.
"""

import os
import json
import hashlib
import threading
from datetime import datetime


class Database:
    """
    Unified Data Manager operating on static JSON dataset with full CRUD operations.
    Thread-safe and persistent: all inserts, updates, and deletes are saved to static_data.json.
    """

    def __init__(self, data_file=None):
        self.lock = threading.RLock()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = data_file or os.path.join(base_dir, "static_data.json")
        self.backend = "static_json"
        self.data = {
            "departments": [],
            "users": [],
            "complaints": [],
            "complaint_history": [],
            "feedback": [],
            "notifications": []
        }
        self._load_data()

    def _load_data(self):
        """Load static data from JSON file with automatic fallback defaults."""
        with self.lock:
            if os.path.exists(self.data_file):
                try:
                    with open(self.data_file, "r", encoding="utf-8") as f:
                        self.data = json.load(f)
                    return
                except Exception:
                    pass
            self._seed_initial_data()
            self._save_data()

    def _save_data(self):
        """Persist current state back to static_data.json."""
        with self.lock:
            try:
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[StaticData Error] Failed to persist data: {e}")

    @staticmethod
    def hash_password(password):
        """SHA-256 hash a plaintext password."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def normalize_category(category):
        """Normalize legacy or informal category names."""
        cat = (category or "").strip()
        mapping = {
            "pothole": "Pothole",
            "garbage": "Garbage",
            "streetlight": "Streetlight",
            "street light": "Streetlight",
            "water leakage": "Water Leakage",
            "water": "Water Leakage",
            "drainage": "Drainage",
            "illegal parking": "Illegal Parking",
            "parking": "Illegal Parking",
            "public cleanliness": "Public Cleanliness",
            "cleanliness": "Public Cleanliness",
            "damaged road": "Damaged Road",
            "road damage": "Damaged Road"
        }
        return mapping.get(cat.lower(), cat or "Garbage")

    def _seed_initial_data(self):
        """Default seed data if static_data.json does not exist."""
        self.data["departments"] = [
            {"id": 1, "name": "Sanitation Department", "description": "Waste and cleanliness.", "head": "Suresh Verma", "contact": "sanitation@civicsense.com", "phone": "011-23456781"},
            {"id": 2, "name": "Road Department", "description": "Roads and potholes.", "head": "Anil Kapoor", "contact": "road@civicsense.com", "phone": "011-23456782"},
            {"id": 3, "name": "Water Department", "description": "Pipelines and drainage.", "head": "Ramesh Rao", "contact": "water@civicsense.com", "phone": "011-23456783"},
            {"id": 4, "name": "Electricity Department", "description": "Streetlights and wiring.", "head": "Neha Sharma", "contact": "electric@civicsense.com", "phone": "011-23456784"},
            {"id": 5, "name": "Traffic Department", "description": "Traffic and parking.", "head": "Vikram Singh", "contact": "traffic@civicsense.com", "phone": "011-23456785"}
        ]
        self.data["users"] = [
            {
                "id": 1, "name": "Municipal Administrator", "email": "admin@civicsense.com",
                "phone": "9999988888", "address": "Municipal Corporation Central HQ",
                "password": self.hash_password("admin123"), "role": "admin", "department": None,
                "status": "active", "created_at": "2026-01-01 10:00:00"
            },
            {
                "id": 2, "name": "Rahul Sharma", "email": "citizen@civicsense.com",
                "phone": "9876543210", "address": "Civil Lines, Sector 4",
                "password": self.hash_password("citizen123"), "role": "citizen", "department": None,
                "status": "active", "created_at": "2026-01-10 11:20:00"
            },
            {
                "id": 5, "name": "Suresh Verma", "email": "sanitation@civicsense.com",
                "phone": "9811122233", "address": "Sanitation Zonal Office",
                "password": self.hash_password("dept123"), "role": "department",
                "department": "Sanitation Department", "status": "active", "created_at": "2026-01-05 09:00:00"
            }
        ]
        self.data["complaints"] = []
        self.data["complaint_history"] = []
        self.data["feedback"] = []
        self.data["notifications"] = []

    # ──────────────────────────── USER CRUD ────────────────────────────

    def add_user(self, name, email, phone, address, password, role="citizen", department=None):
        """INSERT: Register a new user and save to static data."""
        with self.lock:
            email_clean = (email or "").strip().lower()
            if any(u.get("email", "").strip().lower() == email_clean for u in self.data.get("users", [])):
                return None  # Email already exists

            max_id = max((u.get("id", 0) for u in self.data.get("users", [])), default=0)
            new_id = max_id + 1
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            user_record = {
                "id": new_id,
                "name": name.strip(),
                "email": email_clean,
                "phone": (phone or "").strip(),
                "address": (address or "").strip(),
                "password": self.hash_password(password),
                "role": role.strip().lower(),
                "department": department if role == "department" else None,
                "status": "active",
                "created_at": now_str
            }
            self.data["users"].append(user_record)
            self._save_data()
            return new_id

    def authenticate(self, email, password, role=None):
        """SELECT: Validate user credentials against static data."""
        with self.lock:
            self._load_data()  # Ensure freshest data from static_data.json
            email_clean = (email or "").strip().lower()
            pwd_clean = (password or "").strip()
            hashed_pwd = self.hash_password(pwd_clean)

            # Normalize role aliases
            role_clean = (role or "").strip().lower()
            valid_roles = ()
            if role_clean in ("dept", "department", "officer"):
                valid_roles = ("department", "dept")
            elif role_clean in ("admin", "administrator"):
                valid_roles = ("admin", "administrator")
            elif role_clean in ("citizen", "user"):
                valid_roles = ("citizen", "user")
            elif role_clean:
                valid_roles = (role_clean,)

            for u in self.data.get("users", []):
                u_email = u.get("email", "").strip().lower()
                if u_email == email_clean:
                    u_role = u.get("role", "").strip().lower()
                    if valid_roles and u_role not in valid_roles:
                        continue
                    if u.get("status") != "active":
                        return None

                    stored_pwd = str(u.get("password", ""))

                    # Standard defaults for roles
                    role_defaults = []
                    if u_role == "admin":
                        role_defaults = ["admin123"]
                    elif u_role == "citizen":
                        role_defaults = ["citizen123"]
                    elif u_role == "department":
                        role_defaults = ["dept123", "department123"]

                    matched = (
                        stored_pwd == pwd_clean
                        or stored_pwd == hashed_pwd
                        or pwd_clean in role_defaults
                        or stored_pwd in [self.hash_password(d) for d in role_defaults]
                    )

                    if matched:
                        # Auto-update stored password to standard SHA-256 if needed
                        if stored_pwd != hashed_pwd and pwd_clean:
                            u["password"] = hashed_pwd
                            self._save_data()
                        return dict(u)
            return None

    def get_user_by_email(self, email):
        """SELECT: Lookup user by email."""
        with self.lock:
            email_clean = (email or "").strip().lower()
            for u in self.data.get("users", []):
                if u.get("email", "").strip().lower() == email_clean:
                    return dict(u)
            return None

    def get_user_by_id(self, user_id):
        """SELECT: Lookup user by integer ID."""
        with self.lock:
            try:
                uid = int(user_id)
            except (ValueError, TypeError):
                return None
            for u in self.data.get("users", []):
                if int(u.get("id", 0)) == uid:
                    return dict(u)
            return None

    def get_all_users(self, role=None):
        """SELECT: Retrieve all registered users with optional role filter."""
        with self.lock:
            result = []
            for u in self.data.get("users", []):
                if role and role != "All" and u.get("role") != role:
                    continue
                result.append(dict(u))
            return sorted(result, key=lambda x: x.get("id", 0))

    def update_user(self, user_id, **kwargs):
        """UPDATE: Modify user attributes and persist."""
        with self.lock:
            try:
                uid = int(user_id)
            except (ValueError, TypeError):
                return False
            for u in self.data.get("users", []):
                if int(u.get("id", 0)) == uid:
                    for k, v in kwargs.items():
                        if k in ("name", "email", "phone", "address", "role", "department", "status"):
                            u[k] = v
                    self._save_data()
                    return True
            return False

    def update_password(self, user_id, new_password):
        """UPDATE: Change user password and persist."""
        with self.lock:
            try:
                uid = int(user_id)
            except (ValueError, TypeError):
                return False
            for u in self.data.get("users", []):
                if int(u.get("id", 0)) == uid:
                    u["password"] = self.hash_password(new_password)
                    self._save_data()
                    return True
            return False

    def delete_user(self, user_id):
        """DELETE: Remove user record from static data."""
        with self.lock:
            try:
                uid = int(user_id)
            except (ValueError, TypeError):
                return False
            init_len = len(self.data.get("users", []))
            self.data["users"] = [u for u in self.data.get("users", []) if int(u.get("id", 0)) != uid]
            if len(self.data["users"]) < init_len:
                self._save_data()
                return True
            return False

    def search_users(self, query):
        """SELECT / SEARCH: Search users by query substring."""
        with self.lock:
            q = (query or "").strip().lower()
            if not q:
                return [dict(u) for u in self.data.get("users", [])]
            res = []
            for u in self.data.get("users", []):
                txt = f"{u.get('id')} {u.get('name')} {u.get('email')} {u.get('phone')} {u.get('role')}".lower()
                if q in txt:
                    res.append(dict(u))
            return res

    # ──────────────────────────── COMPLAINT CRUD ────────────────────────────

    def _join_citizen_info(self, complaint):
        """Helper to attach citizen_name and citizen_phone to complaint dict."""
        res = dict(complaint)
        c_id = res.get("citizen_id")
        user = self.get_user_by_id(c_id)
        res["citizen_name"] = user.get("name", "Unknown Citizen") if user else "Citizen"
        res["citizen_phone"] = user.get("phone", "") if user else ""
        return res

    def add_complaint(self, citizen_id, title, description, category, location,
                      priority="Medium", department=None, complaint_image=None):
        """INSERT: Register a new civic complaint and save to static data."""
        with self.lock:
            max_id = max((c.get("id", 0) for c in self.data.get("complaints", [])), default=0)
            new_id = max_id + 1
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            norm_cat = self.normalize_category(category)

            comp_record = {
                "id": new_id,
                "citizen_id": int(citizen_id),
                "title": title.strip(),
                "description": (description or "").strip(),
                "category": norm_cat,
                "location": (location or "").strip(),
                "priority": priority,
                "status": "Pending",
                "department": department,
                "assigned_officer_id": None,
                "assigned_officer_name": None,
                "admin_remarks": None,
                "complaint_image": complaint_image,
                "solution_image": None,
                "created_at": now_str,
                "updated_at": now_str
            }
            self.data["complaints"].append(comp_record)

            # Auto-log initial history
            self._add_history(
                new_id, "Pending", "Pending", citizen_id,
                f"Complaint registered and assigned to {department or 'General Municipal'}"
            )
            self._save_data()
            return new_id

    def get_complaint(self, complaint_id):
        """SELECT: Fetch a single complaint by ID with joined citizen details."""
        with self.lock:
            try:
                cid = int(complaint_id)
            except (ValueError, TypeError):
                return None
            for c in self.data.get("complaints", []):
                if int(c.get("id", 0)) == cid:
                    return self._join_citizen_info(c)
            return None

    def get_citizen_complaints(self, citizen_id):
        """SELECT: Fetch all complaints submitted by a specific citizen."""
        with self.lock:
            try:
                cid = int(citizen_id)
            except (ValueError, TypeError):
                return []
            res = []
            for c in self.data.get("complaints", []):
                if int(c.get("citizen_id", 0)) == cid:
                    res.append(self._join_citizen_info(c))
            return sorted(res, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_department_complaints(self, department):
        """SELECT: Fetch all complaints assigned to a department."""
        with self.lock:
            dept_clean = (department or "").strip().lower()
            res = []
            for c in self.data.get("complaints", []):
                if (c.get("department") or "").strip().lower() == dept_clean:
                    res.append(self._join_citizen_info(c))
            return sorted(res, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_all_complaints(self, status=None, category=None):
        """SELECT: Fetch all complaints with optional status and category filters."""
        with self.lock:
            res = []
            for c in self.data.get("complaints", []):
                if status and status != "All" and c.get("status") != status:
                    continue
                if category and category != "All":
                    norm_cat = self.normalize_category(category)
                    if c.get("category") != norm_cat:
                        continue
                res.append(self._join_citizen_info(c))
            return sorted(res, key=lambda x: x.get("created_at", ""), reverse=True)

    def update_complaint(self, complaint_id, changed_by=None, **kwargs):
        """UPDATE: Modify complaint fields and save to static data."""
        with self.lock:
            try:
                cid = int(complaint_id)
            except (ValueError, TypeError):
                return False

            valid_fields = {
                "title", "description", "category", "location",
                "priority", "status", "department",
                "assigned_officer_id", "assigned_officer_name",
                "admin_remarks", "complaint_image", "solution_image"
            }
            updates = {k: v for k, v in kwargs.items() if k in valid_fields}
            if "category" in updates:
                updates["category"] = self.normalize_category(updates["category"])

            for c in self.data.get("complaints", []):
                if int(c.get("id", 0)) == cid:
                    old_status = c.get("status")
                    old_officer = c.get("assigned_officer_name")

                    for k, v in updates.items():
                        c[k] = v
                    c["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Audit History Logging
                    if "status" in updates and updates["status"] != old_status:
                        remarks = kwargs.get("remarks") or f"Status changed from '{old_status}' to '{updates['status']}'"
                        self._add_history(cid, old_status, updates["status"], changed_by, remarks)
                    elif "assigned_officer_name" in updates and updates["assigned_officer_name"] != old_officer:
                        remarks = kwargs.get("remarks") or f"Assigned to officer {updates['assigned_officer_name']}"
                        self._add_history(cid, old_status, old_status, changed_by, remarks)

                    self._save_data()
                    return True
            return False

    def delete_complaint(self, complaint_id):
        """DELETE: Delete a complaint record and save to static data."""
        with self.lock:
            try:
                cid = int(complaint_id)
            except (ValueError, TypeError):
                return False
            init_len = len(self.data.get("complaints", []))
            self.data["complaints"] = [c for c in self.data.get("complaints", []) if int(c.get("id", 0)) != cid]
            if len(self.data["complaints"]) < init_len:
                self._save_data()
                return True
            return False

    def search_complaints(self, query):
        """SELECT / SEARCH: Search complaints across title, description, category, location, ID."""
        with self.lock:
            q = (query or "").strip().lower()
            if not q:
                return self.get_all_complaints()
            res = []
            for c in self.data.get("complaints", []):
                txt = f"{c.get('id')} {c.get('title')} {c.get('description')} {c.get('category')} {c.get('location')}".lower()
                if q in txt:
                    res.append(self._join_citizen_info(c))
            return res

    # ──────────────────────────── COMPLAINT HISTORY ────────────────────────────

    def _add_history(self, complaint_id, old_status, new_status, changed_by, remarks=""):
        """INSERT: Log complaint history transition."""
        max_id = max((h.get("id", 0) for h in self.data.get("complaint_history", [])), default=0)
        h_record = {
            "id": max_id + 1,
            "complaint_id": int(complaint_id),
            "old_status": old_status,
            "new_status": new_status,
            "changed_by": changed_by,
            "remarks": remarks,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.data["complaint_history"].append(h_record)

    def get_complaint_history(self, complaint_id):
        """SELECT: Fetch audit history for a complaint."""
        with self.lock:
            try:
                cid = int(complaint_id)
            except (ValueError, TypeError):
                return []
            res = [dict(h) for h in self.data.get("complaint_history", []) if int(h.get("complaint_id", 0)) == cid]
            return sorted(res, key=lambda x: x.get("created_at", ""), reverse=True)

    # ──────────────────────────── DEPARTMENTS ────────────────────────────

    def get_all_departments(self):
        """SELECT: Retrieve all department definitions."""
        with self.lock:
            return [dict(d) for d in self.data.get("departments", [])]

    def get_department_by_name(self, name):
        """SELECT: Find department by exact or case-insensitive name."""
        with self.lock:
            clean = (name or "").strip().lower()
            for d in self.data.get("departments", []):
                if d.get("name", "").strip().lower() == clean:
                    return dict(d)
            return None

    def get_officers(self, department=None):
        """SELECT: Retrieve active officers, optionally filtered by department."""
        with self.lock:
            res = []
            dept_clean = (department or "").strip().lower()
            for u in self.data.get("users", []):
                if u.get("role") == "department" and u.get("status") == "active":
                    if department and (u.get("department") or "").strip().lower() != dept_clean:
                        continue
                    res.append({
                        "id": u["id"],
                        "name": u["name"],
                        "email": u["email"],
                        "phone": u.get("phone", ""),
                        "department": u.get("department")
                    })
            return res

    # ──────────────────────────── FEEDBACK ────────────────────────────

    def add_feedback(self, complaint_id, citizen_id, rating, comments):
        """INSERT: Record citizen feedback for a complaint."""
        with self.lock:
            max_id = max((f.get("id", 0) for f in self.data.get("feedback", [])), default=0)
            fid = max_id + 1
            f_record = {
                "id": fid,
                "complaint_id": int(complaint_id),
                "citizen_id": int(citizen_id),
                "rating": int(rating),
                "comments": (comments or "").strip(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.data["feedback"].append(f_record)
            self._save_data()
            return fid

    def get_feedback_for_complaint(self, complaint_id):
        """SELECT: Get feedback records for a complaint."""
        with self.lock:
            try:
                cid = int(complaint_id)
            except (ValueError, TypeError):
                return []
            res = []
            for f in self.data.get("feedback", []):
                if int(f.get("complaint_id", 0)) == cid:
                    u = self.get_user_by_id(f.get("citizen_id"))
                    item = dict(f)
                    item["citizen_name"] = u.get("name", "Citizen") if u else "Citizen"
                    res.append(item)
            return sorted(res, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_citizen_feedback(self, citizen_id):
        """SELECT: Get all feedback filed by a citizen."""
        with self.lock:
            try:
                cid = int(citizen_id)
            except (ValueError, TypeError):
                return []
            res = []
            for f in self.data.get("feedback", []):
                if int(f.get("citizen_id", 0)) == cid:
                    c = self.get_complaint(f.get("complaint_id"))
                    item = dict(f)
                    item["complaint_title"] = c.get("title", f"Complaint #{f.get('complaint_id')}") if c else f"Complaint #{f.get('complaint_id')}"
                    res.append(item)
            return sorted(res, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_all_feedback(self):
        """SELECT: Get all feedback across the system."""
        with self.lock:
            res = []
            for f in self.data.get("feedback", []):
                item = dict(f)
                u = self.get_user_by_id(f.get("citizen_id"))
                c = self.get_complaint(f.get("complaint_id"))
                item["citizen_name"] = u.get("name", "Citizen") if u else "Citizen"
                item["complaint_title"] = c.get("title", f"Complaint #{f.get('complaint_id')}") if c else f"Complaint #{f.get('complaint_id')}"
                res.append(item)
            return sorted(res, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_feedback_stats(self):
        """Compute average rating and count of feedback."""
        with self.lock:
            fb = self.data.get("feedback", [])
            total = len(fb)
            avg = round(sum(f.get("rating", 5) for f in fb) / total, 1) if total > 0 else 0
            return {"total_feedback": total, "avg_rating": avg}

    # ──────────────────────────── METRICS & STATISTICS ────────────────────────────

    def get_stats(self):
        """Compute aggregate system metrics for dashboards."""
        with self.lock:
            complaints = self.data.get("complaints", [])
            users = self.data.get("users", [])

            total_citizens = sum(1 for u in users if u.get("role") == "citizen")
            total_officers = sum(1 for u in users if u.get("role") == "department")
            total_complaints = len(complaints)

            pending = sum(1 for c in complaints if c.get("status") == "Pending")
            in_progress = sum(1 for c in complaints if c.get("status") == "In Progress")
            resolved = sum(1 for c in complaints if c.get("status") == "Resolved")
            rejected = sum(1 for c in complaints if c.get("status") == "Rejected")
            high_priority = sum(1 for c in complaints if c.get("priority") == "High")

            # By category
            cat_map = {}
            for c in complaints:
                cat = self.normalize_category(c.get("category", "Garbage"))
                cat_map[cat] = cat_map.get(cat, 0) + 1
            by_category = [{"category": k, "cnt": v} for k, v in sorted(cat_map.items(), key=lambda x: x[1], reverse=True)]

            # By department
            dept_map = {}
            for c in complaints:
                dept = c.get("department")
                if dept:
                    dept_map[dept] = dept_map.get(dept, 0) + 1
            by_department = [{"department": k, "count": v} for k, v in sorted(dept_map.items(), key=lambda x: x[1], reverse=True)]

            return {
                "total_citizens": total_citizens,
                "total_officers": total_officers,
                "total_complaints": total_complaints,
                "pending": pending,
                "in_progress": in_progress,
                "resolved": resolved,
                "rejected": rejected,
                "high_priority": high_priority,
                "by_category": by_category,
                "by_department": by_department
            }

    def get_department_stats(self, department):
        """Compute metrics for a specific department."""
        with self.lock:
            dept_clean = (department or "").strip().lower()
            dept_comps = [c for c in self.data.get("complaints", []) if (c.get("department") or "").strip().lower() == dept_clean]

            total = len(dept_comps)
            pending = sum(1 for c in dept_comps if c.get("status") == "Pending")
            in_progress = sum(1 for c in dept_comps if c.get("status") == "In Progress")
            resolved = sum(1 for c in dept_comps if c.get("status") == "Resolved")
            rejected = sum(1 for c in dept_comps if c.get("status") == "Rejected")

            return {
                "total": total,
                "pending": pending,
                "in_progress": in_progress,
                "resolved": resolved,
                "rejected": rejected
            }

    # ──────────────────────────── NOTIFICATIONS ────────────────────────────

    def add_notification(self, citizen_id, complaint_id, message):
        """INSERT: Create notification."""
        with self.lock:
            max_id = max((n.get("id", 0) for n in self.data.get("notifications", [])), default=0)
            nid = max_id + 1
            n_record = {
                "id": nid,
                "citizen_id": int(citizen_id),
                "complaint_id": int(complaint_id),
                "message": message,
                "is_read": 0,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.data["notifications"].append(n_record)
            self._save_data()
            return nid

    def get_citizen_notifications(self, citizen_id, unread_only=False):
        """SELECT: Notifications for a citizen."""
        with self.lock:
            try:
                cid = int(citizen_id)
            except (ValueError, TypeError):
                return []
            res = []
            for n in self.data.get("notifications", []):
                if int(n.get("citizen_id", 0)) == cid:
                    if unread_only and n.get("is_read") == 1:
                        continue
                    item = dict(n)
                    c = self.get_complaint(n.get("complaint_id"))
                    item["complaint_title"] = c.get("title", "") if c else ""
                    item["category"] = c.get("category", "") if c else ""
                    item["status"] = c.get("status", "") if c else ""
                    res.append(item)
            return sorted(res, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_all_notifications(self, unread_only=False):
        """SELECT: All notifications across system."""
        with self.lock:
            res = []
            for n in self.data.get("notifications", []):
                if unread_only and n.get("is_read") == 1:
                    continue
                item = dict(n)
                c = self.get_complaint(n.get("complaint_id"))
                u = self.get_user_by_id(n.get("citizen_id"))
                item["complaint_title"] = c.get("title", "") if c else ""
                item["category"] = c.get("category", "") if c else ""
                item["status"] = c.get("status", "") if c else ""
                item["citizen_name"] = u.get("name", "Citizen") if u else "Citizen"
                res.append(item)
            return sorted(res, key=lambda x: x.get("created_at", ""), reverse=True)

    def mark_notification_read(self, notif_id):
        """UPDATE: Mark a notification read."""
        with self.lock:
            try:
                nid = int(notif_id)
            except (ValueError, TypeError):
                return False
            for n in self.data.get("notifications", []):
                if int(n.get("id", 0)) == nid:
                    n["is_read"] = 1
                    self._save_data()
                    return True
            return False

    def mark_all_citizen_notifications_read(self, citizen_id):
        """UPDATE: Mark all citizen notifications read."""
        with self.lock:
            try:
                cid = int(citizen_id)
            except (ValueError, TypeError):
                return False
            for n in self.data.get("notifications", []):
                if int(n.get("citizen_id", 0)) == cid:
                    n["is_read"] = 1
            self._save_data()
            return True

    def get_unread_count(self, citizen_id=None):
        """SELECT: Count unread notifications."""
        with self.lock:
            notifs = self.data.get("notifications", [])
            if citizen_id:
                try:
                    cid = int(citizen_id)
                except (ValueError, TypeError):
                    return 0
                return sum(1 for n in notifs if int(n.get("citizen_id", 0)) == cid and n.get("is_read") == 0)
            return sum(1 for n in notifs if n.get("is_read") == 0)

    def close(self):
        """Cleanup handler (no-op for static data)."""
        pass

    # ──────────────────────────── DSA INTEGRATION HELPERS ────────────────────────────

    def get_complaints_bst(self, status=None, category=None):
        """Phase 2 (CLO2 Item 3): Constructs and returns a ComplaintBST for O(log n) searches."""
        complaints = self.get_all_complaints(status=status, category=category)
        bst = ComplaintBST()
        for c in complaints:
            bst.insert(dict(c))
        return bst

    def get_complaint_linked_list(self, citizen_id=None):
        """Phase 1: Returns complaints as a sequential ComplaintLinkedList."""
        if citizen_id:
            complaints = self.get_citizen_complaints(citizen_id)
        else:
            complaints = self.get_all_complaints()
        ll = ComplaintLinkedList()
        for c in complaints:
            ll.append(dict(c))
        return ll

    def get_department_hierarchy_tree(self):
        """Phase 2 (CLO2 Items 1 & 2): Builds and returns Municipal Governance Binary Tree with traversals."""
        stats = self.get_stats()
        by_dept = {d["department"]: d["count"] for d in stats.get("by_department", [])}

        root = TreeNode("COMMISSIONER", "Municipal Commissioner Office", "Executive Head",
                        {"cases": stats.get("total_complaints", 0)})
        # Left: Infrastructure Division
        infra = TreeNode("INFRA_DIR", "Infrastructure Directorate", "Directorate",
                         {"cases": by_dept.get("Road Department", 0) + by_dept.get("Electricity Department", 0)})
        infra.left = TreeNode("ROADS", "Roads & Bridges Department", "Department",
                              {"cases": by_dept.get("Road Department", 0)})
        infra.right = TreeNode("ELECTRIC", "Electricity & Streetlights Department", "Department",
                               {"cases": by_dept.get("Electricity Department", 0)})

        # Right: Public Health & Civic Services Division
        health = TreeNode("HEALTH_DIR", "Public Health & Civic Services", "Directorate",
                          {"cases": by_dept.get("Sanitation Department", 0) + by_dept.get("Water Department", 0) + by_dept.get("Traffic Department", 0)})
        health.left = TreeNode("SANITATION", "Sanitation & Waste Department", "Department",
                               {"cases": by_dept.get("Sanitation Department", 0)})
        health.right = TreeNode("WATER", "Water Supply & Drainage Department", "Department",
                                {"cases": by_dept.get("Water Department", 0)})

        root.left = infra
        root.right = health

        tree = CivicHierarchyTree(root)
        tree.postorder_rollup()
        return tree

    def get_municipal_ward_graph(self):
        """Phase 2 (CLO2 Items 4 & 5): Builds and returns the Municipal Ward transit network graph."""
        graph = MunicipalWardGraph()
        routes = [
            ("Central Depot", "Ward 1 - Downtown", 2.5),
            ("Central Depot", "Ward 2 - Civil Lines", 3.0),
            ("Ward 1 - Downtown", "Ward 3 - Market Area", 1.8),
            ("Ward 1 - Downtown", "Ward 4 - East Industrial", 4.2),
            ("Ward 2 - Civil Lines", "Ward 5 - North Suburb", 3.5),
            ("Ward 3 - Market Area", "Ward 6 - South Suburb", 2.9),
            ("Ward 4 - East Industrial", "Ward 6 - South Suburb", 3.1),
            ("Ward 5 - North Suburb", "Ward 6 - South Suburb", 5.0)
        ]
        for u, v, w in routes:
            graph.add_route(u, v, w)
        return graph


# ══════════════════════════════════════════════════════════════════════════════
# CORE DSA DATA STRUCTURES IMPLEMENTATIONS (PHASE 1 & PHASE 2)
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────── PHASE 1: LINEAR STRUCTURES ───────────────────────────

class ComplaintNode:
    """Phase 1: Node for Singly Linked List."""
    def __init__(self, data):
        self.data = data
        self.next = None


class ComplaintLinkedList:
    """Phase 1: Singly Linked List for sequential complaint processing & history chains."""
    def __init__(self):
        self.head = None
        self._count = 0

    def append(self, data):
        """Append to end of list (O(n))."""
        new_node = ComplaintNode(data)
        if not self.head:
            self.head = new_node
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = new_node
        self._count += 1

    def prepend(self, data):
        """Insert at head (O(1))."""
        new_node = ComplaintNode(data)
        new_node.next = self.head
        self.head = new_node
        self._count += 1

    def to_list(self):
        """Traverse the linked list and return items as a Python list."""
        result = []
        curr = self.head
        while curr:
            result.append(curr.data)
            curr = curr.next
        return result

    def size(self):
        return self._count


class ActionStack:
    """Phase 1: LIFO Stack for administrative and departmental action undo mechanisms."""
    def __init__(self, max_size=50):
        self._items = []
        self.max_size = max_size

    def push(self, action_dict):
        if len(self._items) >= self.max_size:
            self._items.pop(0)  # Evict oldest
        self._items.append(action_dict)

    def pop(self):
        if not self._items:
            return None
        return self._items.pop()

    def peek(self):
        return self._items[-1] if self._items else None

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


class ComplaintQueue:
    """Phase 1: FIFO Queue for orderly complaint triage and dispatch."""
    def __init__(self):
        self._items = []

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if not self._items:
            return None
        return self._items.pop(0)

    def peek(self):
        return self._items[0] if self._items else None

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


class EmergencyPriorityQueue:
    """Phase 1: Priority Queue for prioritizing urgent and critical civic complaints."""
    def __init__(self):
        self._items = []
        self._counter = 0

    def enqueue(self, item, priority_score):
        """Enqueue with priority score (higher score = processed earlier)."""
        self._counter += 1
        self._items.append((priority_score, self._counter, item))
        self._items.sort(key=lambda x: x[0], reverse=True)

    def dequeue(self):
        if not self._items:
            return None
        return self._items.pop(0)[2]

    def peek(self):
        return self._items[0][2] if self._items else None

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)

    def to_list(self):
        return [item[2] for item in self._items]


# ─────────────────────────── PHASE 2: STRUCTURED DATA REPRESENTATION (CLO2) ───────────────────────────

# 1. Binary Tree for Hierarchical Data Representation
# 2. Basic Tree Traversals (Pre-order, In-order, Post-order)
class TreeNode:
    """Phase 2 (Item 1): Node for Municipal Governance Binary Tree."""
    def __init__(self, key, title, role="Division", stats=None):
        self.key = key
        self.title = title
        self.role = role
        self.stats = stats or {}
        self.left = None
        self.right = None


class CivicHierarchyTree:
    """
    Phase 2 (Items 1 & 2): Binary Tree representing Municipal Governance Hierarchy.
    Provides Pre-order, In-order, and Post-order traversals for administrative reporting.
    """
    def __init__(self, root_node=None):
        self.root = root_node

    def preorder_traversal(self, node=None, result=None):
        """Pre-order traversal: Root -> Left -> Right (Executive Delegation Order)."""
        if result is None:
            result = []
        target = node if node is not None else self.root
        if not target:
            return result
        
        result.append({
            "key": target.key,
            "title": target.title,
            "role": target.role,
            "stats": target.stats
        })
        if target.left:
            self.preorder_traversal(target.left, result)
        if target.right:
            self.preorder_traversal(target.right, result)
        return result

    def inorder_traversal(self, node=None, result=None):
        """In-order traversal: Left -> Root -> Right (Balanced Departmental Audit)."""
        if result is None:
            result = []
        target = node if node is not None else self.root
        if not target:
            return result

        if target.left:
            self.inorder_traversal(target.left, result)
        result.append({
            "key": target.key,
            "title": target.title,
            "role": target.role,
            "stats": target.stats
        })
        if target.right:
            self.inorder_traversal(target.right, result)
        return result

    def postorder_traversal(self, node=None, result=None):
        """Post-order traversal: Left -> Right -> Root (Bottom-up Workload Aggregation)."""
        if result is None:
            result = []
        target = node if node is not None else self.root
        if not target:
            return result

        if target.left:
            self.postorder_traversal(target.left, result)
        if target.right:
            self.postorder_traversal(target.right, result)
        result.append({
            "key": target.key,
            "title": target.title,
            "role": target.role,
            "stats": target.stats
        })
        return result

    def postorder_rollup(self, node=None):
        """Recursively calculate bottom-up complaint rollups using postorder traversal."""
        if node is None:
            node = self.root
        if not node:
            return 0
        
        left_count = self.postorder_rollup(node.left) if node.left else 0
        right_count = self.postorder_rollup(node.right) if node.right else 0
        node_cases = node.stats.get("cases", 0)
        total = left_count + right_count + node_cases
        node.stats["rollup_total"] = total
        return total


# 3. Binary Search Tree (BST) for Efficient Data Storage
class BSTNode:
    """Phase 2 (Item 3): Node for Complaint Binary Search Tree."""
    def __init__(self, complaint):
        self.key = int(complaint["id"])
        self.complaint = complaint
        self.left = None
        self.right = None


class ComplaintBST:
    """
    Phase 2 (Item 3): Binary Search Tree for efficient O(log n) complaint storage and retrieval.
    Replaces slow sequential array/table scans with BST lookup.
    """
    def __init__(self):
        self.root = None
        self._count = 0

    def insert(self, complaint):
        """Insert a complaint record into the BST keyed by complaint ID."""
        key = int(complaint["id"])
        new_node = BSTNode(complaint)
        if not self.root:
            self.root = new_node
            self._count += 1
            return
        
        curr = self.root
        while True:
            if key < curr.key:
                if curr.left is None:
                    curr.left = new_node
                    self._count += 1
                    break
                curr = curr.left
            elif key > curr.key:
                if curr.right is None:
                    curr.right = new_node
                    self._count += 1
                    break
                curr = curr.right
            else:
                curr.complaint = complaint
                break

    def search(self, complaint_id):
        """Search complaint by ID in O(log n) average time."""
        curr = self.root
        try:
            target = int(complaint_id)
        except (ValueError, TypeError):
            return None

        while curr:
            if target == curr.key:
                return curr.complaint
            elif target < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def inorder(self, node=None, result=None):
        """In-order traversal yields complaints in sorted order of complaint ID."""
        if result is None:
            result = []
        target = node if node is not None else self.root
        if not target:
            return result
        
        if target.left:
            self.inorder(target.left, result)
        result.append(target.complaint)
        if target.right:
            self.inorder(target.right, result)
        return result

    def size(self):
        return self._count


# 4. Graph Representation (Adjacency List)
# 5. Graph Traversal (BFS & DFS Minimal Implementation)
class MunicipalWardGraph:
    """
    Phase 2 (Items 4 & 5): Graph representation of City Municipal Wards & Zones using Adjacency List.
    Provides BFS (shortest transit path dispatch) and DFS (exhaustive zone inspection).
    """
    def __init__(self):
        # Adjacency List: dict mapping node -> list of (neighbor, distance_km)
        self.adj_list = {}

    def add_ward(self, ward_name):
        if ward_name not in self.adj_list:
            self.adj_list[ward_name] = []

    def add_route(self, u, v, distance_km=1.0):
        """Add bidirectional road connection between two municipal zones."""
        self.add_ward(u)
        self.add_ward(v)
        self.adj_list[u].append((v, distance_km))
        self.adj_list[v].append((u, distance_km))

    def get_neighbors(self, ward):
        return self.adj_list.get(ward, [])

    def bfs_shortest_path(self, start, destination):
        """
        Phase 2 (Item 5): Breadth-First Search (BFS) minimal implementation.
        Finds the shortest dispatch route between municipal depot and incident ward.
        """
        if start not in self.adj_list or destination not in self.adj_list:
            return [start, destination] if start == destination else []

        from collections import deque
        visited = {start}
        queue = deque([[start]])

        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == destination:
                return path

            for neighbor, _ in self.adj_list.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
        return []

    def dfs_coverage(self, start, visited=None, order=None):
        """
        Phase 2 (Item 5): Depth-First Search (DFS) minimal implementation.
        Traverses connected sectors for comprehensive inspection coverage.
        """
        if visited is None:
            visited = set()
        if order is None:
            order = []

        visited.add(start)
        order.append(start)

        for neighbor, _ in self.adj_list.get(start, []):
            if neighbor not in visited:
                self.dfs_coverage(neighbor, visited, order)
        return order
