from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Process liveness only; does not assert database readiness."""
    return HealthResponse()
