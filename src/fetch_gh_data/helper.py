# src/fetch_gh_data/helper.py

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
    """Convert a list of issue dictionaries into a pandas DataFrame.

    The function now flattens additional useful fields that were previously
    missing from the resulting DataFrame, including:
    - state_reason
    - body
    - closed_by (login)
    - reactions (total_count)
    - timeline_url
    - sub_issues_summary (flattened into three columns)
    - assorted metadata such as labels, assignee, etc.
    """
    if not issues:
        return pd.DataFrame()

    issue_data: List[Dict[str, Any]] = []
    for issue in issues:
        issue_data.append(
            {
                # Core metadata
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "state_reason": issue.get("state_reason"),
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
                "closed_at": issue.get("closed_at"),
                "comments": issue.get("comments"),
                # Labels and user information
                "labels": [label.get("name") for label in issue.get("labels", [])]
                if issue.get("labels")
                else [],
                "user": issue.get("user", {}).get("login")
                if isinstance(issue.get("user"), dict)
                else None,
                "assignee": issue.get("assignee", {}).get("login")
                if isinstance(issue.get("assignee"), dict)
                else None,
                "author_association": issue.get("author_association"),
                # Content and additional metadata
                "body": issue.get("body"),
                "closed_by": issue.get("closed_by", {}).get("login")
                if issue.get("closed_by")
                else None,
                "reactions": issue.get("reactions", {}).get("total_count")
                if issue.get("reactions")
                else None,
                "timeline_url": issue.get("timeline_url"),
                # Sub-issue summary (flattened)
                "sub_issues_total": issue.get("sub_issues_summary", {}).get("total")
                if issue.get("sub_issues_summary")
                else None,
                "sub_issues_completed": issue.get("sub_issues_summary", {}).get(
                    "completed"
                )
                if issue.get("sub_issues_summary")
                else None,
                "sub_issues_percent_completed": issue.get("sub_issues_summary", {}).get(
                    "percent_completed"
                )
                if issue.get("sub_issues_summary")
                else None,
                # URLs
                "url": issue.get("html_url"),
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
