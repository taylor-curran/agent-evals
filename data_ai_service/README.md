# Data+AI Service

A standalone FastAPI microservice that provides GitHub data extraction, prompt generation, and AI evaluation capabilities for the agent evaluation platform.

## Quick Start

### Prerequisites
- Python 3.12+
- GitHub Personal Access Token

### Installation

1. **Set up virtual environment** (from parent directory):
   ```bash
   cd agent_evals
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   export GITHUB_TOKEN="your_github_token_here"
   export OPENAI_API_KEY="your_openai_key_here"  # Optional, for AI features
   ```

3. **Run the service**:
   ```bash
   cd data_ai_service
   uvicorn main:app --reload --port 8001
   ```

4. **Verify it's running**:
   ```bash
   curl http://localhost:8001/health
   # Should return: {"status": "healthy"}
   ```

## API Endpoints

### Health Check
- `GET /health` - Service health status

### GitHub Data Extraction
- `POST /github/extract-data` - Extract PR/issue data from a repository
- `GET /github/datasets` - List all extracted datasets
- `GET /github/datasets/{id}` - Get specific dataset details

### Prompt Generation (Planned)
- `POST /prompts/generate` - Generate prompts from a dataset
- `GET /prompts/{dataset_id}` - List prompts for a dataset

### AI Evaluation (Planned)
- `POST /evaluate/compare-diffs` - Compare agent vs real PR diffs
- `GET /evaluate/metrics/{id}` - Get evaluation metrics

## Development

### Running Tests
```bash
# From data_ai_service directory
uv pip install -r requirements.txt
python -m pytest tests/ -v
```

### Database Schema
The service uses SQLite with three main tables:
- `datasets` - Collections of PR/issues from repositories
- `pr_issues` - Individual PR-issue mappings with metadata
- `prompts` - Generated coding prompts from issues

### Architecture

The service follows a layered architecture pattern:

- **API Layer** (`routers/`) - FastAPI endpoints for external communication
- **Service Layer** (`services/`) - Business logic and external API integration
- **Data Layer** (`database/`, `models/`) - Database operations and data models
- **Testing** (`tests/`) - Comprehensive test coverage for all layers

This structure supports:
- Clean separation of concerns
- Easy testing and mocking
- Future scalability and microservice separation

## Integration

The Data+AI Service is designed to work with:
- **Agent Service**: Provides data and evaluation for agent orchestration
- **GitHub API**: Direct integration for data extraction
- **OpenAI API**: For AI-powered prompt enhancement and evaluation


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token for API access |
| `OPENAI_API_KEY` | No | OpenAI API key for AI features |
| `DATABASE_URL` | No | SQLite database path (defaults to `data_ai_service.db`) |

## Contributing

This service follows the existing codebase patterns:
- Functions with keyword arguments (no argparse)
- Raw SQL approach for database operations
- Comprehensive test coverage
- Single function calls in `if __name__ == "__main__":` blocks
