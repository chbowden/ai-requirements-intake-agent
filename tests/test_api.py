from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes import intake
from app.main import app


client = TestClient(app)


def setup_function() -> None:
    intake.session_store.clear()


def test_system_routes_and_frontend() -> None:
    root_response = client.get("/")
    assert root_response.status_code == 200
    assert root_response.json() == {
        "message": "AI Requirements Intake Agent API is running."
    }

    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}

    ui_response = client.get("/app")
    assert ui_response.status_code == 200
    assert "text/html" in ui_response.headers["content-type"]


def test_intake_session_lifecycle_generates_artifacts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_output_dir: Path | None = None
    test_output_dir = Path(".tmp/test-artifacts")
    test_output_dir.mkdir(parents=True, exist_ok=True)

    original_write_artifacts = intake.write_artifacts

    def write_artifacts_in_tmp(session_id, artifacts, output_dir):
        nonlocal captured_output_dir
        captured_output_dir = test_output_dir
        return original_write_artifacts(session_id, artifacts, test_output_dir)

    monkeypatch.setattr(intake, "write_artifacts", write_artifacts_in_tmp)
    monkeypatch.setattr(intake, "output_dir", test_output_dir)

    start_response = client.post(
        "/intake/session/start",
        json={"initial_problem": "Inspection data is scattered across spreadsheets."},
    )
    assert start_response.status_code == 200

    payload = start_response.json()
    session_id = payload["session_id"]
    assert payload["completed"] is False
    assert payload["answered_count"] == 0
    assert payload["total_questions"] == 6
    assert payload["next_question"]["id"] == "problem_clarification"

    answers = [
        "Teams cannot prioritize urgent site issues.",
        "Operations managers, inspectors, executives",
        "Inspectors submit notes manually and managers consolidate them weekly.",
        "Reduce turnaround time and improve audit visibility.",
        "Manual re-entry causes delays and missed defects.",
        "No shared system of record or reporting workflow.",
    ]

    for index, answer in enumerate(answers, start=1):
        response = client.post(
            f"/intake/session/{session_id}/answer",
            json={"answer": answer},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["answered_count"] == index

    session_response = client.get(f"/intake/session/{session_id}")
    assert session_response.status_code == 200
    session_body = session_response.json()
    assert session_body["completed"] is True
    assert session_body["next_question"] is None
    assert session_body["answers"]["initial_problem"] == (
        "Inspection data is scattered across spreadsheets."
    )
    assert session_body["answers"]["stakeholders"] == (
        "Operations managers, inspectors, executives"
    )

    artifact_response = client.post(f"/intake/session/{session_id}/artifacts")
    assert artifact_response.status_code == 200
    artifact_body = artifact_response.json()
    assert artifact_body["session_id"] == session_id
    assert artifact_body["artifacts"]["solution_recommendation"] == "automation"
    assert artifact_body["json_artifact"]["download_url"] == (
        f"/intake/session/{session_id}/artifacts/json"
    )
    assert artifact_body["markdown_artifact"]["download_url"] == (
        f"/intake/session/{session_id}/artifacts/markdown"
    )
    assert Path(captured_output_dir / artifact_body["json_artifact"]["filename"]).exists()
    assert Path(
        captured_output_dir / artifact_body["markdown_artifact"]["filename"]
    ).exists()
    assert captured_output_dir == test_output_dir

    json_download = client.get(artifact_body["json_artifact"]["download_url"])
    assert json_download.status_code == 200
    assert json_download.headers["content-type"].startswith("application/json")

    markdown_download = client.get(artifact_body["markdown_artifact"]["download_url"])
    assert markdown_download.status_code == 200
    assert markdown_download.headers["content-type"].startswith("text/markdown")


def test_artifact_generation_requires_completed_session() -> None:
    start_response = client.post(
        "/intake/session/start",
        json={"initial_problem": "Need better onboarding workflow."},
    )
    session_id = start_response.json()["session_id"]

    artifact_response = client.post(f"/intake/session/{session_id}/artifacts")
    assert artifact_response.status_code == 400
    assert artifact_response.json() == {
        "detail": "Session is not complete. Answer all follow-up questions first."
    }


def test_unknown_session_returns_404() -> None:
    response = client.get("/intake/session/does-not-exist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}


def test_whitespace_only_input_is_rejected() -> None:
    start_response = client.post(
        "/intake/session/start",
        json={"initial_problem": "   "},
    )
    assert start_response.status_code == 422

    valid_start = client.post(
        "/intake/session/start",
        json={"initial_problem": "Need a better approval process."},
    )
    session_id = valid_start.json()["session_id"]

    answer_response = client.post(
        f"/intake/session/{session_id}/answer",
        json={"answer": "   "},
    )
    assert answer_response.status_code == 422


def test_artifact_download_requires_existing_generated_artifact() -> None:
    start_response = client.post(
        "/intake/session/start",
        json={"initial_problem": "Need a cleaner support intake."},
    )
    session_id = start_response.json()["session_id"]

    response = client.get(f"/intake/session/{session_id}/artifacts/json")
    assert response.status_code == 404
    assert response.json() == {"detail": "Artifacts not found"}
