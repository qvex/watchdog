import time
import difflib
import logging
import ast
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import Callable, Optional, List, Dict

logger = logging.getLogger(__name__)

DEBOUNCE_TIME_SECONDS = 0.5
DEFAULT_ENCODING = 'utf-8'


class CodeChangeEvent: #what does this class do
    def __init__(self, file_path: str, before: str, after: str):
        self.file_path = file_path
        self.before = before
        self.after = after
        self.deleted_lines = self._get_deleted_lines()
        self.deleted_functions = self._get_deleted_functions()

    def _get_deleted_lines(self) -> List[str]:
        try:
            diff = difflib.unified_diff(
                self.before.splitlines(),
                self.after.splitlines(),
                lineterm=''
            )
            deleted = []
            for line in diff:
                if line.startswith('-') and not line.startswith('---'):
                    deleted.append(line[1:].strip())

            logger.debug("Detected %d deleted lines", len(deleted))
            return deleted
        except Exception as e:
            logger.warning("Error detecting deleted lines: %s", str(e))
            return []

    def _get_deleted_functions(self) -> List[Dict[str, any]]:
        try:
            before_tree = ast.parse(self.before)
            after_tree = ast.parse(self.after)

            before_funcs = {
                node.name: node for node in ast.walk(before_tree)
                if isinstance(node, ast.FunctionDef)
            }
            after_funcs = {
                node.name: node for node in ast.walk(after_tree)
                if isinstance(node, ast.FunctionDef)
            }

            deleted = []
            for name, node in before_funcs.items():
                if name not in after_funcs:
                    deleted.append({
                        'name': name,
                        'lineno': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })

            if deleted:
                logger.info(
                    "Detected %d deleted functions: %s",
                    len(deleted),
                    [f['name'] for f in deleted]
                )
            return deleted
        except SyntaxError as e:
            logger.debug("Syntax error while detecting deleted functions: %s", str(e))
            return []
        except AttributeError as e:
            logger.warning("Attribute error in _get_deleted_functions: %s", str(e))
            return []
        except Exception as e:
            logger.error(
                "Unexpected error detecting deleted functions: %s",
                str(e),
                exc_info=True
            )
            return []


class PythonFileWatcher(FileSystemEventHandler):
    def __init__(self, file_path: str, on_change: Callable[[CodeChangeEvent], None]):
        try:
            self.file_path = Path(file_path).resolve()

            if not self.file_path.exists():
                raise FileNotFoundError(
                    f"File not found: {file_path}. "
                    f"Please ensure the file exists before starting the watcher."
                )

            if not self.file_path.is_file():
                raise ValueError(
                    f"Path is not a file: {file_path}. "
                    f"Please provide a path to a Python file."
                )

            self.on_change = on_change
            self._last_content = self._read_file()
            self._debounce_time = DEBOUNCE_TIME_SECONDS
            self._last_modified = 0

            logger.info("PythonFileWatcher initialized for: %s", self.file_path)
        except Exception as e:
            logger.error("Failed to initialize PythonFileWatcher: %s", str(e))
            raise

    def _read_file(self) -> str:
        try:
            with open(self.file_path, 'r', encoding=DEFAULT_ENCODING) as f:
                content = f.read()
                logger.debug("Read %d characters from file", len(content))
                return content
        except FileNotFoundError:
            logger.error("File not found: %s", self.file_path)
            print(f"Error: File '{self.file_path}' not found")
            return ""
        except PermissionError:
            logger.error("Permission denied reading file: %s", self.file_path)
            print(f"Error: Permission denied reading '{self.file_path}'")
            return ""
        except UnicodeDecodeError as e:
            logger.error("Unicode decode error reading file: %s", str(e))
            print(f"Error: Cannot decode file '{self.file_path}' (not a text file?)")
            return ""
        except Exception as e:
            logger.error("Unexpected error reading file: %s", str(e), exc_info=True)
            print(f"Error reading file: {e}")
            return ""

    def on_modified(self, event):
        try:
            if event.src_path != str(self.file_path):
                return

            current_time = time.time()
            if current_time - self._last_modified < self._debounce_time:
                logger.debug("Event debounced (too soon)")
                return
            self._last_modified = current_time

            current_content = self._read_file()

            if current_content != self._last_content:
                logger.info("Code change detected in: %s", self.file_path)
                change_event = CodeChangeEvent(
                    str(self.file_path),
                    self._last_content,
                    current_content
                )
                self._last_content = current_content

                try:
                    self.on_change(change_event)
                except Exception as e:
                    logger.error(
                        "Error in on_change callback: %s",
                        str(e),
                        exc_info=True
                    )
                    print(f"Error processing code change: {e}")
        except Exception as e:
            logger.error("Error in on_modified handler: %s", str(e), exc_info=True)
            print(f"Error handling file modification: {e}")

    def start(self) -> Observer:
        try:
            if not self.file_path.parent.exists():
                raise FileNotFoundError(
                    f"Parent directory not found: {self.file_path.parent}"
                )

            observer = Observer()
            observer.schedule(self, str(self.file_path.parent), recursive=False)
            observer.start()

            print(f"File watcher started: {self.file_path}")
            logger.info("Observer started for: %s", self.file_path)

            return observer
        except PermissionError as e:
            logger.error("Permission denied watching directory: %s", str(e))
            print(
                f"Error: Permission denied. Cannot watch directory "
                f"'{self.file_path.parent}'"
            )
            raise
        except Exception as e:
            logger.error("Failed to start file watcher: %s", str(e), exc_info=True)
            print(f"Error starting file watcher: {e}")
            raise
