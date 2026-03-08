import cv2, time, threading, subprocess
from face_engine import process_frame, load_all_embeddings, save_alert
from alert_system import trigger_alert

CAMERA_INDEX = 0
FRAME_SKIP = 3
RELOAD_DB_INTERVAL = 10
_output_frame = None
_frame_lock = threading.Lock()
_is_running = False

def speak(text):
    def _s(): subprocess.Popen(["say","-v","Samantha",text])
    threading.Thread(target=_s, daemon=True).start()

def _recognition_loop():
    global _output_frame, _is_running
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print("[Camera] Could not open webcam."); _is_running = False; return
    print("[Camera] Webcam started.")
    db_embeddings = load_all_embeddings()
    last_db_reload = time.time()
    frame_count = 0
    last_unknown_ts = 0
    last_known_spoken = {}
    while _is_running:
        ret, frame = cap.read()
        if not ret: time.sleep(0.1); continue
        frame_count += 1
        if time.time() - last_db_reload > RELOAD_DB_INTERVAL:
            db_embeddings = load_all_embeddings()
            last_db_reload = time.time()
        if frame_count % FRAME_SKIP == 0:
            annotated, detections = process_frame(frame.copy(), db_embeddings)
            for d in detections:
                if d.get("is_known") and d.get("name"):
                    nm = d["name"]
                    if time.time() - last_known_spoken.get(nm, 0) > 60:
                        speak(f"Welcome, {nm.split('_')[0]}")
                        last_known_spoken[nm] = time.time()
                        try:
                            from db import db_log_known_detection
                            db_log_known_detection(nm)
                        except: pass
            has_unknown = any(not d["is_known"] for d in detections)
            if has_unknown and (time.time() - last_unknown_ts > 30):
                loc_str, maps_url = "", ""
                try:
                    from alert_system import get_location
                    _loc = get_location()
                    if _loc:
                        loc_str = f"{_loc.get('city','')}, {_loc.get('regionName','')}, {_loc.get('country','')}"
                        maps_url = f"https://maps.google.com/?q={_loc['lat']},{_loc['lon']}"
                except: pass
                snapshot = save_alert(annotated, loc_str, maps_url)
                alerted = trigger_alert(snapshot, send_email=True)
                if alerted:
                    speak("Unknown person detected! Alert triggered.")
                    subprocess.Popen(["afplay","/Users/kamaldwivedi/Downloads/fahhhhh.mp3"])
                    last_unknown_ts = time.time()
            cv2.putText(annotated, f"Persons in DB: {len(db_embeddings)}", (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180,180,180), 1)
            with _frame_lock: _output_frame = annotated.copy()
        else:
            with _frame_lock: _output_frame = frame.copy()
    cap.release()
    print("[Camera] Camera released.")

def start_camera():
    global _is_running
    if _is_running: return
    _is_running = True
    threading.Thread(target=_recognition_loop, daemon=True).start()

def stop_camera():
    global _is_running; _is_running = False

def stream_frames():
    global _output_frame
    while True:
        with _frame_lock:
            if _output_frame is None: time.sleep(0.05); continue
            ret, buffer = cv2.imencode(".jpg", _output_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret: continue
            frame_bytes = buffer.tobytes()
        yield (b"--frameContent-Type: image/jpeg" + frame_bytes + b)
        time.sleep(0.04)
