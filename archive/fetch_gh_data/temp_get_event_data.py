# Temporary standalone script to fetch GitHub issue timeline events only.
# This copies the event-related helpers from `fetch_issues.py` so that we can
# run them independently without pulling comments or metadata.

import os
import sys
import pathlib
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from prefect import flow, get_run_logger, task
from prefect.tasks import exponential_backoff
from prefect.task_runners import ThreadPoolTaskRunner

# ---------------------------------------------------------------------------
# Ensure the package path so we can import fetch_issues without installing
# ---------------------------------------------------------------------------

module_dir = pathlib.Path(__file__).resolve().parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

try:
    from fetch_issues import fetch_many_issues  # type: ignore
except ImportError:  # pragma: no cover – fallback failure
    fetch_many_issues = None  # type: ignore


# ---------------------------------------------------------------------------
# Low-level task: timeline request
# ---------------------------------------------------------------------------


@task(retries=4, retry_delay_seconds=exponential_backoff(backoff_factor=20))
def fetch_timeline(timeline_url: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """Fetch the timeline (event stream) for a single issue."""
    resp = requests.get(timeline_url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Helper → DataFrame
# ---------------------------------------------------------------------------


def timeline_to_dataframe(events: List[Dict[str, Any]]) -> pd.DataFrame:
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
# Sub-flow: fetch timelines for many issues in parallel
# ---------------------------------------------------------------------------


@flow(
    name="fetch issue timelines only", task_runner=ThreadPoolTaskRunner(max_workers=3)
)
def fetch_issue_timelines_only(
    repository: str,
    limit: int = 100,
    max_pages: int = 20,
    token: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch timeline events for *limit* issues in *repository* and return a DataFrame."""
    log = get_run_logger()
    token = token or os.getenv("GITHUB_TOKEN", "")

    if fetch_many_issues is None:
        raise RuntimeError(
            "fetch_many_issues import failed – run this script as part of the package or pass issues manually."
        )

    issues = fetch_many_issues(
        repository, token=token, limit=limit, max_pages=max_pages
    )

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
    df = timeline_to_dataframe(events)

    repo_safe = repository.replace("/", "_").replace("-", "_").replace(".", "_")
    path = f"{repo_safe}_issue_timeline.csv"
    df.to_csv(path, index=False)
    log.info("Saved events → %s", path)

    return df


if __name__ == "__main__":
    # Example quick run
    fetch_issue_timelines_only(
        repository="PrefectHQ/prefect",
        limit=50,
        max_pages=10,
    )
