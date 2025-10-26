import time
import logging
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_HINT_LEVEL = 1
MAX_HINT_LEVEL = 4


@dataclass
class LearningSession:
    file_path: str
    started_at: datetime = field(default_factory=datetime.now)
    current_hint_level: int = 1
    hints_shown: List[str] = field(default_factory=list)
    time_on_current_task: float = 0
    task_completed: bool = False


class StateManager:
    def __init__(self):
        self.current_session: Optional[LearningSession] = None
        self.sessions_history: List[LearningSession] = []
        self._task_start_time: Optional[float] = None
        logger.info("StateManager initialized")

    def start_session(self, file_path: str) -> None:
        try:
            if not file_path or not isinstance(file_path, str):
                logger.error("Invalid file_path: %s", file_path)
                print(f"Error: Invalid file path")
                return

            if self.current_session:
                logger.info("Ending existing session before starting new one")
                self.end_session()

            self.current_session = LearningSession(file_path=file_path)
            self._task_start_time = time.time()

            logger.info("Learning session started for: %s", file_path)
            print(f"Learning session started for: {file_path}")
        except Exception as e:
            logger.error("Error starting session: %s", str(e), exc_info=True)
            print(f"Error starting learning session: {e}")

    def record_hint(self, hint) -> None:
        try:
            if not self.current_session:
                logger.warning("Cannot record hint: no active session")
                return

            if not hasattr(hint, 'content') or not hasattr(hint, 'level'):
                logger.error("Invalid hint object: %s", hint)
                return

            self.current_session.hints_shown.append(hint.content)
            self.current_session.current_hint_level = hint.level

            logger.debug(
                "Hint recorded: level=%d, total_hints=%d",
                hint.level,
                len(self.current_session.hints_shown)
            )
        except Exception as e:
            logger.error("Error recording hint: %s", str(e), exc_info=True)

    def get_time_stuck(self) -> float:
        try:
            if self._task_start_time:
                elapsed = time.time() - self._task_start_time
                return max(0, elapsed)
            return 0
        except Exception as e:
            logger.error("Error getting time stuck: %s", str(e))
            return 0

    def reset_timer(self) -> None:
        try:
            self._task_start_time = time.time()
            logger.debug("Task timer reset")
        except Exception as e:
            logger.error("Error resetting timer: %s", str(e))

    def mark_completed(self) -> None:
        try:
            if not self.current_session:
                logger.warning("Cannot mark completed: no active session")
                return

            self.current_session.task_completed = True
            self.sessions_history.append(self.current_session)

            logger.info("Task completed for: %s", self.current_session.file_path)
            print("Great job! Task completed!")
        except Exception as e:
            logger.error("Error marking task completed: %s", str(e), exc_info=True)
            print(f"Error marking task as completed: {e}")

    def get_current_hint_level(self) -> int:
        try:
            if self.current_session:
                level = self.current_session.current_hint_level
                return max(DEFAULT_HINT_LEVEL, min(level, MAX_HINT_LEVEL))
            return DEFAULT_HINT_LEVEL
        except Exception as e:
            logger.error("Error getting current hint level: %s", str(e))
            return DEFAULT_HINT_LEVEL

    def end_session(self) -> None:
        try:
            if not self.current_session:
                logger.debug("No active session to end")
                return

            if self.current_session not in self.sessions_history:
                self.sessions_history.append(self.current_session)

            file_path = self.current_session.file_path
            self.current_session = None
            self._task_start_time = None

            logger.info("Session ended for: %s", file_path)
            print("Session ended. Great work!")
        except Exception as e:
            logger.error("Error ending session: %s", str(e), exc_info=True)
            print(f"Error ending session: {e}")
