# Project-Specific Instructions for agent_evals

## Python Environment Management

When working with this project:

1. **Activate the virtual environment first:**
   ```bash
   source .venv/bin/activate
   ```

2. **After activation, use regular Python commands:**
   - `python script.py` (not `uv run python`)
   - `pytest` (not `uv run pytest`)
   - etc.

3. **Only use `uv` for package management:**
   - `uv pip install package_name`
   - `uv pip list`
   - etc.

The key point: Once the venv is activated, interact with it like a normal Python environment. UV is just the package manager, not a runtime wrapper.