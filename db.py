import os, certifi
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "")
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is not None:
        return _db
    _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000, tls=True, tlsCAFile=certifi.where())
    _db = _client["ironeye"]
    print("[DB] Connected to MongoDB Atlas")
    return _db

def db_register_person(name, image_path, embedding):
    db = get_db()
    doc = {"name": name, "image": image_path, "embedding": embedding, "added_at": datetime.now().isoformat()}
    result = db.persons.insert_one(doc)
    return {"success": True, "id": str(result.inserted_id)}

def db_get_all_persons():
    db = get_db()
    rows = db.persons.find({}, {"embedding": 0}).sort("added_at", DESCENDING)
    return [{"id": str(r["_id"]), "name": r["name"], "image": r["image"], "added_at": r["added_at"]} for r in rows]

def db_load_all_embeddings():
    import numpy as np
    db = get_db()
    rows = db.persons.find({}, {"name": 1, "embedding": 1})
    return [{"id": str(r["_id"]), "name": r["name"], "embedding": np.array(r["embedding"], dtype=np.float32)} for r in rows]

def db_delete_person(person_id):
    db = get_db()
    try:
        r = db.persons.find_one({"_id": ObjectId(person_id)})
        if r:
            try: os.remove(r["image"])
            except: pass
            db.persons.delete_one({"_id": ObjectId(person_id)})
            return True
    except: pass
    return False

def db_save_alert(snapshot, location="", maps_url=""):
    db = get_db()
    doc = {"snapshot": snapshot, "detected_at": datetime.now().isoformat(), "email_sent": False,
           "location": location, "maps_url": maps_url, "hour": datetime.now().hour, "date": datetime.now().strftime("%Y-%m-%d")}
    db.alerts.insert_one(doc)
    return snapshot

def db_get_all_alerts(limit=50):
    db = get_db()
    rows = db.alerts.find({}).sort("detected_at", DESCENDING).limit(limit)
    return [{"id": str(r["_id"]), "snapshot": r["snapshot"], "detected_at": r["detected_at"],
             "email_sent": r.get("email_sent", False), "location": r.get("location",""), "maps_url": r.get("maps_url","")} for r in rows]

def db_mark_alert_sent(snapshot):
    db = get_db()
    db.alerts.update_one({"snapshot": snapshot}, {"$set": {"email_sent": True}})

def db_get_analytics():
    from datetime import timedelta
    db = get_db()
    total_persons = db.persons.count_documents({})
    total_alerts  = db.alerts.count_documents({})
    days_data = []
    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        count = db.alerts.count_documents({"date": day})
        days_data.append({"date": day, "count": count})
    hourly = [{"hour": h, "count": db.alerts.count_documents({"hour": h})} for h in range(24)]
    pipeline = [{"$group": {"_id": "$person_name", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 5}]
    top_raw = list(db.known_detections.aggregate(pipeline))
    top_persons = [{"name": r["_id"], "count": r["count"]} for r in top_raw]
    known_count = db.known_detections.count_documents({})
    return {"total_persons": total_persons, "total_alerts": total_alerts, "days_data": days_data,
            "hourly": hourly, "top_persons": top_persons, "unknown_count": total_alerts, "known_count": known_count}

def db_log_known_detection(person_name):
    db = get_db()
    db.known_detections.insert_one({"person_name": person_name, "detected_at": datetime.now().isoformat(),
                                     "hour": datetime.now().hour, "date": datetime.now().strftime("%Y-%m-%d")})

def db_create_user(username, password_hash):
    db = get_db()
    if db.users.find_one({"username": username}):
        return False
    db.users.insert_one({"username": username, "password": password_hash, "created_at": datetime.now().isoformat(), "role": "admin"})
    return True

def db_get_user(username):
    db = get_db()
    r = db.users.find_one({"username": username})
    if r:
        return {"id": str(r["_id"]), "username": r["username"], "password": r["password"], "role": r.get("role","admin")}
    return None

def db_get_user_by_id(user_id):
    db = get_db()
    try:
        r = db.users.find_one({"_id": ObjectId(user_id)})
        if r:
            return {"id": str(r["_id"]), "username": r["username"], "password": r["password"], "role": r.get("role","admin")}
    except: pass
    return None
