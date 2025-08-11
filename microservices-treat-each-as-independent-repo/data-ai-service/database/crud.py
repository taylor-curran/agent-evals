# data-ai-service/database/crud.py

"""Database CRUD operations for Data+AI Service."""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import text
from datetime import datetime

from models.database import get_db_connection


def create_dataset(
    db_connection,
    repo_name: str,
    repo_url: str,
    total_pr_issues: int
) -> Dict[str, Any]:
    """Create a new dataset entry."""
    dataset_id = str(uuid.uuid4())
    
    query = text("""
        INSERT INTO datasets (id, repo_url, pr_count, issue_count)
        VALUES (:id, :repo_url, :pr_count, :issue_count)
    """)
    
    db_connection.execute(query, {
        "id": dataset_id,
        "repo_url": repo_url,
        "pr_count": total_pr_issues,
        "issue_count": total_pr_issues  # Assuming 1:1 for now
    })
    db_connection.commit()
    
    # Return the created dataset
    return {
        "id": dataset_id,
        "repo_name": repo_name,
        "repo_url": repo_url,
        "total_pr_issues": total_pr_issues,
        "created_at": datetime.now()
    }


def save_pr_issues(
    db_connection,
    dataset_id: str,
    pr_issues_data: List[dict]
) -> List[Dict[str, Any]]:
    """Bulk insert PR-issue mappings."""
    query = text("""
        INSERT INTO pr_issues (
            dataset_id, pr_number, pr_url, pr_title, pr_merged_at,
            pr_base_branch, pr_merge_commit_sha,
            issue_number, issue_url, issue_title, issue_body,
            issue_state, issue_reason
        ) VALUES (
            :dataset_id, :pr_number, :pr_url, :pr_title, :pr_merged_at,
            :pr_base_branch, :pr_merge_commit_sha,
            :issue_number, :issue_url, :issue_title, :issue_body,
            :issue_state, :issue_reason
        )
    """)
    
    pr_issues = []
    for data in pr_issues_data:
        params = {
            "dataset_id": dataset_id,
            "pr_number": data["pr_number"],
            "pr_url": data["pr_url"],
            "pr_title": data.get("pr_title"),  # Nullable
            "pr_merged_at": data.get("pr_merged_at"),
            "pr_base_branch": data.get("pr_base_branch"),  # Nullable
            "pr_merge_commit_sha": data.get("pr_merge_commit_sha"),  # Nullable
            "issue_number": data["issue_number"],
            "issue_url": data["issue_url"],
            "issue_title": data.get("issue_title"),  # Nullable
            "issue_body": data.get("issue_body"),  # Nullable
            "issue_state": data.get("issue_state"),
            "issue_reason": data.get("issue_reason")
        }
        
        result = db_connection.execute(query, params)
        pr_issues.append({
            "id": result.lastrowid,
            **params
        })
    
    db_connection.commit()
    return pr_issues


def get_datasets(db_connection, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all datasets."""
    query = text("""
        SELECT id, repo_url, created_at, pr_count, issue_count
        FROM datasets
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :skip
    """)
    
    result = db_connection.execute(query, {"skip": skip, "limit": limit})
    return [dict(row._mapping) for row in result]


def get_dataset_details(db_connection, dataset_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific dataset with its PR-issue mappings."""
    # Get dataset info
    dataset_query = text("""
        SELECT id, repo_url, created_at, pr_count, issue_count
        FROM datasets
        WHERE id = :dataset_id
    """)
    
    dataset_result = db_connection.execute(dataset_query, {"dataset_id": dataset_id})
    dataset_row = dataset_result.fetchone()
    
    if not dataset_row:
        return None
    
    dataset = dict(dataset_row._mapping)
    
    # Get PR-issues for this dataset
    pr_issues_query = text("""
        SELECT *
        FROM pr_issues
        WHERE dataset_id = :dataset_id
        ORDER BY pr_number, issue_number
    """)
    
    pr_issues_result = db_connection.execute(pr_issues_query, {"dataset_id": dataset_id})
    pr_issues = [dict(row._mapping) for row in pr_issues_result]
    
    dataset["pr_issues"] = pr_issues
    return dataset