# src/get_gh_data/fetch_pr_closing_issues.py

"""Fetch merged pull-requests and the issues they close using GitHub GraphQL.

Each PR node includes `closingIssuesReferences`, giving us the issue numbers that
were automatically closed when the PR was merged.  This script pages through all
merged PRs in the repo and writes a CSV mapping `pr_number → issue_number`.
"""

from __future__ import annotations

import csv
import os
from typing import List, Dict, Optional

import requests

GITHUB_API = "https://api.github.com/graphql"
DEFAULT_PAGE_SIZE = 100  # max GitHub allows


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


def _query(owner: str, name: str, after: Optional[str] = None) -> str:
    """Build GraphQL query for merged PRs ordered newest→oldest."""
    after_clause = f', after: "{after}"' if after else ""
    return (
        "query {\n"
        f'  repository(owner:"{owner}", name:"{name}") {{\n'
        f"    pullRequests(states: MERGED, first: {DEFAULT_PAGE_SIZE}, orderBy: {{field: UPDATED_AT, direction: DESC}}{after_clause}) {{\n"
        "      pageInfo { endCursor hasNextPage }\n"
        "      nodes {\n"
        "        number\n"
        "        mergedAt\n"
        "        url\n"
        "        closingIssuesReferences(first: 10) { nodes { number url state stateReason } }\n"
        "      }\n"
        "    }\n"
        "  }\n"
        "}\n"
    )


def fetch_pr_issue_mapping(
    repo: str,
    token: str,
    max_prs: Optional[int] = None,
) -> List[Dict[str, str]]:
    """Return up to *max_prs* merged PRs that closed issues.

    Parameters
    ----------
    repo : str
        Repository in ``owner/name`` form.
    token : str
        GitHub token.
    max_prs : int | None, optional
        If given, stop after collecting this many **unique PRs** that closed at
        least one issue.  *None* means no limit (default behaviour).
    """
    owner, name = repo.split("/", 1)
    out: List[Dict[str, str]] = []
    processed_prs: set[int] = set()
    cursor: Optional[str] = None
    session = requests.Session()
    while True:
        payload = {"query": _query(owner, name, cursor)}
        resp = session.post(
            GITHUB_API, json=payload, headers=_headers(token), timeout=30
        )
        resp.raise_for_status()
        data = resp.json()["data"]["repository"]["pullRequests"]

        for pr in data["nodes"]:
            iss_nodes = pr["closingIssuesReferences"]["nodes"]
            if not iss_nodes:
                # Skip PRs that did not close any issues
                continue

            pr_number = pr["number"]
            processed_prs.add(pr_number)

            for iss in iss_nodes:
                out.append(
                    {
                        "pr_number": pr_number,
                        "pr_url": pr["url"],
                        "pr_merged_at": pr["mergedAt"],
                        "issue_number": iss["number"],
                        "issue_url": iss["url"],
                        "issue_state": iss["state"],
                        "issue_reason": iss.get("stateReason"),
                    }
                )

            # Early-exit if we've gathered the desired number of PRs
            if max_prs is not None and len(processed_prs) >= max_prs:
                return out

        if not data["pageInfo"]["hasNextPage"]:
            break
        cursor = data["pageInfo"]["endCursor"]
    return out


def save_mapping_csv(rows: List[Dict[str, str]], path: str) -> None:
    if not rows:
        print("[fetch_pr_closing_issues] No rows to save – skipping CSV write.")
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows → {path}")


def fetch_pr_closing_issues(
    repo: str,
    token: Optional[str] = None,
    outfile: str = "pr_issue_mapping.csv",
    max_prs: Optional[int] = None,
) -> None:
    """Top-level helper: fetch PR→issue mapping and write CSV.

    Parameters
    ----------
    repo : str
        GitHub repository in "owner/name" form.
    token : str | None
        Personal-access token.  If *None*, will look at GH_TOKEN / GITHUB_TOKEN env.
    outfile : str
        Path to CSV output.
    max_prs : int | None, optional
        If given, stop after collecting this many **unique PRs** that closed at
        least one issue.  *None* means no limit (default behaviour).
    """

    token = token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GitHub token must be provided via argument or env variable.")

    rows = fetch_pr_issue_mapping(repo, token, max_prs=max_prs)
    save_mapping_csv(rows, outfile)


# ---------------------------------------------------------------------------
# __main__
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Example: fetch the 50 most-recent PRs that closed ≥1 issue.
    fetch_pr_closing_issues("PrefectHQ/prefect", max_prs=70)
