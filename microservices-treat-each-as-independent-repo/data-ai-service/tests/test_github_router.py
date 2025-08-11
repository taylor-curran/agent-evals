# data-ai-service/tests/test_github_router.py

"""Tests for GitHub API router endpoints."""
import pytest
from unittest.mock import AsyncMock, patch


def test_extract_endpoint_validation(client):
    """Test request validation for extract endpoint."""
    # Missing required fields
    response = client.post("/github/extract", json={})
    assert response.status_code == 422
    
    # Invalid repo URL
    response = client.post("/github/extract", json={
        "repo_url": "not-a-url"
    })
    assert response.status_code == 422
    
    # Valid request
    with patch('routers.github.GitHubClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        mock_instance.fetch_pr_issue_data.return_value = []
        
        response = client.post("/github/extract", json={
            "repo_url": "https://github.com/test-owner/test-repo"
        })
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_extract_endpoint_success(client, mock_github_token):
    """Test successful data extraction via endpoint."""
    mock_pr_issues = [
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
        }
    ]
    
    with patch('routers.github.GitHubClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.fetch_pr_issue_data.return_value = mock_pr_issues
        
        response = client.post("/github/extract", json={
            "repo_url": "https://github.com/test-owner/test-repo"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["dataset_id"] is not None
        assert data["pr_issues_count"] == 1
        assert data["repo_url"] == "https://github.com/test-owner/test-repo"


@pytest.mark.asyncio
async def test_extract_endpoint_github_error(client, mock_github_token):
    """Test endpoint handling of GitHub API errors."""
    with patch('routers.github.GitHubClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.fetch_pr_issue_data.side_effect = Exception("GitHub API error: Repository not found")
        
        response = client.post("/github/extract", json={
            "repo_url": "https://github.com/nonexistent/repo"
        })
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Repository not found" in data["detail"]


def test_list_datasets_empty(client):
    """Test listing datasets when none exist."""
    response = client.get("/github/datasets")
    
    assert response.status_code == 200
    data = response.json()
    assert data["datasets"] == []
    assert data["total"] == 0


def test_list_datasets_with_data(client, test_db):
    """Test listing datasets with existing data."""
    # Create test datasets using CRUD
    from database import crud
    
    dataset1 = crud.create_dataset(
        test_db,
        repo_name="test-owner/repo1",
        repo_url="https://github.com/test-owner/repo1",
        total_pr_issues=5
    )
    
    dataset2 = crud.create_dataset(
        test_db,
        repo_name="test-owner/repo2", 
        repo_url="https://github.com/test-owner/repo2",
        total_pr_issues=10
    )
    
    response = client.get("/github/datasets")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["datasets"]) == 2
    # Check both datasets are present (order may vary due to same timestamp)
    repo_urls = [d["repo_url"] for d in data["datasets"]]
    assert "https://github.com/test-owner/repo1" in repo_urls
    assert "https://github.com/test-owner/repo2" in repo_urls


def test_list_datasets_pagination(client):
    """Test dataset listing with pagination."""
    response = client.get("/github/datasets?skip=10&limit=5")
    
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert data["skip"] == 10
    assert data["limit"] == 5


def test_get_dataset_details(client, test_db, sample_dataset_data, sample_pr_issue_data):
    """Test fetching specific dataset with PR-issues."""
    from database import crud
    
    # Create dataset with PR-issues
    dataset = crud.create_dataset(
        test_db,
        repo_name=sample_dataset_data["repo_name"],
        repo_url=sample_dataset_data["repo_url"],
        total_pr_issues=len(sample_pr_issue_data)
    )
    
    crud.save_pr_issues(
        test_db,
        dataset_id=dataset["id"],
        pr_issues_data=sample_pr_issue_data
    )
    
    response = client.get(f"/github/datasets/{dataset['id']}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == dataset["id"]
    assert data["repo_url"] == sample_dataset_data["repo_url"]
    assert len(data["pr_issues"]) == 2
    assert data["pr_issues"][0]["pr_number"] == 123
    assert data["pr_issues"][1]["pr_number"] == 124


def test_get_dataset_not_found(client):
    """Test fetching non-existent dataset."""
    response = client.get("/github/datasets/nonexistent-id")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()