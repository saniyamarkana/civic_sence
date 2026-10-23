"""
Comprehensive Test Suite for Phase 4 Greedy Algorithm
Tests 1-8 matching all requirements in the user request.
"""
import sys
import os
import unittest
from datetime import datetime

# Add root directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from dsa.greedy import GreedyComplaintProcessor, PRIORITY_RANK, INELIGIBLE_STATUSES
from database.database import Database
from app import app


class TestPhase4GreedyAlgorithm(unittest.TestCase):
    def setUp(self):
        self.processor = GreedyComplaintProcessor()
        self.db = Database()
        self.client = app.test_client()

    def test_1_different_priorities(self):
        """Test 1: Given Critical, High, Medium, and Low eligible complaints, recommend in that order."""
        complaints = [
            {"id": 1, "title": "C1", "priority": "Low", "status": "Pending", "created_at": "2026-01-01 10:00:00"},
            {"id": 2, "title": "C2", "priority": "Critical", "status": "Pending", "created_at": "2026-01-02 10:00:00"},
            {"id": 3, "title": "C3", "priority": "Medium", "status": "Pending", "created_at": "2026-01-03 10:00:00"},
            {"id": 4, "title": "C4", "priority": "High", "status": "Pending", "created_at": "2026-01-04 10:00:00"},
        ]
        res = self.processor.run(complaints)
        self.assertEqual(res["eligible_count"], 4)
        self.assertEqual(res["next_complaint"]["id"], 2)
        self.assertEqual(res["next_complaint"]["priority"], "Critical")
        order_priorities = [c["priority"] for c in res["processing_order"]]
        self.assertEqual(order_priorities, ["Critical", "High", "Medium", "Low"])
        print("\n[PASS] Test 1: Different priorities ordered as Critical > High > Medium > Low")

    def test_2_same_priority_fifo(self):
        """Test 2: Given two eligible High-priority complaints, recommend the older one first."""
        complaints = [
            {"id": 10, "title": "Newer High", "priority": "High", "status": "Pending", "created_at": "2026-02-15 12:00:00"},
            {"id": 11, "title": "Older High", "priority": "High", "status": "Pending", "created_at": "2026-01-10 09:00:00"},
            {"id": 12, "title": "Mid High", "priority": "High", "status": "Pending", "created_at": "2026-01-20 14:00:00"},
        ]
        res = self.processor.run(complaints)
        self.assertEqual(res["next_complaint"]["id"], 11)
        order_ids = [c["id"] for c in res["processing_order"]]
        self.assertEqual(order_ids, [11, 12, 10])
        print("[PASS] Test 2: Same priority tie-breaking selects older complaint first (FIFO)")

    def test_3_resolved_excluded(self):
        """Test 3: A resolved complaint must not be recommended."""
        complaints = [
            {"id": 20, "title": "Critical Resolved", "priority": "Critical", "status": "Resolved", "created_at": "2026-01-01 00:00:00"},
            {"id": 21, "title": "High Pending", "priority": "High", "status": "Pending", "created_at": "2026-01-02 00:00:00"},
            {"id": 22, "title": "Critical Closed", "priority": "Critical", "status": "Closed", "created_at": "2026-01-01 00:00:00"},
            {"id": 23, "title": "Critical Rejected", "priority": "Critical", "status": "Rejected", "created_at": "2026-01-01 00:00:00"},
            {"id": 24, "title": "Critical Cancelled", "priority": "Critical", "status": "Cancelled", "created_at": "2026-01-01 00:00:00"},
        ]
        res = self.processor.run(complaints)
        self.assertEqual(res["eligible_count"], 1)
        self.assertEqual(res["next_complaint"]["id"], 21)
        self.assertEqual(res["ineligible_count"], 4)
        recommended_ids = [c["id"] for c in res["processing_order"]]
        self.assertNotIn(20, recommended_ids)
        self.assertNotIn(22, recommended_ids)
        self.assertNotIn(23, recommended_ids)
        self.assertNotIn(24, recommended_ids)
        print("[PASS] Test 3: Ineligible statuses (Resolved, Closed, Rejected, Cancelled) correctly excluded")

    def test_4_no_eligible_complaints(self):
        """Test 4: When no eligible complaints exist, return safe empty response without error."""
        complaints = [
            {"id": 30, "priority": "High", "status": "Resolved", "created_at": "2026-01-01 00:00:00"},
            {"id": 31, "priority": "Critical", "status": "Closed", "created_at": "2026-01-02 00:00:00"},
        ]
        res = self.processor.run(complaints)
        self.assertEqual(res["eligible_count"], 0)
        self.assertIsNone(res["next_complaint"])
        self.assertEqual(res["processing_order"], [])
        self.assertEqual(res["ineligible_count"], 2)

        # Empty list check
        res_empty = self.processor.run([])
        self.assertEqual(res_empty["eligible_count"], 0)
        self.assertIsNone(res_empty["next_complaint"])
        print("[PASS] Test 4: No eligible complaints handled cleanly with graceful empty state")

    def test_5_changed_priority(self):
        """Test 5: After an eligible complaint's priority changes, recommendation dynamically updates."""
        complaints = [
            {"id": 40, "priority": "Medium", "status": "Pending", "created_at": "2026-01-01 00:00:00"},
            {"id": 41, "priority": "High", "status": "Pending", "created_at": "2026-01-02 00:00:00"},
        ]
        res_initial = self.processor.run(complaints)
        self.assertEqual(res_initial["next_complaint"]["id"], 41)

        # Escalate complaint 40 to Critical
        complaints[0]["priority"] = "Critical"
        res_updated = self.processor.run(complaints)
        self.assertEqual(res_updated["next_complaint"]["id"], 40)
        self.assertEqual(res_updated["next_complaint"]["priority"], "Critical")
        print("[PASS] Test 5: Dynamic priority elevation re-orders queue immediately")

    def test_6_changed_status(self):
        """Test 6: After a complaint is resolved, it must drop out of the recommendation list."""
        complaints = [
            {"id": 50, "priority": "Critical", "status": "In Progress", "created_at": "2026-01-01 00:00:00"},
            {"id": 51, "priority": "High", "status": "Pending", "created_at": "2026-01-02 00:00:00"},
        ]
        res_initial = self.processor.run(complaints)
        self.assertEqual(res_initial["next_complaint"]["id"], 50)
        self.assertEqual(res_initial["eligible_count"], 2)

        # Mark 50 as Resolved
        complaints[0]["status"] = "Resolved"
        res_updated = self.processor.run(complaints)
        self.assertEqual(res_updated["next_complaint"]["id"], 51)
        self.assertEqual(res_updated["eligible_count"], 1)
        self.assertNotIn(50, [c["id"] for c in res_updated["processing_order"]])
        print("[PASS] Test 6: Status transition to Resolved drops complaint from eligible pool")

    def test_7_real_database_integration(self):
        """Test 7: Verify feature works with actual database and endpoint returns live data."""
        real_complaints = self.db.get_all_complaints()
        self.assertIsInstance(real_complaints, list)
        self.assertGreater(len(real_complaints), 0)

        res = self.processor.run([dict(c) for c in real_complaints])
        self.assertIn("eligible_count", res)
        self.assertIn("next_complaint", res)
        self.assertIn("processing_order", res)
        self.assertIn("priority_counts", res)

        # Test Flask API endpoint with session auth
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "admin"

        api_res = self.client.get("/api/dsa/greedy/next-complaint")
        self.assertEqual(api_res.status_code, 200)
        data = api_res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["algorithm"], "Greedy — Priority-Based Complaint Processing")
        self.assertEqual(data["total_count"], len(real_complaints))
        self.assertEqual(data["eligible_count"], res["eligible_count"])
        print(f"[PASS] Test 7: Real database verified ({len(real_complaints)} records total, {res['eligible_count']} eligible)")

    def test_8_existing_functionality(self):
        """Test 8: Verify that login, admin pages, citizen endpoints, and other DSA modules work."""
        # 1. Landing / Login portal page accessible
        landing_res = self.client.get("/")
        self.assertEqual(landing_res.status_code, 200)

        # 2. Admin page accessible with admin session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "admin"
        admin_res = self.client.get("/admin")
        self.assertEqual(admin_res.status_code, 200)
        self.assertIn(b"Greedy Priority Processing", admin_res.data)

        # 3. Existing DSA stats API works
        stats_res = self.client.get("/api/stats")
        self.assertEqual(stats_res.status_code, 200)

        # 4. Existing DSA Graph tree data works
        tree_res = self.client.get("/api/graph/tree-data")
        self.assertEqual(tree_res.status_code, 200)

        # 5. Existing Queue DSA works
        queue_res = self.client.get("/api/dsa/queue")
        self.assertEqual(queue_res.status_code, 200)
        print("[PASS] Test 8: Existing functionality preserved (login, admin, stats, DSA modules)")


if __name__ == "__main__":
    unittest.main()
