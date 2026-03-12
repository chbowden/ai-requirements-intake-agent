from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"message": "AI Requirements Intake Agent API is running."}


@router.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
