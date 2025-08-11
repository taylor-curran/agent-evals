"""Tests for GitHub service functionality."""
import pytest
import httpx
from unittest.mock import patch, AsyncMock, Mock
from services.github_service import build_graphql_query, parse_graphql_response, GitHubClient


def test_build_graphql_query():
    """Test GraphQL query construction for enhanced PR-issue data."""
    query = build_graphql_query(repo_owner="PrefectHQ", repo_name="prefect")
    
    # Query should include all required fields
    assert "query" in query
    assert "repository" in query
    assert "pullRequests" in query
    assert "closingIssuesReferences" in query
    
    # Enhanced PR fields (not in original script)
    assert "title" in query  # pr_title
    assert "baseRefName" in query  # pr_base_branch
    assert "mergeCommit" in query  # pr_merge_commit_sha
    
    # Enhanced Issue fields (not in original script)
    assert "body" in query  # issue_body
    
    # Original fields should still be there
    assert "number" in query
    assert "url" in query
    assert "mergedAt" in query
    assert "state" in query
    assert "stateReason" in query


def test_parse_graphql_response():
    """Test parsing PR-issue mappings from GraphQL response."""
    mock_response = {
        "data": {
            "repository": {
                "pullRequests": {
                    "nodes": [
                        {
                            "number": 123,
                            "title": "Fix critical bug",
                            "url": "https://github.com/PrefectHQ/prefect/pull/123",
                            "mergedAt": "2024-01-15T10:30:00Z",
                            "baseRefName": "main",
                            "mergeCommit": {
                                "oid": "abc123def456"
                            },
                            "closingIssuesReferences": {
                                "nodes": [
                                    {
                                        "number": 100,
                                        "title": "Application crashes on startup",
                                        "body": "When starting the app, it immediately crashes with segfault.",
                                        "url": "https://github.com/PrefectHQ/prefect/issues/100",
                                        "state": "CLOSED",
                                        "stateReason": "COMPLETED"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
    
    pr_issues = parse_graphql_response(mock_response)
    
    assert len(pr_issues) == 1
    pr_issue = pr_issues[0]
    
    # PR fields
    assert pr_issue["pr_number"] == 123
    assert pr_issue["pr_title"] == "Fix critical bug"
    assert pr_issue["pr_url"] == "https://github.com/PrefectHQ/prefect/pull/123"
    assert pr_issue["pr_merged_at"] == "2024-01-15T10:30:00Z"
    assert pr_issue["pr_base_branch"] == "main"
    assert pr_issue["pr_merge_commit_sha"] == "abc123def456"
    
    # Issue fields
    assert pr_issue["issue_number"] == 100
    assert pr_issue["issue_title"] == "Application crashes on startup"
    assert pr_issue["issue_body"] == "When starting the app, it immediately crashes with segfault."
    assert pr_issue["issue_url"] == "https://github.com/PrefectHQ/prefect/issues/100"
    assert pr_issue["issue_state"] == "CLOSED"
    assert pr_issue["issue_reason"] == "COMPLETED"


def test_parse_graphql_response_multiple_prs():
    """Test parsing response with multiple PRs and issues."""
    mock_response = {
        "data": {
            "repository": {
                "pullRequests": {
                    "nodes": [
                        {
                            "number": 123,
                            "title": "Fix bug",
                            "url": "https://github.com/PrefectHQ/prefect/pull/123",
                            "mergedAt": "2024-01-15T10:30:00Z",
                            "baseRefName": "main",
                            "mergeCommit": {"oid": "abc123"},
                            "closingIssuesReferences": {
                                "nodes": [
                                    {
                                        "number": 100,
                                        "title": "Bug title",
                                        "body": "Bug description",
                                        "url": "https://github.com/PrefectHQ/prefect/issues/100",
                                        "state": "CLOSED",
                                        "stateReason": "COMPLETED"
                                    },
                                    {
                                        "number": 101,
                                        "title": "Another bug",
                                        "body": "Another description",
                                        "url": "https://github.com/PrefectHQ/prefect/issues/101",
                                        "state": "CLOSED",
                                        "stateReason": "COMPLETED"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
    
    pr_issues = parse_graphql_response(mock_response)
    
    # Should have 2 PR-issue mappings (1 PR with 2 issues)
    assert len(pr_issues) == 2
    assert pr_issues[0]["issue_number"] == 100
    assert pr_issues[1]["issue_number"] == 101
    # Both should have same PR data
    assert pr_issues[0]["pr_number"] == pr_issues[1]["pr_number"] == 123


def test_parse_graphql_response_empty():
    """Test parsing empty response."""
    mock_response = {
        "data": {
            "repository": {
                "pullRequests": {
                    "nodes": []
                }
            }
        }
    }
    
    pr_issues = parse_graphql_response(mock_response)
    assert pr_issues == []


def test_parse_graphql_response_pr_without_issues():
    """Test parsing PR that doesn't close any issues."""
    mock_response = {
        "data": {
            "repository": {
                "pullRequests": {
                    "nodes": [
                        {
                            "number": 456,
                            "title": "Refactor code structure",
                            "url": "https://github.com/PrefectHQ/prefect/pull/456",
                            "mergedAt": "2024-02-01T14:00:00Z",
                            "baseRefName": "develop",
                            "mergeCommit": {
                                "oid": "xyz789"
                            },
                            "closingIssuesReferences": {
                                "nodes": []
                            }
                        }
                    ]
                }
            }
        }
    }
    
    pr_issues = parse_graphql_response(mock_response)
    assert pr_issues == []  # No issues linked, so no records created


def test_parse_graphql_response_malformed():
    """Test parsing malformed response."""
    # Missing data key
    assert parse_graphql_response({}) == []
    
    # Missing repository key
    assert parse_graphql_response({"data": {}}) == []
    
    # Missing pullRequests key
    assert parse_graphql_response({"data": {"repository": {}}}) == []
    
    # Missing nodes key
    assert parse_graphql_response({"data": {"repository": {"pullRequests": {}}}}) == []


# GitHub API Client Tests

def test_github_client_initialization():
    """Test GitHub client setup with token."""
    client = GitHubClient(token="test-token")
    assert client.token == "test-token"
    assert client.base_url == "https://api.github.com/graphql"
    assert "Authorization" in client.headers
    assert client.headers["Authorization"] == "Bearer test-token"


def test_github_client_initialization_no_token():
    """Test GitHub client initialization without token raises error."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            GitHubClient()
        assert "GitHub token is required" in str(exc_info.value)


def test_github_client_initialization_env_token():
    """Test GitHub client uses environment variable when no token provided."""
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'env-test-token'}):
        client = GitHubClient()
        assert client.token == "env-test-token"
        assert client.headers["Authorization"] == "Bearer env-test-token"


@pytest.mark.asyncio
async def test_execute_graphql_query_success():
    """Test successful GraphQL query execution."""
    mock_response_data = {
        "data": {
            "repository": {
                "pullRequests": {
                    "nodes": [
                        {
                            "number": 123,
                            "title": "Test PR",
                            "url": "https://github.com/test/repo/pull/123",
                            "mergedAt": "2024-01-15T10:30:00Z",
                            "baseRefName": "main",
                            "mergeCommit": {"oid": "abc123"},
                            "closingIssuesReferences": {
                                "nodes": [
                                    {
                                        "number": 100,
                                        "title": "Test Issue",
                                        "body": "Test description",
                                        "url": "https://github.com/test/repo/issues/100",
                                        "state": "CLOSED",
                                        "stateReason": "COMPLETED"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        
        client = GitHubClient(token="test-token")
        query = build_graphql_query("PrefectHQ", "prefect")
        variables = {"owner": "PrefectHQ", "name": "prefect", "cursor": None}
        
        result = await client.execute_graphql_query(query, variables)
        
        assert result == mock_response_data
        mock_client.post.assert_called_once()


@pytest.mark.asyncio 
async def test_execute_graphql_query_error():
    """Test GraphQL query execution with error response."""
    mock_error_response = {
        "errors": [
            {
                "message": "Repository not found",
                "type": "NOT_FOUND"
            }
        ]
    }
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = mock_error_response
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        
        client = GitHubClient(token="test-token")
        query = build_graphql_query("nonexistent", "repo")
        variables = {"owner": "nonexistent", "name": "repo", "cursor": None}
        
        with pytest.raises(Exception) as exc_info:
            await client.execute_graphql_query(query, variables)
        
        assert "Repository not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_execute_graphql_query_http_error():
    """Test GraphQL query execution with HTTP error."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Create a mock response that raises on raise_for_status
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=Mock(), response=Mock(status_code=401)
        )
        mock_client.post.return_value = mock_response
        
        client = GitHubClient(token="invalid-token")
        query = build_graphql_query("test", "repo")
        variables = {"owner": "test", "name": "repo", "cursor": None}
        
        with pytest.raises(httpx.HTTPStatusError):
            await client.execute_graphql_query(query, variables)


@pytest.mark.asyncio
async def test_fetch_pr_issue_data():
    """Test full extraction flow with mocked API response."""
    mock_response = {
        "data": {
            "repository": {
                "pullRequests": {
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None
                    },
                    "nodes": [
                        {
                            "number": 123,
                            "title": "Fix bug",
                            "url": "https://github.com/test/repo/pull/123",
                            "mergedAt": "2024-01-15T10:30:00Z",
                            "baseRefName": "main",
                            "mergeCommit": {"oid": "abc123"},
                            "closingIssuesReferences": {
                                "nodes": [
                                    {
                                        "number": 100,
                                        "title": "Bug report",
                                        "body": "There is a bug",
                                        "url": "https://github.com/test/repo/issues/100",
                                        "state": "CLOSED",
                                        "stateReason": "COMPLETED"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response_obj = Mock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response_obj
        
        client = GitHubClient(token="test-token")
        pr_issues = await client.fetch_pr_issue_data("PrefectHQ", "prefect")
        
        assert len(pr_issues) == 1
        assert pr_issues[0]["pr_number"] == 123
        assert pr_issues[0]["issue_number"] == 100
        assert pr_issues[0]["pr_title"] == "Fix bug"
        assert pr_issues[0]["issue_title"] == "Bug report"


@pytest.mark.asyncio
async def test_fetch_pr_issue_data_pagination():
    """Test pagination handling across multiple pages."""
    # First page response
    mock_response_page1 = {
        "data": {
            "repository": {
                "pullRequests": {
                    "pageInfo": {
                        "hasNextPage": True,
                        "endCursor": "cursor123"
                    },
                    "nodes": [
                        {
                            "number": 1,
                            "title": "First PR",
                            "url": "https://github.com/test/repo/pull/1",
                            "mergedAt": "2024-01-01T00:00:00Z",
                            "baseRefName": "main",
                            "mergeCommit": {"oid": "abc1"},
                            "closingIssuesReferences": {
                                "nodes": [{
                                    "number": 10,
                                    "title": "Issue 10",
                                    "body": "Body 10",
                                    "url": "https://github.com/test/repo/issues/10",
                                    "state": "CLOSED",
                                    "stateReason": "COMPLETED"
                                }]
                            }
                        }
                    ]
                }
            }
        }
    }
    
    # Second page response
    mock_response_page2 = {
        "data": {
            "repository": {
                "pullRequests": {
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None
                    },
                    "nodes": [
                        {
                            "number": 2,
                            "title": "Second PR",
                            "url": "https://github.com/test/repo/pull/2",
                            "mergedAt": "2024-01-02T00:00:00Z",
                            "baseRefName": "main",
                            "mergeCommit": {"oid": "abc2"},
                            "closingIssuesReferences": {
                                "nodes": [{
                                    "number": 20,
                                    "title": "Issue 20",
                                    "body": "Body 20",
                                    "url": "https://github.com/test/repo/issues/20",
                                    "state": "CLOSED",
                                    "stateReason": "COMPLETED"
                                }]
                            }
                        }
                    ]
                }
            }
        }
    }
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Set up responses for two pages
        mock_response_obj1 = Mock()
        mock_response_obj1.json.return_value = mock_response_page1
        mock_response_obj1.raise_for_status.return_value = None
        
        mock_response_obj2 = Mock()
        mock_response_obj2.json.return_value = mock_response_page2
        mock_response_obj2.raise_for_status.return_value = None
        
        mock_client.post.side_effect = [mock_response_obj1, mock_response_obj2]
        
        client = GitHubClient(token="test-token")
        pr_issues = await client.fetch_pr_issue_data("test", "repo")
        
        # Should have combined results from both pages
        assert len(pr_issues) == 2
        assert pr_issues[0]["pr_number"] == 1
        assert pr_issues[0]["issue_number"] == 10
        assert pr_issues[1]["pr_number"] == 2
        assert pr_issues[1]["issue_number"] == 20
        
        # Verify API was called twice (once for each page)
        assert mock_client.post.call_count == 2