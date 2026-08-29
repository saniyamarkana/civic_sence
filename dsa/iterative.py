"""
Iterative algorithms for Civic Sense Management System.
Implements iterative traversal, searching, and sorting on complaint data.

Algorithms: Linear Search, Binary Search, Bubble Sort, Selection Sort
"""


class IterativeAlgorithms:
    """Iterative searching and sorting algorithms with step logging."""

    @staticmethod
    def linear_search(arr, key, field="id"):
        """
        Linear search through a list of dicts.
        Returns (found_index, steps) where steps log each comparison.
        """
        steps = []
        for i, item in enumerate(arr):
            val = item.get(field, item) if isinstance(item, dict) else item
            found = (val == key)
            steps.append({
                "index": i,
                "value": val,
                "comparing": key,
                "found": found,
            })
            if found:
                return i, steps
        return -1, steps

    @staticmethod
    def binary_search(arr, key, field="id"):
        """
        Binary search on a sorted list of dicts.
        Array must be sorted by the given field.
        Returns (found_index, steps).
        """
        sorted_arr = sorted(arr, key=lambda x: x.get(field, x) if isinstance(x, dict) else x)
        steps = []
        low, high = 0, len(sorted_arr) - 1

        while low <= high:
            mid = (low + high) // 2
            val = sorted_arr[mid].get(field, sorted_arr[mid]) if isinstance(sorted_arr[mid], dict) else sorted_arr[mid]
            steps.append({
                "low": low,
                "high": high,
                "mid": mid,
                "mid_value": val,
                "target": key,
                "action": "found" if val == key else ("go_left" if val > key else "go_right"),
            })
            if val == key:
                return mid, steps
            elif val < key:
                low = mid + 1
            else:
                high = mid - 1

        return -1, steps

    @staticmethod
    def bubble_sort(arr, field="priority", ascending=True):
        """
        Bubble sort with step logging for animation.
        Returns (sorted_array, steps) where each step records a comparison/swap.
        """
        data = [item.copy() if isinstance(item, dict) else item for item in arr]
        steps = []
        n = len(data)

        for i in range(n - 1):
            swapped = False
            for j in range(n - 1 - i):
                val_a = data[j].get(field, data[j]) if isinstance(data[j], dict) else data[j]
                val_b = data[j + 1].get(field, data[j + 1]) if isinstance(data[j + 1], dict) else data[j + 1]

                should_swap = (val_a > val_b) if ascending else (val_a < val_b)
                steps.append({
                    "pass": i,
                    "comparing": (j, j + 1),
                    "values": (val_a, val_b),
                    "swapped": should_swap,
                    "state": [d.copy() if isinstance(d, dict) else d for d in data],
                })

                if should_swap:
                    data[j], data[j + 1] = data[j + 1], data[j]
                    swapped = True

            if not swapped:
                break

        return data, steps

    @staticmethod
    def selection_sort(arr, field="priority", ascending=True):
        """
        Selection sort with step logging.
        Returns (sorted_array, steps).
        """
        data = [item.copy() if isinstance(item, dict) else item for item in arr]
        steps = []
        n = len(data)

        for i in range(n - 1):
            best = i
            for j in range(i + 1, n):
                val_best = data[best].get(field, data[best]) if isinstance(data[best], dict) else data[best]
                val_j = data[j].get(field, data[j]) if isinstance(data[j], dict) else data[j]

                if (ascending and val_j < val_best) or (not ascending and val_j > val_best):
                    best = j

            swapped = best != i
            if swapped:
                data[i], data[best] = data[best], data[i]

            steps.append({
                "pass": i,
                "selected_index": best,
                "swapped_with": i if swapped else None,
                "swapped": swapped,
                "state": [d.copy() if isinstance(d, dict) else d for d in data],
            })

        return data, steps

    @staticmethod
    def traverse_iterative(arr):
        """Simple iterative traversal returning elements and step count."""
        result = []
        for i, item in enumerate(arr):
            result.append({"index": i, "data": item})
        return result
