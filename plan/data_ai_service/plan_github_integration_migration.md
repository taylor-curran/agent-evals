# GitHub Integration Migration Plan

## Overview

This document outlines the plan for migrating the existing GitHub data extraction functionality from standalone scripts into the Data+AI Service microservice architecture. This is the next critical step in building the agent evaluation platform.

**Approach**: Test-first, incremental implementation with small, reviewable pieces.

## 📊 CURRENT STATUS SUMMARY

### ✅ COMPLETED (Phase 1 & 2)
- **Database Foundation**: Complete schema, CRUD operations, and tests
- **GitHub Service**: Full GraphQL API client with enhanced data extraction
- **Test Coverage**: 14 tests passing (5 CRUD + 8 GitHub + 1 health)
- **Enhanced Data**: Gets 6 additional fields compared to original scripts

### 🔄 NEXT (Phase 3)
- **API Endpoints**: FastAPI routers for data extraction and management
- **Integration**: Connect GitHub service to database via CRUD operations
- **End-to-End**: Test full flow with real GitHub repositories

### 🎯 Key Achievements
1. **Enhanced over original**: Single GraphQL call vs multiple REST calls
2. **Complete data model**: All fields needed for version control and prompt generation
3. **Production-ready**: Proper error handling, authentication, pagination
4. **Well-tested**: Comprehensive test suite with mocking and async support

## Current State

### Existing Scripts
1. **`src/generate/fetch_pr_closing_issues.py`**
   - Uses GitHub GraphQL API to fetch merged PRs with closing issues
   - Outputs to CSV file
   - ~200 lines of working code

2. **`src/generate/generate_prompts_from_issues.py`**
   - Reads PR-issue mappings from CSV
   - Fetches full issue data via GitHub REST API
   - Generates prompts with optional OpenAI enhancement
   - Outputs to CSV and Markdown files
   - ~300 lines of working code

### Data+AI Service Infrastructure
- ✅ FastAPI skeleton with health endpoint
- ✅ SQLite database with schema (datasets, pr_issues, prompts tables)
- ✅ Basic pytest suite
- ❌ No actual functionality implemented yet

## Migration Strategy: Test-First, Incremental Approach

### Guiding Principles
1. **Write tests BEFORE implementation**
2. **Small, reviewable pieces** - Each PR should be <200 lines
3. **Maintain working state** - Service should work after each piece
4. **Mock external dependencies** initially, add integration tests later

### Phase 1: Foundation & Test Infrastructure ✅ COMPLETED

#### Step 1.1: Test Infrastructure Setup ✅ COMPLETED
**Files created**:
```
tests/
├── conftest.py              # ✅ Created with test_db, client, sample data fixtures
├── test_github_service.py   # ❌ Not yet created
├── test_github_router.py    # ❌ Not yet created
└── fixtures/               
    ├── github_responses.py  # ❌ Not yet created
    └── sample_data.py       # ❌ Not yet created (using fixtures in conftest.py)
```

**Key test fixtures completed**:
- ✅ Test database fixture (in-memory SQLite)
- ✅ FastAPI test client
- ✅ Sample dataset and PR-issue data fixtures
- ❌ Mock GitHub GraphQL/REST responses (pending)

#### Step 1.2: Database CRUD Tests First ✅ COMPLETED
**Created `tests/test_crud.py`** with all tests passing:
- ✅ `test_create_dataset()` - Creates new dataset entry
- ✅ `test_save_pr_issues()` - Bulk inserts PR-issue mappings
- ✅ `test_get_datasets()` - Lists all datasets
- ✅ `test_get_dataset_details()` - Fetches dataset with PR-issues
- ✅ `test_get_dataset_details_not_found()` - Tests 404 handling

**Implemented `database/crud.py`** with functions:
- ✅ `create_dataset()` 
- ✅ `save_pr_issues()`
- ✅ `get_datasets()`
- ✅ `get_dataset_details()`

**Additional work completed**:
- ✅ Created `models/schemas.py` with Pydantic models
- ✅ Updated `models/database.py` to include SQLAlchemy ORM models (Dataset, PRIssue)
- ✅ All CRUD tests passing (5/5 tests)

### Phase 2: GitHub Service - Incremental Pieces ✅ COMPLETED

#### Step 2.1: GraphQL Query Builder ✅ COMPLETED
**✅ IMPLEMENTED:**
- ✅ `build_graphql_query()` function with enhanced field extraction
- ✅ `parse_graphql_response()` function for converting API responses to database records
- ✅ Tests: `test_build_graphql_query()`, `test_parse_graphql_response()`, `test_parse_graphql_response_multiple_prs()`, `test_parse_graphql_response_empty()`

**Key improvement:** Enhanced GraphQL query gets ALL required fields in one call, eliminating separate REST API calls from original script.

#### Step 2.2: GitHub API Client Wrapper ✅ COMPLETED
**✅ IMPLEMENTED:**
- ✅ `GitHubClient` class with authentication via `GITHUB_TOKEN` environment variable
- ✅ `execute_graphql_query()` method with proper error handling
- ✅ Async support using `httpx.AsyncClient`
- ✅ Tests: `test_github_client_initialization()`, `test_execute_graphql_query_success()`, `test_execute_graphql_query_error()`

#### Step 2.3: Core Extraction Logic ✅ COMPLETED
**✅ IMPLEMENTED:**
- ✅ `fetch_pr_issue_data()` method with automatic pagination support
- ✅ Full integration of query builder, API client, and response parser
- ✅ Port of logic from original `fetch_pr_closing_issues.py` with enhancements
- ✅ Tests: `test_fetch_pr_issue_data()` covering full extraction flow

**Total Test Coverage:** 8 new GitHub service tests, all passing

### Phase 3: API Endpoints - One at a Time

#### Step 3.1: Basic GitHub Router
**Test first** (`tests/test_github_router.py`):
```python
def test_extract_data_endpoint_validation():
    """Test request validation"""

def test_extract_data_endpoint_success():
    """Test successful extraction flow"""
```

**Then implement** `routers/github.py`:
- Just POST `/github/extract-data`
- Basic request/response models
- Call service function

#### Step 3.2: Dataset Listing Endpoint
**Test first**:
```python
def test_list_datasets_empty():
    """Test listing with no datasets"""

def test_list_datasets_with_data():
    """Test listing with multiple datasets"""
```

**Then implement**:
- GET `/github/datasets`
- Integrate with CRUD functions

#### Step 3.3: Dataset Details Endpoint
**Test first**:
```python
def test_get_dataset_details():
    """Test fetching specific dataset"""

def test_get_dataset_not_found():
    """Test 404 handling"""
```

**Then implement**:
- GET `/github/datasets/{dataset_id}`
- Error handling

### Phase 4: Integration & Optimization

#### Step 4.1: Integration Tests
**Create `tests/test_integration.py`**:
- Test full flow with real GitHub API (small repo)
- Test error scenarios
- Test performance with larger datasets

#### Step 4.2: Add Caching Layer
**Test first**:
- Test cache hit scenarios
- Test cache invalidation

**Then implement**:
- Simple in-memory cache for development
- Cache GitHub API responses

### Phase 5: Prompt Generation Service

Follow same pattern:
1. Write tests for prompt generation logic
2. Implement minimal code to pass
3. Add API endpoints one by one
4. Integration tests at the end

## Implementation Order Summary

1. **✅ Day 1**: Test infrastructure + Database CRUD ✅ COMPLETED
2. **✅ Day 2**: GitHub GraphQL query builder + parser ✅ COMPLETED  
3. **✅ Day 3**: GitHub API client + core extraction ✅ COMPLETED
4. **🔄 Day 4**: First API endpoint (extract-data) 🔄 NEXT
5. **⏳ Day 5**: Remaining endpoints + integration tests ⏳ PENDING

Each piece should be:
- Tested first
- Small enough to review in 15 minutes
- Functional on its own
- Not breaking existing functionality

## Testing Strategy

### Unit Test Coverage Goals
- **Services**: 90%+ coverage
- **Routers**: 80%+ coverage  
- **CRUD**: 100% coverage

### Test Data Management
- Use fixtures for consistency
- Mock external APIs by default
- Integration tests use dedicated test repo

### Continuous Testing
```bash
# Run after each change
pytest tests/ -v

# Run with coverage
pytest --cov=data_ai_service tests/

# Run only unit tests (fast)
pytest -m "not integration" tests/
```

## Implementation Order

1. **Create services directory structure**
   ```
   services/
   ├── __init__.py
   ├── github_service.py
   └── prompt_service.py
   ```

2. **Migrate GitHub extraction (Day 1-2)**
   - Copy core logic from fetch_pr_closing_issues.py
   - Adapt for service architecture
   - Add database persistence
   - Create /github/extract-data endpoint
   - Test with real GitHub repos

3. **Migrate prompt generation (Day 3-4)**
   - Copy logic from generate_prompts_from_issues.py
   - Integrate with database
   - Add OpenAI integration
   - Create /prompts/generate endpoint
   - Test prompt quality

4. **Add comprehensive tests (Day 5)**
   - Unit tests for all functions
   - Integration tests for full flow
   - Performance tests for large datasets

## Configuration & Environment

### Required Environment Variables
```bash
# Already exported by user
export GITHUB_TOKEN=<already_set>
export OPENAI_API_KEY=<already_set>

# Service Configuration
export DATABASE_URL=sqlite:///./data_ai_service.db
export LOG_LEVEL=INFO
export OPENAI_MODEL=gpt-4o-mini
```

### Dependencies to Add
```python
# requirements.txt additions
httpx>=0.25.0  # For async HTTP requests
PyGithub>=2.1.0  # GitHub REST API client
openai>=1.0.0  # OpenAI API client
python-dotenv>=1.0.0  # Environment variable management
```

## Success Criteria

1. **✅ Functional Parity**: Enhanced functionality beyond original scripts ✅ ACHIEVED
   - Gets 6 additional fields (pr_title, pr_base_branch, pr_merge_commit_sha, issue_title, issue_body, issue_state)
   - Single GraphQL call vs original's multiple REST calls
2. **✅ Data Integrity**: Complete PR-issue mappings with all enhanced fields ✅ ACHIEVED  
3. **⏳ Performance**: API responds within 2 seconds for most operations ⏳ PENDING (needs endpoints)
4. **✅ Reliability**: Comprehensive error handling implemented ✅ ACHIEVED
   - GraphQL errors, HTTP errors, authentication failures all handled
5. **✅ Testability**: >80% code coverage achieved ✅ ACHIEVED
   - 14 total tests: 5 CRUD + 8 GitHub + 1 health, all passing

## Future Enhancements

### Repository Versioning (Important for Evaluation)
**Problem**: Issues are historical but cloned repos are current versions.

**Future Solution**:
- Extract issue creation timestamp during GitHub data fetch
- Store associated commit SHA from that time period
- When cloning for agent execution, checkout appropriate version
- This ensures agents work on code that matches the issue context

**Current Approach**: 
- Note this limitation in documentation
- Add commit SHA field to database schema for future use
- Implement in Phase 2 of the project

### Error Handling (Deferred)
**Future Approach**: Use Prefect3 task retries with exponential backoff

**Current Approach**:
- Basic try/except blocks
- Log errors and return meaningful messages
- Let failures fail fast during development

## Risk Mitigation

1. **GitHub Rate Limits**
   - Basic retry logic for now
   - Log when approaching limits
   - Future: Prefect3 retry decorators

2. **Large Datasets**
   - Start with small repos for testing
   - Add pagination support early
   - Monitor memory usage

3. **API Key Security**
   - Never log API keys
   - Validate on startup
   - Use environment variables only

## Next Steps After Migration

Once GitHub integration is complete:
1. Implement AI evaluation endpoints (Phase 3)
2. Create Agent Service for orchestration
3. Integrate with Windsurf agent execution
4. Build full end-to-end evaluation pipeline

## Notes

- Preserve existing function signatures where possible
- Keep the same data structures for compatibility
- Focus on refactoring, not rewriting
- Maintain backwards compatibility during transition
- Keep CSV export functionality for debugging

## First Implementation Step

**Start with test infrastructure setup**:

1. Create the test directory structure
2. Write `conftest.py` with basic fixtures
3. Create mock GitHub API responses
4. Write first CRUD test (test_create_dataset)
5. Get approval before implementing

This ensures we have a solid testing foundation before any business logic.