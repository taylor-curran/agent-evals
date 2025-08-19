# Data+AI Service - Microservice Architecture

## Role in System

This service is a **stateless toolbox** in the agent evaluation platform. It provides GitHub data extraction, prompt generation, and evaluation utilities to support agent testing experiments.

## Architecture Principles

- **Stateless**: No project or experiment tracking (that's Agent Controller's job)
- **Data Cache**: Shared repository data pool for efficiency
- **Version Aware**: Tracks exact commit SHAs for accurate agent testing
- **Reusable**: Same data/prompts used across multiple evaluation projects

## Key Responsibilities

### 1. Repository Data Management
- Cache GitHub repository metadata
- Extract PR/issue pairs with version tracking
- Store `pr_base_sha` (commit to test against) and `pr_merge_sha` (for comparison)

### 2. Prompt Generation
- Convert GitHub issues into sanitized prompts
- Remove PR hints to prevent agent cheating
- Include checkout instructions (repo + exact commit SHA)
- Cache prompts for reuse across experiments

### 3. Evaluation Utilities
- Compare agent-generated diffs vs real PR diffs
- Provide scoring and analysis
- Stateless operations (no result storage)

## Data Flow

```
Agent Controller → Data+AI Service → GitHub API
                ↓
Agent Controller ← Cached data + prompts + evaluations
```

## Critical Version Tracking

**Problem**: Agent must test against the same codebase the original developer saw
**Solution**: Track `pr_base_sha` - the exact commit the PR branched from

Example:
- Issue #123 created (January)
- Developer branches from commit `abc123` (February)  
- PR merged (February)
- Agent tests against commit `abc123` (March evaluation)

## Database Schema

```sql
repositories (id: "owner/repo", last_synced, default_branch)
pr_issues (repo_id, pr_number, pr_base_sha, pr_merge_sha, issue_numbers: json)
prompts (id, pr_issue_id, prompt_text, generation_strategy)
```

## API Design

```
POST /repos/sync - Extract/update repository data
GET /repos/{owner/repo}/pr-issues - List PR/issue pairs
POST /prompts/generate - Create sanitized prompts
POST /evaluate/diff - Compare agent vs real diffs
```

## Current Status

⚠️ **Under Development** - See `PROGRESS_TRACKER.md` for implementation gaps

The service currently has a different schema and endpoints that need to be migrated to match this architecture. Use `VALIDATION_GUIDE.md` to test the target state once implementation is complete.