# Fetch issues that a specific pull-request closes via GitHub GraphQL.

from __future__ import annotations

from typing import List, Dict, Optional
import os
import requests

GITHUB_API = "https://api.github.com/graphql"

def _headers(token: str) -> Dict[str, str]:
    """Standard request headers for GitHub GraphQL API."""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


def _pr_query(owner: str, name: str, pr_number: int) -> str:
    """Return GraphQL query fetching `closingIssuesReferences` for *pr_number*."""
    return (
        "query {\n"
        f'  repository(owner:"{owner}", name:"{name}") {{\n'
        f"    pullRequest(number: {pr_number}) {{\n"
        "      number\n"
        "      title\n"
        "      url\n"
        "      closingIssuesReferences(first: 50) {\n"
        "        nodes {\n"
        "          number\n"
        "          title\n"
        "          url\n"
        "          state\n"
        "          stateReason\n"
        "        }\n"
        "      }\n"
        "    }\n"
        "  }\n"
        "}\n"
    )

def fetch_issues_for_pr(
    repo: str,
    pr_number: int,
    token: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Return a list of issue dicts that *pr_number* closes.

    Each element contains at least: ``number``, ``title``, ``url``, ``state`` and
    ``stateReason`` (may be *None*).
    """

    token = token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GitHub token must be provided via argument or environment variable (GH_TOKEN / GITHUB_TOKEN)."
        )

    try:
        owner, name = repo.split("/", 1)
    except ValueError as exc:
        raise ValueError("`repo` must be in the form 'owner/name'.") from exc

    payload = {"query": _pr_query(owner, name, pr_number)}
    resp = requests.post(GITHUB_API, json=payload, headers=_headers(token), timeout=30)
    resp.raise_for_status()

    pr_data = resp.json()["data"]["repository"].get("pullRequest")
    if pr_data is None:
        raise ValueError(f"Pull-request #{pr_number} not found in repository {repo}.")

    return pr_data["closingIssuesReferences"]["nodes"]

def print_issues_for_pr(repo: str, pr_number: int, token: Optional[str] = None) -> None:
    """Fetch issues for *pr_number* and print a readable summary to stdout."""
    issues = fetch_issues_for_pr(repo, pr_number, token)

    if not issues:
        print(f"PR #{pr_number} closes **no** issues.")
        return

    print(f"PR #{pr_number} closes {len(issues)} issue(s):")
    for iss in issues:
        state = iss["state"]
        reason = iss.get("stateReason")
        reason_str = f" ({reason})" if reason else ""
        print(
            f"  • #{iss['number']}: {iss['title']} – {state}{reason_str}\n    ↳ {iss['url']}"
        )


def create_prompt_from_issues(pr_number: int, token: Optional[str] = None) -> None:
    """Fetch issues for *pr_number* and print a readable summary to stdout."""
    print_issues_for_pr(repo="PrefectHQ/prefect", pr_number=pr_number)


if __name__ == "__main__":
    create_prompt_from_issues(pr_number=18003)
