import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.llm.hint_service import CodeContext, generate_code_hint
from src.effects import Success


def normalize_code(code: str) -> str:
    lines = []
    for line in code.splitlines():
        stripped = line.split('#')[0].strip()
        if stripped:
            lines.append(stripped)
    return '\n'.join(lines)


class CodeHintHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_processed_content = {}

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.py'):
            return

        file_path = str(Path(event.src_path).resolve())

        try:
            code = Path(file_path).read_text(encoding='utf-8')
            normalized = normalize_code(code)
        except:
            return

        if file_path in self.last_processed_content:
            if normalized == self.last_processed_content[file_path]:
                return

        self.last_processed_content[file_path] = normalized

        print(f"\n{'-'*60}")
        print(f"File changed: {Path(file_path).name}")
        print(f"{'-'*60}")

        try:
            last_50_lines = '\n'.join(code.splitlines()[-50:])

            context = CodeContext(
                file_path=Path(file_path).name,
                code_snippet=last_50_lines,
                change_type="modified",
                language="python"
            )

            print("Generating hint...")
            result = generate_code_hint(context)

            if isinstance(result, Success):
                print(f"\nHINT: {result.value}\n")
            else:
                print(f"\nHint generation failed: {result.context}\n")

        except Exception as e:
            print(f"\nError: {str(e)}\n")


def main():
    print("REAL-TIME CODE HINT MONITOR")
    print("Watching Python files in current directory for changes...")
    print("(Press Ctrl+C to stop)\n")

    event_handler = CodeHintHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitoring stopped.")

    observer.join()


if __name__ == "__main__":
    main()
