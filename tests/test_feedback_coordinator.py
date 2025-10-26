import pytest
from unittest.mock import Mock
from src.feedback_coordinator import FeedbackCoordinator, EnhancedContext
from src.code_analyzer import CodeContext
from src.knowledge_graph_domain import CodeGraph, GraphNode, NodeType
from src.test_domain import RunResult, FailureInfo
from src.proficiency_domain import StudentProfile, PatternStats
from src.effects import Success, Failure, ErrorType


@pytest.fixture
def mock_graph_builder():
    builder = Mock()
    builder.build_from_code = Mock()
    return builder


@pytest.fixture
def mock_test_runner():
    runner = Mock()
    runner.run_tests = Mock()
    return runner


@pytest.fixture
def mock_profile_calculator():
    calculator = Mock()
    calculator.get_pattern_mastery = Mock(return_value=2)
    return calculator


@pytest.fixture
def coordinator(mock_graph_builder, mock_test_runner, mock_profile_calculator):
    return FeedbackCoordinator(
        mock_graph_builder,
        mock_test_runner,
        mock_profile_calculator
    )


@pytest.fixture
def sample_code_context():
    return CodeContext(
        surrounding_code="def test(): pass",
        missing_element="functions",
        expected_pattern="def",
        difficulty_level=2
    )


@pytest.fixture
def sample_profile():
    return StudentProfile(
        student_id="student_1",
        pattern_stats={
            "functions": PatternStats(
                pattern_type="functions",
                attempts=10,
                successes=7,
                total_time=500.0,
                hint_level_reached=2
            )
        },
        overall_score=0.7,
        mastery_level=2
    )


def test_build_enhanced_context_success(
    coordinator,
    mock_graph_builder,
    sample_code_context,
    sample_profile
):
    graph = CodeGraph()
    mock_graph_builder.build_from_code.return_value = Success(graph)

    result = coordinator.build_enhanced_context(
        "def test(): pass",
        sample_code_context,
        sample_profile
    )

    assert result.value.code_context == sample_code_context
    assert result.value.knowledge_graph == graph
    assert result.value.student_profile == sample_profile


def test_build_enhanced_context_graph_failure(
    coordinator,
    mock_graph_builder,
    sample_code_context,
    sample_profile
):
    mock_graph_builder.build_from_code.return_value = Failure(
        ErrorType.PARSE_ERROR,
        "syntax error"
    )

    result = coordinator.build_enhanced_context(
        "invalid code",
        sample_code_context,
        sample_profile
    )

    assert result.value.knowledge_graph is None


def test_enrich_with_tests_success(
    coordinator,
    mock_test_runner,
    sample_code_context
):
    test_result = RunResult(
        total_tests=5,
        passed=3,
        failed=2,
        errors=0,
        duration=1.5,
        failures=[]
    )
    mock_test_runner.run_tests.return_value = Success(test_result)

    context = EnhancedContext(
        code_context=sample_code_context,
        knowledge_graph=None,
        test_result=None,
        student_profile=None
    )

    result = coordinator.enrich_with_tests(context, "test_file.py")

    assert result.value.test_result == test_result


def test_enrich_with_tests_failure(
    coordinator,
    mock_test_runner,
    sample_code_context
):
    mock_test_runner.run_tests.return_value = Failure(
        ErrorType.TEST_ERROR,
        "test failed"
    )

    context = EnhancedContext(
        code_context=sample_code_context,
        knowledge_graph=None,
        test_result=None,
        student_profile=None
    )

    result = coordinator.enrich_with_tests(context, "test_file.py")

    assert result.value.test_result is None


def test_calculate_adaptive_hint_level_no_profile(
    coordinator,
    sample_code_context
):
    context = EnhancedContext(
        code_context=sample_code_context,
        knowledge_graph=None,
        test_result=None,
        student_profile=None
    )

    level = coordinator.calculate_adaptive_hint_level(context, 2)
    assert level == 2


def test_calculate_adaptive_hint_level_expert(
    coordinator,
    mock_profile_calculator,
    sample_code_context,
    sample_profile
):
    mock_profile_calculator.get_pattern_mastery.return_value = 3

    context = EnhancedContext(
        code_context=sample_code_context,
        knowledge_graph=None,
        test_result=None,
        student_profile=sample_profile
    )

    level = coordinator.calculate_adaptive_hint_level(context, 2)
    assert level == 1


def test_calculate_adaptive_hint_level_beginner(
    coordinator,
    mock_profile_calculator,
    sample_code_context,
    sample_profile
):
    mock_profile_calculator.get_pattern_mastery.return_value = 1

    context = EnhancedContext(
        code_context=sample_code_context,
        knowledge_graph=None,
        test_result=None,
        student_profile=sample_profile
    )

    level = coordinator.calculate_adaptive_hint_level(context, 2)
    assert level == 3


def test_calculate_adaptive_hint_level_intermediate(
    coordinator,
    mock_profile_calculator,
    sample_code_context,
    sample_profile
):
    mock_profile_calculator.get_pattern_mastery.return_value = 2

    context = EnhancedContext(
        code_context=sample_code_context,
        knowledge_graph=None,
        test_result=None,
        student_profile=sample_profile
    )

    level = coordinator.calculate_adaptive_hint_level(context, 2)
    assert level == 2


def test_should_show_test_feedback_no_tests(
    coordinator,
    sample_code_context
):
    context = EnhancedContext(
        code_context=sample_code_context,
        knowledge_graph=None,
        test_result=None,
        student_profile=None
    )

    assert not coordinator.should_show_test_feedback(context)


def test_should_show_test_feedback_all_passed(
    coordinator,
    sample_code_context
):
    test_result = RunResult(
        total_tests=5,
        passed=5,
        failed=0,
        errors=0,
        duration=1.5,
        failures=[]
    )

    context = EnhancedContext(
        code_context=sample_code_context,
        knowledge_graph=None,
        test_result=test_result,
        student_profile=None
    )

    assert not coordinator.should_show_test_feedback(context)


def test_should_show_test_feedback_has_failures(
    coordinator,
    sample_code_context
):
    test_result = RunResult(
        total_tests=5,
        passed=3,
        failed=2,
        errors=0,
        duration=1.5,
        failures=[]
    )

    context = EnhancedContext(
        code_context=sample_code_context,
        knowledge_graph=None,
        test_result=test_result,
        student_profile=None
    )

    assert coordinator.should_show_test_feedback(context)
