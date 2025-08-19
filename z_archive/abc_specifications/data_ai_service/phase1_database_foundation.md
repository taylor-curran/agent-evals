# Phase 1: Database Foundation - Focused Plan

## What We've Learned

### Key Insight: Version Control is Critical
- **Problem**: Issues are historical but repos are current versions
- **Solution**: Store `pr_merged_at` timestamp to checkout correct commit when running agents
- **Impact**: This is why we need rich PR metadata, not just issue data

### Architecture Decision: Raw SQL vs ORM
- **Decision**: Use raw SQL approach (existing pattern in codebase)
- **Reason**: User comfortable with SQL, existing `models/database.py` uses raw SQL
- **Mistake**: I added SQLAlchemy ORM models without checking existing approach

## Current Status - END OF DAY ✅ PHASE 1 COMPLETE

### ✅ ALL TASKS COMPLETED
- ✅ **Schema Analysis & Design** - Analyzed existing scripts, identified all required fields
- ✅ **Test Infrastructure** - conftest.py with fixtures for new schema
- ✅ **CRUD Tests** - test_crud.py with 5 tests, all passing 
- ✅ **Raw SQL Implementation** - database/crud.py using raw SQL queries
- ✅ **Updated Schema** - Added nullable fields for future features
- ✅ **Pydantic Schemas** - Updated to match new field structure

### 🎯 Key Achievements
1. **Fixed Architecture** - Reverted from ORM to raw SQL approach
2. **Rich Schema** - Added 6 new nullable fields ready for data population
3. **Version Control Ready** - Schema includes `pr_merge_commit_sha` and `pr_base_branch`
4. **Prompt Generation Ready** - Schema includes `issue_title` and `issue_body`

## Phase 1 Tasks (Revised)

### Task 1.1: Schema Analysis & Design ⏳ IN PROGRESS
**Goal**: Determine exactly what fields we need based on existing fetch scripts

**Research needed**:
- Analyze `src/generate/get_gh_data/fetch_pr_closing_issues.py` - what fields does it extract?
- Check `src/generate/get_gh_data/generate_prompts_from_issues.py` - what additional fields needed?
- Look at GitHub GraphQL/REST API docs for available fields

**Current fetch script (`fetch_pr_closing_issues.py`) extracts**:
```python
{
    "pr_number": pr_number,
    "pr_url": pr["url"], 
    "pr_merged_at": pr["mergedAt"],  # Critical for version control!
    "issue_number": iss["number"],
    "issue_url": iss["url"],
    "issue_state": iss["state"],
    "issue_reason": iss.get("stateReason"),
}
```

**Prompt generation script (`generate_prompts_from_issues.py`) needs**:
```python
# Makes separate REST API calls to get:
{
    "number": issue_number,
    "title": data.get("title", ""),     # Issue title - REQUIRED for prompts
    "body": data.get("body", ""),       # Issue body - REQUIRED for prompts  
    "url": issue_url,
}
```

**Fields we need to add to schema**:
- ✅ `pr_merged_at` - already in current schema (for version control)
- ❌ `pr_title` - need for prompt context and debugging  
- ❌ `issue_title` - CRITICAL for prompt generation
- ❌ `issue_body` - CRITICAL for prompt generation (core content)
- ❌ `pr_merge_commit_sha` - exact commit to checkout (future need)
- ❌ `pr_base_branch` - context for checkout (future need)

**GitHub GraphQL API can provide** (from `fetch_pr_closing_issues.py`):
- PR fields: `number`, `mergedAt`, `url`, `title`, `baseRefName`, `mergeCommit { oid }`
- Issue fields: `number`, `url`, `state`, `stateReason`, `title`, `body`

**Key insight**: We can get ALL required fields in one GraphQL query instead of making separate REST calls!

**Proposed Updated Schema**:
```sql
-- datasets table (minimal changes)
CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,              -- Keep TEXT for UUID/repo-name flexibility  
    repo_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pr_count INTEGER,
    issue_count INTEGER
);

-- pr_issues table (major additions)
CREATE TABLE IF NOT EXISTS pr_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id TEXT REFERENCES datasets(id),
    
    -- PR fields (some existing, some new)
    pr_number INTEGER,
    pr_url TEXT,
    pr_title TEXT,                    -- NEW: for prompt context
    pr_merged_at TIMESTAMP,           -- EXISTING: critical for version control
    pr_base_branch TEXT,              -- NEW: for checkout context (future)
    pr_merge_commit_sha TEXT,         -- NEW: exact commit to checkout (future)
    
    -- Issue fields (some existing, some new)  
    issue_number INTEGER,
    issue_url TEXT,
    issue_title TEXT,                 -- NEW: CRITICAL for prompt generation
    issue_body TEXT,                  -- NEW: CRITICAL for prompt generation (was existing)
    issue_state TEXT,                 -- EXISTING: open/closed
    issue_reason TEXT                 -- EXISTING: completed/not_planned/etc
);
```

**Key Changes from Current Schema**:
1. Added `pr_title` - for better prompt context and debugging
2. Added `pr_base_branch` - for future checkout functionality
3. Added `pr_merge_commit_sha` - for precise version control
4. Added `issue_title` - CRITICAL for prompt generation
5. Kept `issue_body` - already in schema but critical for prompts

**Deliverable**: Updated raw SQL schema with all required fields

### Task 1.2: Revert to Raw SQL Approach ⏳ PENDING
**Goal**: Remove ORM models, use raw SQL queries in crud.py

**Actions**:
1. Remove SQLAlchemy ORM models from `models/database.py`
2. Update `database/crud.py` to use raw SQL queries matching new schema
3. Update Pydantic schemas in `models/schemas.py` to match new fields
4. Update test fixtures to include new required fields
5. Update tests to work with raw SQL approach

**CRUD Functions to Update**:
```python
# database/crud.py - Raw SQL approach
def create_dataset(db_connection, repo_name: str, repo_url: str, total_pr_issues: int):
    # Use raw SQL INSERT with text-based ID

def save_pr_issues(db_connection, dataset_id: str, pr_issues_data: List[dict]):
    # Use raw SQL INSERT with all new fields:
    # pr_title, pr_base_branch, pr_merge_commit_sha, issue_title, issue_body

def get_datasets(db_connection):
    # Use raw SQL SELECT 

def get_dataset_details(db_connection, dataset_id: str):
    # Use raw SQL JOIN to get dataset + pr_issues
```

**Pydantic Schema Updates**:
```python
# models/schemas.py - Add new fields
class PRIssueBase(BaseModel):
    pr_number: int
    pr_title: str          # NEW
    pr_url: str
    pr_merged_at: datetime # NEW
    pr_base_branch: str    # NEW (optional)
    pr_merge_commit_sha: str # NEW (optional)
    issue_number: int
    issue_title: str       # NEW - CRITICAL
    issue_body: str        # NEW - CRITICAL  
    issue_url: str
    issue_state: str       # NEW
    issue_reason: Optional[str] # NEW
```

**Deliverable**: Working CRUD operations using raw SQL with updated schema

### Task 1.3: Test Schema Alignment ⏳ PENDING
**Goal**: Ensure tests match updated schema

**Actions**:
1. Update test fixtures to match new schema
2. Update test assertions to match new field names
3. Verify all tests pass with raw SQL approach

**Deliverable**: All tests passing with final schema

## Schema Questions to Resolve

1. **Dataset ID**: TEXT vs INTEGER?
   - Current raw SQL uses TEXT 
   - My ORM used INTEGER
   - Decision needed

2. **Field Completeness**: What fields are we missing?
   - Need to analyze existing scripts
   - Check GitHub API capabilities
   - Consider future prompt generation needs

3. **Normalization**: Separate PR/Issue tables vs denormalized?
   - Current: Denormalized (PR data repeated per issue)
   - Pros: Simple queries, matches CSV output
   - Cons: Data duplication
   - Decision: Keep denormalized for now (matches existing pattern)

## Next Steps

1. **Research existing fetch scripts** to identify all required fields
2. **Update schema** in `models/database.py` 
3. **Revert CRUD implementation** to raw SQL
4. **Update tests** to match new schema
5. **Get approval** before moving to Phase 2

## Future Phases (Simplified)

### Phase 2: GitHub Service
- Port existing GraphQL query logic from fetch scripts
- Add API client wrapper
- Handle pagination and rate limits

### Phase 3: API Endpoints  
- Create FastAPI endpoints for data extraction
- Add dataset management endpoints

### Phase 4: Integration
- End-to-end testing with real GitHub data
- Performance optimization

## Key Principle
**Test-first, incremental approach**: Write tests before implementation, small reviewable pieces, maintain working state after each change.

---

## 📅 TOMORROW'S PLAN - Phase 2: GitHub Service

### Ready to Start Phase 2
With Phase 1 complete, we have a solid foundation:
- ✅ Database schema with all required fields (including nullable ones)
- ✅ Working CRUD operations with raw SQL
- ✅ Test infrastructure that supports the new schema
- ✅ Clear understanding of what data we need from GitHub

### Phase 2 Priorities (in order):

#### 2.1: **Services Directory Setup** (5 min)
- Create `services/` directory with `__init__.py`
- Create `services/github_service.py` stub

#### 2.2: **Red Tests First** (20 min)
- Create `tests/test_github_service.py` 
- Write failing tests for enhanced GraphQL query and response parsing
- Include tests for all nullable fields being populated
- Let them be RED until we implement

#### 2.3: **Enhanced GraphQL Query** (30 min)
- Port existing query from `fetch_pr_closing_issues.py`
- **ENHANCE** to get ALL fields in one call:
  - Add `title` to PR query (fills `pr_title`)
  - Add `baseRefName` for base branch (fills `pr_base_branch`)
  - Add `mergeCommit { oid }` for commit SHA (fills `pr_merge_commit_sha`)
  - Add `title`, `body` to issue query (fills `issue_title`, `issue_body`)
- **Eliminates need for separate REST calls!**

#### 2.4: **Service Implementation** (25 min)
- Implement GitHub service functions to make tests GREEN
- Focus on making red tests pass

#### 2.5: **Integration** (30 min)
- Connect GitHub service to CRUD layer
- Test end-to-end data flow with real GitHub data (small repo)

### Key Questions for Tomorrow:
1. **Should we test with a real small repo** - ✅ **YES: PrefectHQ/prefect**
2. **Rate limiting strategy** - ✅ **Start basic, add retries later**
3. **Error handling** - ✅ **Start minimal, improve later**

### Success Criteria for Tomorrow:
- [x] Can extract rich PR-issue data from GitHub in one API call ✅ GraphQL query built
- [x] All nullable fields get populated (no more NULLs) ✅ Enhanced parser includes all fields
- [ ] Data flows from GitHub → Service → CRUD → Database (API client still needed)
- [x] Tests cover the happy path ✅ 4 new tests all passing

**Estimated time: ~2 hours of focused work**

---

## 📅 PHASE 2 PROGRESS UPDATE

### ✅ PHASE 2 COMPLETED (GitHub Service Implementation)

#### ✅ Step 2.1: Services Directory Setup
**Completed:**
- Created `services/` directory with `__init__.py`
- Created `services/github_service.py` with initial stub

#### ✅ Step 2.2: Enhanced GraphQL Query Builder
**Completed:**
- `build_graphql_query()` function that gets ALL fields in one call
- Enhanced query includes fields missing from original script:
  - `pr_title` (was missing from original)
  - `pr_base_branch` (was missing from original) 
  - `pr_merge_commit_sha` (was missing from original)
  - `issue_title` (was missing from original)
  - `issue_body` (was missing from original)
- Supports pagination with cursor-based navigation
- Eliminates need for separate REST API calls

#### ✅ Step 2.3: GraphQL Response Parser  
**Completed:**
- `parse_graphql_response()` function converts API response to database records
- Handles multiple issues per PR (creates separate records)
- Populates all enhanced fields with no nullable values
- Robust error handling for empty responses

#### ✅ Step 2.4: GitHub API Client Implementation
**Completed:**
- `GitHubClient` class with full authentication support
- `execute_graphql_query()` method with error handling and async support
- `fetch_pr_issue_data()` method with automatic pagination
- Environment variable integration for `GITHUB_TOKEN`
- Proper GraphQL error detection and reporting

#### ✅ Step 2.5: Comprehensive Test Coverage
**Completed test suite (8 new tests):**
- `test_build_graphql_query()` - Query construction validation
- `test_parse_graphql_response()` - Single PR-issue parsing  
- `test_parse_graphql_response_multiple_prs()` - Multiple issues per PR
- `test_parse_graphql_response_empty()` - Empty response handling
- `test_github_client_initialization()` - Client setup and authentication
- `test_execute_graphql_query_success()` - Successful API calls with mocking
- `test_execute_graphql_query_error()` - Error handling and GraphQL errors
- `test_fetch_pr_issue_data()` - Full extraction flow with pagination

**Test Infrastructure:**
- Added `pytest-asyncio` dependency for async test support
- Proper mocking of `httpx.AsyncClient` for isolated testing
- All 14 tests passing (5 CRUD + 8 GitHub + 1 health)

#### 🎯 Key Achievements
1. **Enhanced Data Extraction**: Gets 6 additional fields compared to original script
2. **Single API Call**: Eliminates separate REST calls, improving efficiency
3. **Complete Pagination**: Handles repos with 100+ merged PRs automatically  
4. **Robust Error Handling**: GraphQL errors, HTTP errors, and authentication failures
5. **Full Test Coverage**: 8 comprehensive tests covering all scenarios
6. **Ready for Integration**: All components ready to connect with CRUD layer

### 🔄 NEXT: Phase 3 - API Endpoints & Integration
**Ready to implement:**
- FastAPI router for GitHub data extraction endpoints
- Integration between GitHub service and CRUD operations
- End-to-end testing with real GitHub repositories
- Dataset management endpoints

**Immediate next steps:**
1. Create `routers/github.py` with extraction endpoint
2. Connect GitHub service to database via CRUD operations  
3. Test full flow: API call → GitHub → Service → CRUD → Database
4. Add dataset listing and details endpoints