"""
Queue implementation for Civic Sense Management System.
Used for FIFO complaint processing — first complaint submitted is processed first.
Also includes PriorityQueue for emergency complaint handling.

Operations: Enqueue, Dequeue, Peek, Display, is_empty, size
"""


class Queue:
    """Array-based queue for complaint processing (FIFO)."""

    def __init__(self, max_size=100):
        self.items = []
        self.max_size = max_size

    def enqueue(self, item):
        """Add item to the rear of the queue. O(1)"""
        if self.is_full():
            return False
        self.items.append(item)
        return True

    def dequeue(self):
        """Remove and return item from the front. O(n)"""
        if self.is_empty():
            return None
        return self.items.pop(0)

    def peek(self):
        """Return front item without removing. O(1)"""
        if self.is_empty():
            return None
        return self.items[0]

    def rear(self):
        """Return rear item without removing. O(1)"""
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def is_full(self):
        return len(self.items) >= self.max_size

    def size(self):
        return len(self.items)

    def display(self):
        """Return items from front to rear."""
        return self.items.copy()

    def clear(self):
        self.items.clear()

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        if self.is_empty():
            return "Queue: [empty]"
        items_str = " <- ".join(
            str(item.get("id", item) if isinstance(item, dict) else item)
            for item in self.items
        )
        return f"Queue (front → rear): {items_str}"


class PriorityQueue:
    """Priority-based queue — higher priority complaints are processed first.

    Priority values: High=3, Medium=2, Low=1
    """

    PRIORITY_VALUES = {"High": 3, "Medium": 2, "Low": 1}

    def __init__(self, max_size=100):
        self.items = []  # List of (priority_value, data) tuples
        self.max_size = max_size

    def enqueue(self, item, priority="Medium"):
        """Insert item based on priority. O(n)"""
        if self.is_full():
            return False
        pv = self.PRIORITY_VALUES.get(priority, 2)
        # Find correct position — higher priority goes to front
        pos = 0
        for i, (p, _) in enumerate(self.items):
            if pv > p:
                pos = i
                break
            pos = i + 1
        self.items.insert(pos, (pv, item))
        return True

    def dequeue(self):
        """Remove highest priority item (front). O(1)"""
        if self.is_empty():
            return None
        return self.items.pop(0)[1]

    def peek(self):
        if self.is_empty():
            return None
        return self.items[0][1]

    def is_empty(self):
        return len(self.items) == 0

    def is_full(self):
        return len(self.items) >= self.max_size

    def size(self):
        return len(self.items)

    def display(self):
        """Return items with their priorities."""
        return [(p, d) for p, d in self.items]

    def display_items(self):
        """Return just the data items, front to rear."""
        return [d for _, d in self.items]

    def clear(self):
        self.items.clear()

    def __len__(self):
        return len(self.items)
