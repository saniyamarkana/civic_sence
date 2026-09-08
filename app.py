"""
Flask Web Application for CivicSense — Civic Complaint Management & DSA Platform.
Provides both Web UI (HTML/CSS/JS with glassmorphism & animations) and REST APIs connecting to SQLite & Python DSA modules.
"""

# pyrefly: ignore [missing-import]
import os
# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify, session, redirect, send_file
# pyrefly: ignore [missing-import]
from werkzeug.utils import secure_filename
from database.database import Database
from dsa.linked_list import LinkedList
from dsa.stack import Stack
from dsa.queue import Queue, PriorityQueue
from dsa.infix_postfix import InfixPostfix
from dsa.iterative import IterativeAlgorithms
from dsa.recursive import RecursiveAlgorithms
from dsa.simple_infix_postfix import calc_priority_score as simple_calc_priority_score

app = Flask(__name__)
app.secret_key = "civicsense_super_secret_phase1_key"

# Upload configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER_COMPLAINT = os.path.join(BASE_DIR, "static", "uploads", "complaint_images")
UPLOAD_FOLDER_SOLUTION  = os.path.join(BASE_DIR, "static", "uploads", "solution_images")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "jfif", "avif", "bmp", "tiff", "heic", "svg"}
os.makedirs(UPLOAD_FOLDER_COMPLAINT, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_SOLUTION, exist_ok=True)

def allowed_file(filename):
    if not filename or "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file, folder):
    """Save an uploaded file and return its saved filename, or None."""
    if not file or not getattr(file, "filename", None):
        return None
    raw_name = file.filename.strip()
    if not raw_name or not allowed_file(raw_name):
        return None
    import time
    ext = raw_name.rsplit(".", 1)[1].lower()
    safe_name = secure_filename(raw_name)
    if not safe_name or safe_name == ext:
        safe_name = f"image.{ext}"
    fname = f"{int(time.time() * 1000)}_{safe_name}"
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, fname))
    return fname

def save_base64_image(data_str, folder):
    """Save base64 data url (data:image/...;base64,...) to disk and return filename."""
    if not data_str or not isinstance(data_str, str) or "base64," not in data_str:
        return None
    try:
        import base64, time
        header, encoded = data_str.split("base64,", 1)
        ext = "jpg"
        if "image/png" in header:
            ext = "png"
        elif "image/webp" in header:
            ext = "webp"
        elif "image/gif" in header:
            ext = "gif"
        fname = f"{int(time.time() * 1000)}_upload.{ext}"
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, fname), "wb") as fh:
            fh.write(base64.b64decode(encoded.strip()))
        return fname
    except Exception as e:
        app.logger.error(f"Error saving base64 image: {e}")
        return None

# Database Singleton
db = Database()

# In-memory DSA instances for live interactive visual lab
live_queue = Queue(max_size=10)
live_p_queue = PriorityQueue(max_size=10)
live_stack = Stack(max_size=8)
live_ll = LinkedList()

# ══════════════════════════════════════════════════════════════════════════════
# BACKEND DSA SECTION: INFIX TO POSTFIX PRIORITY EVALUATION
# ══════════════════════════════════════════════════════════════════════════════
# Operates purely in the backend (no frontend display).
# Evaluates complaint urgency based on Priority (High/Med/Low) & Status (Pending/etc.)
# Uses Stack-based Infix -> Postfix conversion and evaluation:
#   Formula (Infix):   ( priority_weight * 3 + status_weight * 2 ) / 5
#   Converted Postfix: priority_weight 3 * status_weight 2 * + 5 /
# ══════════════════════════════════════════════════════════════════════════════

def backend_calc_priority_score(priority, status="Pending"):
    """
    Backend-only DSA Operation.
    Converts (priority * 3 + status * 2) / 5 from Infix to Postfix and evaluates it
    using a Stack. Operates silently in the backend whenever complaints are submitted
    or their status changes.
    """
    try:
        return simple_calc_priority_score(priority, status)
    except Exception as err:
        app.logger.error(f"[Backend DSA Error] Infix-Postfix calculation failed: {err}")
        return {
            "priority": priority,
            "status": status,
            "score": 2.0,
            "label": "MEDIUM",
            "level": "medium",
            "infix": "( 2 * 3 + 2 * 2 ) / 5",
            "postfix": "2 3 * 2 2 * + 5 /"
        }

# ─────────────────────────── Page Routes ───────────────────────────

@app.route("/download/dsa-pdf")
def download_dsa_pdf():
    """Serves the generated comprehensive DSA Architecture & Code Explanation PDF."""
    pdf_path = os.path.join(BASE_DIR, "CivicSense_DSA_Architecture_and_Code_Explanation.pdf")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=False, mimetype="application/pdf")
    return "DSA PDF not found. Please generate it first.", 404

@app.route("/")
def index():
    if "user_id" in session:
        user = db.get_user_by_id(session["user_id"])
        if not user:
            session.clear()
            return render_template("index.html")
        role = session.get("role")
        if role == "admin":
            return redirect("/admin")
        elif role == "department":
            return redirect("/department")
        else:
            return redirect("/citizen")
    return render_template("index.html")

@app.route("/citizen")
def citizen_page():
    if "user_id" not in session or session.get("role") != "citizen":
        return redirect("/")
    user = db.get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect("/")
    return render_template("citizen.html", user=dict(user))

@app.route("/admin")
def admin_page():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/")
    user = db.get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect("/")
    return render_template("admin.html", user=dict(user))

@app.route("/department")
def department_page():
    if "user_id" not in session or session.get("role") != "department":
        return redirect("/")
    user = db.get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect("/")
    return render_template("department.html", user=dict(user))

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ─────────────────────────── Auth APIs ───────────────────────────

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "citizen")

    user = db.authenticate(email, password, role)
    if user:
        session["user_id"] = user["id"]
        session["name"] = user["name"]
        session["email"] = user["email"]
        session["role"] = user["role"]
        session["department"] = user.get("department")
        return jsonify({"success": True, "role": user["role"], "user": dict(user)})
    return jsonify({"success": False, "message": "Invalid email, password, or role."}), 401

@app.route("/api/departments", methods=["GET"])
def get_departments():
    depts = db.get_all_departments()
    return jsonify([dict(d) for d in depts])

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "citizen").strip().lower()
    department = data.get("department", "").strip()

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email, and password are required."}), 400

    if role not in ("citizen", "admin", "department"):
        role = "citizen"

    if role == "department" and not department:
        return jsonify({"success": False, "message": "Please select a department for the officer account."}), 400

    dept_value = department if role == "department" else None
    uid = db.add_user(name, email, phone, address, password, role=role, department=dept_value)
    if uid:
        role_label = "Department Officer" if role == "department" else ("Admin" if role == "admin" else "Citizen")
        return jsonify({"success": True, "message": f"{role_label} account created successfully! Please sign in."})
    return jsonify({"success": False, "message": "Email address already registered."}), 400

# ─────────────────────────── Complaints APIs ───────────────────────────

@app.route("/api/complaints", methods=["GET"])
def get_complaints():
    try:
        status = request.args.get("status")
        category = request.args.get("category")
        role = session.get("role")
        user_id = session.get("user_id")

        if role == "citizen":
            complaints = db.get_citizen_complaints(user_id) if user_id else []
        elif role == "department":
            dept_name = session.get("department", "Sanitation Department")
            complaints = db.get_department_complaints(dept_name)
        else:
            complaints = db.get_all_complaints(status=status, category=category)

        return jsonify([dict(c) for c in (complaints or [])])
    except Exception as e:
        app.logger.error(f"Error fetching complaints: {e}")
        return jsonify([])

@app.route("/api/complaints", methods=["POST"])
def submit_complaint():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    try:
        # Check files regardless of how content_type is formatted
        img_file = (
            request.files.get("complaint_image")
            or request.files.get("image")
            or request.files.get("photo")
            or request.files.get("file")
        )

        if request.is_json:
            data = request.get_json(silent=True) or {}
            title       = (data.get("title") or "").strip()
            category    = data.get("category", "Garbage")
            location    = (data.get("location") or "").strip()
            priority    = data.get("priority", "Medium")
            description = (data.get("description") or "").strip()
            raw_img     = data.get("complaint_image") or data.get("image")
        else:
            title       = (request.form.get("title") or "").strip()
            category    = request.form.get("category", "Garbage")
            location    = (request.form.get("location") or "").strip()
            priority    = request.form.get("priority", "Medium")
            description = (request.form.get("description") or "").strip()
            raw_img     = request.form.get("complaint_image") or request.form.get("image")

        if not title or not location:
            return jsonify({"success": False, "message": "Title and location are required."}), 400

        category = db.normalize_category(category)

        dept_map = {
            "Garbage": "Sanitation Department",
            "Pothole": "Road Department",
            "Water Leakage": "Water Department",
            "Streetlight": "Electricity Department",
            "Drainage": "Water Department",
            "Illegal Parking": "Traffic Department",
            "Public Cleanliness": "Sanitation Department",
            "Damaged Road": "Road Department"
        }
        dept = dept_map.get(category, "Sanitation Department")

        # Save complaint image if provided
        complaint_image_fname = None
        if img_file and getattr(img_file, "filename", None):
            complaint_image_fname = save_upload(img_file, UPLOAD_FOLDER_COMPLAINT)
        elif raw_img:
            if isinstance(raw_img, str) and "base64," in raw_img:
                complaint_image_fname = save_base64_image(raw_img, UPLOAD_FOLDER_COMPLAINT)
            elif isinstance(raw_img, str) and str(raw_img).strip():
                clean_raw = str(raw_img).strip()
                if os.path.exists(os.path.join(UPLOAD_FOLDER_COMPLAINT, clean_raw)):
                    complaint_image_fname = clean_raw

        app.logger.info(f"Submitting complaint '{title}' with image file: {complaint_image_fname}")

        # Single-step INSERT with department and complaint_image included
        cid = db.add_complaint(
            citizen_id=session["user_id"],
            title=title,
            description=description,
            category=category,
            location=location,
            priority=priority,
            department=dept,
            complaint_image=complaint_image_fname
        )

        if not cid:
            app.logger.error("add_complaint returned no ID")
            return jsonify({"success": False, "message": "Failed to save complaint. Please try again."}), 500

        # ── Backend DSA Operation: Infix -> Postfix Priority Evaluation ──
        score_eval = backend_calc_priority_score(priority, "Pending")
        app.logger.info(
            f"[BACKEND DSA | Infix->Postfix] Complaint #{cid} ('{title}') | "
            f"Priority: {priority}, Status: Pending | "
            f"Infix: '{score_eval['infix']}' -> Postfix: '{score_eval['postfix']}' -> "
            f"Urgency Score: {score_eval['score']} [{score_eval['label']}]"
        )

        # Update in-memory DSA structures
        comp_dict = {
            "id": cid, "title": title, "category": category,
            "location": location, "priority": priority, "status": "Pending",
            "complaint_image": complaint_image_fname,
            "urgency_score": score_eval["score"],
            "urgency_label": score_eval["label"]
        }
        live_ll.insert_at_beginning(comp_dict)
        live_queue.enqueue(comp_dict)
        live_p_queue.enqueue(comp_dict, priority)
        live_stack.push({"id": cid, "action": f"Submitted #{cid} ({title})", "status": "Pending"})

        return jsonify({
            "success": True,
            "complaint_id": cid,
            "complaint_image": complaint_image_fname,
            "message": f"Complaint #{cid} registered successfully!"
        })

    except Exception as e:
        app.logger.error(f"Error submitting complaint: {e}", exc_info=True)
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route("/api/complaints/<int:cid>", methods=["GET"])
def get_single_complaint(cid):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    complaint = db.get_complaint(cid)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found"}), 404
    history = db.get_complaint_history(cid)
    feedback = db.get_feedback_for_complaint(cid)
    return jsonify({
        "complaint": dict(complaint),
        "history": [dict(h) for h in history],
        "feedback": [dict(f) for f in feedback]
    })

@app.route("/api/officers", methods=["GET"])
def get_officers_list():
    dept = request.args.get("department")
    officers = db.get_officers(department=dept)
    return jsonify([dict(o) for o in officers])

@app.route("/api/complaints/<int:cid>", methods=["PUT"])
def update_complaint(cid):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.json or {}
    status       = data.get("status")
    priority     = data.get("priority")
    department   = data.get("department")
    officer_id   = data.get("assigned_officer_id")
    officer_name = data.get("assigned_officer_name")
    remarks      = data.get("remarks", "")
    admin_remarks = data.get("admin_remarks", "")

    updates = {}
    if status:                       updates["status"]               = status
    if priority:                     updates["priority"]             = priority
    if department is not None:       updates["department"]           = department
    if officer_id is not None:       updates["assigned_officer_id"]  = officer_id
    if officer_name is not None:     updates["assigned_officer_name"]= officer_name
    if admin_remarks is not None:    updates["admin_remarks"]        = admin_remarks
    if "complaint_image" in data:    updates["complaint_image"]      = data.get("complaint_image")

    if not updates:
        return jsonify({"success": False, "message": "Nothing to update."}), 400

    auto_remark = remarks or (
        f"Assigned to {officer_name} | Status: {status}" if officer_name
        else f"Status updated to {status or 'unchanged'}"
    )

    # Fetch complaint BEFORE updating so we can compare old status
    old_complaint = db.get_complaint(cid)

    success = db.update_complaint(
        cid,
        changed_by=session["user_id"],
        remarks=auto_remark,
        **updates
    )
    if success:
        live_stack.push({"id": cid, "action": f"Updated #{cid} -> {status or 'Modified'}", "status": status or "Modified"})

        # ── Backend DSA Operation: Recalculate Urgency Score via Infix -> Postfix ──
        eff_priority = priority or (old_complaint.get("priority") if old_complaint else "Medium")
        eff_status   = status   or (old_complaint.get("status")   if old_complaint else "Pending")
        updated_eval = backend_calc_priority_score(eff_priority, eff_status)
        app.logger.info(
            f"[BACKEND DSA | Infix->Postfix] Complaint #{cid} updated | "
            f"Priority: {eff_priority}, Status: {eff_status} | "
            f"Infix: '{updated_eval['infix']}' -> Postfix: '{updated_eval['postfix']}' -> "
            f"Recalculated Urgency Score: {updated_eval['score']} [{updated_eval['label']}]"
        )

        # Auto-create notification when status changes to Resolved
        if status == "Resolved" and old_complaint and old_complaint.get("status") != "Resolved":
            citizen_id = old_complaint.get("citizen_id")
            complaint_title = old_complaint.get("title", f"Complaint #{cid}")
            if citizen_id:
                msg = f"✅ Your complaint '#{cid} — {complaint_title}' has been resolved!"
                if admin_remarks:
                    msg += f" Notes: {admin_remarks}"
                db.add_notification(citizen_id, cid, msg)

        return jsonify({"success": True, "message": "Complaint updated successfully."})
    return jsonify({"success": False, "message": "Failed to update complaint."}), 400


@app.route("/api/complaints/<int:cid>/solve-image", methods=["POST"])
def upload_solution_image(cid):
    """Officer uploads a proof-of-resolution image for a complaint."""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    img_file = request.files.get("solution_image")
    if not img_file:
        return jsonify({"success": False, "message": "No image file provided."}), 400

    fname = save_upload(img_file, UPLOAD_FOLDER_SOLUTION)
    if not fname:
        return jsonify({"success": False, "message": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp."}), 400

    db.update_complaint(cid, solution_image=fname, changed_by=session["user_id"])
    return jsonify({"success": True, "filename": fname, "message": "Solution image uploaded successfully."})

@app.route("/api/complaints/<int:cid>/complaint-image", methods=["POST"])
def upload_complaint_image(cid):
    """Upload or attach an issue photo to an existing complaint."""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    img_file = request.files.get("complaint_image") or request.files.get("image") or request.files.get("file")
    if not img_file:
        return jsonify({"success": False, "message": "No image file provided."}), 400

    fname = save_upload(img_file, UPLOAD_FOLDER_COMPLAINT)
    if not fname:
        return jsonify({"success": False, "message": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp, jfif, avif."}), 400

    db.update_complaint(cid, complaint_image=fname, changed_by=session["user_id"])
    return jsonify({"success": True, "filename": fname, "message": "Complaint image uploaded successfully."})

@app.route("/api/complaints/<int:cid>/history", methods=["GET"])
def get_complaint_history(cid):
    history = db.get_complaint_history(cid)
    complaint = db.get_complaint(cid)
    return jsonify({
        "complaint": dict(complaint) if complaint else None,
        "history": [dict(h) for h in history]
    })

# ─────────────────────────── Notifications APIs ───────────────────────────

@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    role = session.get("role")
    unread_only = request.args.get("unread_only") == "true"
    if role == "admin":
        notifs = db.get_all_notifications(unread_only=unread_only)
    else:
        notifs = db.get_citizen_notifications(session["user_id"], unread_only=unread_only)
    return jsonify([dict(n) for n in notifs])

@app.route("/api/notifications/count", methods=["GET"])
def get_notification_count():
    if "user_id" not in session:
        return jsonify({"count": 0})
    role = session.get("role")
    if role == "admin":
        count = db.get_unread_count()
    else:
        count = db.get_unread_count(citizen_id=session["user_id"])
    return jsonify({"count": count})

@app.route("/api/notifications/<int:nid>/read", methods=["PUT"])
def mark_notification_read(nid):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    db.mark_notification_read(nid)
    return jsonify({"success": True})

@app.route("/api/notifications/read-all", methods=["PUT"])
def mark_all_notifications_read():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    role = session.get("role")
    if role != "admin":
        db.mark_all_citizen_notifications_read(session["user_id"])
    return jsonify({"success": True})

# ─────────────────────────── Feedback & Profile ───────────────────────────

@app.route("/api/feedback", methods=["GET", "POST"])
def handle_feedback():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    if request.method == "POST":
        data = request.json or {}
        cid = data.get("complaint_id")
        rating = int(data.get("rating", 5))
        comments = data.get("comments", "").strip()

        fid = db.add_feedback(cid, session["user_id"], rating, comments)
        return jsonify({"success": True, "feedback_id": fid})

    feedbacks = db.get_citizen_feedback(session["user_id"])
    return jsonify([dict(f) for f in feedbacks])

@app.route("/api/profile", methods=["PUT"])
def update_profile():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.json or {}
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()
    password = data.get("password", "").strip()

    if name:
        db.update_user(session["user_id"], name=name, phone=phone, address=address)
        session["name"] = name
    if password:
        db.update_password(session["user_id"], password)

    return jsonify({"success": True, "message": "Profile updated successfully!"})

# ─────────────────────────── Admin & Stats APIs ───────────────────────────

@app.route("/api/stats", methods=["GET"])
def get_stats():
    role = session.get("role")
    if role == "department":
        dept = session.get("department", "Sanitation Department")
        stats = db.get_department_stats(dept)
    else:
        stats = db.get_stats()
        stats["by_category"] = [dict(c) for c in stats["by_category"]]
        stats["by_department"] = [dict(d) for d in stats["by_department"]]
    return jsonify(stats)

@app.route("/api/users", methods=["GET", "POST"])
def handle_users():
    if session.get("role") != "admin":
        return jsonify({"success": False, "message": "Forbidden"}), 403

    if request.method == "POST":
        data = request.json or {}
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()
        role = data.get("role", "department")
        department = data.get("department")

        if not name or not email or not password:
            return jsonify({"success": False, "message": "Name, email, and password are required."}), 400

        if role not in ["department", "admin"]:
            return jsonify({"success": False, "message": "Admin can only create Department Officer or Administrator accounts (not Citizen accounts)."}), 400

        # Check if email is already registered
        existing_user = db.get_user_by_email(email)
        if existing_user:
            return jsonify({"success": False, "message": f"An account with email '{email}' already exists."}), 400

        if role == "department" and not department:
            department = "Sanitation Department"

        uid = db.add_user(
            name=name,
            email=email,
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            password=password,
            role=role,
            department=department if role == "department" else None
        )
        if not uid:
            return jsonify({"success": False, "message": "Database error: Could not create user account."}), 500

        role_label = "Department Officer" if role == "department" else "Administrator"
        return jsonify({"success": True, "user_id": uid, "message": f"{role_label} account for '{name}' created successfully!"})

    role = request.args.get("role")
    users = db.get_all_users(role=role)
    return jsonify([dict(u) for u in users])

@app.route("/api/users/<int:uid>/status", methods=["PUT"])
def toggle_user_status(uid):
    if session.get("role") != "admin":
        return jsonify({"success": False, "message": "Forbidden"}), 403
    if uid == session.get("user_id"):
        return jsonify({"success": False, "message": "You cannot block or deactivate your own admin account!"}), 400

    data = request.json or {}
    status = data.get("status", "active")
    db.update_user(uid, status=status)
    return jsonify({"success": True, "message": f"User status set to {status}."})

@app.route("/api/users/<int:uid>/role", methods=["PUT"])
def change_user_role(uid):
    if session.get("role") != "admin":
        return jsonify({"success": False, "message": "Forbidden"}), 403
    if uid == session.get("user_id"):
        return jsonify({"success": False, "message": "You cannot change your own role!"}), 400

    data = request.json or {}
    new_role = data.get("role")
    department = data.get("department")

    if new_role not in ["citizen", "department", "admin"]:
        return jsonify({"success": False, "message": "Invalid role specified."}), 400

    update_kwargs = {"role": new_role}
    if new_role == "department":
        update_kwargs["department"] = department or "Sanitation Department"
    else:
        update_kwargs["department"] = None

    db.update_user(uid, **update_kwargs)
    return jsonify({"success": True, "message": f"User role updated to {new_role.capitalize()}."})

# ─────────────────────────── DSA Visual Lab APIs ───────────────────────────

@app.route("/api/dsa/queue", methods=["GET", "POST", "DELETE"])
def dsa_queue():
    action = request.args.get("action", "get")
    is_prio = request.args.get("priority_mode") == "true"
    target_q = live_p_queue if is_prio else live_queue

    if request.method == "POST":
        data = request.json or {}
        prio = data.get("priority", "Medium")
        cid = data.get("id") or 999
        item = {"id": cid, "title": data.get("title", "Civic Issue"), "priority": prio, "category": data.get("category", "General")}

        if is_prio:
            success = live_p_queue.enqueue(item, prio)
        else:
            success = live_queue.enqueue(item)
        return jsonify({"success": success, "size": len(target_q)})

    elif request.method == "DELETE":
        if action == "clear":
            target_q.clear()
            return jsonify({"success": True, "message": "Queue cleared."})
        item = target_q.dequeue()
        return jsonify({"success": True if item else False, "dequeued": item, "size": len(target_q)})

    # GET
    items = live_p_queue.display_items() if is_prio else live_queue.display()
    return jsonify({"items": items, "size": len(target_q), "max_size": target_q.max_size})

@app.route("/api/dsa/stack", methods=["GET", "POST", "DELETE"])
def dsa_stack():
    action = request.args.get("action", "get")
    if request.method == "POST":
        data = request.json or {}
        success = live_stack.push(data)
        return jsonify({"success": success, "size": live_stack.size()})
    elif request.method == "DELETE":
        if action == "clear":
            live_stack.clear()
            return jsonify({"success": True, "message": "Stack cleared."})
        popped = live_stack.pop()
        return jsonify({"success": True if popped else False, "popped": popped, "size": live_stack.size()})

    return jsonify({"items": live_stack.display(), "size": live_stack.size(), "max_size": live_stack.max_size})

@app.route("/api/dsa/linked_list", methods=["GET", "POST", "DELETE"])
def dsa_linked_list():
    action = request.args.get("action", "get")
    if request.method == "POST":
        data = request.json or {}
        pos = data.get("position", "end")
        item = {"id": data.get("id", 100), "title": data.get("title", "Complaint"), "category": data.get("category", "General")}
        if pos == "beginning":
            live_ll.insert_at_beginning(item)
        else:
            live_ll.insert_at_end(item)
        return jsonify({"success": True, "size": live_ll.size()})
    elif request.method == "DELETE":
        if action == "reverse":
            live_ll.reverse()
            return jsonify({"success": True, "message": "List reversed in-place."})
        elif action == "clear":
            live_ll.clear()
            return jsonify({"success": True, "message": "List cleared."})
        cid = int(request.args.get("id", 0))
        removed = live_ll.delete_by_id(cid)
        return jsonify({"success": True if removed else False, "removed": removed})

    # Get
    
    nodes = [n.data for n in live_ll.get_nodes()]
    return jsonify({"nodes": nodes, "size": live_ll.size()})

@app.route("/api/dsa/expression", methods=["POST"])
def dsa_expression():
    data = request.json or {}
    expr = data.get("expression", "( 3 + 5 ) * 2")
    postfix, steps = InfixPostfix.infix_to_postfix(expr)
    result, eval_steps = InfixPostfix.evaluate_postfix(postfix)
    return jsonify({
        "infix": expr,
        "postfix": postfix,
        "result": result,
        "steps": steps,
        "eval_steps": eval_steps
    })

@app.route("/api/dsa/iterative", methods=["POST"])
def dsa_iterative():
    data = request.json or {}
    algo = data.get("algorithm", "bubble_sort")
    arr = data.get("array", [45, 12, 85, 32, 89, 21, 67, 10, 53, 38])
    target = data.get("target", 67)

    if algo == "bubble_sort":
        sorted_arr, steps = IterativeAlgorithms.bubble_sort(arr)
        return jsonify({"sorted": sorted_arr, "steps": steps})
    elif algo == "selection_sort":
        sorted_arr, steps = IterativeAlgorithms.selection_sort(arr)
        return jsonify({"sorted": sorted_arr, "steps": steps})
    elif algo == "linear_search":
        idx, steps = IterativeAlgorithms.linear_search(arr, target)
        return jsonify({"index": idx, "steps": steps})
    elif algo == "binary_search":
        idx, steps = IterativeAlgorithms.binary_search(arr, target)
        return jsonify({"index": idx, "steps": steps})

    return jsonify({"error": "Unknown algorithm"}), 400

@app.route("/api/dsa/priority-score", methods=["POST"])
def dsa_priority_score():
    """
    Calculate complaint priority score using basic Infix to Postfix evaluation.

    Uses dsa/simple_infix_postfix.py — written from scratch with:
      - SimpleStack class (push, pop, peek)
      - infix_to_postfix()  : converts expression string step by step
      - evaluate_postfix()  : evaluates postfix using stack
      - calc_priority_score(): applies the above for complaints

    Formula (Infix): ( priority_weight * 3 + status_weight * 2 ) / 5
    Priority weights: High=3, Medium=2, Low=1
    Status weights:   Pending=3, In Progress=2, Approved=2, Resolved=1, Rejected=0
    """
    data = request.json or {}
    priority = data.get("priority", "Medium")
    status   = data.get("status",   "Pending")

    # Call the backend implementation
    result = backend_calc_priority_score(priority, status)

    return jsonify(result)


@app.route("/api/dsa/recursive", methods=["POST"])
def dsa_recursive():
    data = request.json or {}
    algo = data.get("algorithm", "factorial")
    n = int(data.get("n", 5))

    if algo == "factorial":
        res, steps = RecursiveAlgorithms.factorial(n)
        return jsonify({"result": res, "steps": steps})
    elif algo == "fibonacci":
        res, steps = RecursiveAlgorithms.fibonacci(n)
        return jsonify({"result": res, "steps": steps})
    elif algo == "merge_sort":
        arr = data.get("array", [38, 27, 43, 3, 9, 82, 10])
        res, steps = RecursiveAlgorithms.merge_sort(arr)
        return jsonify({"result": res, "steps": steps})
    elif algo == "quick_sort":
        arr = data.get("array", [10, 80, 30, 90, 40, 50, 70])
        res, steps = RecursiveAlgorithms.quick_sort(arr)
        return jsonify({"result": res, "steps": steps})

    return jsonify({"error": "Unknown algorithm"}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
