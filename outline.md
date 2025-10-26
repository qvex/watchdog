# Python Learning Bot - Starter Template
# Complete project structure for VS Code + Claude Code

"""
PROJECT STRUCTURE:
python-learning-bot/
├── src/
│   ├── __init__.py
│   ├── file_watcher.py
│   ├── code_analyzer.py
│   ├── hint_engine.py
│   ├── state_manager.py
│   └── vscode_integration.py
├── hints/
│   └── patterns.json
├── tests/
│   └── test_hint_engine.py
├── examples/
│   └── practice.py
├── requirements.txt
├── setup.py
└── README.md
"""

# ============================================================================
# FILE: requirements.txt
# ============================================================================
"""
watchdog==3.0.0
gitpython==3.1.40
openai==1.3.0
anthropic==0.7.0
python-dotenv==1.0.0
rich==13.7.0
"""

# ============================================================================
# FILE: src/file_watcher.py
# ============================================================================
import time
import difflib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import Callable, Optional
import ast


class CodeChangeEvent:
    """Represents a code change event with before/after states."""
    
    def __init__(self, file_path: str, before: str, after: str):
        self.file_path = file_path
        self.before = before
        self.after = after
        self.deleted_lines = self._get_deleted_lines()
        self.deleted_functions = self._get_deleted_functions()
    
    def _get_deleted_lines(self) -> list[str]:
        """Extract lines that were deleted."""
        diff = difflib.unified_diff(
            self.before.splitlines(),
            self.after.splitlines(),
            lineterm=''
        )
        deleted = []
        for line in diff:
            if line.startswith('-') and not line.startswith('---'):
                deleted.append(line[1:].strip())
        return deleted
    
    def _get_deleted_functions(self) -> list[dict]:
        """Identify if any functions were deleted using AST."""
        try:
            before_tree = ast.parse(self.before)
            after_tree = ast.parse(self.after)
            
            before_funcs = {node.name: node for node in ast.walk(before_tree) 
                           if isinstance(node, ast.FunctionDef)}
            after_funcs = {node.name: node for node in ast.walk(after_tree) 
                          if isinstance(node, ast.FunctionDef)}
            
            deleted = []
            for name, node in before_funcs.items():
                if name not in after_funcs:
                    deleted.append({
                        'name': name,
                        'lineno': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
            return deleted
        except SyntaxError:
            return []


class PythonFileWatcher(FileSystemEventHandler):
    """Watches Python files for changes and triggers callbacks."""
    
    def __init__(self, file_path: str, on_change: Callable[[CodeChangeEvent], None]):
        self.file_path = Path(file_path).resolve()
        self.on_change = on_change
        self._last_content = self._read_file()
        self._debounce_time = 0.5  # seconds
        self._last_modified = 0
    
    def _read_file(self) -> str:
        """Read the current file content."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return ""
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.src_path != str(self.file_path):
            return
        
        # Debounce rapid changes
        current_time = time.time()
        if current_time - self._last_modified < self._debounce_time:
            return
        self._last_modified = current_time
        
        current_content = self._read_file()
        
        # Only trigger if content actually changed
        if current_content != self._last_content:
            event = CodeChangeEvent(
                str(self.file_path),
                self._last_content,
                current_content
            )
            self._last_content = current_content
            self.on_change(event)
    
    def start(self):
        """Start watching the file."""
        observer = Observer()
        observer.schedule(self, str(self.file_path.parent), recursive=False)
        observer.start()
        print(f"👀 Watching: {self.file_path}")
        return observer


# ============================================================================
# FILE: src/code_analyzer.py
# ============================================================================
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


# ============================================================================
# FILE: src/hint_engine.py
# ============================================================================
from typing import List, Optional
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
                    "🤔 You need to iterate through something here...",
                    "💭 Think about repeating an action for each item...",
                ],
                2: [
                    "📝 A loop structure would work well here. Which type of loop fits?",
                    "🔁 Consider: do you know the number of iterations, or are you checking a condition?",
                ],
                3: [
                    "✏️ Syntax: `for item in collection:` or `while condition:`",
                    "💡 Try starting with `for` followed by a variable name...",
                ],
                4: [
                    "```python\nfor item in items:\n    # your code here\n```",
                    "```python\nwhile condition:\n    # your code here\n```",
                ]
            },
            'functions': {
                1: [
                    "🤔 This looks like it should be its own reusable piece of logic...",
                    "💭 Think about wrapping this in a function for clarity...",
                ],
                2: [
                    "📝 You'll need: function definition, parameters, return value",
                    "🔧 What inputs does this need? What should it output?",
                ],
                3: [
                    "✏️ Syntax: `def function_name(parameters):`",
                    "💡 Start with `def`, choose a descriptive name...",
                ],
                4: [
                    "```python\ndef function_name(param1, param2):\n    # implementation\n    return result\n```",
                ]
            },
            'conditionals': {
                1: [
                    "🤔 You need to make a decision based on a condition...",
                    "💭 Think about when you'd want different code to run...",
                ],
                2: [
                    "📝 An if-statement controls the flow. What's the condition?",
                    "🔀 Consider: what condition determines which path to take?",
                ],
                3: [
                    "✏️ Syntax: `if condition:` or add `elif`/`else`",
                    "💡 Try `if some_condition:` followed by indented code...",
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
        context: CodeContext, 
        current_hint_level: int = 1,
        time_elapsed: float = 0
    ) -> Hint:
        """Generate a progressive hint based on context and current level."""
        
        pattern_type = context.missing_element
        
        # Get appropriate hint template
        templates = self.hint_templates.get(pattern_type, {})
        level_hints = templates.get(current_hint_level, [
            f"🤔 Think about adding {pattern_type} here..."
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


# ============================================================================
# FILE: src/state_manager.py
# ============================================================================
import time
from typing import Dict, Optional
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


class StateManager:
    """Manages learning state and progress tracking."""
    
    def __init__(self):
        self.current_session: Optional[LearningSession] = None
        self.sessions_history: List[LearningSession] = []
        self._task_start_time: Optional[float] = None
    
    def start_session(self, file_path: str):
        """Start a new learning session."""
        self.current_session = LearningSession(file_path=file_path)
        self._task_start_time = time.time()
        print(f"🎯 Learning session started for: {file_path}")
    
    def record_hint(self, hint: Hint):
        """Record that a hint was shown."""
        if self.current_session:
            self.current_session.hints_shown.append(hint.content)
            self.current_session.current_hint_level = hint.level
    
    def get_time_stuck(self) -> float:
        """Get time spent on current task."""
        if self._task_start_time:
            return time.time() - self._task_start_time
        return 0
    
    def reset_timer(self):
        """Reset the task timer (when code is updated)."""
        self._task_start_time = time.time()
    
    def mark_completed(self):
        """Mark current task as completed."""
        if self.current_session:
            self.current_session.task_completed = True
            self.sessions_history.append(self.current_session)
            print("✅ Great job! Task completed!")
    
    def get_current_hint_level(self) -> int:
        """Get current hint level for the session."""
        return self.current_session.current_hint_level if self.current_session else 1
    
    def end_session(self):
        """End the current session."""
        if self.current_session:
            self.sessions_history.append(self.current_session)
            self.current_session = None
            print("📊 Session ended. Great work!")


# ============================================================================
# FILE: src/vscode_integration.py
# ============================================================================
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import sys


class VSCodeIntegration:
    """Handles integration with VS Code for displaying hints."""
    
    def __init__(self):
        self.console = Console()
    
    def display_hint(self, hint: Hint):
        """Display a hint in the terminal (visible in VS Code)."""
        
        # Create styled hint based on level
        emoji_map = {1: "🤔", 2: "💡", 3: "✏️", 4: "📝"}
        emoji = emoji_map.get(hint.level, "💭")
        
        # Format hint content
        hint_text = f"{emoji} **Hint (Level {hint.level}/4)**\n\n{hint.content}"
        
        # Add best practice if available
        if hint.best_practice:
            hint_text += f"\n\n✨ **Best Practice:** {hint.best_practice}"
        
        # Display in rich panel
        self.console.print(Panel(
            Markdown(hint_text),
            title="Python Learning Assistant",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def show_progress(self, session: LearningSession):
        """Show current progress."""
        self.console.print(f"\n📈 Hints shown: {len(session.hints_shown)}")
        self.console.print(f"⏱️  Time: {session.time_on_current_task:.0f}s\n")
    
    def show_encouragement(self):
        """Show encouraging message."""
        messages = [
            "🌟 You're doing great!",
            "💪 Keep going!",
            "🚀 You've got this!",
        ]
        self.console.print(f"\n{random.choice(messages)}\n")


# ============================================================================
# FILE: main.py - Main application entry point
# ============================================================================
import sys
import argparse
from pathlib import Path
from src.file_watcher import PythonFileWatcher, CodeChangeEvent
from src.code_analyzer import CodeAnalyzer
from src.hint_engine import HintEngine
from src.state_manager import StateManager
from src.vscode_integration import VSCodeIntegration


class PythonLearningBot:
    """Main application coordinator."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.analyzer = CodeAnalyzer()
        self.hint_engine = HintEngine()
        self.state = StateManager()
        self.ui = VSCodeIntegration()
        self.watcher = None
    
    def on_code_change(self, event: CodeChangeEvent):
        """Handle code changes and provide hints."""
        
        # Reset timer when user makes changes
        self.state.reset_timer()
        
        # If deletion detected, analyze and provide hint
        if event.deleted_lines or event.deleted_functions:
            print("\n🔍 Detected code deletion - analyzing...")
            
            context = self.analyzer.analyze_deletion(
                event.before, 
                event.after
            )
            
            # Check if we should increase hint level
            time_stuck = self.state.get_time_stuck()
            current_level = self.state.get_current_hint_level()
            
            if self.hint_engine.should_increase_hint_level(time_stuck, current_level):
                current_level = min(current_level + 1, 4)
            
            # Generate and display hint
            hint = self.hint_engine.generate_hint(context, current_level, time_stuck)
            self.state.record_hint(hint)
            self.ui.display_hint(hint)
    
    def start(self):
        """Start the learning bot."""
        self.ui.console.print("\n🎓 Python Learning Bot Started!\n", style="bold green")
        self.ui.console.print(f"📁 Watching: {self.file_path}\n")
        self.ui.console.print("💡 Delete code to receive progressive hints!\n")
        
        self.state.start_session(self.file_path)
        
        self.watcher = PythonFileWatcher(
            self.file_path,
            self.on_code_change
        )
        
        observer = self.watcher.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.state.end_session()
            print("\n👋 Learning session ended. Keep practicing!")
        
        observer.join()


def main():
    parser = argparse.ArgumentParser(description='Python Learning Bot')
    parser.add_argument('file', help='Python file to watch')
    args = parser.parse_args()
    
    if not Path(args.file).exists():
        print(f"❌ Error: File '{args.file}' not found")
        sys.exit(1)
    
    bot = PythonLearningBot(args.file)
    bot.start()


if __name__ == "__main__":
    main()


# ============================================================================
# FILE: examples/practice.py - Example practice file
# ============================================================================
"""
Practice file for testing the Python Learning Bot.

Try deleting the function below and rewriting it yourself!
The bot will guide you with progressive hints.
"""

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


# Test the function
numbers = [10, 20, 30, 40, 50]
result = calculate_average(numbers)
print(f"Average: {result}")


# ============================================================================
# FILE: README.md
# ============================================================================
"""
# Python Learning Bot 🐍🤖

An interactive Python learning assistant that provides progressive hints as you code.

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the bot:**
```bash
python main.py examples/practice.py
```

3. **Start learning:**
   - Open `examples/practice.py` in VS Code
   - Delete a function or code block
   - Watch the terminal for progressive hints!

## How It Works

1. **Delete code** - Remove a function, loop, or any code block
2. **Get hints** - Receive progressive hints (4 levels)
3. **Rewrite** - Practice writing the code yourself
4. **Learn** - Hints include best practices

## Using with Claude Code

Open VS Code and use Claude Code to extend this bot:

```
"Add a feature to hint_engine.py that detects when 
I'm writing inefficient code and suggests optimizations"
```

```
"Extend code_analyzer.py to detect common beginner mistakes 
like missing colons or incorrect indentation"
```

```
"Add support for tracking my learning progress over multiple sessions"
```

## Features to Add with Claude Code

- 🎯 Custom hint patterns for specific topics
- 📊 Progress tracking dashboard
- 🏆 Achievement system
- 🔄 Integration with Claude API for dynamic hints
- 📝 Exercise generation

## Project Structure

- `src/file_watcher.py` - Monitors file changes
- `src/code_analyzer.py` - Analyzes code context
- `src/hint_engine.py` - Generates progressive hints
- `src/state_manager.py` - Tracks learning progress
- `src/vscode_integration.py` - Terminal UI
- `main.py` - Application entry point

Happy Learning! 🚀
"""