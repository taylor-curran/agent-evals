"""get_pr_data_lite.py – lightweight utility to discover which pull-request(s)
closed a given GitHub issue.

Strategy: call the REST `/issues/{num}/timeline` endpoint and look for
`cross-referenced` events whose `source.issue` object contains a `pull_request`
key.  Those events represent automatic references from PRs that included
"Fixes #123" etc.  Capturing their number & URL lets us jump straight to the
solution that closed the issue.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------


def _headers(token: Optional[str] = None) -> Dict[str, str]:
    """Generate GitHub API headers."""
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def fetch_issue_timeline(
    repo: str, issue_number: int, token: Optional[str] = None
) -> List[Dict]:
    """Return raw timeline events for a single issue via REST."""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/timeline"
    resp = requests.get(url, headers=_headers(token), timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_cross_referenced_prs(events: List[Dict]) -> List[Dict[str, str]]:
    """Extract PR number & URL from cross-referenced events that point at a PR."""
    prs: List[Dict[str, str]] = []
    for e in events:
        if e.get("event") == "cross-referenced":
            src_issue = e.get("source", {}).get("issue", {})
            if "pull_request" in src_issue:
                prs.append(
                    {
                        "pr_number": str(src_issue.get("number")),
                        "pr_url": src_issue.get("html_url"),
                    }
                )
    return prs


# ---------------------------------------------------------------------------
# Public, parameterised entry point
# ---------------------------------------------------------------------------


def get_closing_prs_for_issue(
    repository: str, issue_number: int, token: Optional[str] | None = None
) -> List[Dict[str, str]]:
    """Return list of PR dicts (number, url) that reference/close *issue_number*.

    Example::
        prs = get_closing_prs_for_issue("PrefectHQ/prefect", 18035)
        for pr in prs:
            print(pr["pr_number"], pr["pr_url"])
    """

    token = token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    events = fetch_issue_timeline(repository, issue_number, token)
    return extract_cross_referenced_prs(events)


# ---------------------------------------------------------------------------
# Convenience display helper (no CLI argument parsing)
# ---------------------------------------------------------------------------


def display_closing_prs(
    repository: str = "PrefectHQ/prefect",
    issue_number: int | None = None,
    token: Optional[str] | None = None,
) -> None:
    """Pretty-print the PR(s) that closed *issue_number* in *repository*.

    Parameters
    ----------
    repository : str
        e.g. "PrefectHQ/prefect"
    issue_number : int | None
        GitHub issue number. If *None*, nothing happens.
    token : str | None
        GitHub personal-access token (falls back to GH_TOKEN / GITHUB_TOKEN).
    """

    if issue_number is None:
        print("[display_closing_prs] issue_number is required → nothing to do.")
        return

    prs = get_closing_prs_for_issue(repository, issue_number, token)
    if prs:
        print(f"Issue #{issue_number} was referenced by (likely closed by):")
        for pr in prs:
            print(f"  PR #{pr['pr_number']} → {pr['pr_url']}")
    else:
        print(f"No cross-referenced PRs found for issue #{issue_number}.")


if __name__ == "__main__":
    display_closing_prs()
