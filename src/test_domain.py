from typing import Protocol, List
from dataclasses import dataclass
from enum import Enum, auto
from src.effects import Result, ErrorType


class TestStatus(Enum):
    PASSED = auto()
    FAILED = auto()
    ERROR = auto()
    SKIPPED = auto()


@dataclass(frozen=True, slots=True)
class FailureInfo:
    test_name: str
    failure_message: str
    line_number: int | None = None
    traceback: str = ""


@dataclass(frozen=True, slots=True)
class RunResult:
    total_tests: int
    passed: int
    failed: int
    errors: int
    duration: float
    failures: List[FailureInfo]


class TestRunner(Protocol):
    def run_tests(
        self,
        file_path: str
    ) -> Result[RunResult, ErrorType]:
        ...

    def discover_tests(
        self,
        directory: str
    ) -> Result[List[str], ErrorType]:
        ...


class TestDetector(Protocol):
    def has_tests(
        self,
        file_path: str
    ) -> bool:
        ...

    def get_test_file(
        self,
        source_file: str
    ) -> str | None:
        ...
