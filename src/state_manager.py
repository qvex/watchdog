import time
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LearningSession:
    """Tracks a single learning session."""
    file_path: str
    started_at: datetime = field(default_factory=datetime.now)
    current_hint_level: int = 1
    hints_shown: List[str] = field(default_factory=list)
    time_on_current_task: float = 0
    task_completed: bool = False


class StateManager:
    """Manages learning state and progress tracking."""

    def __init__(self):
        self.current_session: Optional[LearningSession] = None
        self.sessions_history: List[LearningSession] = []
        self._task_start_time: Optional[float] = None

    def start_session(self, file_path: str):
        """Start a new learning session."""
        self.current_session = LearningSession(file_path=file_path)
        self._task_start_time = time.time()
        print(f"Learning session started for: {file_path}")

    def record_hint(self, hint):  # hint: Hint from hint_engine
        """Record that a hint was shown."""
        if self.current_session:
            self.current_session.hints_shown.append(hint.content)
            self.current_session.current_hint_level = hint.level

    def get_time_stuck(self) -> float:
        """Get time spent on current task."""
        if self._task_start_time:
            return time.time() - self._task_start_time
        return 0

    def reset_timer(self):
        """Reset the task timer (when code is updated)."""
        self._task_start_time = time.time()

    def mark_completed(self):
        """Mark current task as completed."""
        if self.current_session:
            self.current_session.task_completed = True
            self.sessions_history.append(self.current_session)
            print("Great job! Task completed!")

    def get_current_hint_level(self) -> int:
        """Get current hint level for the session."""
        return self.current_session.current_hint_level if self.current_session else 1

    def end_session(self):
        """End the current session."""
        if self.current_session:
            self.sessions_history.append(self.current_session)
            self.current_session = None
            print("Session ended. Great work!")
