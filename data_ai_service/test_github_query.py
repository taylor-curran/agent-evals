"""Debug GitHub GraphQL query."""
import asyncio
import httpx
import os

async def test_query():
    """Test basic GraphQL query."""
    token = os.getenv("GITHUB_TOKEN")
    
    # Full query with closing issues
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            pullRequests(
                first: 5,
                states: [MERGED],
                orderBy: {field: MERGED_AT, direction: DESC}
            ) {
                nodes {
                    number
                    title
                    url
                    mergedAt
                    baseRefName
                    mergeCommit {
                        oid
                    }
                    closingIssuesReferences(first: 10) {
                        nodes {
                            number
                            title
                            body
                            url
                            state
                            stateReason
                        }
                    }
                }
            }
        }
    }
    """
    
    variables = {
        "owner": "PrefectHQ",
        "name": "prefect"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if "errors" in result:
            print("Errors:", result["errors"])
        else:
            print("Success! Repository:", result["data"]["repository"]["name"])
            print("PRs:", result["data"]["repository"]["pullRequests"]["nodes"])

if __name__ == "__main__":
    asyncio.run(test_query())