"""Comprehensive tests for StateManager module."""

import pytest
import time
from datetime import datetime
from src.state_manager import StateManager, LearningSession
from src.hint_engine import Hint


class TestLearningSession:
    """Test suite for LearningSession dataclass."""

    # Test 1: Initialization with defaults
    def test_learning_session_defaults(self):
        """Test LearningSession initialization with defaults."""
        session = LearningSession(file_path="test.py")

        assert session.file_path == "test.py"
        assert isinstance(session.started_at, datetime)
        assert session.current_hint_level == 1
        assert session.hints_shown == []
        assert session.time_on_current_task == 0
        assert session.task_completed is False

    # Test 2: Custom values
    def test_learning_session_custom_values(self):
        """Test LearningSession with custom values."""
        now = datetime.now()
        session = LearningSession(
            file_path="custom.py",
            started_at=now,
            current_hint_level=3,
            hints_shown=["hint1", "hint2"],
            time_on_current_task=45.5,
            task_completed=True
        )

        assert session.file_path == "custom.py"
        assert session.started_at == now
        assert session.current_hint_level == 3
        assert len(session.hints_shown) == 2
        assert session.time_on_current_task == 45.5
        assert session.task_completed is True


class TestStateManager:
    """Test suite for StateManager class."""

    @pytest.fixture
    def manager(self):
        """Create a StateManager instance."""
        return StateManager()

    @pytest.fixture
    def sample_hint(self):
        """Create a sample hint for testing."""
        return Hint(level=1, content="Test hint content")

    # Test 3: Initialization
    def test_manager_initialization(self, manager):
        """Test StateManager initialization."""
        assert manager.current_session is None
        assert manager.sessions_history == []
        assert manager._task_start_time is None

    # Test 4: Start session
    def test_start_session(self, manager, capsys):
        """Test starting a new session."""
        manager.start_session("test.py")

        assert manager.current_session is not None
        assert manager.current_session.file_path == "test.py"
        assert manager._task_start_time is not None

        # Check console output
        captured = capsys.readouterr()
        assert "Learning session started" in captured.out

    # Test 5-6: Record hint
    def test_record_hint(self, manager, sample_hint):
        """Test recording a hint."""
        manager.start_session("test.py")
        manager.record_hint(sample_hint)

        assert len(manager.current_session.hints_shown) == 1
        assert manager.current_session.hints_shown[0] == sample_hint.content
        assert manager.current_session.current_hint_level == sample_hint.level

    def test_record_hint_no_session(self, manager, sample_hint):
        """Test recording hint when no session exists."""
        # Should not crash
        manager.record_hint(sample_hint)
        assert manager.current_session is None

    # Test 7: Get time stuck
    def test_get_time_stuck(self, manager):
        """Test getting time stuck on current task."""
        manager.start_session("test.py")
        time.sleep(0.1)  # Wait a bit

        time_stuck = manager.get_time_stuck()
        assert time_stuck >= 0.1
        assert time_stuck < 1.0  # Should be less than a second

    # Test 8: Reset timer
    def test_reset_timer(self, manager):
        """Test resetting the task timer."""
        manager.start_session("test.py")
        old_time = manager._task_start_time
        time.sleep(0.05)

        manager.reset_timer()
        new_time = manager._task_start_time

        assert new_time > old_time

    # Test 9: Mark completed
    def test_mark_completed(self, manager, capsys):
        """Test marking task as completed."""
        manager.start_session("test.py")
        manager.mark_completed()

        assert manager.current_session.task_completed is True
        assert len(manager.sessions_history) == 1

        # Check console output
        captured = capsys.readouterr()
        assert "completed" in captured.out.lower()

    # Test 10: Get current hint level
    def test_get_current_hint_level_with_session(self, manager):
        """Test getting current hint level with active session."""
        manager.start_session("test.py")
        manager.current_session.current_hint_level = 3

        level = manager.get_current_hint_level()
        assert level == 3

    # Test 11: Get current hint level without session
    def test_get_current_hint_level_no_session(self, manager):
        """Test getting hint level when no session exists."""
        level = manager.get_current_hint_level()
        assert level == 1  # Default

    # Test 12: End session
    def test_end_session(self, manager, capsys):
        """Test ending a session."""
        manager.start_session("test.py")
        manager.end_session()

        assert manager.current_session is None
        assert len(manager.sessions_history) == 1

        # Check console output
        captured = capsys.readouterr()
        assert "Session ended" in captured.out

    # Test 13: Multiple sessions
    def test_multiple_sessions(self, manager):
        """Test handling multiple sessions."""
        # First session
        manager.start_session("file1.py")
        manager.mark_completed()

        # Second session
        manager.start_session("file2.py")
        manager.end_session()

        assert len(manager.sessions_history) == 2
        assert manager.sessions_history[0].file_path == "file1.py"
        assert manager.sessions_history[1].file_path == "file2.py"

    # Test 14: Session history persistence
    def test_session_history_persistence(self, manager, sample_hint):
        """Test that session history persists across sessions."""
        # Session 1
        manager.start_session("test1.py")
        manager.record_hint(sample_hint)
        manager.end_session()

        # Session 2
        manager.start_session("test2.py")

        # History should still have session 1
        assert len(manager.sessions_history) == 1
        assert manager.sessions_history[0].file_path == "test1.py"
