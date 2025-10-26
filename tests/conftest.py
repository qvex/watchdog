"""Shared pytest fixtures for Watchdog tests."""

import pytest
import tempfile
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_python_file() -> Generator[Path, None, None]:
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""def example_function(x, y):
    '''Example function for testing.'''
    return x + y


def another_function():
    '''Another function.'''
    for i in range(10):
        print(i)


class ExampleClass:
    '''Example class.'''
    def method(self):
        pass
""")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_code_before() -> str:
    """Sample Python code for before state."""
    return """def calculate_average(numbers):
    '''Calculate average of numbers.'''
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


def process_data(data):
    '''Process data.'''
    if not data:
        return None
    return [x * 2 for x in data]
"""


@pytest.fixture
def sample_code_after_function_deleted() -> str:
    """Sample code with function deleted."""
    return """def calculate_average(numbers):
    '''Calculate average of numbers.'''
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
"""


@pytest.fixture
def sample_code_after_loop_deleted() -> str:
    """Sample code with loop deleted."""
    return """def calculate_average(numbers):
    '''Calculate average of numbers.'''
    total = 0
    return total / len(numbers)


def process_data(data):
    '''Process data.'''
    if not data:
        return None
    return [x * 2 for x in data]
"""


@pytest.fixture
def sample_code_invalid_syntax() -> str:
    """Sample code with invalid syntax."""
    return """def broken_function(
    # Missing closing parenthesis and colon
    return x + y
"""


@pytest.fixture
def sample_code_empty() -> str:
    """Empty Python file."""
    return ""


@pytest.fixture
def sample_code_with_class() -> str:
    """Sample code with class definition."""
    return """class Calculator:
    '''Simple calculator class.'''

    def add(self, x, y):
        return x + y

    def subtract(self, x, y):
        return x - y
"""
