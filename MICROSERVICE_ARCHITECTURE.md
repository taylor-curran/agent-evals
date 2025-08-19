# Microservice Architecture - Agent Evaluation Platform

## Overview

Two-service architecture for evaluating coding agents using real GitHub data.

```
┌──────────────────────────────────────┐
│        Agent Controller              │
│         (Orchestrator)               │
│  • Manages evaluation projects       │
│  • Executes agents                   │
│  • Stores experiment results         │
└──────────────────────────────────────┘
                 ↓ HTTP
┌──────────────────────────────────────┐
│         Data+AI Service              │
│      (Stateless Toolbox)             │
│  • GitHub data extraction & caching  │
│  • Prompt generation from issues     │
│  • Diff evaluation                   │
└──────────────────────────────────────┘
```

## Service Responsibilities

### Agent Controller (Port 8000)
**Owns**: Evaluation projects, experiment configs, agent results, evaluation scores  
**Does**: Orchestrates workflows, executes agents, tracks experiments

### Data+AI Service (Port 8001)
**Owns**: Repository data, issue/PR pairs, generated prompts  
**Does**: GitHub sync, prompt generation, diff comparison

## Data Model

### Data+AI Service Database

```sql
-- Cached repository metadata
repositories (
    id: "owner/repo"
    last_synced: timestamp
    default_branch: text
)

-- Issue/PR pairs with version info
pr_issues (
    repo_id: FK
    pr_number: int
    pr_base_sha: text      -- commit PR branched from (what agent checks out)
    pr_base_branch: text   -- branch name (usually 'main')
    pr_merge_sha: text     -- merge commit (for diff comparison)
    issue_numbers: json    -- [123, 456]
    issues_metadata: json  -- [{number: 123, created_at: "...", title: "..."}, ...]
)

-- Cached prompts
prompts (
    id: uuid
    pr_issue_id: FK
    prompt_text: text
    generation_strategy: text
)
```

### Agent Controller Database

```sql
-- Evaluation projects
projects (
    id: uuid
    name: text
    description: text
    config: json
)

-- Agent execution results
agent_runs (
    project_id: FK
    prompt_id: text  -- from Data+AI
    agent_type: text
    generated_diff: text
    execution_time: timestamp
)

-- Evaluation scores
evaluations (
    agent_run_id: FK
    score: float
    analysis: json
)
```

## API Endpoints

### Data+AI Service

```
POST /repos/sync
  Input: {repo_url, lookback_days}
  Output: {new_prs: 15, new_issues: 23}

GET /repos/{owner/repo}/pr-issues
  Output: List of PR/issue pairs with version info

POST /prompts/generate
  Input: {pr_issue_ids: [...], strategy: "clean"}
  Output: {prompts: [{id, text, checkout_sha, checkout_branch, repo_url}]}

POST /evaluate/diff
  Input: {agent_diff, real_diff}
  Output: {score: 0.87, analysis: {...}}
```

### Agent Controller

```
POST /projects
  Create evaluation project

POST /projects/{id}/run
  Input: {repo, agent_type, prompt_strategy}
  Orchestrates: sync → generate → execute → evaluate

GET /projects/{id}/results
  Returns all experiment results
```

## Data Relationships

**Issues → Prompts → PRs → Agent Execution**
- Multiple issues can be closed by one PR (issues 123, 456 → PR 789)
- Prompts are generated from issue text (sanitized to prevent info leaking)
- One prompt per PR (combining all related issues)
- Each prompt includes the exact commit SHA to checkout (pr_base_sha)
- Agents clone repo at pr_base_sha to see code as developer did
- Prompts are cached and reusable across experiments

## Workflow Example

Real scenario: Issue #123 created in January (repo at commit `aaa111`), PR #789 merged in February, evaluation run in March

1. **Controller** creates project "Compare Claude vs GPT-4 on bug fixes"
2. **Controller** → **Data+AI**: Sync prefect/prefect repo
3. **Data+AI** returns:
   - Issue #123 linked to PR #789
   - `pr_base_sha: "bbb222"` (commit developer branched from)
   - `pr_merge_sha: "ccc333"` (merge commit for comparison)
4. **Controller** → **Data+AI**: Generate prompt from issue #123
5. **Data+AI** returns:
   ```json
   {
     "prompt_text": "Fix PDF parsing bug...",
     "checkout_sha": "bbb222",
     "repo_url": "https://github.com/prefect-io/prefect"
   }
   ```
6. **Controller** tells Claude: Clone prefect at `bbb222`, then fix: [prompt]
7. **Controller** tells GPT-4: Same repo, same commit `bbb222`, same prompt
8. **Controller** → **Data+AI**: Evaluate both agent diffs vs PR #789 actual diff
9. **Controller** stores results: which agent solution closer to human PR

## Key Design Principles

1. **Version Awareness**: Track exact commit states for accurate testing
2. **Data Reuse**: Repository data extracted once, used many times
3. **Stateless Operations**: Data+AI has no concept of projects or experiments
4. **Clear Boundaries**: GitHub data vs experiment data

## Configuration

```bash
# Data+AI Service
GITHUB_TOKEN=xxx
DATABASE_URL=sqlite:///data_ai.db
PORT=8001

# Agent Controller
DATA_AI_URL=http://localhost:8001
DATABASE_URL=sqlite:///controller.db
PORT=8000
```

## Development

```bash
# Terminal 1
cd microservices/data-ai-service
uvicorn main:app --port 8001 --reload

# Terminal 2
cd microservices/agent-controller
uvicorn main:app --port 8000 --reload
```

## Next Steps

1. Update Data+AI schema for version tracking
2. Implement stateless prompt generation API
3. Build Agent Controller orchestration
4. Add experiment tracking to Controller