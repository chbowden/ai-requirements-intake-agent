from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.intake import router as intake_router
from app.api.routes.system import router as system_router

app = FastAPI(title="AI Requirements Intake Agent")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(system_router)
app.include_router(intake_router)


@app.get("/app", include_in_schema=False)
def intake_ui() -> FileResponse:
    return FileResponse(static_dir / "index.html")
