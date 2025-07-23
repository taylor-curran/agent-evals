"""FastAPI entry point for Data+AI Service.

Bootstraps the SQLite database (explicit CREATE TABLE statements) and exposes a minimal health
check endpoint at `/health`.
"""
from typing import Dict

from fastapi import FastAPI
from models.database import init_db
from routers import github

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(title="Data+AI Service", version="0.1.0")

# Include routers
app.include_router(github.router)


@app.on_event("startup")
async def on_startup() -> None:
    init_db()


@app.get("/health", response_model=Dict[str, str])
async def health() -> Dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"}
