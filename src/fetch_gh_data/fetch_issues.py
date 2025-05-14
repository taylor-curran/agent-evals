# src/fetch_gh_data_3/fetch_issues.py

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from prefect import flow

# import helper utilities
from helper import (
    fetch_issue_page,
    convert_and_process,
)


@flow
def fetch_issues(
    repo: str,
    token: Optional[str] = None,
    limit: int = 30,
    exclude_pulls: bool = False,
    max_pages: int = 20,
) -> List[Dict[Any, Any]]:
    """
    Fetch issues from a GitHub repository.

    Args:
        repo: Repository name in the format 'owner/repo'
        token: GitHub personal access token (optional)
        limit: Maximum number of issues to return (default: 30)
              Will fetch multiple pages if limit > 100
        exclude_pulls: If True, excludes pull requests from results (default: False)

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

        # Keep original length (before filtering) for pagination checks
        original_count = len(page_issues_raw)

        # Filter out pull requests if requested
        if exclude_pulls:
            page_issues = [
                issue for issue in page_issues_raw if "pull_request" not in issue
            ]
        else:
            page_issues = page_issues_raw

        all_issues.extend(page_issues)

        # If the page contained fewer items than requested, we've reached the last page
        if original_count < per_page:
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
    exclude_pulls: bool = True,
    max_pages: int = 20,
    token: Optional[str] = None,
    show_urls: bool = True,
) -> pd.DataFrame:
    """
    Main function to fetch GitHub issues and return them as a DataFrame.

    Args:
        repository: Repository name in the format 'owner/repo'
        limit: Maximum number of issues to return (default: 100)
        exclude_pulls: Whether to exclude pull requests (default: True)
        max_pages: Maximum number of pages to fetch (default: 20)
        token: GitHub personal access token (default: None, will use GITHUB_TOKEN env variable if not provided)
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
        issues = fetch_issues(repository, token, limit, exclude_pulls, max_pages)
        print(f"Found {len(issues)} issues in {repository}")

        # Convert to DataFrame using a separate task
        return convert_and_process(issues, show_urls)

    except Exception as e:
        print(f"Error in flow execution: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    # Example usage - change these parameters as needed
    repository = (
        "DataDog/datadog-agent"  # Fixed capitalization to match GitHub's format
    )

    # Get token from environment variable
    token = os.environ.get("GITHUB_TOKEN", "")  # Use empty string instead of None

    # Fetch issues and get as DataFrame
    issues_df = fetch_gh_issues(
        repository=repository,
        limit=500,
        exclude_pulls=True,
        max_pages=20,
        token=token,  # Pass the token directly
        show_urls=True,
    )

    # Now you can work with the DataFrame
    # For example, you could filter by state:
    # open_issues = issues_df[issues_df['state'] == 'open']
    # print("Open issues:", open_issues)
