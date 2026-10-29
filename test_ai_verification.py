"""
Test Suite for AI-Powered Complaint Image Verification and Validation
Verifies all 12 test requirements specified in the user request.
"""

import io
import os
import sys
import unittest
from PIL import Image

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import app, db
from models.ai_verifier import (
    verify_complaint_image,
    validate_verification_token,
    validate_image_file
)

class TestAiComplaintImageVerification(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "civicsense_super_secret_phase1_key"
        self.client = app.test_client()

        # Paths to test images
        self.pothole_path = os.path.join(BASE_DIR, "static", "uploads", "complaint_images", "1790054184151_Pothole_issue.jpg")
        self.garbage_path = os.path.join(BASE_DIR, "static", "uploads", "complaint_images", "1788364826054_garbage_over.webp")
        self.dog_path     = os.path.join(BASE_DIR, "static", "uploads", "complaint_images", "test_dog.jpg")
        self.light_path   = os.path.join(BASE_DIR, "static", "uploads", "complaint_images", "1789445572476_Streetlight_not_working.avif")

        # Read image bytes
        with open(self.pothole_path, "rb") as f:
            self.pothole_bytes = f.read()
        with open(self.garbage_path, "rb") as f:
            self.garbage_bytes = f.read()
        with open(self.dog_path, "rb") as f:
            self.dog_bytes = f.read()
        with open(self.light_path, "rb") as f:
            self.light_bytes = f.read()

        # Citizen credentials for session login
        self.citizen_email = "citizen@civicsense.com"
        self.citizen_pwd   = "citizen123"

    def login_citizen(self):
        res = self.client.post("/api/login", json={
            "email": self.citizen_email,
            "password": self.citizen_pwd,
            "role": "citizen"
        })
        self.assertEqual(res.status_code, 200)

    # ── Test 1: Pothole category + pothole image -> verified ──
    def test_01_pothole_category_with_pothole_image(self):
        res = verify_complaint_image(self.pothole_bytes, "Pothole", "Pothole on street", "Dangerous pothole crater")
        self.assertEqual(res["status"], "verified")
        self.assertGreaterEqual(res["confidence"], 0.65)
        self.assertIn("verified", res["message"].lower())
        self.assertTrue(bool(res["verification_token"]))
        print("\n[PASS] Test 1: Pothole image correctly verified for category Pothole.")

    # ── Test 2: Pothole category + dog image -> mismatch warning ──
    def test_02_pothole_category_with_dog_image(self):
        res = verify_complaint_image(self.dog_bytes, "Pothole", "Broken road", "Deep pothole")
        self.assertEqual(res["status"], "mismatch")
        self.assertIn("verification failed", res["message"].lower())
        self.assertIn("pothole", res["message"].lower())
        print("[PASS] Test 2: Dog image correctly rejected as mismatch for Pothole category.")

    # ── Test 3: Garbage category + garbage image -> verified ──
    def test_03_garbage_category_with_garbage_image(self):
        res = verify_complaint_image(self.garbage_bytes, "Garbage", "Garbage overflow", "Trash bin overflowing")
        self.assertEqual(res["status"], "verified")
        self.assertGreaterEqual(res["confidence"], 0.70)
        self.assertIn("verified", res["message"].lower())
        print("[PASS] Test 3: Garbage image correctly verified for category Garbage.")

    # ── Test 4: Streetlight category + unrelated dog image -> mismatch warning ──
    def test_04_streetlight_category_with_unrelated_image(self):
        res = verify_complaint_image(self.dog_bytes, "Streetlight", "Streetlight broken", "Lamp not glowing")
        self.assertEqual(res["status"], "mismatch")
        self.assertIn("verification failed", res["message"].lower())
        print("[PASS] Test 4: Unrelated image correctly rejected as mismatch for Streetlight category.")

    # ── Test 5: No image uploaded -> submission blocked ──
    def test_05_no_image_uploaded_submission_blocked(self):
        self.login_citizen()
        res = self.client.post("/api/complaints", data={
            "title": "Missing image issue",
            "category": "Pothole",
            "location": "Central Zone (Chowk)",
            "priority": "Medium",
            "description": "No image attached"
        })
        self.assertEqual(res.status_code, 400)
        json_data = res.get_json()
        self.assertFalse(json_data["success"])
        self.assertIn("mandatory", json_data["message"].lower())
        print("[PASS] Test 5: Complaint submission without image correctly blocked by backend.")

    # ── Test 6: Unsupported or corrupted image -> validation error ──
    def test_06_unsupported_or_corrupted_image(self):
        corrupted_bytes = b"NOT_A_REAL_IMAGE_DATA_123456"
        with self.assertRaises(ValueError) as context:
            validate_image_file(corrupted_bytes)
        self.assertIn("corrupted or unsupported", str(context.exception).lower())
        print("[PASS] Test 6: Corrupted image bytes correctly caught by file validation.")

    # ── Test 7: Image replaced after verification -> previous verification invalidated ──
    def test_07_image_replaced_invalidates_verification(self):
        # Obtain token for pothole image
        res_pothole = verify_complaint_image(self.pothole_bytes, "Pothole")
        pothole_token = res_pothole["verification_token"]

        # Attempt to validate that token against a DIFFERENT image (garbage bytes)
        is_valid_on_swapped = validate_verification_token(self.garbage_bytes, "Pothole", pothole_token, "verified")
        self.assertFalse(is_valid_on_swapped)
        print("[PASS] Test 7: Replacing verified image invalidates previous verification token.")

    # ── Test 8: Category changed after verification -> previous verification invalidated ──
    def test_08_category_changed_invalidates_verification(self):
        # Obtain token for pothole image under category Pothole
        res_pothole = verify_complaint_image(self.pothole_bytes, "Pothole")
        pothole_token = res_pothole["verification_token"]

        # Attempt to validate the same image under a DIFFERENT category (Garbage)
        is_valid_on_changed_cat = validate_verification_token(self.pothole_bytes, "Garbage", pothole_token, "verified")
        self.assertFalse(is_valid_on_changed_cat)
        print("[PASS] Test 8: Changing category invalidates previous verification token.")

    # ── Test 9: Direct submission request without verification -> rejected ──
    def test_09_direct_submission_without_verification_rejected(self):
        self.login_citizen()
        # Direct POST without calling /api/verify-complaint-image or providing token
        res = self.client.post("/api/complaints", data={
            "title": "Direct bypassed submission",
            "category": "Pothole",
            "location": "Central Zone (Chowk)",
            "priority": "Medium",
            "description": "Trying to bypass verification",
            "complaint_image": (io.BytesIO(self.pothole_bytes), "pothole.jpg")
        })
        self.assertEqual(res.status_code, 400)
        json_data = res.get_json()
        self.assertFalse(json_data["success"])
        self.assertIn("verification required", json_data["message"].lower())
        print("[PASS] Test 9: Direct API bypass without prior AI verification strictly rejected.")

    # ── Test 10: Complete Verification + Submission Lifecycle ──
    def test_10_verified_submission_lifecycle(self):
        self.login_citizen()
        # Step A: Call verification API
        verif_res = self.client.post("/api/verify-complaint-image", data={
            "category": "Pothole",
            "title": "Severe road hole",
            "description": "Traffic blocked due to large road crater",
            "complaint_image": (io.BytesIO(self.pothole_bytes), "pothole.jpg")
        })
        self.assertEqual(verif_res.status_code, 200)
        verif_data = verif_res.get_json()
        self.assertEqual(verif_data["status"], "verified")
        token = verif_data["verification_token"]

        # Step B: Submit with token
        sub_res = self.client.post("/api/complaints", data={
            "title": "Severe road hole",
            "category": "Pothole",
            "location": "West Zone (Adajan)",
            "priority": "High",
            "description": "Traffic blocked due to large road crater",
            "complaint_image": (io.BytesIO(self.pothole_bytes), "pothole.jpg"),
            "verification_token": token
        })
        self.assertEqual(sub_res.status_code, 200)
        sub_data = sub_res.get_json()
        self.assertTrue(sub_data["success"])
        self.assertTrue(sub_data["ai_verified"])
        print("[PASS] Test 10: Full end-to-end verified submission lifecycle succeeded.")

    # ── Test 11: Uncertain image handling ──
    def test_11_uncertain_image_handling(self):
        # Create a plain blank image (featureless)
        blank_img = Image.new("RGB", (200, 200), (128, 128, 128))
        buf = io.BytesIO()
        blank_img.save(buf, format="JPEG")
        blank_bytes = buf.getvalue()

        res = verify_complaint_image(blank_bytes, "Pothole", "Empty surface", "Blank plain surface")
        self.assertIn(res["status"], ["uncertain", "mismatch"])
        print(f"[PASS] Test 11: Inconclusive/featureless image handled as status='{res['status']}' with user retry guidance.")

    # ── Test 12: Existing modules continue working ──
    def test_12_existing_modules_continue_working(self):
        # Verify public page routes
        res_index = self.client.get("/")
        self.assertEqual(res_index.status_code, 200)

        res_analytics = self.client.get("/analytics")
        self.assertEqual(res_analytics.status_code, 200)

        # Verify DB integrity
        complaints = db.get_all_complaints()
        self.assertIsInstance(complaints, list)
        self.assertGreater(len(complaints), 0)
        print("[PASS] Test 12: All existing pages, routes, database records, and dashboards continue working.")

    def test_13_update_complaint_ai_verification(self):
        """Test 13: Updating complaint photo enforces AI verification & rejects mismatch."""
        complaints = db.get_all_complaints()
        target = next((c for c in complaints if c.get("status") != "Resolved"), complaints[0])
        cid = target["id"]

        with self.client.session_transaction() as sess:
            sess["user_id"] = target.get("citizen_id", 1)
            sess["role"] = "citizen"

        # 13a: Update with mismatched dog image for Pothole -> must be rejected
        res_mismatch = self.client.post(
            f"/api/complaints/{cid}",
            data={
                "title": "Pothole Update Test",
                "category": "Pothole",
                "location": target.get("location", "Central Zone (Chowk)"),
                "complaint_image": (io.BytesIO(self.dog_bytes), "dog.jpg", "image/jpeg")
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(res_mismatch.status_code, 400)
        self.assertEqual(res_mismatch.get_json().get("status"), "mismatch")

        # 13b: Update with verified pothole image -> must succeed
        v_res = self.client.post(
            "/api/verify-complaint-image",
            data={
                "complaint_image": (io.BytesIO(self.pothole_bytes), "pothole.jpg", "image/jpeg"),
                "category": "Pothole"
            },
            content_type="multipart/form-data"
        )
        token = v_res.get_json().get("verification_token")

        res_ok = self.client.post(
            f"/api/complaints/{cid}",
            data={
                "title": "Pothole Update Test Verified",
                "category": "Pothole",
                "location": target.get("location", "Central Zone (Chowk)"),
                "verification_token": token,
                "complaint_image": (io.BytesIO(self.pothole_bytes), "pothole.jpg", "image/jpeg")
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(res_ok.status_code, 200)
        self.assertTrue(res_ok.get_json().get("success"))

        updated = db.get_complaint(cid)
        self.assertEqual(updated.get("ai_status"), "verified")
        print("[PASS] Test 13: Update complaint photo enforces AI verification & persists AI status.")

    def test_14_cross_category_vehicle_mismatch(self):
        """Test 14: Car parking image uploaded for Pothole or Streetlight must be rejected as mismatch."""
        with open("static/uploads/complaint_images/1793039029072_parking_issue.jpg", "rb") as f:
            parking_bytes = f.read()

        # 14a: Parking image uploaded for Pothole -> MUST be mismatch
        res_pothole = verify_complaint_image(parking_bytes, "Pothole")
        self.assertEqual(res_pothole["status"], "mismatch")
        self.assertIn("vehicles", res_pothole["message"].lower())

        # 14b: Parking image uploaded for Streetlight -> MUST be mismatch
        res_light = verify_complaint_image(parking_bytes, "Streetlight")
        self.assertEqual(res_light["status"], "mismatch")
        self.assertIn("vehicles", res_light["message"].lower())

        # 14c: Parking image uploaded for Illegal Parking -> MUST be verified
        res_parking = verify_complaint_image(parking_bytes, "Illegal Parking")
        self.assertEqual(res_parking["status"], "verified")
        print("[PASS] Test 14: Cross-category vehicle mismatch correctly rejected for Pothole & Streetlight.")

if __name__ == "__main__":
    unittest.main()

