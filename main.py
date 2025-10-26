import sys
import argparse
import time
from pathlib import Path
from src.file_watcher import PythonFileWatcher, CodeChangeEvent
from src.code_analyzer import CodeAnalyzer
from src.hint_engine import HintEngine
from src.state_manager import StateManager
from src.vscode_integration import VSCodeIntegration

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


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
            print("\nDetected code deletion - analyzing...")

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
        self.ui.console.print("\nWatchdog is now running in the background\n", style="bold green")
        self.ui.console.print(f"Watching: {self.file_path}\n")
        self.ui.console.print("Delete code to receive progressive hints\n")

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
            print("\nLearning session ended. Keep practicing!")

        observer.join()


def main():
    parser = argparse.ArgumentParser(description='Python Learning Bot')
    parser.add_argument('file', help='Python file to watch')
    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)

    bot = PythonLearningBot(args.file)
    bot.start()


if __name__ == "__main__":
    main()
