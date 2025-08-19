# Data+AI Service Validation Guide v2

This guide validates the Data+AI Service endpoints based on the architecture in MICROSERVICE_ARCHITECTURE.md.

## Prerequisites

```bash
# Start the service
source .venv/bin/activate
cd microservices/data-ai-service
python -m uvicorn main:app --port 8001
```

## Core Endpoints

### 1. Health Check

```bash
curl http://localhost:8001/health
```

**Expected:**
```json
{"status": "ok"}
```

---

### 2. Sync Repository Data

**Purpose:** Extract PR/issue pairs with version tracking

```bash
curl -X POST http://localhost:8001/repos/sync \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/psf/requests",
    "lookback_days": 30
  }'
```

**Expected Response:**
```json
{
  "repo_id": "psf/requests",
  "new_prs": 15,
  "new_issues": 23,
  "total_pr_issue_pairs": 12
}
```

**What happens:**
- Fetches PRs that closed issues
- Stores `pr_base_sha` (commit PR branched from)
- Stores `pr_merge_sha` (merge commit for comparison)
- Links issues to PRs

**Check database:**
```bash
sqlite3 microservices/data-ai-service/data_ai_service.db \
  "SELECT pr_number, pr_base_sha, issue_numbers FROM pr_issues WHERE repo_id='psf/requests' LIMIT 3;"
```

---

### 3. Get PR/Issue Pairs

**Purpose:** List PR/issue pairs with version info

```bash
curl http://localhost:8001/repos/psf/requests/pr-issues
```

**Expected Response:**
```json
[
  {
    "pr_number": 6789,
    "pr_base_sha": "abc123def",
    "pr_base_branch": "main",
    "pr_merge_sha": "xyz789ghi",
    "issue_numbers": [1234, 5678],
    "issues_metadata": [
      {
        "number": 1234,
        "title": "Bug in session handling",
        "created_at": "2024-01-15T10:00:00Z"
      },
      {
        "number": 5678,
        "title": "Related auth issue",
        "created_at": "2024-01-20T14:30:00Z"
      }
    ]
  }
]
```

---

### 4. Generate Prompts

**Purpose:** Create sanitized prompts from issues with checkout instructions

```bash
curl -X POST http://localhost:8001/prompts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "pr_issue_ids": [1, 2],
    "strategy": "clean"
  }'
```

**Expected Response:**
```json
{
  "prompts": [
    {
      "id": "prompt-uuid-123",
      "prompt_text": "Fix the following bugs:\n1. Session handling is broken when...\n2. Authentication fails when...",
      "checkout_sha": "abc123def",
      "checkout_branch": "main",
      "repo_url": "https://github.com/psf/requests",
      "pr_number": 6789
    }
  ]
}
```

**Key points:**
- `prompt_text` has no PR references or hints
- `checkout_sha` tells agent exact commit to use
- Prompts are cached for reuse

---

### 5. Evaluate Diff

**Purpose:** Compare agent-generated diff vs real PR diff

```bash
curl -X POST http://localhost:8001/evaluate/diff \
  -H "Content-Type: application/json" \
  -d '{
    "agent_diff": "diff --git a/requests/sessions.py...",
    "real_diff": "diff --git a/requests/sessions.py...",
    "evaluation_strategy": "similarity"
  }'
```

**Expected Response:**
```json
{
  "score": 0.87,
  "analysis": {
    "files_matched": ["requests/sessions.py"],
    "files_missed": [],
    "similarity_score": 0.87,
    "approach_analysis": "Agent correctly identified the root cause..."
  }
}
```

---

## Complete Workflow Test

Simulate the full evaluation flow:

```bash
# 1. Sync repository
curl -X POST http://localhost:8001/repos/sync \
  -d '{"repo_url": "https://github.com/psf/requests", "lookback_days": 30}'

# 2. Get PR/issue pairs
curl http://localhost:8001/repos/psf/requests/pr-issues > pr_issues.json

# 3. Generate prompt from first pair
PR_ISSUE_ID=$(cat pr_issues.json | jq '.[0].id')
curl -X POST http://localhost:8001/prompts/generate \
  -d "{\"pr_issue_ids\": [$PR_ISSUE_ID], \"strategy\": \"clean\"}" > prompt.json

# 4. Check what commit agent should use
cat prompt.json | jq '.prompts[0].checkout_sha'

# 5. (Agent would clone at that SHA and generate a diff)

# 6. Evaluate the diff
curl -X POST http://localhost:8001/evaluate/diff \
  -d '{
    "agent_diff": "...",
    "real_diff": "..."
  }'
```

---

## Database Inspection

### View repository cache:
```sql
SELECT id, last_synced, default_branch 
FROM repositories;
```

### View PR/issue pairs with versions:
```sql
SELECT 
  pr_number,
  pr_base_sha,
  pr_base_branch,
  json_extract(issue_numbers, '$') as issues
FROM pr_issues 
WHERE repo_id = 'psf/requests'
LIMIT 5;
```

### View cached prompts:
```sql
SELECT 
  id,
  substr(prompt_text, 1, 100) as prompt_preview,
  generation_strategy
FROM prompts;
```

---

## Testing Version Awareness

To verify agents get the right commit:

```bash
# Get a PR/issue pair
curl http://localhost:8001/repos/psf/requests/pr-issues | jq '.[0]'

# Note the pr_base_sha (e.g., "abc123def")
# Generate prompt
curl -X POST http://localhost:8001/prompts/generate \
  -d '{"pr_issue_ids": [1], "strategy": "clean"}' | jq '.prompts[0]'

# Verify checkout_sha matches pr_base_sha
# This ensures agent sees code as developer did
```

---

## Key Differences from V1

1. **No projects table** - Data+AI is stateless
2. **Version tracking** - `pr_base_sha` for accurate testing
3. **Cached prompts** - Reusable across experiments
4. **Clear checkout instructions** - Each prompt includes exact SHA
5. **Stateless evaluation** - Just compares diffs, no project context

---

## Error Testing

```bash
# Invalid repo URL
curl -X POST http://localhost:8001/repos/sync \
  -d '{"repo_url": "not-a-url"}'

# Non-existent PR/issue ID
curl -X POST http://localhost:8001/prompts/generate \
  -d '{"pr_issue_ids": [999999]}'

# Missing required fields
curl -X POST http://localhost:8001/evaluate/diff \
  -d '{}'
```

This validates the Data+AI Service as a stateless toolbox that provides versioned GitHub data and evaluation utilities!