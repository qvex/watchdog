from typing import Protocol, Dict
from dataclasses import dataclass, field
from datetime import datetime
from src.effects import Result, ErrorType


@dataclass(frozen=True, slots=True)
class PatternStats:
    pattern_type: str
    attempts: int = 0
    successes: int = 0
    total_time: float = 0.0
    hint_level_reached: int = 1


@dataclass(frozen=True, slots=True)
class StudentProfile:
    student_id: str
    pattern_stats: Dict[str, PatternStats] = field(default_factory=dict)
    overall_score: float = 0.0
    mastery_level: int = 1
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True, slots=True)
class ProfileUpdate:
    pattern_type: str
    success: bool
    time_taken: float
    hint_level: int


class ProfileCalculator(Protocol):
    def calculate_score(
        self,
        stats: PatternStats
    ) -> float:
        ...

    def get_pattern_mastery(
        self,
        stats: PatternStats
    ) -> int:
        ...

    def update_stats(
        self,
        stats: PatternStats,
        update: ProfileUpdate
    ) -> PatternStats:
        ...

    def calculate_overall_score(
        self,
        pattern_stats: Dict[str, PatternStats]
    ) -> float:
        ...


class ProfileRepository(Protocol):
    def load(
        self,
        student_id: str
    ) -> Result[StudentProfile, ErrorType]:
        ...

    def save(
        self,
        profile: StudentProfile
    ) -> Result[None, ErrorType]:
        ...

    def exists(
        self,
        student_id: str
    ) -> bool:
        ...
