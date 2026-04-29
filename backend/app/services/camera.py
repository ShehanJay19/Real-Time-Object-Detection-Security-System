from app.services.detector import detect_objects
from app.services.alerts import DANGEROUS_LABELS, should_trigger_alert, trigger_alert
from app.services.database import save_log
import cv2
import threading
import time

CAMERA_STATE_LOCK = threading.Lock()
CAMERA_RUNNING = False
LAST_CAMERA_ERROR = ""
SELECTED_CAMERA_INDEX = 0
LATEST_FRAME_JPEG = None
CACHED_CAMERAS = []
CAMERA_CACHE_TIME = 0
CAMERA_CACHE_DURATION = 5  # Cache for 5 seconds


def is_camera_running():
    with CAMERA_STATE_LOCK:
        return CAMERA_RUNNING


def get_camera_status():
    with CAMERA_STATE_LOCK:
        return {
            "running": CAMERA_RUNNING,
            "last_error": LAST_CAMERA_ERROR,
            "selected_camera_index": SELECTED_CAMERA_INDEX,
        }


def list_available_cameras(max_index=16, force_rescan=False):
    global CACHED_CAMERAS, CAMERA_CACHE_TIME
    
    current_time = time.time()
    
    # Return cached list if available and not forcing rescan
    if not force_rescan and CACHED_CAMERAS and (current_time - CAMERA_CACHE_TIME) < CAMERA_CACHE_DURATION:
        print(f"📦 Using cached camera list ({len(CACHED_CAMERAS)} cameras)")
        return CACHED_CAMERAS
    
    cameras = []
    print(f"🔍 Scanning for cameras (indices 0-{max_index-1})...")
    
    for index in range(max_index):
        try:
            # Try with CAP_DSHOW first (Windows)
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if not cap.isOpened():
                # Fallback to default backend
                cap = cv2.VideoCapture(index)
            
            if not cap.isOpened():
                cap.release()
                continue

            # Set a timeout by reading with a limit
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                cameras.append({
                    "index": index,
                    "name": f"Camera {index}",
                })
                print(f"  ✅ Index {index}: Available")

        except Exception as e:
            try:
                cap.release()
            except:
                pass
            print(f"  ⚠️ Index {index}: {type(e).__name__}")
            continue

    print(f"Found {len(cameras)} camera(s)")
    
    # Update cache
    CACHED_CAMERAS = cameras
    CAMERA_CACHE_TIME = current_time
    
    return cameras


def get_camera_options():
    with CAMERA_STATE_LOCK:
        selected_index = SELECTED_CAMERA_INDEX

    # Return cached list immediately - don't trigger background scans
    return {
        "selected_camera_index": selected_index,
        "cameras": CACHED_CAMERAS,
    }


def set_selected_camera(index):
    global SELECTED_CAMERA_INDEX

    if is_camera_running():
        return {
            "ok": False,
            "message": "Cannot switch camera while stream is running",
            "selected_camera_index": SELECTED_CAMERA_INDEX,
        }

    available = list_available_cameras()
    available_indexes = {camera["index"] for camera in available}

    if index not in available_indexes:
        return {
            "ok": False,
            "message": f"Camera index {index} is not available",
            "selected_camera_index": SELECTED_CAMERA_INDEX,
            "cameras": available,
        }

    with CAMERA_STATE_LOCK:
        SELECTED_CAMERA_INDEX = index

    return {
        "ok": True,
        "message": f"Camera switched to {index}",
        "selected_camera_index": index,
        "cameras": available,
    }


def generate_mjpeg_stream():
    while True:
        with CAMERA_STATE_LOCK:
            frame = LATEST_FRAME_JPEG

        if frame is not None:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )

        time.sleep(0.05)


def start_camera():
    global CAMERA_RUNNING
    global LAST_CAMERA_ERROR
    global LATEST_FRAME_JPEG

    with CAMERA_STATE_LOCK:
        if CAMERA_RUNNING:
            return
        CAMERA_RUNNING = True
        LAST_CAMERA_ERROR = ""
        selected_index = SELECTED_CAMERA_INDEX

    cap = cv2.VideoCapture(selected_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        with CAMERA_STATE_LOCK:
            LAST_CAMERA_ERROR = f"Unable to open camera {selected_index}. Check GlideX camera connection."
            CAMERA_RUNNING = False
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                with CAMERA_STATE_LOCK:
                    LAST_CAMERA_ERROR = "Failed to read frame from selected camera"
                break

            results, detected_objects = detect_objects(frame)
            labels = [obj[0] for obj in detected_objects]
            
            # Log detected objects for debugging
            if detected_objects:
                obj_summary = ", ".join([f"{label}({conf:.0%})" for label, conf in detected_objects[:5]])
                print(f"🎯 Detected: {obj_summary}")
            
            if should_trigger_alert(labels):
                print(f"⚠️ DANGEROUS OBJECT ALERT! Labels: {labels}")
                trigger_alert(detected_objects)
            else:
                # Check if knife/gun was close but not triggered (cooldown)
                dangerous = [l for l in labels if l.lower() in DANGEROUS_LABELS]
                if dangerous:
                    print(f"⏳ Dangerous object detected but on cooldown: {dangerous}")

            for obj, conf in detected_objects:
                save_log(obj, conf)

            annotated_frame = results[0].plot()
            ok, jpeg = cv2.imencode(".jpg", annotated_frame)
            if ok:
                with CAMERA_STATE_LOCK:
                    LATEST_FRAME_JPEG = jpeg.tobytes()
    except Exception as exc:
        with CAMERA_STATE_LOCK:
            LAST_CAMERA_ERROR = str(exc)
    finally:
        cap.release()
        with CAMERA_STATE_LOCK:
            CAMERA_RUNNING = False