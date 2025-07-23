"""Test script for real GitHub API interaction."""
import asyncio
from services.github_service import GitHubClient

async def test_real_github():
    """Test fetching data from a real GitHub repo."""
    try:
        client = GitHubClient()
        print("✅ GitHub client initialized with token")
        
        # Test with a small number of PRs first
        repo_owner = "PrefectHQ"
        repo_name = "prefect"
        
        print(f"🔄 Fetching PR-issue data from {repo_owner}/{repo_name}...")
        pr_issues = await client.fetch_pr_issue_data(repo_owner, repo_name)
        
        print(f"✅ Successfully fetched {len(pr_issues)} PR-issue mappings")
        
        if pr_issues:
            print("\n📊 Sample data (first PR-issue):")
            first = pr_issues[0]
            print(f"  PR #{first['pr_number']}: {first['pr_title']}")
            print(f"  Issue #{first['issue_number']}: {first['issue_title']}")
            print(f"  Merged at: {first['pr_merged_at']}")
            print(f"  Base branch: {first['pr_base_branch']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_github())