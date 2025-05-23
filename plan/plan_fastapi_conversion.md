# FastAPI Conversion Plan

> Prototype scope: expose two existing scripts as HTTP endpoints, use SQLite (async) for prompt storage, minimal auth, and keep existing CLI usability.

---
## 1. Objectives

1. **Expose functionality as a web service**
   * Map `src/generate/generate_prompts_from_issues.py` → `POST /prompts/generate`  
   * Map `src/run_ides/run_windsurf_prompts.py`   → `POST /prompts/run`
2. **Persist prompts in SQLite** (table: `prompts(pr_number INTEGER PRIMARY KEY, prompt_text TEXT)`), using **SQLModel** for a lightweight async ORM.
3. **Stay fully async** so FastAPI can scale with `uvicorn --workers` later.
4. **Maintain import-friendly functions**; CLI scripts remain callable directly (no argparse added).
5. **Prototype-level auth**: none initially; optional Basic / Bearer token stub ready.
6. **Simple deployment path**: local `uvicorn`, then dockerise → K8s / serverless when needed.

---
## 2. Deliverables

| Item | Path | Notes |
|------|------|-------|
| FastAPI app factory | `app/main.py` | `create_app()` returns `FastAPI` instance |
| Routers | `app/routers/prompts.py` | Houses two endpoint functions |
| Models | `app/models.py` | `Prompt` SQLModel table |
| DB utils | `app/db.py` | Async engine/session helpers |
| DB setup script | `scripts/init_db.py` | One-off: create SQLite schema |
| Package config | `pyproject.toml` | Hatch build settings |
| Tests | `tests/test_prompts.py` | Pytest, uses `httpx` async client |
| Dockerfile (optional) | `Dockerfile` | Only if/when containerising |

---
## 3. Project Structure After Migration

```
agent_evals/
├── app/
│   ├── __init__.py           # create_app()
│   ├── main.py               # uvicorn entry-point
│   ├── models.py             # SQLModel Prompt
│   ├── db.py                 # engine/session, init_db()
│   └── routers/
│       └── prompts.py        # /prompts endpoints
├── src/                      # original code stays
│   └── ...
├── plan/
│   └── fastapi_conversion.md # ← this file
└── requirements.txt
```

---
## 4. Dependencies

Add (or update) `requirements.txt`:

```
fastapi>=0.111
uvicorn[standard]>=0.29
sqlmodel>=0.0.16  # built on SQLAlchemy 2.x
aiosqlite>=0.20   # async SQLite driver
httpx[async]>=0.27 # testing client
```

> Keep existing libs; no argparse added.

---
## 5. Database Layer

1. **Define model**
   ```python
   # app/models.py
   class Prompt(SQLModel, table=True):
       pr_number: int | None = Field(default=None, primary_key=True)
       prompt_text: str
   ```
2. **Engine & session** (`app/db.py`)
   ```python
   from sqlalchemy.ext.asyncio import create_async_engine
   
   engine = create_async_engine("sqlite+aiosqlite:///evals.db", echo=False)
   async_session = async_sessionmaker(engine, expire_on_commit=False)
   ```
3. **Init DB setup** via `scripts/init_db.py` (one-off):
   ```python
   async def init_db() -> None:
       async with engine.begin() as conn:
           await conn.run_sync(SQLModel.metadata.create_all)
   ```

---
## 6. Endpoint Design

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| POST | `/prompts/generate` | `generate_prompts` | Runs generator script, stores rows in DB, returns count added |
| POST | `/prompts/run` | `run_windsurf_prompt` | Pops next prompt from DB (FIFO), calls `run_prompt_for_next_row`, streams/logs result |

**Implementation notes**
* Wrap existing synchronous helper functions in `run_in_threadpool` if they cannot be made `async def` directly.
* Ensure underlying functions remain import-friendly with keyword args.
* Use dependency injection for DB session (`Depends(get_session)`).

---
## 7. Auth Stub (optional, future)

```python
security = HTTPBearer()

async def require_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != os.environ.get("API_TOKEN"):
        raise HTTPException(status_code=401)
```
Apply with `dependencies=[Depends(require_token)]` once needed.

---
## 8. Running Locally

```bash
# Create venv & install deps
uv venv
source .venv/bin/activate
uv pip install -e .     # install package in dev mode

# Initialize DB
python scripts/init_db.py

# Run API
python -m app.main     # auto-reload dev server
```

Open Swagger UI: `http://127.0.0.1:8000/docs`

---
## 9. Deployment Path

1. **Phase 0**: run with `uvicorn` + `systemd` on dev box.
2. **Phase 1**: add `Dockerfile`:
   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /code
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "80"]
   ```
3. **Phase 2**: push image to registry & deploy via K8s or serverless (e.g., Cloud Run, Lambda + API Gateway).

_No immediate decision required; prototype works in phase 0._

---
## 10. Testing

* Use `pytest-asyncio` + `httpx.AsyncClient`.
* Provide fixtures for temp SQLite in memory.
* Cover:
  * Successful generation, DB insert count.
  * Running prompt returns 200 & triggers script stub.

---
## 11. Timeline / Steps

| # | Task | Est.
|---|------|-----|
| 1 | Scaffold `app/` structure, requirements | 0.5 d |
| 2 | Implement DB layer & migration script | 0.5 d |
| 3 | Port scripts to async-friendly functions | 0.5 d |
| 4 | Build routers & wiring | 0.5 d |
| 5 | Smoke test with Swagger UI | 0.25 d |
| 6 | Add tests | 0.5 d |
| 7 | Write Dockerfile (optional) | 0.25 d |
| **Total** | **~3 d** |

---
## 12. Next Steps / Nice-to-haves

* Add auth token & rate-limiting.
* Prometheus metrics & `/health` endpoint.
* Pagination / filtering for prompts list.
* Background worker (Celery / RQ) if prompt processing becomes long-running.
* Migrate from SQLite → Postgres when multi-instance deployment required.

---
### Done 🚀
