
import json
from datetime import datetime
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:1b"

FALLBACK_MISSIONS = [
    {
        "title": "The Leaf Detective",
        "duration_minutes": 10,
        "mission": "Compare three different leaf shapes without picking them.",
        "steps": [
            "Choose a safe outdoor spot.",
            "Observe the shapes, edges, and visible veins.",
            "Write down one difference you noticed.",
        ],
        "reflection_question": "Which detail surprised you?",
        "safety_note": "Stay on public paths and avoid touching unknown plants.",
    },
    {
        "title": "Tiny Signs of Life",
        "duration_minutes": 10,
        "mission": "Look for three signs of life in your surroundings.",
        "steps": [
            "Pause somewhere safe and observe quietly.",
            "Look for plants, birds, or insects from a distance.",
            "Record three things you noticed.",
        ],
        "reflection_question": "What did you notice after slowing down?",
        "safety_note": "Do not disturb wildlife or approach unfamiliar animals.",
    },
    {
        "title": "Listen to the Outdoors",
        "duration_minutes": 5,
        "mission": "Discover three different sounds outdoors.",
        "steps": [
            "Choose a safe spot away from traffic.",
            "Listen quietly for one minute.",
            "Record three different sounds.",
        ],
        "reflection_question": "Which sound would you normally overlook?",
        "safety_note": "Remain aware of traffic and your surroundings.",
    },
]

REQUIRED_FIELDS = {
    "title",
    "duration_minutes",
    "mission",
    "steps",
    "reflection_question",
    "safety_note",
}


def validate_mission(mission, max_minutes):
    """Reject incomplete or incorrectly structured model output."""
    if not isinstance(mission, dict):
        raise ValueError("Mission must be a JSON object.")

    if not REQUIRED_FIELDS.issubset(mission):
        raise ValueError("Mission is missing required fields.")

    duration = mission["duration_minutes"]
    if (
        isinstance(duration, bool)
        or not isinstance(duration, int)
        or not 1 <= duration <= max_minutes
    ):
        raise ValueError("Invalid mission duration.")

    for field in REQUIRED_FIELDS - {"duration_minutes", "steps"}:
        if not isinstance(mission[field], str) or not mission[field].strip():
            raise ValueError(f"Invalid field: {field}")

    steps = mission["steps"]
    if (
        not isinstance(steps, list)
        or not 2 <= len(steps) <= 4
        or not all(isinstance(step, str) and step.strip() for step in steps)
    ):
        raise ValueError("Invalid mission steps.")

    return mission


def generate_mission(environment, minutes, interest):
    """Generate a local AI quest or use a curated fallback."""
    prompt = f"""
Create one safe, beginner-friendly outdoor nature quest.
Environment: {environment}
Available time: {minutes} minutes
Interest: {interest}

Return only a JSON object with these fields:
title, duration_minutes, mission, steps,
reflection_question, safety_note.

Use an integer duration between 1 and {minutes}.
Include 2 to 4 short steps.
Do not ask users to touch unknown plants, disturb wildlife,
enter private property, or use special equipment.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.7},
            },
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        mission = json.loads(payload["response"])
        validate_mission(mission, minutes)
        return mission, "Local Gemma AI"

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
    ):
        index = (minutes + len(interest) + len(environment)) % len(
            FALLBACK_MISSIONS
        )
        fallback = FALLBACK_MISSIONS[index].copy()
        fallback["steps"] = fallback["steps"].copy()
        fallback["duration_minutes"] = min(
            fallback["duration_minutes"], minutes
        )
        return fallback, "Curated offline fallback"


def save_observation(mission, note, journal_file):
    """Append an observation to a local JSON journal."""
    if not isinstance(note, str) or not note.strip():
        raise ValueError("Observation cannot be empty.")

    journal_file = Path(journal_file)
    records = []

    if journal_file.exists():
        try:
            records = json.loads(journal_file.read_text(encoding="utf-8"))
            if not isinstance(records, list):
                records = []
        except (json.JSONDecodeError, OSError):
            records = []

    records.append(
        {
            "completed_at": datetime.now().astimezone().isoformat(),
            "mission_title": mission["title"],
            "observation": note.strip(),
        }
    )

    journal_file.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
