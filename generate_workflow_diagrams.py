"""
High-Resolution Workflow Diagram Generator for CivicSense Management System.
Generates:
  1. project_workflow_color.png  (Modern full-color architecture diagram)
  2. project_workflow_bw.png     (Clean high-contrast black & white diagram for reports/thesis)
Also copies them to the system artifact directory.
"""

import os
import math
import shutil
from PIL import Image, ImageDraw, ImageFont

WIDTH = 2400
HEIGHT = 2860

FONT_BOLD_TITLE = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR    = "C:/Windows/Fonts/segoeui.ttf"
FONT_MONO       = "C:/Windows/Fonts/consola.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def draw_arrow(draw, start, end, color, width=4, arrow_size=15, is_dashed=False):
    """Draw a vector line with an arrowhead at the target end."""
    x1, y1 = start
    x2, y2 = end
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist <= 0:
        return

    angle = math.atan2(y2 - y1, x2 - x1)
    base_x = x2 - arrow_size * math.cos(angle)
    base_y = y2 - arrow_size * math.sin(angle)

    if is_dashed:
        dash_len = 10
        gap_len = 6
        dx = (x2 - x1) / dist
        dy = (y2 - y1) / dist
        curr = 0
        limit = dist - arrow_size
        while curr < limit:
            step_end = min(curr + dash_len, limit)
            draw.line([(x1 + dx * curr, y1 + dy * curr), (x1 + dx * step_end, y1 + dy * step_end)], fill=color, width=width)
            curr += dash_len + gap_len
    else:
        draw.line([(x1, y1), (base_x, base_y)], fill=color, width=width)

    # Arrow head
    p1 = (x2, y2)
    p2 = (x2 - arrow_size * math.cos(angle - math.pi / 6), y2 - arrow_size * math.sin(angle - math.pi / 6))
    p3 = (x2 - arrow_size * math.cos(angle + math.pi / 6), y2 - arrow_size * math.sin(angle + math.pi / 6))
    draw.polygon([p1, p2, p3], fill=color)

def draw_bridge(draw, start, end, label, color, text_color, bg_color, is_bw=False):
    """Draw a horizontal connection bridge with a centered label badge."""
    x1, y1 = start
    x2, y2 = end
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2

    # Line
    draw_arrow(draw, (x1, y1), (x2, y2), color, width=3 if not is_bw else 4, arrow_size=14)

    # Label box
    f_badge = get_font(FONT_MONO, 14)
    # Estimate badge width
    w = len(label) * 9 + 20
    h = 24
    bx1 = mid_x - w // 2
    by1 = mid_y - h // 2
    bx2 = mid_x + w // 2
    by2 = mid_y + h // 2

    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=5, fill=bg_color, outline=color, width=1 if not is_bw else 2)
    draw.text((mid_x, mid_y), label, font=f_badge, fill=text_color, anchor="mm")

def draw_rounded_card(draw, rect, fill, border_color, border_width=2, radius=12):
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=border_color, width=border_width)

def render_diagram(mode="color"):
    is_bw = (mode == "bw")

    if is_bw:
        bg_color = (255, 255, 255)
        header_bg = (0, 0, 0)
        header_text = (255, 255, 255)
        sub_text = (230, 230, 230)
        lane_hdr_bg = [(0, 0, 0), (25, 25, 25), (45, 45, 45), (65, 65, 65)]
        lane_hdr_text = (255, 255, 255)
        lane_bg = [(255, 255, 255), (250, 250, 250), (255, 255, 255), (250, 250, 250)]
        card_fill = (255, 255, 255)
        card_border = (0, 0, 0)
        card_title_fill = (235, 235, 235)
        text_primary = (0, 0, 0)
        text_secondary = (50, 50, 50)
        badge_bg = (245, 245, 245)
        badge_border = (0, 0, 0)
        badge_text = (0, 0, 0)
        arrow_color = (0, 0, 0)
        table_hdr_bg = (0, 0, 0)
        table_hdr_text = (255, 255, 255)
        table_border = (0, 0, 0)
        table_row_alt = (242, 242, 242)
    else:
        bg_color = (248, 250, 252) # #f8fafc
        header_bg = (15, 23, 42)    # #0f172a
        header_text = (255, 255, 255)
        sub_text = (148, 163, 184) # #94a3b8
        lane_hdr_bg = [
            (30, 64, 175),  # Citizen - Blue #1e40af
            (67, 56, 202),  # Backend - Indigo #4338ca
            (5, 150, 105),  # Dept - Emerald #059669
            (180, 83, 9)    # Admin - Amber #b45309
        ]
        lane_hdr_text = (255, 255, 255)
        lane_bg = [
            (240, 249, 255), # #f0f9ff
            (245, 243, 255), # #f5f3ff
            (236, 253, 245), # #ecfdf5
            (255, 251, 235)  # #fffbeb
        ]
        card_fill = (255, 255, 255)
        card_border = (203, 213, 225)
        card_title_fill = (241, 245, 249)
        text_primary = (15, 23, 42)
        text_secondary = (71, 85, 105)
        badge_bg = (224, 231, 255)
        badge_border = (129, 140, 248)
        badge_text = (49, 46, 129)
        arrow_color = (30, 41, 59)
        table_hdr_bg = (30, 41, 59)
        table_hdr_text = (255, 255, 255)
        table_border = (203, 213, 225)
        table_row_alt = (241, 245, 249)

    img = Image.new("RGB", (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)

    # Fonts
    f_title_big   = get_font(FONT_BOLD_TITLE, 48)
    f_sub_title   = get_font(FONT_REGULAR, 23)
    f_lane_hdr    = get_font(FONT_BOLD_TITLE, 25)
    f_body        = get_font(FONT_REGULAR, 17)
    f_body_bold   = get_font(FONT_BOLD_TITLE, 17)
    f_mono_badge  = get_font(FONT_MONO, 15)
    f_tbl_hdr     = get_font(FONT_BOLD_TITLE, 18)
    f_tbl_body    = get_font(FONT_REGULAR, 16)

    # 1. Header Banner (y: 0 - 175)
    draw.rectangle([(0, 0), (WIDTH, 175)], fill=header_bg)
    draw.text((WIDTH//2, 45), "CIVICSENSE MANAGEMENT SYSTEM", font=f_title_big, fill=header_text, anchor="mm")
    tagline = "END-TO-END MUNICIPAL ARCHITECTURE & INTEGRATED DATA STRUCTURES WORKFLOW" if not is_bw else "PROJECT ARCHITECTURAL WORKFLOW DIAGRAM (PUBLICATION & THESIS BLACK & WHITE SPECIFICATION)"
    draw.text((WIDTH//2, 105), tagline, font=f_sub_title, fill=sub_text, anchor="mm")
    meta = "Full Lifecycle: Citizen Ingestion  ->  Algorithmic Dispatch  ->  Department Triage  ->  Administrative Governance"
    draw.text((WIDTH//2, 142), meta, font=get_font(FONT_MONO, 16), fill=(56, 189, 248) if not is_bw else (200, 200, 200), anchor="mm")

    # 2. Swimlanes Configuration
    lanes = [
        {"name": "1. CITIZEN PORTAL", "sub": "Reporting & Tracking UI", "color_idx": 0},
        {"name": "2. BACKEND CONTROLLER", "sub": "Flask API & DSA Routing", "color_idx": 1},
        {"name": "3. DEPARTMENT OPS", "sub": "Triage & Field Execution", "color_idx": 2},
        {"name": "4. ADMIN GOVERNANCE", "sub": "Master Oversight & BI", "color_idx": 3}
    ]

    margin_x = 55
    lane_gap = 26
    num_lanes = 4
    lane_width = (WIDTH - (2 * margin_x) - (num_lanes - 1) * lane_gap) // num_lanes
    lane_top = 210
    lane_bottom = 1600

    lane_rects = []
    for i, lane in enumerate(lanes):
        lx1 = margin_x + i * (lane_width + lane_gap)
        lx2 = lx1 + lane_width
        lane_rects.append((lx1, lx2))

        # Lane bounding column
        draw_rounded_card(draw, (lx1, lane_top, lx2, lane_bottom), lane_bg[i], (0, 0, 0) if is_bw else (226, 232, 240), border_width=2 if is_bw else 1, radius=12)

        # Lane Header Box
        draw_rounded_card(draw, (lx1, lane_top, lx2, lane_top + 75), lane_hdr_bg[i], (0, 0, 0) if is_bw else lane_hdr_bg[i], border_width=2 if is_bw else 1, radius=10)
        draw.text((lx1 + lane_width//2, lane_top + 26), lane["name"], font=f_lane_hdr, fill=lane_hdr_text, anchor="mm")
        draw.text((lx1 + lane_width//2, lane_top + 54), lane["sub"], font=get_font(FONT_REGULAR, 15), fill=(210, 230, 255) if not is_bw else (220, 220, 220), anchor="mm")

    # 3. Cards Definitions (y coordinates aligned per row)
    card_rows = [
        {"y": 310, "h": 185},
        {"y": 525, "h": 185},
        {"y": 740, "h": 185},
        {"y": 955, "h": 185},
        {"y": 1170, "h": 185},
        {"y": 1385, "h": 185}
    ]

    # Lane 1: Citizen Cards
    c_cards = [
        {
            "step": "STEP 1.1", "title": "Citizen Auth & Access",
            "lines": ["- Login / Registration endpoint", "- Role verification: 'citizen'", "- Pre-populated demo profiles"],
            "dsa": "Array / Hash Table Lookup"
        },
        {
            "step": "STEP 1.2", "title": "File Civic Grievance",
            "lines": ["- Category, Title & Description", "- Hazard Severity (High/Med/Low)", "- Upload photo proof to server"],
            "dsa": "Multipart Form / File Store"
        },
        {
            "step": "STEP 1.3", "title": "Urgency Score Preview",
            "lines": ["- Infix: (Priority*3 + Status*2)/5", "- Postfix stack-based evaluation", "- Dynamic urgency score (1 to 5)"],
            "dsa": "Stack (Shunting-Yard DSA)"
        },
        {
            "step": "STEP 1.4", "title": "Vehicle BFS Route View",
            "lines": ["- Shortest route from depot", "- Level-order traversal of zones", "- Live visual path highlighting"],
            "dsa": "Graph (BFS Shortest Path)"
        },
        {
            "step": "STEP 1.5", "title": "Sequential Ticket View",
            "lines": ["- Sequential Previous / Next view", "- Dynamic pointer traversal", "- Track resolution lifecycle"],
            "dsa": "Singly Linked List DSA"
        },
        {
            "step": "STEP 1.6", "title": "Citizen Rating & Feedback",
            "lines": ["- Unlocked upon 'Resolved' status", "- 1 to 5 Star municipal rating", "- Citizen satisfaction feedback"],
            "dsa": "Rating Aggregator Model"
        }
    ]

    # Lane 2: Backend Cards
    b_cards = [
        {
            "step": "STEP 2.1", "title": "Flask API Controller",
            "lines": ["- RESTful API routing layer", "- Session auth & request hygiene", "- Parameter parsing & validation"],
            "dsa": "Flask Web Micro-framework"
        },
        {
            "step": "STEP 2.2", "title": "Database Engine",
            "lines": ["- JSON file database engine", "- Optional MySQL connector", "- Atomic read/write transactions"],
            "dsa": "JSON / B-Tree File Record"
        },
        {
            "step": "STEP 2.3", "title": "Shunting-Yard Calculator",
            "lines": ["- Infix-to-postfix tokenizer", "- Operator precedence evaluation", "- Urgency score computation"],
            "dsa": "Stack Infix Engine (Phase 1)"
        },
        {
            "step": "STEP 2.4", "title": "Zonal Graph Engine",
            "lines": ["- City adjacency list & nodes", "- Depot (Chowk) to destination", "- Queue-based BFS exploration"],
            "dsa": "Graph Traversal (BFS & DFS)"
        },
        {
            "step": "STEP 2.5", "title": "Department Router",
            "lines": ["- Map issue category to Dept", "- Sanitation / Road / Water / etc.", "- Push ticket to Dept Priority Heap"],
            "dsa": "Category Dispatch Hash Table"
        },
        {
            "step": "STEP 2.6", "title": "State Machine & Audit",
            "lines": ["- State: Pending->In Progress->Done", "- Log timestamp & operator notes", "- Push previous state to undo stack"],
            "dsa": "Finite State Machine + Log"
        }
    ]

    # Lane 3: Department Cards
    d_cards = [
        {
            "step": "STEP 3.1", "title": "Officer Authentication",
            "lines": ["- Role: 'department'", "- Scope limited to assigned sector", "- 5 Zonal Officers (Road, Water...)"],
            "dsa": "Role-Based Access Control"
        },
        {
            "step": "STEP 3.2", "title": "Emergency Priority Queue",
            "lines": ["- Complaints queued by urgency", "- Max-Heap root holds top ticket", "- Immediate life-hazard priority"],
            "dsa": "Priority Queue (Max-Heap)"
        },
        {
            "step": "STEP 3.3", "title": "Greedy Task Scheduler",
            "lines": ["- Score: 0.4*Urg + 0.35*Sev + 0.25*Wait", "- Sorts eligible tickets O(N log N)", "- Optimal greedy selection next"],
            "dsa": "Greedy Algorithm (Phase 4)"
        },
        {
            "step": "STEP 3.4", "title": "Field Work & Resolution",
            "lines": ["- Dispatch crew & start repair", "- Transition state: 'In Progress'", "- Upload resolution photo proof"],
            "dsa": "Workflow Progression"
        },
        {
            "step": "STEP 3.5", "title": "LIFO Action Undo Stack",
            "lines": ["- Instant 1-click mistake rollback", "- Pops prior state from stack O(1)", "- Reverts accidental status shifts"],
            "dsa": "Stack LIFO Undo (Phase 1)"
        },
        {
            "step": "STEP 3.6", "title": "Department Analytics",
            "lines": ["- Daily resolved ticket count", "- Officer turnaround time metrics", "- Department backlog health index"],
            "dsa": "Iterative Metrics Aggregation"
        }
    ]

    # Lane 4: Admin Cards
    a_cards = [
        {
            "step": "STEP 4.1", "title": "Admin Authentication",
            "lines": ["- Role: 'admin' (Municipal HQ)", "- Full read/write CRUD privileges", "- Cross-department supervisory scope"],
            "dsa": "Central Supervisor Auth"
        },
        {
            "step": "STEP 4.2", "title": "KPI Master Dashboard",
            "lines": ["- Real-time counters: Total, Active", "- Pending vs. Resolved breakdown", "- High-priority emergency alerts"],
            "dsa": "O(N) Metric Aggregation"
        },
        {
            "step": "STEP 4.3", "title": "Binary Search Tree (BST)",
            "lines": ["- Fast O(log N) ticket lookup", "- Search by Complaint ID / Key", "- In-order sorted list generation"],
            "dsa": "Binary Search Tree (Phase 3)"
        },
        {
            "step": "STEP 4.4", "title": "Governance Hierarchy Tree",
            "lines": ["- Commissioner -> Zonal -> Dept", "- Pre/In/Post-order traversals", "- Models administrative ranks"],
            "dsa": "Binary Tree (Phase 3)"
        },
        {
            "step": "STEP 4.5", "title": "Zonal Graph Explorer",
            "lines": ["- City network BFS level-order view", "- DFS depth exploration of nodes", "- Area connectivity diagnostics"],
            "dsa": "Graph BFS / DFS Traversal"
        },
        {
            "step": "STEP 4.6", "title": "BI Analytics & Heatmaps",
            "lines": ["- Category-wise pie & bar charts", "- Problem-prone zonal heatmap", "- Citizen satisfaction ratings"],
            "dsa": "Statistical Analysis Engine"
        }
    ]

    all_lanes = [c_cards, b_cards, d_cards, a_cards]

    # Render Cards
    for lane_idx, cards in enumerate(all_lanes):
        lx1, lx2 = lane_rects[lane_idx]
        card_w = lx2 - lx1 - 28
        cx1 = lx1 + 14
        cx2 = cx1 + card_w

        for r_idx, c in enumerate(cards):
            cy1 = card_rows[r_idx]["y"]
            cy2 = cy1 + card_rows[r_idx]["h"]

            # Main Card Box
            draw_rounded_card(draw, (cx1, cy1, cx2, cy2), card_fill, (0, 0, 0) if is_bw else card_border, border_width=2 if is_bw else 1, radius=10)

            # Card Header Bar
            draw_rounded_card(draw, (cx1, cy1, cx2, cy1 + 38), card_title_fill if not is_bw else (230, 230, 230), (0, 0, 0) if is_bw else (226, 232, 240), border_width=1, radius=8)
            draw.text((cx1 + 12, cy1 + 19), c["step"], font=get_font(FONT_BOLD_TITLE, 14), fill=(30, 64, 175) if not is_bw else (0, 0, 0), anchor="lm")
            draw.text((cx1 + 84, cy1 + 19), c["title"], font=get_font(FONT_BOLD_TITLE, 17), fill=text_primary, anchor="lm")

            # Content Bullet Lines
            cur_y = cy1 + 48
            for line in c["lines"]:
                draw.text((cx1 + 16, cur_y), line, font=f_body, fill=text_secondary if not is_bw else (30, 30, 30))
                cur_y += 24

            # Bottom DSA Badge Pill
            badge_h = 28
            badge_y1 = cy2 - badge_h - 10
            badge_y2 = cy2 - 10
            badge_text_str = f"DSA: {c['dsa']}"
            draw_rounded_card(draw, (cx1 + 14, badge_y1, cx2 - 14, badge_y2), badge_bg, (0, 0, 0) if is_bw else badge_border, border_width=1, radius=6)
            draw.text((cx1 + card_w//2, badge_y1 + badge_h//2), badge_text_str, font=f_mono_badge, fill=badge_text, anchor="mm")

    # Vertical Flow Arrows between cards inside each lane
    for lane_idx in range(num_lanes):
        lx1, lx2 = lane_rects[lane_idx]
        cx = lx1 + (lx2 - lx1) // 2
        for r_idx in range(5):
            top_y = card_rows[r_idx]["y"] + card_rows[r_idx]["h"]
            btm_y = card_rows[r_idx+1]["y"]
            draw_arrow(draw, (cx, top_y + 4), (cx, btm_y - 4), arrow_color, width=3 if not is_bw else 4, arrow_size=12)

    # Cross-Lane Communication Bridges (Horizontal Arrows)
    # Bridge 1: Citizen 1.2 -> Backend 2.2 (Submit Ticket Payload)
    draw_bridge(draw, (lane_rects[0][1] - 14, 617), (lane_rects[1][0] + 14, 617), "HTTP POST /api/complaints", (2, 132, 199) if not is_bw else (0,0,0), (2, 132, 199) if not is_bw else (0,0,0), (255,255,255), is_bw)

    # Bridge 2: Backend 2.5 -> Dept 3.2 (Route to Department Heap)
    draw_bridge(draw, (lane_rects[1][1] - 14, 617), (lane_rects[2][0] + 14, 617), "Auto-Triage Max-Heap", (79, 70, 229) if not is_bw else (0,0,0), (79, 70, 229) if not is_bw else (0,0,0), (255,255,255), is_bw)

    # Bridge 3: Dept 3.4 -> Admin 4.2 (Status Updates & KPI)
    draw_bridge(draw, (lane_rects[2][1] - 14, 617), (lane_rects[3][0] + 14, 617), "Live KPI Sync", (217, 119, 6) if not is_bw else (0,0,0), (217, 119, 6) if not is_bw else (0,0,0), (255,255,255), is_bw)

    # Bridge 4: Citizen 1.6 Feedback -> Admin 4.6 Analytics
    draw_bridge(draw, (lane_rects[0][1] - 14, 1477), (lane_rects[3][0] + 14, 1477), "Citizen Star Rating & Review Stream (Feedback Loop)", (5, 150, 105) if not is_bw else (0,0,0), (5, 150, 105) if not is_bw else (0,0,0), (255,255,255), is_bw)

    # 4. DSA Specification Matrix Table (y: 1635 - 2290)
    tbl_top = 1635
    draw.rectangle([(margin_x, tbl_top), (WIDTH - margin_x, tbl_top + 50)], fill=table_hdr_bg)
    draw.text((WIDTH//2, tbl_top + 25), "CIVICSENSE DATA STRUCTURES & ALGORITHMS (DSA) SPECIFICATION MATRIX", font=f_lane_hdr, fill=table_hdr_text, anchor="mm")

    cols = [
        {"name": "DATA STRUCTURE / ALGORITHM", "w": 460},
        {"name": "CORE MECHANISM & LOGIC", "w": 490},
        {"name": "CIVICSENSE REAL-WORLD APPLICATION", "w": 720},
        {"name": "TIME COMPLEXITY", "w": 360},
        {"name": "COURSE PHASE", "w": 250}
    ]

    th_y1 = tbl_top + 50
    th_y2 = th_y1 + 45
    draw.rectangle([(margin_x, th_y1), (WIDTH - margin_x, th_y2)], fill=(45, 55, 72) if not is_bw else (220, 220, 220))

    cur_x = margin_x
    for col in cols:
        draw.text((cur_x + 12, th_y1 + 22), col["name"], font=f_tbl_hdr, fill=(255, 255, 255) if not is_bw else (0, 0, 0), anchor="lm")
        cur_x += col["w"]

    table_data = [
        ("1. Stack (Infix to Postfix)", "Shunting-Yard operator stack & post evaluation", "Dynamic urgency formula: (Priority*3 + Status*2) / 5", "O(N) tokens conversion", "Phase 1: Linear"),
        ("2. Singly Linked List", "Dynamic sequential Node pointers (prev / next)", "Citizen sequential complaint ticket browsing & history", "O(N) search / O(1) prepend", "Phase 1: Linear"),
        ("3. Priority Queue (Max-Heap)", "Binary Heap array: parent >= children", "Emergency hazard ordering: top priority tickets first", "O(log N) insert/pop", "Phase 1: Linear"),
        ("4. Action Stack (LIFO Undo)", "Last-In First-Out state transition storage", "1-Click undo rollback for mistaken status changes", "O(1) push and pop", "Phase 1: Linear"),
        ("5. Binary Search Tree (BST)", "Ordered Binary Tree: left < root <= right", "Admin fast complaint ticket lookup by ID and key", "O(log N) average search", "Phase 3: Hierarchical"),
        ("6. Binary Tree & Traversals", "Hierarchical tree nodes (Pre/In/Post-order)", "Municipal administrative governance hierarchy modeling", "O(N) full traversal", "Phase 3: Hierarchical"),
        ("7. Graph (BFS Shortest Path)", "Adjacency matrix/list + Queue level-order traversal", "Municipal vehicle routing from central depot to complaint zone", "O(V + E) shortest path", "Phase 3: Network"),
        ("8. Graph (DFS Traversal)", "Recursive / Stack-based deep branch search", "City sector connectivity diagnostics & isolated node check", "O(V + E) deep search", "Phase 3: Network"),
        ("9. Greedy Selection Model", "Multi-criteria normalized heuristic scoring", "Optimal task recommendation: 0.4*Urg + 0.35*Sev + 0.25*Wait", "O(N log N) sorting selection", "Phase 4: Optimization"),
        ("10. Iterative & Recursive Suites", "Loop structures vs. Divide-and-conquer calls", "Zonal complaint tallies, factorial weights, binary search", "O(N) iterative / O(log N) rec", "Phase 2: Procedural")
    ]

    row_h = 56
    row_y = th_y2
    for r_idx, row in enumerate(table_data):
        r_bg = (255, 255, 255) if (r_idx % 2 == 0) else (table_row_alt if not is_bw else (245, 245, 245))
        draw.rectangle([(margin_x, row_y), (WIDTH - margin_x, row_y + row_h)], fill=r_bg, outline=table_border if not is_bw else (0, 0, 0), width=1)

        cur_x = margin_x
        draw.text((cur_x + 12, row_y + row_h//2), row[0], font=f_body_bold, fill=text_primary, anchor="lm")
        cur_x += cols[0]["w"]

        draw.text((cur_x + 12, row_y + row_h//2), row[1], font=f_tbl_body, fill=text_secondary if not is_bw else (40, 40, 40), anchor="lm")
        cur_x += cols[1]["w"]

        draw.text((cur_x + 12, row_y + row_h//2), row[2], font=f_tbl_body, fill=text_primary, anchor="lm")
        cur_x += cols[2]["w"]

        draw.text((cur_x + 12, row_y + row_h//2), row[3], font=f_mono_badge, fill=(30, 64, 175) if not is_bw else (0, 0, 0), anchor="lm")
        cur_x += cols[3]["w"]

        draw.text((cur_x + 12, row_y + row_h//2), row[4], font=get_font(FONT_BOLD_TITLE, 14), fill=(180, 83, 9) if not is_bw else (0, 0, 0), anchor="lm")
        row_y += row_h

    draw.rectangle([(margin_x, tbl_top), (WIDTH - margin_x, row_y)], outline=(0, 0, 0) if is_bw else (71, 85, 105), width=2)

    # 5. Summary & Lifecycle Notes Card (y: 2325 - 2740)
    notes_top = 2325
    notes_bottom = 2740
    draw_rounded_card(draw, (margin_x, notes_top, WIDTH - margin_x, notes_bottom), (255, 255, 255) if is_bw else (241, 245, 249), (0, 0, 0) if is_bw else (203, 213, 225), border_width=2 if is_bw else 1, radius=12)

    draw.text((margin_x + 30, notes_top + 35), "SYSTEM DESIGN & WORKFLOW LIFECYCLE SUMMARY", font=get_font(FONT_BOLD_TITLE, 22), fill=text_primary, anchor="lm")

    summary_bullets = [
        "1. Ingestion & Pre-Processing: Citizens submit complaints via Web/GUI. The system validates payload and calculates dynamic urgency using Shunting-Yard Infix->Postfix.",
        "2. Dispatch & Routing: Graph BFS establishes the shortest logistical transit route between the central municipal depot (Chowk) and the hazard zone.",
        "3. Department Triage: Department Officers process incoming tickets through a Max-Heap Priority Queue and Greedy Optimization Scheduler (scoring urgency, severity, wait time).",
        "4. Execution & Rollback: Officers inspect sites, start works, upload resolution images, and utilize the LIFO Undo Action Stack to roll back erroneous state transitions.",
        "5. Governance & BI: Administrators navigate the Municipal Hierarchy Tree, search complaints via BST in O(log N), and monitor real-time city health via the analytics dashboard."
    ]

    b_y = notes_top + 80
    for b in summary_bullets:
        draw.text((margin_x + 30, b_y), b, font=get_font(FONT_REGULAR, 18), fill=text_secondary if not is_bw else (20, 20, 20), anchor="lm")
        b_y += 55

    # 6. Footer Text
    foot_y = 2800
    footer_text = "CivicSense Management System | Academic Project Specification | Python, CustomTkinter, Flask, MySQL/JSON Architecture"
    draw.text((WIDTH//2, foot_y), footer_text, font=get_font(FONT_REGULAR, 16), fill=(100, 116, 139) if not is_bw else (80, 80, 80), anchor="mm")

    out_filename = "project_workflow_color.png" if not is_bw else "project_workflow_bw.png"
    img.save(out_filename, "PNG", dpi=(300, 300))
    print(f"Successfully generated: {out_filename}")

    # Copy to artifact directory
    art_dir = r"C:\Users\01\.gemini\antigravity\brain\857430ef-5c93-463d-bef8-01f8e4014854"
    if os.path.exists(art_dir):
        dest_path = os.path.join(art_dir, out_filename)
        shutil.copy2(out_filename, dest_path)
        print(f"Copied to artifact dir: {dest_path}")

if __name__ == "__main__":
    render_diagram(mode="color")
    render_diagram(mode="bw")
