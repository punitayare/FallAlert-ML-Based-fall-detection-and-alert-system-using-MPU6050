import time
from fastapi import FastAPI, Query
import firebase_admin
from firebase_admin import credentials, messaging, firestore
import joblib
import numpy as np
from collections import deque
import logging
from datetime import datetime

# ------------------- Logging -------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------- FastAPI -------------------
app = FastAPI()

# ------------------- Firebase -------------------
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ------------------- Globals -------------------
last_fall_time = {}
FALL_DISPLAY_TIME = 30

WINDOW_SIZE = 100
NUM_CHANNELS = 8
sensor_windows = {}  # user_id -> deque

# Track active fall per user to avoid duplicate notifications/storage
active_fall = {}  # user_id -> True/False

# Load ML model
try:
    fall_model = joblib.load("fall_detection_model.pkl")
    logger.info("✅ ML model loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load model: {e}")
    fall_model = None

# ------------------- Device → User Mapping -------------------
def get_user_from_device(device_id: str):
    try:
        device_id = device_id.strip()
        logger.info(f"Looking up device: {device_id}")

        doc = db.collection("devices").document(device_id).get()

        if doc.exists:
            data = doc.to_dict()
            logger.info(f"Firestore data: {data}")

            # ✅ Robust field handling
            user_id = data.get("user_id") or data.get("userId")

            if not user_id:
                logger.warning("⚠️ user_id missing in document")

            return user_id

        else:
            logger.warning(f"No mapping found for device {device_id}")
            return None

    except Exception as e:
        logger.error(f"Device mapping error: {e}")
        return None

# ------------------- FCM -------------------
def send_fcm_notification(user_id: str, fcm_token: str, title: str, body: str):
    current_time = time.time()
    last_time = last_fall_time.get(user_id, 0)

    # Prevent spam
    if current_time - last_time < FALL_DISPLAY_TIME:
        logger.info(f"🔕 Notification suppressed for {user_id}")
        return None

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=fcm_token
        )

        response = messaging.send(message)

        logger.info(f"✅ FCM sent to {user_id}: {response}")
        last_fall_time[user_id] = current_time
        return response

    except Exception as e:
        logger.error(f"❌ FCM error: {e}")
        return None

# ------------------- Feature Builder -------------------
def build_feature_vector(window):
    try:
        if len(window) < WINDOW_SIZE:
            padding = np.zeros((WINDOW_SIZE - len(window), NUM_CHANNELS))
            data = np.vstack([np.array(window), padding])
        else:
            data = np.array(window)

        return data.flatten().reshape(1, -1)

    except Exception as e:
        logger.error(f"❌ Feature build error: {e}")
        return None

# ------------------- Get FCM Token -------------------
async def get_user_fcm_token(user_id: str):
    try:
        doc = db.collection("users").document(user_id).get()

        if doc.exists:
            token = doc.to_dict().get("activeFcmToken")

            if token:
                logger.info(f"📲 Using FCM token for {user_id}")
                return token

        logger.warning(f"⚠️ No FCM token for user {user_id}")
        return None

    except Exception as e:
        logger.error(f"❌ Token fetch error: {e}")
        return None

# ------------------- API -------------------
@app.get("/fall_status")
async def fall_status(
    device_id: str = Query(..., description="ESP32 Device ID"),
    ax: float = Query(...), ay: float = Query(...), az: float = Query(...),
    gx: float = Query(...), gy: float = Query(...), gz: float = Query(...),
    trigger_fcm: bool = Query(True)
):
    # -------- Step 1: Map device → user --------
    user_id = get_user_from_device(device_id)

    if not user_id:
        return {"error": "Device not linked", "device_id": device_id}

    # -------- Step 2: Initialize window --------
    if user_id not in sensor_windows:
        sensor_windows[user_id] = deque(maxlen=WINDOW_SIZE)

    window = sensor_windows[user_id]

    # -------- Step 3: Append sensor data --------
    try:
        window.append([ax, ay, az, gx, gy, gz, 0, 0])
    except Exception as e:
        logger.error(f"❌ Invalid sensor data: {e}")
        return {"error": "Invalid sensor values"}

    if len(window) < WINDOW_SIZE:
        return {"fall_detected": False, "message": "Collecting data..."}

    # -------- Step 4: Prediction --------
    if not fall_model:
        return {"fall_detected": False, "error": "Model not loaded"}

    try:
        X = build_feature_vector(window)
        if X is None:
            raise Exception("Feature vector failed")

        prediction = fall_model.predict(X)[0]
        probability = float(max(fall_model.predict_proba(X)[0]))
        fall_detected = bool(prediction)

    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        return {"fall_detected": False, "confidence": 0.0}

    # -------- Step 5: Single Notification & Single Storage --------
    fcm_token = None
    # Check if a fall is already active
    if not active_fall.get(user_id, False) and fall_detected:
        # Mark fall as active
        active_fall[user_id] = True

        # Get FCM token
        if trigger_fcm:
            fcm_token = await get_user_fcm_token(user_id)

        # Save fall event in Firestore
        try:
            doc_ref = db.collection("fall_events").add({
                "deviceId": device_id,
                "userId": user_id,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "accelerometer": {"x": ax, "y": ay, "z": az},
                "gyroscope": {"x": gx, "y": gy, "z": gz},
                "confidence": probability,
                "severity": "high",               # or 'critical'
                "detectionMethod": "ml_api",
                "status": "detected",
                "notified": trigger_fcm,
            })
            logger.info(f"✅ Fall event saved for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Could not save fall event: {e}")

        # Send notification
        if fcm_token:
            send_fcm_notification(
                user_id,
                fcm_token,
                "🚨 Fall Detected!",
                f"Confidence: {probability:.2f}"
            )

    # Reset active fall if no fall detected for 10s
    if not fall_detected and active_fall.get(user_id, False):
        if time.time() - last_fall_time.get(user_id, 0) > 10:
            active_fall[user_id] = False

    # -------- Step 6: Response --------
    return {
        "device_id": device_id,
        "user_id": user_id,
        "fall_detected": fall_detected,
        "confidence": probability,
        "timestamp": datetime.utcnow().isoformat()
    }

# ------------------- Root -------------------
@app.get("/")
async def root():
    return {
        "message": "Fall Detection API running",
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat()
    }
