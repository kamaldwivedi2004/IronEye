import os, uuid
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from db import get_db, db_register_person, db_get_all_persons, db_delete_person, db_load_all_embeddings, db_get_all_alerts, db_get_analytics, db_create_user, db_get_user, db_get_user_by_id
from face_engine import get_embedding, KNOWN_DIR
from camera import start_camera, stop_camera, stream_frames
from alert_system import create_env_template
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24).hex())
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access IronEye."
login_manager.login_message_category = "error"
ALLOWED_EXT = {"png","jpg","jpeg","webp"}
create_env_template()

class User(UserMixin):
    def __init__(self, u):
        self.id = u["id"]; self.username = u["username"]; self.role = u.get("role","admin")

@login_manager.user_loader
def load_user(user_id):
    u = db_get_user_by_id(user_id)
    return User(u) if u else None

def allowed(f): return "." in f and f.rsplit(".",1)[1].lower() in ALLOWED_EXT

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated: return redirect(url_for("dashboard"))
    db = get_db()
    if db.users.count_documents({}) == 0:
        return redirect(url_for("register_account"))
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        user = db_get_user(username)
        if user and bcrypt.check_password_hash(user["password"], password):
            login_user(User(user), remember=True)
            flash(f"Welcome back, {username}!", "success")
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("auth/login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user(); flash("Logged out.", "info"); return redirect(url_for("login"))

@app.route("/register-account", methods=["GET","POST"])
def register_account():
    db = get_db()
    if db.users.count_documents({}) > 0:
        flash("Registration disabled. Contact admin.", "error"); return redirect(url_for("login"))
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        password2 = request.form.get("password2","")
        if not username or not password: flash("Username and password required.", "error")
        elif password != password2: flash("Passwords do not match.", "error")
        elif len(password) < 6: flash("Password must be at least 6 characters.", "error")
        else:
            hashed = bcrypt.generate_password_hash(password).decode("utf-8")
            if db_create_user(username, hashed):
                flash("Account created! Please log in.", "success"); return redirect(url_for("login"))
            else: flash("Username already taken.", "error")
    return render_template("auth/register_account.html")

@app.route("/")
@login_required
def dashboard():
    persons = db_get_all_persons(); alerts = db_get_all_alerts(limit=5)
    return render_template("dashboard.html", persons=persons, alerts=alerts,
                           total_persons=len(persons), total_alerts=len(db_get_all_alerts(1000)))

@app.route("/video_feed")
@login_required
def video_feed():
    return Response(stream_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/camera/start", methods=["POST"])
@login_required
def camera_start():
    start_camera(); flash("Camera started.", "success"); return redirect(url_for("dashboard"))

@app.route("/camera/stop", methods=["POST"])
@login_required
def camera_stop():
    stop_camera(); flash("Camera stopped.", "info"); return redirect(url_for("dashboard"))

@app.route("/register", methods=["GET","POST"])
@login_required
def register():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        file = request.files.get("photo")
        if not name: flash("Name is required.", "error"); return redirect(url_for("register"))
        if not file or not allowed(file.filename): flash("Please upload a valid image.", "error"); return redirect(url_for("register"))
        ext = file.filename.rsplit(".",1)[1].lower()
        filename = secure_filename(f"{name.replace(' ','_')}_{uuid.uuid4().hex[:6]}.{ext}")
        save_path = os.path.join(KNOWN_DIR, filename)
        file.save(save_path)
        emb = get_embedding(save_path)
        if emb is None:
            os.remove(save_path); flash("No face detected. Use a clear front-facing photo.", "error"); return redirect(url_for("register"))
        db_register_person(name, save_path, emb.tolist())
        flash(f"{name} registered successfully.", "success"); return redirect(url_for("database_view"))
    return render_template("register.html")

@app.route("/database")
@login_required
def database_view():
    return render_template("database.html", persons=db_get_all_persons())

@app.route("/database/delete/<person_id>", methods=["POST"])
@login_required
def delete_person_route(person_id):
    if db_delete_person(person_id): flash("Person removed.", "info")
    else: flash("Person not found.", "error")
    return redirect(url_for("database_view"))

@app.route("/alerts")
@login_required
def alerts_view():
    return render_template("alerts.html", alerts=db_get_all_alerts(limit=100))

@app.route("/analytics")
@login_required
def analytics():
    return render_template("analytics.html", data=db_get_analytics())

@app.route("/api/analytics")
@login_required
def api_analytics():
    return jsonify(db_get_analytics())

@app.route("/api/stats")
@login_required
def api_stats():
    return jsonify({"total_persons": len(db_get_all_persons()), "total_alerts": len(db_get_all_alerts(1000))})

@app.route("/alerts/<path:filename>")
@login_required
def serve_alert(filename): return send_from_directory("alerts", filename)

@app.route("/known_faces/<path:filename>")
@login_required
def serve_known_face(filename): return send_from_directory("known_faces", filename)

if __name__ == "__main__":
    print("\n🦾 IronEye — AI Surveillance System")
    print("   Open http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
