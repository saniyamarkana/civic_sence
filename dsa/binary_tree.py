# Simple Binary Tree for Civic Sense

class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class BinaryTree:

    # Pre-order: Root -> Left -> Right
    def preorder(self, node):
        if node:
            print(node.data)
            self.preorder(node.left)
            self.preorder(node.right)

    # In-order: Left -> Root -> Right
    def inorder(self, node):
        if node:
            self.inorder(node.left)
            print(node.data)
            self.inorder(node.right)

    # Post-order: Left -> Right -> Root
    def postorder(self, node):
        if node:
            self.postorder(node.left)
            self.postorder(node.right)
            print(node.data)


# Create tree
root = Node("Municipal Commissioner")

root.left = Node("Infrastructure")
root.right = Node("Health")

root.left.left = Node("Road Department")
root.left.right = Node("Electricity Department")

root.right.left = Node("Sanitation Department")
root.right.right = Node("Water Department")


# Create Binary Tree
tree = BinaryTree()

# Pre-order
print("Pre-order:")
tree.preorder(root)

# In-order
print("\nIn-order:")
tree.inorder(root)

# Post-order
print("\nPost-order:")
tree.postorder(root)