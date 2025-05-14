# src/fetch_gh_data/investigate_issues.py

import pandas as pd

df = pd.read_csv("DataDog_datadog-agent_issues.csv")

closed_issues_verbose = df.query('state == "closed"')

for _, row in closed_issues_verbose.iterrows():
    print(row["url"])
    print(row["title"])
    print(row["state"])
    print(row["state_reason"])
    print("\n")

print(closed_issues_verbose)
