import subprocess
import json
import re
from pathlib import Path
from typing import List
from src.test_domain import RunResult, FailureInfo, TestStatus
from src.effects import Result, Success, Failure, ErrorType


class PytestRunner:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def run_tests(
        self,
        file_path: str
    ) -> Result[RunResult, ErrorType]:
        if not Path(file_path).exists():
            return Failure(ErrorType.FILE_ERROR, f"File not found: {file_path}")

        exec_result = self._execute_pytest(file_path)

        match exec_result:
            case Success(output):
                return Success(self._parse_output(output))
            case Failure(error, context):
                return Failure(error, context)

    def discover_tests(
        self,
        directory: str
    ) -> Result[List[str], ErrorType]:
        if not Path(directory).is_dir():
            return Failure(ErrorType.FILE_ERROR, f"Directory not found: {directory}")

        cmd = ["pytest", "--collect-only", "-q", directory]
        exec_result = self._run_command(cmd)

        match exec_result:
            case Success(output):
                test_files = self._extract_test_files(output)
                return Success(test_files)
            case Failure(error, context):
                return Failure(error, context)

    def _execute_pytest(
        self,
        file_path: str
    ) -> Result[str, ErrorType]:
        cmd = [
            "pytest",
            file_path,
            "-v",
            "--tb=short",
            "--no-header",
            "--no-summary"
        ]
        return self._run_command(cmd)

    def _run_command(
        self,
        cmd: List[str]
    ) -> Result[str, ErrorType]:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return Success(result.stdout + result.stderr)
        except subprocess.TimeoutExpired:
            return Failure(ErrorType.TEST_ERROR, "Test execution timeout")
        except FileNotFoundError:
            return Failure(ErrorType.TEST_ERROR, "pytest not found")
        except Exception as e:
            return Failure(ErrorType.TEST_ERROR, str(e))

    def _parse_output(
        self,
        output: str
    ) -> RunResult:
        lines = output.split('\n')
        passed = self._count_status(lines, 'PASSED')
        failed = self._count_status(lines, 'FAILED')
        errors = self._count_status(lines, 'ERROR')
        total = passed + failed + errors
        failures = self._extract_failures(lines)

        return RunResult(
            total_tests=total,
            passed=passed,
            failed=failed,
            errors=errors,
            duration=0.0,
            failures=failures
        )

    def _count_status(
        self,
        lines: List[str],
        status: str
    ) -> int:
        return sum(1 for line in lines if status in line)

    def _extract_failures(
        self,
        lines: List[str]
    ) -> List[FailureInfo]:
        failures = []
        i = 0

        while i < len(lines):
            if 'FAILED' in lines[i]:
                failure = self._parse_failure(lines, i)
                if failure:
                    failures.append(failure)
            i += 1

        return failures

    def _parse_failure(
        self,
        lines: List[str],
        start_idx: int
    ) -> FailureInfo | None:
        test_line = lines[start_idx]
        test_name = self._extract_test_name(test_line)

        message_lines = []
        for i in range(start_idx + 1, min(start_idx + 10, len(lines))):
            if 'FAILED' in lines[i] or 'PASSED' in lines[i]:
                break
            message_lines.append(lines[i])

        return FailureInfo(
            test_name=test_name,
            failure_message='\n'.join(message_lines).strip(),
            line_number=None
        )

    def _extract_test_name(
        self,
        line: str
    ) -> str:
        match = re.search(r'test_\w+', line)
        return match.group(0) if match else "unknown"

    def _extract_test_files(
        self,
        output: str
    ) -> List[str]:
        lines = output.split('\n')
        test_files = []

        for line in lines:
            if 'test_' in line and '.py' in line:
                test_files.append(line.strip())

        return test_files


class SimpleTestDetector:
    def has_tests(
        self,
        file_path: str
    ) -> bool:
        test_file = self.get_test_file(file_path)
        return test_file is not None and Path(test_file).exists()

    def get_test_file(
        self,
        source_file: str
    ) -> str | None:
        path = Path(source_file)
        test_name = f"test_{path.stem}.py"
        test_path = path.parent / "tests" / test_name

        if test_path.exists():
            return str(test_path)

        alt_test_path = path.parent / test_name
        if alt_test_path.exists():
            return str(alt_test_path)

        return None
