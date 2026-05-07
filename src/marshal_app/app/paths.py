from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "marshal"
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PACKAGE_ROOT.parent
PROJECT_ROOT = SOURCE_ROOT.parent
DEFAULT_DATA_DIR = PROJECT_ROOT / ".marshal-data"
USER_DATA_DIR = Path(os.environ.get("MARSHAL_DATA_DIR", DEFAULT_DATA_DIR))
DATABASE_PATH = USER_DATA_DIR / "marshal.db"
