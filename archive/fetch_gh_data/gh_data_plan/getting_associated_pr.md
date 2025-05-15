`/issues/{num}/events` only returns the *minimal* event object.

For cross-reference events it strips the `source` sub-object that tells you *who* did the referencing, so you can’t see the pull-request number there.
**What to call instead** 
 
2. **REST – timeline endpoint** 


```bash
curl -H "Accept: application/vnd.github+json" \
     -H "Authorization: Bearer $TOKEN" \
     https://api.github.com/repos/PrefectHQ/prefect/issues/18035/timeline \
| jq -r '
    .[]
    | select(.event=="cross-referenced" and .source.issue.pull_request)
    | .source.issue.number
  '
# → 18036
```

 
  - `/timeline` keeps the full **cross-referenced**  event, including

`source.issue.pull_request` → that object contains the PR number, title, URL, etc.[GitHub Docs](https://docs.github.com/en/rest/issues/timeline) [GitHub Docs](https://docs.github.com/en/rest/using-the-rest-api/issue-event-types)
 
4. **GraphQL – ask the issue who closed it** 


```graphql
{
  repository(owner:"PrefectHQ", name:"prefect") {
    issue(number: 18035) {
      timelineItems(first: 10, itemTypes: CLOSED_EVENT) {
        nodes {
          ... on ClosedEvent {
            closedAt
            closer {                  # Union → Commit | PullRequest | Project
              __typename
              ... on PullRequest {
                number
                title
                url
              }
            }
          }
        }
      }
    }
  }
}
```

The `closer` union tells you whether a **PullRequest** , commit, or something

else closed the issue. Here it returns PR `18036`.[GitHub Docs](https://docs.github.com/fr/enterprise-cloud%40latest/graphql/reference/unions)
 
6. **GraphQL – ask the PR which issues it closes** 


```graphql
{
  repository(owner:"PrefectHQ", name:"prefect") {
    pullRequest(number: 18036) {
      closingIssuesReferences(first: 10) {
        nodes { number title url }
      }
    }
  }
}
```

`closingIssuesReferences` is purpose-built for “what will / did this PR close?” and works in the opposite direction.[GitHub Docs](https://docs.github.com/en/graphql/overview/changelog?utm_source=chatgpt.com)



---



### Quick Python helper 



```python
import requests, os

REPO = "PrefectHQ/prefect"
ISSUE = 18035
token = os.getenv("GH_TOKEN")
url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/timeline"
resp = requests.get(url, headers={"Accept": "application/vnd.github+json",
                                  "Authorization": f"Bearer {token}"})
pr_nums = [e["source"]["issue"]["number"]
           for e in resp.json()
           if e["event"] == "cross-referenced"
           and "pull_request" in e["source"]["issue"]]

print(pr_nums)   # ['18036']
```



---


**TL;DR** 
 
- Use `/timeline`, not `/events`, and filter for `event == "cross-referenced"` where `source.issue.pull_request` exists.
 
- If you prefer GraphQL, `issue → ClosedEvent.closer` or `pullRequest → closingIssuesReferences` give you the same answer.

![Favicon](https://www.google.com/s2/favicons?domain=https://docs.github.com&sz=32) 
