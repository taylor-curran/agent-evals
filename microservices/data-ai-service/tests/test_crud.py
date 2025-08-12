# data-ai-service/tests/test_crud.py

import pytest

from database import crud


def test_create_dataset(test_db, sample_dataset_data):
    """Test creating a new dataset entry"""
    dataset = crud.create_dataset(
        db_connection=test_db,
        repo_name=sample_dataset_data["repo_name"],
        repo_url=sample_dataset_data["repo_url"],
        total_pr_issues=sample_dataset_data["total_pr_issues"]
    )
    
    assert dataset["id"] is not None
    assert dataset["repo_name"] == sample_dataset_data["repo_name"]
    assert dataset["repo_url"] == sample_dataset_data["repo_url"]
    assert dataset["total_pr_issues"] == sample_dataset_data["total_pr_issues"]
    assert dataset["created_at"] is not None


def test_save_pr_issues(test_db, sample_dataset_data, sample_pr_issue_data):
    """Test bulk inserting PR-issue mappings"""
    # First create a dataset
    dataset = crud.create_dataset(
        db_connection=test_db,
        repo_name=sample_dataset_data["repo_name"],
        repo_url=sample_dataset_data["repo_url"],
        total_pr_issues=len(sample_pr_issue_data)
    )
    
    # Then save PR-issues
    pr_issues = crud.save_pr_issues(
        db_connection=test_db,
        dataset_id=dataset["id"],
        pr_issues_data=sample_pr_issue_data
    )
    
    assert len(pr_issues) == 2
    assert pr_issues[0]["pr_number"] == 123
    assert pr_issues[0]["issue_number"] == 100
    assert pr_issues[1]["pr_number"] == 124
    assert pr_issues[1]["issue_number"] == 101


def test_get_datasets(test_db, sample_dataset_data):
    """Test listing all datasets"""
    # Create multiple datasets
    for i in range(3):
        crud.create_dataset(
            db_connection=test_db,
            repo_name=f"test-owner/test-repo-{i}",
            repo_url=f"https://github.com/test-owner/test-repo-{i}",
            total_pr_issues=i + 1
        )
    
    datasets = crud.get_datasets(db_connection=test_db)
    
    assert len(datasets) == 3
    # Note: Results are ordered by created_at DESC, so newest first
    assert "test-owner/test-repo" in datasets[0]["repo_url"]
    assert "test-owner/test-repo" in datasets[1]["repo_url"]
    assert "test-owner/test-repo" in datasets[2]["repo_url"]


def test_get_dataset_details(test_db, sample_dataset_data, sample_pr_issue_data):
    """Test fetching full dataset with PR-issues"""
    # Create dataset with PR-issues
    dataset = crud.create_dataset(
        db_connection=test_db,
        repo_name=sample_dataset_data["repo_name"],
        repo_url=sample_dataset_data["repo_url"],
        total_pr_issues=len(sample_pr_issue_data)
    )
    
    crud.save_pr_issues(
        db_connection=test_db,
        dataset_id=dataset["id"],
        pr_issues_data=sample_pr_issue_data
    )
    
    # Fetch dataset with details
    dataset_details = crud.get_dataset_details(db_connection=test_db, dataset_id=dataset["id"])
    
    assert dataset_details is not None
    assert dataset_details["id"] == dataset["id"]
    assert dataset_details["repo_url"] == sample_dataset_data["repo_url"]
    assert len(dataset_details["pr_issues"]) == 2
    assert dataset_details["pr_issues"][0]["pr_number"] == 123
    assert dataset_details["pr_issues"][1]["pr_number"] == 124


def test_get_dataset_details_not_found(test_db):
    """Test fetching non-existent dataset returns None"""
    dataset_details = crud.get_dataset_details(db_connection=test_db, dataset_id="nonexistent-id")
    assert dataset_details is None