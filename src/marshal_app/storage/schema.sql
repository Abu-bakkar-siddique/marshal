PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    sort_order  INTEGER NOT NULL,
    is_closed   INTEGER NOT NULL DEFAULT 0 CHECK (is_closed IN (0, 1)),
    closed_at   TEXT,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sections (
    id          INTEGER PRIMARY KEY,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER PRIMARY KEY,
    project_id   INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    section_id   INTEGER REFERENCES sections(id) ON DELETE SET NULL,
    title        TEXT NOT NULL,
    comments     TEXT NOT NULL DEFAULT '',
    is_done      INTEGER NOT NULL DEFAULT 0 CHECK (is_done IN (0, 1)),
    sort_order   INTEGER NOT NULL,
    completed_at TEXT,
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (section_id IS NULL OR project_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS task_checkpoints (
    id          INTEGER PRIMARY KEY,
    task_id     INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    body        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_projects_sort_order
    ON projects(sort_order);

CREATE INDEX IF NOT EXISTS idx_sections_project
    ON sections(project_id);

CREATE INDEX IF NOT EXISTS idx_tasks_project_order
    ON tasks(project_id, sort_order);

CREATE INDEX IF NOT EXISTS idx_tasks_section_order
    ON tasks(section_id, sort_order);

CREATE INDEX IF NOT EXISTS idx_tasks_project_incomplete
    ON tasks(project_id, sort_order)
    WHERE is_done = 0;

CREATE INDEX IF NOT EXISTS idx_tasks_project_completed
    ON tasks(project_id, completed_at)
    WHERE is_done = 1;

CREATE INDEX IF NOT EXISTS idx_checkpoints_task_created
    ON task_checkpoints(task_id, created_at DESC);
