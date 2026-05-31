from __future__ import annotations

from enum import Enum


class PaneKind(str, Enum):
    PROJECT = "project"
    STANDALONE = "standalone"


class PlanningPhase(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
