# Plan: Prompt Generation & Evaluation for Coding Agents

## Goal
For each **pull request (PR)** with its associated batch of closed issues, we will:
1. Craft a **natural-language prompt** that presents *only* the requirements contained in those issues – **no hints about the PR implementation, files affected, branch names, or code snippets unless clearly stated in the issue**.
2. Run a coding agent against the repository snapshot **prior to** the PR merge, supplying that prompt.
3. Evaluate the agent’s output by comparing it with the actual merged PR.

---

## Inputs & Data Flow

| Artifact | Produced by | Purpose |
|----------|-------------|---------|
| `pr_issue_mapping.csv` | `fetch_pr_closing_issues.py` | Maps each merged PR → list of issues it closed |
| **Issue details** | GitHub REST (`/repos/{owner}/{repo}/issues/{issue_number}`) | Title, body, labels, etc. |
| **Pre-PR repo snapshot** | `git checkout <sha_before_pr>` | Starting codebase for the agent |
| **Merged PR diff** | `git diff <sha_before_pr>..<pr_merge_sha>` | Ground-truth implementation to evaluate against |

---

## 1  Collect Issue Text

1. Iterate over each unique `pr_number` in `pr_issue_mapping.csv`.
2. Retrieve JSON for every associated `issue_number`.
3. For each issue store:
   * `title`
   * `body` (full Markdown)
   * `labels`
   * URL (kept **only** for traceability, not included in the agent prompt)
4. Serialize to `pr_<num>_issues.json` for trace-free caching.

## 2  Generate Agent Prompt

Template (YAML front-matter style for easy parsing):
```text
<<SYSTEM>>
You are a seasoned open-source contributor …
<</SYSTEM>>

<<USER>>
Repository: prefect (commit 0123abcd **before** PR {{pr_number}})

The project owners have opened the following issues which you must resolve **in one PR**.

{% for issue in issues %}
### Issue {{ loop.index }} – {{ issue.title }}
{{ issue.body }}
{% endfor %}

Deliver code changes that fully satisfy all of the above requirements.  Do **not** reference pull-requests or issue numbers in commit messages or code.  Follow existing project conventions.
<</USER>>
```

Generation steps:
1. Substitute `issues` with sanitized Markdown (strip HTML, redact e-mails, remove code links).
2. Write prompt to `prompts/pr_{pr_number}.md`.

## 3  Run Coding Agent

Script: `run_agent_on_prompt.py`
1. Checkout repo at **pre-merge** SHA.
2. Invoke selected agent (OpenAI, OSS model, etc.) with the prompt file.
3. Capture:
   * Wall-clock time
   * Tool usage stats
   * Generated diff / commits
4. Save outputs to `runs/pr_{pr_number}/`.

## 4  Evaluate Agent Output

Metrics:
| Metric | Method |
|--------|--------|
| **Diff similarity** | `git diff --stat` between agent patch and ground-truth PR |
| **Exact hunks matched** | `diff -u` granularity |
| **Compilation / tests pass** | Run project’s test suite on agent result |
| **File coverage** | % of files edited by both agent & PR |
| **Latency** | Seconds to draft solution |

Evaluation pipeline `evaluate_agent_run.py`:
1. Apply agent’s patch on pre-merge commit in a temp branch.
2. Run unit tests; record pass/fail & coverage.
3. Produce numeric score sheet `scores.csv` with columns:
   * `pr_number`, `similarity_score`, `tests_passed`, `latency_s`, etc.

## 5  Reporting & Visualization
* Aggregate scores across PRs.
* Jupyter notebook `analysis/agent_vs_human.ipynb` to plot distributions.

---

## Directory Layout (new)
```
agent_evals/
└─ src/
   └─ prompt_runs/
      ├─ data/
      │   ├─ pr_issue_mapping.csv
      │   └─ pr_<num>_issues.json
      ├─ prompts/
      │   └─ pr_<num>.md
      ├─ runs/
      │   └─ pr_<num>/
      ├─ scores.csv
      ├─ generate_prompts.py
      ├─ run_agent_on_prompt.py
      └─ evaluate_agent_run.py
```

---

## Next Actions
1. **Implement `generate_prompts.py`** → reads mapping CSV, fetches issues, writes prompt files.
2. Draft **agent runner wrapper** (`run_agent_on_prompt.py`) – can be a thin shell that POSTs to local agent API.
3. Create **evaluation script** with diff & test hooks.
4. Validate pipeline on a single small PR.
5. Iterate on prompt phrasing & metrics.
