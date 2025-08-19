# Progress Tracker - Data+AI Service Implementation

## Current State vs Architecture Gaps

After exhaustive review of current microservice vs `MICROSERVICE_ARCHITECTURE.md`, here are the critical mismatches:

---

## ❌ MAJOR GAPS - DATABASE SCHEMA

### Current Schema (Wrong)
```sql
-- datasets table (should not exist in Data+AI service)
datasets (id, repo_url, created_at, pr_count, issue_count)

-- pr_issues table (missing critical version fields)
pr_issues (
    dataset_id,      -- ❌ Wrong FK reference
    pr_number,
    pr_url, pr_title, pr_merged_at, pr_base_branch, pr_merge_commit_sha,
    issue_number,    -- ❌ Only ONE issue per row
    issue_url, issue_title, issue_body, issue_state, issue_reason
)

-- prompts table (missing generation strategy)
prompts (id, dataset_id, pr_number, prompt_text, mode, created_at)
```

### Required Schema (Per Architecture)
```sql
-- repositories table (NEW - for caching)
repositories (
    id: "owner/repo",
    last_synced: timestamp,
    default_branch: text
)

-- pr_issues table (MAJOR RESTRUCTURE)
pr_issues (
    repo_id: FK to repositories,     -- ❌ NOT dataset_id
    pr_number: int,
    pr_base_sha: text,               -- ❌ MISSING - critical for version tracking
    pr_base_branch: text,            -- ✅ exists but different purpose
    pr_merge_sha: text,              -- ❌ MISSING - need this for comparison
    issue_numbers: json,             -- ❌ MISSING - should be array [123, 456]
    issues_metadata: json            -- ❌ MISSING - consolidated issue data
)

-- prompts table (RESTRUCTURE)
prompts (
    id: uuid,
    pr_issue_id: FK,                 -- ❌ NOT dataset_id
    prompt_text: text,
    generation_strategy: text        -- ❌ NOT "mode"
)
```

---

## ❌ MAJOR GAPS - API ENDPOINTS

### Current Endpoints (Wrong)
```
❌ POST /github/extract - Creates "datasets", project-based
❌ GET /github/datasets - Lists "datasets"
❌ GET /github/datasets/{id} - Dataset details
```

### Required Endpoints (Per Architecture)
```
✅ Need: POST /repos/sync
✅ Need: GET /repos/{owner/repo}/pr-issues
✅ Need: POST /prompts/generate
✅ Need: POST /evaluate/diff
```

---

## ❌ MAJOR GAPS - DATA FLOW

### Current Flow (Wrong)
1. Extract data → Create "dataset" → Store pr_issues with dataset_id
2. Service is **stateful** (owns datasets)
3. No version tracking (missing pr_base_sha)
4. One issue per pr_issues row

### Required Flow (Per Architecture)
1. Sync repo → Store in repositories table → Create pr_issues with repo_id
2. Service is **stateless** (no projects/datasets)
3. Version tracking (pr_base_sha for agent checkout)
4. Multiple issues per PR (JSON arrays)

---

## ❌ MAJOR GAPS - MISSING FEATURES

### Version Tracking (Critical)
- ❌ No `pr_base_sha` capture (what commit to test against)
- ❌ No checkout instructions in prompt generation
- ❌ Missing merge commit SHA for diff comparison

### Prompt Generation
- ❌ No prompt generation endpoint
- ❌ No sanitization (info leak prevention)
- ❌ No caching/reuse logic

### Diff Evaluation
- ❌ No diff comparison endpoint
- ❌ No evaluation algorithms

---

## ✅ WHAT WORKS (Can Reuse)

### From Current Microservice
- ✅ Basic FastAPI structure
- ✅ GitHub GraphQL client (services/github_service.py)
- ✅ Database initialization pattern
- ✅ Health check endpoint
- ✅ PR/issue fetching logic (needs modification)

### From Archive (archive_src/generate)
- ✅ PR-issue mapping logic (fetch_pr_closing_issues.py)
- ✅ Prompt generation logic (generate_prompts_from_issues.py)
- ✅ Issue data fetching
- ✅ OpenAI integration for prompt sanitization

---

## 📋 IMPLEMENTATION PRIORITY

### Phase 1: Database Schema Migration (CRITICAL)
1. **Create migration script** to transform existing data
2. **Replace datasets table** with repositories table
3. **Restructure pr_issues table** with version fields
4. **Update prompts table** structure

### Phase 2: API Endpoints (HIGH)
1. **Replace /github/extract** with **POST /repos/sync**
2. **Add GET /repos/{owner/repo}/pr-issues**
3. **Add POST /prompts/generate** (port from archive)
4. **Add POST /evaluate/diff**

### Phase 3: Version Tracking (HIGH)
1. **Capture pr_base_sha** in GitHub service
2. **Add checkout instructions** to prompt generation
3. **Store merge commit SHA** for comparison

### Phase 4: Prompt Generation (MEDIUM)
1. **Port prompt generation** from archive_src
2. **Add sanitization** (remove PR hints)
3. **Implement caching** logic

### Phase 5: Diff Evaluation (MEDIUM)
1. **Create evaluation service**
2. **Implement similarity algorithms**
3. **Add analysis/scoring**

---

## 🔧 IMMEDIATE ACTIONS NEEDED

### 1. Schema Migration Script
- Read existing pr_issues data
- Group by PR number → create new pr_issues records
- Populate pr_base_sha (will need GitHub API calls)
- Drop datasets table

### 2. Update GitHub Service
- Modify GraphQL query to capture base commit SHA
- Add repository metadata caching
- Remove dataset creation logic

### 3. New Router Structure
- Create /repos endpoints
- Create /prompts endpoints  
- Create /evaluate endpoints
- Remove /github/datasets endpoints

### 4. Port Archive Code
- Move prompt generation logic from archive_src
- Adapt for new schema
- Add to microservice

---

## 🎯 SUCCESS CRITERIA

The Data+AI service should be **stateless** and provide:
1. ✅ Repository data caching with version tracking
2. ✅ PR/issue pairs with exact commit SHAs
3. ✅ Sanitized prompt generation with checkout instructions
4. ✅ Diff evaluation capabilities
5. ❌ NO project/dataset management (that's Agent Controller's job)

This transforms it from a **stateful dataset manager** to a **stateless toolbox** as designed.

---

## 🧪 VALIDATION REALITY CHECK

To demonstrate the gaps, here's what **VALIDATION_GUIDE_V2.md** expects vs current reality:

| V2 Guide Expects | Current Implementation | Status |
|------------------|----------------------|---------|
| `POST /repos/sync` | `POST /github/extract` | ❌ Wrong endpoint |
| `GET /repos/{owner/repo}/pr-issues` | `GET /github/datasets/{id}` | ❌ Wrong structure |
| `POST /prompts/generate` | **Missing entirely** | ❌ Not implemented |
| `POST /evaluate/diff` | **Missing entirely** | ❌ Not implemented |
| `repositories` table | `datasets` table | ❌ Wrong schema |
| `pr_base_sha` field | **Missing** | ❌ No version tracking |
| JSON issue arrays | Single issue rows | ❌ Wrong data model |
| Stateless operation | Stateful datasets | ❌ Wrong architecture |
| Cached prompts | No prompt generation | ❌ Missing feature |
| Checkout instructions | No version info | ❌ Missing critical data |

**Right now, every endpoint in VALIDATION_GUIDE_V2.md will fail.**

The tracker above shows exactly what needs to be implemented to make the validation guide work. Once these gaps are filled, VALIDATION_GUIDE_V2.md becomes your test suite to verify the service works as architected.