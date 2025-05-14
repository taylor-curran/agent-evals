# src/fetch_gh_data/fetch_issues.py

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from prefect import flow

from helper import (
    fetch_issue_page,
    convert_and_process,
)


@flow
def fetch_issues(
    repo: str,
    token: Optional[str] = None,
    limit: int = 30,
    max_pages: int = 20,
) -> List[Dict[Any, Any]]:
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

    # Prepare headers for authentication if token is provided
    headers = {
        "Accept": "application/vnd.github.v3+json"  # Explicitly request v3 API
    }
    if token:
        headers["Authorization"] = f"token {token}"

    all_issues = []

    # Continue fetching pages until we reach the limit, max pages, or run out of issues
    for page in range(1, max_pages + 1):
        if len(all_issues) >= limit:
            break

        page_url = f"{url}?per_page={per_page}&page={page}&state=all&sort=created&direction=desc"

        try:
            # Fetch this page via the dedicated task (handles its own retries)
            page_issues = fetch_issue_page.submit(page_url, headers)
            page_issues_raw = page_issues.result()
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            raise

        # If no more issues are returned, we've reached the end
        if not page_issues_raw:
            break

        # Always exclude pull requests from results
        page_issues = [
            issue for issue in page_issues_raw if "pull_request" not in issue
        ]

        all_issues.extend(page_issues)

        # If the page contained fewer items than requested, we've reached the last page
        if len(page_issues_raw) < per_page:
            break

    # Return only up to the requested limit
    return all_issues[:limit]


@flow(
    name="Fetch GitHub Issues",
    description="Fetch issues from a GitHub repository with automatic retries",
)
def fetch_gh_issues(
    repository: str,
    limit: int = 100,
    max_pages: int = 20,
    token: Optional[str] = None,
    show_urls: bool = True,
) -> pd.DataFrame:
    """
    Main function to fetch GitHub issues and return them as a DataFrame.

    Args:
        repository: Repository name in the format 'owner/repo'
        limit: Maximum number of issues to return (default: 100)
        max_pages: Maximum number of pages to fetch (default: 20)
        token: GitHub personal access token (optional). If omitted, the function falls back to the GITHUB_TOKEN environment variable.
        show_urls: Whether to print issue URLs (default: True)

    Returns:
        pandas DataFrame containing the issues
    """
    # If token is not provided or empty, try to get it from environment variable
    if not token:
        env_token = os.environ.get("GITHUB_TOKEN", "")
        token = env_token if env_token else ""

    try:
        # Fetch issues via the page-level retry mechanism
        # Always exclude pull requests
        issues = fetch_issues(repository, token, limit, max_pages)
        print(f"Found {len(issues)} issues in {repository}")
        # Convert to DataFrame using a separate task
        df = convert_and_process(issues, show_urls)

        # Save data to CSV file with sanitized repository name
        sanitized_repo = (
            repository.replace("/", "_").replace("-", "_").replace(".", "_")
        )
        df.to_csv(f"{sanitized_repo}_issues.csv", index=False)

        print(f"Saved {len(issues)} issues to {sanitized_repo}_issues.csv")

        return df

    except Exception as e:
        print(f"Error in flow execution: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    repository = "PrefectHQ/prefect"  # or DataDog/datadog-agent
    limit = 200

    # Fetch issues and save as DataFrame
    issues_df = fetch_gh_issues(
        repository=repository,
        limit=limit,
        max_pages=20,
        show_urls=True,
    )
