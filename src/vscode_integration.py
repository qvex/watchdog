from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import random


class VSCodeIntegration:
    def __init__(self):
        self.console = Console()

    def display_hint(self, hint):
        hint_text = f"**Hint (Level {hint.level}/4)**\n\n{hint.content}"

        if hint.best_practice:
            hint_text += f"\n\n**Best Practice:** {hint.best_practice}"

        self.console.print(Panel(
            Markdown(hint_text),
            title="Watchdog Learning Assistant",
            border_style="blue",
            padding=(1, 2)
        ))

    def show_progress(self, session):
        self.console.print(f"\nHints shown: {len(session.hints_shown)}")
        self.console.print(f"Time: {session.time_on_current_task:.0f}s\n")

    def show_encouragement(self):
        messages = [
            "You're doing great!",
            "Keep going!",
            "You've got this!",
        ]
        self.console.print(f"\n{random.choice(messages)}\n")
