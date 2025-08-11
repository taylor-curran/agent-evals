# data-ai-service/services/github_service.py

"""GitHub API service for extracting PR-issue data."""
import os
import httpx
from typing import List, Dict, Any, Optional


def build_graphql_query(repo_owner: str, repo_name: str) -> str:
    """Build enhanced GraphQL query to get all PR-issue data in one call.
    
    This query gets all the fields we need, eliminating the need for
    separate REST API calls like the original script required.
    """
    return """
    query($owner: String!, $name: String!, $cursor: String) {
        repository(owner: $owner, name: $name) {
            pullRequests(
                first: 100,
                after: $cursor,
                states: [MERGED],
                orderBy: {field: UPDATED_AT, direction: DESC}
            ) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    number
                    title
                    url
                    mergedAt
                    baseRefName
                    mergeCommit {
                        oid
                    }
                    closingIssuesReferences(first: 10) {
                        nodes {
                            number
                            title
                            body
                            url
                            state
                            stateReason
                        }
                    }
                }
            }
        }
    }
    """


def parse_graphql_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse GraphQL response into PR-issue mapping records.
    
    Each record represents one PR-issue pair, ready for database insertion.
    Multiple issues per PR will create multiple records.
    """
    pr_issues = []
    
    repository = response.get("data", {}).get("repository", {})
    pull_requests = repository.get("pullRequests", {}).get("nodes", [])
    
    for pr in pull_requests:
        pr_number = pr.get("number")
        pr_title = pr.get("title")
        pr_url = pr.get("url")
        pr_merged_at = pr.get("mergedAt")
        pr_base_branch = pr.get("baseRefName")
        pr_merge_commit_sha = pr.get("mergeCommit", {}).get("oid")
        
        # Handle closing issues
        closing_issues = pr.get("closingIssuesReferences", {}).get("nodes", [])
        
        for issue in closing_issues:
            pr_issue_record = {
                "pr_number": pr_number,
                "pr_title": pr_title,
                "pr_url": pr_url,
                "pr_merged_at": pr_merged_at,
                "pr_base_branch": pr_base_branch,
                "pr_merge_commit_sha": pr_merge_commit_sha,
                "issue_number": issue.get("number"),
                "issue_title": issue.get("title"),
                "issue_body": issue.get("body"),
                "issue_url": issue.get("url"),
                "issue_state": issue.get("state"),
                "issue_reason": issue.get("stateReason")
            }
            pr_issues.append(pr_issue_record)
    
    return pr_issues


class GitHubClient:
    """GitHub API client for executing GraphQL queries."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with authentication token."""
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass token parameter.")
        
        self.base_url = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def execute_graphql_query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GraphQL query against GitHub API."""
        payload = {
            "query": query,
            "variables": variables
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Check for GraphQL errors
            if "errors" in result:
                error_messages = [error.get("message", "Unknown error") for error in result["errors"]]
                raise Exception(f"GraphQL errors: {', '.join(error_messages)}")
            
            return result
    
    async def fetch_pr_issue_data(self, repo_owner: str, repo_name: str) -> List[Dict[str, Any]]:
        """Fetch all PR-issue data for a repository."""
        all_pr_issues = []
        cursor = None
        page_count = 0
        
        while True:
            page_count += 1
            query = build_graphql_query(repo_owner, repo_name)
            variables = {
                "owner": repo_owner,
                "name": repo_name,
                "cursor": cursor
            }
            
            response = await self.execute_graphql_query(query, variables)
            pr_issues = parse_graphql_response(response)
            all_pr_issues.extend(pr_issues)
            
            print(f"  Page {page_count}: fetched {len(pr_issues)} PR-issue mappings (total: {len(all_pr_issues)})")
            
            # Check for pagination
            page_info = response.get("data", {}).get("repository", {}).get("pullRequests", {}).get("pageInfo", {})
            if not page_info.get("hasNextPage", False):
                break
                
            cursor = page_info.get("endCursor")
        
        return all_pr_issues