# agent_evals

## Quick-start (uv)

1. Create and activate a virtual environment

   ```bash
   uv venv
   source .venv/bin/activate
   ```

2. Install dependencies from `requirements.txt`

   ```bash
   uv pip install -r requirements.txt
   ```

3. Launch the development API server

   ```bash
   python -m app.main  # http://127.0.0.1:8000/docs
   ```

Optional extras:

* **Lock exact versions** for reproducible builds:
  ```bash
  uv pip compile -o requirements.lock
  ```
* **Run tests** (once they exist):
  ```bash
  pytest -q
  ```