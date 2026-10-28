"""
DSA Phase 4 - Greedy Algorithm: Multi-Criteria Priority-Based Complaint Processing
==================================================================================
Implements a greedy selection strategy that evaluates eligible civic complaints
using a normalized multi-criteria scoring model and always selects the highest-scoring
complaint next, breaking ties by submission timestamp (FIFO fairness: oldest first).

Priorities in Civic Sense (3 Types):
    1. High   (Priority Rank = 1) -> Urgency Score: 100.0
    2. Medium (Priority Rank = 2) -> Urgency Score: 60.0
    3. Low    (Priority Rank = 3) -> Urgency Score: 30.0
    (Note: "Critical" has been removed as Civic Sense only uses High, Medium, Low)

Greedy Algorithm Logic:
    1. Retrieve complaints from the database.
    2. Filter out terminal / ineligible states: Resolved, Rejected, Closed, Cancelled.
    3. Calculate a multi-criteria priority score for each eligible complaint:
           Score = (Urgency × 0.40) + (Severity × 0.35) + (Waiting Time × 0.25)
       - Urgency: based on numeric Priority (High = 1 [100], Medium = 2 [60], Low = 3 [30])
       - Severity: based on category impact (Drainage/Water = 90-95, Road/Pothole = 80, Garbage = 70, etc.)
       - Waiting Time: normalized hours elapsed since submission (escalates urgency for older pending cases)
    4. Rank complaints from highest score to lowest score (tie-breaker: oldest submission timestamp).
    5. Greedy choice property: select the highest-scoring complaint as next recommended.
    6. When a complaint's status changes or new complaints arrive, recalculate greedily.

Time Complexity:
    O(N log N) for sort-based greedy selection across N eligible complaints.
"""

from datetime import datetime

# Priority Rank Mapping: High = 1, Medium = 2, Low = 3 (Lower rank number = higher urgency)
PRIORITY_RANK = {
    "High":   1,
    "Medium": 2,
    "Low":    3,
}

# Priority Labels with numbers for clear display
PRIORITY_LABELS = {
    "High":   "1 - High",
    "Medium": "2 - Medium",
    "Low":    "3 - Low",
}

# Urgency factor on 0-100 scale (Weight: 40%)
URGENCY_SCORES = {
    "High":   100.0,
    "Medium":  60.0,
    "Low":     30.0,
}

# Civic category public-safety / infrastructure severity on 0-100 scale (Weight: 35%)
SEVERITY_SCORES = {
    "drainage":            95.0,
    "drainage & sewage":   95.0,
    "water leakage":       90.0,
    "water supply":        90.0,
    "damaged road":        80.0,
    "pothole":             80.0,
    "roads & potholes":    80.0,
    "garbage":             70.0,
    "public cleanliness":  70.0,
    "streetlight":         65.0,
    "illegal parking":     55.0,
    "other":               50.0,
}

# Weighting configuration matching prompt:
# Score = (Urgency × 0.40) + (Severity × 0.35) + (Waiting Time × 0.25)
WEIGHT_URGENCY = 0.40
WEIGHT_SEVERITY = 0.35
WEIGHT_WAITING = 0.25

# Statuses that make a complaint ineligible for greedy selection
INELIGIBLE_STATUSES = {"Resolved", "Rejected", "Closed", "Cancelled"}


class GreedyComplaintProcessor:
    """
    Greedy Algorithm for multi-criteria complaint priority selection.

    At each step, picks the locally optimal (highest scored) eligible complaint.
    Scores combine Urgency (40%), Category Severity (35%), and Waiting Time (25%).
    Tie-breaking: among equal scores, earlier created_at wins (FIFO fairness).
    """

    @staticmethod
    def normalize_priority(priority_str):
        """Clean priority string and map legacy 'Critical' to 'High' gracefully."""
        p = (priority_str or "").strip().title()
        if p == "Critical":
            return "High"
        return p

    @classmethod
    def get_priority_rank(cls, priority_str):
        """
        Return the numeric rank for a priority string (High=1, Medium=2, Low=3).
        Returns 999 for unrecognised values.
        """
        clean = cls.normalize_priority(priority_str)
        return PRIORITY_RANK.get(clean, 999)

    @classmethod
    def get_priority_label(cls, priority_str):
        """Return formatted label e.g. '1 - High', '2 - Medium', '3 - Low'."""
        clean = cls.normalize_priority(priority_str)
        return PRIORITY_LABELS.get(clean, clean or "Unknown")

    @classmethod
    def get_urgency_score(cls, priority_str):
        """Return urgency score (0-100 scale)."""
        clean = cls.normalize_priority(priority_str)
        return URGENCY_SCORES.get(clean, 20.0)

    @staticmethod
    def get_severity_score(category_str):
        """Return category severity score (0-100 scale)."""
        c = (category_str or "").strip().lower()
        return SEVERITY_SCORES.get(c, 50.0)

    @staticmethod
    def parse_timestamp(ts_str):
        """Parse created_at timestamp string into datetime."""
        if not ts_str:
            return datetime.max
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(str(ts_str).strip(), fmt)
            except ValueError:
                continue
        return datetime.max

    @classmethod
    def get_waiting_score(cls, ts, ref_time=None):
        """
        Calculate waiting time score (0-100 scale) based on hours elapsed.
        Escalates waiting score linearly up to 7 days (168 hours) maxing at 100.
        """
        ref = ref_time or datetime.now()
        if ts == datetime.max:
            return 5.0, 0.0

        diff_seconds = max(0.0, (ref - ts).total_seconds())
        hours = diff_seconds / 3600.0
        # Normalize: 0 hrs = 5 pts, 168 hrs (7 days) or more = 100 pts
        norm_score = min(100.0, max(5.0, (hours / 168.0) * 100.0))
        return round(norm_score, 2), round(hours, 1)

    @classmethod
    def is_eligible(cls, complaint):
        """Return True if complaint is pending/actionable (not resolved/closed/rejected)."""
        status = (complaint.get("status") or "").strip().title()
        return status not in INELIGIBLE_STATUSES

    @classmethod
    def compute_complaint_score(cls, complaint, ref_time=None):
        """
        Calculate total weighted priority score and generate a clear human explanation.
        Formula: (Urgency × 0.40) + (Severity × 0.35) + (Waiting Time × 0.25)
        """
        priority_str = complaint.get("priority")
        category_str = complaint.get("category")
        created_at_str = complaint.get("created_at")

        urgency_val = cls.get_urgency_score(priority_str)
        severity_val = cls.get_severity_score(category_str)
        ts = cls.parse_timestamp(created_at_str)
        waiting_val, waiting_hours = cls.get_waiting_score(ts, ref_time)

        # Weighted calculation
        u_pts = urgency_val * WEIGHT_URGENCY
        s_pts = severity_val * WEIGHT_SEVERITY
        w_pts = waiting_val * WEIGHT_WAITING
        total_score = round(u_pts + s_pts + w_pts, 2)

        p_rank = cls.get_priority_rank(priority_str)
        p_label = cls.get_priority_label(priority_str)

        days = round(waiting_hours / 24.0, 1)
        wait_desc = f"{days} days" if days >= 1.0 else f"{waiting_hours} hrs"

        explanation = (
            f"Score {total_score:.1f}/100: Urgency {p_label} ({u_pts:.1f} pts) + "
            f"Category Severity '{category_str or 'General'}' ({s_pts:.1f} pts) + "
            f"Waiting Time {wait_desc} ({w_pts:.1f} pts)"
        )

        return {
            "score": total_score,
            "priority_rank": p_rank,
            "priority_label": p_label,
            "score_breakdown": {
                "urgency_score": round(urgency_val, 1),
                "urgency_weighted": round(u_pts, 2),
                "severity_score": round(severity_val, 1),
                "severity_weighted": round(s_pts, 2),
                "waiting_score": round(waiting_val, 1),
                "waiting_weighted": round(w_pts, 2),
                "waiting_hours": waiting_hours,
            },
            "explanation": explanation,
            "_ts": ts,
        }

    def run(self, complaints, ref_time=None):
        """
        Run the Greedy Algorithm on a list of complaint dicts.

        Returns dict with:
            eligible_count   - count of eligible pending complaints
            ineligible_count - count of terminal/resolved complaints
            total_count      - total count evaluated
            next_complaint   - highest-scoring eligible complaint
            processing_order - ranked list of all eligible complaints
            priority_counts  - breakdown by High (1), Medium (2), Low (3)
            unknown_priority - IDs with invalid priority
            algorithm        - description of algorithm
            weights          - scoring weights used
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

            calc = self.compute_complaint_score(c, ref_time=ref_time)
            if calc["priority_rank"] == 999:
                unknown_priority.append(c.get("id"))

            eligible.append({
                **c,
                "score": calc["score"],
                "priority_rank": calc["priority_rank"],
                "priority_label": calc["priority_label"],
                "score_breakdown": calc["score_breakdown"],
                "explanation": calc["explanation"],
                "_ts": calc["_ts"],
            })

        if not eligible:
            return self._empty_result(total, ineligible_count, unknown_priority)

        # Greedy sort:
        # Primary key: highest score first (-score)
        # Secondary key: older creation time first (FIFO fairness)
        eligible.sort(key=lambda x: (-x["score"], x["_ts"]))

        # Remove internal sort key _ts before returning
        processing_order = [
            {k: v for k, v in item.items() if k != "_ts"}
            for item in eligible
        ]
        next_complaint = processing_order[0] if processing_order else None

        # Priority breakdown: High (1), Medium (2), Low (3), Unknown (No Critical!)
        priority_counts = {"High": 0, "Medium": 0, "Low": 0, "Unknown": 0}
        for c in processing_order:
            p = self.normalize_priority(c.get("priority"))
            if p in priority_counts:
                priority_counts[p] += 1
            else:
                priority_counts["Unknown"] += 1

        return {
            "eligible_count":   len(processing_order),
            "ineligible_count": ineligible_count,
            "total_count":      total,
            "next_complaint":   next_complaint,
            "processing_order": processing_order,
            "priority_counts":  priority_counts,
            "unknown_priority": unknown_priority,
            "algorithm":        "Greedy Multi-Criteria Priority Scoring",
            "weights": {
                "urgency": WEIGHT_URGENCY,
                "severity": WEIGHT_SEVERITY,
                "waiting_time": WEIGHT_WAITING,
            },
        }

    def _empty_result(self, total, ineligible_count, unknown_priority=None):
        return {
            "eligible_count":   0,
            "ineligible_count": ineligible_count,
            "total_count":      total,
            "next_complaint":   None,
            "processing_order": [],
            "priority_counts":  {"High": 0, "Medium": 0, "Low": 0, "Unknown": 0},
            "unknown_priority": unknown_priority or [],
            "algorithm":        "Greedy Multi-Criteria Priority Scoring",
            "weights": {
                "urgency": WEIGHT_URGENCY,
                "severity": WEIGHT_SEVERITY,
                "waiting_time": WEIGHT_WAITING,
            },
        }


def _run_tests():
    """Self-contained test suite for the Phase 4 Greedy Algorithm."""
    processor = GreedyComplaintProcessor()
    passed = 0
    failed = 0
    fixed_now = datetime(2026, 2, 10, 12, 0, 0)

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

    print("\n=== Phase 4 Greedy Algorithm Unit Tests ===\n")

    print("Test 1: Priorities ordered by Score -> High (1) > Medium (2) > Low (3)")
    t1 = [
        {"id": 10, "title": "Low Issue",    "priority": "Low",    "category": "Streetlight",   "status": "Pending", "created_at": "2026-02-05 10:00:00"},
        {"id": 11, "title": "High Issue",   "priority": "High",   "category": "Water Leakage", "status": "Pending", "created_at": "2026-02-05 10:00:00"},
        {"id": 12, "title": "Medium Issue", "priority": "Medium", "category": "Garbage",       "status": "Pending", "created_at": "2026-02-05 10:00:00"},
    ]
    r1 = processor.run(t1, ref_time=fixed_now)
    assert_eq("next_complaint is High (1)", r1["next_complaint"]["id"], 11)
    assert_eq("next_complaint priority_rank is 1", r1["next_complaint"]["priority_rank"], 1)
    order1 = [c["priority"] for c in r1["processing_order"]]
    assert_eq("order is High > Medium > Low", order1, ["High", "Medium", "Low"])
    assert_eq("priority_counts does not contain Critical", "Critical" not in r1["priority_counts"], True)

    print("\nTest 2: Same priority tie-breaker -> Older submission gets higher waiting score & recommended first")
    t2 = [
        {"id": 20, "title": "Newer High", "priority": "High", "category": "Pothole", "status": "Pending", "created_at": "2026-02-08 10:00:00"},
        {"id": 21, "title": "Older High", "priority": "High", "category": "Pothole", "status": "Pending", "created_at": "2026-02-01 10:00:00"},
    ]
    r2 = processor.run(t2, ref_time=fixed_now)
    assert_eq("older High complaint recommended first", r2["next_complaint"]["id"], 21)
    assert_eq("older has higher score than newer", r2["processing_order"][0]["score"] > r2["processing_order"][1]["score"], True)

    print("\nTest 3: Terminal statuses (Resolved, Closed, Rejected, Cancelled) excluded")
    t3 = [
        {"id": 30, "title": "Resolved High",  "priority": "High",   "category": "Drainage", "status": "Resolved",  "created_at": "2026-02-01 00:00:00"},
        {"id": 31, "title": "Pending Medium", "priority": "Medium", "category": "Drainage", "status": "Pending",   "created_at": "2026-02-02 00:00:00"},
        {"id": 32, "title": "Closed High",    "priority": "High",   "category": "Drainage", "status": "Closed",    "created_at": "2026-02-01 00:00:00"},
        {"id": 33, "title": "Rejected Low",   "priority": "Low",    "category": "Drainage", "status": "Rejected",  "created_at": "2026-02-01 00:00:00"},
        {"id": 34, "title": "Cancelled High", "priority": "High",   "category": "Drainage", "status": "Cancelled", "created_at": "2026-02-01 00:00:00"},
    ]
    r3 = processor.run(t3, ref_time=fixed_now)
    assert_eq("eligible_count is 1", r3["eligible_count"], 1)
    assert_eq("ineligible_count is 4", r3["ineligible_count"], 4)
    assert_eq("next_complaint is Pending Medium (id=31)", r3["next_complaint"]["id"], 31)

    print("\nTest 4: No eligible complaints returns graceful empty state")
    t4 = [
        {"id": 40, "priority": "High", "status": "Resolved", "created_at": "2026-01-01 00:00:00"},
        {"id": 41, "priority": "Low",  "status": "Rejected", "created_at": "2026-01-02 00:00:00"},
    ]
    r4 = processor.run(t4)
    assert_eq("next_complaint is None", r4["next_complaint"], None)
    assert_eq("eligible_count is 0", r4["eligible_count"], 0)

    print("\nTest 5: Dynamic score update when priority changes (Low -> High)")
    t5 = [
        {"id": 50, "priority": "Low",    "category": "Garbage", "status": "Pending", "created_at": "2026-02-01 00:00:00"},
        {"id": 51, "priority": "Medium", "category": "Garbage", "status": "Pending", "created_at": "2026-02-02 00:00:00"},
    ]
    r5a = processor.run(t5, ref_time=fixed_now)
    assert_eq("before: next is Medium (id=51)", r5a["next_complaint"]["id"], 51)
    # Escalate id=50 to High
    t5[0]["priority"] = "High"
    r5b = processor.run(t5, ref_time=fixed_now)
    assert_eq("after: next is escalated High (id=50)", r5b["next_complaint"]["id"], 50)

    print("\nTest 6: Ineligible status change removes complaint and chooses next best")
    t6 = [
        {"id": 60, "priority": "Medium", "category": "Streetlight", "status": "Pending", "created_at": "2026-02-01 00:00:00"},
        {"id": 61, "priority": "High",   "category": "Streetlight", "status": "Pending", "created_at": "2026-02-02 00:00:00"},
    ]
    r6a = processor.run(t6, ref_time=fixed_now)
    assert_eq("before: next is High (id=61)", r6a["next_complaint"]["id"], 61)
    t6[1]["status"] = "Resolved"
    r6b = processor.run(t6, ref_time=fixed_now)
    assert_eq("after: next is Medium (id=60)", r6b["next_complaint"]["id"], 60)
    assert_eq("eligible_count is 1", r6b["eligible_count"], 1)

    print("\nTest 7: Missing or invalid priority handled safely")
    t7 = [
        {"id": 70, "priority": "INVALID_PRIO", "category": "Garbage", "status": "Pending", "created_at": "2026-02-01 00:00:00"},
        {"id": 71, "priority": "Low",          "category": "Garbage", "status": "Pending", "created_at": "2026-02-01 00:00:00"},
    ]
    r7 = processor.run(t7, ref_time=fixed_now)
    assert_eq("valid Low beats invalid priority", r7["next_complaint"]["id"], 71)
    assert_eq("invalid priority id 70 tracked in unknown_priority", 70 in r7["unknown_priority"], True)

    print("\nTest 8: Empty input handled safely")
    r8 = processor.run([])
    assert_eq("empty input returns eligible_count 0", r8["eligible_count"], 0)
    assert_eq("empty input returns next_complaint None", r8["next_complaint"], None)

    print(f"\nResults: {passed} passed, {failed} failed\n")
    return failed == 0


if __name__ == "__main__":
    ok = _run_tests()
    raise SystemExit(0 if ok else 1)
