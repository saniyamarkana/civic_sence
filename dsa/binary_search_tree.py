# Simple Binary Search Tree for Civic Sense

class Node:
    def __init__(self, id, complaint):
        self.id = id
        self.complaint = complaint
        self.left = None
        self.right = None


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
                print("Complaint ID already exists")
                return

    # Search complaint
    def search(self, id):
        current = self.root

        while current is not None:
            if id == current.id:
                return current

            elif id < current.id:
                current = current.left

            else:
                current = current.right

        return None

    # In-order traversal
    def inorder(self, node):
        if node is not None:
            self.inorder(node.left)
            print("ID:", node.id, "Complaint:", node.complaint)
            self.inorder(node.right)


# Create BST
bst = BST()

# Add complaints
bst.insert(5, "Water Leakage")
bst.insert(2, "Pothole")
bst.insert(8, "Park Cleaning")
bst.insert(1, "Garbage Overflow")
bst.insert(4, "Broken Streetlight")

# Search complaint
result = bst.search(4)

if result:
    print("Complaint Found:", result.complaint)
else:
    print("Complaint Not Found")


# Display complaints in sorted order
print("\nComplaints in Sorted Order:")
bst.inorder(bst.root)