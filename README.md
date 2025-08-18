# agent-evals

Agent evaluation platform using real GitHub data to test coding agents.

## Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export GITHUB_TOKEN=your_github_token_here
   export OPENAI_API_KEY=your_openai_key_here  # Optional, for AI summarization
   ```