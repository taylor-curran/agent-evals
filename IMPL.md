# Data+AI Service Implementation Plan

## Overview
Transform the current service from a stateful dataset manager to a stateless toolbox following `MICROSERVICE_ARCHITECTURE.md`.

## Implementation Decisions ✅

### 1. Data Strategy: **Start Fresh**
- Move existing database to `z_archive/` 
- Create new schema from scratch
- No data migration needed

### 2. Implementation Approach: **Incremental**
- Transform existing endpoints step-by-step
- Validate each step using manual testing
- Maintain service functionality throughout

### 3. GitHub API Strategy: **Light Usage**
- Rate limits not a concern initially (5000/hour authenticated)
- Simple error handling and retry logic
- Focus on correctness over optimization

### 4. Testing Depth: **Medium**
- Core functionality tests
- Integration tests for key workflows
- Manual validation using VALIDATION_GUIDE.md

## Implementation Phases

### Phase 1: Fresh Database Setup 🗃️

#### Step 1.1: Archive Existing Data
```bash
# Move existing database to archive
mv microservices/data-ai-service/data_ai_service.db z_archive/data_ai_service_old.db
```

#### Step 1.2: Update Database Models
```python
# models/database.py - complete rewrite:
+ repositories table (id, last_synced, default_branch)
+ pr_issues table (repo_id, pr_base_sha, pr_merge_sha, issue_numbers: json)
+ prompts table (id, pr_issue_id, prompt_text, generation_strategy)
- Remove all old table definitions
```

#### Step 1.3: Test New Schema
```bash
# Start service to create new tables
python -m uvicorn main:app --port 8001
curl http://localhost:8001/health  # Should work
```

**🧪 MANUAL VALIDATION**: Human developer validates health check works and database tables are created properly.

### Phase 2: GitHub Service Updates 🔧

#### Step 2.1: Enhance GraphQL Query
```python
# services/github_service.py updates:
+ Add baseRefOid field to capture pr_base_sha
+ Add repository metadata collection
+ Group issues by PR (JSON arrays)
```

#### Step 2.2: Add Repository Caching
```python
+ create_or_update_repository()
+ get_repository_metadata()
+ check_sync_status()
```

**🧪 MANUAL VALIDATION**: Human developer tests repository sync endpoint using updated VALIDATION_GUIDE.md step 2.

### Phase 3: API Endpoint Migration 🌐

#### Step 3.1: Replace GitHub Router
```python
# routers/github.py → routers/repos.py
- POST /github/extract → POST /repos/sync
- GET /github/datasets → GET /repos/{owner/repo}/pr-issues  
- GET /github/datasets/{id} → (remove - stateless)
```

#### Step 3.2: Add New Routers
```python
+ routers/prompts.py (POST /prompts/generate)
+ routers/evaluate.py (POST /evaluate/diff)
```

#### Step 3.3: Update Main App
```python
# main.py updates:
- Remove github router
+ Add repos, prompts, evaluate routers
```

**🧪 MANUAL VALIDATION**: Human developer tests PR/issue pairs endpoint using updated VALIDATION_GUIDE.md step 3.

### Phase 4: Prompt Generation Implementation 📝

#### Step 4.1: Port Archive Code
```python
# Port from archive_src/generate/generate_prompts_from_issues.py:
+ Issue data fetching
+ Text sanitization (remove PR hints)
+ OpenAI integration (optional)
+ Caching logic
```

#### Step 4.2: Create Prompt Service
```python
+ services/prompt_service.py
+ database/prompt_crud.py
+ models/prompt_schemas.py
```

#### Step 4.3: Add Checkout Instructions
```python
+ Include repo_url, checkout_sha in prompt response
+ Link to pr_base_sha from pr_issues table
```

**🧪 MANUAL VALIDATION**: Human developer tests prompt generation using updated VALIDATION_GUIDE.md step 4.

### Phase 5: Diff Evaluation Implementation ⚖️

#### Step 5.1: Create Evaluation Service
```python
+ services/evaluation_service.py
+ Basic diff similarity algorithms
+ File path matching
+ Line change analysis
```

#### Step 5.2: Add Analysis Features
```python
+ Scoring mechanisms (0.0 - 1.0)
+ Detailed comparison reports
+ Approach analysis
```

**🧪 MANUAL VALIDATION**: Human developer tests diff evaluation using updated VALIDATION_GUIDE.md step 5.

### Phase 6: Testing & Validation ✅

#### Step 6.1: Update Existing Tests
```python
# Update all tests for new schema:
- test_crud.py updates
- test_github_router.py → test_repos_router.py
+ test_prompt_generation.py
+ test_evaluation.py
```

#### Step 6.2: Integration Testing
```python
+ Test full workflow: sync → generate → evaluate
+ Test with real GitHub repos
+ Validate updated VALIDATION_GUIDE.md endpoints
```

**🧪 MANUAL VALIDATION**: Human developer runs complete workflow test and database inspection from updated VALIDATION_GUIDE.md.

## Implementation Order

### Phase 1: Foundation (Days 1-2)
- [ ] Archive existing data 
- [ ] Create new database schema
- [ ] Update GitHub service for version tracking
- [ ] Transform /github/extract → /repos/sync endpoint
- [ ] **Update VALIDATION_GUIDE.md** with new schema expectations

### Phase 2: Core Features (Days 3-4)
- [ ] Add /repos/{owner/repo}/pr-issues endpoint
- [ ] Port prompt generation from archive_src
- [ ] Create /prompts/generate endpoint
- [ ] **Update VALIDATION_GUIDE.md** with prompt generation tests

### Phase 3: Evaluation & Testing (Days 5-6)
- [ ] Implement diff evaluation service
- [ ] Add /evaluate/diff endpoint
- [ ] Medium-depth testing
- [ ] **Update VALIDATION_GUIDE.md** with complete workflow
- [ ] **Human developer validates** each step manually

## Key Implementation Files

```
microservices/data-ai-service/
├── migrate_schema.py           # NEW - migration script
├── models/database.py          # UPDATE - new schema
├── routers/
│   ├── repos.py               # NEW - replaces github.py
│   ├── prompts.py             # NEW - prompt generation
│   └── evaluate.py            # NEW - diff evaluation
├── services/
│   ├── github_service.py      # UPDATE - version tracking
│   ├── prompt_service.py      # NEW - from archive
│   └── evaluation_service.py  # NEW - diff comparison
└── database/
    ├── crud.py                # UPDATE - new schema
    ├── prompt_crud.py         # NEW
    └── evaluation_crud.py     # NEW (if needed)
```

## Risk Mitigation

### Data Preservation
- Move existing database to z_archive/ (not deleted)
- Can reference old implementation if needed
- Fresh start reduces complexity

### GitHub API Limits
- Simple retry logic for failures
- Rate limit awareness (5000/hour authenticated)
- Start with small repos for testing

### Breaking Changes
- Incremental endpoint updates
- Maintain health check throughout
- Manual validation after each phase

## Success Metrics

1. ✅ All VALIDATION_GUIDE.md endpoints return 200
2. ✅ Fresh database schema matches architecture
3. ✅ GitHub API integration captures pr_base_sha
4. ✅ Prompt generation works with real repos  
5. ✅ Diff evaluation provides meaningful scores
6. ✅ Manual validation passes all test cases

## Next Steps

1. **Archive existing data** to z_archive/
2. **Update VALIDATION_GUIDE.md** as we implement each feature 
3. **Start with Phase 1** - fresh database setup
4. **Human developer manually validates** each step using the guide
5. **Transform endpoints** one by one to match architecture

## Manual Validation Protocol

After each major step, the **human developer must**:
1. Update the corresponding section in VALIDATION_GUIDE.md
2. Run the curl commands from the guide
3. Verify expected responses match actual responses
4. Check database state using SQL queries
5. Confirm before proceeding to next step

This ensures the implementation stays aligned with the architecture and catches issues early.