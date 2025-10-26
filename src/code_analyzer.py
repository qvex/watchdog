import ast
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class CodeContext:
    """Context about the code being written."""
    surrounding_code: str
    missing_element: str  # 'function', 'loop', 'conditional', 'variable', etc.
    expected_pattern: Optional[str]
    difficulty_level: int  # 1-5


class CodeAnalyzer:
    """Analyzes Python code to understand what's missing and provide context."""

    def __init__(self):
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        """Load common Python patterns for detection."""
        return {
            'loops': ['for', 'while'],
            'conditionals': ['if', 'elif', 'else'],
            'functions': ['def'],
            'classes': ['class'],
            'comprehensions': ['[', 'for', 'in'],
            'context_managers': ['with'],
            'error_handling': ['try', 'except', 'finally']
        }

    def analyze_deletion(self, before: str, after: str) -> CodeContext:
        """Analyze what was deleted and determine context."""
        try:
            before_tree = ast.parse(before)
            after_tree = ast.parse(after)

            # Detect deleted patterns
            missing = self._detect_missing_patterns(before, after)
            difficulty = self._estimate_difficulty(missing)

            return CodeContext(
                surrounding_code=after,
                missing_element=missing.get('type', 'unknown'),
                expected_pattern=missing.get('pattern'),
                difficulty_level=difficulty
            )
        except SyntaxError:
            # Handle incomplete code gracefully
            return CodeContext(
                surrounding_code=after,
                missing_element='syntax',
                expected_pattern=None,
                difficulty_level=1
            )

    def _detect_missing_patterns(self, before: str, after: str) -> Dict:
        """Detect what pattern was removed."""
        before_lines = before.split('\n')
        after_lines = after.split('\n')

        # Simple pattern detection
        for pattern_type, keywords in self.patterns.items():
            for keyword in keywords:
                before_has = any(keyword in line for line in before_lines)
                after_has = any(keyword in line for line in after_lines)

                if before_has and not after_has:
                    return {
                        'type': pattern_type,
                        'pattern': keyword
                    }

        return {'type': 'unknown', 'pattern': None}

    def _estimate_difficulty(self, missing: Dict) -> int:
        """Estimate difficulty level (1-5) based on what's missing."""
        difficulty_map = {
            'loops': 2,
            'conditionals': 2,
            'functions': 3,
            'comprehensions': 4,
            'classes': 4,
            'error_handling': 3,
            'unknown': 1
        }
        return difficulty_map.get(missing.get('type', 'unknown'), 1)

    def get_function_signature(self, code: str, function_name: str) -> Optional[str]:
        """Extract function signature if it exists."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    args = [arg.arg for arg in node.args.args]
                    return f"def {function_name}({', '.join(args)}):"
        except:
            pass
        return None
