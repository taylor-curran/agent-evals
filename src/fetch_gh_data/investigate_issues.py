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
for _, row in closed_as_completed.head(5).iterrows():
    print("#", row["number"])
    print("TITLE :", row["title"])
    print("BODY  :\n", row["body"])
    print("COMMENTS:", row["comments"])
    print("-" * 80)

df_comments = pd.read_csv(f"{sanitized_repo}_issue_comments.csv")

print(df_comments.columns)
# Index(['comment_id', 'issue_number', 'user', 'created_at', 'updated_at',
#        'author_association', 'body', 'reactions', 'node_id', 'issue_url',
#        'performed_via_github_app', 'url'],
#       dtype='object')
for _, row in df_comments.head(5).iterrows():
    print(row["issue_number"])
    print(row["body"])
    print("-" * 80)
    