# Graph – Complaint Area Network

# 1. Graph Representation using Adjacency List
graph = {
    "Central Chowk": ["Main Highway", "Market Area", "Bus Station"],
    "Main Highway": ["Central Chowk", "Hospital Zone"],
    "Market Area": ["Central Chowk", "Hospital Zone"],
    "Bus Station": ["Central Chowk", "Hospital Zone"],
    "Hospital Zone": ["Main Highway", "Market Area", "Bus Station"]
}


# 2. BFS Traversal
def bfs(start):
    visited = []
    queue = [start]

    while queue:
        node = queue.pop(0)

        if node not in visited:
            visited.append(node)

            for neighbor in graph[node]:
                if neighbor not in visited:
                    queue.append(neighbor)

    return visited


# 3. DFS Traversal
def dfs(node, visited=None):
    if visited is None:
        visited = []

    if node not in visited:
        visited.append(node)

        for neighbor in graph[node]:
            dfs(neighbor, visited)

    return visited


# 4. Test the Graph
print("Graph:")
for area, neighbors in graph.items():
    print(area, "->", neighbors)


print("\nBFS Traversal:")
print(" -> ".join(bfs("Central Chowk")))


print("\nDFS Traversal:")
print(" -> ".join(dfs("Central Chowk")))