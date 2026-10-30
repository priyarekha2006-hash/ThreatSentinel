# ThreatSentinel

ThreatSentinel is a hackathon prototype designed to identify
suspicious instructions, assess proposed actions, recommend
security decisions, and record an audit trail.

## Technology stack

- React: frontend
- Vite: frontend development server and build tool
- Tailwind CSS: styling
- Lucide React: icons
- Python: detection and risk assessment
- FastAPI: backend API
- SQLite: audit history

## Team responsibilities

Member 1:
- member1_detector/detector.py

Member 2:
- member2_risk_engine/risk_engine.py

Member 3:
- member3_dashboard/src/App.jsx
- member3_dashboard/src/api.js
- member3_dashboard/src/index.css

Shared integration:
- backend/main.py
- backend/database.py

## Python setup

Create a virtual environment:

    python -m venv .venv

Activate it in Windows PowerShell:

    .venv\Scripts\Activate.ps1

Activate it on macOS/Linux:

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

## Start the backend

From the project root:

    python -m uvicorn backend.main:app --reload --port 8000

API documentation:

    http://127.0.0.1:8000/docs

## Start the frontend

Open a second terminal:

    cd member3_dashboard

    npm install

    npm run dev

Open the Vite address displayed in the terminal,
normally http://localhost:5173.

## Run tests

From the project root:

    python -m pytest -q

## Prototype limitations

The detector uses regular expressions and is not a complete
prompt-injection defense. Risk scores are heuristic estimates.

The application does not execute or intercept real agent actions.
A production system would need agent-tool integration,
authorization checks, stronger detection, and additional testing.