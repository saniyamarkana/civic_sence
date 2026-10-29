"""
AI-Powered Complaint Image Verification and Validation Module for CivicSense.
Supports:
  1. Local Pretrained Computer Vision Neural Network (ONNX SqueezeNet/MobileNet)
     with Semantic Scene & Texture Analysis (zero cloud latency / works completely offline).
  2. Cloud Vision-Language Model (Gemini Vision API) when GEMINI_API_KEY is configured.
  3. Cryptographic Token Binding (HMAC-SHA256) to ensure the submitted image
     and category cannot be tampered with or bypassed on the client side.
"""

import os
import io
import time
import json
import base64
import hmac
import hashlib
from PIL import Image

# Robust Independent Imports
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    ort = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "squeezenet1.1-7.onnx")
LABELS_PATH = os.path.join(BASE_DIR, "models", "imagenet_labels.json")

# Load 1000 ImageNet label names if available
IMAGENET_LABELS = []
if os.path.exists(LABELS_PATH):
    try:
        with open(LABELS_PATH, "r", encoding="utf-8") as _lf:
            IMAGENET_LABELS = json.load(_lf)
    except Exception as _e:
        IMAGENET_LABELS = []

# Lazy-loaded ONNX Session
_ONNX_SESSION = None

# Secret key for HMAC token signing (falls back to default if not configured)
DEFAULT_SECRET = "civicsense_ai_verification_secret_2026"

def get_secret_key():
    return os.environ.get("FLASK_SECRET_KEY", DEFAULT_SECRET)

def get_onnx_session():
    """Singleton getter for the local ONNX inference session."""
    global _ONNX_SESSION
    if _ONNX_SESSION is None and ONNX_AVAILABLE:
        if os.path.exists(MODEL_PATH):
            try:
                _ONNX_SESSION = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
            except Exception as e:
                print(f"[AI Verifier] Failed to load ONNX model: {e}")
                _ONNX_SESSION = None
    return _ONNX_SESSION

# ─────────────────────────────────────────────────────────────────────────────
# 1. Semantic Class Categories for ImageNet 1000 Labels
# ─────────────────────────────────────────────────────────────────────────────

# Animals & Domestic Pets (Always mismatch for civic infrastructure)
PET_AND_ANIMAL_KEYWORDS = {
    "dog", "puppy", "hound", "terrier", "retriever", "spaniel", "shepherd",
    "poodle", "collie", "chihuahua", "pug", "bulldog", "beagle", "boxer",
    "cat", "kitten", "tabby", "siamese", "persian", "egyptian cat", "cougar",
    "lion", "tiger", "bear", "fox", "wolf", "rabbit", "hamster", "mouse",
    "horse", "zebra", "pig", "cow", "ox", "sheep", "goat", "elephant",
    "monkey", "ape", "chimpanzee", "bird", "parrot", "canary", "duck", "goose",
    "chicken", "rooster", "fish", "shark", "frog", "lizard", "snake"
}

# Indoor / Domestic Household items (Unrelated to outdoor civic issues)
INDOOR_IRRELEVANT_KEYWORDS = {
    "bedroom", "bed", "pillow", "quilt", "sofa", "couch", "wardrobe",
    "dining table", "refrigerator", "microwave", "oven", "toaster",
    "television", "laptop", "cellphone", "keyboard", "mouse", "teddy",
    "teddy bear", "lipstick", "perfume", "shoe", "sneaker", "dress",
    "suit", "pajamas", "watch", "necklace"
}

# Documents, Printed Text, Paper, Books, Screenshots (Always mismatch for outdoor civic issues)
DOCUMENT_AND_TEXT_KEYWORDS = {
    "website", "web site", "dust jacket", "book", "comic book", "menu",
    "envelope", "ring binder", "paper", "document", "screen", "monitor",
    "crt screen", "television", "ballpoint pen", "fountain pen", "pencil",
    "ruler", "packet", "notebook", "sunscreen", "bookcase", "bookstore",
    "paper towel", "pencil case", "pencil sharpener", "paper knife"
}

# Vehicles, Automobiles, and Parking Items (Exclusively for Illegal Parking)
VEHICLE_AND_PARKING_KEYWORDS = {
    "car", "automobile", "passenger car", "minivan", "van", "pickup", "truck",
    "trailer", "cab", "taxi", "limousine", "convertible", "jeep", "sports car",
    "racer", "race car", "motor scooter", "scooter", "moped", "motorcycle",
    "bike", "bicycle", "mountain bike", "bus", "parking meter", "disc brake",
    "snowmobile", "bobsleigh", "crash helmet", "vehicle", "parking", "golfcart",
    "tow truck", "trailer truck", "tractor trailer", "police van", "beach wagon",
    "station wagon", "landrover", "wheelbarrow", "go-kart", "ambulance", "forklift"
}

# Civic category semantic keyword mappings
CATEGORY_SEMANTIC_MAP = {
    "Pothole": {
        "keywords": ["pothole", "road", "asphalt", "pavement", "crack", "street", "barrier", "manhole cover", "curb", "curbstone", "grille", "gravel", "tarmac", "hole", "highway"],
        "display_name": "Pothole / Damaged Road"
    },
    "Damaged Road": {
        "keywords": ["damaged road", "road", "asphalt", "pavement", "crack", "barrier", "manhole cover", "curb", "curbstone", "street", "tarmac", "highway", "gravel"],
        "display_name": "Damaged Road"
    },
    "Garbage": {
        "keywords": ["garbage", "trash", "waste", "rubbish", "ashcan", "trash can", "garbage truck", "barrel", "crate", "carton", "plastic bag", "water bottle", "dumpster", "litter", "debris"],
        "display_name": "Garbage / Solid Waste"
    },
    "Public Cleanliness": {
        "keywords": ["cleanliness", "garbage", "trash", "waste", "litter", "ashcan", "broom", "dust", "debris", "dirt", "pavement"],
        "display_name": "Public Cleanliness"
    },
    "Streetlight": {
        "keywords": ["streetlight", "street light", "lamp", "lampshade", "spotlight", "pole", "light pole", "lantern", "traffic light", "beacon", "lighting", "electric pole"],
        "display_name": "Streetlight / Public Lighting"
    },
    "Water Leakage": {
        "keywords": ["water leakage", "water leak", "water", "pipe", "pipeline", "puddle", "fountain", "geyser", "dam", "washbasin", "tub", "water jug", "plumbing", "spray"],
        "display_name": "Water Leakage"
    },
    "Drainage": {
        "keywords": ["drainage", "drain", "sewer", "manhole", "manhole cover", "water", "gutter", "puddle", "overflow", "grille", "culvert"],
        "display_name": "Drainage Overflow"
    },
    "Illegal Parking": {
        "keywords": [
            "parking", "car", "cab", "minivan", "pickup", "truck", "automobile", "motor scooter",
            "moped", "vehicle", "parking meter", "traffic", "street", "curb", "brake", "disc brake",
            "wheel", "cart", "bus", "jeep", "trailer", "tow truck", "limousine", "convertible"
        ],
        "display_name": "Illegal Parking"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. Image Preprocessing & Texture Feature Extraction
# ─────────────────────────────────────────────────────────────────────────────

def validate_image_file(file_obj_or_bytes):
    """
    Validates file format, readability, and dimensions.
    Returns (PIL.Image, image_bytes) or raises ValueError.
    """
    if file_obj_or_bytes is None:
        raise ValueError("No image file provided.")

    if hasattr(file_obj_or_bytes, "read"):
        file_bytes = file_obj_or_bytes.read()
        # Rewind if possible
        if hasattr(file_obj_or_bytes, "seek"):
            file_obj_or_bytes.seek(0)
    elif isinstance(file_obj_or_bytes, (bytes, bytearray)):
        file_bytes = bytes(file_obj_or_bytes)
    else:
        raise ValueError("Invalid file object type.")

    if len(file_bytes) == 0:
        raise ValueError("Uploaded image file is empty (0 bytes).")

    if len(file_bytes) > 15 * 1024 * 1024:
        raise ValueError("Image file exceeds maximum permitted size of 15MB.")

    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
        # Re-open after verify() since verify() alters file pointer
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except Exception as e:
        raise ValueError(f"Corrupted or unsupported image file: {str(e)}")

    if img.width < 30 or img.height < 30:
        raise ValueError("Image resolution is too low for verification (minimum 30x30 pixels required).")

    return img, file_bytes

def preprocess_for_onnx(pil_img):
    """
    Preprocess image to standard SqueezeNet / MobileNet NCHW tensor:
    Resize 224x224, normalize with ImageNet mean/std.
    """
    img = pil_img.resize((224, 224), Image.Resampling.BILINEAR)
    arr = np.array(img).astype(np.float32) / 255.0  # (224, 224, 3)

    # Standard ImageNet normalization
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    arr = (arr - mean) / std

    # HWC to CHW -> (3, 224, 224)
    arr = np.transpose(arr, (2, 0, 1))
    # Add batch dim -> (1, 3, 224, 224)
    arr = np.expand_dims(arr, axis=0)
    return arr

def analyze_visual_features(pil_img):
    """
    Extracts computer vision heuristic features:
    - Road asphalt color presence (dark gray / muted tones)
    - Contrast and edge variance (cracks, potholes, waste piles)
    - Brightness distribution
    Works with NumPy or pure PIL fallback.
    """
    if np is not None:
        gray = pil_img.convert("L").resize((128, 128))
        arr = np.array(gray).astype(np.float32)
        
        mean_val = float(np.mean(arr))
        std_val  = float(np.std(arr))
        white_fraction = float(np.mean(arr > 185))
        max_val = float(np.max(arr))
        
        # Laplacian-like high frequency / edge density
        diff_h = np.abs(arr[1:, :] - arr[:-1, :])
        diff_w = np.abs(arr[:, 1:] - arr[:, :-1])
        edge_density = float((np.mean(diff_h) + np.mean(diff_w)) / 2.0)
        
        # Color check on RGB thumbnail
        rgb_thumb = pil_img.resize((64, 64))
        rgb_arr = np.array(rgb_thumb).astype(np.float32)
        r, g, b = rgb_arr[:, :, 0], rgb_arr[:, :, 1], rgb_arr[:, :, 2]
        color_diff = float(np.mean(np.abs(r - g) + np.abs(g - b) + np.abs(b - r)) / 3.0)
    else:
        gray = pil_img.convert("L").resize((64, 64))
        pixels = list(gray.getdata())
        n = max(len(pixels), 1)
        mean_val = float(sum(pixels) / n)
        variance = float(sum((p - mean_val) ** 2 for p in pixels) / n)
        std_val = float(variance ** 0.5)
        white_fraction = float(sum(1 for p in pixels if p > 185) / n)
        max_val = float(max(pixels)) if pixels else 128.0
        edge_density = 10.0
        color_diff = 20.0
    
    return {
        "mean_brightness": float(mean_val),
        "max_brightness": float(max_val),
        "contrast_std": float(std_val),
        "edge_density": float(edge_density),
        "color_variance": float(color_diff),
        "white_fraction": float(white_fraction)
    }

# ─────────────────────────────────────────────────────────────────────────────
# 3. ONNX Model Inference & Class Decoding
# ─────────────────────────────────────────────────────────────────────────────

# Compact top ImageNet index mapping for critical civic and mismatch classes
def get_imagenet_class_name(idx):
    """Maps ImageNet 1000 index to canonical class name."""
    if IMAGENET_LABELS and 0 <= idx < len(IMAGENET_LABELS):
        raw_name = IMAGENET_LABELS[idx]
        if 151 <= idx <= 268:
            return f"{raw_name} (dog breed)"
        if 281 <= idx <= 285:
            return f"{raw_name} (domestic cat)"
        return raw_name

    # Fallback ranges for dogs and cats
    if 151 <= idx <= 268:
        return f"domestic dog breed (class #{idx})"
    if 281 <= idx <= 285:
        return f"domestic cat (class #{idx})"

    # Common outdoor/civic objects
    mapping = {
        412: "ashcan, trash can, garbage bin",
        428: "barrier, roadblock",
        436: "beach wagon, car",
        468: "cab, taxi",
        511: "convertible, car",
        525: "dam, dike",
        535: "disc brake, automotive car wheel",
        562: "fountain",
        569: "garbage truck, dustcart",
        575: "golfcart, vehicle",
        617: "lampshade, lamp",
        627: "limousine, car",
        637: "manhole cover",
        656: "minivan",
        665: "moped",
        670: "motor scooter",
        705: "passenger car",
        728: "plastic bag",
        734: "police van",
        751: "racer, race car",
        817: "sports car",
        818: "spotlight, searchlight",
        825: "street sign",
        864: "tow truck",
        866: "trailer truck, tractor trailer",
        867: "traffic light, traffic signal",
        898: "water bottle",
        920: "traffic light",
        970: "curb, curbstone",
        974: "geyser",
        978: "seashore, coast",
        979: "lakeside",
        980: "volcano",
    }
    return mapping.get(idx, f"object class #{idx}")

def run_local_onnx_inference(pil_img):
    """
    Runs local ONNX inference on the image and returns top predicted labels and confidences.
    """
    session = get_onnx_session()
    if session is None:
        return []

    input_data = preprocess_for_onnx(pil_img)
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: input_data})
    logits = outputs[0][0]  # shape: (1000,)

    # Softmax
    exp_logits = np.exp(logits - np.max(logits))
    probs = exp_logits / np.sum(exp_logits)

    top_indices = np.argsort(probs)[::-1][:5]
    results = []
    for idx in top_indices:
        results.append({
            "index": int(idx),
            "label": get_imagenet_class_name(int(idx)),
            "probability": float(probs[idx])
        })
    return results

# ─────────────────────────────────────────────────────────────────────────────
# 4. Multimodal Cloud Vision API (Gemini Vision)
# ─────────────────────────────────────────────────────────────────────────────

def run_gemini_vision_verification(image_bytes, category, title="", description=""):
    """
    Calls Google Gemini Multimodal Vision API if GEMINI_API_KEY is available.
    Returns (dict, True) on success or (None, False) on failure/fallback.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None, False

    try:
        import requests
        b64_img = base64.b64encode(image_bytes).decode("utf-8")

        prompt = f"""You are an automated Civic Complaint Verification AI for a municipal corporation.
Analyze this uploaded photograph to verify if it is genuinely relevant to the reported civic complaint.

Reported Category: {category}
Reported Title: {title}
Reported Description: {description}

Determine:
1. Does the image depict issues related to '{category}' (e.g. road pothole, road damage, overflowing garbage, broken streetlight, water pipe leak, drainage overflow, illegal vehicle parking)?
2. Is the image completely UNRELATED (e.g., photo of a pet dog/cat, personal selfie, bedroom furniture, food dish, random unrelated graphic)?
3. Is the image UNCERTAIN (too dark, blurry, corrupted, or impossible to determine)?

Respond ONLY with valid JSON in this exact structure:
{{
  "status": "verified" | "mismatch" | "uncertain",
  "confidence": 0.0 to 1.0,
  "detected_summary": "short description of what is in the photo",
  "explanation": "brief citizen-facing explanation"
}}
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": b64_img
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }

        resp = requests.post(url, json=payload, timeout=12)
        if resp.status_code == 200:
            res_json = resp.json()
            candidates = res_json.get("candidates", [])
            if candidates:
                raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                parsed = json.loads(raw_text)
                return parsed, True
    except Exception as e:
        print(f"[AI Verifier] Gemini Vision API call failed or timed out: {e}")

    return None, False

# ─────────────────────────────────────────────────────────────────────────────
# 5. Core Verification Decision Engine
# ─────────────────────────────────────────────────────────────────────────────

def verify_complaint_image(file_obj_or_bytes, category, title="", description=""):
    """
    Main verification pipeline:
      1. Validates image integrity and format.
      2. Tries Gemini Vision Multimodal API if configured.
      3. Otherwise uses Local Pretrained ONNX Computer Vision + Semantic Analysis.
      4. Cryptographically signs verification token with HMAC-SHA256.
    Returns:
      dict with keys:
        - status: 'verified' | 'mismatch' | 'uncertain'
        - confidence: float (0.0 to 1.0)
        - message: user-facing explanation
        - model_used: 'Gemini-Vision-API' | 'SqueezeNet-ONNX-Local'
        - image_hash: SHA256 of image bytes
        - verification_token: cryptographic tamper-proof token
        - detected_objects: list of top detected tags
    """
    # Step 1: Validate file & get PIL image + bytes
    pil_img, img_bytes = validate_image_file(file_obj_or_bytes)
    img_hash = hashlib.sha256(img_bytes).hexdigest()
    
    norm_cat = category.strip() if category else "Garbage"
    sem_info = CATEGORY_SEMANTIC_MAP.get(norm_cat, {
        "keywords": [norm_cat.lower()],
        "display_name": norm_cat
    })

    # Step 2: Try Cloud Vision LLM if available
    gemini_res, gemini_ok = run_gemini_vision_verification(img_bytes, norm_cat, title, description)
    if gemini_ok and gemini_res:
        status = gemini_res.get("status", "uncertain").lower()
        confidence = float(gemini_res.get("confidence", 0.8))
        detected_summary = gemini_res.get("detected_summary", "Analyzed image")
        explanation = gemini_res.get("explanation", "")

        if status == "verified":
            msg = f"Image Verified: The uploaded image appears relevant to your selected complaint category ({norm_cat}). You can now submit your complaint."
        elif status == "mismatch":
            msg = f"Image Verification Failed: The uploaded image does not appear to match the selected complaint category, {norm_cat}. (Detected: {detected_summary}). Please upload a relevant photograph of the {norm_cat} issue."
        else:
            status = "uncertain"
            msg = "Unable to verify this image confidently. Please upload a clearer photograph showing the reported problem."

        token = generate_verification_token(img_bytes, norm_cat, status)
        return {
            "status": status,
            "confidence": round(confidence, 2),
            "message": msg,
            "detected_objects": [detected_summary],
            "model_used": "Gemini-1.5-Flash (Cloud VLM)",
            "image_hash": img_hash,
            "verification_token": token
        }

    # Step 3: Local Pretrained ONNX Computer Vision Model + Scene Analysis
    top_preds = run_local_onnx_inference(pil_img)
    vis_features = analyze_visual_features(pil_img)

    detected_labels = [p["label"] for p in top_preds]
    top_label = detected_labels[0] if detected_labels else "Unclassified Object"
    top_prob = top_preds[0]["probability"] if top_preds else 0.5

    # Check A: Is it clearly a domestic pet, animal, indoor item, document/text, or vehicle?
    is_pet_or_animal = any(
        (151 <= p["index"] <= 285) or any(k in p["label"].lower() for k in PET_AND_ANIMAL_KEYWORDS)
        for p in top_preds[:2]
    ) and (top_prob > 0.15 or (top_preds and (151 <= top_preds[0]["index"] <= 285)))

    is_indoor_unrelated = any(
        any(k in p["label"].lower() for k in INDOOR_IRRELEVANT_KEYWORDS)
        for p in top_preds[:2]
    )

    is_document_or_text = any(
        any(k in p["label"].lower() for k in DOCUMENT_AND_TEXT_KEYWORDS)
        for p in top_preds[:2]
    ) or (vis_features.get("white_fraction", 0) > 0.50 and vis_features["mean_brightness"] > 165)

    # Check vehicle and parking presence (excluding sanitation garbage trucks)
    veh_matches = [
        p["label"] for p in top_preds[:4]
        if any(k in p["label"].lower() for k in VEHICLE_AND_PARKING_KEYWORDS)
        and "garbage truck" not in p["label"].lower()
    ]
    is_vehicle_or_parking = len(veh_matches) > 0
    top_veh_name = veh_matches[0].split(" (class")[0] if veh_matches else "vehicle"

    # Check lighting infrastructure
    LIGHTING_KEYWORDS = {
        "light", "lamp", "lampshade", "spotlight", "searchlight", "pole", "lantern",
        "beacon", "traffic light", "torch", "candle", "bulb", "chandelier", "fluorescent",
        "safety pin", "hook", "nail"
    }
    has_lighting_infrastructure = any(
        any(k in p["label"].lower() for k in LIGHTING_KEYWORDS)
        for p in top_preds[:4]
    )

    # Check B: Does it match civic category semantics?
    cat_keywords = sem_info["keywords"]
    direct_civic_match = any(
        any(k in p["label"].lower() for k in cat_keywords)
        for p in top_preds
    )

    # Check C: Visual Texture & Asphalt/Road heuristics
    # Real asphalt roads and potholes exhibit dark gray/tarmac tones, low white background, and crack edge variance
    is_asphalt_texture = (
        35 < vis_features["mean_brightness"] < 155
        and vis_features.get("white_fraction", 0) < 0.20
        and vis_features["color_variance"] < 35  # Muted grayscale/road hue
        and vis_features["edge_density"] > 7.0   # Structural crack / crater edges
    )
    is_waste_pile = (
        vis_features["edge_density"] > 10.0 and vis_features["contrast_std"] > 30.0
    )

    # Decision Logic:
    status = "uncertain"
    confidence = 0.50
    explanation = ""

    # 1. Unambiguous Mismatch: Animals & Domestic Pets
    if is_pet_or_animal:
        status = "mismatch"
        confidence = max(top_prob, 0.88)
        detected_name = top_label.split(" (class")[0]
        explanation = f"Image Verification Failed: The uploaded image does not appear to match the selected complaint category, {norm_cat}. (Detected: {detected_name}). Please upload a relevant photograph of the {norm_cat} issue."

    # 2. Unambiguous Mismatch: Documents, Paper, Books, Screenshots
    elif is_document_or_text:
        status = "mismatch"
        confidence = max(top_prob, 0.90)
        detected_name = top_label.split(" (class")[0]
        explanation = f"Image Verification Failed: The uploaded image appears to be a printed document, text page, or screenshot ({detected_name}), not a physical outdoor {norm_cat} issue. Please upload a clear photo of the actual {norm_cat}."

    # 3. Unambiguous Mismatch: Indoor Household Items
    elif is_indoor_unrelated:
        status = "mismatch"
        confidence = 0.82
        detected_name = top_label.split(" (class")[0]
        explanation = f"Image Verification Failed: The uploaded image appears to show indoor items ({detected_name}), not an outdoor civic {norm_cat} issue. Please upload a clear photo of the problem."

    # 4. Cross-Category Conflict: Vehicles or Parking lot uploaded for non-parking category!
    elif is_vehicle_or_parking and norm_cat != "Illegal Parking":
        status = "mismatch"
        confidence = 0.88
        explanation = f"Image Verification Failed: The uploaded image shows vehicles or a parking area (Detected: {top_veh_name}), which does not match your selected complaint category '{norm_cat}'. Please upload a relevant photograph of the {norm_cat} issue."

    # 5. Category-Specific Validation
    elif norm_cat == "Illegal Parking":
        if is_vehicle_or_parking or direct_civic_match:
            status = "verified"
            confidence = 0.90
            explanation = f"Image Verified: The uploaded image appears relevant to your selected complaint category ({norm_cat}). Vehicle ({top_veh_name}) detected in scene. You can now submit your complaint."
        else:
            status = "mismatch"
            confidence = 0.85
            detected_name = top_label.split(" (class")[0]
            explanation = f"Image Verification Failed: The uploaded image does not appear to show parked or obstructing vehicles (Detected: {detected_name}). Please upload a clear photo of the parking violation."

    elif norm_cat in ["Pothole", "Damaged Road"]:
        if is_asphalt_texture or direct_civic_match:
            status = "verified"
            confidence = 0.85 if is_asphalt_texture else 0.75
            explanation = f"Image Verified: The uploaded image appears relevant to your selected complaint category ({norm_cat}). Road surface and damage texture detected. You can now submit your complaint."
        elif vis_features["edge_density"] < 3.0 and vis_features["contrast_std"] < 15.0:
            status = "uncertain"
            confidence = 0.45
            explanation = "Unable to verify this image confidently. The photo appears too plain or blurry. Please upload a clearer photograph showing the pothole or damaged road."
        else:
            status = "uncertain"
            confidence = 0.50
            explanation = f"Unable to verify this image confidently for {norm_cat}. The photo does not clearly show road damage or a pothole. Please upload a clearer photograph."

    elif norm_cat == "Streetlight":
        if has_lighting_infrastructure or direct_civic_match:
            status = "verified"
            confidence = 0.84
            explanation = f"Image Verified: The uploaded image appears relevant to your selected complaint category ({norm_cat}). Lighting infrastructure detected. You can now submit your complaint."
        else:
            status = "mismatch"
            confidence = 0.82
            detected_name = top_label.split(" (class")[0]
            explanation = f"Image Verification Failed: The uploaded image does not appear to show a streetlight, lamp post, or public lighting fixture (Detected: {detected_name}). Please upload a photograph of the streetlight issue."

    elif norm_cat in ["Garbage", "Public Cleanliness"]:
        if direct_civic_match or is_waste_pile or any(k in top_label.lower() for k in ["carton", "barrel", "ashcan", "bottle", "bag", "truck", "broom", "waste"]):
            status = "verified"
            confidence = 0.86
            explanation = f"Image Verified: The uploaded image appears relevant to your selected complaint category ({norm_cat}). Solid waste/debris detected. You can now submit your complaint."
        elif vis_features["contrast_std"] < 15.0:
            status = "uncertain"
            confidence = 0.40
            explanation = "Unable to verify this image confidently. Please upload a clearer photograph showing the garbage or cleanliness issue."
        else:
            status = "uncertain"
            confidence = 0.50
            explanation = "Unable to verify this image confidently. The photo does not clearly show garbage or waste debris. Please upload a clearer photograph."

    elif norm_cat in ["Water Leakage", "Drainage"]:
        if direct_civic_match or (vis_features["mean_brightness"] > 30 and vis_features["edge_density"] > 5.0):
            status = "verified"
            confidence = 0.80
            explanation = f"Image Verified: The uploaded image appears relevant to your selected complaint category ({norm_cat}). Water or drainage condition detected. You can now submit your complaint."
        else:
            status = "uncertain"
            confidence = 0.45
            explanation = "Unable to verify this image confidently. Please upload a clearer photograph showing the water leakage or drainage overflow."

    else:
        # Default fallback for other/custom categories
        if is_pet_or_animal or is_indoor_unrelated:
            status = "mismatch"
            confidence = 0.85
            explanation = f"Image Verification Failed: The uploaded image does not appear to match the selected category, {norm_cat}."
        else:
            status = "verified"
            confidence = 0.65
            explanation = f"Image Verified: The uploaded image appears relevant to your selected complaint category ({norm_cat}). You can now submit your complaint."

    token = generate_verification_token(img_bytes, norm_cat, status)

    return {
        "status": str(status),
        "confidence": round(float(confidence), 2),
        "message": str(explanation),
        "detected_objects": [str(p["label"].split(" (class")[0]) for p in top_preds[:3]] if top_preds else ["Visual Feature Analysis"],
        "model_used": "SqueezeNet-ONNX-Local (Pretrained Neural Net)",
        "image_hash": str(img_hash),
        "verification_token": str(token)
    }

# ─────────────────────────────────────────────────────────────────────────────
# 6. Cryptographic Token Binding (Security & Anti-Tamper)
# ─────────────────────────────────────────────────────────────────────────────

def generate_verification_token(image_bytes, category, status="verified"):
    """
    Generates a cryptographically signed HMAC-SHA256 token binding:
    (image_hash + category_normalized + status + 30-min time window).
    """
    secret = get_secret_key()
    img_hash = hashlib.sha256(image_bytes).hexdigest()
    time_window = int(time.time() // 1800)
    raw = f"{img_hash}:{category.strip().lower()}:{status}:{time_window}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()
    return f"{img_hash}.{sig}"

def validate_verification_token(image_bytes, category, token_str, required_status="verified"):
    """
    Validates that token_str matches the exact image_bytes, category, and status.
    Returns True if valid, False otherwise.
    """
    if not token_str or "." not in token_str:
        return False

    secret = get_secret_key()
    img_hash = hashlib.sha256(image_bytes).hexdigest()
    norm_cat = category.strip().lower()

    parts = token_str.split(".", 1)
    if len(parts) != 2:
        return False
    provided_hash, provided_sig = parts

    if not hmac.compare_digest(img_hash, provided_hash):
        return False  # Image was swapped!

    # Check current 30-minute window
    time_window = int(time.time() // 1800)
    raw_current = f"{img_hash}:{norm_cat}:{required_status}:{time_window}".encode("utf-8")
    expected_sig = hmac.new(secret.encode("utf-8"), raw_current, hashlib.sha256).hexdigest()
    if hmac.compare_digest(expected_sig, provided_sig):
        return True

    # Check previous 30-minute window for smooth edge transitions
    time_window_prev = int((time.time() - 1800) // 1800)
    raw_prev = f"{img_hash}:{norm_cat}:{required_status}:{time_window_prev}".encode("utf-8")
    prev_sig = hmac.new(secret.encode("utf-8"), raw_prev, hashlib.sha256).hexdigest()
    return hmac.compare_digest(prev_sig, provided_sig)

