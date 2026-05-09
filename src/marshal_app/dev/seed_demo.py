from __future__ import annotations

from marshal_app.app.settings import DEFAULT_SETTINGS
from marshal_app.storage.db import connect, initialize_database


PROJECT_ROWS = [
    (
        1,
        "Calculus for ML/AI",
        "Core math topics before diving into models. Use this one to test reordering and active task movement.",
        100,
        0,
    ),
    (
        2,
        "Build marshal v1",
        "A product build queue with a few completed items so the progress block and completed area are easy to verify.",
        200,
        0,
    ),
    (
        3,
        "Job Hunt System",
        "A second live project to make sidebar switching feel realistic while testing.",
        300,
        0,
    ),
]

TASK_ROWS = [
    (1, 1, None, "Build intuition for derivatives", "Start with slope and rate-of-change intuition before formulas.", 0, 100, None),
    (2, 1, None, "Understand the chain rule deeply", "This should stay near the top. Good candidate for reordering tests.", 0, 200, None),
    (3, 1, None, "Practice partial derivatives", "Use 3-4 concrete multivariable examples.", 0, 300, None),
    (4, 1, None, "Review gradient descent intuition", "Think in terms of moving opposite the gradient on a loss surface.", 0, 400, None),
    (5, 1, None, "Read about Jacobians conceptually", "Nice-to-have topic. Good item to drag further down.", 0, 500, None),
    (6, 1, None, "Limits and continuity refresher", "This one is already done and should appear in the completed section.", 1, 600, "2026-05-03 10:30:00"),
    (7, 1, None, "Integration as accumulation", "Also completed so progress is not starting from zero.", 1, 700, "2026-05-03 11:00:00"),

    (8, 2, None, "Lock SQLite schema", "This mirrors the current architecture work and gives a second project queue.", 1, 100, "2026-05-03 09:00:00"),
    (9, 2, None, "Wire project selection into main window", "Already done in the current build.", 1, 200, "2026-05-03 09:30:00"),
    (10, 2, None, "Implement task reordering", "This should be the active task in the seeded marshal project.", 0, 300, None),
    (11, 2, None, "Add checkpoint prompt on active-task switch", "Next behavior after reordering.", 0, 400, None),
    (12, 2, None, "Add contiguous task sections", "Organizational grouping only, no separate queue logic.", 0, 500, None),
    (13, 2, None, "Support standalone task persistence", "Secondary feature. Useful once the main project workflow is stable.", 0, 600, None),

    (14, 3, None, "Refresh resume bullet points", "Keep this brief and measurable.", 0, 100, None),
    (15, 3, None, "Compile target company list", "A flat queue is enough here.", 0, 200, None),
    (16, 3, None, "Prepare outreach template", "Could move higher if you want to test priority shifts.", 0, 300, None),
    (17, 3, None, "Send first 5 applications", "Done task to verify completion state in a shorter project.", 1, 400, "2026-05-02 18:20:00"),

    (18, None, None, "Pay electricity bill", "Standalone because it is not part of any project queue.", 0, 100, None),
    (19, None, None, "Call mechanic", "Quick personal follow-up with no project context.", 0, 200, None),
    (20, None, None, "Back up laptop", "Already handled; useful for checking standalone completed state.", 1, 300, "2026-05-04 15:45:00"),
]

CHECKPOINT_ROWS = [
    (1, 2, "Stopped here because I needed better intuition for derivatives first.", "2026-05-03 11:40:00"),
    (2, 10, "Left off after finishing repository wiring. Next is the checkpoint modal on reorder.", "2026-05-03 12:15:00"),
]


def main() -> int:
    database_path = DEFAULT_SETTINGS.database_path
    initialize_database(database_path)

    with connect(database_path) as connection:
        connection.execute("DELETE FROM task_checkpoints")
        connection.execute("DELETE FROM tasks")
        connection.execute("DELETE FROM sections")
        connection.execute("DELETE FROM projects")

        connection.executemany(
            """
            INSERT INTO projects (id, title, description, sort_order, is_closed)
            VALUES (?, ?, ?, ?, ?)
            """,
            PROJECT_ROWS,
        )
        connection.executemany(
            """
            INSERT INTO tasks (
                id, project_id, section_id, title, comments, is_done, sort_order, completed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            TASK_ROWS,
        )
        connection.executemany(
            """
            INSERT INTO task_checkpoints (id, task_id, body, created_at)
            VALUES (?, ?, ?, ?)
            """,
            CHECKPOINT_ROWS,
        )
        connection.commit()

    print(f"Seeded demo data into {database_path}")
    print("Projects:", len(PROJECT_ROWS))
    print("Tasks:", len(TASK_ROWS))
    print("Checkpoints:", len(CHECKPOINT_ROWS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
