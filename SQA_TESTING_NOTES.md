# SQA Testing Notes

This note explains what I added for the software quality assurance presentation, in simple terms.
It is not the main product philosophy. It is just the testing-focused version of the work we did for class.

## What We Did

We built out a much richer test setup for the `marshal` project.

The main goal was to show that the app is not just code that runs, but code that is checked properly.
That matters a lot for SQA, because testing is the point of the course.

The work included:

- a smaller core test file for the basic workflow checks
- a larger presentation-style test suite with broader coverage
- a fancy terminal test reporter with colors and a cleaner log layout

## Why We Did It

The idea was to make the test story strong for the presentation.

Instead of only showing source code, we now have a clear test suite that demonstrates:

- domain logic works correctly
- SQLite schema and integrity rules are being exercised
- repositories return the right data
- services are wired correctly
- planning behavior handles different kinds of input

That gives a much better SQA story than just saying the app exists.

## What the Test Suite Covers

The test suite now checks a lot of the project’s important behavior:

- active task selection
- project progress calculation
- project closing rules
- project creation and ordering
- task creation, completion, listing, and reordering
- section listing
- checkpoint lookup
- planning draft generation and revision flow
- approval into structured output
- SQLite table and index creation
- foreign key integrity
- service container wiring

In total, the suite currently has `28` test cases.

## How We Built It

We kept the new presentation suite separate from the existing tests.
That was intentional.

The new suite lives in:

- [tests/test_sqa_suite.py](./tests/test_sqa_suite.py)

The test files use normal `unittest` tests, so they are easy to run from the project root.
For the presentation, we also added a custom terminal runner that prints a more polished log.

The fancy runner lives in:

- [src/marshal_app/dev/test_report.py](./src/marshal_app/dev/test_report.py)

And the command for it is:

```bash
python -m marshal_app.dev.test_report
```

## How To Run The Tests

From the `marshal/` root, run:

```bash
python -m unittest discover -s tests -v
```

If you want the colorized presentation output, run:

```bash
python -m marshal_app.dev.test_report
```

## Presentation Angle

For the SQA presentation, the important message is:

the project now has tests that prove behavior, not just code that looks finished.

That is the main point to emphasize.

The testing work is intentionally separate from the actual product philosophy.
This file is just the presentation/testing layer, so it can be shown, explained, and then removed later if needed.
