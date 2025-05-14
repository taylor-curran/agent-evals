# Helper utilities for GitHub issue fetching

from typing import List, Dict, Any

import requests
import pandas as pd
from prefect import task
from prefect.tasks import exponential_backoff


@task(retries=3, retry_delay_seconds=exponential_backoff(backoff_factor=10))
def fetch_issue_page(page_url: str, headers: dict) -> List[Dict[Any, Any]]:
    """Fetch a single page of issues from the GitHub API with retries."""
    response = requests.get(page_url, headers=headers)
    response.raise_for_status()
    return response.json()


def issues_to_dataframe(issues: List[Dict[Any, Any]]) -> pd.DataFrame:
    """Convert a list of issue dictionaries into a pandas DataFrame."""
    if not issues:
        return pd.DataFrame()

    issue_data: List[Dict[str, Any]] = []
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


def print_urls(df: pd.DataFrame) -> None:
    """Print the URLs of the issues in the provided DataFrame."""
    for _, row in df.iterrows():
        print(row["url"])


@task
def convert_and_process(
    issues: List[Dict[Any, Any]], show_urls: bool = True
) -> pd.DataFrame:  # type: ignore[name-defined]
    """Convert issues to DataFrame and optionally print their URLs."""
    df: pd.DataFrame = issues_to_dataframe(issues)

    if show_urls and not df.empty:
        print_urls(df)

    return df
