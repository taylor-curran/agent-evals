# Data-AI Service Manual Validation Guide

This guide walks you through validating each endpoint of the data-ai service step by step, showing you exactly what's happening with requests, responses, and database changes.

## Prerequisites

1. **Start the service:**
```bash
source .venv/bin/activate
cd microservices/data-ai-service
python -m uvicorn main:app --port 8000
```

2. **Check the database (optional):**
```bash
sqlite3 microservices/data-ai-service/data_ai_service.db
.tables
.schema
```

## Step-by-Step Validation

### 1. Health Check
**Purpose:** Verify the service is running

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok"
}
```

---

### 2. Create a Project
**Purpose:** Store project metadata in the database

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test GitHub Analysis",
    "description": "Analyzing Python repositories for code quality"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "Test GitHub Analysis",
  "description": "Analyzing Python repositories for code quality",
  "created_at": "2025-01-18T18:30:00.123456"
}
```

**What happens behind the scenes:**
- Creates a new row in the `projects` table
- Auto-generates an ID and timestamp
- Returns the created project with its ID

**Check the database:**
```bash
sqlite3 microservices/data-ai-service/data_ai_service.db "SELECT * FROM projects;"
```

---

### 3. Get Project Details
**Purpose:** Retrieve a specific project by ID

```bash
curl http://localhost:8000/projects/1
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "Test GitHub Analysis",
  "description": "Analyzing Python repositories for code quality",
  "created_at": "2025-01-18T18:30:00.123456"
}
```

---

### 4. List All Projects
**Purpose:** See all projects in the database

```bash
curl http://localhost:8000/projects
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "name": "Test GitHub Analysis",
    "description": "Analyzing Python repositories for code quality",
    "created_at": "2025-01-18T18:30:00.123456"
  }
]
```

---

### 5. Extract GitHub Data
**Purpose:** The main feature - fetch and analyze repository data from GitHub

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "repo_url": "https://github.com/psf/requests",
    "filters": {
      "file_extensions": [".py"],
      "max_files": 3
    }
  }'
```

**Expected Response:**
```json
{
  "extraction_id": 1,
  "status": "completed",
  "message": "Successfully extracted data from psf/requests"
}
```

**What happens behind the scenes:**
1. Parses the GitHub URL to extract owner/repo
2. Makes GitHub API call to get repository metadata
3. Fetches file tree from the repository
4. Filters files by extension (.py)
5. Downloads content of up to 3 Python files
6. Stores everything in the `extractions` table
7. Links extraction to the project via `project_id`

**Check the extraction in database:**
```bash
sqlite3 microservices/data-ai-service/data_ai_service.db \
  "SELECT id, project_id, status, created_at FROM extractions;"
```

---

### 6. Get Extraction Details
**Purpose:** Check status and results of a specific extraction

```bash
curl http://localhost:8000/extractions/1
```

**Expected Response:**
```json
{
  "id": 1,
  "project_id": 1,
  "status": "completed",
  "created_at": "2025-01-18T18:31:00.123456",
  "result": {
    "repository": {
      "full_name": "psf/requests",
      "description": "A simple, yet elegant, HTTP library.",
      "stars": 50000,
      "language": "Python"
    },
    "files": [
      {
        "path": "requests/__init__.py",
        "size": 4521,
        "content": "# -*- coding: utf-8 -*-\n..."
      },
      {
        "path": "requests/api.py",
        "size": 6234,
        "content": "# -*- coding: utf-8 -*-\n..."
      }
    ],
    "metadata": {
      "extraction_time": "2025-01-18T18:31:00.123456",
      "files_processed": 2,
      "total_size": 10755
    }
  }
}
```

---

### 7. Update a Project
**Purpose:** Modify project metadata

```bash
curl -X PUT http://localhost:8000/projects/1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated: Analyzed requests library for code patterns"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "Test GitHub Analysis",
  "description": "Updated: Analyzed requests library for code patterns",
  "created_at": "2025-01-18T18:30:00.123456"
}
```

---

### 8. Delete a Project
**Purpose:** Remove a project and all its extractions (cascade delete)

```bash
curl -X DELETE http://localhost:8000/projects/1
```

**Expected Response:**
```json
{
  "message": "Project deleted successfully"
}
```

**What happens behind the scenes:**
- Deletes the project from `projects` table
- CASCADE DELETE removes all related extractions
- Database is cleaned up automatically

**Verify deletion:**
```bash
sqlite3 microservices/data-ai-service/data_ai_service.db \
  "SELECT COUNT(*) as project_count FROM projects; \
   SELECT COUNT(*) as extraction_count FROM extractions;"
```

---

## Understanding the Data Flow

### Request Journey
1. **Client** → HTTP Request → **FastAPI Router**
2. **Router** → Validates input → **Service Layer**
3. **Service** → Business logic → **Database (CRUD)**
4. **Database** → SQLite operations → **Return data**
5. **Service** → Format response → **Router**
6. **Router** → JSON response → **Client**

### Key Components

**Routers** (`routers/github.py`):
- Define API endpoints
- Handle HTTP requests/responses
- Validate input data using Pydantic schemas

**Services** (`services/github_service.py`):
- Business logic for GitHub integration
- Makes external API calls
- Processes and transforms data

**CRUD** (`database/crud.py`):
- Database operations (Create, Read, Update, Delete)
- SQL queries via SQLAlchemy
- Transaction management

**Models** (`models/database.py`):
- SQLAlchemy table definitions
- Database schema

**Schemas** (`models/schemas.py`):
- Pydantic models for request/response validation
- Data type enforcement

---

## Debugging Tips

### Watch the server logs
The terminal running uvicorn shows:
- Incoming requests with method and path
- Response status codes
- Any errors or exceptions

Example:
```
INFO:     127.0.0.1:58432 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:58433 - "POST /projects HTTP/1.1" 200 OK
```

### Check database state
```bash
# Open SQLite shell
sqlite3 microservices/data-ai-service/data_ai_service.db

# Useful commands:
.tables                    # List all tables
.schema projects          # Show table structure
SELECT * FROM projects;   # View all projects
SELECT * FROM extractions WHERE project_id = 1;  # View extractions for a project
.quit                     # Exit
```

### Test error handling
Try these to see error responses:

```bash
# Non-existent project
curl http://localhost:8000/projects/999

# Invalid GitHub URL
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "repo_url": "not-a-url"
  }'

# Missing required field
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## What You're Seeing "With Your Own Eyes"

When you run these commands, you're observing:

1. **HTTP Traffic**: The actual requests being sent and responses received
2. **Database Changes**: Real data being written to SQLite
3. **GitHub API Integration**: Live calls to GitHub's API (rate limited to 60/hour for unauthenticated)
4. **Error Handling**: How the service responds to bad input
5. **Data Transformation**: Raw GitHub data → Structured database records

This is your "debugger-like experience" - you can see exactly what goes in, what happens inside, and what comes out!