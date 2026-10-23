"""
DSA Phase 4 - Greedy Algorithm: Priority-Based Complaint Processing
====================================================================
Implements a greedy selection strategy that always picks the highest-priority
eligible complaint next, breaking ties by submission timestamp (oldest first).

Priority Ordering (descending urgency):
    Critical > High > Medium > Low

Eligibility:
    A complaint is eligible for greedy selection if its status is NOT one of
    the ineligible terminal states: Resolved, Rejected, Closed, Cancelled.

Algorithm Explanation:
    Greedy choice property: at each step pick the locally optimal (highest
    priority) eligible complaint without reconsidering earlier choices.
    Implementation: sort the eligible set by (priority_rank ASC, created_at ASC).
    This is O(N log N) which is optimal for comparison-based ordering and
    produces a stable, deterministic processing order.

Usage:
    from dsa.greedy import GreedyComplaintProcessor
    processor = GreedyComplaintProcessor()
    result = processor.run(complaints)
"""

from datetime import datetime

# Priority rank table (lower number = higher urgency)
PRIORITY_RANK = {
    "Critical": 1,
    "High":     2,
    "Medium":   3,
    "Low":      4,
}

# Statuses that make a complaint ineligible for greedy selection
INELIGIBLE_STATUSES = {"Resolved", "Rejected", "Closed", "Cancelled"}


class GreedyComplaintProcessor:
    """
    Greedy Algorithm for priority-based complaint processing.

    The greedy choice at each step: select the complaint with the smallest
    priority_rank (= highest urgency). Among ties, prefer the oldest complaint
    (smallest created_at timestamp) - FIFO fairness within the same priority.
    """

    @staticmethod
    def get_priority_rank(priority_str):
        """
        Return the numeric rank for a priority string.
        Returns 999 for any unrecognised value so that invalid priorities
        appear at the bottom rather than being silently elevated to Critical.
        """
        clean = (priority_str or "").strip().title()
        return PRIORITY_RANK.get(clean, 999)

    @staticmethod
    def parse_timestamp(ts_str):
        """
        Parse a created_at timestamp string into a datetime for comparison.
        Falls back to datetime.max so complaints without a timestamp appear last.
        """
        if not ts_str:
            return datetime.max
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(str(ts_str).strip(), fmt)
            except ValueError:
                continue
        return datetime.max

    @staticmethod
    def is_eligible(complaint):
        """Return True if the complaint is actionable / eligible for processing."""
        status = (complaint.get("status") or "").strip()
        return status not in INELIGIBLE_STATUSES

    def run(self, complaints):
        """
        Run the Greedy Algorithm on a list of complaint dicts.

        Returns dict with:
            eligible_count   - number of eligible complaints
            next_complaint   - complaint to process next (dict or None)
            processing_order - all eligible complaints in greedy order
            priority_counts  - count per priority level (eligible only)
            total_count      - total complaints passed in
            ineligible_count - count of ineligible complaints
            unknown_priority - list of complaint IDs with unrecognised priority
        """
        if not complaints:
            return self._empty_result(0, 0)

        total = len(complaints)
        eligible = []
        ineligible_count = 0
        unknown_priority = []

        for c in complaints:
            if not self.is_eligible(c):
                ineligible_count += 1
                continue

            priority_str = (c.get("priority") or "").strip()
            rank = self.get_priority_rank(priority_str)

            if rank == 999:
                unknown_priority.append(c.get("id"))

            ts = self.parse_timestamp(c.get("created_at"))
            eligible.append({**c, "_rank": rank, "_ts": ts})

        if not eligible:
            return self._empty_result(total, ineligible_count, unknown_priority)

        # Greedy sort: primary = priority rank (asc), secondary = timestamp (asc)
        eligible.sort(key=lambda x: (x["_rank"], x["_ts"]))

        # Strip internal sort-key fields before returning
        processing_order = [
            {k: v for k, v in c.items() if not k.startswith("_")}
            for c in eligible
        ]
        next_complaint = processing_order[0] if processing_order else None

        # Build priority breakdown (eligible only)
        priority_counts = {label: 0 for label in PRIORITY_RANK}
        priority_counts["Unknown"] = 0
        for c in processing_order:
            p = (c.get("priority") or "").strip().title()
            if p in priority_counts:
                priority_counts[p] += 1
            else:
                priority_counts["Unknown"] += 1

        return {
            "eligible_count":    len(processing_order),
            "ineligible_count":  ineligible_count,
            "total_count":       total,
            "next_complaint":    next_complaint,
            "processing_order":  processing_order,
            "priority_counts":   priority_counts,
            "unknown_priority":  unknown_priority,
        }

    def _empty_result(self, total, ineligible_count, unknown_priority=None):
        return {
            "eligible_count":    0,
            "ineligible_count":  ineligible_count,
            "total_count":       total,
            "next_complaint":    None,
            "processing_order":  [],
            "priority_counts":   {label: 0 for label in list(PRIORITY_RANK) + ["Unknown"]},
            "unknown_priority":  unknown_priority or [],
        }


def _run_tests():
    """Self-contained test suite for the Greedy Algorithm."""
    processor = GreedyComplaintProcessor()
    passed = 0
    failed = 0

    def assert_eq(label, actual, expected):
        nonlocal passed, failed
        if actual == expected:
            print(f"  PASS  {label}")
            passed += 1
        else:
            print(f"  FAIL  {label}")
            print(f"       Expected : {expected!r}")
            print(f"       Actual   : {actual!r}")
            failed += 1

    print("\n=== Greedy Algorithm Unit Tests ===\n")

    print("Test 1: Different priorities -> Critical first")
    t1 = [
        {"id": 10, "priority": "Low",      "status": "Pending",     "created_at": "2026-02-01 10:00:00"},
        {"id": 11, "priority": "High",     "status": "Pending",     "created_at": "2026-02-02 10:00:00"},
        {"id": 12, "priority": "Critical", "status": "In Progress", "created_at": "2026-02-03 10:00:00"},
        {"id": 13, "priority": "Medium",   "status": "Approved",    "created_at": "2026-02-04 10:00:00"},
    ]
    r1 = processor.run(t1)
    assert_eq("next_complaint is Critical", r1["next_complaint"]["priority"], "Critical")
    order1 = [c["priority"] for c in r1["processing_order"]]
    assert_eq("order is Critical>High>Medium>Low", order1, ["Critical", "High", "Medium", "Low"])

    print("\nTest 2: Same priority - older first")
    t2 = [
        {"id": 20, "priority": "High", "status": "Pending", "created_at": "2026-03-10 09:00:00"},
        {"id": 21, "priority": "High", "status": "Pending", "created_at": "2026-01-05 08:00:00"},
    ]
    r2 = processor.run(t2)
    assert_eq("next_complaint is the older one (id=21)", r2["next_complaint"]["id"], 21)

    print("\nTest 3: Resolved excluded")
    t3 = [
        {"id": 30, "priority": "Critical", "status": "Resolved", "created_at": "2026-01-01 00:00:00"},
        {"id": 31, "priority": "High",     "status": "Pending",  "created_at": "2026-01-02 00:00:00"},
    ]
    r3 = processor.run(t3)
    eligible_ids = [c["id"] for c in r3["processing_order"]]
    assert_eq("Resolved id=30 excluded", 30 not in eligible_ids, True)
    assert_eq("next_complaint is High (id=31)", r3["next_complaint"]["id"], 31)

    print("\nTest 4: No eligible complaints")
    t4 = [
        {"id": 40, "priority": "High", "status": "Resolved", "created_at": "2026-01-01 00:00:00"},
        {"id": 41, "priority": "Low",  "status": "Rejected", "created_at": "2026-01-02 00:00:00"},
    ]
    r4 = processor.run(t4)
    assert_eq("next_complaint is None", r4["next_complaint"], None)
    assert_eq("eligible_count is 0", r4["eligible_count"], 0)

    print("\nTest 5: Changed priority reflected")
    t5 = [
        {"id": 50, "priority": "Low",  "status": "Pending", "created_at": "2026-01-01 00:00:00"},
        {"id": 51, "priority": "High", "status": "Pending", "created_at": "2026-01-02 00:00:00"},
    ]
    r5a = processor.run(t5)
    assert_eq("before: next is High (id=51)", r5a["next_complaint"]["id"], 51)
    t5[0]["priority"] = "Critical"
    r5b = processor.run(t5)
    assert_eq("after: next is Critical (id=50)", r5b["next_complaint"]["id"], 50)

    print("\nTest 6: Status change ineligible")
    t6 = [
        {"id": 60, "priority": "High",     "status": "Pending", "created_at": "2026-01-01 00:00:00"},
        {"id": 61, "priority": "Critical", "status": "Pending", "created_at": "2026-01-02 00:00:00"},
    ]
    r6a = processor.run(t6)
    assert_eq("before: next is Critical (id=61)", r6a["next_complaint"]["id"], 61)
    t6[1]["status"] = "Resolved"
    r6b = processor.run(t6)
    assert_eq("after: next is High (id=60)", r6b["next_complaint"]["id"], 60)
    assert_eq("eligible_count is 1", r6b["eligible_count"], 1)

    print("\nTest 7: Unknown priority last")
    t7 = [
        {"id": 70, "priority": "INVALID_XYZ", "status": "Pending", "created_at": "2026-01-01 00:00:00"},
        {"id": 71, "priority": "Low",         "status": "Pending", "created_at": "2026-01-02 00:00:00"},
    ]
    r7 = processor.run(t7)
    assert_eq("unknown priority is last", r7["processing_order"][-1]["id"], 70)
    assert_eq("unknown_priority list contains id=70", 70 in r7["unknown_priority"], True)

    print("\nTest 8: Empty input")
    r8 = processor.run([])
    assert_eq("next_complaint is None", r8["next_complaint"], None)
    assert_eq("eligible_count is 0", r8["eligible_count"], 0)

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    ok = _run_tests()
    raise SystemExit(0 if ok else 1)
