from typing import Dict
from dataclasses import replace
from src.proficiency_domain import (
    PatternStats,
    ProfileUpdate,
    ProfileCalculator
)

SUCCESS_WEIGHT = 0.4
TIME_WEIGHT = 0.3
HINT_WEIGHT = 0.3
BEGINNER_THRESHOLD = 0.4
INTERMEDIATE_THRESHOLD = 0.7
MAX_HINT_LEVEL = 4
OPTIMAL_TIME_PER_PATTERN = 60.0


class SimpleProfileCalculator:
    def calculate_score(
        self,
        stats: PatternStats
    ) -> float:
        if stats.attempts == 0:
            return 0.0

        success_rate = stats.successes / stats.attempts
        avg_time = stats.total_time / stats.attempts
        time_score = self._calculate_time_score(avg_time)
        hint_score = self._calculate_hint_score(stats.hint_level_reached)

        return (
            SUCCESS_WEIGHT * success_rate +
            TIME_WEIGHT * time_score +
            HINT_WEIGHT * hint_score
        )

    def get_pattern_mastery(
        self,
        stats: PatternStats
    ) -> int:
        score = self.calculate_score(stats)

        if score >= INTERMEDIATE_THRESHOLD:
            return 3
        if score >= BEGINNER_THRESHOLD:
            return 2
        return 1

    def update_stats(
        self,
        stats: PatternStats,
        update: ProfileUpdate
    ) -> PatternStats:
        new_attempts = stats.attempts + 1
        new_successes = stats.successes + (1 if update.success else 0)
        new_time = stats.total_time + update.time_taken
        max_hint = max(stats.hint_level_reached, update.hint_level)

        return replace(
            stats,
            attempts=new_attempts,
            successes=new_successes,
            total_time=new_time,
            hint_level_reached=max_hint
        )

    def calculate_overall_score(
        self,
        pattern_stats: Dict[str, PatternStats]
    ) -> float:
        if not pattern_stats:
            return 0.0

        scores = [
            self.calculate_score(stats)
            for stats in pattern_stats.values()
        ]
        return sum(scores) / len(scores)

    def _calculate_time_score(self, avg_time: float) -> float:
        if avg_time <= 0:
            return 0.0

        ratio = OPTIMAL_TIME_PER_PATTERN / avg_time
        return min(1.0, ratio)

    def _calculate_hint_score(self, max_hint_level: int) -> float:
        normalized = (MAX_HINT_LEVEL - max_hint_level) / (MAX_HINT_LEVEL - 1)
        return max(0.0, normalized)
