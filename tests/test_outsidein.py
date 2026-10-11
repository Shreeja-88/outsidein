
import json

import pytest
import requests

from src import outsidein


def valid_mission():
    return {
        "title": "Leaf Detective",
        "duration_minutes": 5,
        "mission": "Compare three leaf shapes.",
        "steps": ["Find a safe spot.", "Observe without picking."],
        "reflection_question": "What surprised you?",
        "safety_note": "Avoid touching unknown plants.",
    }


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return {"response": json.dumps(self.payload)}


def test_generate_mission_with_local_model(monkeypatch):
    expected = valid_mission()

    def fake_post(*args, **kwargs):
        assert kwargs["json"]["model"] == outsidein.MODEL_NAME
        assert kwargs["timeout"] == 90
        return FakeResponse(expected)

    monkeypatch.setattr(outsidein.requests, "post", fake_post)

    mission, source = outsidein.generate_mission("Garden", 5, "Plants")

    assert mission == expected
    assert source == "Local Gemma AI"


def test_fallback_when_ollama_is_unavailable(monkeypatch):
    def fake_post(*args, **kwargs):
        raise requests.ConnectionError("Ollama is not running")

    monkeypatch.setattr(outsidein.requests, "post", fake_post)

    mission, source = outsidein.generate_mission("Garden", 5, "Plants")

    assert source == "Curated offline fallback"
    assert mission["title"]
    assert 1 <= mission["duration_minutes"] <= 5


def test_fallback_when_model_returns_invalid_json(monkeypatch):
    class BadResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": "not valid JSON"}

    monkeypatch.setattr(
        outsidein.requests, "post", lambda *args, **kwargs: BadResponse()
    )

    mission, source = outsidein.generate_mission("Park", 10, "Sounds")

    assert source == "Curated offline fallback"
    assert mission["steps"]


def test_fallback_when_model_returns_non_object_json(monkeypatch):
    class BadResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": '["this", "is", "not", "a", "mission"]'}

    monkeypatch.setattr(
        outsidein.requests, "post", lambda *args, **kwargs: BadResponse()
    )

    mission, source = outsidein.generate_mission("Forest", 15, "Wildlife")

    assert source == "Curated offline fallback"
    assert isinstance(mission, dict)
    assert mission["title"]


def test_fallback_when_model_response_is_missing_required_fields(monkeypatch):
    class BadResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "response": json.dumps(
                    {
                        "title": "Broken quest",
                        "duration_minutes": 5,
                        "mission": "Only part of a mission",
                        "steps": ["One step"],
                    }
                )
            }

    monkeypatch.setattr(
        outsidein.requests, "post", lambda *args, **kwargs: BadResponse()
    )

    mission, source = outsidein.generate_mission("Riverside", 10, "Water birds")

    assert source == "Curated offline fallback"
    assert mission["reflection_question"]


@pytest.mark.parametrize(
    "bad_mission",
    [
        [],
        {"title": "Broken", "duration_minutes": 5, "steps": ["A", "B"]},
        {
            "title": "Broken",
            "duration_minutes": 5,
            "mission": "Pick up clues.",
            "steps": "not a list",
            "reflection_question": "Why?",
            "safety_note": "Be safe.",
        },
        {
            "title": "Broken",
            "duration_minutes": 5,
            "mission": "Pick up clues.",
            "steps": ["A", "B", "C", "D", "E"],
            "reflection_question": "Why?",
            "safety_note": "Be safe.",
        },
        {
            "title": "Broken",
            "duration_minutes": 5,
            "mission": "Pick up clues.",
            "steps": ["A", 1],
            "reflection_question": "Why?",
            "safety_note": "Be safe.",
        },
    ],
)
def test_rejects_invalid_mission_shape(bad_mission):
    with pytest.raises(ValueError):
        outsidein.validate_mission(bad_mission, max_minutes=5)


@pytest.mark.parametrize("duration", [0, -1, 6, True, "5"])
def test_rejects_invalid_duration(duration):
    mission = valid_mission()
    mission["duration_minutes"] = duration

    with pytest.raises(ValueError):
        outsidein.validate_mission(mission, max_minutes=5)


def test_rejects_missing_fields():
    with pytest.raises(ValueError):
        outsidein.validate_mission({"title": "Incomplete"}, max_minutes=10)


def test_rejects_invalid_steps():
    mission = valid_mission()
    mission["steps"] = ["Only one step"]

    with pytest.raises(ValueError):
        outsidein.validate_mission(mission, max_minutes=5)


def test_saves_observation_locally(tmp_path):
    journal = tmp_path / "observations.json"

    outsidein.save_observation(
        valid_mission(), "I noticed two leaf shapes.", journal
    )

    records = json.loads(journal.read_text(encoding="utf-8"))
    assert len(records) == 1
    assert records[0]["mission_title"] == "Leaf Detective"
    assert records[0]["observation"] == "I noticed two leaf shapes."
    assert records[0]["completed_at"]


def test_appends_to_existing_journal(tmp_path):
    journal = tmp_path / "observations.json"
    outsidein.save_observation(valid_mission(), "First observation", journal)
    outsidein.save_observation(valid_mission(), "Second observation", journal)

    records = json.loads(journal.read_text(encoding="utf-8"))
    assert len(records) == 2


def test_rejects_empty_observation(tmp_path):
    with pytest.raises(ValueError):
        outsidein.save_observation(
            valid_mission(), "   ", tmp_path / "observations.json"
        )
