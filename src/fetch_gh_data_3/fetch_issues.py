# src/fetch_gh_data_3/fetch_issues.py

import requests
import os
import pandas as pd
from typing import List, Dict, Any, Optional
from prefect import flow, task
from prefect.tasks import exponential_backoff


# Prefect task to fetch a single page of issues with retries
@task(retries=3, retry_delay_seconds=exponential_backoff(backoff_factor=10))
def fetch_issue_page(page_url: str, headers: dict) -> List[Dict[Any, Any]]:
    """
    Fetch a single page of issues from the GitHub API.
    Prefect handles retries with exponential back-off at this granular level.
    """
    response = requests.get(page_url, headers=headers)
    response.raise_for_status()
    return response.json()


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


def issues_to_dataframe(issues: List[Dict[Any, Any]]) -> pd.DataFrame:
    """
    Convert a list of GitHub issue dictionaries to a pandas DataFrame.

    Args:
        issues: List of issue dictionaries from the GitHub API

    Returns:
        pandas DataFrame containing issue data
    """
    if not issues:
        return pd.DataFrame()
    # Select relevant columns for the DataFrame
    issue_data = []
    for issue in issues:
        issue_data.append(
            {
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "comments": issue["comments"],
                "user": issue["user"]["login"] if issue["user"] else None,
                "url": issue["html_url"],
            }
        )

    return pd.DataFrame(issue_data)


def print_urls(df: pd.DataFrame):
    """
    Print the URLs of the issues in the DataFrame.

    Args:
        df: DataFrame containing issue data
    """
    for index, row in df.iterrows():
        print(row["url"])


@task
def convert_and_process(issues, show_urls=True):
    """Convert issues to DataFrame and process results"""
    # Convert issues to DataFrame
    df = issues_to_dataframe(issues)

    # Print issue URLs if requested
    if show_urls and not df.empty:
        print_urls(df)

    return df


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
