from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.intake import (
    ArtifactFileResponse,
    ArtifactGenerationResponse,
    AnswerRequest,
    QuestionPayload,
    SessionProgressResponse,
    StartSessionRequest,
)
from app.services.artifact_generator import generate_artifacts, write_artifacts
from app.services.intake_engine import INTAKE_QUESTIONS, get_next_question

router = APIRouter(prefix="/intake", tags=["intake"])
output_dir = Path(__file__).resolve().parents[3] / "output"

session_store: dict[str, dict[str, object]] = {}


@router.post("/session/start", response_model=SessionProgressResponse)
def start_session(payload: StartSessionRequest) -> SessionProgressResponse:
    session_id = str(uuid4())
    session_store[session_id] = {
        "answered_count": 0,
        "answers": {"initial_problem": payload.initial_problem.strip()},
    }
    return _build_response(session_id)


@router.post("/session/{session_id}/answer", response_model=SessionProgressResponse)
def submit_answer(session_id: str, payload: AnswerRequest) -> SessionProgressResponse:
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answered_count = int(session["answered_count"])
    if answered_count >= len(INTAKE_QUESTIONS):
        return _build_response(session_id)

    answer_text = payload.answer.strip()
    question = INTAKE_QUESTIONS[answered_count]
    answers = dict(session["answers"])
    answers[question.id] = answer_text

    session_store[session_id] = {
        "answered_count": answered_count + 1,
        "answers": answers,
    }
    return _build_response(session_id)


@router.get("/session/{session_id}", response_model=SessionProgressResponse)
def get_session(session_id: str) -> SessionProgressResponse:
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")
    return _build_response(session_id)


@router.post(
    "/session/{session_id}/artifacts",
    response_model=ArtifactGenerationResponse,
)
def generate_session_artifacts(session_id: str) -> ArtifactGenerationResponse:
    progress = _build_response(session_id)
    if not progress.completed:
        raise HTTPException(
            status_code=400,
            detail="Session is not complete. Answer all follow-up questions first.",
        )

    artifacts = generate_artifacts(progress.answers)
    json_file, markdown_file = write_artifacts(session_id, artifacts, output_dir)
    session = _get_session_or_404(session_id)
    session["artifacts"] = {
        "json": json_file,
        "markdown": markdown_file,
    }
    json_path = Path(json_file)
    markdown_path = Path(markdown_file)

    return ArtifactGenerationResponse(
        session_id=session_id,
        json_artifact=ArtifactFileResponse(
            filename=json_path.name,
            download_url=f"/intake/session/{session_id}/artifacts/json",
        ),
        markdown_artifact=ArtifactFileResponse(
            filename=markdown_path.name,
            download_url=f"/intake/session/{session_id}/artifacts/markdown",
        ),
        artifacts=artifacts,
    )


@router.get("/session/{session_id}/artifacts/{artifact_type}")
def download_session_artifact(session_id: str, artifact_type: str) -> FileResponse:
    session = _get_session_or_404(session_id)
    generated_artifacts = session.get("artifacts")
    if not isinstance(generated_artifacts, dict):
        raise HTTPException(status_code=404, detail="Artifacts not found")

    artifact_path_raw = generated_artifacts.get(artifact_type)
    if not isinstance(artifact_path_raw, str):
        raise HTTPException(status_code=404, detail="Artifacts not found")

    artifact_path = Path(artifact_path_raw).resolve()
    try:
        artifact_path.relative_to(output_dir.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Artifacts not found") from exc

    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="Artifacts not found")

    media_type = "application/json" if artifact_type == "json" else "text/markdown"
    return FileResponse(
        artifact_path,
        media_type=media_type,
        filename=artifact_path.name,
    )


def _build_response(session_id: str) -> SessionProgressResponse:
    session = _get_session_or_404(session_id)
    answered_count = int(session["answered_count"])
    answers = dict(session["answers"])
    next_question = get_next_question(answered_count)
    return SessionProgressResponse(
        session_id=session_id,
        completed=next_question is None,
        answered_count=answered_count,
        total_questions=len(INTAKE_QUESTIONS),
        next_question=(
            QuestionPayload(id=next_question.id, text=next_question.text)
            if next_question
            else None
        ),
        answers=answers,
    )


def _get_session_or_404(session_id: str) -> dict[str, object]:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
