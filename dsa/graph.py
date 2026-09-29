# Graph - Complaint Area Location Network & BFS / DFS Traversal
# Uses exact complaint form location areas mapped to Zone A, Zone B, Zone C, Zone D, etc.

import re as _re
import json as _json

# 1. Graph Representation using Adjacency List
# Matching the city complaint areas network (including core diamond & peripheral zones)
graph = {
    "Central Zone (Chowk)": [
        "West Zone (Adajan)",
        "Varachha Zone A",
        "North Zone (Katargam)",
        "Shakti Nagar",
        "South Zone (Udhana)",
        "South West (Athwa)",
    ],
    "West Zone (Adajan)": [
        "Central Zone (Chowk)",
        "South Zone (Udhana)",
        "South West (Athwa)",
        "North Zone (Katargam)",
    ],
    "Varachha Zone A": [
        "Central Zone (Chowk)",
        "South Zone (Udhana)",
        "Varachha Zone B",
        "South East (Dindoli)",
        "North Zone (Katargam)",
    ],
    "South Zone (Udhana)": [
        "West Zone (Adajan)",
        "Varachha Zone A",
        "South West (Athwa)",
        "South East (Dindoli)",
        "Central Zone (Chowk)",
    ],
    "North Zone (Katargam)": [
        "Central Zone (Chowk)",
        "West Zone (Adajan)",
    ],
    "South West (Athwa)": [
        "West Zone (Adajan)",
        "South Zone (Udhana)",
        "Central Zone (Chowk)",
    ],
    "Varachha Zone B": [
        "Varachha Zone A",
        "South East (Dindoli)",
    ],
    "South East (Dindoli)": [
        "Varachha Zone A",
        "South Zone (Udhana)",
        "Varachha Zone B",
    ],
    "Shakti Nagar": [
        "Central Zone (Chowk)",
    ],
}

# The specific 11 edges depicted in the reference screenshot:
SCREENSHOT_EDGES = [
    ("North Zone (Katargam)", "Central Zone (Chowk)"),
    ("Central Zone (Chowk)",  "Shakti Nagar"),
    ("Central Zone (Chowk)",  "West Zone (Adajan)"),
    ("Central Zone (Chowk)",  "Varachha Zone A"),
    ("West Zone (Adajan)",    "South West (Athwa)"),
    ("West Zone (Adajan)",    "South Zone (Udhana)"),
    ("South West (Athwa)",    "South Zone (Udhana)"),
    ("Varachha Zone A",       "South Zone (Udhana)"),
    ("Varachha Zone A",       "Varachha Zone B"),
    ("Varachha Zone A",       "South East (Dindoli)"),
    ("South Zone (Udhana)",   "South East (Dindoli)"),
]

# Project Zone Aliases (Zone A, Zone B, Zone C, Zone D...)
ZONE_ALIASES = {
    "Central Zone (Chowk)":  "Zone A",
    "West Zone (Adajan)":    "Zone B",
    "Varachha Zone A":       "Zone C",
    "South Zone (Udhana)":   "Zone D",
    "North Zone (Katargam)": "Zone E",
    "South West (Athwa)":    "Zone F",
    "Varachha Zone B":       "Zone G",
    "South East (Dindoli)":  "Zone H",
    "Shakti Nagar":          "Zone I",
}

# Real-world Surat GPS Coordinates
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

# 2D Point Coordinates for SVG Map Layout
POINT_LAYOUT_COORDINATES = {
    "Central Zone (Chowk)":  {"x": 410, "y": 110, "short": "Central\nChowk"},
    "West Zone (Adajan)":    {"x": 215, "y": 245, "short": "Adajan\n(West)"},
    "Varachha Zone A":       {"x": 600, "y": 245, "short": "Varachha A"},
    "South Zone (Udhana)":   {"x": 430, "y": 400, "short": "Udhana\n(South)"},
    "North Zone (Katargam)": {"x": 95,  "y": 125, "short": "Kataragam"},
    "South West (Athwa)":    {"x": 82,  "y": 390, "short": "Athwa"},
    "Varachha Zone B":       {"x": 855, "y": 255, "short": "Varachha B"},
    "South East (Dindoli)":  {"x": 790, "y": 400, "short": "Dindoli"},
    "Shakti Nagar":          {"x": 720, "y": 125, "short": "Shakti Nagar"},
}


def get_map_data():
    """
    Returns full network data (nodes with coordinates, aliases, and edges)
    for rendering in Admin frontend.
    """
    nodes = []
    for area, coords in MAP_COORDINATES.items():
        layout = POINT_LAYOUT_COORDINATES.get(area, {"x": 400, "y": 200, "short": area})
        nodes.append({
            "area": area,
            "code": ZONE_ALIASES.get(area, "Zone"),
            "zone": ZONE_ALIASES.get(area, "Zone"),
            "lat": coords[0],
            "lng": coords[1],
            "x": layout["x"],
            "y": layout["y"],
            "short_label": layout["short"].replace("\n", " "),
        })

    edges = []
    seen = set()
    for u, v in SCREENSHOT_EDGES:
        pair = tuple(sorted([u, v]))
        if pair not in seen:
            seen.add(pair)
            edges.append({"from": u, "to": v})

    return {
        "nodes": nodes,
        "edges": edges,
        "zone_aliases": ZONE_ALIASES
    }


# 2. BFS Traversal (Breadth-First Search) using Queue (FIFO)
def bfs(start, target=None):
    if start not in graph:
        return []

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


# 3. BFS Shortest Path
def bfs_shortest_path(start, target):
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


# 4. BFS Traversal with Step-by-Step State Recording
def bfs_with_steps(start, target=None):
    if start not in graph:
        return {"start": start, "target": target, "visited": [], "steps": [], "shortest_path": []}

    visited = []
    queue = [start]
    visited.append(start)
    steps = []
    step_num = 1

    steps.append({
        "step": step_num,
        "visiting": start,
        "queue_state": list(queue),
        "visited_state": list(visited),
        "discovered": []
    })

    while queue:
        current = queue.pop(0)

        if target and current == target:
            break

        discovered_now = []
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.append(neighbor)
                queue.append(neighbor)
                discovered_now.append(neighbor)

        step_num += 1
        steps.append({
            "step": step_num,
            "visiting": current,
            "queue_state": list(queue),
            "visited_state": list(visited),
            "discovered": discovered_now
        })

    shortest_path = []
    if target:
        shortest_path = bfs_shortest_path(start, target)

    return {
        "start": start,
        "target": target,
        "visited": visited,
        "steps": steps,
        "shortest_path": shortest_path
    }


# 5. DFS Traversal (Depth-First Search)
def dfs(node, visited=None):
    if visited is None:
        visited = []

    if node not in visited:
        visited.append(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor, visited)

    return visited


def dfs_with_steps(start):
    if start not in graph:
        return {"start": start, "visited": [], "steps": []}

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

            steps.append({
                "step": step_num,
                "visiting": current,
                "stack_state": list(stack),
                "visited_state": list(visited)
            })
            step_num += 1

    return {
        "start": start,
        "visited": visited,
        "steps": steps
    }


# =============================================================================
# 6. BFS Graph HTML Visualizer
#    Exact match for reference screenshot:
#      - Pale banner: "This graph shows the connected complaint areas in the city..."
#      - 9 pastel nodes: Katargam (green), Central Chowk (blue + red ring + badge 1),
#        Shakti Nagar (purple), Adajan West (orange + badge 2), Varachha A (teal + badge 3),
#        Varachha B (purple), Athwa (pink), Udhana South (blue + badge 4), Dindoli (green)
#      - 11 dark grey connection edges
#      - Interactive BFS traversal: Play, Step, Pause, Reset, Speed Control
#      - Live FIFO Queue visualizer + step explanation + adjacency list
# =============================================================================

# Exact colors from reference screenshot
_NODE_COLORS = {
    "Central Zone (Chowk)":  {"fill": "#bbdefb", "stroke": "#1976d2", "text": "#0d47a1", "badge": "#ef4444", "badge_pos": "top-left"},
    "West Zone (Adajan)":    {"fill": "#ffe082", "stroke": "#f57c00", "text": "#b26a00", "badge": "#f59e0b", "badge_pos": "top-right"},
    "Varachha Zone A":       {"fill": "#80cbc4", "stroke": "#00695c", "text": "#004d40", "badge": "#f59e0b", "badge_pos": "top-right"},
    "South Zone (Udhana)":   {"fill": "#90caf9", "stroke": "#1565c0", "text": "#0d47a1", "badge": "#f59e0b", "badge_pos": "top-right"},
    "North Zone (Katargam)": {"fill": "#c8e6c9", "stroke": "#2e7d32", "text": "#1b5e20", "badge": "#10b981", "badge_pos": "top-right"},
    "South West (Athwa)":    {"fill": "#f8bbd0", "stroke": "#c2185b", "text": "#880e4f", "badge": "#ec4899", "badge_pos": "top-right"},
    "Varachha Zone B":       {"fill": "#e1bee7", "stroke": "#6a1b9a", "text": "#4a148c", "badge": "#8b5cf6", "badge_pos": "top-right"},
    "South East (Dindoli)":  {"fill": "#c8e6c9", "stroke": "#2e7d32", "text": "#1b5e20", "badge": "#10b981", "badge_pos": "top-right"},
    "Shakti Nagar":          {"fill": "#e1bee7", "stroke": "#6a1b9a", "text": "#4a148c", "badge": "#8b5cf6", "badge_pos": "top-right"},
}

# Layout on 940 x 480 canvas
_BFS_LAYOUT = {
    "Central Zone (Chowk)":  {"x": 410, "y": 110, "r": 50, "short": "Central\nChowk"},
    "West Zone (Adajan)":    {"x": 215, "y": 245, "r": 48, "short": "Adajan\n(West)"},
    "Varachha Zone A":       {"x": 600, "y": 245, "r": 48, "short": "Varachha A"},
    "South Zone (Udhana)":   {"x": 430, "y": 400, "r": 48, "short": "Udhana\n(South)"},
    "North Zone (Katargam)": {"x": 95,  "y": 125, "r": 44, "short": "Kataragam"},
    "South West (Athwa)":    {"x": 82,  "y": 390, "r": 44, "short": "Athwa"},
    "Varachha Zone B":       {"x": 855, "y": 255, "r": 44, "short": "Varachha B"},
    "South East (Dindoli)":  {"x": 790, "y": 400, "r": 44, "short": "Dindoli"},
    "Shakti Nagar":          {"x": 720, "y": 125, "r": 44, "short": "Shakti Nagar"},
}

# The 11 screenshot edges
_BFS_EDGES = [
    ("North Zone (Katargam)", "Central Zone (Chowk)"),
    ("Central Zone (Chowk)",  "Shakti Nagar"),
    ("Central Zone (Chowk)",  "West Zone (Adajan)"),
    ("Central Zone (Chowk)",  "Varachha Zone A"),
    ("West Zone (Adajan)",    "South West (Athwa)"),
    ("West Zone (Adajan)",    "South Zone (Udhana)"),
    ("South West (Athwa)",    "South Zone (Udhana)"),
    ("Varachha Zone A",       "South Zone (Udhana)"),
    ("Varachha Zone A",       "Varachha Zone B"),
    ("Varachha Zone A",       "South East (Dindoli)"),
    ("South Zone (Udhana)",   "South East (Dindoli)"),
]

def _safe(name: str) -> str:
    return _re.sub(r"[^a-zA-Z0-9]", "_", name)


def get_bfs_graph_html(start_node: str = "Central Zone (Chowk)") -> str:
    """
    Generate an interactive, self-contained HTML+CSS+JS component that renders
    the exact graph visualization from the reference screenshot with BFS operation.
    """
    if start_node not in _BFS_LAYOUT:
        start_node = "Central Zone (Chowk)"

    # Static default badges (1, 2, 3, 4 for the screenshot state)
    default_badges = {
        "Central Zone (Chowk)": "1",
        "West Zone (Adajan)":   "2",
        "Varachha Zone A":      "3",
        "South Zone (Udhana)":  "4",
    }

    # 1. SVG Edges
    svg_edges = ""
    for u, v in _BFS_EDGES:
        pos_u = _BFS_LAYOUT.get(u)
        pos_v = _BFS_LAYOUT.get(v)
        if not pos_u or not pos_v:
            continue
        edge_id = "bfse_" + _safe(u) + "_" + _safe(v)
        svg_edges += (
            f'<line id="{edge_id}" data-u="{u}" data-v="{v}" '
            f'x1="{pos_u["x"]}" y1="{pos_u["y"]}" x2="{pos_v["x"]}" y2="{pos_v["y"]}" '
            f'stroke="#576574" stroke-width="2.6" stroke-linecap="round" '
            f'style="transition: stroke 0.3s ease, stroke-width 0.3s ease;" />\n'
        )

    # 2. SVG Nodes
    svg_nodes = ""
    for area, pos in _BFS_LAYOUT.items():
        sid = _safe(area)
        col = _NODE_COLORS.get(area, {"fill": "#e2e8f0", "stroke": "#64748b", "text": "#1e293b", "badge": "#f59e0b", "badge_pos": "top-right"})
        cx = pos["x"]
        cy = pos["y"]
        r = pos["r"]
        short_lines = pos["short"].split("\n")
        badge_val = default_badges.get(area, "")
        badge_visible = "inline" if badge_val else "none"

        if col.get("badge_pos") == "top-left":
            bx = cx - int(r * 0.72)
            by = cy - int(r * 0.72)
        else:
            bx = cx + int(r * 0.72)
            by = cy - int(r * 0.72)

        if len(short_lines) == 1:
            label_svg = f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b" font-family="Segoe UI,system-ui,sans-serif" style="pointer-events:none;">{short_lines[0]}</text>'
        else:
            label_svg = (
                f'<text x="{cx}" y="{cy - 5}" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b" font-family="Segoe UI,system-ui,sans-serif" style="pointer-events:none;">{short_lines[0]}</text>'
                f'<text x="{cx}" y="{cy + 13}" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b" font-family="Segoe UI,system-ui,sans-serif" style="pointer-events:none;">{short_lines[1]}</text>'
            )

        ring_stroke = "#ef4444" if area == "Central Zone (Chowk)" else "transparent"
        ring_svg = f'<circle id="bfsActiveRing_{sid}" cx="{cx}" cy="{cy}" r="{r + 7}" fill="none" stroke="{ring_stroke}" stroke-width="2.6" style="transition: all 0.3s ease;" />'

        svg_nodes += f'''
        <g id="bfsn_{sid}" data-area="{area}" onclick="window.bfsSelectNode('{area}')" style="cursor: pointer;">
          {ring_svg}
          <circle id="bfsh_{sid}" cx="{cx}" cy="{cy}" r="{r + 14}" fill="transparent" style="transition: fill 0.3s ease;" />
          <circle id="bfsc_{sid}" cx="{cx}" cy="{cy}" r="{r}"
                  fill="{col["fill"]}" stroke="{col["stroke"]}" stroke-width="3"
                  style="transition: all 0.3s ease; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.08));" />
          {label_svg}
          <g id="bfsbg_{sid}" style="display: {badge_visible}; pointer-events: none;">
            <circle id="bfsbc_{sid}" cx="{bx}" cy="{by}" r="12.5" fill="{col["badge"]}" stroke="#ffffff" stroke-width="2" />
            <text id="bfsbt_{sid}" x="{bx}" y="{by + 4}" text-anchor="middle" font-size="11" font-weight="900" fill="#ffffff" font-family="Segoe UI,system-ui,sans-serif">{badge_val}</text>
          </g>
        </g>
'''

    # 3. Selector Options
    options_html = ""
    for a in _BFS_LAYOUT.keys():
        sel = 'selected="selected"' if a == start_node else ''
        clean_lbl = _BFS_LAYOUT[a]["short"].replace("\n", " ")
        options_html += f'<option value="{a}" {sel}>{clean_lbl} ({ZONE_ALIASES.get(a, "Zone")})</option>\n'

    # 4. Adjacency Table
    adj_rows = ""
    for a, neighbors in graph.items():
        col = _NODE_COLORS.get(a, {}).get("stroke", "#475569")
        clean_a = _BFS_LAYOUT.get(a, {}).get("short", a).replace("\n", " ")
        nb_clean = " &bull; ".join(_BFS_LAYOUT.get(n, {}).get("short", n).replace("\n", " ") for n in neighbors)
        adj_rows += f'''
        <tr style="border-bottom: 1px solid #e2e8f0;">
          <td style="padding: 8px 12px; font-weight: 700; color: {col}; white-space: nowrap;">{clean_a}</td>
          <td style="padding: 8px 12px; color: #475569; font-size: 12px;">{nb_clean}</td>
        </tr>
'''

    js_layout = _json.dumps({
        k: {
            "x": v["x"], "y": v["y"], "r": v["r"],
            "short": v["short"].replace("\n", " "),
            "fill": _NODE_COLORS.get(k, {}).get("fill", "#e2e8f0"),
            "stroke": _NODE_COLORS.get(k, {}).get("stroke", "#64748b"),
            "badge": _NODE_COLORS.get(k, {}).get("badge", "#f59e0b"),
            "badge_pos": _NODE_COLORS.get(k, {}).get("badge_pos", "top-right"),
            "sid": _safe(k)
        } for k, v in _BFS_LAYOUT.items()
    })
    js_edges = _json.dumps(_BFS_EDGES)
    js_graph = _json.dumps(graph)

    # Return pure HTML string assembled cleanly with placeholders
    template = """<!-- ════════════════════════════════════════════════════════════════
     REFERENCE BFS GRAPH VISUALIZER (Generated by dsa/graph.py)
     ════════════════════════════════════════════════════════════════ -->
<div id="civicBfsVisualizerCard" style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); overflow: hidden; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; margin-bottom: 24px;">

  <!-- 1. Top Reference Banner (Matches Screenshot Header) -->
  <div style="background: #f0f7ff; border-bottom: 1px solid #dbeafe; padding: 14px 22px; color: #334155; font-size: 14px; font-weight: 500; line-height: 1.55; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
    <div style="display: flex; align-items: center; gap: 10px;">
      <i class="fa-solid fa-circle-info" style="color: #3b82f6; font-size: 16px;"></i>
      <span>This graph shows the connected complaint areas in the city. Each area is a node and the connections represent nearby or related areas.</span>
    </div>
    <span style="font-size: 11px; font-weight: 800; background: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 12px; letter-spacing: 0.5px; text-transform: uppercase;">
      BFS &bull; O(V + E)
    </span>
  </div>

  <!-- 2. Interactive Control Bar -->
  <div style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
    <!-- Start Node Selector -->
    <div style="display: flex; align-items: center; gap: 8px;">
      <span style="font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px;">Start Node:</span>
      <select id="bfsStartSelectCtrl" onchange="window.bfsChangeStart(this.value)"
              style="padding: 7px 12px; font-size: 13px; font-weight: 600; color: #1e293b; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; outline: none; cursor: pointer;">
        __OPTIONS_HTML__
      </select>
    </div>

    <!-- Playback Buttons -->
    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
      <button id="bfsBtnPlay" onclick="window.bfsTogglePlay()"
              style="display: inline-flex; align-items: center; gap: 6px; padding: 7px 16px; font-size: 13px; font-weight: 700; color: #ffffff; background: #2563eb; border: none; border-radius: 8px; cursor: pointer; transition: background 0.2s; box-shadow: 0 2px 6px rgba(37,99,235,0.3);">
        <i class="fa-solid fa-play"></i> <span>Run BFS Animation</span>
      </button>

      <button onclick="window.bfsStepForward()"
              style="display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; font-size: 12px; font-weight: 700; color: #334155; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; cursor: pointer; transition: background 0.2s;">
        <i class="fa-solid fa-forward-step"></i> Next Step
      </button>

      <button onclick="window.bfsReset()"
              style="display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; font-size: 12px; font-weight: 700; color: #64748b; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; cursor: pointer; transition: background 0.2s;">
        <i class="fa-solid fa-rotate-left"></i> Reset
      </button>

      <!-- Speed Control -->
      <div style="display: flex; align-items: center; gap: 5px; margin-left: 8px;">
        <span style="font-size: 11px; font-weight: 700; color: #64748b;">Speed:</span>
        <select id="bfsSpeedSelect" onchange="window.bfsSetSpeed(this.value)"
                style="padding: 5px 8px; font-size: 12px; font-weight: 600; color: #334155; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px;">
          <option value="1200">Slow (1.2s)</option>
          <option value="750" selected>Normal (0.75s)</option>
          <option value="400">Fast (0.4s)</option>
        </select>
      </div>
    </div>
  </div>

  <!-- 3. SVG Canvas (Matches Reference Image) -->
  <div style="background: #ffffff; padding: 14px 10px; position: relative; overflow-x: auto;">
    <svg id="civicBfsSvg" viewBox="0 0 940 480" width="100%" height="auto" style="display: block; min-width: 680px; max-height: 480px; margin: 0 auto;">
      <g id="bfsEdgesGroup">
        __SVG_EDGES__
      </g>
      <g id="bfsNodesGroup">
        __SVG_NODES__
      </g>
    </svg>
  </div>

  <!-- 4. Live BFS Status, Queue & Explanation Dashboard -->
  <div style="background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 18px 22px;">
    <!-- Step Explanation Card -->
    <div id="bfsExplainCard" style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; border-radius: 10px; padding: 12px 18px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
        <span id="bfsStepBadge" style="font-size: 11px; font-weight: 800; color: #2563eb; text-transform: uppercase; letter-spacing: 0.5px;">Ready to Traverse</span>
        <span id="bfsProgressText" style="font-size: 11px; color: #64748b; font-weight: 600;">Central Chowk</span>
      </div>
      <div id="bfsExplainText" style="font-size: 13px; color: #1e293b; font-weight: 500; line-height: 1.5;">
        Click <strong>Run BFS Animation</strong> or any node on the graph to start breadth-first search traversal from that location.
      </div>
    </div>

    <!-- Two-Column Queue & Visited Status -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
      <!-- FIFO Queue Display -->
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px;">
        <div style="font-size: 11px; font-weight: 800; color: #0284c7; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
          <i class="fa-solid fa-arrows-turn-to-dots"></i> BFS Queue (FIFO &bull; First-In, First-Out)
        </div>
        <div id="bfsQueueDisplay" style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; min-height: 32px;">
          <span style="font-size: 12px; color: #94a3b8; font-style: italic;">Queue empty (idle)</span>
        </div>
      </div>

      <!-- Visited Order Display -->
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px;">
        <div style="font-size: 11px; font-weight: 800; color: #16a34a; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
          <i class="fa-solid fa-list-ol"></i> Visited Order (BFS Sequence)
        </div>
        <div id="bfsVisitedDisplay" style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; min-height: 32px;">
          <span style="font-size: 12px; color: #94a3b8; font-style: italic;">No traversal executed yet</span>
        </div>
      </div>
    </div>

    <!-- Expandable Adjacency List Details -->
    <details style="margin-top: 14px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden;">
      <summary style="padding: 10px 16px; font-size: 12px; font-weight: 700; color: #475569; cursor: pointer; user-select: none; background: #f8fafc; outline: none;">
        <i class="fa-solid fa-table-list" style="margin-right: 6px; color: #64748b;"></i> View Graph Adjacency List Representation
      </summary>
      <div style="padding: 10px 16px; max-height: 240px; overflow-y: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
          <thead>
            <tr style="border-bottom: 2px solid #cbd5e1; text-align: left; color: #64748b; font-weight: 700;">
              <th style="padding: 6px 12px; width: 35%;">Area Node (V)</th>
              <th style="padding: 6px 12px;">Adjacent Neighbors (E)</th>
            </tr>
          </thead>
          <tbody>
            __ADJ_ROWS__
          </tbody>
        </table>
      </div>
    </details>
  </div>
</div>

<!-- ── Scoped BFS Engine JavaScript ── -->
<script>
(function() {
  const _layout = __JS_LAYOUT__;
  const _edges = __JS_EDGES__;
  const _graph = __JS_GRAPH__;

  let _startNode = "__START_NODE__";
  let _stepIndex = 0;
  let _steps = [];
  let _timer = null;
  let _isPlaying = false;
  let _speedMs = 750;

  function safeId(str) {
    return (str || "").replace(/[^a-zA-Z0-9]/g, "_");
  }

  function buildSteps(start) {
    const steps = [];
    if (!_graph[start]) return steps;

    const visited = [];
    const queue = [start];
    const inQueue = new Set([start]);
    let orderNum = 1;

    steps.push({
      action: "start",
      current: start,
      queue: [...queue],
      visited: [...visited],
      discovered: [start],
      activeEdge: null,
      msg: "Starting BFS at <strong>" + (_layout[start] ? _layout[start].short : start) + "</strong>. Enqueued as Node #1."
    });

    while (queue.length > 0) {
      const current = queue.shift();
      visited.push(current);

      const neighbors = _graph[current] || [];
      const newlyDiscovered = [];

      for (let i = 0; i < neighbors.length; i++) {
        const nb = neighbors[i];
        if (!visited.includes(nb) && !inQueue.has(nb)) {
          inQueue.add(nb);
          queue.push(nb);
          newlyDiscovered.push(nb);
          orderNum++;
        }
      }

      const nbNames = newlyDiscovered.map(function(n) { return _layout[n] ? _layout[n].short : n; }).join(", ");
      steps.push({
        action: "visit",
        current: current,
        queue: [...queue],
        visited: [...visited],
        discovered: newlyDiscovered,
        activeEdge: null,
        msg: "Visiting <strong>" + (_layout[current] ? _layout[current].short : current) + "</strong>. Discovered " + newlyDiscovered.length + " neighbor(s): " + (nbNames || "None") + "."
      });
    }

    return steps;
  }

  function applyStep(step) {
    if (!step) return;

    const stepBadge = document.getElementById("bfsStepBadge");
    const progressText = document.getElementById("bfsProgressText");
    const explainText = document.getElementById("bfsExplainText");

    if (stepBadge) stepBadge.textContent = step.action === "start" ? "Queue Initialized" : ("Step " + (_stepIndex + 1) + " of " + _steps.length);
    if (progressText) progressText.textContent = "Visiting: " + (_layout[step.current] ? _layout[step.current].short : step.current);
    if (explainText) explainText.innerHTML = step.msg;

    Object.keys(_layout).forEach(function(area) {
      const sid = safeId(area);
      const ring = document.getElementById("bfsActiveRing_" + sid);
      const halo = document.getElementById("bfsh_" + sid);
      const circ = document.getElementById("bfsc_" + sid);
      const badgeGroup = document.getElementById("bfsbg_" + sid);
      const badgeText = document.getElementById("bfsbt_" + sid);
      const badgeCirc = document.getElementById("bfsbc_" + sid);

      const isVisited = step.visited.includes(area);
      const isCurrent = step.current === area;
      const isEnqueued = step.queue.includes(area);
      const nodeCol = _layout[area] || {};

      if (ring) {
        ring.setAttribute("stroke", isCurrent ? "#ef4444" : "transparent");
        ring.setAttribute("stroke-width", isCurrent ? "3" : "2.6");
      }

      if (halo) {
        halo.setAttribute("fill", isCurrent ? "rgba(239, 68, 68, 0.2)" : (isVisited ? "rgba(16, 185, 129, 0.15)" : "transparent"));
      }

      if (circ) {
        if (isCurrent) {
          circ.setAttribute("fill", nodeCol.fill || "#dbeafe");
          circ.setAttribute("stroke", "#ef4444");
          circ.setAttribute("stroke-width", "3.5");
        } else if (isVisited) {
          circ.setAttribute("fill", nodeCol.fill || "#dcfce7");
          circ.setAttribute("stroke", nodeCol.stroke || "#16a34a");
          circ.setAttribute("stroke-width", "3");
        } else if (isEnqueued) {
          circ.setAttribute("fill", nodeCol.fill || "#fef3c7");
          circ.setAttribute("stroke", "#f59e0b");
          circ.setAttribute("stroke-width", "2.8");
        } else {
          circ.setAttribute("fill", nodeCol.fill || "#f1f5f9");
          circ.setAttribute("stroke", nodeCol.stroke || "#64748b");
          circ.setAttribute("stroke-width", "2.6");
        }
      }

      if (badgeGroup && badgeText && badgeCirc) {
        const orderIdx = step.visited.indexOf(area);
        if (orderIdx !== -1) {
          badgeGroup.style.display = "inline";
          badgeText.textContent = (orderIdx + 1);
          badgeCirc.setAttribute("fill", orderIdx === 0 ? "#ef4444" : "#f59e0b");
        } else if (isCurrent && step.action === "start") {
          badgeGroup.style.display = "inline";
          badgeText.textContent = "1";
          badgeCirc.setAttribute("fill", "#ef4444");
        } else {
          badgeGroup.style.display = "none";
        }
      }
    });

    _edges.forEach(function(edge) {
      const u = edge[0];
      const v = edge[1];
      const edgeId1 = "bfse_" + safeId(u) + "_" + safeId(v);
      const edgeId2 = "bfse_" + safeId(v) + "_" + safeId(u);
      const el = document.getElementById(edgeId1) || document.getElementById(edgeId2);
      if (el) {
        const uVisited = step.visited.includes(u);
        const vVisited = step.visited.includes(v);
        if (uVisited && vVisited) {
          el.setAttribute("stroke", "#2563eb");
          el.setAttribute("stroke-width", "3.2");
        } else {
          el.setAttribute("stroke", "#576574");
          el.setAttribute("stroke-width", "2.6");
        }
      }
    });

    const queueDisp = document.getElementById("bfsQueueDisplay");
    if (queueDisp) {
      if (step.queue.length === 0) {
        queueDisp.innerHTML = '<span style="font-size: 12px; color: #94a3b8; font-style: italic;">Queue is currently empty</span>';
      } else {
        queueDisp.innerHTML = step.queue.map(function(q, idx) {
          const shortName = _layout[q] ? _layout[q].short : q;
          return '<span style="display: inline-flex; align-items: center; gap: 5px; background: #e0f2fe; border: 1.5px solid #0284c7; color: #0369a1; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 700;">' +
            '<span style="font-size: 10px; background: #0284c7; color: #fff; border-radius: 4px; padding: 1px 5px;">' + (idx === 0 ? "FRONT" : idx) + '</span> ' +
            shortName +
          '</span>';
        }).join("");
      }
    }

    const visitedDisp = document.getElementById("bfsVisitedDisplay");
    if (visitedDisp) {
      if (step.visited.length === 0) {
        visitedDisp.innerHTML = '<span style="font-size: 12px; color: #94a3b8; font-style: italic;">No nodes visited yet</span>';
      } else {
        visitedDisp.innerHTML = step.visited.map(function(v, idx) {
          const shortName = _layout[v] ? _layout[v].short : v;
          const bgCol = idx === 0 ? "#ef4444" : "#f59e0b";
          return '<span style="display: inline-flex; align-items: center; gap: 5px; background: #dcfce7; border: 1.5px solid #16a34a; color: #15803d; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 700;">' +
            '<span style="font-size: 10px; background: ' + bgCol + '; color: #fff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center;">' + (idx + 1) + '</span> ' +
            shortName +
          '</span>';
        }).join("");
      }
    }
  }

  window.bfsSelectNode = function(area) {
    window.bfsChangeStart(area);
    window.bfsTogglePlay(true);
  };

  window.bfsChangeStart = function(area) {
    _startNode = area;
    const sel = document.getElementById("bfsStartSelectCtrl");
    if (sel && sel.value !== area) sel.value = area;
    window.bfsReset();
  };

  window.bfsTogglePlay = function(forcePlay) {
    if (forcePlay !== undefined) _isPlaying = !forcePlay;

    const btn = document.getElementById("bfsBtnPlay");
    if (_isPlaying) {
      _isPlaying = false;
      clearInterval(_timer);
      _timer = null;
      if (btn) btn.innerHTML = '<i class="fa-solid fa-play"></i> <span>Resume BFS</span>';
    } else {
      _isPlaying = true;
      if (btn) btn.innerHTML = '<i class="fa-solid fa-pause"></i> <span>Pause BFS</span>';

      if (_steps.length === 0 || _stepIndex >= _steps.length - 1) {
        _steps = buildSteps(_startNode);
        _stepIndex = 0;
        applyStep(_steps[0]);
      }

      clearInterval(_timer);
      _timer = setInterval(function() {
        if (_stepIndex < _steps.length - 1) {
          _stepIndex++;
          applyStep(_steps[_stepIndex]);
        } else {
          _isPlaying = false;
          clearInterval(_timer);
          _timer = null;
          if (btn) btn.innerHTML = '<i class="fa-solid fa-rotate-left"></i> <span>Restart BFS</span>';
          const explain = document.getElementById("bfsExplainText");
          if (explain) explain.innerHTML += " &bull; <strong style='color: #16a34a;'>BFS Traversal Completed!</strong>";
        }
      }, _speedMs);
    }
  };

  window.bfsStepForward = function() {
    if (_isPlaying) window.bfsTogglePlay();
    if (_steps.length === 0) {
      _steps = buildSteps(_startNode);
      _stepIndex = 0;
    } else if (_stepIndex < _steps.length - 1) {
      _stepIndex++;
    }
    applyStep(_steps[_stepIndex]);
  };

  window.bfsReset = function() {
    _isPlaying = false;
    clearInterval(_timer);
    _timer = null;
    _steps = buildSteps(_startNode);
    _stepIndex = 0;

    const btn = document.getElementById("bfsBtnPlay");
    if (btn) btn.innerHTML = '<i class="fa-solid fa-play"></i> <span>Run BFS Animation</span>';

    Object.keys(_layout).forEach(function(area) {
      const sid = safeId(area);
      const ring = document.getElementById("bfsActiveRing_" + sid);
      const halo = document.getElementById("bfsh_" + sid);
      const circ = document.getElementById("bfsc_" + sid);
      const badgeGroup = document.getElementById("bfsbg_" + sid);
      const badgeText = document.getElementById("bfsbt_" + sid);
      const badgeCirc = document.getElementById("bfsbc_" + sid);
      const nodeCol = _layout[area] || {};

      if (ring) ring.setAttribute("stroke", area === _startNode ? "#ef4444" : "transparent");
      if (halo) halo.setAttribute("fill", "transparent");
      if (circ) {
        circ.setAttribute("fill", nodeCol.fill || "#f1f5f9");
        circ.setAttribute("stroke", nodeCol.stroke || "#64748b");
        circ.setAttribute("stroke-width", "3");
      }

      const defBadges = {
        "Central Zone (Chowk)": "1",
        "West Zone (Adajan)": "2",
        "Varachha Zone A": "3",
        "South Zone (Udhana)": "4"
      };
      if (badgeGroup && badgeText && badgeCirc) {
        if (defBadges[area]) {
          badgeGroup.style.display = "inline";
          badgeText.textContent = defBadges[area];
          badgeCirc.setAttribute("fill", defBadges[area] === "1" ? "#ef4444" : "#f59e0b");
        } else {
          badgeGroup.style.display = "none";
        }
      }
    });

    _edges.forEach(function(edge) {
      const u = edge[0];
      const v = edge[1];
      const edgeId1 = "bfse_" + safeId(u) + "_" + safeId(v);
      const edgeId2 = "bfse_" + safeId(v) + "_" + safeId(u);
      const el = document.getElementById(edgeId1) || document.getElementById(edgeId2);
      if (el) {
        el.setAttribute("stroke", "#576574");
        el.setAttribute("stroke-width", "2.6");
      }
    });

    const stepBadge = document.getElementById("bfsStepBadge");
    const progressText = document.getElementById("bfsProgressText");
    const explainText = document.getElementById("bfsExplainText");
    const queueDisp = document.getElementById("bfsQueueDisplay");
    const visitedDisp = document.getElementById("bfsVisitedDisplay");

    if (stepBadge) stepBadge.textContent = "Ready to Traverse";
    if (progressText) progressText.textContent = "Start: " + (_layout[_startNode] ? _layout[_startNode].short : _startNode);
    if (explainText) explainText.innerHTML = "Click <strong>Run BFS Animation</strong> or any node on the graph to start breadth-first search traversal from that location.";
    if (queueDisp) queueDisp.innerHTML = '<span style="font-size: 12px; color: #94a3b8; font-style: italic;">Queue empty (idle)</span>';
    if (visitedDisp) visitedDisp.innerHTML = '<span style="font-size: 12px; color: #94a3b8; font-style: italic;">No traversal executed yet</span>';
  };

  window.bfsSetSpeed = function(val) {
    _speedMs = parseInt(val, 10) || 750;
    if (_isPlaying) {
      clearInterval(_timer);
      _timer = setInterval(function() {
        if (_stepIndex < _steps.length - 1) {
          _stepIndex++;
          applyStep(_steps[_stepIndex]);
        } else {
          _isPlaying = false;
          clearInterval(_timer);
          _timer = null;
        }
      }, _speedMs);
    }
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
        .replace("__START_NODE__", start_node)
    )
