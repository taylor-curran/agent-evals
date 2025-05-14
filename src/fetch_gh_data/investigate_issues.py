# src/fetch_gh_data/investigate_issues.py

import pandas as pd

repository = "PrefectHQ/prefect"
sanitized_repo = repository.replace("/", "_").replace("-", "_").replace(".", "_")
df = pd.read_csv(f"{sanitized_repo}_issues.csv")

closed_issues_verbose = df.query('state == "closed"')

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
