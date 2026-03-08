# Smart Face Recognition System 🎯

A production-grade real-time face recognition system built with **DeepFace (FaceNet-512)**, **OpenCV**, and **Flask**.

---

## 🚀 Features

| Feature | Details |
|---|---|
| **Face Registration** | Upload a photo via web UI → auto-extracts 512-dim embedding |
| **Live Recognition** | Webcam feed identifies known persons in real time |
| **Unknown Alerts** | Snapshots saved + email sent when unknown face detected |
| **Web Dashboard** | Flask UI to manage database, view feed, see alert history |
| **No raw image matching** | Uses cosine similarity on embeddings — fast & accurate |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **DeepFace** — FaceNet-512 model for face embeddings
- **OpenCV** — webcam capture & frame annotation
- **scikit-learn** — cosine similarity matching
- **Flask** — web dashboard + MJPEG stream
- **SQLite** — stores embeddings & alert logs
- **smtplib** — email alerts

---

## ⚡ Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/yourname/smart-face-recognition
cd smart-face-recognition
pip install -r requirements.txt
```

### 2. Configure Email Alerts (optional)
Edit the `.env` file:
```
ALERT_EMAIL_FROM=your_email@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password   # Gmail App Password
ALERT_EMAIL_TO=receiver@gmail.com
```
> Generate a Gmail App Password at: https://myaccount.google.com/apppasswords

### 3. Run the App
```bash
python app.py
```
Open **http://localhost:5000** in your browser.

---

## 📖 How to Use

1. **Register persons** → Go to "Register Person" → upload photo + enter name
2. **Start the camera** → Click "▶ Start Camera" on the dashboard
3. **Live recognition** → Known faces show name + confidence %; unknowns trigger alerts
4. **View alerts** → Go to "Alerts" tab to see all unknown-face snapshots

---

## 🧠 How It Works

```
Photo Upload
    │
    ▼
DeepFace.represent()          ← FaceNet-512 model
    │  512-dim embedding
    ▼
SQLite DB (embeddings table)

Camera Frame
    │
    ▼
DeepFace.extract_faces()      ← detect face regions
    │  face crops
    ▼
DeepFace.represent()          ← embed each face
    │
    ▼
cosine_similarity(query, known_matrix)
    │
    ├─ score ≥ 0.68  →  "Rahul  94.2%"  (green box)
    └─ score <  0.68  →  "⚠️ UNKNOWN"  (red box) → alert
```

---

## 📁 Project Structure

```
smart-face-recognition/
├── app.py              # Flask web server
├── face_engine.py      # Core ML: embeddings, matching, DB
├── camera.py           # Webcam loop + MJPEG streaming
├── alert_system.py     # Email alerts with cooldown
├── requirements.txt
├── .env                # Email credentials (git-ignored)
├── database/           # SQLite DB + temp files
├── known_faces/        # Uploaded reference photos
├── alerts/             # Unknown-face snapshots
└── templates/          # Flask HTML templates
```

---

## 🎯 Resume Talking Points

- **"Used FaceNet-512 embeddings + cosine similarity for O(n) real-time matching"**
- **"Built an MJPEG streaming pipeline in Flask for live browser-based monitoring"**
- **"Designed a cooldown-protected alert system with email notifications"**
- **"Stored face embeddings (not raw images) for privacy-conscious design"**

---

## 📈 Possible Extensions

- [ ] Multi-camera support
- [ ] Face liveness detection (anti-spoofing)
- [ ] Attendance tracking with CSV export
- [ ] Telegram bot alerts
- [ ] Docker deployment
# IronEye
