
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.outsidein import generate_mission, save_observation

BASE_DIR = Path(__file__).resolve().parent
JOURNAL_FILE = BASE_DIR / "observations.json"

app = FastAPI(
    title="OutsideIn API",
    description="Local-first AI nature quest generator",
    version="1.0.0",
)

# Allow the Vite development server to call the API.
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


class QuestRequest(BaseModel):
    environment: str = Field(min_length=1, max_length=60)
    minutes: int = Field(ge=5, le=20)
    interest: str = Field(min_length=1, max_length=80)


class ObservationRequest(BaseModel):
    mission_title: str = Field(min_length=1, max_length=200)
    observation: str = Field(min_length=1, max_length=2000)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "application": "OutsideIn"}


@app.post("/api/quests")
def create_quest(request: QuestRequest):
    try:
        mission, source = generate_mission(
            request.environment,
            request.minutes,
            request.interest,
        )

        return {
            "mission": mission,
            "source": source,
        }

    except Exception as exc:
        # Log the exception locally for debugging.
        print(f"Quest generation failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate a nature quest.",
        ) from exc


@app.post("/api/observations")
def create_observation(request: ObservationRequest):
    mission = {"title": request.mission_title}

    try:
        save_observation(
            mission,
            request.observation,
            JOURNAL_FILE,
        )
        return {"saved": True}

    except (OSError, ValueError, TypeError) as exc:
        print(f"Observation save failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to save the observation.",
        ) from exc


@app.get("/api/observations")
def get_observations():
    if not JOURNAL_FILE.exists():
        return {"observations": []}

    try:
        records = json.loads(JOURNAL_FILE.read_text(encoding="utf-8"))

        if not isinstance(records, list):
            raise ValueError("Journal must contain a JSON list.")

        return {"observations": records}

    except (json.JSONDecodeError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail="The local journal could not be read.",
        ) from exc
