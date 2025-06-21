# GitHub Integration Migration Plan

## Overview

This document outlines the plan for migrating the existing GitHub data extraction functionality from standalone scripts into the Data+AI Service microservice architecture. This is the next critical step in building the agent evaluation platform.

**Approach**: Test-first, incremental implementation with small, reviewable pieces.

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

### Phase 1: Foundation & Test Infrastructure

#### Step 1.1: Test Infrastructure Setup
**Files to create**:
```
tests/
├── conftest.py              # Shared fixtures
├── test_github_service.py   # GitHub service tests
├── test_github_router.py    # GitHub endpoint tests
└── fixtures/               
    ├── github_responses.py  # Mock GraphQL/REST responses
    └── sample_data.py       # Test data
```

**Key test fixtures**:
- Mock GitHub GraphQL responses
- Mock GitHub REST API responses  
- Test database with sample data
- FastAPI test client

#### Step 1.2: Database CRUD Tests First
**Create `tests/test_crud.py`**:
```python
def test_create_dataset():
    """Test creating a new dataset entry"""

def test_save_pr_issues():
    """Test bulk inserting PR-issue mappings"""

def test_get_datasets():
    """Test listing all datasets"""

def test_get_dataset_details():
    """Test fetching full dataset with PR-issues"""
```

**Then implement `database/crud.py`** with minimal code to pass tests.

### Phase 2: GitHub Service - Incremental Pieces

#### Step 2.1: GraphQL Query Builder
**Test first** (`tests/test_github_service.py`):
```python
def test_build_graphql_query():
    """Test GraphQL query construction"""

def test_parse_graphql_response():
    """Test parsing PR-issue mappings from response"""
```

**Then implement** in `services/github_service.py`:
- Just the query building logic
- Response parsing logic
- No actual API calls yet

#### Step 2.2: GitHub API Client Wrapper
**Test first**:
```python
def test_github_client_initialization():
    """Test client setup with token"""

def test_execute_graphql_query_mocked():
    """Test GraphQL execution with mocked responses"""
```

**Then implement**:
- Basic GitHub client class
- GraphQL execution method
- Use httpx for async support

#### Step 2.3: Core Extraction Logic
**Test first**:
```python
def test_fetch_pr_issue_mapping():
    """Test full extraction flow with mocks"""

def test_pagination_handling():
    """Test handling multiple pages of results"""
```

**Then implement**:
- Port logic from `fetch_pr_closing_issues.py`
- Keep same data structures
- Add async/await

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

1. **Day 1**: Test infrastructure + Database CRUD
2. **Day 2**: GitHub GraphQL query builder + parser
3. **Day 3**: GitHub API client + core extraction
4. **Day 4**: First API endpoint (extract-data)
5. **Day 5**: Remaining endpoints + integration tests

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

1. **Functional Parity**: All existing script functionality works via API
2. **Data Integrity**: Same PR-issue mappings extracted
3. **Performance**: API responds within 2 seconds for most operations
4. **Reliability**: Proper error handling for API failures
5. **Testability**: >80% code coverage with tests

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