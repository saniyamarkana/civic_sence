"""
Recursive algorithms for Civic Sense Management System.
Implements recursive traversal, searching, sorting, and classic problems.

Algorithms: Factorial, Fibonacci, Recursive Binary Search, Merge Sort, Quick Sort
"""


class RecursiveAlgorithms:
    """Recursive algorithms with call tracking for visualization."""

    @staticmethod
    def factorial(n, steps=None):
        """
        Recursive factorial with call tree logging.
        Returns (result, steps).
        """
        if steps is None:
            steps = []
        steps.append({"call": f"factorial({n})", "depth": len(steps), "type": "call"})

        if n <= 1:
            steps.append({"call": f"factorial({n}) = 1", "depth": len(steps), "type": "return", "value": 1})
            return 1, steps

        sub_result, steps = RecursiveAlgorithms.factorial(n - 1, steps)
        result = n * sub_result
        steps.append({"call": f"factorial({n}) = {n} * {sub_result} = {result}",
                       "depth": len(steps), "type": "return", "value": result})
        return result, steps

    @staticmethod
    def fibonacci(n, steps=None, memo=None):
        """
        Recursive Fibonacci with memoization and call logging.
        Returns (result, steps).
        """
        if steps is None:
            steps = []
        if memo is None:
            memo = {}

        steps.append({"call": f"fib({n})", "depth": len(steps), "type": "call"})

        if n in memo:
            steps.append({"call": f"fib({n}) = {memo[n]} [cached]",
                           "depth": len(steps), "type": "cached", "value": memo[n]})
            return memo[n], steps

        if n <= 1:
            steps.append({"call": f"fib({n}) = {n}",
                           "depth": len(steps), "type": "return", "value": n})
            return n, steps

        a, steps = RecursiveAlgorithms.fibonacci(n - 1, steps, memo)
        b, steps = RecursiveAlgorithms.fibonacci(n - 2, steps, memo)
        result = a + b
        memo[n] = result
        steps.append({"call": f"fib({n}) = fib({n-1}) + fib({n-2}) = {a} + {b} = {result}",
                       "depth": len(steps), "type": "return", "value": result})
        return result, steps

    @staticmethod
    def binary_search_recursive(arr, key, low=0, high=None, field="id", steps=None):
        """
        Recursive binary search on sorted list.
        Returns (found_index, steps).
        """
        if steps is None:
            steps = []
        if high is None:
            arr = sorted(arr, key=lambda x: x.get(field, x) if isinstance(x, dict) else x)
            high = len(arr) - 1

        if low > high:
            steps.append({"low": low, "high": high, "action": "not_found"})
            return -1, steps

        mid = (low + high) // 2
        val = arr[mid].get(field, arr[mid]) if isinstance(arr[mid], dict) else arr[mid]

        steps.append({
            "low": low, "high": high, "mid": mid,
            "mid_value": val, "target": key,
            "action": "found" if val == key else ("go_left" if val > key else "go_right"),
        })

        if val == key:
            return mid, steps
        elif val < key:
            return RecursiveAlgorithms.binary_search_recursive(arr, key, mid + 1, high, field, steps)
        else:
            return RecursiveAlgorithms.binary_search_recursive(arr, key, low, mid - 1, field, steps)

    @staticmethod
    def merge_sort(arr, field="id", ascending=True, steps=None, depth=0):
        """
        Recursive merge sort on real complaint objects with step logging.
        Returns (sorted_array, steps).
        """
        if steps is None:
            steps = []

        def get_val(item):
            if isinstance(item, dict):
                val = item.get(field, item)
            else:
                val = item
            if field == "priority" and isinstance(val, str):
                p_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
                return p_map.get(val, 0)
            return val if val is not None else ""

        ids = [get_val(x) for x in arr]
        steps.append({"action": "split", "data": ids, "depth": depth})

        if len(arr) <= 1:
            return arr[:], steps

        mid = len(arr) // 2
        left, steps = RecursiveAlgorithms.merge_sort(arr[:mid], field, ascending, steps, depth + 1)
        right, steps = RecursiveAlgorithms.merge_sort(arr[mid:], field, ascending, steps, depth + 1)

        # Merge
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            v_left = get_val(left[i])
            v_right = get_val(right[j])
            should_take_left = (v_left <= v_right) if ascending else (v_left >= v_right)
            if should_take_left:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])

        m_ids = [get_val(x) for x in merged]
        steps.append({"action": "merge", "data": m_ids, "depth": depth})

        return merged, steps

    @staticmethod
    def quick_sort(arr, field="id", ascending=True, steps=None, depth=0):
        """
        Recursive quick sort on real complaint objects with step logging.
        Returns (sorted_array, steps).
        """
        if steps is None:
            steps = []

        def get_val(item):
            if isinstance(item, dict):
                val = item.get(field, item)
            else:
                val = item
            if field == "priority" and isinstance(val, str):
                p_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
                return p_map.get(val, 0)
            return val if val is not None else ""

        if len(arr) <= 1:
            return arr[:], steps

        pivot = arr[-1]
        pivot_val = get_val(pivot)

        steps.append({
            "action": "partition",
            "pivot": pivot_val,
            "data": [get_val(x) for x in arr],
            "depth": depth,
        })

        left = []
        right = []
        for x in arr[:-1]:
            val = get_val(x)
            if (val <= pivot_val) if ascending else (val >= pivot_val):
                left.append(x)
            else:
                right.append(x)

        sorted_left, steps = RecursiveAlgorithms.quick_sort(left, field, ascending, steps, depth + 1)
        sorted_right, steps = RecursiveAlgorithms.quick_sort(right, field, ascending, steps, depth + 1)

        result = sorted_left + [pivot] + sorted_right

        steps.append({
            "action": "combine",
            "data": [get_val(x) for x in result],
            "depth": depth,
        })

        return result, steps

    @staticmethod
    def traverse_recursive(arr, index=0, result=None):
        """Recursive list traversal."""
        if result is None:
            result = []
        if index >= len(arr):
            return result
        result.append({"index": index, "data": arr[index]})
        return RecursiveAlgorithms.traverse_recursive(arr, index + 1, result)
