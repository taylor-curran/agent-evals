# Agent Controller Service

**Main orchestrator** for the agent evaluation platform. Coordinates evaluation workflows and manages agent execution.

## Architecture Role
```
┌─────────────────────────────────────┐
│        Agent Controller             │ ← YOU ARE HERE
│      (Main Orchestrator)            │
│ • Manages evaluation runs           │
│ • Executes agents (Windsurf)        │
│ • Coordinates with Data+AI Service  │
└─────────────────────────────────────┘
                    ▼ HTTP calls
┌─────────────────────────────────────┐
│       Data+AI Service               │
│ • GitHub API • Prompts • Evaluation │
└─────────────────────────────────────┘
```

## Key Endpoints
- `POST /eval/run-evaluation` - Start agent evaluation 
- `GET /eval/status/{id}` - Check evaluation progress
- `POST /agents/windsurf/execute` - Execute Windsurf agent
- `GET /agents/available` - List supported agents

## Tech Stack
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server  
- **Port 8000** - Service port

## Quick Start
```bash
uvicorn main:app --port 8000
```

## Environment
```bash
AGENT_SERVICE_PORT=8000
DATA_AI_SERVICE_URL=http://localhost:8001
```

Coordinates with **Data+AI Service** (port 8001) for GitHub data, prompt generation, and evaluation.
