"""Interactive menu system."""

import inquirer
from rich.console import Console

console = Console()


def get_menu_choices():
    """Get the menu choices for the interactive prompt."""
    return [
        ("📧  Send an Email", "email"),
        ("📥  View Resume", "view_resume"),
        ("🌐  Visit Portfolio", "view_portfolio"),
        ("💻  View GitHub", "view_github"),
        ("💼  View LinkedIn", "view_linkedin"),
        ("🐦  View Twitter", "view_twitter"),
        ("🚪  Exit", "quit"),
    ]


def prompt_user() -> str:
    """Prompt user for menu selection."""
    choices = get_menu_choices()

    questions = [
        inquirer.List(
            "action",
            message="What would you like to do?",
            choices=choices,
            carousel=True,
        )
    ]

    try:
        answers = inquirer.prompt(questions)
        return answers["action"] if answers else "quit"
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]👋 Thanks for stopping by! Have a great day![/yellow]")
        return "quit"
