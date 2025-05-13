# src/fetch_gh_data_3/fetch_issues.py

import requests
import os
from typing import List, Dict, Any

def fetch_issues(repo: str, token: str = None, limit: int = 30) -> List[Dict[Any, Any]]:
    """
    Fetch issues from a GitHub repository.
    
    Args:
        repo: Repository name in the format 'owner/repo'
        token: GitHub personal access token (optional)
        limit: Maximum number of issues to return (default: 30)
              Will fetch multiple pages if limit > 100
    
    Returns:
        List of issue dictionaries
    """
    url = f"https://api.github.com/repos/{repo}/issues"
    
    # GitHub API allows max 100 items per page
    per_page = min(limit, 100)
    
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    all_issues = []
    page = 1
    
    # Continue fetching pages until we reach the limit or run out of issues
    while len(all_issues) < limit:
        params = {
            'per_page': per_page,
            'page': page
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        page_issues = response.json()
        
        # If no more issues are returned, we've reached the end
        if not page_issues:
            break
            
        all_issues.extend(page_issues)
        
        # If this page had fewer issues than per_page, there are no more issues
        if len(page_issues) < per_page:
            break
            
        # Move to the next page
        page += 1
    
    # Return only up to the requested limit
    return all_issues[:limit]

def print_github_issues(repo: str, token: str = None, limit: int = 30):
    """
    Fetch and print GitHub issues for a repository.
    
    Args:
        repo: Repository name in the format 'owner/repo'
        token: GitHub personal access token (optional)
    """
    try:
        issues = fetch_issues(repo, token, limit)
        print(f"Found {len(issues)} issues in {repo}")
        
        for issue in issues:
            print(f"#{issue['number']} - {issue['title']} ({issue['state']})")
            
    except Exception as e:
        print(f"Error fetching issues: {e}")

if __name__ == "__main__":
    # Example usage - change these parameters as needed
    repository = "DataDog/datadog-agent"
    # Get GitHub token from environment variable
    github_token = os.environ.get("GITHUB_TOKEN")
    # Limit number of issues to retrieve (default: 30)
    issue_limit = 10
    
    print_github_issues(repository, github_token, issue_limit)
