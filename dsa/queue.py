"""
Queue implementation for Civic Sense Management System.
Used for FIFO complaint processing — first complaint submitted is processed first.
Also includes PriorityQueue for emergency complaint handling.

Two queue variants:
  - Queue         : List-based FIFO queue
  - LinkedQueue   : Linked-list based FIFO queue (Phase 1: linked list variant)
  - PriorityQueue : Priority-sorted queue for emergency complaints

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

    def to_string(self):
        """Visual: FRONT → [item1] → [item2] → REAR"""
        if self.is_empty():
            return "FRONT → [empty] → REAR"
        parts = []
        for item in self.items:
            label = item.get("id", item) if isinstance(item, dict) else item
            parts.append(f"[{label}]")
        return "FRONT → " + " → ".join(parts) + " → REAR"

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


# ─────────────────────────────────────────────────────────────
# LinkedQueue — Linked-List based Queue (Phase 1: linked list variant)
# ─────────────────────────────────────────────────────────────

class _QNode:
    """Internal node for LinkedQueue."""
    __slots__ = ("data", "next")

    def __init__(self, data):
        self.data = data
        self.next = None  # Points to the next node (toward rear)


class LinkedQueue:
    """
    Linked-list based FIFO Queue for Civic Sense Management System.
    
    Uses two pointers:
      - _front  : Points to the node at the front (dequeue side)
      - _rear   : Points to the node at the rear  (enqueue side)
    
    Phase 1 requirement: Queue using linked-list nodes (not an array).
    Enqueue O(1) — Dequeue O(1) — no array shifting needed.
    """

    def __init__(self, max_size=100):
        self._front = None   # Front pointer (dequeue from here)
        self._rear = None    # Rear pointer  (enqueue here)
        self._size = 0
        self.max_size = max_size

    def enqueue(self, item):
        """Add item to the rear of the linked queue. O(1)"""
        if self.is_full():
            return False
        new_node = _QNode(item)
        if self._rear is None:
            # Empty queue: both front and rear point to the new node
            self._front = self._rear = new_node
        else:
            self._rear.next = new_node   # Link current rear to new node
            self._rear = new_node        # Move rear pointer forward
        self._size += 1
        return True

    def dequeue(self):
        """Remove and return item from the front. O(1)"""
        if self.is_empty():
            return None
        data = self._front.data
        self._front = self._front.next   # Move front pointer forward
        if self._front is None:
            self._rear = None            # Queue is now empty
        self._size -= 1
        return data

    def peek(self):
        """Return front item without removing. O(1)"""
        if self.is_empty():
            return None
        return self._front.data

    def rear(self):
        """Return rear item without removing. O(1)"""
        if self.is_empty():
            return None
        return self._rear.data

    def is_empty(self):
        return self._front is None

    def is_full(self):
        return self._size >= self.max_size

    def size(self):
        return self._size

    def display(self):
        """Return all items from front to rear as a list."""
        items = []
        current = self._front
        while current:
            items.append(current.data)
            current = current.next
        return items

    def clear(self):
        self._front = self._rear = None
        self._size = 0

    def to_string(self):
        """Visual: FRONT → [item1] → [item2] → NULL (REAR)"""
        parts = []
        current = self._front
        while current:
            label = current.data.get("id", current.data) if isinstance(current.data, dict) else current.data
            parts.append(f"[{label}]")
            current = current.next
        return "FRONT → " + " → ".join(parts) + " → NULL" if parts else "FRONT → NULL"

    def __len__(self):
        return self._size

    def __repr__(self):
        return self.to_string()
