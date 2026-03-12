# AI Requirements Intake Agent (MVP)

## Current MVP Scope
- FastAPI backend shell
- Root and health check routes
- Intake session flow with structured follow-up questions
- Static frontend for initial problem + follow-up answers
- Modular folders for future LLM and voice features

## Run locally
1. Create and activate a virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Start server:
   uvicorn app.main:app --reload
4. Open:
   - API root: http://127.0.0.1:8000/
   - Health: http://127.0.0.1:8000/health
   - Frontend: http://127.0.0.1:8000/app

## Run tests
1. Install dependencies:
   pip install -r requirements.txt
2. Run:
   pytest

## Intake API
- `POST /intake/session/start`
- `POST /intake/session/{session_id}/answer`
- `GET /intake/session/{session_id}`
- `POST /intake/session/{session_id}/artifacts`

## Generated outputs
Artifacts are written to `output/` as:
- `requirements_<session_id>_<timestamp>.json`
- `requirements_<session_id>_<timestamp>.md`
