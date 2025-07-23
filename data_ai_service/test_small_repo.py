"""Test with a smaller repository."""
import asyncio
import httpx
import json

async def test_extract():
    """Test extraction endpoint with a smaller repo."""
    # Use a smaller repo for testing
    repo_url = "https://github.com/PrefectHQ/marvin"
    
    async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
        print(f"🔄 Extracting data from {repo_url}...")
        
        response = await client.post(
            "http://localhost:8001/github/extract",
            json={"repo_url": repo_url}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"  Dataset ID: {data['dataset_id']}")
            print(f"  PR-Issues count: {data['pr_issues_count']}")
        else:
            print(f"❌ Error: {response.text}")

async def list_datasets():
    """List all datasets."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8001/github/datasets")
        data = response.json()
        print(f"\n📊 Total datasets: {data['total']}")
        for ds in data['datasets']:
            print(f"  - {ds['repo_url']} (PRs: {ds['pr_count']})")

if __name__ == "__main__":
    # First start the server in a separate terminal:
    # uv run uvicorn main:app --port 8001
    print("Make sure the server is running: uv run uvicorn main:app --port 8001")
    input("Press Enter when ready...")
    
    asyncio.run(test_extract())
    asyncio.run(list_datasets())