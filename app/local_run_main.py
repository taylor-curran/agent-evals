# app/local_run_main.py

"""Uvicorn entry-point so `python -m app.main` just works.

Running this file will spin up an auto-reloading dev server when executed
 directly.  In production we expect a process manager (systemd, docker, etc.)
 to run `uvicorn app.main:create_app --factory ...` instead.
"""

from __future__ import annotations

import uvicorn

from . import create_app


def run() -> None:
    """Launch a local development server."""
    uvicorn.run(
        "app.main:create_app",
        factory=True,
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run()
