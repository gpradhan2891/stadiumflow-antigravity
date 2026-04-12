# StadiumFlow AI Assistant

> Real-time AI-powered crowd management for large stadiums — built with Google Cloud.

## What It Does
StadiumFlow dynamically routes fans to optimal gates and concession zones, reducing wait times and improving safety during high-attendance events.

## Architecture
- **Backend:** FastAPI + Python
- **Database:** Google Cloud Firestore (real-time crowd data)
- **Messaging:** Google Cloud Pub/Sub (live event streaming)
- **Frontend:** Fan-facing web app + Ops dashboard (HTML/CSS/JS)

## Features
- 🏟️ Real-time zone occupancy monitoring
- 🔀 AI-driven crowd routing recommendations
- 📊 Live operations dashboard for stadium staff
- 🎟️ Fan-facing gate and concession guidance

## Setup

### Prerequisites
- Python 3.10+
- Google Cloud project with Firestore + Pub/Sub enabled
- Service account with appropriate IAM roles

### Installation
```bash
git clone https://github.com/gpradhan2891/stadiumflow-antigravity
cd stadiumflow-antigravity/backend
pip install -r requirements.txt
cp .env.example .env   # Fill in your GCP credentials
uvicorn main:app --reload
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/zones` | Get all zone occupancy data |
| GET | `/queues` | Get current queue lengths |
| GET | `/routing` | Get AI routing recommendations |

## License
MIT
