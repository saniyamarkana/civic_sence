"""
Linked List implementation for Civic Sense Management System.
Used to store and process complaint records dynamically.

Operations: Insert (beginning/end/position), Delete, Search, Update, Traverse, Reverse
"""


class Node:
    """A single node in the linked list."""

    def __init__(self, data):
        self.data = data  # Dictionary holding complaint data
        self.next = None

    def __repr__(self):
        if isinstance(self.data, dict) and "id" in self.data:
            return f"Node(ID:{self.data['id']})"
        return f"Node({self.data})"


class LinkedList:
    """Singly linked list for complaint management."""

    def __init__(self):
        self.head = None
        self._size = 0

    # ──────────────── Insert Operations ────────────────

    def insert_at_beginning(self, data):
        """Insert a new node at the beginning."""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1
        return new_node

    def insert_at_end(self, data):
        """Insert a new node at the end. O(n)"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1
        return new_node

    def insert_at_position(self, data, position):
        """Insert at a specific position (0-indexed). O(n)"""
        if position < 0 or position > self._size:
            return None
        if position == 0:
            return self.insert_at_beginning(data)

        new_node = Node(data)
        current = self.head
        for _ in range(position - 1):
            current = current.next
        new_node.next = current.next
        current.next = new_node
        self._size += 1
        return new_node

    # ──────────────── Delete Operations ────────────────

    def delete_at_beginning(self):
        """Remove the first node. O(1)"""
        if not self.head:
            return None
        removed = self.head
        self.head = self.head.next
        self._size -= 1
        return removed.data

    def delete_at_end(self):
        """Remove the last node. O(n)"""
        if not self.head:
            return None
        if not self.head.next:
            removed = self.head
            self.head = None
            self._size -= 1
            return removed.data

        current = self.head
        while current.next.next:
            current = current.next
        removed = current.next
        current.next = None
        self._size -= 1
        return removed.data

    def delete_by_id(self, complaint_id):
        """Delete a node by complaint ID. O(n)"""
        if not self.head:
            return None

        if isinstance(self.head.data, dict) and self.head.data.get("id") == complaint_id:
            return self.delete_at_beginning()

        current = self.head
        while current.next:
            if isinstance(current.next.data, dict) and current.next.data.get("id") == complaint_id:
                removed = current.next
                current.next = current.next.next
                self._size -= 1
                return removed.data
            current = current.next
        return None

    # ──────────────── Search Operations ────────────────

    def search_by_id(self, complaint_id):
        """Search for a complaint by ID. Returns (node, position) or (None, -1). O(n)"""
        current = self.head
        pos = 0
        while current:
            if isinstance(current.data, dict) and current.data.get("id") == complaint_id:
                return current, pos
            current = current.next
            pos += 1
        return None, -1

    def search_by_field(self, field, value):
        """Search by any field. Returns list of matching nodes."""
        results = []
        current = self.head
        while current:
            if isinstance(current.data, dict) and current.data.get(field) == value:
                results.append(current)
            current = current.next
        return results

    # ──────────────── Update ────────────────

    def update_by_id(self, complaint_id, updates):
        """Update fields of a complaint by ID. O(n)"""
        node, pos = self.search_by_id(complaint_id)
        if node and isinstance(node.data, dict):
            node.data.update(updates)
            return True
        return False

    # ──────────────── Traversal ────────────────

    def traverse(self):
        """Return all data items as a list. O(n)"""
        items = []
        current = self.head
        while current:
            items.append(current.data)
            current = current.next
        return items

    def get_nodes(self):
        """Return all nodes as a list (for visualization). O(n)"""
        nodes = []
        current = self.head
        while current:
            nodes.append(current)
            current = current.next
        return nodes

    # ──────────────── Reverse ────────────────

    def reverse(self):
        """Reverse the linked list in-place. O(n)"""
        prev = None
        current = self.head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head = prev

    # ──────────────── Utilities ────────────────

    def size(self):
        return self._size

    def is_empty(self):
        return self.head is None

    def clear(self):
        self.head = None
        self._size = 0

    def to_string(self):
        """Visual representation: [101] -> [102] -> [103] -> None"""
        parts = []
        current = self.head
        while current:
            if isinstance(current.data, dict) and "id" in current.data:
                parts.append(f"[{current.data['id']}]")
            else:
                parts.append(f"[{current.data}]")
            current = current.next
        parts.append("None")
        return " -> ".join(parts)

    def __len__(self):
        return self._size

    def __repr__(self):
        return self.to_string()
