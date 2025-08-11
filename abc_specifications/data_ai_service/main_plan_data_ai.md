# Data+AI Service Main Plan

## Overview

The Data+AI Service is a FastAPI microservice that provides data and AI operations for the agent evaluation platform. It handles GitHub data extraction, prompt generation, and evaluation of agent-generated code.

## Core Responsibilities

1. **GitHub Integration** - Extract PR/issue data from repositories
2. **Prompt Generation** - Convert issues to clean coding prompts  
3. **AI Evaluation** - Compare agent solutions vs real PR solutions

## Service Architecture

```
data_ai_service/
├── main.py                    # FastAPI app entry point
├── routers/                   # API endpoints
│   ├── github.py             # GitHub data extraction
│   ├── prompts.py            # Prompt generation
│   └── evaluation.py         # AI evaluation
├── services/                  # Business logic
│   ├── github_service.py     # GitHub API integration
│   ├── prompt_service.py     # Prompt generation logic
│   └── evaluation_service.py # Diff comparison
├── models/                    # Data models
│   ├── schemas.py            # Pydantic models
│   └── database.py           # Database setup
├── database/                  # Data layer
│   └── crud.py               # Database operations
└── tests/                     # Test suite
```

## API Endpoints

### GitHub Data Extraction
- `POST /github/extract-data` - Extract PR/issue data from a repository
- `GET /github/datasets` - List all extracted datasets
- `GET /github/datasets/{id}` - Get specific dataset details

### Prompt Generation  
- `POST /prompts/generate` - Generate prompts from a dataset
- `GET /prompts/{dataset_id}` - List prompts for a dataset

### AI Evaluation
- `POST /evaluate/compare-diffs` - Compare agent vs real PR diffs
- `GET /evaluate/metrics/{id}` - Get evaluation metrics

## Implementation Status

### ✅ Completed
1. FastAPI skeleton with health endpoint
2. SQLite database with schema (datasets, pr_issues, prompts tables)
3. Basic pytest suite
4. Project structure

### 🚧 In Progress
- GitHub integration (see [GitHub Integration Plan](plan_github_integration_migration.md))

### 📋 Planned
- Prompt generation service
- AI evaluation endpoints
- Integration with Agent Service

## Database Schema

```sql
-- Datasets: Collection of PR/issues from a repo
CREATE TABLE datasets (
    id TEXT PRIMARY KEY,
    repo_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pr_count INTEGER,
    issue_count INTEGER
);

-- PR/Issue mappings
CREATE TABLE pr_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id TEXT REFERENCES datasets(id),
    pr_number INTEGER,
    pr_url TEXT,
    pr_merged_at TIMESTAMP,
    issue_number INTEGER,
    issue_url TEXT,
    issue_title TEXT,
    issue_body TEXT
);

-- Generated prompts
CREATE TABLE prompts (
    id TEXT PRIMARY KEY,
    dataset_id TEXT REFERENCES datasets(id),
    pr_number INTEGER,
    prompt_text TEXT,
    mode TEXT,  -- 'summary' or 'raw'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Configuration

```bash
# Already set by user
export GITHUB_TOKEN=<token>
export OPENAI_API_KEY=<key>

# Service config
export DATABASE_URL=sqlite:///./data_ai_service.db
export DATA_AI_SERVICE_PORT=8001
export LOG_LEVEL=INFO
```

## Development Workflow

### Running the Service
```bash
cd data_ai_service
uvicorn main:app --port 8001 --reload
```

### Running Tests
```bash
cd data_ai_service
pytest tests/ -v
```

### Health Check
```bash
curl http://localhost:8001/health
```

## Integration with Agent Service

The Data+AI Service provides data and AI operations that the Agent Service orchestrates:

1. Agent Service requests GitHub data extraction
2. Agent Service requests prompt generation
3. Agent Service executes agents with prompts
4. Agent Service sends diffs for evaluation

## Key Design Decisions

- **Test-First Development** - Write tests before implementation
- **Incremental Implementation** - Small, reviewable pieces
- **SQLite Database** - Simple, sufficient for demo
- **Function-Based Services** - No classes, keyword arguments
- **Async/Await** - Better performance for I/O operations

## Sub-Plans

- [GitHub Integration Migration](plan_github_integration_migration.md) - Detailed plan for GitHub service implementation

## Next Major Milestone

Complete GitHub integration to enable:
- Extracting real PR/issue data
- Storing in database
- API access to datasets

This forms the foundation for prompt generation and evaluation features.