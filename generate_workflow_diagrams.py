"""
Script to generate high-resolution Color and Black-and-White Workflow Diagrams
for CivicSense Management System.
Outputs:
  - project_workflow_color.png
  - project_workflow_bw.png
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

WIDTH = 2400
HEIGHT = 3200

# Fonts
FONT_BOLD_TITLE = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR    = "C:/Windows/Fonts/segoeui.ttf"
FONT_MONO       = "C:/Windows/Fonts/consola.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def draw_arrow(draw, start, end, color, width=4, arrow_size=16, is_dashed=False):
    """Draw a line with an arrowhead at the end."""
    x1, y1 = start
    x2, y2 = end
    
    if is_dashed:
        # Draw dashed line
        total_dist = math.hypot(x2 - x1, y2 - y1)
        dash_len = 12
        gap_len = 8
        if total_dist > 0:
            dx = (x2 - x1) / total_dist
            dy = (y2 - y1) / total_dist
            curr = 0
            while curr < total_dist - arrow_size:
                step_end = min(curr + dash_len, total_dist - arrow_size)
                draw.line([(x1 + dx * curr, y1 + dy * curr), (x1 + dx * step_end, y1 + dy * step_end)], fill=color, width=width)
                curr += dash_len + gap_len
    else:
        # Draw solid line up to arrow head base
        angle = math.atan2(y2 - y1, x2 - x1)
        base_x = x2 - arrow_size * math.cos(angle)
        base_y = y2 - arrow_size * math.sin(angle)
        draw.line([(x1, y1), (base_x, base_y)], fill=color, width=width)

    # Arrow head
    angle = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2, y2)
    p2 = (x2 - arrow_size * math.cos(angle - math.pi / 6), y2 - arrow_size * math.sin(angle - math.pi / 6))
    p3 = (x2 - arrow_size * math.cos(angle + math.pi / 6), y2 - arrow_size * math.sin(angle + math.pi / 6))
    draw.polygon([p1, p2, p3], fill=color)

def draw_rounded_card(draw, rect, fill, border_color, border_width=2, radius=12):
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=border_color, width=border_width)

def render_diagram(mode="color"):
    is_bw = (mode == "bw")
    
    # Palette configuration
    if is_bw:
        bg_color = (255, 255, 255)
        header_bg = (0, 0, 0)
        header_text = (255, 255, 255)
        sub_text = (220, 220, 220)
        lane_hdr_bg = [(20, 20, 20), (40, 40, 40), (60, 60, 60), (80, 80, 80)]
        lane_hdr_text = (255, 255, 255)
        lane_bg = [(250, 250, 250), (245, 245, 245), (250, 250, 250), (245, 245, 245)]
        card_fill = (255, 255, 255)
        card_border = (0, 0, 0)
        card_title_fill = (235, 235, 235)
        text_primary = (0, 0, 0)
        text_secondary = (60, 60, 60)
        badge_bg = (240, 240, 240)
        badge_border = (0, 0, 0)
        badge_text = (0, 0, 0)
        arrow_color = (0, 0, 0)
        table_hdr_bg = (0, 0, 0)
        table_hdr_text = (255, 255, 255)
        table_border = (0, 0, 0)
        table_row_alt = (245, 245, 245)
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

    # Load fonts
    f_title_big   = get_font(FONT_BOLD_TITLE, 52)
    f_sub_title   = get_font(FONT_REGULAR, 24)
    f_lane_hdr    = get_font(FONT_BOLD_TITLE, 26)
    f_card_title  = get_font(FONT_BOLD_TITLE, 22)
    f_body        = get_font(FONT_REGULAR, 18)
    f_body_bold   = get_font(FONT_BOLD_TITLE, 18)
    f_mono_badge  = get_font(FONT_MONO, 16)
    f_tbl_hdr     = get_font(FONT_BOLD_TITLE, 19)
    f_tbl_body    = get_font(FONT_REGULAR, 17)

    # 1. Header Banner
    draw.rectangle([(0, 0), (WIDTH, 170)], fill=header_bg)
    draw.text((WIDTH//2, 45), "CIVICSENSE MANAGEMENT SYSTEM", font=f_title_big, fill=header_text, anchor="mm")
    tagline = "END-TO-END MUNICIPAL ARCHITECTURE & INTEGRATED DATA STRUCTURES WORKFLOW" if not is_bw else "SYSTEM WORKFLOW & ARCHITECTURE DIAGRAM (PRINT SPECIFICATION / BLACK & WHITE)"
    draw.text((WIDTH//2, 105), tagline, font=f_sub_title, fill=sub_text, anchor="mm")
    meta = "Full Lifecycle: Citizen Ingestion  ->  Algorithmic Dispatch  ->  Department Triage  ->  Administrative Governance"
    draw.text((WIDTH//2, 140), meta, font=get_font(FONT_MONO, 16), fill=(56, 189, 248) if not is_bw else (200, 200, 200), anchor="mm")

    # Layout Parameters for 4 Swimlanes
    lanes = [
        {"name": "1. CITIZEN PORTAL", "sub": "Reporting & Tracking UI", "color_idx": 0},
        {"name": "2. BACKEND & DISPATCH ENGINE", "sub": "Flask API & DSA Routing", "color_idx": 1},
        {"name": "3. DEPARTMENT OPERATIONS", "sub": "Triage & Field Execution", "color_idx": 2},
        {"name": "4. ADMIN GOVERNANCE", "sub": "Master Oversight & BI", "color_idx": 3}
    ]

    margin_x = 60
    lane_gap = 28
    num_lanes = 4
    lane_width = (WIDTH - (2 * margin_x) - (num_lanes - 1) * lane_gap) // num_lanes
    lane_top = 205
    lane_bottom = 2460

    # Draw Swimlane Backgrounds & Headers
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
        draw.text((lx1 + lane_width//2, lane_top + 54), lane["sub"], font=get_font(FONT_REGULAR, 16), fill=(200, 220, 245) if not is_bw else (210, 210, 210), anchor="mm")

    # Define Cards in each Lane
    # Lane 1: Citizen (5 steps)
    c_cards = [
        {
            "step": "Step 1.1",
            "title": "Citizen Auth & Access",
            "lines": ["- Login / Register account", "- Role check: role == 'citizen'", "- Pre-populated demo accounts"],
            "dsa": "Array / Hash Table Lookup",
            "y": 305, "h": 165
        },
        {
            "step": "Step 1.2",
            "title": "File Civic Grievance",
            "lines": ["- Form: Category, Title, Detail", "- Hazard severity & Location Zone", "- Upload photo proof to server"],
            "dsa": "Multipart Form / File Store",
            "y": 500, "h": 170
        },
        {
            "step": "Step 1.3",
            "title": "Algorithmic Urgency Preview",
            "lines": ["- Infix: (Priority*3 + Status*2)/5", "- Postfix stack-based evaluation", "- Generates numeric urgency 1-5"],
            "dsa": "Stack (Shunting-Yard DSA)",
            "y": 700, "h": 175
        },
        {
            "step": "Step 1.4",
            "title": "Vehicle BFS Route Preview",
            "lines": ["- Computes shortest depot route", "- Level-order traversal across zones", "- Visual route display on map"],
            "dsa": "Graph (BFS Shortest Path)",
            "y": 905, "h": 175
        },
        {
            "step": "Step 1.5",
            "title": "Ticket Browsing & History",
            "lines": ["- Sequential Previous / Next view", "- Dynamic pointer traversal", "- Citizen track ticket status"],
            "dsa": "Singly Linked List DSA",
            "y": 1110, "h": 170
        },
        {
            "step": "Step 1.6",
            "title": "Citizen Feedback & Rating",
            "lines": ["- Unlocks when status = 'Resolved'", "- 1 to 5 Star municipal rating", "- Citizen comments & validation"],
            "dsa": "Rating Aggregator Model",
            "y": 1310, "h": 170
        }
    ]

    # Lane 2: Backend Controller & Dispatch (5 steps)
    b_cards = [
        {
            "step": "Step 2.1",
            "title": "Flask API Controller",
            "lines": ["- Restful API endpoint handlers", "- Session management & auth tokens", "- Request sanitation & validation"],
            "dsa": "Flask Web Micro-framework",
            "y": 305, "h": 165
        },
        {
            "step": "Step 2.2",
            "title": "Database Persistence",
            "lines": ["- JSON file database engine", "- Optional MySQL connector", "- Atomic read/write transactions"],
            "dsa": "JSON / B-Tree File Record",
            "y": 500, "h": 170
        },
        {
            "step": "Step 2.3",
            "title": "Shunting-Yard Calculator",
            "lines": ["- Infix-to-postfix tokenizer", "- Operator precedence evaluation", "- Urgency score computation"],
            "dsa": "Stack Infix Engine (Phase 1)",
            "y": 700, "h": 175
        },
        {
            "step": "Step 2.4",
            "title": "Zonal Graph Engine",
            "lines": ["- City adjacency list & nodes", "- Depot (Chowk) to destination", "- Queue-based BFS exploration"],
            "dsa": "Graph Traversal (BFS & DFS)",
            "y": 905, "h": 175
        },
        {
            "step": "Step 2.5",
            "title": "Department Router",
            "lines": ["- Map issue category to Dept", "- Sanitation / Road / Water / etc.", "- Push ticket to Dept Priority Heap"],
            "dsa": "Category Dispatch Hash Table",
            "y": 1110, "h": 170
        },
        {
            "step": "Step 2.6",
            "title": "State Machine & Audit",
            "lines": ["- State: Pending->In Progress->Done", "- Log timestamp & operator notes", "- Push previous state to undo stack"],
            "dsa": "Finite State Machine + Log",
            "y": 1310, "h": 170
        }
    ]

    # Lane 3: Department Operations (6 steps)
    d_cards = [
        {
            "step": "Step 3.1",
            "title": "Officer Authentication",
            "lines": ["- Role: 'department'", "- Scope limited to assigned sector", "- 5 Zonal Officers (Road, Water...)"],
            "dsa": "Role-Based Access Control",
            "y": 305, "h": 165
        },
        {
            "step": "Step 3.2",
            "title": "Emergency Priority Queue",
            "lines": ["- Complaints queued by urgency", "- Max-Heap root holds top ticket", "- Immediate life-hazard priority"],
            "dsa": "Priority Queue (Max-Heap)",
            "y": 500, "h": 170
        },
        {
            "step": "Step 3.3",
            "title": "Greedy Task Scheduler",
            "lines": ["- Score: 0.4*Urg + 0.35*Sev + 0.25*Wait", "- Sorts eligible tickets O(N log N)", "- Optimal greedy selection next"],
            "dsa": "Greedy Algorithm (Phase 4)",
            "y": 700, "h": 175
        },
        {
            "step": "Step 3.4",
            "title": "Field Work & Resolution",
            "lines": ["- Dispatch crew & start repair", "- Transition state: 'In Progress'", "- Upload resolution photo proof"],
            "dsa": "Workflow Progression",
            "y": 905, "h": 175
        },
        {
            "step": "Step 3.5",
            "title": "LIFO Action Undo Stack",
            "lines": ["- Instant 1-click mistake rollback", "- Pops prior state from stack O(1)", "- Reverts accidental status shifts"],
            "dsa": "Stack LIFO Undo (Phase 1)",
            "y": 1110, "h": 170
        },
        {
            "step": "Step 3.6",
            "title": "Department Analytics",
            "lines": ["- Daily resolved ticket count", "- Officer turnaround time metrics", "- Department backlog health index"],
            "dsa": "Iterative Metrics Aggregation",
            "y": 1310, "h": 170
        }
    ]

    # Lane 4: Admin Governance (6 steps)
    a_cards = [
        {
            "step": "Step 4.1",
            "title": "Admin Authentication",
            "lines": ["- Role: 'admin' (Municipal HQ)", "- Full read/write CRUD privileges", "- Cross-department supervisory scope"],
            "dsa": "Central Supervisor Auth",
            "y": 305, "h": 165
        },
        {
            "step": "Step 4.2",
            "title": "KPI Master Dashboard",
            "lines": ["- Real-time counters: Total, Active", "- Pending vs. Resolved breakdown", "- High-priority emergency alerts"],
            "dsa": "O(N) Metric Aggregation",
            "y": 500, "h": 170
        },
        {
            "step": "Step 4.3",
            "title": "Binary Search Tree (BST)",
            "lines": ["- Fast O(log N) ticket lookup", "- Search by Complaint ID / Key", "- In-order sorted list generation"],
            "dsa": "Binary Search Tree (Phase 3)",
            "y": 700, "h": 175
        },
        {
            "step": "Step 4.4",
            "title": "Governance Hierarchy Tree",
            "lines": ["- Commissioner -> Zonal -> Dept", "- Pre/In/Post-order traversals", "- Models administrative ranks"],
            "dsa": "Binary Tree (Phase 3)",
            "y": 905, "h": 175
        },
        {
            "step": "Step 4.5",
            "title": "Zonal Graph Explorer",
            "lines": ["- City network BFS level-order view", "- DFS depth exploration of nodes", "- Area connectivity diagnostics"],
            "dsa": "Graph BFS / DFS Traversal",
            "y": 1110, "h": 170
        },
        {
            "step": "Step 4.6",
            "title": "BI Analytics & Heatmaps",
            "lines": ["- Category-wise pie & bar charts", "- Problem-prone zonal heatmap", "- Citizen satisfaction ratings"],
            "dsa": "Statistical Analysis Engine",
            "y": 1310, "h": 170
        }
    ]

    all_lanes_cards = [c_cards, b_cards, d_cards, a_cards]

    # Draw all cards
    for lane_idx, cards in enumerate(all_lanes_cards):
        lx1, lx2 = lane_rects[lane_idx]
        card_w = lx2 - lx1 - 32
        cx1 = lx1 + 16
        cx2 = cx1 + card_w

        for c in cards:
            cy1 = c["y"]
            cy2 = cy1 + c["h"]

            # Card box
            draw_rounded_card(draw, (cx1, cy1, cx2, cy2), card_fill, card_border if not is_bw else (0, 0, 0), border_width=2 if is_bw else 1, radius=10)

            # Card Header Bar
            draw_rounded_card(draw, (cx1, cy1, cx2, cy1 + 38), card_title_fill if not is_bw else (225, 225, 225), (0, 0, 0) if is_bw else (226, 232, 240), border_width=1, radius=8)
            draw.text((cx1 + 12, cy1 + 19), c["step"], font=get_font(FONT_BOLD_TITLE, 14), fill=(30, 64, 175) if not is_bw else (0, 0, 0), anchor="lm")
            draw.text((cx1 + 80, cy1 + 19), c["title"], font=get_font(FONT_BOLD_TITLE, 17), fill=text_primary, anchor="lm")

            # Content lines
            cur_y = cy1 + 48
            for line in c["lines"]:
                draw.text((cx1 + 16, cur_y), line, font=f_body, fill=text_secondary if not is_bw else (30, 30, 30))
                cur_y += 24

            # DSA Badge Pill at bottom of card
            badge_h = 26
            badge_y1 = cy2 - badge_h - 10
            badge_y2 = cy2 - 10
            badge_text_str = f"DSA: {c['dsa']}"
            draw_rounded_card(draw, (cx1 + 14, badge_y1, cx2 - 14, badge_y2), badge_bg, badge_border if not is_bw else (0, 0, 0), border_width=1, radius=6)
            draw.text((cx1 + card_w//2, badge_y1 + badge_h//2), badge_text_str, font=f_mono_badge, fill=badge_text, anchor="mm")

    # Connectors within lanes (Vertical Downward Arrows)
    for lane_idx, cards in enumerate(all_lanes_cards):
        lx1, lx2 = lane_rects[lane_idx]
        cx = lx1 + (lx2 - lx1) // 2
        for i in range(len(cards) - 1):
            top_card_bottom = cards[i]["y"] + cards[i]["h"]
            next_card_top = cards[i+1]["y"]
            draw_arrow(draw, (cx, top_card_bottom + 4), (cx, next_card_top - 4), arrow_color, width=3 if not is_bw else 4, arrow_size=12)

    # Cross-Lane Arrows (Interaction & Data Pipelines)
    # 1. Citizen files grievance (Step 1.2) -> Backend Controller (Step 2.1)
    draw_arrow(draw, (lane_rects[0][1] - 16, 585), (lane_rects[1][0] + 16, 585), (2, 132, 199) if not is_bw else (0, 0, 0), width=4, arrow_size=14)

    # 2. Backend Shunting-Yard (Step 2.3) -> Dept Emergency Heap (Step 3.2)
    draw_arrow(draw, (lane_rects[1][1] - 16, 785), (lane_rects[2][0] + 16, 785), (79, 70, 229) if not is_bw else (0, 0, 0), width=4, arrow_size=14)

    # 3. Dept Greedy Scheduler (Step 3.3) -> Field Work Execution (Step 3.4)
    # 4. Dept Field Work Resolved (Step 3.4) -> Citizen Feedback (Step 1.6) [Feedback Loop Across]
    # Draw long curved/routed arrow from Dept 3.4 to Citizen 1.6
    pts_feedback = [
        (lane_rects[2][0] + 16, 1020),
        (lane_rects[1][0] - 20, 1020),
        (lane_rects[1][0] - 20, 1390),
        (lane_rects[0][1] - 16, 1390)
    ]
    # Draw dashed feedback loop
    draw_arrow(draw, (lane_rects[2][0] + 16, 1000), (lane_rects[1][1] - 16, 1000), (5, 150, 105) if not is_bw else (0, 0, 0), width=3, arrow_size=12, is_dashed=True)
    draw_arrow(draw, (lane_rects[1][0] + 16, 1000), (lane_rects[0][1] - 16, 1370), (5, 150, 105) if not is_bw else (0, 0, 0), width=3, arrow_size=12, is_dashed=True)

    # 5. Backend DB & Audit (Step 2.6) -> Admin KPI & BST Search (Step 4.2 / 4.3)
    draw_arrow(draw, (lane_rects[2][1] - 16, 585), (lane_rects[3][0] + 16, 585), (217, 119, 6) if not is_bw else (0, 0, 0), width=4, arrow_size=14)
    draw_arrow(draw, (lane_rects[2][1] - 16, 785), (lane_rects[3][0] + 16, 785), (217, 119, 6) if not is_bw else (0, 0, 0), width=4, arrow_size=14)

    # Draw Section Banner for DSA Specification Table
    tbl_top = 1520
    draw.rectangle([(margin_x, tbl_top), (WIDTH - margin_x, tbl_top + 50)], fill=table_hdr_bg)
    draw.text((WIDTH//2, tbl_top + 25), "CIVICSENSE DATA STRUCTURES & ALGORITHMS (DSA) SPECIFICATION MATRIX", font=f_lane_hdr, fill=table_hdr_text, anchor="mm")

    # Table columns: DSA Name, Type / Mechanism, Application in CivicSense, Time Complexity, Phase
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

    row_h = 58
    row_y = th_y2
    for r_idx, row in enumerate(table_data):
        r_bg = (255, 255, 255) if (r_idx % 2 == 0) else (table_row_alt if not is_bw else (245, 245, 245))
        draw.rectangle([(margin_x, row_y), (WIDTH - margin_x, row_y + row_h)], fill=r_bg, outline=table_border if not is_bw else (0, 0, 0), width=1)
        
        cur_x = margin_x
        # Col 0: Bold name
        draw.text((cur_x + 12, row_y + row_h//2), row[0], font=f_body_bold, fill=text_primary, anchor="lm")
        cur_x += cols[0]["w"]

        # Col 1: Mechanism
        draw.text((cur_x + 12, row_y + row_h//2), row[1], font=f_tbl_body, fill=text_secondary if not is_bw else (40, 40, 40), anchor="lm")
        cur_x += cols[1]["w"]

        # Col 2: Application
        draw.text((cur_x + 12, row_y + row_h//2), row[2], font=f_tbl_body, fill=text_primary, anchor="lm")
        cur_x += cols[2]["w"]

        # Col 3: Complexity (Monospace)
        draw.text((cur_x + 12, row_y + row_h//2), row[3], font=f_mono_badge, fill=(30, 64, 175) if not is_bw else (0, 0, 0), anchor="lm")
        cur_x += cols[3]["w"]

        # Col 4: Phase Badge
        draw.text((cur_x + 12, row_y + row_h//2), row[4], font=get_font(FONT_BOLD_TITLE, 14), fill=(180, 83, 9) if not is_bw else (0, 0, 0), anchor="lm")

        row_y += row_h

    # Outer border for the table
    draw.rectangle([(margin_x, tbl_top), (WIDTH - margin_x, row_y)], outline=(0, 0, 0) if is_bw else (71, 85, 105), width=2)

    # Bottom Architecture Summary & Notes Box
    notes_top = row_y + 28
    notes_bottom = notes_top + 340
    draw_rounded_card(draw, (margin_x, notes_top, WIDTH - margin_x, notes_bottom), (255, 255, 255) if is_bw else (241, 245, 249), (0, 0, 0) if is_bw else (203, 213, 225), border_width=2 if is_bw else 1, radius=12)

    draw.text((margin_x + 30, notes_top + 35), "SYSTEM DESIGN & WORKFLOW LIFECYCLE SUMMARY", font=get_font(FONT_BOLD_TITLE, 22), fill=text_primary, anchor="lm")

    summary_bullets = [
        "1. Ingestion & Pre-Processing: Citizens submit complaints via Web/GUI. The system validates payload and calculates dynamic urgency using Shunting-Yard Infix->Postfix.",
        "2. Dispatch & Routing: Graph BFS establishes the shortest logistical transit route between the central municipal depot (Chowk) and the hazard zone.",
        "3. Department Triage: Department Officers process incoming tickets through a Max-Heap Priority Queue and Greedy Optimization Scheduler (scoring urgency, severity, wait time).",
        "4. Execution & Rollback: Officers inspect sites, start works, upload resolution images, and utilize the LIFO Undo Action Stack to roll back erroneous state transitions.",
        "5. Governance & BI: Administrators navigate the Municipal Hierarchy Tree, search complaints via BST in O(log N), and monitor real-time city health via the analytics dashboard."
    ]

    b_y = notes_top + 75
    for b in summary_bullets:
        draw.text((margin_x + 30, b_y), b, font=get_font(FONT_REGULAR, 18), fill=text_secondary if not is_bw else (20, 20, 20), anchor="lm")
        b_y += 38

    # Legend / Footer line
    foot_y = notes_bottom + 35
    footer_text = "CivicSense Management System | Academic Project Specification | Python, CustomTkinter, Flask, MySQL/JSON Architecture"
    draw.text((WIDTH//2, foot_y), footer_text, font=get_font(FONT_REGULAR, 16), fill=(100, 116, 139) if not is_bw else (80, 80, 80), anchor="mm")

    # Output file
    out_filename = "project_workflow_color.png" if not is_bw else "project_workflow_bw.png"
    img.save(out_filename, "PNG", dpi=(300, 300))
    print(f"Saved: {out_filename}")

if __name__ == "__main__":
    render_diagram(mode="color")
    render_diagram(mode="bw")
