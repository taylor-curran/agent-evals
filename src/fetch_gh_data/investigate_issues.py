# src/fetch_gh_data/investigate_issues.py

import pandas as pd

repository = "PrefectHQ/prefect"
sanitized_repo = repository.replace("/", "_").replace("-", "_").replace(".", "_")
df_issues_metadata = pd.read_csv(f"{sanitized_repo}_issues.csv")

closed_issues_verbose = df_issues_metadata.query('state == "closed"')

for _, row in closed_issues_verbose.head(20).iterrows():
    print(row["url"])
    print(row["title"])
    print(row["state"])
    print(row["state_reason"])
    print("\n")

closed_as_completed = closed_issues_verbose.query('state_reason == "completed"')

# Display full details for the first five completed issues
for _, row in closed_as_completed.head(2).iterrows():
    print("#", row["issue_number"])
    print("TITLE :", row["title"])
    print("STATE :", row["state"])
    print("REASON:", row["state_reason"])
    print("BODY  :\n", row["body"])
    print("CREATED:", row["created_at"])
    print("UPDATED:", row["updated_at"])
    print("CLOSED :", row["closed_at"])
    print("COMMENTS:", row["n_comments"])
    print("LABELS :", row["labels"])
    print("USER   :", row["user"])
    print("ASSIGNEE:", row["assignee"])
    print("AUTHOR :", row["author_association"])
    print("CLOSED BY:", row["closed_by"])
    print("REACTIONS:", row["reactions"])
    print("TIMELINE:", row["timeline_url"])
    print("SUB ISSUES:", row["sub_issues_total"])
    print("COMPLETED:", row["sub_issues_completed"])
    print("PERCENT COMPLETE:", row["sub_issues_percent_completed"])
    print("URL    :", row["url"])
    print("-" * 80)

df_comments = pd.read_csv(f"{sanitized_repo}_issue_comments.csv")

# only df comments on issues that are completed
df_comments = df_comments[df_comments["issue_number"].isin(closed_as_completed["issue_number"])]

# Show details for the first five comments
for _, row in df_comments.head(5).iterrows():
    print("ISSUE #:", row["issue_number"])
    print("COMMENT ID:", row["comment_id"])
    print("USER:", row["user"])
    print("CREATED:", row["created_at"])
    print("UPDATED:", row["updated_at"])
    print("AUTHOR ASSOCIATION:", row["author_association"])
    print("BODY:\n", row["body"])
    print("REACTIONS:", row["reactions"])
    print("NODE ID:", row["node_id"])
    print("ISSUE URL:", row["issue_url"])
    print("URL:", row["url"])
    print("-" * 80)
    

print(closed_as_completed.columns)
print(df_comments.columns)