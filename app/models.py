# app/models.py

from sqlmodel import SQLModel, Field


class Prompt(SQLModel, table=True):
    """Prompt row persisted in SQLite (proto)."""

    pr_number: int | None = Field(default=None, primary_key=True)
    prompt_text: str
