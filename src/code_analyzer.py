import ast
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CodeContext:
    surrounding_code: str
    missing_element: str  # 'function', 'loop', 'conditional', 'variable', etc.
    expected_pattern: Optional[str]
    difficulty_level: int  # 1-5


class CodeAnalyzer:
    def __init__(self):
        self.patterns = self._load_patterns()
        logger.debug("CodeAnalyzer initialized with %d pattern types", len(self.patterns))

    def _load_patterns(self) -> Dict[str, List[str]]:
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
        if not isinstance(before, str) or not isinstance(after, str):
            logger.error(
                "Invalid input types: before=%s, after=%s",
                type(before).__name__,
                type(after).__name__
            )
            return self._create_fallback_context(after)

        try:
            before_tree = ast.parse(before)
            after_tree = ast.parse(after)

            missing = self._detect_missing_patterns(before, after)
            difficulty = self._estimate_difficulty(missing)

            logger.debug(
                "Analyzed deletion: missing=%s, difficulty=%d",
                missing.get('type'),
                difficulty
            )

            return CodeContext(
                surrounding_code=after,
                missing_element=missing.get('type', 'unknown'),
                expected_pattern=missing.get('pattern'),
                difficulty_level=difficulty
            )
        except SyntaxError as e:
            logger.debug("Syntax error in code analysis: %s", str(e))
            return self._create_fallback_context(after, missing_element='syntax')
        except (ValueError, TypeError) as e:
            logger.warning("Unexpected error during AST parsing: %s", str(e))
            return self._create_fallback_context(after)
        except Exception as e:
            logger.error("Critical error in analyze_deletion: %s", str(e), exc_info=True)
            return self._create_fallback_context(after)

    def _create_fallback_context(
        self,
        code: str,
        missing_element: str = 'unknown'
    ) -> CodeContext:
        return CodeContext(
            surrounding_code=code if code else "",
            missing_element=missing_element,
            expected_pattern=None,
            difficulty_level=1
        )

    def _detect_missing_patterns(self, before: str, after: str) -> Dict[str, Optional[str]]:
        try:
            before_lines = before.split('\n')
            after_lines = after.split('\n')

            for pattern_type, keywords in self.patterns.items():
                for keyword in keywords:
                    before_has = any(keyword in line for line in before_lines)
                    after_has = any(keyword in line for line in after_lines)

                    if before_has and not after_has:
                        logger.debug(
                            "Detected missing pattern: type=%s, keyword=%s",
                            pattern_type,
                            keyword
                        )
                        return {
                            'type': pattern_type,
                            'pattern': keyword
                        }

            return {'type': 'unknown', 'pattern': None}
        except Exception as e:
            logger.warning("Error detecting missing patterns: %s", str(e))
            return {'type': 'unknown', 'pattern': None}

    def _estimate_difficulty(self, missing: Dict[str, Optional[str]]) -> int:
        difficulty_map = {
            'loops': 2,
            'conditionals': 2,
            'functions': 3,
            'comprehensions': 4,
            'classes': 4,
            'error_handling': 3,
            'unknown': 1
        }
        pattern_type = missing.get('type', 'unknown')
        difficulty = difficulty_map.get(pattern_type, 1)

        logger.debug("Estimated difficulty: %d for pattern type: %s", difficulty, pattern_type)
        return difficulty

    def get_function_signature(self, code: str, function_name: str) -> Optional[str]:
        if not code or not isinstance(code, str):
            logger.warning("Invalid code input for get_function_signature")
            return None

        if not function_name or not isinstance(function_name, str):
            logger.warning("Invalid function_name input for get_function_signature")
            return None

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    args = [arg.arg for arg in node.args.args]
                    signature = f"def {function_name}({', '.join(args)}):"
                    logger.debug("Found function signature: %s", signature)
                    return signature

            logger.debug("Function '%s' not found in code", function_name)
            return None
        except SyntaxError as e:
            logger.debug("Syntax error while parsing code for function signature: %s", str(e))
            return None
        except AttributeError as e:
            logger.warning("Attribute error in get_function_signature: %s", str(e))
            return None
        except Exception as e:
            logger.error(
                "Unexpected error in get_function_signature: %s",
                str(e),
                exc_info=True
            )
            return None
