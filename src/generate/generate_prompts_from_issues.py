# src/generate/generate_prompts_from_issues.py
"""Generate evaluation prompts from GitHub issues grouped by pull-request.

This is the **minimal first cut** for the pipeline described in
`src/generate/get_gh_data/prompt_generating_plan.md` (sections 1–5).

It supports two modes:

* ``summary``: synthesise a single human request (naive heuristic if no model).
* ``raw``: concatenate full issue texts.

Only CSV + Markdown artefacts are written; Prefect flows, retries, and
advanced OpenAI summarisation will be added later (section 6 of the plan).
"""

from __future__ import annotations

import csv
import os
import re
import textwrap
from pathlib import Path
from typing import Dict, List, Optional

import requests

try:
    # Optional import – only needed if a model is provided.
    from openai import OpenAI  # type: ignore
except ModuleNotFoundError:  # pragma: no cover  – library may not be installed yet
    OpenAI = None  # type: ignore

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Paths are now relative to this file's directory structure.
BASE_DIR = Path(__file__).resolve().parent  # .../src/generate

# CSV lives under ``get_gh_data`` sub-folder next to this script.
CSV_MAPPING_PATH = BASE_DIR / "get_gh_data" / "pr_issue_mapping.csv"

# Generated artefacts will be written alongside this script for easy discovery.
OUTPUT_CSV = BASE_DIR / "generated_prompts.csv"
OUTPUT_MD = BASE_DIR / "generated_prompts.md"
GITHUB_API_REST = "https://api.github.com/repos/{owner}/{repo}/issues/{num}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_pr_issue_mapping(csv_path: Path = CSV_MAPPING_PATH) -> List[Dict[str, str]]:
    """Return list of rows from ``pr_issue_mapping.csv`` as dictionaries."""
    with csv_path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def group_by_pr(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, object]]:
    """Group mapping rows by ``pr_number`` collecting associated issue URLs."""
    grouped: Dict[str, Dict[str, object]] = {}
    for row in rows:
        pr_num = row["pr_number"]
        grp = grouped.setdefault(
            pr_num,
            {
                "pr_number": pr_num,
                "pr_url": row["pr_url"],
                "issues": [],  # list of issue urls
            },
        )
        grp["issues"].append(row["issue_url"])
    # sort issues list to have stable order
    for g in grouped.values():
        g["issues"].sort()
    return grouped


ISSUE_URL_RE = re.compile(
    r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/issues/(?P<num>\d+)"
)


def _parse_issue_url(url: str):
    m = ISSUE_URL_RE.fullmatch(url)
    if not m:
        raise ValueError(f"Unrecognised issue URL: {url}")
    return m.group("owner"), m.group("repo"), int(m.group("num"))


def fetch_issue_data(issue_url: str, token: Optional[str] = None) -> Dict[str, str]:
    """Fetch ``title`` and ``body`` for *issue_url* via GitHub REST API."""
    owner, repo, num = _parse_issue_url(issue_url)
    token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = GITHUB_API_REST.format(owner=owner, repo=repo, num=num)
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return {
        "number": num,
        "title": data.get("title", ""),
        "body": data.get("body", ""),
        "url": issue_url,
    }


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------


def _naive_summary(issues: List[Dict[str, str]]) -> str:
    """Naive imperative summary derived from issue titles."""
    if len(issues) == 1:
        return issues[0]["title"].rstrip(".") + "."
    joined = "; and ".join(iss["title"].rstrip(".") for iss in issues)
    return f"Implement the following: {joined}."


def build_prompt_text(
    issues: List[Dict[str, str]],
    *,
    mode: str = "summary",
    model: Optional[str] = None,
) -> str:
    """Return prompt text in the configured *mode* (summary/raw)."""
    if mode == "raw":
        chunks = []
        for iss in issues:
            chunks.append(
                textwrap.dedent(f"""
            #{iss["number"]}: {iss["title"]}
            {iss["body"] or "<no description>"}
            """).strip()
            )
        return "\n---\n".join(chunks)

    # summary mode
    if model and OpenAI is not None:
        client = OpenAI()

        joined = "\n---\n".join(f"### {iss['title']}\n{iss['body']}" for iss in issues)

        resp = client.responses.create(
            model=model,
            instructions=(
                "Rewrite the following GitHub issue texts into ONE imperative task statement "
                "addressed to a coding agent. Start with a verb. Do NOT mention GitHub, issues, "
                "pull-requests, version numbers, or environment details unless absolutely necessary."
            ),
            input=joined,
        )

        return resp.output_text.strip()

    # fallback heuristic
    return _naive_summary(issues)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def generate_prompt_from_issues(
    *,
    csv_path: Path = CSV_MAPPING_PATH,
    output_csv: Path = OUTPUT_CSV,
    output_md: Path = OUTPUT_MD,
    limit: Optional[int] = None,
    mode: str = "summary",
    model: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Main entry-point. Returns list of generated prompts."""

    rows = load_pr_issue_mapping(csv_path)
    grouped = group_by_pr(rows)

    # sort by numeric pr_number desc
    sorted_prs = sorted(
        grouped.values(), key=lambda d: int(d["pr_number"]), reverse=True
    )
    if limit is not None:
        sorted_prs = sorted_prs[:limit]

    prompts: List[Dict[str, str]] = []

    for pr in sorted_prs:
        issues = [fetch_issue_data(url) for url in pr["issues"]]
        prompt_text = build_prompt_text(issues, mode=mode, model=model)
        prompts.append(
            {
                "pr_number": pr["pr_number"],
                "prompt_text": prompt_text,
                "pr_url": pr["pr_url"],
                "issues": issues,
            }
        )

    # write CSV
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["pr_number", "prompt_text"])
        for p in prompts:
            writer.writerow([p["pr_number"], p["prompt_text"]])

    # write Markdown
    with output_md.open("w", encoding="utf-8") as md:
        for p in prompts:
            md.write(f"### PR {p['pr_number']} – [link]({p['pr_url']})\n\n")
            md.write("Prompt\n------\n")
            md.write("```text\n")
            md.write(p["prompt_text"].rstrip() + "\n")
            md.write("```\n\n")
            md.write("**Linked issues**\n\n")
            for iss in p["issues"]:
                md.write(f"* [#{iss['number']}]({iss['url']})\n")
            md.write("\n---\n\n")

    return prompts


if __name__ == "__main__":
    generate_prompt_from_issues(limit=6, mode="summary", model="o4-mini")
