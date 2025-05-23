# app/routers/prompts.py

from __future__ import annotations

from fastapi import APIRouter, status

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_prompts() -> dict[str, str]:  # pragma: no cover
    """Stub endpoint that will call the generator script later."""

    return {"detail": "generate_prompts not yet implemented"}


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def run_prompt() -> dict[str, str]:  # pragma: no cover
    """Stub endpoint that will call run_windsurf_prompt later."""

    return {"detail": "run_prompt not yet implemented"}
