# Microservice Architecture - Agent Evaluation Platform

## Overview

This document outlines a **2-service microservice architecture** designed for backend engineering beginners. The architecture balances simplicity with scalability, avoiding over-engineering while maintaining clear separation of concerns.

## Architecture Summary

```
┌─────────────────────────────────────┐
│          Agent Service              │
│        (Main Controller)            │
│  ┌─────────────────────────────────┐ │
│  │ Orchestrates Full Workflow      │ │
│  │ • Manages evaluation runs       │ │
│  │ • Executes agents               │ │
│  │ • Coordinates with Data+AI      │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
                    │
                    ▼ (HTTP calls)
┌─────────────────────────────────────┐
│         Data+AI Service             │
│        (Support Service)            │
│  ┌─────────────────────────────────┐ │
│  │ Provides Data & AI Operations   │ │
│  │ • GitHub API integration        │ │
│  │ • Prompt generation             │ │
│  │ • Diff evaluation               │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Service Details

### 1. Agent Service (Main Controller)

**Responsibility**: Orchestrates the entire evaluation workflow and manages agent execution.

**Technology Stack**:
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- Requests (for HTTP calls to Data+AI service)
- Agent execution libraries (Windsurf integration)

**API Endpoints**:
```
POST /eval/run-evaluation
  - Main entry point for evaluation runs
  - Orchestrates full workflow
  - Returns complete evaluation results

GET /eval/status/{evaluation_id}
  - Check status of running evaluation
  - Returns progress and logs

POST /agents/windsurf/execute
  - Execute Windsurf agent with given prompt
  - Returns generated code diff

GET /agents/available
  - List available agent types
  - Returns supported agents and their capabilities
```

**Key Functions**:
- Receive evaluation requests from users
- Call Data+AI service for data preparation
- Execute agents locally with generated prompts
- Call Data+AI service for evaluation
- Manage evaluation state and progress

### 2. Data+AI Service (Support Service)

**Responsibility**: Handles all data operations and AI-powered tasks.

**Technology Stack**:
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- GitHub API client (PyGithub or similar)
- OpenAI/Anthropic API clients
- SQLite/PostgreSQL (for data storage)

**API Endpoints**:
```
POST /github/extract-data
  - Extract PR/issue data from repositories
  - Returns structured dataset

GET /github/datasets
  - List available datasets
  - Returns dataset metadata

POST /prompts/generate
  - Convert issues to realistic prompts
  - Returns cleaned prompts

POST /evaluate/compare-diffs
  - Compare agent diff vs real PR diff
  - Returns evaluation scores and analysis

GET /evaluate/metrics/{evaluation_id}
  - Get detailed evaluation metrics
  - Returns performance analysis
```

**Key Functions**:
- GitHub API integration and rate limiting
- Data storage and caching
- AI prompt generation
- AI-powered evaluation
- Data preprocessing and cleaning

## Communication Flow

### Complete Evaluation Workflow

```
1. User Request
   POST /eval/run-evaluation
   {
     "repo_url": "https://github.com/user/repo",
     "agent_type": "windsurf",
     "n_prompts": 5
   }

2. Agent Service → Data+AI Service
   POST /github/extract-data
   {
     "repo_url": "https://github.com/user/repo",
     "limit": 10
   }

3. Agent Service → Data+AI Service
   POST /prompts/generate
   {
     "issues": [...],
     "count": 5
   }

4. Agent Service (Internal)
   Execute Windsurf agent with each prompt
   Capture generated diffs

5. Agent Service → Data+AI Service
   POST /evaluate/compare-diffs
   {
     "agent_diffs": [...],
     "real_pr_diffs": [...]
   }

6. Agent Service Response
   Return complete evaluation results to user
```

## File Structure

### Agent Service
```
agent_service/
├── main.py                 # FastAPI app entry point
├── routers/
│   ├── evaluation.py       # /eval/* endpoints
│   └── agents.py          # /agents/* endpoints
├── services/
│   ├── orchestrator.py    # Main workflow orchestration
│   ├── windsurf_agent.py  # Windsurf integration
│   └── data_client.py     # HTTP client for Data+AI service
├── models/
│   └── schemas.py         # Pydantic models
└── requirements.txt
```

### Data+AI Service
```
data_ai_service/
├── main.py                 # FastAPI app entry point
├── routers/
│   ├── github.py          # /github/* endpoints
│   ├── prompts.py         # /prompts/* endpoints
│   └── evaluation.py      # /evaluate/* endpoints
├── services/
│   ├── github_client.py   # GitHub API integration
│   ├── prompt_generator.py # AI prompt generation
│   └── evaluator.py       # AI evaluation
├── models/
│   └── schemas.py         # Pydantic models
├── database/
│   └── models.py          # Database models
└── requirements.txt
```

## Deployment Strategy

### Development Environment
```bash
# Terminal 1 - Data+AI Service
cd data_ai_service
uvicorn main:app --port 8001

# Terminal 2 - Agent Service  
cd agent_service
uvicorn main:app --port 8000
```

### Production Environment
- **Docker containers** for each service
- **Docker Compose** for local development
- **Kubernetes** or **Docker Swarm** for production scaling
- **nginx** as reverse proxy/load balancer

## Benefits of This Architecture

1. **Simple to Understand**: Only 2 services with clear responsibilities
2. **Easy to Deploy**: Fewer moving parts than complex microservices
3. **Scalable**: Can scale agent execution independently from data operations
4. **Maintainable**: Clear separation between orchestration and support functions
5. **Testable**: Each service can be tested independently

## Configuration Management

### Environment Variables
```bash
# Agent Service
AGENT_SERVICE_PORT=8000
DATA_AI_SERVICE_URL=http://localhost:8001

# Data+AI Service  
DATA_AI_SERVICE_PORT=8001
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_key
DATABASE_URL=sqlite:///./data.db
```

## Next Steps

1. **Start with Data+AI Service**: Build GitHub integration first
2. **Add Agent Service**: Build basic orchestration
3. **Test Integration**: Ensure services communicate properly
4. **Add Monitoring**: Logging and health checks
5. **Containerize**: Docker setup for deployment
6. **Scale**: Add load balancing and multiple instances

This architecture provides a solid foundation that can evolve as your understanding of backend engineering grows.
