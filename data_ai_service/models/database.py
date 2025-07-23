"""Database initialization and connection management for Data+AI Service.

This module handles SQLite database setup and ensures required tables exist.
"""
from pathlib import Path
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATABASE_URL = "sqlite:///./data_ai_service.db"  # relative to project root
DB_PATH = Path(__file__).resolve().parent.parent.parent / "data_ai_service.db"

CREATE_TABLE_STATEMENTS = [
    # datasets
    """
    CREATE TABLE IF NOT EXISTS datasets (
        id TEXT PRIMARY KEY,
        repo_url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        pr_count INTEGER,
        issue_count INTEGER
    );
    """,
    # pr_issues
    """
    CREATE TABLE IF NOT EXISTS pr_issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id TEXT REFERENCES datasets(id),
        
        -- PR fields
        pr_number INTEGER,
        pr_url TEXT,
        pr_title TEXT,
        pr_merged_at TIMESTAMP,
        pr_base_branch TEXT,
        pr_merge_commit_sha TEXT,
        
        -- Issue fields
        issue_number INTEGER,
        issue_url TEXT,
        issue_title TEXT,
        issue_body TEXT,
        issue_state TEXT,
        issue_reason TEXT
    );
    """,
    # prompts
    """
    CREATE TABLE IF NOT EXISTS prompts (
        id TEXT PRIMARY KEY,
        dataset_id TEXT REFERENCES datasets(id),
        pr_number INTEGER,
        prompt_text TEXT,
        mode TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
]

# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create SQLite DB file and ensure required tables exist."""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    with engine.begin() as conn:
        for stmt in CREATE_TABLE_STATEMENTS:
            conn.execute(text(stmt))


def get_engine():
    """Get a SQLAlchemy engine for the database."""
    return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def get_db_connection():
    """Get a raw database connection for SQL queries."""
    engine = get_engine()
    return engine.connect()
