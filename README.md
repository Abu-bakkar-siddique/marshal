# marshal

`marshal` is a local-first Linux desktop task manager built with Python, PySide6, and SQLite.

The app is structured around ordered project task queues:

- a project represents one concrete job or objective
- task order defines queue priority
- the first incomplete project task is implicitly active
- sections are organizational wrappers over contiguous task ranges
- checkpoints record where work paused when focus changes

## Tech stack

- Python 3.11+
- PySide6
- SQLite

## Current state

This repository currently contains the initial scaffold:

- app bootstrap and paths
- UI shell and placeholder views
- domain models and rules
- SQLite schema and repository layer skeleton
- service layer skeleton
- reserved integration modules for future AI, Slack, and WhatsApp work

## Planned next step

Implement the first vertical slice:

- project list in the sidebar
- create/select project
- project progress header
- ordered task list
- active task derivation
- add/edit/delete/reorder task flow
