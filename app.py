"""
Flask Web Application for CivicSense — Civic Complaint Management & DSA Platform.
Provides both Web UI (HTML/CSS/JS with glassmorphism & animations) and REST APIs connecting to SQLite & Python DSA modules.
"""

# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify, session, redirect
from database.database import Database
from dsa.linked_list import LinkedList
from dsa.stack import Stack
from dsa.queue import Queue, PriorityQueue
from dsa.infix_postfix import InfixPostfix
from dsa.iterative import IterativeAlgorithms
from dsa.recursive import RecursiveAlgorithms

app = Flask(__name__)
app.secret_key = "civicsense_super_secret_phase1_key"

# Database Singleton
db = Database()

# In-memory DSA instances for live interactive visual lab
live_queue = Queue(max_size=10)
live_p_queue = PriorityQueue(max_size=10)
live_stack = Stack(max_size=8)
live_ll = LinkedList()

# ─────────────────────────── Page Routes ───────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
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
    return render_template("citizen.html", user=dict(user))

@app.route("/admin")
def admin_page():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/")
    user = db.get_user_by_id(session["user_id"])
    return render_template("admin.html", user=dict(user))

@app.route("/department")
def department_page():
    if "user_id" not in session or session.get("role") != "department":
        return redirect("/")
    user = db.get_user_by_id(session["user_id"])
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
        session["department"] = user["department"]
        return jsonify({"success": True, "role": user["role"], "user": dict(user)})
    return jsonify({"success": False, "message": "Invalid email, password, or role."}), 401

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()
    password = data.get("password", "").strip()

    if not name or not email or not password:
        return jsonify({"success": False, "message": "All required fields must be filled."}), 400

    uid = db.add_user(name, email, phone, address, password, "citizen")
    if uid:
        return jsonify({"success": True, "message": "Account created successfully! Please login."})
    return jsonify({"success": False, "message": "Email address already registered."}), 400

# ─────────────────────────── Complaints APIs ───────────────────────────

@app.route("/api/complaints", methods=["GET"])
def get_complaints():
    status = request.args.get("status")
    category = request.args.get("category")
    role = session.get("role")
    user_id = session.get("user_id")

    if role == "citizen":
        complaints = db.get_citizen_complaints(user_id)
    elif role == "department":
        dept_name = session.get("department", "Sanitation Department")
        complaints = db.get_department_complaints(dept_name)
    else:
        complaints = db.get_all_complaints(status=status, category=category)

    return jsonify([dict(c) for c in complaints])

@app.route("/api/complaints", methods=["POST"])
def submit_complaint():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.json or {}
    title = data.get("title", "").strip()
    category = data.get("category", "Garbage")
    location = data.get("location", "").strip()
    priority = data.get("priority", "Medium")
    description = data.get("description", "").strip()

    if not title or not location:
        return jsonify({"success": False, "message": "Title and location are required."}), 400

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

    cid = db.add_complaint(
        citizen_id=session["user_id"],
        title=title,
        description=description,
        category=category,
        location=location,
        priority=priority
    )
    db.update_complaint(cid, department=dept)

    # Also update in-memory DSA linked list and queue
    comp_dict = {"id": cid, "title": title, "category": category, "location": location, "priority": priority, "status": "Pending"}
    live_ll.insert_at_beginning(comp_dict)
    live_queue.enqueue(comp_dict)
    live_p_queue.enqueue(comp_dict, priority)
    live_stack.push({"id": cid, "action": f"Submitted #{cid} ({title})", "status": "Pending"})

    return jsonify({"success": True, "complaint_id": cid, "message": f"Complaint #{cid} registered successfully!"})

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

    if not updates:
        return jsonify({"success": False, "message": "Nothing to update."}), 400

    auto_remark = remarks or (
        f"Assigned to {officer_name} | Status: {status}" if officer_name
        else f"Status updated to {status or 'unchanged'}"
    )

    success = db.update_complaint(
        cid,
        changed_by=session["user_id"],
        remarks=auto_remark,
        **updates
    )
    if success:
        live_stack.push({"id": cid, "action": f"Updated #{cid} -> {status or 'Modified'}", "status": status or "Modified"})
        return jsonify({"success": True, "message": "Complaint updated successfully."})
    return jsonify({"success": False, "message": "Failed to update complaint."}), 400

@app.route("/api/complaints/<int:cid>/history", methods=["GET"])
def get_complaint_history(cid):
    history = db.get_complaint_history(cid)
    complaint = db.get_complaint(cid)
    return jsonify({
        "complaint": dict(complaint) if complaint else None,
        "history": [dict(h) for h in history]
    })

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
        uid = db.add_user(
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            password=data.get("password"),
            role=data.get("role", "citizen"),
            department=data.get("department")
        )
        return jsonify({"success": True if uid else False, "user_id": uid})

    role = request.args.get("role")
    users = db.get_all_users(role=role)
    return jsonify([dict(u) for u in users])

@app.route("/api/users/<int:uid>/status", methods=["PUT"])
def toggle_user_status(uid):
    if session.get("role") != "admin":
        return jsonify({"success": False, "message": "Forbidden"}), 403
    data = request.json or {}
    status = data.get("status", "active")
    db.update_user(uid, status=status)
    return jsonify({"success": True})

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
