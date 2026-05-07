from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Project:
    id: int | None
    title: str
    description: str = ""
    sort_order: int = 0
    is_closed: bool = False
    closed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class Section:
    id: int | None
    project_id: int
    title: str
    description: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class Task:
    id: int | None
    title: str
    project_id: int | None = None
    section_id: int | None = None
    comments: str = ""
    is_done: bool = False
    sort_order: int = 0
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class TaskCheckpoint:
    id: int | None
    task_id: int
    body: str
    created_at: datetime | None = None
