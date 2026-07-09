# Face Attendance System

A Face Recognition Attendance System built with **FastAPI**, **InsightFace**, **OpenCV**, and **SQLite**. The system allows users to register facial embeddings and perform real-time attendance using face recognition.

---

## Features

- Face registration
  - Register a new user with facial embedding.
  - Prevent duplicate face registration using cosine similarity.

- Face recognition
  - Extract facial embeddings from live images.
  - Compare embeddings with registered users.
  - Identify the most similar user using cosine similarity.

- Attendance management
  - Check in using face recognition.
  - Store attendance history in SQLite.

- RESTful API
  - User management.
  - Attendance management.
  - Face recognition endpoints.

---

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

### Computer Vision

- InsightFace
- OpenCV
- NumPy

---

## Project Structure

```
face-attendance/
│
├── app/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── static/
│   ├── utils/
│   └── vision/
│       ├── camera.py
│       ├── embedding.py
│       ├── face_capture.py
│       ├── face_detector.py
│       ├── face_recognizer.py
│       ├── face_similarity.py
│       └── storage.py
│
├── embeddings/
├── uploads/
├── main.py
├── requirements.txt
└── README.md
```

---

## Recognition Workflow

```
Camera
    │
    ▼
Face Detection
    │
    ▼
Embedding Extraction
    │
    ▼
Load Registered Embeddings
    │
    ▼
Cosine Similarity
    │
    ▼
Recognized User
    │
    ▼
Attendance Check-in
```

---

## Installation

### Clone repository

```bash
git clone https://github.com/your-username/face-attendance.git

cd face-attendance
```

### Create virtual environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run Project

```bash
uvicorn main:app --reload
```

API Documentation

```
http://127.0.0.1:8000/docs
```

---

## Face Registration

1. Detect face.
2. Extract embedding.
3. Compare with existing embeddings.
4. Reject duplicate faces.
5. Save embedding.
6. Save user information.

---

## Face Recognition

1. Capture image.
2. Detect face.
3. Extract embedding.
4. Compare with registered embeddings.
5. Return user ID with highest similarity.
6. Record attendance.

---

## Similarity Algorithm

The system uses **Cosine Similarity** to compare facial embeddings.

```
Similarity = cosine(current_embedding, saved_embedding)
```

If the similarity score is greater than the predefined threshold, the face is considered a match.

---

## API Endpoints

### User

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/users` | Register a user |
| GET | `/users` | Get all users |

### Attendance

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/attendance/check-in` | Face attendance |
| GET | `/attendance` | Attendance history |

---

## Database

### User

- id
- name
- embedding_path

### Attendance

- id
- user_id
- check_in_time

---

## Future Improvements

- Real-time webcam recognition
- Multi-face recognition
- Face anti-spoofing
- JWT Authentication
- PostgreSQL support
- Docker deployment
- Frontend dashboard
- Attendance analytics
- User photos management

---

## Author

Nguyen Duc Hung