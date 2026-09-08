"""
Stack implementation for Civic Sense Management System.
Used for undo/redo of complaint status updates and action history.

Two variants:
  - Stack        : List-based (array) stack — O(1) push/pop
  - LinkedStack  : Linked-list-based stack — O(1) push/pop using Node pointers

Operations: Push, Pop, Peek, Display, is_empty, size
"""


class Stack:
    """Array-based stack for complaint action history (LIFO)."""

    def __init__(self, max_size=100):
        self.items = []
        self.max_size = max_size

    def push(self, item):
        """Push an item onto the stack. O(1)"""
        if self.is_full():
            return False  # Stack overflow
        self.items.append(item)
        return True

    def pop(self):
        """Remove and return the top item. O(1)"""
        if self.is_empty():
            return None  # Stack underflow
        return self.items.pop()

    def peek(self):
        """Return the top item without removing it. O(1)"""
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        """Check if stack is empty. O(1)"""
        return len(self.items) == 0

    def is_full(self):
        """Check if stack is full. O(1)"""
        return len(self.items) >= self.max_size

    def size(self):
        """Return current size. O(1)"""
        return len(self.items)

    def display(self):
        """Return items from top to bottom."""
        return list(reversed(self.items))

    def clear(self):
        """Remove all items."""
        self.items.clear()

    def to_list(self):
        """Return a copy of internal list (bottom to top)."""
        return self.items.copy()

    def to_string(self):
        """Visual representation: TOP → [item1] → [item2] → BOTTOM"""
        if self.is_empty():
            return "TOP → [empty] → BOTTOM"
        parts = []
        for item in reversed(self.items):
            label = item.get("id", item) if isinstance(item, dict) else item
            parts.append(f"[{label}]")
        return "TOP → " + " → ".join(parts) + " → BOTTOM"

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        if self.is_empty():
            return "Stack: [empty]"
        items_str = " | ".join(
            str(item.get("id", item) if isinstance(item, dict) else item)
            for item in reversed(self.items)
        )
        return f"Stack (top → bottom): {items_str}"


# ─────────────────────────────────────────────────────────────
# LinkedStack — Linked-List based Stack (Phase 1: linked list variant)
# ─────────────────────────────────────────────────────────────

class _SNode:
    """Internal node for LinkedStack."""
    __slots__ = ("data", "next")

    def __init__(self, data):
        self.data = data
        self.next = None  # Points to the node below in the stack


class LinkedStack:
    """
    Linked-list based stack for Civic Sense Management System.
    Each element is a Node that holds data and a pointer to the element below it.
    
    Phase 1 requirement: Stack using linked-list nodes (not an array).
    Used to demonstrate pointer-based LIFO behaviour.
    """

    def __init__(self, max_size=100):
        self._top = None        # Pointer to the top node
        self._size = 0
        self.max_size = max_size

    def push(self, item):
        """Push an item onto the top of the linked stack. O(1)"""
        if self.is_full():
            return False  # Stack overflow
        new_node = _SNode(item)
        new_node.next = self._top   # New node points to previous top
        self._top = new_node        # New node becomes the top
        self._size += 1
        return True

    def pop(self):
        """Remove and return the top item. O(1)"""
        if self.is_empty():
            return None  # Stack underflow
        data = self._top.data
        self._top = self._top.next  # Move top pointer down
        self._size -= 1
        return data

    def peek(self):
        """Return the top item without removing it. O(1)"""
        if self.is_empty():
            return None
        return self._top.data

    def is_empty(self):
        """Check if linked stack is empty. O(1)"""
        return self._top is None

    def is_full(self):
        """Check if linked stack reached max_size. O(1)"""
        return self._size >= self.max_size

    def size(self):
        """Return current size. O(1)"""
        return self._size

    def display(self):
        """Return all items top-to-bottom as a list."""
        items = []
        current = self._top
        while current:
            items.append(current.data)
            current = current.next
        return items

    def clear(self):
        """Remove all nodes."""
        self._top = None
        self._size = 0

    def to_string(self):
        """Visual: TOP → [item1] → [item2] → NULL"""
        parts = []
        current = self._top
        while current:
            label = current.data.get("id", current.data) if isinstance(current.data, dict) else current.data
            parts.append(f"[{label}]")
            current = current.next
        return "TOP → " + " → ".join(parts) + " → NULL" if parts else "TOP → NULL"

    def __len__(self):
        return self._size

    def __repr__(self):
        return self.to_string()
