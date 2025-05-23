# app/__init__.py
from fastapi import FastAPI


def create_app() -> FastAPI:
    """Application factory for the agent_evals API."""

    app = FastAPI(title="agent_evals API")

    # Include routers if available; during early scaffolding they may not exist yet.
    try:
        from .routers import prompts  # pylint: disable=import-error

        app.include_router(prompts.router)
    except ImportError:
        pass

    return app


__all__ = ["create_app"]

