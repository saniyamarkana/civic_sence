# Binary Tree – Department Hierarchy

class Node:
    def __init__(self, data):
        self.data  = data
        self.left  = None
        self.right = None


# Pre-order: Root -> Left -> Right
def preorder(node):
    if node:
        print(node.data)
        preorder(node.left)
        preorder(node.right)

# In-order: Left -> Root -> Right
def inorder(node):
    if node:
        inorder(node.left)
        print(node.data)
        inorder(node.right)

# Post-order: Left -> Right -> Root
def postorder(node):
    if node:
        postorder(node.left)
        postorder(node.right)
        print(node.data)


#        Municipal Commissioner
#        /                    \
#   Infrastructure        Health
#    /         \          /       \
# Roads   Electricity  Sanitation  Water

if __name__ == "__main__":
    root = Node("Municipal Commissioner")

    root.left  = Node("Infrastructure")
    root.right = Node("Health")

    root.left.left   = Node("Roads Department")
    root.left.right  = Node("Electricity Department")
    root.right.left  = Node("Sanitation Department")
    root.right.right = Node("Water Department")

    print("Pre-order:")
    preorder(root)

    print("\nIn-order:")
    inorder(root)

    print("\nPost-order:")
    postorder(root)