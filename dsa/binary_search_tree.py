# Binary Search Tree – Search Complaints

class Node:
    def __init__(self, id, complaint):
        self.id        = id
        self.complaint = complaint
        self.left      = None
        self.right     = None


class BST:
    def __init__(self):
        self.root = None

    # Insert complaint
    def insert(self, id, complaint):
        new_node = Node(id, complaint)
        if self.root is None:
            self.root = new_node
            return
        current = self.root
        while True:
            if id < current.id:
                if current.left is None:
                    current.left = new_node
                    return
                current = current.left
            elif id > current.id:
                if current.right is None:
                    current.right = new_node
                    return
                current = current.right
            else:
                return

    # Search complaint by ID
    def search(self, id):
        current = self.root
        while current:
            if id == current.id:
                return current
            elif id < current.id:
                current = current.left
            else:
                current = current.right
        return None


if __name__ == "__main__":
    bst = BST()

    bst.insert(5, "Water Leakage")
    bst.insert(2, "Pothole Near School")
    bst.insert(8, "Park Cleaning")
    bst.insert(1, "Garbage Overflow")
    bst.insert(4, "Broken Streetlight")

    # Search
    result = bst.search(4)
    if result:
        print(f"Found: ID {result.id} | {result.complaint}")
    else:
        print("Not Found")

    result = bst.search(9)
    if result:
        print(f"Found: ID {result.id} | {result.complaint}")
    else:
        print("Not Found")