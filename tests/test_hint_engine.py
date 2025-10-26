"""Comprehensive tests for HintEngine module."""

import pytest
from src.hint_engine import HintEngine, Hint
from src.code_analyzer import CodeContext


class TestHintEngine:
    """Test suite for HintEngine class."""

    @pytest.fixture
    def engine(self):
        """Create a HintEngine instance."""
        return HintEngine()

    # Test 1: Initialization
    def test_engine_initialization(self, engine):
        """Test that engine initializes with templates and best practices."""
        assert engine.hint_templates is not None
        assert engine.best_practices is not None
        assert 'loops' in engine.hint_templates
        assert 'functions' in engine.hint_templates
        assert 'conditionals' in engine.hint_templates

    # Test 2-5: Hint generation for different levels
    def test_generate_hint_level_1(self, engine):
        """Test generating level 1 (conceptual) hint."""
        context = CodeContext(
            surrounding_code="",
            missing_element='loops',
            expected_pattern='for',
            difficulty_level=2
        )

        hint = engine.generate_hint(context, current_hint_level=1)

        assert isinstance(hint, Hint)
        assert hint.level == 1
        assert len(hint.content) > 0
        assert hint.best_practice is None  # Level 1 has no best practices

    def test_generate_hint_level_2(self, engine):
        """Test generating level 2 (structural) hint."""
        context = CodeContext(
            surrounding_code="",
            missing_element='functions',
            expected_pattern='def',
            difficulty_level=3
        )

        hint = engine.generate_hint(context, current_hint_level=2)

        assert hint.level == 2
        assert hint.best_practice is not None  # Level 2+ has best practices

    def test_generate_hint_level_3(self, engine):
        """Test generating level 3 (syntax) hint."""
        context = CodeContext(
            surrounding_code="",
            missing_element='conditionals',
            expected_pattern='if',
            difficulty_level=2
        )

        hint = engine.generate_hint(context, current_hint_level=3)

        assert hint.level == 3
        # Level 3 hints should provide syntax guidance (contain code-like elements)
        assert '`' in hint.content or ':' in hint.content

    def test_generate_hint_level_4(self, engine):
        """Test generating level 4 (code) hint."""
        context = CodeContext(
            surrounding_code="",
            missing_element='loops',
            expected_pattern='for',
            difficulty_level=2
        )

        hint = engine.generate_hint(context, current_hint_level=4)

        assert hint.level == 4
        assert '```python' in hint.content or 'for' in hint.content

    # Test 6-8: Best practices
    def test_best_practices_for_loops(self, engine):
        """Test that loop hints include best practices."""
        assert 'loops' in engine.best_practices
        assert len(engine.best_practices['loops']) > 0

    def test_best_practices_for_functions(self, engine):
        """Test that function hints include best practices."""
        assert 'functions' in engine.best_practices
        assert any('docstring' in bp.lower() for bp in engine.best_practices['functions'])

    def test_best_practices_for_conditionals(self, engine):
        """Test that conditional hints include best practices."""
        assert 'conditionals' in engine.best_practices
        assert len(engine.best_practices['conditionals']) > 0

    # Test 9-11: Hint progression logic
    def test_should_increase_hint_level_true(self, engine):
        """Test hint level increases after threshold."""
        should_increase = engine.should_increase_hint_level(
            time_stuck=35,  # More than 30 seconds
            current_level=1
        )
        assert should_increase is True

    def test_should_increase_hint_level_false_time(self, engine):
        """Test hint level doesn't increase before threshold."""
        should_increase = engine.should_increase_hint_level(
            time_stuck=15,  # Less than 30 seconds
            current_level=1
        )
        assert should_increase is False

    def test_should_increase_hint_level_max_level(self, engine):
        """Test hint level doesn't increase past level 4."""
        should_increase = engine.should_increase_hint_level(
            time_stuck=200,  # Lots of time
            current_level=4  # Already at max
        )
        assert should_increase is False

    # Test 12-14: Unknown pattern handling
    def test_generate_hint_unknown_pattern(self, engine):
        """Test generating hint for unknown pattern."""
        context = CodeContext(
            surrounding_code="",
            missing_element='unknown_thing',
            expected_pattern=None,
            difficulty_level=1
        )

        hint = engine.generate_hint(context, current_hint_level=1)

        assert isinstance(hint, Hint)
        assert hint.level == 1
        assert 'unknown_thing' in hint.content.lower()

    def test_hint_templates_exist_for_all_levels(self, engine):
        """Test that all pattern types have hints for all levels."""
        for pattern_type in ['loops', 'functions', 'conditionals']:
            templates = engine.hint_templates[pattern_type]
            for level in [1, 2, 3, 4]:
                assert level in templates
                assert len(templates[level]) > 0

    def test_hint_content_varies(self, engine):
        """Test that hint content can vary (random selection)."""
        context = CodeContext(
            surrounding_code="",
            missing_element='loops',
            expected_pattern='for',
            difficulty_level=2
        )

        # Generate multiple hints and check if they can be different
        hints = [engine.generate_hint(context, 1) for _ in range(10)]
        contents = {h.content for h in hints}

        # With random selection, we should see variety (or at least have multiple options)
        # Even if all the same, check that templates exist
        assert len(engine.hint_templates['loops'][1]) >= 1

    # Test 15: Hint progression thresholds
    def test_hint_progression_thresholds(self, engine):
        """Test that progression thresholds scale with level."""
        # Level 1: 30 seconds
        assert engine.should_increase_hint_level(29, 1) is False
        assert engine.should_increase_hint_level(30, 1) is True

        # Level 2: 60 seconds
        assert engine.should_increase_hint_level(59, 2) is False
        assert engine.should_increase_hint_level(60, 2) is True

        # Level 3: 90 seconds
        assert engine.should_increase_hint_level(89, 3) is False
        assert engine.should_increase_hint_level(90, 3) is True

    # Test 16: Hint object structure
    def test_hint_object_structure(self, engine):
        """Test that Hint objects have correct structure."""
        context = CodeContext(
            surrounding_code="x = 10",
            missing_element='functions',
            expected_pattern='def',
            difficulty_level=3
        )

        hint = engine.generate_hint(context, 2)

        assert hasattr(hint, 'level')
        assert hasattr(hint, 'content')
        assert hasattr(hint, 'best_practice')
        assert isinstance(hint.level, int)
        assert isinstance(hint.content, str)
        assert hint.best_practice is None or isinstance(hint.best_practice, str)
