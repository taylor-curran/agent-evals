import os
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from prefect import flow, get_run_logger, task
from prefect.tasks import exponential_backoff
from prefect.task_runners import ThreadPoolTaskRunner

# ---------------------------------------------------------------------------
# Low‑level tasks (plain HTTP + minimal retries)
# ---------------------------------------------------------------------------


@task(retries=4, retry_delay_seconds=exponential_backoff(backoff_factor=20))
def fetch_issue_page(url: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """Grab one page of issues (or PRs) via the GitHub REST API."""
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


@task(retries=4, retry_delay_seconds=exponential_backoff(backoff_factor=20))
def fetch_comments(comments_url: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """Fetch every comment attached to a single issue."""
    resp = requests.get(comments_url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


@task(retries=4, retry_delay_seconds=exponential_backoff(backoff_factor=20))
def fetch_timeline(timeline_url: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """Fetch the timeline (event stream) for a single issue."""
    resp = requests.get(timeline_url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Helpers for DataFrame construction
# ---------------------------------------------------------------------------


def issues_to_dataframe(issues: List[Dict[str, Any]]) -> pd.DataFrame:
    if not issues:
        return pd.DataFrame()
    rows: List[Dict[str, Any]] = []

    for i in issues:
        rows.append(
            {
                "issue_number": i.get("number"),
                "title": i.get("title"),
                "state": i.get("state"),
                "state_reason": i.get("state_reason"),
                "body": i.get("body"),
                "created_at": i.get("created_at"),
                "updated_at": i.get("updated_at"),
                "closed_at": i.get("closed_at"),
                "n_comments": i.get("comments"),
                "labels": i.get("labels"),
                "user": i.get("user", {}).get("login"),
                "assignee": i.get("assignee", {}).get("login")
                if i.get("assignee")
                else None,
                "author_association": i.get("author_association"),
                "closed_by": i.get("closed_by", {}).get("login")
                if i.get("closed_by")
                else None,
                "reactions": i.get("reactions", {}).get("total_count")
                if i.get("reactions")
                else 0,
                "timeline_url": i.get("timeline_url"),
                "sub_issues_total": i.get("sub_issues_summary", {}).get(
                    "total_count", 0
                )
                if i.get("sub_issues_summary")
                else 0,
                "sub_issues_completed": i.get("sub_issues_summary", {}).get(
                    "completed_count", 0
                )
                if i.get("sub_issues_summary")
                else 0,
                "sub_issues_percent_completed": i.get("sub_issues_summary", {}).get(
                    "percent_complete", 0
                )
                if i.get("sub_issues_summary")
                else 0,
                "url": i.get("html_url"),
            }
        )
    return pd.DataFrame(rows)


def comments_to_dataframe(comments: List[Dict[str, Any]]) -> pd.DataFrame:
    if not comments:
        return pd.DataFrame()
    rows: List[Dict[str, Any]] = []
    for c in comments:
        rows.append(
            {
                "comment_id": c.get("id"),
                "issue_number": c.get("issue_number"),
                "user": c.get("user", {}).get("login"),
                "created_at": c.get("created_at"),
                "updated_at": c.get("updated_at"),
                "author_association": c.get("author_association"),
                "body": c.get("body"),
                "reactions": c.get("reactions", {}).get("total_count")
                if c.get("reactions")
                else 0,
                "node_id": c.get("node_id"),
                "issue_url": c.get("issue_url"),
                "performed_via_github_app": c.get("performed_via_github_app"),
                "url": c.get("html_url"),
            }
        )
    return pd.DataFrame(rows)


def timeline_to_dataframe(events: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert a list of timeline events (all issues combined) into a DataFrame."""
    if not events:
        return pd.DataFrame()

    rows: List[Dict[str, Any]] = []
    for e in events:
        rows.append(
            {
                "event_id": e.get("id"),
                "node_id": e.get("node_id"),
                "issue_number": e.get("issue_number"),
                "event": e.get("event"),
                "created_at": e.get("created_at"),
                "actor": e.get("actor", {}).get("login") if e.get("actor") else None,
                "commit_id": e.get("commit_id"),
                "commit_url": e.get("commit_url"),
                "label": e.get("label", {}).get("name") if e.get("label") else None,
                "performed_via_github_app": e.get("performed_via_github_app"),
                "pull_number": e.get("pull_request", {}).get("number")
                if e.get("pull_request")
                else None,
                "pull_url": e.get("pull_request", {}).get("url")
                if e.get("pull_request")
                else None,
                "source_type": e.get("source", {}).get("type")
                if e.get("source")
                else None,
                "url": e.get("url"),
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sub‑flow: fetch a bunch of issues (metadata only)
# ---------------------------------------------------------------------------


@flow(name="fetch many issues metadata", log_prints=False)
def fetch_many_issues(
    repo: str,
    token: Optional[str] = None,
    limit: int = 30,
    max_pages: int = 20,
) -> List[Dict[str, Any]]:
    """Return up to *limit* non‑PR issues sorted by newest first."""
    log = get_run_logger()
    per_page = min(limit, 100)

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    base_url = f"https://api.github.com/repos/{repo}/issues"
    collected: List[Dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        if len(collected) >= limit:
            break
        url = f"{base_url}?state=all&sort=created&direction=desc&per_page={per_page}&page={page}"
        page_issues = fetch_issue_page.submit(url, headers)
        batch = page_issues.result()
        if not batch:
            break
        batch = [i for i in batch if "pull_request" not in i]
        collected.extend(batch)
        if len(batch) < per_page:
            break

    log.info("Fetched %s issues (after PR filter)", len(collected))
    return collected[:limit]


# ---------------------------------------------------------------------------
# Sub‑flow: fetch comments for many issues in parallel
# ---------------------------------------------------------------------------


@flow(name="fetch many issue comments", log_prints=False)
def fetch_many_comments_for_issues(
    issues: List[Dict[str, Any]],
    token: Optional[str] = None,
) -> pd.DataFrame:
    log = get_run_logger()
    if not issues:
        log.warning("No issues passed in – skipping comment collection.")
        return pd.DataFrame()

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    futures: List[Tuple[int, Any]] = []
    for issue in issues:
        url = issue.get("comments_url") or f"{issue['url']}/comments"
        fut = fetch_comments.submit(url, headers)
        futures.append((issue["number"], fut))

    comments: List[Dict[str, Any]] = []
    for num, fut in futures:
        try:
            for c in fut.result():
                c["issue_number"] = num
                comments.append(c)
        except Exception as exc:
            log.error("Failed to fetch comments for #%-5s: %s", num, exc, exc_info=True)

    log.info("Collected %s total comments", len(comments))
    return comments_to_dataframe(comments)


# ---------------------------------------------------------------------------
# Sub-flow: fetch timeline events for many issues in parallel
# ---------------------------------------------------------------------------


@flow(name="fetch many issue timelines", log_prints=False)
def fetch_many_timelines_for_issues(
    issues: List[Dict[str, Any]],
    token: Optional[str] = None,
) -> pd.DataFrame:
    log = get_run_logger()
    if not issues:
        log.warning("No issues passed in – skipping timeline collection.")
        return pd.DataFrame()

    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    futures: List[Tuple[int, Any]] = []
    for issue in issues:
        url = issue.get("timeline_url") or f"{issue['url']}/timeline"
        fut = fetch_timeline.submit(url, headers)
        futures.append((issue["number"], fut))

    events: List[Dict[str, Any]] = []
    for num, fut in futures:
        try:
            for ev in fut.result():
                ev["issue_number"] = num
                events.append(ev)
        except Exception as exc:
            log.error("Failed to fetch timeline for #%-5s: %s", num, exc, exc_info=True)

    log.info("Collected %s total timeline events", len(events))
    return timeline_to_dataframe(events)


# ---------------------------------------------------------------------------
# Top‑level orchestration flow
# ---------------------------------------------------------------------------


@flow(
    name="Fetch Closed GitHub Issues",
    task_runner=ThreadPoolTaskRunner(max_workers=3),
    log_prints=False,
)
def fetch_closed_gh_issues(
    repository: str,
    limit: int = 100,
    max_pages: int = 20,
    token: Optional[str] = None,
    show_urls: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """End‑to‑end pipeline – returns *(issues_df, comments_df, timeline_df)* and writes three CSVs."""
    log = get_run_logger()

    token = token or os.getenv("GITHUB_TOKEN", "")

    issues = fetch_many_issues(repository, token, limit, max_pages)
    issues_df = issues_to_dataframe(issues)

    if show_urls and not issues_df.empty:
        for url in issues_df["url"]:
            log.info(url)

    comments_df = fetch_many_comments_for_issues(issues, token)
    timeline_df = fetch_many_timelines_for_issues(issues, token)

    repo_safe = repository.replace("/", "_").replace("-", "_").replace(".", "_")
    issues_df.to_csv(f"{repo_safe}_issues.csv", index=False)
    comments_df.to_csv(f"{repo_safe}_issue_comments.csv", index=False)
    timeline_df.to_csv(f"{repo_safe}_issue_timeline.csv", index=False)

    log.info("Saved %s issues → %s", len(issues_df), f"{repo_safe}_issues.csv")
    log.info(
        "Saved %s comments → %s", len(comments_df), f"{repo_safe}_issue_comments.csv"
    )
    log.info(
        "Saved %s timeline events → %s",
        len(timeline_df),
        f"{repo_safe}_issue_timeline.csv",
    )

    return issues_df, comments_df, timeline_df


if __name__ == "__main__":
    fetch_closed_gh_issues(
        repository="PrefectHQ/prefect",
        limit=100,
        max_pages=20,
        show_urls=True,
    )
