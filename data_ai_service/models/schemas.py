"""Pydantic schemas for Data+AI Service."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# PR-Issue schemas
class PRIssueBase(BaseModel):
    pr_number: int
    pr_url: str
    pr_title: Optional[str] = None
    pr_merged_at: Optional[datetime] = None
    pr_base_branch: Optional[str] = None
    pr_merge_commit_sha: Optional[str] = None
    issue_number: int
    issue_url: str
    issue_title: Optional[str] = None
    issue_body: Optional[str] = None
    issue_state: Optional[str] = None
    issue_reason: Optional[str] = None


class PRIssueCreate(PRIssueBase):
    pass


class PRIssue(PRIssueBase):
    id: int
    dataset_id: str


# Dataset schemas
class DatasetBase(BaseModel):
    repo_name: str
    repo_url: str
    total_pr_issues: int


class DatasetCreate(DatasetBase):
    pass


class Dataset(DatasetBase):
    id: str
    created_at: datetime


class DatasetDetail(Dataset):
    pr_issues: List[PRIssue] = []