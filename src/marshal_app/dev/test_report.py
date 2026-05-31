from __future__ import annotations

import sys
import time
import unittest
from dataclasses import dataclass
from pathlib import Path


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"


def _supports_color() -> bool:
    return sys.stdout.isatty()


def _paint(text: str, color: str) -> str:
    if not _supports_color():
        return text
    return f"{color}{text}{RESET}"


def _banner(text: str) -> str:
    return _paint(text, BOLD + CYAN)


def _frame(lines: list[str], width: int = 66) -> list[str]:
    top = f"+{'-' * (width - 2)}+"
    framed = [top]
    for line in lines:
        framed.append(f"| {line:<{width - 4}} |")
    framed.append(top)
    return framed


def _section_title(title: str) -> str:
    return _paint(f"== {title} {('=' * max(0, 52 - len(title)))}", BOLD + WHITE)


@dataclass(slots=True)
class TestEvent:
    name: str
    outcome: str
    seconds: float
    detail: str = ""


class FancyTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):  # noqa: D401
        super().__init__(stream, descriptions, verbosity)
        self._passed = 0

    def startTestRun(self) -> None:  # noqa: N802 - unittest API
        super().startTestRun()
        self._run_started_at = time.perf_counter()
        for line in _frame(
            [
                "marshal test diagnostics",
                "colorized terminal report",
                "suite discovery and execution",
            ]
        ):
            print(_banner(line))
        print()
        print(_section_title("Discovery"))
        print(_paint("Scanning tests and preparing execution order...\n", DIM + CYAN))
        self._events: list[TestEvent] = []

    def startTest(self, test: unittest.case.TestCase) -> None:  # noqa: N802 - unittest API
        self._started_at = time.perf_counter()
        print(_paint(f"┌─ {test.id()}", CYAN))
        super().startTest(test)

    def addSuccess(self, test: unittest.case.TestCase) -> None:  # noqa: N802 - unittest API
        super().addSuccess(test)
        elapsed = time.perf_counter() - self._started_at
        self._passed += 1
        self._events.append(TestEvent(test.id(), "PASS", elapsed))
        print(_paint(f"│  PASS  {test.id().split('.')[-1]}  [{elapsed:.3f}s]", GREEN))

    def addFailure(self, test: unittest.case.TestCase, err) -> None:  # noqa: N802 - unittest API
        super().addFailure(test, err)
        elapsed = time.perf_counter() - self._started_at
        detail = self._exc_info_to_string(err, test)
        self._events.append(TestEvent(test.id(), "FAIL", elapsed, detail))
        print(_paint(f"│  FAIL  {test.id().split('.')[-1]}  [{elapsed:.3f}s]", RED))

    def addError(self, test: unittest.case.TestCase, err) -> None:  # noqa: N802 - unittest API
        super().addError(test, err)
        elapsed = time.perf_counter() - self._started_at
        detail = self._exc_info_to_string(err, test)
        self._events.append(TestEvent(test.id(), "ERROR", elapsed, detail))
        print(_paint(f"│  ERROR {test.id().split('.')[-1]}  [{elapsed:.3f}s]", MAGENTA))

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:  # noqa: N802 - unittest API
        super().addSkip(test, reason)
        elapsed = time.perf_counter() - self._started_at
        self._events.append(TestEvent(test.id(), "SKIP", elapsed, reason))
        print(_paint(f"│  SKIP  {test.id().split('.')[-1]}  [{elapsed:.3f}s]  {reason}", YELLOW))

    def stopTestRun(self) -> None:  # noqa: N802 - unittest API
        super().stopTestRun()
        total_seconds = time.perf_counter() - self._run_started_at
        passed = self._passed
        failed = len(self.failures)
        errors = len(self.errors)
        skipped = len(self.skipped)
        total = self.testsRun

        print()
        print(_section_title("Summary"))
        for line in _frame(
            [
                f"total   : {total}",
                f"passed  : {passed}",
                f"failed  : {failed}",
                f"errors  : {errors}",
                f"skipped : {skipped}",
                f"runtime : {total_seconds:.3f}s",
            ],
            width=40,
        ):
            print(_paint(line, DIM if ":" in line else WHITE))

        print()
        print(_section_title("Results"))
        for event in self._events:
            color = GREEN if event.outcome == "PASS" else RED if event.outcome in {"FAIL", "ERROR"} else YELLOW
            print(_paint(f"{event.outcome:<6} {event.seconds:>7.3f}s  {event.name}", color))

        if self.failures or self.errors:
            print()
            print(_section_title("Failures"))
            for test, detail in [*self.failures, *self.errors]:
                print(_paint(f"\n+-- {test.id()} --", RED))
                print(detail)


class FancyTestRunner(unittest.TextTestRunner):
    resultclass = FancyTestResult


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    src_root = repo_root / "src"
    tests_root = repo_root / "tests"

    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    loader = unittest.defaultTestLoader
    suite = loader.discover(str(tests_root), pattern="test*.py")

    runner = FancyTestRunner(stream=sys.stdout, verbosity=2, descriptions=False)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
