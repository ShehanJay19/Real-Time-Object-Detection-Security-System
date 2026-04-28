# 🛡️ Real-Time Object Detection Security System

An AI-powered surveillance system that detects intruders, weapons, and suspicious activities in real time using computer vision and deep learning. The system processes live video streams and triggers instant alerts via email/SMS.

---

## 🚀 Features

- 📡 Real-time video stream processing (Webcam / CCTV / RTSP)
- 🧠 AI-based object detection (person, weapon detection)
- 🚨 Instant alerts (Email / SMS)
- 📊 Detection logs and monitoring dashboard
- 🎯 Custom rule-based alert system
- ⚡ Optimized for real-time performance

---

## 🧠 Tech Stack

### 🔹 AI / Computer Vision
- YOLOv8 (Object Detection)
- OpenCV (Video Processing)

### 🔹 Backend
- FastAPI (Python)
- REST APIs

### 🔹 Frontend
- React.js (Dashboard UI)

### 🔹 Alerts & Notifications
- SMTP (Email Alerts)
- Twilio (SMS Alerts)

### 🔹 DevOps
- Docker (Containerization)
- GitHub Actions (CI/CD)

---

## 🏗️ System Architecture
Camera / CCTV
↓
OpenCV (Frame Capture)
↓
YOLOv8 (Detection Engine)
↓
Detection Processor
↓ ↓
Alerts Database
↓ ↓
Email/SMS Logs
↓
Frontend Dashboard (React)



---

## 🔌 API Endpoints

### Detection
- POST /detect/frame → Detect objects in a frame
- POST /detect/video → Process video stream

### Alerts
- POST /alerts/trigger → Trigger alert
- GET /alerts → Get alert history

### Logs
- GET /logs → Retrieve detection logs
- GET /logs/{id} → Get specific log

### System
- GET /health → Check system status

---

## ⚙️ Installation

### 1. Clone the repository
git clone https://github.com/ShehanJay19/Real-Time-Object-Detection-Security-System.git

cd security-system


### 2. Backend Setup
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload


### 3. Frontend Setup
cd frontend
npm install
npm start


---

## ▶️ Usage

1. Start backend server  
2. Start frontend  
3. Connect camera or video stream  
4. Monitor detections in real time  
5. Receive alerts when threats are detected  

---

## 🧠 Model Details

- Model: YOLOv8 (Ultralytics)
- Classes: Person, Knife, Gun
- Optimizations:
  - Frame skipping
  - Confidence threshold tuning
  - Lightweight model (YOLOv8n)

---

## ⚠️ Challenges & Solutions

- Real-time lag → Frame skipping + lightweight model  
- False positives → Threshold tuning + filtering  
- Alert spam → Cooldown mechanism  
- Camera disconnect → Auto-reconnect logic  
- Scalability → Queue-based architecture  

---

## 📊 Future Improvements

- Face recognition (known vs unknown)
- Mobile app for alerts
- Cloud storage integration
- Behavior analysis using deep learning
- Geo-fencing alerts

---

## 📸 Demo

(Add screenshots or demo video here)

---

## 🧾 License

This project is licensed under the MIT License.

---

## 🙌 Acknowledgements

- Ultralytics YOLOv8
- OpenCV community
