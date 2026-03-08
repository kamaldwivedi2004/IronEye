import os, smtplib, time, urllib.request, json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

SENDER_EMAIL    = os.getenv("ALERT_EMAIL_FROM","")
SENDER_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD","")
RECEIVER_EMAIL  = os.getenv("ALERT_EMAIL_TO","")
SMTP_HOST       = os.getenv("SMTP_HOST","smtp.gmail.com")
SMTP_PORT       = int(os.getenv("SMTP_PORT","587"))
ALERT_COOLDOWN  = 30
_last_alert_time = 0.0

def get_location():
    try:
        with urllib.request.urlopen("http://ip-api.com/json/?fields=city,regionName,country,lat,lon,status", timeout=5) as r:
            data = json.loads(r.read().decode())
        if data.get("status") == "success": return data
    except: pass
    return {}

def send_email_alert(snapshot_path):
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]): return False
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL; msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = "IronEye Alert — Unknown Person Detected"
        ts = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")
        _loc = get_location()
        loc_str = f"{_loc.get('city','')}, {_loc.get('regionName','')}, {_loc.get('country','')}" if _loc else "Location unavailable"
        maps_url = f"https://maps.google.com/?q={_loc['lat']},{_loc['lon']}" if _loc else "#"
        body = f"""<html><body style="font-family:Arial;background:#0d0d0d;padding:20px">
          <div style="background:#1a1a2e;border-radius:12px;padding:28px;max-width:520px;margin:auto;border:1px solid #00d084">
            <h1 style="color:#00d084">IronEye Alert</h1>
            <h2 style="color:#e74c3c">Unknown Person Detected</h2>
            <table style="width:100%;border-collapse:collapse;margin:16px 0">
              <tr><td style="padding:10px;color:#888">Time</td><td style="padding:10px;color:#fff"><b>{ts}</b></td></tr>
              <tr><td style="padding:10px;color:#888">Status</td><td style="padding:10px"><b style="color:#e74c3c">NOT in database</b></td></tr>
              <tr><td style="padding:10px;color:#888">Location</td><td style="padding:10px;color:#fff"><b>{loc_str}</b></td></tr>
              <tr><td style="padding:10px;color:#888">Maps</td><td style="padding:10px"><a href="{maps_url}" style="color:#00d084">Open in Google Maps</a></td></tr>
            </table>
          </div></body></html>"""
        msg.attach(MIMEText(body, "html"))
        if os.path.exists(snapshot_path):
            with open(snapshot_path, "rb") as f:
                msg.attach(MIMEImage(f.read(), name=os.path.basename(snapshot_path)))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo(); s.starttls(); s.login(SENDER_EMAIL, SENDER_PASSWORD)
            s.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        try:
            from db import db_mark_alert_sent
            db_mark_alert_sent(snapshot_path)
        except: pass
        print(f"[AlertSystem] Email sent to {RECEIVER_EMAIL}")
        return True
    except Exception as e:
        print(f"[AlertSystem] Email failed: {e}"); return False

def trigger_alert(snapshot_path, send_email=True):
    global _last_alert_time
    now = time.time()
    if now - _last_alert_time < ALERT_COOLDOWN: return False
    _last_alert_time = now
    print("[AlertSystem] Unknown face alert triggered!")
    if send_email: send_email_alert(snapshot_path)
    return True

def create_env_template():
    pass
