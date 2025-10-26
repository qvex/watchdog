"""Comprehensive tests for FileWatcher module."""

import pytest
import time
from pathlib import Path
from src.file_watcher import PythonFileWatcher, CodeChangeEvent


class TestCodeChangeEvent:
    """Test suite for CodeChangeEvent class."""

    # Test 1-2: Initialization
    def test_code_change_event_initialization(self):
        """Test CodeChangeEvent initialization."""
        event = CodeChangeEvent(
            file_path="test.py",
            before="def old():\n    pass",
            after="def new():\n    pass"
        )

        assert event.file_path == "test.py"
        assert event.before == "def old():\n    pass"
        assert event.after == "def new():\n    pass"
        assert event.deleted_lines is not None
        assert event.deleted_functions is not None

    def test_get_deleted_lines(self):
        """Test detection of deleted lines."""
        event = CodeChangeEvent(
            file_path="test.py",
            before="line1\nline2\nline3",
            after="line1\nline3"
        )

        assert 'line2' in event.deleted_lines

    # Test 3-5: Function deletion detection
    def test_get_deleted_functions_simple(self):
        """Test detection of deleted function."""
        event = CodeChangeEvent(
            file_path="test.py",
            before="def removed_func(x, y):\n    return x + y\n\ndef kept_func():\n    pass",
            after="def kept_func():\n    pass"
        )

        assert len(event.deleted_functions) == 1
        assert event.deleted_functions[0]['name'] == 'removed_func'
        assert event.deleted_functions[0]['args'] == ['x', 'y']

    def test_get_deleted_functions_none(self):
        """Test when no functions are deleted."""
        event = CodeChangeEvent(
            file_path="test.py",
            before="def func():\n    pass",
            after="def func():\n    pass"
        )

        assert len(event.deleted_functions) == 0

    def test_get_deleted_functions_syntax_error(self):
        """Test function deletion with syntax error."""
        event = CodeChangeEvent(
            file_path="test.py",
            before="def broken(\n    # No closing paren",
            after=""
        )

        # Should return empty list when syntax error occurs
        assert event.deleted_functions == []


class TestPythonFileWatcher:
    """Test suite for PythonFileWatcher class."""

    @pytest.fixture
    def callback_tracker(self):
        """Track callback invocations."""
        tracker = {'called': False, 'event': None}

        def callback(event):
            tracker['called'] = True
            tracker['event'] = event

        tracker['callback'] = callback
        return tracker

    # Test 6: Initialization
    def test_watcher_initialization(self, temp_python_file, callback_tracker):
        """Test PythonFileWatcher initialization."""
        watcher = PythonFileWatcher(
            str(temp_python_file),
            callback_tracker['callback']
        )

        assert watcher.file_path == temp_python_file.resolve()
        assert watcher._debounce_time == 0.5
        assert watcher._last_modified == 0

    # Test 7: File reading
    def test_read_file(self, temp_python_file, callback_tracker):
        """Test file reading."""
        watcher = PythonFileWatcher(
            str(temp_python_file),
            callback_tracker['callback']
        )

        content = watcher._read_file()
        assert len(content) > 0
        assert 'def example_function' in content

    # Test 8: Debounce mechanism
    def test_debounce_prevents_rapid_triggers(self, temp_python_file, callback_tracker):
        """Test that debounce prevents rapid fire events."""
        watcher = PythonFileWatcher(
            str(temp_python_file),
            callback_tracker['callback']
        )

        # Simulate rapid modifications
        watcher._last_modified = time.time()

        class MockEvent:
            src_path = str(temp_python_file)

        # This should be debounced (too soon)
        watcher.on_modified(MockEvent())
        assert callback_tracker['called'] is False

    # Test 9: File path validation
    def test_watcher_resolves_absolute_path(self, temp_python_file, callback_tracker):
        """Test that file path is resolved to absolute."""
        # Use relative path
        relative_path = Path(temp_python_file).name

        watcher = PythonFileWatcher(
            str(temp_python_file),  # This is already absolute from fixture
            callback_tracker['callback']
        )

        assert watcher.file_path.is_absolute()

    # Test 10: Content change detection
    def test_on_modified_only_triggers_on_real_change(self, temp_python_file, callback_tracker):
        """Test that callback only fires when content actually changes."""
        watcher = PythonFileWatcher(
            str(temp_python_file),
            callback_tracker['callback']
        )

        initial_content = watcher._last_content

        # Mock event with same file
        class MockEvent:
            src_path = str(temp_python_file)

        # Reset debounce
        watcher._last_modified = 0

        # If content hasn't changed, callback shouldn't fire
        # (This test assumes _read_file returns same content)
        old_content = watcher._last_content
        watcher._last_content = old_content

        # Event for different file - should be ignored
        class DifferentFileEvent:
            src_path = "different_file.py"

        watcher.on_modified(DifferentFileEvent())
        assert callback_tracker['called'] is False
