IronEye 👁️‍🗨️
Real-Time Face Recognition & Security Monitoring System

IronEye is a real-time intelligent face recognition system designed for automated identity detection and security monitoring. It uses DeepFace (FaceNet-512) for generating facial embeddings and OpenCV for live video processing, combined with a Flask web dashboard for managing users and monitoring alerts.

🚀 Features
Feature	Description
Face Registration	Upload a person's photo and store their facial embedding in the database
Real-Time Recognition	Detect and identify faces instantly through webcam feed
Unknown Face Alerts	Captures snapshot and logs unknown faces automatically
Web Dashboard	Manage faces, monitor alerts, and control camera via Flask UI
Embedding-Based Recognition	Uses cosine similarity instead of raw image comparison
🛠️ Tech Stack

Python 3.10+

DeepFace — FaceNet-512 model for facial embeddings

OpenCV — Webcam capture and face detection

Flask — Web dashboard and backend API

scikit-learn — Cosine similarity matching

SQLite — Database for storing embeddings and alerts

NumPy & Pandas — Data processing

⚡ Quick Start
1️⃣ Clone the Repository
git clone https://github.com/yourusername/iron-eye.git
cd iron-eye
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Run the Application
python app.py

Open your browser and go to:

http://localhost:5000
📖 How to Use
1️⃣ Register a Person

Open Register Person in the dashboard

Upload an image and enter the person's name

System generates and stores the face embedding

2️⃣ Start Camera

Click Start Camera to activate real-time recognition.

3️⃣ Live Detection

Known faces → Display Name + Confidence Score

Unknown faces → Marked as UNKNOWN and logged

4️⃣ View Alerts

Go to the Alerts Page to view captured unknown faces.

🧠 System Workflow
Image Upload
      │
      ▼
DeepFace.represent()
      │
      ▼
512-Dimension Face Embedding
      │
      ▼
Store in SQLite Database
Webcam Frame
      │
      ▼
Face Detection (OpenCV)
      │
      ▼
DeepFace.represent()
      │
      ▼
Cosine Similarity Matching
      │
      ├── Score ≥ Threshold → Known Person
      └── Score < Threshold → Unknown Face Alert
📁 Project Structure
iron-eye/
│
├── app.py                # Main Flask application
├── face_engine.py        # Face embedding & recognition logic
├── camera.py             # Webcam capture and streaming
├── alert_system.py       # Unknown face alert management
│
├── database/             # SQLite database
├── known_faces/          # Stored reference images
├── alerts/               # Unknown face snapshots
│
├── templates/            # HTML templates for Flask UI
├── static/               # CSS / JS / assets
│
├── requirements.txt
├── README.md
└── .env                  # Environment variables
🎯 Resume Talking Points

Implemented FaceNet-512 embeddings for high-accuracy face recognition

Built real-time webcam processing pipeline using OpenCV

Developed a Flask-based monitoring dashboard with MJPEG video streaming

Implemented cosine similarity matching for efficient identity detection

Designed a secure system storing embeddings instead of raw facial images

📈 Future Improvements

Multi-camera monitoring support

Face liveness detection (anti-spoofing)

Mobile notification alerts

Cloud database integration

Docker container deployment

📄 License

This project is developed for educational and research purposes.
