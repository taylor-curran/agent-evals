import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from main import app
from models.database import CREATE_TABLE_STATEMENTS


@pytest.fixture
def test_db():
    """Create a test database for each test."""
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create tables using raw SQL
    with engine.begin() as conn:
        for stmt in CREATE_TABLE_STATEMENTS:
            conn.execute(text(stmt))
    
    yield engine.connect()


@pytest.fixture
def client(test_db):
    """Create a test client with the test database."""
    from routers.github import get_db
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_dataset_data():
    """Sample dataset data for testing."""
    return {
        "repo_name": "test-owner/test-repo",
        "repo_url": "https://github.com/test-owner/test-repo",
        "total_pr_issues": 5
    }


@pytest.fixture
def sample_pr_issue_data():
    """Sample PR-issue mapping data for testing."""
    return [
        {
            "pr_number": 123,
            "pr_title": "Fix critical bug",
            "pr_url": "https://github.com/test-owner/test-repo/pull/123",
            "pr_merged_at": "2024-01-15T10:30:00Z",
            "pr_base_branch": "main",
            "pr_merge_commit_sha": "abc123def456",
            "issue_number": 100,
            "issue_title": "Application crashes on startup",
            "issue_body": "When starting the app, it immediately crashes with segfault.",
            "issue_url": "https://github.com/test-owner/test-repo/issues/100",
            "issue_state": "closed",
            "issue_reason": "completed"
        },
        {
            "pr_number": 124,
            "pr_title": "Add new feature",
            "pr_url": "https://github.com/test-owner/test-repo/pull/124",
            "pr_merged_at": "2024-01-16T14:20:00Z",
            "pr_base_branch": "main", 
            "pr_merge_commit_sha": "def456ghi789",
            "issue_number": 101,
            "issue_title": "Users need export functionality",
            "issue_body": "Please add ability to export data to CSV format.",
            "issue_url": "https://github.com/test-owner/test-repo/issues/101",
            "issue_state": "closed",
            "issue_reason": "completed"
        }
    ]


@pytest.fixture
def mock_github_token(monkeypatch):
    """Mock GitHub token environment variable."""
    monkeypatch.setenv("GITHUB_TOKEN", "mock-github-token-123")
    return "mock-github-token-123"