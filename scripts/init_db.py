# scripts/init_db.py

from __future__ import annotations

import asyncio

from app.db import init_db


async def _main() -> None:
    await init_db()
    print("✓ Database initialised -> evals.db")


if __name__ == "__main__":
    asyncio.run(_main())
