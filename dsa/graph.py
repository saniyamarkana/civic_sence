# ==========================================
# Simple Graph with Add Node & BFS Traversal
# ==========================================

# Graph Representation (Adjacency List)
graph = {
    "Zone A": ["Zone B", "Zone C"],
    "Zone B": ["Zone A", "Zone D"],
    "Zone C": ["Zone A", "Zone D"],
    "Zone D": ["Zone B", "Zone C"]
}

ZONE_ALIASES = {}
ROOT_NODE = "Zone A"


# ==========================================
# Add Node / Edge Facility
# ==========================================

def add_node(node_name, neighbors=None):
    """Add a new node to the graph with optional neighbors."""
    if node_name not in graph:
        graph[node_name] = []
    
    if neighbors:
        for neighbor in neighbors:
            add_edge(node_name, neighbor)


def add_edge(node1, node2):
    """Add an undirected connection (edge) between two nodes."""
    if node1 not in graph:
        graph[node1] = []
    if node2 not in graph:
        graph[node2] = []
        
    if node2 not in graph[node1]:
        graph[node1].append(node2)
    if node1 not in graph[node2]:
        graph[node2].append(node1)


# ==========================================
# Basic BFS (Breadth-First Search) Algorithm
# ==========================================

def bfs(start="Zone A", target=None):
    """Basic BFS traversal starting from a node using Queue (FIFO)."""
    visited = []
    queue = [start]

    while queue:
        node = queue.pop(0)  # Take first node from queue

        if node not in visited:
            visited.append(node)

            # Stop if target node is found
            if target and node == target:
                break

            # Add all connected unvisited neighbors
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    queue.append(neighbor)

    return visited


def bfs_search(start, target=None):
    """Search if target is reachable using BFS."""
    if target is None:
        target = start
        start = "Zone A"
    visited = bfs(start, target)
    return target in visited


def bfs_shortest_path(start, target):
    """Find shortest path between start and target using BFS."""
    queue = [[start]]
    visited = []

    while queue:
        path = queue.pop(0)
        node = path[-1]

        if node == target:
            return path

        if node not in visited:
            visited.append(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    queue.append(path + [neighbor])

    return []


def bfs_with_steps(start="Zone A", target=None):
    """Returns BFS traversal order along with step history."""
    visited = bfs(start, target)
    steps = []

    for i, node in enumerate(visited, 1):
        steps.append({
            "step": i,
            "visiting": node,
            "visited_state": visited[:i]
        })

    return {
        "start": start,
        "visited": visited,
        "steps": steps
    }


def dfs(node="Zone A", visited=None):
    """Basic fallback traversal."""
    return bfs(node)


def dfs_with_steps(start="Zone A"):
    """Basic fallback step traversal."""
    return bfs_with_steps(start)


def get_map_data():
    """Get graph nodes and edges for visualization."""
    edges = []
    for area in graph:
        for neighbour in graph[area]:
            if [neighbour, area] not in edges:
                edges.append([area, neighbour])

    return {
        "root": ROOT_NODE,
        "nodes": list(graph.keys()),
        "edges": edges,
        "zone_aliases": ZONE_ALIASES
    }


def get_bfs_graph_html(start="Zone A"):
    """Get simple BFS HTML layout."""
    visited = bfs(start)
    html = "<div><h3>BFS Traversal</h3>"
    for i, node in enumerate(visited, 1):
        html += f"<p>{i}. {node}</p>"
    html += "</div>"
    return html


# ==========================================
# Civic Area Graph Class (Object-Oriented)
# ==========================================

class CivicAreaGraph:
    def __init__(self):
        self.adj = {}

    def add_node(self, node):
        """Add node to graph."""
        if node not in self.adj:
            self.adj[node] = []

    def add_vertex(self, node):
        """Alias for add_node."""
        self.add_node(node)

    def add_edge(self, u, v):
        """Add undirected edge between two nodes."""
        self.add_node(u)
        self.add_node(v)
        if v not in self.adj[u]:
            self.adj[u].append(v)
        if u not in self.adj[v]:
            self.adj[v].append(u)

    def bfs(self, start):
        """Basic BFS on dynamic graph."""
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