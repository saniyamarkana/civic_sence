# Simple Graph for Civic Sense

graph = {
    "Depot": ["Ward 1", "Ward 2"],
    "Ward 1": ["Depot", "Ward 3"],
    "Ward 2": ["Depot", "Ward 4"],
    "Ward 3": ["Ward 1", "Ward 4"],
    "Ward 4": ["Ward 2", "Ward 3"]
}

# Display Graph
print("Adjacency List:")
for node in graph:
    print(node, "->", graph[node])


# BFS
def bfs(start):
    visited = []
    queue = [start]

    while queue:
        node = queue.pop(0)

        if node not in visited:
            visited.append(node)

            for neighbour in graph[node]:
                if neighbour not in visited:
                    queue.append(neighbour)

    return visited


# DFS
def dfs(node, visited=None):
    if visited is None:
        visited = []

    visited.append(node)

    for neighbour in graph[node]:
        if neighbour not in visited:
            dfs(neighbour, visited)

    return visited


# BFS
print("\nBFS:")
print(bfs("Depot"))

# DFS
print("\nDFS:")
print(dfs("Depot"))