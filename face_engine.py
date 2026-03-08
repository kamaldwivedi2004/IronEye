import os, numpy as np
from datetime import datetime
import face_recognition, cv2

KNOWN_DIR = "known_faces"
ALERTS_DIR = "alerts"
THRESHOLD = 0.6
UNKNOWN_LABEL = "UNKNOWN"
os.makedirs(KNOWN_DIR, exist_ok=True)
os.makedirs(ALERTS_DIR, exist_ok=True)

def get_embedding(image_path):
    try:
        img = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(img)
        if not encodings: return None
        return np.array(encodings[0], dtype=np.float32)
    except: return None

def load_all_embeddings():
    from db import db_load_all_embeddings
    return db_load_all_embeddings()

def identify_embedding(query_emb, db_embeddings):
    if query_emb is None or not db_embeddings:
        return {"name": UNKNOWN_LABEL, "confidence": 0.0, "is_known": False}
    known = [e["embedding"] for e in db_embeddings]
    distances = face_recognition.face_distance(known, query_emb)
    best_idx = int(np.argmin(distances))
    best_dist = float(distances[best_idx])
    confidence = round((1 - best_dist) * 100, 1)
    if best_dist <= THRESHOLD:
        return {"name": db_embeddings[best_idx]["name"], "confidence": confidence, "is_known": True}
    return {"name": UNKNOWN_LABEL, "confidence": confidence, "is_known": False}

def process_frame(frame_bgr, db_embeddings):
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (0,0), fx=0.5, fy=0.5)
    locations = face_recognition.face_locations(small, model="hog")
    encodings = face_recognition.face_encodings(small, locations)
    detections = []
    for (top, right, bottom, left), enc in zip(locations, encodings):
        top, right, bottom, left = top*2, right*2, bottom*2, left*2
        result = identify_embedding(np.array(enc, dtype=np.float32), db_embeddings)
        color = (0,200,80) if result["is_known"] else (0,50,220)
        label = f"{result['name']}  {result['confidence']}%"
        cv2.rectangle(frame_bgr, (left,top), (right,bottom), color, 2)
        (tw,th),_ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(frame_bgr, (left,top-th-12), (left+tw+8,top), color, -1)
        cv2.putText(frame_bgr, label, (left+4,top-6), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1)
        detections.append({**result, "bbox": (left,top,right-left,bottom-top)})
    return frame_bgr, detections

def save_alert(frame, location="", maps_url=""):
    from db import db_save_alert
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"alerts/unknown_{ts}.jpg"
    cv2.imwrite(filename, frame)
    db_save_alert(filename, location, maps_url)
    print(f"[FaceEngine] Alert saved: {filename}")
    return filename

def get_all_alerts(limit=50):
    from db import db_get_all_alerts
    return db_get_all_alerts(limit)

def register_person(name, image_path):
    from db import db_register_person
    emb = get_embedding(image_path)
    if emb is None:
        return {"success": False, "message": "No face detected."}
    db_register_person(name, image_path, emb.tolist())
    return {"success": True, "message": f"{name} registered."}

def delete_person(person_id):
    from db import db_delete_person
    return db_delete_person(str(person_id))

def get_all_persons():
    from db import db_get_all_persons
    return db_get_all_persons()
