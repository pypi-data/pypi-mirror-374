#!/usr/bin/env python3
"""Main entry point for the Carlos Ferreyra CLI business card."""

import sys

from rich.console import Console
from rich.text import Text

from .actions import action_handlers
from .banner import welcome_banner
from .card import create_profile_card
from .menu import prompt_user
from .utils import animate_text

console = Console()


def main() -> None:
    """CLI entry point for carlosferreyra package."""
    try:
        # Show welcome banner
        welcome_banner()

        # Display profile card
        create_profile_card()

        # Show helpful tip
        tip_text = Text()
        tip_text.append("💡 Tip: Use ", style="bright_red")
        tip_text.append("cmd/ctrl + click", style="bright_cyan")
        tip_text.append(" on links to open directly.", style="bright_red")
        console.print()
        console.print(tip_text)
        console.print()

        # Main interaction loop
        while True:
            action = prompt_user()

            if action == "quit":
                animate_text("👋 Thanks for stopping by! Have a great day!")
                break

            # Execute the selected action
            if action in action_handlers:
                action_handlers[action]()
                console.print()  # Add spacing after action
            else:
                console.print("[yellow]Unknown action selected[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Thanks for stopping by! Have a great day![/yellow]")
        sys.exit(0)
    except Exception as error:
        console.print(f"\n[red]❌ An error occurred: {error}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
