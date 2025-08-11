# data-ai-service/routers/github.py

"""GitHub API router for data extraction endpoints."""
import re
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy.engine import Connection

from database import crud
from models.database import get_db_connection
from services.github_service import GitHubClient


router = APIRouter(prefix="/github", tags=["github"])


class ExtractRequest(BaseModel):
    """Request model for data extraction."""
    repo_url: str
    
    @field_validator('repo_url')
    def validate_repo_url(cls, v):
        """Validate GitHub repository URL format."""
        pattern = r'^https://github\.com/[\w-]+/[\w-]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid GitHub repository URL format')
        return v


class ExtractResponse(BaseModel):
    """Response model for data extraction."""
    status: str
    dataset_id: str
    repo_url: str
    pr_issues_count: int


class DatasetListResponse(BaseModel):
    """Response model for dataset listing."""
    datasets: List[Dict[str, Any]]
    total: int
    skip: int = 0
    limit: int = 100


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str


def get_db() -> Connection:
    """Dependency to get database connection."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


@router.post("/extract", response_model=ExtractResponse)
async def extract_github_data(
    request: ExtractRequest,
    db: Connection = Depends(get_db)
) -> ExtractResponse:
    """Extract PR-issue data from a GitHub repository."""
    try:
        # Parse repo owner and name from URL
        match = re.match(r'https://github\.com/([\w-]+)/([\w-]+)$', request.repo_url)
        if not match:
            raise ValueError("Invalid repository URL")
        
        repo_owner, repo_name = match.groups()
        
        # Initialize GitHub client and fetch data
        client = GitHubClient()
        pr_issues = await client.fetch_pr_issue_data(repo_owner, repo_name)
        
        # Create dataset entry
        dataset = crud.create_dataset(
            db,
            repo_name=f"{repo_owner}/{repo_name}",
            repo_url=request.repo_url,
            total_pr_issues=len(pr_issues)
        )
        
        # Save PR-issue mappings
        if pr_issues:
            crud.save_pr_issues(db, dataset["id"], pr_issues)
        
        return ExtractResponse(
            status="success",
            dataset_id=dataset["id"],
            repo_url=request.repo_url,
            pr_issues_count=len(pr_issues)
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"GitHub API error: {str(e)}"
        )


@router.get("/datasets", response_model=DatasetListResponse)
def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db: Connection = Depends(get_db)
) -> DatasetListResponse:
    """List all extracted datasets."""
    datasets = crud.get_datasets(db, skip=skip, limit=limit)
    
    # Get total count (simple implementation - could be optimized)
    all_datasets = crud.get_datasets(db, skip=0, limit=10000)
    total = len(all_datasets)
    
    return DatasetListResponse(
        datasets=datasets,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/datasets/{dataset_id}")
def get_dataset_details(
    dataset_id: str,
    db: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed information about a specific dataset."""
    dataset = crud.get_dataset_details(db, dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset {dataset_id} not found"
        )
    
    return dataset