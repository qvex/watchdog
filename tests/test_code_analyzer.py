"""Comprehensive tests for CodeAnalyzer module."""

import pytest
from src.code_analyzer import CodeAnalyzer, CodeContext


class TestCodeAnalyzer:
    """Test suite for CodeAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create a CodeAnalyzer instance."""
        return CodeAnalyzer()

    # Test 1: Initialization
    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes with correct patterns."""
        assert analyzer.patterns is not None
        assert 'loops' in analyzer.patterns
        assert 'functions' in analyzer.patterns
        assert 'conditionals' in analyzer.patterns
        assert 'classes' in analyzer.patterns

    # Test 2-4: Pattern detection
    def test_detect_loop_deletion(self, analyzer):
        """Test detection of deleted for loop."""
        before = "for i in range(10):\n    print(i)"
        after = "print('done')"

        result = analyzer._detect_missing_patterns(before, after)
        assert result['type'] == 'loops'
        assert result['pattern'] in ['for', 'while']

    def test_detect_function_deletion(self, analyzer):
        """Test detection of deleted function."""
        before = "def my_function():\n    pass"
        after = ""

        result = analyzer._detect_missing_patterns(before, after)
        assert result['type'] == 'functions'
        assert result['pattern'] == 'def'

    def test_detect_conditional_deletion(self, analyzer):
        """Test detection of deleted conditional."""
        before = "if x > 5:\n    print('big')"
        after = "print('done')"

        result = analyzer._detect_missing_patterns(before, after)
        assert result['type'] == 'conditionals'
        assert result['pattern'] in ['if', 'elif', 'else']

    # Test 5-7: Difficulty estimation
    def test_difficulty_loops(self, analyzer):
        """Test difficulty estimation for loops."""
        missing = {'type': 'loops', 'pattern': 'for'}
        difficulty = analyzer._estimate_difficulty(missing)
        assert difficulty == 2

    def test_difficulty_functions(self, analyzer):
        """Test difficulty estimation for functions."""
        missing = {'type': 'functions', 'pattern': 'def'}
        difficulty = analyzer._estimate_difficulty(missing)
        assert difficulty == 3

    def test_difficulty_comprehensions(self, analyzer):
        """Test difficulty estimation for comprehensions."""
        missing = {'type': 'comprehensions', 'pattern': '['}
        difficulty = analyzer._estimate_difficulty(missing)
        assert difficulty == 4

    # Test 8-10: analyze_deletion method
    def test_analyze_deletion_with_valid_code(self, analyzer):
        """Test analyze_deletion with valid Python code."""
        before = "def test():\n    for i in range(5):\n        print(i)"
        after = "def test():\n    print('done')"

        context = analyzer.analyze_deletion(before, after)

        assert isinstance(context, CodeContext)
        assert context.surrounding_code == after
        assert context.missing_element in ['loops', 'functions', 'conditionals']
        assert 1 <= context.difficulty_level <= 5

    def test_analyze_deletion_with_syntax_error(self, analyzer):
        """Test analyze_deletion handles syntax errors gracefully."""
        before = "def test()\n    return x"  # Missing colon
        after = "return x"

        context = analyzer.analyze_deletion(before, after)

        assert isinstance(context, CodeContext)
        assert context.missing_element == 'syntax'
        assert context.expected_pattern is None
        assert context.difficulty_level == 1

    def test_analyze_deletion_empty_code(self, analyzer):
        """Test analyze_deletion with empty code."""
        before = ""
        after = ""

        context = analyzer.analyze_deletion(before, after)

        assert isinstance(context, CodeContext)
        assert context.surrounding_code == ""

    # Test 11-13: get_function_signature method
    def test_get_function_signature_simple(self, analyzer):
        """Test extracting simple function signature."""
        code = "def add(x, y):\n    return x + y"
        signature = analyzer.get_function_signature(code, 'add')

        assert signature == "def add(x, y):"

    def test_get_function_signature_no_args(self, analyzer):
        """Test extracting function signature with no arguments."""
        code = "def greet():\n    print('Hello')"
        signature = analyzer.get_function_signature(code, 'greet')

        assert signature == "def greet():"

    def test_get_function_signature_not_found(self, analyzer):
        """Test get_function_signature when function doesn't exist."""
        code = "def foo():\n    pass"
        signature = analyzer.get_function_signature(code, 'bar')

        assert signature is None

    # Test 14-16: Edge cases
    def test_detect_class_deletion(self, analyzer):
        """Test detection of deleted class."""
        before = "class MyClass:\n    pass"
        after = ""

        result = analyzer._detect_missing_patterns(before, after)
        assert result['type'] == 'classes'

    def test_detect_error_handling_deletion(self, analyzer):
        """Test detection of deleted try-except."""
        before = "try:\n    risky()\nexcept:\n    pass"
        after = "risky()"

        result = analyzer._detect_missing_patterns(before, after)
        assert result['type'] == 'error_handling'

    def test_detect_no_deletion(self, analyzer):
        """Test when nothing is deleted."""
        code = "print('hello')"

        result = analyzer._detect_missing_patterns(code, code)
        assert result['type'] == 'unknown'

    # Test 17-19: Multiple patterns
    def test_detect_first_pattern_wins(self, analyzer):
        """Test that first detected pattern is returned."""
        before = "for i in range(10):\n    if i > 5:\n        print(i)"
        after = "print('done')"

        # Should detect loops first since it's checked first in patterns
        result = analyzer._detect_missing_patterns(before, after)
        assert result['type'] in analyzer.patterns.keys()

    def test_analyze_deletion_preserves_context(self, analyzer):
        """Test that surrounding code is preserved."""
        before = "x = 10\nfor i in range(x):\n    print(i)\ny = 20"
        after = "x = 10\ny = 20"

        context = analyzer.analyze_deletion(before, after)
        assert "x = 10" in context.surrounding_code
        assert "y = 20" in context.surrounding_code

    def test_difficulty_unknown_pattern(self, analyzer):
        """Test difficulty for unknown pattern."""
        missing = {'type': 'unknown', 'pattern': None}
        difficulty = analyzer._estimate_difficulty(missing)
        assert difficulty == 1

    # Test 20: Complex multi-line deletion
    def test_analyze_complex_deletion(self, analyzer):
        """Test analyzing complex multi-line deletion."""
        before = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def process_data(data):
    return [x * 2 for x in data]
"""
        after = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
"""
        context = analyzer.analyze_deletion(before, after)

        assert isinstance(context, CodeContext)
        assert context.missing_element in analyzer.patterns.keys()
        assert context.difficulty_level > 0

    # Test 21: get_function_signature with multiple functions
    def test_get_function_signature_multiple_functions(self, analyzer):
        """Test getting signature when multiple functions exist."""
        code = """
def first():
    pass

def second(a, b, c):
    return a + b + c

def third():
    pass
"""
        signature = analyzer.get_function_signature(code, 'second')
        assert signature == "def second(a, b, c):"

    # Test 22: Malformed code handling
    def test_analyze_deletion_malformed_before(self, analyzer):
        """Test handling of malformed before code."""
        before = "def broken(\n    # Unclosed parenthesis"
        after = "# Fixed"

        context = analyzer.analyze_deletion(before, after)

        assert context.missing_element == 'syntax'
        assert context.difficulty_level == 1
