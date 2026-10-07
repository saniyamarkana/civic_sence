# =============================================================================
# CivicSense DSA: Binary Tree Graph & BFS (Breadth-First Search) Engine
# =============================================================================
#
# Tree-Structured Graph Representation:
#
#                     [ Central Zone (Chowk) ]   <--- ROOT NODE (Level 0)
#                             /          \
#                            /            \
#          [ West Zone (Adajan) ]      [ Varachha Zone A ]   <--- CHILDREN (Level 1)
#              /            \              /            \
#       [ North Zone ]  [ South West ] [ South Zone ]  [ Varachha B ] <--- LEVEL 2
#         (Katargam)       (Athwa)        (Udhana)
#            /                              /
#      [ Shakti Nagar ]              [ South East ]  <--- LEAF NODES (Level 3)
#                                       (Dindoli)
#
# Level-Order BFS Traversal Sequence (Starting from Root):
#   Level 0: Central Zone (Chowk)
#   Level 1: West Zone (Adajan) -> Varachha Zone A
#   Level 2: North Zone (Katargam) -> South West (Athwa) -> South Zone (Udhana) -> Varachha Zone B
#   Level 3: Shakti Nagar -> South East (Dindoli)
#
# =============================================================================

import re as _re
import json as _json

# ─────────────────────────────────────────────────────────────────────────────
# 1. Binary Tree Node & Hierarchy Definition
# ─────────────────────────────────────────────────────────────────────────────

ROOT_NODE = "Central Zone (Chowk)"

BINARY_TREE_STRUCTURE = {
    "Central Zone (Chowk)": {
        "id": "root",
        "role": "Root Node",
        "level": 0,
        "parent": None,
        "left": "West Zone (Adajan)",
        "right": "Varachha Zone A",
        "zone": "Zone A",
        "code": "Zone A",
        "short": "Central Chowk",
        "description": "City Core Civic Headquarters (Root of the Administrative Network)",
        "icon": "fa-solid fa-crown",
        "color": {"fill": "#0f2b48", "stroke": "#38bdf8", "text": "#f0f9ff", "badge": "#0284c7"}
    },
    "West Zone (Adajan)": {
        "id": "child_left",
        "role": "Left Child",
        "level": 1,
        "parent": "Central Zone (Chowk)",
        "left": "North Zone (Katargam)",
        "right": "South West (Athwa)",
        "zone": "Zone B",
        "code": "Zone B",
        "short": "Adajan (West)",
        "description": "Western Sector Hub (Infrastructure & Residential Sector)",
        "icon": "fa-solid fa-diagram-nested",
        "color": {"fill": "#1e293b", "stroke": "#f59e0b", "text": "#fef3c7", "badge": "#d97706"}
    },
    "Varachha Zone A": {
        "id": "child_right",
        "role": "Right Child",
        "level": 1,
        "parent": "Central Zone (Chowk)",
        "left": "South Zone (Udhana)",
        "right": "Varachha Zone B",
        "zone": "Zone C",
        "code": "Zone C",
        "short": "Varachha A",
        "description": "Eastern Commercial Hub (Diamond & Textile Commercial District)",
        "icon": "fa-solid fa-diagram-nested",
        "color": {"fill": "#1e293b", "stroke": "#10b981", "text": "#dcfce7", "badge": "#059669"}
    },
    "North Zone (Katargam)": {
        "id": "child_ll",
        "role": "Child (Left.Left)",
        "level": 2,
        "parent": "West Zone (Adajan)",
        "left": "Shakti Nagar",
        "right": None,
        "zone": "Zone E",
        "code": "Zone E",
        "short": "Katargam",
        "description": "Northern Industrial Corridor & Diamond Polishing Cluster",
        "icon": "fa-solid fa-code-fork",
        "color": {"fill": "#1e293b", "stroke": "#a855f7", "text": "#f3e8ff", "badge": "#9333ea"}
    },
    "South West (Athwa)": {
        "id": "child_lr",
        "role": "Child (Left.Right)",
        "level": 2,
        "parent": "West Zone (Adajan)",
        "left": None,
        "right": None,
        "zone": "Zone F",
        "code": "Zone F",
        "short": "Athwa",
        "description": "South-Western Waterfront & Institutional Educational District",
        "icon": "fa-solid fa-leaf",
        "color": {"fill": "#1e293b", "stroke": "#ec4899", "text": "#fce7f3", "badge": "#db2777"}
    },
    "South Zone (Udhana)": {
        "id": "child_rl",
        "role": "Child (Right.Left)",
        "level": 2,
        "parent": "Varachha Zone A",
        "left": "South East (Dindoli)",
        "right": None,
        "zone": "Zone D",
        "code": "Zone D",
        "short": "Udhana",
        "description": "Heavy Industrial & Railway Logistics Corridor",
        "icon": "fa-solid fa-code-fork",
        "color": {"fill": "#1e293b", "stroke": "#06b6d4", "text": "#cffafe", "badge": "#0891b2"}
    },
    "Varachha Zone B": {
        "id": "child_rr",
        "role": "Child (Right.Right)",
        "level": 2,
        "parent": "Varachha Zone A",
        "left": None,
        "right": None,
        "zone": "Zone G",
        "code": "Zone G",
        "short": "Varachha B",
        "description": "North-Eastern Residential Extension & Green Belt",
        "icon": "fa-solid fa-leaf",
        "color": {"fill": "#1e293b", "stroke": "#84cc16", "text": "#ecfccb", "badge": "#65a30d"}
    },
    "Shakti Nagar": {
        "id": "leaf_l",
        "role": "Leaf Node",
        "level": 3,
        "parent": "North Zone (Katargam)",
        "left": None,
        "right": None,
        "zone": "Zone I",
        "code": "Zone I",
        "short": "Shakti Nagar",
        "description": "Northern Peripheral Civic Community Ward",
        "icon": "fa-solid fa-seedling",
        "color": {"fill": "#1e293b", "stroke": "#64748b", "text": "#f1f5f9", "badge": "#475569"}
    },
    "South East (Dindoli)": {
        "id": "leaf_r",
        "role": "Leaf Node",
        "level": 3,
        "parent": "South Zone (Udhana)",
        "left": None,
        "right": None,
        "zone": "Zone H",
        "code": "Zone H",
        "short": "Dindoli",
        "description": "South-Eastern High-Density Civic Housing Expansion",
        "icon": "fa-solid fa-seedling",
        "color": {"fill": "#1e293b", "stroke": "#64748b", "text": "#f1f5f9", "badge": "#475569"}
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. Graph Adjacency List (Binary Tree Edges)
# ─────────────────────────────────────────────────────────────────────────────

graph = {
    "Central Zone (Chowk)": [
        "West Zone (Adajan)",
        "Varachha Zone A",
    ],
    "West Zone (Adajan)": [
        "Central Zone (Chowk)",
        "North Zone (Katargam)",
        "South West (Athwa)",
    ],
    "Varachha Zone A": [
        "Central Zone (Chowk)",
        "South Zone (Udhana)",
        "Varachha Zone B",
    ],
    "North Zone (Katargam)": [
        "West Zone (Adajan)",
        "Shakti Nagar",
    ],
    "South West (Athwa)": [
        "West Zone (Adajan)",
    ],
    "South Zone (Udhana)": [
        "Varachha Zone A",
        "South East (Dindoli)",
    ],
    "Varachha Zone B": [
        "Varachha Zone A",
    ],
    "Shakti Nagar": [
        "North Zone (Katargam)",
    ],
    "South East (Dindoli)": [
        "South Zone (Udhana)",
    ],
}

# Directed tree edges (Parent -> Child)
TREE_EDGES = [
    ("Central Zone (Chowk)", "West Zone (Adajan)", "Left Child"),
    ("Central Zone (Chowk)", "Varachha Zone A", "Right Child"),
    ("West Zone (Adajan)", "North Zone (Katargam)", "Left Child"),
    ("West Zone (Adajan)", "South West (Athwa)", "Right Child"),
    ("Varachha Zone A", "South Zone (Udhana)", "Left Child"),
    ("Varachha Zone A", "Varachha Zone B", "Right Child"),
    ("North Zone (Katargam)", "Shakti Nagar", "Left Child"),
    ("South Zone (Udhana)", "South East (Dindoli)", "Left Child"),
]

SCREENSHOT_EDGES = [(u, v) for u, v, _ in TREE_EDGES]

ZONE_ALIASES = {k: v["zone"] for k, v in BINARY_TREE_STRUCTURE.items()}

MAP_COORDINATES = {
    "Central Zone (Chowk)":  (21.1989, 72.8223),
    "West Zone (Adajan)":    (21.1950, 72.7950),
    "Varachha Zone A":       (21.2150, 72.8550),
    "South Zone (Udhana)":   (21.1550, 72.8350),
    "North Zone (Katargam)": (21.2300, 72.8200),
    "South West (Athwa)":    (21.1700, 72.7950),
    "Varachha Zone B":       (21.2350, 72.8800),
    "South East (Dindoli)":  (21.1600, 72.8750),
    "Shakti Nagar":          (21.2200, 72.8700),
}

# SVG layout coordinates (symmetrical binary tree, canvas 900x440)
POINT_LAYOUT_COORDINATES = {
    "Central Zone (Chowk)":  {"x": 450, "y": 55,  "r": 34, "short": "Central Chowk", "level": 0},
    "West Zone (Adajan)":    {"x": 230, "y": 160, "r": 30, "short": "Adajan (West)", "level": 1},
    "Varachha Zone A":       {"x": 670, "y": 160, "r": 30, "short": "Varachha A",    "level": 1},
    "North Zone (Katargam)": {"x": 120, "y": 265, "r": 27, "short": "Katargam",      "level": 2},
    "South West (Athwa)":    {"x": 340, "y": 265, "r": 27, "short": "Athwa",         "level": 2},
    "South Zone (Udhana)":   {"x": 560, "y": 265, "r": 27, "short": "Udhana",        "level": 2},
    "Varachha Zone B":       {"x": 780, "y": 265, "r": 27, "short": "Varachha B",    "level": 2},
    "Shakti Nagar":          {"x": 120, "y": 370, "r": 25, "short": "Shakti Nagar",  "level": 3},
    "South East (Dindoli)":  {"x": 560, "y": 370, "r": 25, "short": "Dindoli",       "level": 3},
}

import os as _os
_BASE_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DYNAMIC_NODES_FILE = _os.path.join(_BASE_DIR, "database", "dynamic_graph_nodes.json")
INITIAL_TREE_NODES = set(BINARY_TREE_STRUCTURE.keys())

def _save_dynamic_nodes():
    try:
        data = {
            "BINARY_TREE_STRUCTURE": {k: v for k, v in BINARY_TREE_STRUCTURE.items() if k not in INITIAL_TREE_NODES},
            "POINT_LAYOUT_COORDINATES": {k: v for k, v in POINT_LAYOUT_COORDINATES.items() if k not in INITIAL_TREE_NODES},
            "ZONE_ALIASES": {k: v for k, v in ZONE_ALIASES.items() if k not in INITIAL_TREE_NODES},
            "TREE_EDGES": [list(e) for e in TREE_EDGES if e[0] not in INITIAL_TREE_NODES or e[1] not in INITIAL_TREE_NODES],
            "dynamic_nodes": [k for k in BINARY_TREE_STRUCTURE if k not in INITIAL_TREE_NODES]
        }
        with open(_DYNAMIC_NODES_FILE, "w", encoding="utf-8") as f:
            _json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[Graph Persistence Error] Failed to save dynamic nodes: {e}")

def _load_dynamic_nodes():
    if not _os.path.exists(_DYNAMIC_NODES_FILE):
        return
    try:
        with open(_DYNAMIC_NODES_FILE, "r", encoding="utf-8") as f:
            data = _json.load(f)
        for k, v in data.get("BINARY_TREE_STRUCTURE", {}).items():
            BINARY_TREE_STRUCTURE[k] = v
        for k, v in data.get("POINT_LAYOUT_COORDINATES", {}).items():
            POINT_LAYOUT_COORDINATES[k] = v
        for k, v in data.get("ZONE_ALIASES", {}).items():
            ZONE_ALIASES[k] = v
        for e in data.get("TREE_EDGES", []):
            tup = tuple(e)
            if not any((u == tup[0] and v == tup[1]) or (u == tup[1] and v == tup[0]) for u, v, *_ in TREE_EDGES):
                TREE_EDGES.append(tup)
            if tup[0] not in graph: graph[tup[0]] = []
            if tup[1] not in graph: graph[tup[1]] = []
            if tup[1] not in graph[tup[0]]: graph[tup[0]].append(tup[1])
            if tup[0] not in graph[tup[1]]: graph[tup[1]].append(tup[0])
    except Exception as e:
        print(f"[Graph Persistence Error] Failed to load dynamic nodes: {e}")

_load_dynamic_nodes()


def get_map_data():
    """Returns complete Location Graph data (nodes, edges, tree levels) for the frontend."""
    nodes = []
    for area, meta in BINARY_TREE_STRUCTURE.items():
        coords = MAP_COORDINATES.get(area, (21.1989, 72.8223))
        layout = POINT_LAYOUT_COORDINATES.get(area, {"x": 450, "y": 200, "r": 28, "short": area, "level": meta["level"]})
        nodes.append({
            "area": area,
            "code": meta["zone"],
            "zone": meta["zone"],
            "role": meta["role"],
            "level": meta["level"],
            "parent": meta["parent"],
            "left": meta["left"],
            "right": meta["right"],
            "lat": coords[0],
            "lng": coords[1],
            "x": layout["x"],
            "y": layout["y"],
            "r": layout.get("r", 28),
            "short_label": layout["short"],
            "description": meta["description"],
            "color": meta["color"],
        })

    edges = []
    for u, v, branch in TREE_EDGES:
        edges.append({"from": u, "to": v, "branch": branch})

    return {
        "root": ROOT_NODE,
        "nodes": nodes,
        "edges": edges,
        "zone_aliases": ZONE_ALIASES,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. BFS Traversal (Breadth-First Search / Level-Order)
# ─────────────────────────────────────────────────────────────────────────────

def bfs(start=ROOT_NODE, target=None):
    """BFS Level-Order traversal using a FIFO Queue."""
    if start not in graph:
        start = ROOT_NODE
    visited = []
    queue = [start]
    visited.append(start)
    while queue:
        current = queue.pop(0)
        if target and current == target:
            break
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.append(neighbor)
                queue.append(neighbor)
    return visited


def bfs_shortest_path(start, target):
    """Shortest path between two nodes using BFS."""
    if start not in graph or target not in graph:
        return []
    if start == target:
        return [start]
    visited = {start}
    queue = [[start]]
    while queue:
        path = queue.pop(0)
        node = path[-1]
        for neighbor in graph.get(node, []):
            if neighbor == target:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return []


def bfs_with_steps(start=ROOT_NODE, target=None):
    """BFS with step-by-step state logging for interactive visualizers."""
    if start not in graph:
        start = ROOT_NODE
    visited = []
    queue = [start]
    in_queue = {start}
    steps = []
    step_num = 1

    start_meta = BINARY_TREE_STRUCTURE.get(start, {})
    steps.append({
        "step": step_num,
        "action": "enqueue_root",
        "visiting": start,
        "visiting_role": start_meta.get("role", "Root Node"),
        "visiting_level": start_meta.get("level", 0),
        "queue_state": list(queue),
        "visited_state": list(visited),
        "discovered": [start],
        "message": f"Initialized BFS. Enqueued Root Node <strong>{start}</strong> (Level {start_meta.get('level', 0)}) into FIFO Queue."
    })

    while queue:
        current = queue.pop(0)
        visited.append(current)
        curr_meta = BINARY_TREE_STRUCTURE.get(current, {})

        if target and current == target:
            step_num += 1
            steps.append({
                "step": step_num,
                "action": "target_reached",
                "visiting": current,
                "visiting_role": curr_meta.get("role", "Node"),
                "visiting_level": curr_meta.get("level", 0),
                "queue_state": list(queue),
                "visited_state": list(visited),
                "discovered": [],
                "message": f"Target <strong>{current}</strong> found! BFS complete."
            })
            break

        discovered_now = []
        for neighbor in graph.get(current, []):
            if neighbor not in visited and neighbor not in in_queue:
                in_queue.add(neighbor)
                queue.append(neighbor)
                discovered_now.append(neighbor)

        step_num += 1
        disc_names = ", ".join([f"{n} ({BINARY_TREE_STRUCTURE.get(n, {}).get('role', 'Child')})" for n in discovered_now])
        steps.append({
            "step": step_num,
            "action": "visit_node",
            "visiting": current,
            "visiting_role": curr_meta.get("role", "Node"),
            "visiting_level": curr_meta.get("level", 0),
            "queue_state": list(queue),
            "visited_state": list(visited),
            "discovered": discovered_now,
            "message": (
                f"Visited <strong>{current}</strong> ({curr_meta.get('role','Node')}, Level {curr_meta.get('level',0)}). " +
                (f"Enqueued children: {disc_names}." if discovered_now else "Leaf node — no further branches.")
            )
        })

    shortest_path = []
    if target:
        shortest_path = bfs_shortest_path(start, target)

    return {
        "start": start,
        "target": target,
        "visited": visited,
        "steps": steps,
        "shortest_path": shortest_path,
        "total_steps": len(steps)
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. DFS Traversal
# ─────────────────────────────────────────────────────────────────────────────

def dfs(node=ROOT_NODE, visited=None):
    """Depth-First Search traversal."""
    if visited is None:
        visited = []
    if node not in visited:
        visited.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, visited)
    return visited


def dfs_with_steps(start=ROOT_NODE):
    """DFS with step-by-step state recording using a Stack (LIFO)."""
    if start not in graph:
        start = ROOT_NODE
    visited = []
    stack = [start]
    steps = []
    step_num = 1
    while stack:
        current = stack.pop()
        if current not in visited:
            visited.append(current)
            neighbors = graph.get(current, [])
            for neighbor in reversed(neighbors):
                if neighbor not in visited and neighbor not in stack:
                    stack.append(neighbor)
            meta = BINARY_TREE_STRUCTURE.get(current, {})
            steps.append({
                "step": step_num,
                "visiting": current,
                "visiting_role": meta.get("role", "Node"),
                "visiting_level": meta.get("level", 0),
                "stack_state": list(stack),
                "visited_state": list(visited)
            })
            step_num += 1
    return {"start": start, "visited": visited, "steps": steps}


# ─────────────────────────────────────────────────────────────────────────────
# 5. Interactive HTML Component Generator
# ─────────────────────────────────────────────────────────────────────────────

def _safe(name: str) -> str:
    return _re.sub(r"[^a-zA-Z0-9]", "_", name)


def get_bfs_graph_html(start_node: str = ROOT_NODE) -> str:
    """
    Generates a self-contained HTML component showing the Location Graph
    (Binary Tree) with interactive BFS Level-Order Traversal animation.
    """
    if start_node not in POINT_LAYOUT_COORDINATES:
        start_node = ROOT_NODE

    # 1. Tree Branch Lines
    svg_edges = ""
    for u, v, branch in TREE_EDGES:
        pos_u = POINT_LAYOUT_COORDINATES.get(u)
        pos_v = POINT_LAYOUT_COORDINATES.get(v)
        if not pos_u or not pos_v:
            continue
        edge_id = f"bfse_{_safe(u)}_{_safe(v)}"
        branch_label = "L" if "Left" in branch else "R"
        mid_x = (pos_u["x"] + pos_v["x"]) / 2
        mid_y = (pos_u["y"] + pos_v["y"]) / 2
        svg_edges += f"""
        <g>
          <line id="{edge_id}" x1="{pos_u['x']}" y1="{pos_u['y']}" x2="{pos_v['x']}" y2="{pos_v['y']}"
                stroke="#475569" stroke-width="2.8" stroke-linecap="round"
                style="transition: stroke 0.35s ease, stroke-width 0.35s ease;" />
          <circle cx="{mid_x}" cy="{mid_y}" r="8" fill="#0f172a" stroke="#334155" stroke-width="1.5" />
          <text x="{mid_x}" y="{mid_y + 3.5}" text-anchor="middle" font-size="9" font-weight="800"
                fill="#94a3b8" font-family="system-ui,sans-serif">{branch_label}</text>
        </g>
"""

    # 2. Tree Nodes
    svg_nodes = ""
    for area, meta in BINARY_TREE_STRUCTURE.items():
        sid = _safe(area)
        pos = POINT_LAYOUT_COORDINATES[area]
        cx, cy, r = pos["x"], pos["y"], pos["r"]
        is_root = (area == ROOT_NODE)
        col = meta["color"]
        badge_x = cx + int(r * 0.75)
        badge_y = cy - int(r * 0.75)
        crown = f'<text x="{cx}" y="{cy - r - 6}" text-anchor="middle" font-size="14">👑</text>' if is_root else ""

        svg_nodes += f"""
        <g id="bfsn_{sid}" data-area="{area}" onclick="window.bfsSelectNode('{area}')" style="cursor:pointer;">
          {crown}
          <circle id="bfsActiveRing_{sid}" cx="{cx}" cy="{cy}" r="{r + 7}" fill="none"
                  stroke="{col['stroke'] if is_root else 'transparent'}" stroke-width="2.5"
                  style="transition: all 0.3s ease;" />
          <circle id="bfsh_{sid}" cx="{cx}" cy="{cy}" r="{r + 14}" fill="transparent"
                  style="transition: fill 0.3s ease;" />
          <circle id="bfsc_{sid}" cx="{cx}" cy="{cy}" r="{r}"
                  fill="{col['fill']}" stroke="{col['stroke']}" stroke-width="{3.5 if is_root else 2.6}"
                  style="transition: all 0.3s ease; filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3));" />
          <text x="{cx}" y="{cy - 2}" text-anchor="middle" font-size="{10 if is_root else 9}" font-weight="800"
                fill="{col['text']}" font-family="system-ui,sans-serif" style="pointer-events:none;">{meta['zone']}</text>
          <text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="8" font-weight="700"
                fill="#94a3b8" font-family="system-ui,sans-serif" style="pointer-events:none;">L{meta['level']}</text>
          <text x="{cx}" y="{cy + r + 15}" text-anchor="middle" font-size="11" font-weight="700"
                fill="#e2e8f0" font-family="system-ui,sans-serif" style="pointer-events:none; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">{pos['short']}</text>
          <g id="bfsbg_{sid}" style="display: {'inline' if is_root else 'none'}; pointer-events:none;">
            <circle id="bfsbc_{sid}" cx="{badge_x}" cy="{badge_y}" r="11" fill="{col['badge']}" stroke="#ffffff" stroke-width="1.8" />
            <text id="bfsbt_{sid}" x="{badge_x}" y="{badge_y + 3.5}" text-anchor="middle" font-size="10" font-weight="900" fill="#ffffff" font-family="system-ui,sans-serif">{'1' if is_root else ''}</text>
          </g>
        </g>
"""

    # 3. Options for start-node selector
    options_html = ""
    for a, meta in BINARY_TREE_STRUCTURE.items():
        sel = 'selected="selected"' if a == start_node else ''
        options_html += f'<option value="{a}" {sel}>{meta["short"]} — {meta["role"]} ({meta["zone"]})</option>\n'

    # 4. Adjacency table rows
    adj_rows = ""
    for a, meta in BINARY_TREE_STRUCTURE.items():
        p = meta["parent"] or "None (Root)"
        l = meta["left"] or "—"
        r = meta["right"] or "—"
        adj_rows += f"""
        <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
          <td style="padding: 9px 12px; font-weight:800; color:#f8fafc;">{meta['short']}</td>
          <td style="padding: 9px 12px;"><span style="background:rgba(6,182,212,0.15);color:#06b6d4;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;">Level {meta['level']}</span></td>
          <td style="padding: 9px 12px; color:#38bdf8; font-weight:700;">{meta['role']}</td>
          <td style="padding: 9px 12px; color:#94a3b8;">{p}</td>
          <td style="padding: 9px 12px; color:#10b981;">{l}</td>
          <td style="padding: 9px 12px; color:#f59e0b;">{r}</td>
        </tr>
"""

    js_layout = _json.dumps({
        k: {
            "x": v["x"], "y": v["y"], "r": v["r"], "short": v["short"],
            "fill": BINARY_TREE_STRUCTURE[k]["color"]["fill"],
            "stroke": BINARY_TREE_STRUCTURE[k]["color"]["stroke"],
            "badge": BINARY_TREE_STRUCTURE[k]["color"]["badge"],
            "sid": _safe(k),
            "role": BINARY_TREE_STRUCTURE[k]["role"],
            "level": BINARY_TREE_STRUCTURE[k]["level"],
        } for k, v in POINT_LAYOUT_COORDINATES.items()
    })
    js_edges = _json.dumps([(u, v) for u, v, _ in TREE_EDGES])
    js_graph = _json.dumps(graph)
    js_meta  = _json.dumps(BINARY_TREE_STRUCTURE)

    template = """<!-- Location Graph – Binary Tree & BFS Visualizer (dsa/graph.py) -->
<div id="civicBfsVisualizerCard" style="background:linear-gradient(135deg,#0a1120 0%,#0e172a 100%);border:1px solid rgba(56,189,248,0.25);border-radius:18px;box-shadow:0 15px 45px rgba(0,0,0,0.5);overflow:hidden;font-family:'Segoe UI',system-ui,sans-serif;margin-bottom:24px;">

  <!-- Header Banner -->
  <div style="background:rgba(14,23,42,0.9);border-bottom:1px solid rgba(255,255,255,0.08);padding:14px 22px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
    <div style="display:flex;align-items:center;gap:12px;">
      <div style="width:36px;height:36px;border-radius:10px;background:rgba(6,182,212,0.15);border:1px solid rgba(6,182,212,0.4);display:flex;align-items:center;justify-content:center;color:#06b6d4;font-size:16px;">
        <i class="fa-solid fa-sitemap"></i>
      </div>
      <div>
        <div style="font-size:15px;font-weight:800;color:#f8fafc;">Location Graph — Binary Tree &amp; BFS Level-Order</div>
        <div style="font-size:12px;color:#94a3b8;">Root Node (Level 0) &bull; Child Nodes (Levels 1–3) &bull; FIFO Queue Traversal</div>
      </div>
    </div>
    <span style="font-size:11px;font-weight:800;background:rgba(59,130,246,0.15);color:#60a5fa;border:1px solid rgba(59,130,246,0.3);padding:4px 10px;border-radius:12px;letter-spacing:0.5px;">BFS &bull; O(V + E)</span>
  </div>

  <!-- Control Bar -->
  <div style="background:rgba(15,23,42,0.95);border-bottom:1px solid rgba(255,255,255,0.06);padding:12px 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="font-size:11px;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Start Node:</span>
      <select id="bfsStartSelectCtrl" onchange="window.bfsChangeStart(this.value)"
              style="padding:7px 12px;font-size:12px;font-weight:700;color:#f8fafc;background:#1e293b;border:1px solid rgba(255,255,255,0.15);border-radius:8px;outline:none;cursor:pointer;">
        __OPTIONS_HTML__
      </select>
    </div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <button id="bfsBtnPlay" onclick="window.bfsTogglePlay()"
              style="display:inline-flex;align-items:center;gap:6px;padding:7px 16px;font-size:12px;font-weight:800;color:#fff;background:linear-gradient(135deg,#0284c7,#2563eb);border:none;border-radius:8px;cursor:pointer;box-shadow:0 4px 12px rgba(37,99,235,0.3);">
        <i class="fa-solid fa-play"></i> <span>Run BFS</span>
      </button>
      <button onclick="window.bfsStepForward()"
              style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;font-size:12px;font-weight:700;color:#cbd5e1;background:#1e293b;border:1px solid rgba(255,255,255,0.12);border-radius:8px;cursor:pointer;">
        <i class="fa-solid fa-forward-step"></i> Next Step
      </button>
      <button onclick="window.bfsReset()"
              style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;font-size:12px;font-weight:700;color:#94a3b8;background:#1e293b;border:1px solid rgba(255,255,255,0.12);border-radius:8px;cursor:pointer;">
        <i class="fa-solid fa-rotate-left"></i> Reset
      </button>
      <div style="display:flex;align-items:center;gap:5px;margin-left:6px;">
        <span style="font-size:11px;font-weight:700;color:#94a3b8;">Speed:</span>
        <select id="bfsSpeedSelect" onchange="window.bfsSetSpeed(this.value)"
                style="padding:5px 8px;font-size:11px;font-weight:700;color:#f8fafc;background:#1e293b;border:1px solid rgba(255,255,255,0.15);border-radius:6px;">
          <option value="1200">Slow (1.2s)</option>
          <option value="750" selected>Normal (0.75s)</option>
          <option value="350">Fast (0.35s)</option>
        </select>
      </div>
    </div>
  </div>

  <!-- SVG Canvas -->
  <div style="background:radial-gradient(ellipse at 50% 15%,rgba(6,182,212,0.08) 0%,rgba(10,17,32,0.98) 75%);padding:18px 12px;position:relative;overflow-x:auto;">
    <div style="position:absolute;left:18px;top:50px;font-size:10px;font-weight:800;color:rgba(255,255,255,0.2);letter-spacing:1px;text-transform:uppercase;">Level 0 &bull; Root Node</div>
    <div style="position:absolute;left:18px;top:155px;font-size:10px;font-weight:800;color:rgba(255,255,255,0.2);letter-spacing:1px;text-transform:uppercase;">Level 1 &bull; Children</div>
    <div style="position:absolute;left:18px;top:260px;font-size:10px;font-weight:800;color:rgba(255,255,255,0.2);letter-spacing:1px;text-transform:uppercase;">Level 2 &bull; Grandchildren</div>
    <div style="position:absolute;left:18px;top:365px;font-size:10px;font-weight:800;color:rgba(255,255,255,0.2);letter-spacing:1px;text-transform:uppercase;">Level 3 &bull; Leaf Nodes</div>
    <svg id="civicBfsSvg" viewBox="0 0 900 440" width="100%" height="auto" style="display:block;min-width:700px;max-height:440px;margin:0 auto;">
      <line x1="80" y1="105" x2="840" y2="105" stroke="rgba(255,255,255,0.04)" stroke-dasharray="4 4"/>
      <line x1="80" y1="210" x2="840" y2="210" stroke="rgba(255,255,255,0.04)" stroke-dasharray="4 4"/>
      <line x1="80" y1="315" x2="840" y2="315" stroke="rgba(255,255,255,0.04)" stroke-dasharray="4 4"/>
      <g id="bfsEdgesGroup">__SVG_EDGES__</g>
      <g id="bfsNodesGroup">__SVG_NODES__</g>
    </svg>
  </div>

  <!-- Status Dashboard -->
  <div style="background:rgba(11,19,36,0.95);border-top:1px solid rgba(255,255,255,0.07);padding:18px 22px;">
    <div id="bfsExplainCard" style="background:rgba(15,23,42,0.8);border:1px solid rgba(56,189,248,0.2);border-left:4px solid #38bdf8;border-radius:10px;padding:12px 18px;margin-bottom:16px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
        <span id="bfsStepBadge" style="font-size:11px;font-weight:800;color:#38bdf8;text-transform:uppercase;letter-spacing:0.5px;">Ready to Traverse</span>
        <span id="bfsProgressText" style="font-size:11px;color:#94a3b8;font-weight:600;">Start: Central Chowk [Root Node]</span>
      </div>
      <div id="bfsExplainText" style="font-size:13px;color:#f1f5f9;font-weight:500;line-height:1.5;">
        Click <strong>Run BFS</strong> to observe level-order traversal: Root (Level 0) &rarr; Children (Level 1) &rarr; Grandchildren (Level 2) &rarr; Leaf Nodes (Level 3).
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
      <div style="background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:12px 16px;">
        <div style="font-size:11px;font-weight:800;color:#38bdf8;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
          <i class="fa-solid fa-arrows-turn-to-dots"></i> BFS Queue (FIFO)
        </div>
        <div id="bfsQueueDisplay" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;min-height:32px;">
          <span style="font-size:12px;color:#64748b;font-style:italic;">Queue empty (idle)</span>
        </div>
      </div>
      <div style="background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:12px 16px;">
        <div style="font-size:11px;font-weight:800;color:#10b981;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
          <i class="fa-solid fa-list-ol"></i> Visited Order (BFS Sequence)
        </div>
        <div id="bfsVisitedDisplay" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;min-height:32px;">
          <span style="font-size:12px;color:#64748b;font-style:italic;">No traversal executed yet</span>
        </div>
      </div>
    </div>
    <details style="margin-top:14px;background:rgba(15,23,42,0.6);border:1px solid rgba(255,255,255,0.07);border-radius:10px;overflow:hidden;">
      <summary style="padding:10px 16px;font-size:12px;font-weight:700;color:#94a3b8;cursor:pointer;background:rgba(15,23,42,0.9);outline:none;">
        <i class="fa-solid fa-sitemap" style="margin-right:6px;color:#06b6d4;"></i> Binary Tree Node Hierarchy &amp; Adjacency
      </summary>
      <div style="padding:10px 16px;max-height:240px;overflow-y:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:12px;text-align:left;">
          <thead>
            <tr style="border-bottom:2px solid rgba(255,255,255,0.1);color:#64748b;font-weight:800;font-size:11px;text-transform:uppercase;">
              <th style="padding:8px 12px;">Node</th>
              <th style="padding:8px 12px;">Level</th>
              <th style="padding:8px 12px;">Role</th>
              <th style="padding:8px 12px;">Parent</th>
              <th style="padding:8px 12px;">Left Child</th>
              <th style="padding:8px 12px;">Right Child</th>
            </tr>
          </thead>
          <tbody>__ADJ_ROWS__</tbody>
        </table>
      </div>
    </details>
  </div>
</div>

<script>
(function() {
  const _layout = __JS_LAYOUT__;
  const _edges  = __JS_EDGES__;
  const _graph  = __JS_GRAPH__;
  const _meta   = __JS_META__;
  const ROOT    = "__START_NODE__";

  let _startNode = ROOT;
  let _stepIndex = 0, _steps = [], _timer = null, _isPlaying = false, _speedMs = 750;

  function sid(str) { return (str||"").replace(/[^a-zA-Z0-9]/g,"_"); }

  function buildSteps(start) {
    var steps = [], visited = [], queue = [start], inQ = new Set([start]);
    steps.push({ action:"start", current:start, queue:[...queue], visited:[...visited], discovered:[start],
      msg:"Starting BFS at <strong>"+(_layout[start]?_layout[start].short:start)+"</strong>. Enqueued as Node #1 in FIFO Queue." });
    while (queue.length) {
      var cur = queue.shift(); visited.push(cur);
      var nb = _graph[cur]||[], disc = [];
      for (var i=0;i<nb.length;i++) { if (!visited.includes(nb[i])&&!inQ.has(nb[i])) { inQ.add(nb[i]); queue.push(nb[i]); disc.push(nb[i]); } }
      var cm = _meta[cur]||{};
      var names = disc.map(function(n){return _layout[n]?_layout[n].short:n;}).join(", ");
      steps.push({ action:"visit", current:cur, queue:[...queue], visited:[...visited], discovered:disc,
        msg:"Visited <strong>"+(_layout[cur]?_layout[cur].short:cur)+"</strong> ("+( cm.role||"Node")+", Level "+(cm.level!==undefined?cm.level:0)+"). "+
            (disc.length?"Enqueued children: <strong>"+names+"</strong>.":"Leaf node — no further branches.") });
    }
    return steps;
  }

  function applyStep(step) {
    if (!step) return;
    var sb=document.getElementById("bfsStepBadge"), pt=document.getElementById("bfsProgressText"), et=document.getElementById("bfsExplainText");
    var cm=_meta[step.current]||{};
    if(sb) sb.textContent=step.action==="start"?"Queue Initialized":("Step "+(_stepIndex+1)+" of "+_steps.length);
    if(pt) pt.textContent="Visiting: "+(_layout[step.current]?_layout[step.current].short:step.current)+" ("+(cm.role||"Node")+")";
    if(et) et.innerHTML=step.msg;

    Object.keys(_layout).forEach(function(area) {
      var s=sid(area);
      var ring=document.getElementById("bfsActiveRing_"+s), halo=document.getElementById("bfsh_"+s);
      var circ=document.getElementById("bfsc_"+s), bg=document.getElementById("bfsbg_"+s);
      var bt=document.getElementById("bfsbt_"+s), bc=document.getElementById("bfsbc_"+s);
      var isV=step.visited.includes(area), isC=step.current===area, isE=step.queue.includes(area);
      var nl=_layout[area]||{};
      if(ring){ring.setAttribute("stroke",isC?"#38bdf8":(isV?"#10b981":"transparent"));ring.setAttribute("stroke-width",isC?"3.5":"2.5");}
      if(halo) halo.setAttribute("fill",isC?"rgba(56,189,248,0.35)":(isV?"rgba(16,185,129,0.15)":"transparent"));
      if(circ){
        if(isC){circ.setAttribute("fill","#0284c7");circ.setAttribute("stroke","#38bdf8");circ.setAttribute("stroke-width","3.5");}
        else if(isV){circ.setAttribute("fill","#064e3b");circ.setAttribute("stroke","#10b981");circ.setAttribute("stroke-width","2.8");}
        else if(isE){circ.setAttribute("fill","#78350f");circ.setAttribute("stroke","#f59e0b");circ.setAttribute("stroke-width","2.8");}
        else{circ.setAttribute("fill",nl.fill||"#1e293b");circ.setAttribute("stroke",nl.stroke||"#475569");circ.setAttribute("stroke-width","2.6");}
      }
      if(bg&&bt&&bc){
        var vi=step.visited.indexOf(area);
        if(vi!==-1){bg.style.display="inline";bt.textContent=(vi+1);bc.setAttribute("fill",vi===0?"#0284c7":"#10b981");}
        else if(isC&&step.action==="start"){bg.style.display="inline";bt.textContent="1";bc.setAttribute("fill","#0284c7");}
        else{bg.style.display="none";}
      }
    });

    _edges.forEach(function(e){
      var el=document.getElementById("bfse_"+sid(e[0])+"_"+sid(e[1]))||document.getElementById("bfse_"+sid(e[1])+"_"+sid(e[0]));
      if(el){
        var uV=step.visited.includes(e[0]),vV=step.visited.includes(e[1]);
        el.setAttribute("stroke",uV&&vV?"#38bdf8":"#475569");el.setAttribute("stroke-width",uV&&vV?"3.5":"2.8");
      }
    });

    var qd=document.getElementById("bfsQueueDisplay");
    if(qd){
      if(!step.queue.length){qd.innerHTML='<span style="font-size:12px;color:#64748b;font-style:italic;">Queue is empty</span>';}
      else{qd.innerHTML=step.queue.map(function(q,i){var m=_layout[q]||{};return'<span style="display:inline-flex;align-items:center;gap:5px;background:rgba(2,132,199,0.2);border:1.5px solid #0284c7;color:#38bdf8;padding:4px 10px;border-radius:8px;font-size:12px;font-weight:700;"><span style="font-size:10px;background:#0284c7;color:#fff;border-radius:4px;padding:1px 5px;">'+(i===0?"FRONT":i)+'</span> '+(m.short||q)+' <span style="font-size:10px;opacity:0.7;">(L'+(m.level!==undefined?m.level:"?")+')  </span></span>';}).join("");}
    }

    var vd=document.getElementById("bfsVisitedDisplay");
    if(vd){
      if(!step.visited.length){vd.innerHTML='<span style="font-size:12px;color:#64748b;font-style:italic;">No nodes visited yet</span>';}
      else{vd.innerHTML=step.visited.map(function(v,i){var m=_layout[v]||{};var bg=i===0?"#0284c7":"#10b981";return'<span style="display:inline-flex;align-items:center;gap:5px;background:rgba(16,185,129,0.18);border:1.5px solid #10b981;color:#4ade80;padding:4px 10px;border-radius:8px;font-size:12px;font-weight:700;"><span style="background:'+bg+';color:#fff;font-size:9px;width:16px;height:16px;border-radius:50%;display:flex;align-items:center;justify-content:center;">'+(i+1)+'</span> '+(m.short||v)+'</span>';}).join("");}
    }
  }

  window.bfsSelectNode=function(a){window.bfsChangeStart(a);window.bfsTogglePlay(true);};
  window.bfsChangeStart=function(a){_startNode=a;var s=document.getElementById("bfsStartSelectCtrl");if(s&&s.value!==a)s.value=a;window.bfsReset();};

  window.bfsTogglePlay=function(fp){
    if(fp!==undefined)_isPlaying=!fp;
    var btn=document.getElementById("bfsBtnPlay");
    if(_isPlaying){_isPlaying=false;clearInterval(_timer);_timer=null;if(btn)btn.innerHTML='<i class="fa-solid fa-play"></i> <span>Resume BFS</span>';}
    else{
      _isPlaying=true;if(btn)btn.innerHTML='<i class="fa-solid fa-pause"></i> <span>Pause BFS</span>';
      if(!_steps.length||_stepIndex>=_steps.length-1){_steps=buildSteps(_startNode);_stepIndex=0;applyStep(_steps[0]);}
      clearInterval(_timer);_timer=setInterval(function(){
        if(_stepIndex<_steps.length-1){_stepIndex++;applyStep(_steps[_stepIndex]);}
        else{_isPlaying=false;clearInterval(_timer);_timer=null;if(btn)btn.innerHTML='<i class="fa-solid fa-rotate-left"></i> <span>Restart BFS</span>';
          var e=document.getElementById("bfsExplainText");if(e)e.innerHTML+=" &bull; <strong style='color:#10b981;'>BFS Complete!</strong>";}
      },_speedMs);
    }
  };

  window.bfsStepForward=function(){
    if(_isPlaying)window.bfsTogglePlay();
    if(!_steps.length){_steps=buildSteps(_startNode);_stepIndex=0;}
    else if(_stepIndex<_steps.length-1)_stepIndex++;
    applyStep(_steps[_stepIndex]);
  };

  window.bfsReset=function(){
    _isPlaying=false;clearInterval(_timer);_timer=null;_steps=buildSteps(_startNode);_stepIndex=0;
    var btn=document.getElementById("bfsBtnPlay");if(btn)btn.innerHTML='<i class="fa-solid fa-play"></i> <span>Run BFS</span>';
    Object.keys(_layout).forEach(function(area){
      var s=sid(area),nl=_layout[area]||{},m=_meta[area]||{};
      var ring=document.getElementById("bfsActiveRing_"+s),halo=document.getElementById("bfsh_"+s),circ=document.getElementById("bfsc_"+s);
      var bg=document.getElementById("bfsbg_"+s),bt=document.getElementById("bfsbt_"+s),bc=document.getElementById("bfsbc_"+s);
      if(ring)ring.setAttribute("stroke",area===_startNode?"#38bdf8":"transparent");
      if(halo)halo.setAttribute("fill","transparent");
      if(circ){circ.setAttribute("fill",nl.fill||"#1e293b");circ.setAttribute("stroke",nl.stroke||"#475569");circ.setAttribute("stroke-width",area===ROOT?"3.5":"2.6");}
      if(bg){if(area===_startNode){bg.style.display="inline";bt.textContent="1";bc.setAttribute("fill",nl.badge||"#0284c7");}else{bg.style.display="none";}}
    });
    _edges.forEach(function(e){var el=document.getElementById("bfse_"+sid(e[0])+"_"+sid(e[1]));if(el){el.setAttribute("stroke","#475569");el.setAttribute("stroke-width","2.8");}});
    var sb=document.getElementById("bfsStepBadge"),pt=document.getElementById("bfsProgressText"),et=document.getElementById("bfsExplainText");
    var qd=document.getElementById("bfsQueueDisplay"),vd=document.getElementById("bfsVisitedDisplay");
    if(sb)sb.textContent="Ready to Traverse";
    if(pt)pt.textContent="Start: "+(_layout[_startNode]?_layout[_startNode].short:_startNode);
    if(et)et.innerHTML="Click <strong>Run BFS</strong> to observe level-order traversal: Root (Level 0) &rarr; Children (Level 1) &rarr; Grandchildren (Level 2) &rarr; Leaf Nodes (Level 3).";
    if(qd)qd.innerHTML='<span style="font-size:12px;color:#64748b;font-style:italic;">Queue empty (idle)</span>';
    if(vd)vd.innerHTML='<span style="font-size:12px;color:#64748b;font-style:italic;">No traversal executed yet</span>';
  };

  window.bfsSetSpeed=function(val){
    _speedMs=parseInt(val,10)||750;
    if(_isPlaying){clearInterval(_timer);_timer=setInterval(function(){if(_stepIndex<_steps.length-1){_stepIndex++;applyStep(_steps[_stepIndex]);}else{_isPlaying=false;clearInterval(_timer);_timer=null;}},_speedMs);}
  };
})();
</script>
"""

    return (
        template
        .replace("__SVG_EDGES__", svg_edges)
        .replace("__SVG_NODES__", svg_nodes)
        .replace("__OPTIONS_HTML__", options_html)
        .replace("__ADJ_ROWS__", adj_rows)
        .replace("__JS_LAYOUT__", js_layout)
        .replace("__JS_EDGES__", js_edges)
        .replace("__JS_GRAPH__", js_graph)
        .replace("__JS_META__", js_meta)
        .replace("__START_NODE__", start_node)
    )


# ==========================================
# Dynamic Add Node / Edge & Search Facilities
# ==========================================

def bfs_search(target, start=ROOT_NODE):
    """Search if target is reachable using BFS."""
    if not start or start not in graph:
        start = ROOT_NODE
    visited = bfs(start, target)
    return {
        "found": target in visited,
        "target": target,
        "start": start,
        "visited": visited,
        "success": True
    }


def add_edge(node1, node2):
    """Add an undirected connection between two nodes."""
    if node1 not in graph:
        graph[node1] = []
    if node2 not in graph:
        graph[node2] = []
    if node2 not in graph[node1]:
        graph[node1].append(node2)
    if node1 not in graph[node2]:
        graph[node2].append(node1)

    edge_exists = any((u == node1 and v == node2) or (u == node2 and v == node1) for u, v, *_ in TREE_EDGES)
    if not edge_exists:
        TREE_EDGES.append((node1, node2, "Connected Branch"))


def add_node(node_name, neighbors=None, zone_code=None, branch=None, role=None, description=None):
    """
    Dynamically add a new location/ward node to the Civic Location Graph.
    Computes collision-free symmetrical SVG layout coordinates, establishes
    tree parent-child hierarchy & adjacency list, and registers node metadata.
    """
    if not node_name or not str(node_name).strip():
        return False, "Node name is required."

    node_name = str(node_name).strip()
    if node_name in graph and node_name in BINARY_TREE_STRUCTURE:
        return False, f"Location '{node_name}' already exists in the graph."

    # Identify parent / neighbor node
    if neighbors and isinstance(neighbors, list) and len(neighbors) > 0 and neighbors[0] in graph:
        parent_node = neighbors[0]
    elif neighbors and isinstance(neighbors, str) and neighbors in graph:
        parent_node = neighbors
    else:
        parent_node = ROOT_NODE

    parent_meta = BINARY_TREE_STRUCTURE.get(parent_node, {})
    parent_level = parent_meta.get("level", 0)
    new_level = min(parent_level + 1, 3)
    parent_layout = POINT_LAYOUT_COORDINATES.get(parent_node, {"x": 450, "y": 55})
    parent_x = parent_layout.get("x", 450)

    # Determine branch placement
    desired_branch = (branch or "auto").lower().strip()
    curr_left = parent_meta.get("left")
    curr_right = parent_meta.get("right")

    if desired_branch == "left" or (desired_branch == "auto" and curr_left is None):
        assigned_branch = "Left Child"
        if parent_meta.get("left") is None:
            parent_meta["left"] = node_name
    elif desired_branch == "right" or (desired_branch == "auto" and curr_right is None):
        assigned_branch = "Right Child"
        if parent_meta.get("right") is None:
            parent_meta["right"] = node_name
    else:
        assigned_branch = "Connected Ward"

    # Calculate SVG coordinates
    level_y_map = {0: 55, 1: 160, 2: 265, 3: 370}
    new_y = level_y_map.get(new_level, 370)

    # Base X spacing based on tree level
    level_spread = {1: 220, 2: 110, 3: 60}
    spread = level_spread.get(new_level, 60)

    if "Left" in assigned_branch:
        proposed_x = parent_x - spread
    elif "Right" in assigned_branch:
        proposed_x = parent_x + spread
    else:
        proposed_x = parent_x + (spread if len(graph.get(parent_node, [])) % 2 == 0 else -spread)

    # Collision avoidance: ensure at least 45px gap between any existing node at similar Y
    occupied_xs = [
        coord["x"] for name, coord in POINT_LAYOUT_COORDINATES.items()
        if abs(coord.get("y", 0) - new_y) < 30
    ]

    final_x = proposed_x
    step = 40
    direction = 1 if "Right" in assigned_branch else -1
    attempts = 0
    while any(abs(final_x - ox) < 45 for ox in occupied_xs) and attempts < 15:
        final_x += direction * step
        if final_x > 840:
            final_x = 840 - (attempts * 15)
            direction = -1
        elif final_x < 60:
            final_x = 60 + (attempts * 15)
            direction = 1
        attempts += 1

    final_x = max(60, min(840, final_x))

    # Generate Zone Code
    existing_zones = {meta.get("zone") for meta in BINARY_TREE_STRUCTURE.values()}
    if zone_code and str(zone_code).strip():
        assigned_zone = str(zone_code).strip()
    else:
        for char_code in range(ord('A'), ord('Z') + 1):
            candidate = f"Zone {chr(char_code)}"
            if candidate not in existing_zones:
                assigned_zone = candidate
                break
        else:
            assigned_zone = f"Zone {len(BINARY_TREE_STRUCTURE) + 1}"

    # Node Role
    if role and str(role).strip():
        assigned_role = str(role).strip()
    elif new_level == 1:
        assigned_role = "Major Sector Hub"
    elif new_level == 2:
        assigned_role = "Sub-Zone Command"
    else:
        assigned_role = "Local Ward Division"

    desc = description or f"Municipal civic division under {parent_node}"

    node_id = f"node_{len(BINARY_TREE_STRUCTURE) + 1}"
    BINARY_TREE_STRUCTURE[node_name] = {
        "id": node_id,
        "role": assigned_role,
        "level": new_level,
        "parent": parent_node,
        "left": None,
        "right": None,
        "zone": assigned_zone,
        "code": assigned_zone,
        "short": node_name[:14],
        "description": desc,
        "icon": "fa-solid fa-map-pin",
        "color": {
            "fill": "#0f2027",
            "stroke": "#10b981",
            "text": "#ecfdf5",
            "badge": "#059669"
        }
    }

    POINT_LAYOUT_COORDINATES[node_name] = {
        "x": final_x,
        "y": new_y,
        "r": 25,
        "short": node_name[:14],
        "level": new_level
    }

    ZONE_ALIASES[node_name] = assigned_zone

    # Register in Adjacency Graph
    if node_name not in graph:
        graph[node_name] = []
    if parent_node not in graph:
        graph[parent_node] = []

    if parent_node not in graph[node_name]:
        graph[node_name].append(parent_node)
    if node_name not in graph[parent_node]:
        graph[parent_node].append(node_name)

    # Register Edge
    edge_exists = any((u == parent_node and v == node_name) or (u == node_name and v == parent_node) for u, v, *_ in TREE_EDGES)
    if not edge_exists:
        TREE_EDGES.append((parent_node, node_name, assigned_branch))

    _save_dynamic_nodes()
    return True, f"Location node '{node_name}' ({assigned_zone}) successfully added under '{parent_node}'."


# ==========================================
# Civic Area Graph Class (Object-Oriented)
# ==========================================

class CivicAreaGraph:
    def __init__(self):
        self.adj = {}

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []

    def add_vertex(self, node):
        self.add_node(node)

    def add_edge(self, u, v):
        self.add_node(u)
        self.add_node(v)
        if v not in self.adj[u]:
            self.adj[u].append(v)
        if u not in self.adj[v]:
            self.adj[v].append(u)

    def bfs(self, start):
        visited = []
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.append(node)
                for neighbor in self.adj.get(node, []):
                    if neighbor not in visited:
                        queue.append(neighbor)
        return visited

    def clear(self):
        self.adj = {}

    def to_dict(self):
        return self.adj
