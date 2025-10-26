import pytest
from src.proficiency_calculator import SimpleProfileCalculator
from src.proficiency_domain import PatternStats, ProfileUpdate


@pytest.fixture
def calculator():
    return SimpleProfileCalculator()


def test_calculate_score_no_attempts(calculator):
    stats = PatternStats(pattern_type="loops", attempts=0)
    score = calculator.calculate_score(stats)
    assert score == 0.0


def test_calculate_score_perfect(calculator):
    stats = PatternStats(
        pattern_type="loops",
        attempts=10,
        successes=10,
        total_time=300.0,
        hint_level_reached=1
    )
    score = calculator.calculate_score(stats)
    assert score > 0.8


def test_calculate_score_poor(calculator):
    stats = PatternStats(
        pattern_type="loops",
        attempts=10,
        successes=2,
        total_time=1200.0,
        hint_level_reached=4
    )
    score = calculator.calculate_score(stats)
    assert score < 0.3


def test_get_pattern_mastery_expert(calculator):
    stats = PatternStats(
        pattern_type="functions",
        attempts=10,
        successes=9,
        total_time=400.0,
        hint_level_reached=1
    )
    mastery = calculator.get_pattern_mastery(stats)
    assert mastery == 3


def test_get_pattern_mastery_intermediate(calculator):
    stats = PatternStats(
        pattern_type="functions",
        attempts=10,
        successes=5,
        total_time=700.0,
        hint_level_reached=3
    )
    mastery = calculator.get_pattern_mastery(stats)
    assert mastery == 2


def test_get_pattern_mastery_beginner(calculator):
    stats = PatternStats(
        pattern_type="functions",
        attempts=10,
        successes=3,
        total_time=900.0,
        hint_level_reached=4
    )
    mastery = calculator.get_pattern_mastery(stats)
    assert mastery == 1


def test_update_stats_success(calculator):
    stats = PatternStats(
        pattern_type="loops",
        attempts=5,
        successes=3,
        total_time=250.0,
        hint_level_reached=2
    )
    update = ProfileUpdate(
        pattern_type="loops",
        success=True,
        time_taken=50.0,
        hint_level=3
    )

    new_stats = calculator.update_stats(stats, update)

    assert new_stats.attempts == 6
    assert new_stats.successes == 4
    assert new_stats.total_time == 300.0
    assert new_stats.hint_level_reached == 3


def test_update_stats_failure(calculator):
    stats = PatternStats(
        pattern_type="loops",
        attempts=5,
        successes=3,
        total_time=250.0,
        hint_level_reached=2
    )
    update = ProfileUpdate(
        pattern_type="loops",
        success=False,
        time_taken=50.0,
        hint_level=1
    )

    new_stats = calculator.update_stats(stats, update)

    assert new_stats.attempts == 6
    assert new_stats.successes == 3


def test_calculate_overall_score_empty(calculator):
    score = calculator.calculate_overall_score({})
    assert score == 0.0


def test_calculate_overall_score_multiple_patterns(calculator):
    pattern_stats = {
        "loops": PatternStats(
            pattern_type="loops",
            attempts=10,
            successes=8,
            total_time=500.0,
            hint_level_reached=2
        ),
        "functions": PatternStats(
            pattern_type="functions",
            attempts=10,
            successes=9,
            total_time=400.0,
            hint_level_reached=1
        )
    }

    score = calculator.calculate_overall_score(pattern_stats)
    assert 0.0 < score < 1.0


def test_calculate_time_score_optimal(calculator):
    score = calculator._calculate_time_score(60.0)
    assert score == 1.0


def test_calculate_time_score_slow(calculator):
    score = calculator._calculate_time_score(120.0)
    assert score == 0.5


def test_calculate_time_score_fast(calculator):
    score = calculator._calculate_time_score(30.0)
    assert score == 1.0


def test_calculate_hint_score_no_hints(calculator):
    score = calculator._calculate_hint_score(1)
    assert score == 1.0


def test_calculate_hint_score_max_hints(calculator):
    score = calculator._calculate_hint_score(4)
    assert score == 0.0


def test_calculate_hint_score_mid_hints(calculator):
    score = calculator._calculate_hint_score(2)
    assert 0.0 < score < 1.0
