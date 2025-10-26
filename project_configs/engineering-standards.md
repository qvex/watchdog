# Engineering Standards - Watchdog

**CRITICAL: This is the SINGLE source of truth for all engineering practices, protocols, and standards**

---

# PART 1: WORKING DIRECTIVE - Process & Protocol

## Foundational Principle

**ACCURACY OVER SPEED**: Slow, methodical, and correct responses are ALWAYS preferred over fast, incorrect ones. Taking time to plan and execute correctly is better than rushing and creating bugs.

## Zero Assumption Policy

### Absolute Prohibitions
1. **NEVER GUESS** - If uncertain about any detail, implementation, API, or behavior
2. **NEVER ASSUME** - If file content, configuration, or system state is unknown
3. **NEVER PROCEED** - If confidence level is below 10/10 for implementation decisions

### Required Actions When Uncertain
1. **Read the actual source** - Use Read, Grep, or Glob tools to examine code
2. **Check documentation** - Reference this document, dev_log.md, outline.md
3. **Verify with testing** - Run the code to confirm behavior
4. **Ask the user** - If information cannot be obtained through tools, explicitly ask

### Red Flags That Trigger Investigation
- "This probably works like..."
- "Based on typical patterns..."
- "I assume the function..."
- "It should be implemented as..."
- Any statement containing uncertainty markers without follow-up verification

## File Reading Protocol

**When user asks "read this file" or references a file:**

1. **Use Read tool** to get the complete file contents
2. **Use Grep** if searching for specific patterns or sections
3. **State explicitly** what you found and any gaps in understanding
4. **Admit limitations** if the file is too large or complex to fully comprehend

## Confidence Assessment Protocol

### Before EVERY Implementation
Rate confidence on scale 1-10:
- **10/10**: Verified through code inspection, documentation, or testing
- **7-9/10**: High confidence but minor unknowns - INVESTIGATE BEFORE PROCEEDING
- **4-6/10**: Medium confidence with unknowns - MUST ASK USER OR INVESTIGATE
- **1-3/10**: Low confidence - STOP IMMEDIATELY, DO NOT PROCEED

### Confidence Rating Checklist
- [ ] Have I read the relevant source files?
- [ ] Have I verified the implementation approach?
- [ ] Do I understand all edge cases?
- [ ] Can I explain WHY this approach is correct?
- [ ] Have I considered failure modes?

**IF ANY CHECKBOX IS UNCHECKED: Confidence is NOT 10/10**

## Pre-Response Checklist

Before EVERY response involving code or technical decisions, verify:
- [ ] Have I made any assumptions?
- [ ] Is my confidence 10/10?
- [ ] Have I referenced relevant files?
- [ ] Have I checked outline.md for implementation details?
- [ ] Is this response accurate or just fast?
- [ ] Should I investigate further before responding?

**IF ANY CHECKBOX FAILS: INVESTIGATE BEFORE RESPONDING**

---

# PART 2: PYTHON PROGRAMMING STANDARDS - Code Quality & Design

## Core Principles

**READABILITY FIRST**: Code is read more often than written. Prioritize clarity over cleverness.

**EXPLICIT OVER IMPLICIT**: Make intentions clear through descriptive names and straightforward logic.

**SIMPLE OVER COMPLEX**: Use the simplest solution that solves the problem correctly.

## Code Style Standards

### PEP 8 Compliance

**ABSOLUTE REQUIREMENTS**:
- 4 spaces for indentation (never tabs)
- Maximum line length: 88 characters (Black formatter standard)
- Two blank lines between top-level functions and classes
- One blank line between methods in a class
- Lowercase with underscores for function and variable names (snake_case)
- CapitalizedWords for class names (PascalCase)
- UPPERCASE with underscores for constants

### Naming Conventions

**Variables and Functions**:
```python
# Good
user_name = "Alice"
def calculate_average(numbers):
    ...

# Bad
userName = "Alice"  # camelCase
def calcAvg(nums):  # abbreviations
    ...
```

**Classes**:
```python
# Good
class CodeAnalyzer:
    ...

# Bad
class code_analyzer:  # lowercase
class Code_Analyzer:  # underscores
    ...
```

**Constants**:
```python
# Good
MAX_HINT_LEVEL = 4
DEFAULT_DEBOUNCE_TIME = 0.5

# Bad
max_hint_level = 4  # lowercase
MaxHintLevel = 4    # PascalCase
```

### Type Hints

**REQUIREMENT**: All public function signatures must have type hints.

```python
# Good
def generate_hint(context: CodeContext, level: int) -> Hint:
    ...

def process_deletion(before: str, after: str) -> List[str]:
    ...

# Bad
def generate_hint(context, level):  # No type hints
    ...
```

**For Complex Types**:
```python
from typing import List, Dict, Optional, Callable

def analyze_code(
    code: str,
    patterns: Dict[str, List[str]]
) -> Optional[CodeContext]:
    ...

def set_callback(
    callback: Callable[[CodeChangeEvent], None]
) -> None:
    ...
```

## Documentation Standards

### Docstrings

**REQUIREMENT**: All public classes, methods, and functions must have docstrings.

**Format**: Google-style docstrings

```python
def calculate_average(numbers: List[float]) -> float:
    """Calculate the average of a list of numbers.

    Args:
        numbers: A list of numeric values to average.

    Returns:
        The arithmetic mean of the input numbers.

    Raises:
        ValueError: If the numbers list is empty.

    Example:
        >>> calculate_average([1, 2, 3, 4, 5])
        3.0
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
```

**Class Docstrings**:
```python
class HintEngine:
    """Generates progressive hints based on code context.

    The HintEngine provides a 4-level progressive hint system:
    - Level 1: Conceptual hints
    - Level 2: Structural hints
    - Level 3: Syntax hints
    - Level 4: Complete code examples

    Attributes:
        hint_templates: Dictionary mapping pattern types to hint templates.
        best_practices: Dictionary of best practice suggestions.
    """
```

### Inline Comments

**Use inline comments for**:
- Complex algorithms that need explanation
- Non-obvious design decisions
- Workarounds for known issues

**DO NOT use inline comments for**:
- Obvious code ("increment i")
- Restating what the code does
- Commented-out code (use version control instead)

```python
# Good
# Using difflib instead of simple string comparison to handle
# whitespace differences and provide better diff granularity
deleted_lines = difflib.unified_diff(before, after)

# Bad
i += 1  # Increment i by 1
```

## Error Handling

### Exception Handling Best Practices

**Use specific exceptions**:
```python
# Good
try:
    tree = ast.parse(code)
except SyntaxError as e:
    logger.error(f"Syntax error in code: {e}")
    return None

# Bad
try:
    tree = ast.parse(code)
except:  # Bare except
    return None
```

**Provide context in error messages**:
```python
# Good
if not Path(file_path).exists():
    raise FileNotFoundError(
        f"Practice file not found: {file_path}. "
        f"Please ensure the file exists and path is correct."
    )

# Bad
if not Path(file_path).exists():
    raise FileNotFoundError("File not found")
```

### Graceful Degradation

**When non-critical operations fail, degrade gracefully**:
```python
def analyze_deletion(self, before: str, after: str) -> CodeContext:
    """Analyze what was deleted and determine context."""
    try:
        before_tree = ast.parse(before)
        after_tree = ast.parse(after)
        missing = self._detect_missing_patterns(before, after)
        difficulty = self._estimate_difficulty(missing)

        return CodeContext(
            surrounding_code=after,
            missing_element=missing.get('type', 'unknown'),
            expected_pattern=missing.get('pattern'),
            difficulty_level=difficulty
        )
    except SyntaxError:
        # Graceful degradation: Return basic context without AST analysis
        return CodeContext(
            surrounding_code=after,
            missing_element='syntax',
            expected_pattern=None,
            difficulty_level=1
        )
```

## Code Organization

### File Structure

**Module Organization**:
```python
"""Module docstring explaining purpose and main classes/functions."""

# Standard library imports
import sys
import time
from pathlib import Path
from typing import List, Optional

# Third-party imports
from watchdog.observers import Observer
from rich.console import Console

# Local imports
from src.code_analyzer import CodeAnalyzer
from src.hint_engine import HintEngine

# Constants
MAX_HINT_LEVEL = 4
DEFAULT_TIMEOUT = 30

# Classes and functions
class MyClass:
    ...

def my_function():
    ...
```

### Class Design

**Single Responsibility Principle**:
Each class should have one clear purpose.

```python
# Good
class CodeAnalyzer:
    """Analyzes Python code to detect patterns and estimate difficulty."""

class HintEngine:
    """Generates progressive hints based on code context."""

# Bad
class CodeAnalyzerAndHintGenerator:
    """Analyzes code AND generates hints."""  # Two responsibilities
```

**Small, Focused Methods**:
```python
# Good
def on_modified(self, event):
    """Handle file modification events."""
    if not self._should_process_event(event):
        return

    current_content = self._read_file()
    if self._content_changed(current_content):
        self._process_change(current_content)

# Bad
def on_modified(self, event):
    """Handle file modification events."""
    # 100 lines of logic all in one method
    ...
```

## Performance Considerations

### Avoid Premature Optimization

**Start with clarity, optimize if needed**:
```python
# Good for initial implementation
def get_deleted_functions(self) -> List[dict]:
    """Identify deleted functions using AST."""
    # Clear, readable implementation
    before_funcs = {node.name: node for node in ast.walk(before_tree)
                   if isinstance(node, ast.FunctionDef)}
    after_funcs = {node.name: node for node in ast.walk(after_tree)
                  if isinstance(node, ast.FunctionDef)}

    return [{'name': name, ...} for name in before_funcs
            if name not in after_funcs]
```

### Debouncing and Rate Limiting

**Use debouncing for event-driven code**:
```python
def on_modified(self, event):
    """Handle file modification with debounce."""
    current_time = time.time()
    if current_time - self._last_modified < self._debounce_time:
        return  # Skip this event
    self._last_modified = current_time

    # Process event
    ...
```

## Testing Standards

### Unit Testing

**Test public interfaces**:
```python
def test_hint_generation_level_1():
    """Test that level 1 hints are conceptual."""
    engine = HintEngine()
    context = CodeContext(
        surrounding_code="",
        missing_element='loops',
        expected_pattern='for',
        difficulty_level=2
    )

    hint = engine.generate_hint(context, current_hint_level=1)

    assert hint.level == 1
    assert "think about" in hint.content.lower()
    assert hint.best_practice is None  # Level 1 has no best practices
```

### Test Coverage Goals

- **Core components**: 80%+ coverage (analyzer, hint engine, state manager)
- **Integration points**: Test key workflows end-to-end
- **Edge cases**: Test error conditions and boundary cases

---

# PART 3: WATCHDOG-SPECIFIC STANDARDS - Implementation Guidelines

## File Watcher Standards

### Event Handler Design

**Debounce all file events**:
```python
class PythonFileWatcher(FileSystemEventHandler):
    def __init__(self, file_path: str, on_change: Callable):
        self._debounce_time = 0.5  # Required: prevent event spam
        self._last_modified = 0
```

**Check event relevance**:
```python
def on_modified(self, event):
    """Handle file modification events."""
    # REQUIRED: Verify this is the file we're watching
    if event.src_path != str(self.file_path):
        return

    # REQUIRED: Debounce rapid changes
    current_time = time.time()
    if current_time - self._last_modified < self._debounce_time:
        return
```

## AST Analysis Standards

### Error Handling for AST Operations

**ALWAYS wrap ast.parse in try-except**:
```python
# REQUIRED pattern
try:
    tree = ast.parse(code)
    # ... analyze tree
except SyntaxError:
    # Provide fallback behavior
    logger.debug(f"Syntax error in code, using fallback analysis")
    return fallback_result()
```

### Pattern Detection

**Use explicit pattern matching**:
```python
# Good
def _detect_missing_patterns(self, before: str, after: str) -> Dict:
    """Detect what pattern was removed."""
    for pattern_type, keywords in self.patterns.items():
        for keyword in keywords:
            before_has = any(keyword in line for line in before_lines)
            after_has = any(keyword in line for line in after_lines)

            if before_has and not after_has:
                return {'type': pattern_type, 'pattern': keyword}

    return {'type': 'unknown', 'pattern': None}
```

## Hint Generation Standards

### Progressive Hint Levels

**ENFORCE 4-level progression**:
- Level 1: Conceptual only (no code)
- Level 2: Structure and components (no syntax)
- Level 3: Syntax templates (no complete code)
- Level 4: Complete working code example

**Example hint template structure**:
```python
hint_templates = {
    'loops': {
        1: ["Think about repeating an action..."],
        2: ["You'll need: loop structure, iteration variable..."],
        3: ["Syntax: `for item in collection:`"],
        4: ["```python\nfor item in items:\n    # code here\n```"]
    }
}
```

### Time-Based Progression

**REQUIREMENT**: 30 seconds per hint level
```python
def should_increase_hint_level(
    self,
    time_stuck: float,
    current_level: int
) -> bool:
    """Determine if hint level should increase."""
    threshold = 30 * current_level  # 30s, 60s, 90s, 120s
    return time_stuck >= threshold and current_level < 4
```

## Session Management Standards

### State Tracking

**Use dataclasses for state objects**:
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class LearningSession:
    """Tracks a single learning session."""
    file_path: str
    started_at: datetime = field(default_factory=datetime.now)
    current_hint_level: int = 1
    hints_shown: List[str] = field(default_factory=list)
    time_on_current_task: float = 0
    task_completed: bool = False
```

### Timer Management

**Reset timer on code updates**:
```python
def on_code_change(self, event: CodeChangeEvent):
    """Handle code changes and provide hints."""
    # REQUIRED: Reset timer when user makes changes
    self.state.reset_timer()

    # Continue with hint generation
    ...
```

## VS Code Integration Standards

### Terminal Output

**Use Rich library for all formatted output**:
```python
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

def display_hint(self, hint: Hint):
    """Display a hint in the terminal."""
    emoji_map = {1: "🤔", 2: "💡", 3: "✏️", 4: "📝"}
    emoji = emoji_map.get(hint.level, "💭")

    hint_text = f"{emoji} **Hint (Level {hint.level}/4)**\n\n{hint.content}"

    if hint.best_practice:
        hint_text += f"\n\n✨ **Best Practice:** {hint.best_practice}"

    self.console.print(Panel(
        Markdown(hint_text),
        title="Watchdog Learning Assistant",
        border_style="blue",
        padding=(1, 2)
    ))
```

## Configuration Standards

### File Paths

**ALWAYS use pathlib.Path**:
```python
from pathlib import Path

# Good
file_path = Path(args.file).resolve()
if not file_path.exists():
    print(f"Error: File '{file_path}' not found")

# Bad
import os
file_path = os.path.abspath(args.file)  # Use pathlib instead
```

### Constants

**Define all magic numbers as constants**:
```python
# Good
DEBOUNCE_TIME_SECONDS = 0.5
HINT_PROGRESSION_TIME_SECONDS = 30
MAX_HINT_LEVEL = 4

# Bad
if current_time - self._last_modified < 0.5:  # Magic number
    return
```

---

# SESSION START INSTRUCTION

State: "Following Watchdog engineering standards. All implementations require:
- Part 1: 10/10 confidence, zero assumptions
- Part 2: PEP 8 compliance, type hints, docstrings
- Part 3: Debounced file watching, AST error handling, 4-level progressive hints"
