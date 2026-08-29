"""
Stack implementation for Civic Sense Management System.
Used for undo/redo of complaint status updates and action history.

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
