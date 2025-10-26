from typing import List, Optional, Dict
from dataclasses import dataclass
import random


@dataclass
class Hint:
    """A progressive hint with level and content."""
    level: int  # 1=conceptual, 2=structural, 3=syntax, 4=code
    content: str
    best_practice: Optional[str] = None


class HintEngine:
    """Generates progressive hints based on code context."""

    def __init__(self):
        self.hint_templates = self._load_hint_templates()
        self.best_practices = self._load_best_practices()

    def _load_hint_templates(self) -> Dict:
        """Load hint templates for different patterns."""
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

    def _load_best_practices(self) -> Dict:
        """Load Python best practices for different patterns."""
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
        context,  # CodeContext from code_analyzer
        current_hint_level: int = 1,
        time_elapsed: float = 0
    ) -> Hint:
        """Generate a progressive hint based on context and current level."""

        pattern_type = context.missing_element

        # Get appropriate hint template
        templates = self.hint_templates.get(pattern_type, {})
        level_hints = templates.get(current_hint_level, [
            f"Think about adding {pattern_type} here..."
        ])

        hint_content = random.choice(level_hints)

        # Add best practice if at higher levels
        best_practice = None
        if current_hint_level >= 2:
            practices = self.best_practices.get(pattern_type, [])
            if practices:
                best_practice = random.choice(practices)

        return Hint(
            level=current_hint_level,
            content=hint_content,
            best_practice=best_practice
        )

    def should_increase_hint_level(
        self,
        time_stuck: float,
        current_level: int
    ) -> bool:
        """Determine if hint level should increase."""
        # Increase hint level after 30 seconds per level
        threshold = 30 * current_level
        return time_stuck >= threshold and current_level < 4
