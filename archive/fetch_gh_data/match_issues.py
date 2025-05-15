import pandas as pd

repository = "PrefectHQ/prefect"
sanitized_repo = repository.replace("/", "_").replace("-", "_").replace(".", "_")
df_issues_metadata = pd.read_csv(f"{sanitized_repo}_issues.csv")

closed_as_completed = df_issues_metadata.query(
    'state_reason == "completed" & state == "closed"'
)

df_comments = pd.read_csv(f"{sanitized_repo}_issue_comments.csv")
df_events = pd.read_csv(f"{sanitized_repo}_issue_timeline.csv")

# only df comments on issues that are completed
df_comments = df_comments[
    df_comments["issue_number"].isin(closed_as_completed["issue_number"])
]
# print issue metadata then comments for issue 18035
issue_data_example_with_pr = closed_as_completed[
    closed_as_completed["issue_number"] == 18035
]
if not issue_data_example_with_pr.empty:
    for i, row in issue_data_example_with_pr.iterrows():
        print("#", row["issue_number"])
        print("TITLE :", row["title"])
        print("STATE :", row["state"])
        print("REASON:", row["state_reason"])
        print("BODY  :\n", row["body"])
        print("-" * 80)
        # print comments
        comments = df_comments[df_comments["issue_number"] == row["issue_number"]]
        for j, comment in comments.iterrows():
            print("~" * 80)
            print("COMMENT ID:", comment["comment_id"])
            print("USER:", comment["user"])
            print("CREATED:", comment["created_at"])
            print("UPDATED:", comment["updated_at"])
            print("AUTHOR ASSOCIATION:", comment["author_association"])
            print("BODY:\n", comment["body"])
            print("REACTIONS:", comment["reactions"])
            print("NODE ID:", comment["node_id"])
            print("ISSUE URL:", comment["issue_url"])
            print("URL:", comment["url"])
            print("~" * 80)
        # print timeline events
        events = df_events[df_events["issue_number"] == row["issue_number"]]
        if events.empty:
            print("No timeline events found for this issue.")
        else:
            for k, ev in events.iterrows():
                print("*" * 80)
                print("EVENT ID:", ev.get("event_id"))
                print("EVENT   :", ev["event"])
                print("CREATED :", ev["created_at"])
                print("ACTOR   :", ev["actor"])
                print("COMMIT  :", ev.get("commit_id"))
                print("COMMIT URL:", ev.get("commit_url"))
                print("NODE ID :", ev.get("node_id"))
                print("PR #    :", ev.get("pull_number"))
                print("PR URL  :", ev.get("pull_url"))
                print("LABEL   :", ev.get("label"))
                print("SOURCE  :", ev.get("source_type"))
                print("APP     :", ev.get("performed_via_github_app"))
                print("URL     :", ev.get("url"))
                print("*" * 80)
        print("- ~ -" * 40)
else:
    print("Issue #18017 not found in the completed issues dataset")


# rows for events
#             {
#                 "event_id": e.get("id"),
#                 "node_id": e.get("node_id"),
#                 "issue_number": e.get("issue_number"),
#                 "event": e.get("event"),
#                 "created_at": e.get("created_at"),
#                 "actor": e.get("actor", {}).get("login") if e.get("actor") else None,
#                 "commit_id": e.get("commit_id"),
#                 "commit_url": e.get("commit_url"),
#                 "label": e.get("label", {}).get("name") if e.get("label") else None,
#                 "performed_via_github_app": e.get("performed_via_github_app"),
#                 "pull_number": e.get("pull_request", {}).get("number")
#                 if e.get("pull_request")
#                 else None,
#                 "pull_url": e.get("pull_request", {}).get("url")
#                 if e.get("pull_request")
#                 else None,
#                 "source_type": e.get("source", {}).get("type")
#                 if e.get("source")
#                 else None,
#                 "url": e.get("url"),
