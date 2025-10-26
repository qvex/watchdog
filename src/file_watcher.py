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
        print(f"File watcher started: {self.file_path}")
        return observer
