from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from member1_detector.detector import scan_text
from member2_risk_engine.risk_engine import assess_risk

from backend.database import (
    initialize_database,
    save_audit,
    get_audit_history,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()

    yield


app = FastAPI(
    title="ThreatSentinel API",
    description=(
        "API for prompt-injection detection, risk assessment, "
        "security recommendations, and audit logging."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# Allow the Vite development frontend to access the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ScanRequest(BaseModel):
    user_goal: str = Field(
        min_length=1,
        max_length=2000,
    )

    untrusted_content: str = Field(
        min_length=1,
        max_length=20000,
    )

    proposed_action: str = Field(
        default="none",
        max_length=100,
    )


@app.get("/")
def home():
    return {
        "name": "ThreatSentinel",
        "status": "running",
        "message": "AI security analysis API is ready.",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "ThreatSentinel API",
    }


@app.post("/api/scan")
def scan_request(request: ScanRequest):
    try:
        # Step 1: Detect suspicious instructions.
        findings = scan_text(
            request.untrusted_content
        )

        # Step 2: Assess risk.
        assessment = assess_risk(
            user_goal=request.user_goal,
            untrusted_content=request.untrusted_content,
            proposed_action=request.proposed_action,
            findings=findings,
        )

        # Step 3: Save an audit record.
        record_id = save_audit(
            user_goal=request.user_goal,
            proposed_action=request.proposed_action,
            findings=findings,
            assessment=assessment,
        )

        # Step 4: Return results to React.
        return {
            "id": record_id,
            "findings": findings,
            "assessment": assessment,
        }

    except Exception as exc:
        # Log the error server-side in a production deployment.
        print(f"ThreatSentinel scan error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="The security analysis could not be completed.",
        )


@app.get("/api/history")
def audit_history(
    limit: int = Query(default=100, ge=1, le=500),
):
    try:
        return get_audit_history(limit)

    except Exception as exc:
        print(f"ThreatSentinel history error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="The audit history could not be loaded.",
        )