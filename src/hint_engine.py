import logging
import random
from typing import List, Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

MAX_HINT_LEVEL = 4
HINT_PROGRESSION_TIME_SECONDS = 30


@dataclass
class Hint:
    level: int  # 1=conceptual, 2=structural, 3=syntax, 4=code
    content: str
    best_practice: Optional[str] = None


class HintEngine:
    def __init__(self):
        try:
            self.hint_templates = self._load_hint_templates()
            self.best_practices = self._load_best_practices()
            logger.info(
                "HintEngine initialized with %d pattern types",
                len(self.hint_templates)
            )
        except Exception as e:
            logger.error("Failed to initialize HintEngine: %s", str(e), exc_info=True)
            self.hint_templates = {}
            self.best_practices = {}

    def _load_hint_templates(self) -> Dict[str, Dict[int, List[str]]]:
        return {
            'loops': {
                1: [
                    "You need to iterate through something here...",
                    "Think about repeating an action for each item...",
                ],
                2: [
                    "A loop structure would work well here. Which type of loop fits?",
                    "Consider: do you know the number of iterations, or are you checking a condition?",
                ],
                3: [
                    "Syntax: `for item in collection:` or `while condition:`",
                    "Try starting with `for` followed by a variable name...",
                ],
                4: [
                    "```python\nfor item in items:\n    # your code here\n```",
                    "```python\nwhile condition:\n    # your code here\n```",
                ]
            },
            'functions': {
                1: [
                    "This looks like it should be its own reusable piece of logic...",
                    "Think about wrapping this in a function for clarity...",
                ],
                2: [
                    "You'll need: function definition, parameters, return value",
                    "What inputs does this need? What should it output?",
                ],
                3: [
                    "Syntax: `def function_name(parameters):`",
                    "Start with `def`, choose a descriptive name...",
                ],
                4: [
                    "```python\ndef function_name(param1, param2):\n    # implementation\n    return result\n```",
                ]
            },
            'conditionals': {
                1: [
                    "You need to make a decision based on a condition...",
                    "Think about when you'd want different code to run...",
                ],
                2: [
                    "An if-statement controls the flow. What's the condition?",
                    "Consider: what condition determines which path to take?",
                ],
                3: [
                    "Syntax: `if condition:` or add `elif`/`else`",
                    "Try `if some_condition:` followed by indented code...",
                ],
                4: [
                    "```python\nif condition:\n    # do something\nelse:\n    # do something else\n```",
                ]
            }
        }

    def _load_best_practices(self) -> Dict[str, List[str]]:
        return {
            'loops': [
                "Use `enumerate()` when you need both index and value",
                "List comprehensions are Pythonic for simple transformations",
                "Avoid modifying a list while iterating over it",
            ],
            'functions': [
                "Use descriptive names that explain what the function does",
                "Keep functions small and focused on one task",
                "Add docstrings to explain purpose, params, and return value",
                "Consider using type hints for clarity",
            ],
            'conditionals': [
                "Use 'elif' instead of multiple 'if' statements when appropriate",
                "Consider the ternary operator for simple conditions: `x if condition else y`",
                "Early returns can make code more readable",
            ]
        }

    def generate_hint(
        self,
        context,
        current_hint_level: int = 1,
        time_elapsed: float = 0
    ) -> Hint:
        try:
            if not isinstance(current_hint_level, int):
                logger.warning(
                    "Invalid hint level type: %s, defaulting to 1",
                    type(current_hint_level).__name__
                )
                current_hint_level = 1

            current_hint_level = max(1, min(current_hint_level, MAX_HINT_LEVEL))

            pattern_type = getattr(context, 'missing_element', 'unknown')
            logger.debug(
                "Generating hint: pattern=%s, level=%d",
                pattern_type,
                current_hint_level
            )

            templates = self.hint_templates.get(pattern_type, {})
            level_hints = templates.get(
                current_hint_level,
                self._get_fallback_hints(pattern_type, current_hint_level)
            )

            if level_hints:
                hint_content = random.choice(level_hints)
            else:
                hint_content = self._get_generic_hint(pattern_type, current_hint_level)

            best_practice = None
            if current_hint_level >= 2:
                practices = self.best_practices.get(pattern_type, [])
                if practices:
                    best_practice = random.choice(practices)

            logger.debug("Generated hint: level=%d, has_practice=%s", current_hint_level, best_practice is not None)

            return Hint(
                level=current_hint_level,
                content=hint_content,
                best_practice=best_practice
            )
        except Exception as e:
            logger.error("Error generating hint: %s", str(e), exc_info=True)
            return Hint(
                level=current_hint_level,
                content="Consider what code element might be needed here.",
                best_practice=None
            )

    def _get_fallback_hints(self, pattern_type: str, level: int) -> List[str]:
        level_descriptors = {
            1: f"Think about adding {pattern_type} here...",
            2: f"You'll need a {pattern_type} structure. What components are required?",
            3: f"Consider the syntax for {pattern_type}...",
            4: f"Here's an example structure for {pattern_type}..."
        }

        hint = level_descriptors.get(level, f"Consider using {pattern_type}")
        return [hint]

    def _get_generic_hint(self, pattern_type: str, level: int) -> str:
        logger.warning(
            "Using generic hint for pattern=%s, level=%d",
            pattern_type,
            level
        )
        return f"Think about adding {pattern_type} to solve this problem."

    def should_increase_hint_level(
        self,
        time_stuck: float,
        current_level: int
    ) -> bool:
        try:
            if not isinstance(time_stuck, (int, float)) or time_stuck < 0:
                logger.warning("Invalid time_stuck: %s", time_stuck)
                return False

            if not isinstance(current_level, int) or current_level < 1:
                logger.warning("Invalid current_level: %s", current_level)
                return False

            threshold = HINT_PROGRESSION_TIME_SECONDS * current_level
            should_increase = time_stuck >= threshold and current_level < MAX_HINT_LEVEL

            logger.debug(
                "Hint progression check: time_stuck=%.1fs, level=%d, threshold=%.1fs, increase=%s",
                time_stuck,
                current_level,
                threshold,
                should_increase
            )

            return should_increase
        except Exception as e:
            logger.error("Error in should_increase_hint_level: %s", str(e))
            return False
