import sys
import argparse
import time
import logging
from pathlib import Path
from typing import Optional
from src.file_watcher import PythonFileWatcher, CodeChangeEvent
from src.code_analyzer import CodeAnalyzer
from src.hint_engine import HintEngine
from src.state_manager import StateManager
from src.vscode_integration import VSCodeIntegration
from src.feedback_coordinator import FeedbackCoordinator
from src.graph_builder import ASTGraphBuilder
from src.test_runner_impl import PytestRunner, SimpleTestDetector
from src.proficiency_calculator import SimpleProfileCalculator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watchdog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {'.py'}
MAX_FILE_SIZE_MB = 10

if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


class Watchdog:
    def __init__(self, file_path: str):
        try:
            self.file_path = file_path
            self.analyzer = CodeAnalyzer()
            self.hint_engine = HintEngine()
            self.state = StateManager()
            self.ui = VSCodeIntegration()
            self.watcher: Optional[PythonFileWatcher] = None

            self.graph_builder = ASTGraphBuilder()
            self.test_runner = PytestRunner()
            self.test_detector = SimpleTestDetector()
            self.profile_calculator = SimpleProfileCalculator()
            self.coordinator = FeedbackCoordinator(
                self.graph_builder,
                self.test_runner,
                self.profile_calculator
            )

            logger.info("Watchdog initialized for: %s", file_path)
        except Exception as e:
            logger.error("Failed to initialize Watchdog: %s", str(e), exc_info=True)
            raise

    def on_code_change(self, event: CodeChangeEvent) -> None:
        try:
            self.state.reset_timer()

            if event.deleted_lines or event.deleted_functions:
                logger.info("Code deletion detected")
                print("\nDetected code deletion - analyzing...")

                code_context = self.analyzer.analyze_deletion(
                    event.before,
                    event.after
                )

                enhanced_result = self.coordinator.build_enhanced_context(
                    event.after,
                    code_context,
                    None
                )

                if enhanced_result.value:
                    enhanced_ctx = enhanced_result.value

                    test_file = self.test_detector.get_test_file(self.file_path)
                    if test_file:
                        test_enriched = self.coordinator.enrich_with_tests(
                            enhanced_ctx,
                            test_file
                        )
                        if test_enriched.value:
                            enhanced_ctx = test_enriched.value

                    time_stuck = self.state.get_time_stuck()
                    current_level = self.state.get_current_hint_level()

                    if self.hint_engine.should_increase_hint_level(time_stuck, current_level):
                        current_level = min(current_level + 1, 4)
                        logger.debug("Increasing hint level to: %d", current_level)

                    adaptive_level = self.coordinator.calculate_adaptive_hint_level(
                        enhanced_ctx,
                        current_level
                    )

                    hint = self.hint_engine.generate_hint(
                        code_context,
                        adaptive_level,
                        time_stuck
                    )
                    self.state.record_hint(hint)
                    self.ui.display_hint(hint)

                    if self.coordinator.should_show_test_feedback(enhanced_ctx):
                        if enhanced_ctx.test_result:
                            print(f"\nTest Results: {enhanced_ctx.test_result.failed} failed")
        except Exception as e:
            logger.error("Error handling code change: %s", str(e), exc_info=True)
            print(f"Error processing code change: {e}")
            print("Continuing to watch for changes...")

    def start(self) -> None:
        try:
            self.ui.console.print(
                "\nWatchdog is now running in the background\n",
                style="bold green"
            )
            self.ui.console.print(f"Watching: {self.file_path}\n")
            self.ui.console.print("Delete code to receive progressive hints\n")

            self.state.start_session(self.file_path)

            self.watcher = PythonFileWatcher(
                self.file_path,
                self.on_code_change
            )

            observer = self.watcher.start()
            logger.info("Watchdog started successfully")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, shutting down...")
                observer.stop()
                self.state.end_session()
                print("\nLearning session ended. Keep practicing!")
            except Exception as e:
                logger.error("Error in main event loop: %s", str(e), exc_info=True)
                observer.stop()
                self.state.end_session()
                raise

            observer.join()
        except Exception as e:
            logger.error("Error starting learning bot: %s", str(e), exc_info=True)
            raise


def validate_file_path(file_path: str) -> Path:
    try:
        path = Path(file_path).resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}\n"
                f"Please provide a valid path to a Python file."
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {file_path}\n"
                f"Please provide a path to a Python file, not a directory."
            )

        if path.suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix}\n"
                f"Watchdog only supports Python files (.py)."
            )

        try:
            with open(path, 'r', encoding='utf-8') as f:
                f.read(1)
        except PermissionError:
            raise PermissionError(
                f"Permission denied: {file_path}\n"
                f"Cannot read file. Please check file permissions."
            )
        except UnicodeDecodeError:
            raise ValueError(
                f"File encoding error: {file_path}\n"
                f"File must be valid UTF-8 encoded Python source."
            )

        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            logger.warning(
                "Large file detected: %.2f MB (max recommended: %d MB)",
                file_size_mb,
                MAX_FILE_SIZE_MB
            )
            print(
                f"Warning: File is {file_size_mb:.2f} MB. "
                f"Large files may impact performance."
            )

        logger.info("File validation passed: %s", path)
        return path
    except (FileNotFoundError, ValueError, PermissionError) as e:
        logger.error("File validation failed: %s", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error during file validation: %s", str(e), exc_info=True)
        raise ValueError(f"Error validating file: {e}")


def main() -> None:
    try:
        parser = argparse.ArgumentParser(
            prog='watchdog',
            description='Watchdog - Interactive Python Learning Assistant',
            epilog='Delete code to receive progressive hints while learning Python.'
        )
        parser.add_argument(
            'file',
            help='Path to Python file to watch'
        )
        parser.add_argument(
            '--version',
            action='version',
            version='Watchdog 0.1.0'
        )

        args = parser.parse_args()

        try:
            file_path = validate_file_path(args.file)
        except (FileNotFoundError, ValueError, PermissionError) as e:
            print(f"Error: {e}")
            sys.exit(1)

        try:
            watchdog = Watchdog(str(file_path))
            watchdog.start()
        except KeyboardInterrupt:
            logger.info("Application terminated by user")
            sys.exit(0)
        except Exception as e:
            logger.error("Fatal error: %s", str(e), exc_info=True)
            print(f"\nFatal error: {e}")
            print("Check watchdog.log for details.")
            sys.exit(1)

    except Exception as e:
        logger.error("Unexpected error in main: %s", str(e), exc_info=True)
        print(f"\nUnexpected error: {e}")
        print("Check watchdog.log for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
