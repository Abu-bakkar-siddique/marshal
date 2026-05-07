from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from marshal_app.app.paths import DATABASE_PATH


@dataclass(slots=True, frozen=True)
class AppSettings:
    app_name: str = "marshal"
    organization_name: str = "marshal"
    database_path: Path = DATABASE_PATH


DEFAULT_SETTINGS = AppSettings()
