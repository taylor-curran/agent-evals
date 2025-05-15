# Plan: Linking Closed Issues to the Pull Request That Closed Them

Goal: For every issue whose `state == "closed"` and `state_reason == "completed"`, capture the pull-request(s) that actually closed it so we can read *both* the ask (issue) and the solution (PR).

---

## 1  Use the existing REST endpoint

* Continue calling **`/issues/{number}/timeline`** – we already fetch this in `fetch_many_timelines_for_issues`.  
* The timeline keeps full **cross-referenced** events that include the PR object.

## 2  Detect cross-reference events that point at a PR

```python
if e["event"] == "cross-referenced" \
   and e.get("source", {}).get("issue", {}).get("pull_request"):
    pr_num = e["source"]["issue"]["number"]   # e.g. 18036
    pr_url = e["source"]["issue"]["html_url"]  # https://github.com/…/pull/18036
```

* These events usually appear seconds **before** the final `closed` event.

## 3  Extend `timeline_to_dataframe`

Add columns on every row (filled only for cross-refs):

| column             | value                                                          |
|--------------------|----------------------------------------------------------------|
| `xref_pr_number`   | `e["source"]["issue"]["number"]`                           |
| `xref_pr_url`      | `e["source"]["issue"]["html_url"]`                        |

## 4  Post-processing join

For each closed-as-completed issue:

```python
closing_prs = timeline_df.query(
    "(issue_number == @issue) & (event == 'cross-referenced') & xref_pr_number.notna()"
)[["xref_pr_number", "xref_pr_url"]].drop_duplicates()
```

* If you only need the primary PR, take the first row. Otherwise keep all.

## 5  Fallbacks (rare cases)

* If no cross-reference was found **and** you still want a PR:
  * **GraphQL** – `issue → timelineItems(type: CLOSED_EVENT) → closer`.  
    It returns a union that can be `PullRequest`, commit, or other.
  * Or look from the other side: `pullRequest → closingIssuesReferences`.

## 6  Update the report script (`match_issues.py`)

* Merge the new PR columns so the console output shows:
  * Issue metadata & body
  * Comments
  * Timeline events (with `xref_pr_number` filled)
  * → Easy jump from issue → PR.

---

### TL;DR

1. Parse **cross-referenced** events in the timeline.  
2. Capture `source.issue.number/html_url` into the DataFrame.  
3. Join on `issue_number` during reporting.
