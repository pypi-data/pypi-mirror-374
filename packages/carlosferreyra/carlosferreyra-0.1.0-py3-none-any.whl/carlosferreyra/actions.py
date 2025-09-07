"""Action handlers for menu options."""

import webbrowser

from rich.console import Console

from .config import CONFIG
from .utils import animate_text, animated_spinner

console = Console()


def open_url(url: str) -> bool:
    """Open URL in default browser."""
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        console.print(f"[red]Error opening URL: {e}[/red]")
        return False


class ActionHandlers:
    """Collection of action handlers for menu options."""

    @staticmethod
    def email():
        """Open email client."""
        with animated_spinner("Opening mail client..."):
            success = open_url(CONFIG.urls.email)

        if success:
            console.print("[bright_red]📧 Email client opened![/bright_red]")
            animate_text("Looking forward to hearing from you!")
        else:
            console.print("[red]❌ Failed to open email client[/red]")

    @staticmethod
    def view_resume():
        """Open resume in browser."""
        with animated_spinner("Preparing to open resume..."):
            success = open_url(CONFIG.urls.resume)

        if success:
            console.print("[green]📥 Resume opened in your browser! 🎉[/green]")
            animate_text("Tip: You can download it directly")
        else:
            console.print("[red]❌ Failed to open resume[/red]")

    @staticmethod
    def view_portfolio():
        """Open portfolio website."""
        with animated_spinner("Loading portfolio..."):
            success = open_url(CONFIG.urls.portfolio)

        if success:
            console.print("[bright_cyan]🌐 Portfolio opened![/bright_cyan]")
            animate_text("Hope you enjoy exploring my work!")
        else:
            console.print("[red]❌ Failed to open portfolio[/red]")

    @staticmethod
    def view_github():
        """Open GitHub profile."""
        with animated_spinner("Opening GitHub..."):
            success = open_url(CONFIG.urls.github)

        if success:
            console.print("[bright_green]💻 GitHub profile opened![/bright_green]")
            animate_text("Check out my latest projects!")
        else:
            console.print("[red]❌ Failed to open GitHub[/red]")

    @staticmethod
    def view_linkedin():
        """Open LinkedIn profile."""
        with animated_spinner("Opening LinkedIn..."):
            success = open_url(CONFIG.urls.linkedin)

        if success:
            console.print("[bright_blue]💼 LinkedIn profile opened![/bright_blue]")
            animate_text("Let's connect professionally!")
        else:
            console.print("[red]❌ Failed to open LinkedIn[/red]")

    @staticmethod
    def view_twitter():
        """Open Twitter profile."""
        if CONFIG.urls.twitter:
            with animated_spinner("Opening Twitter..."):
                success = open_url(CONFIG.urls.twitter)

            if success:
                console.print("[bright_cyan]🐦 Twitter profile opened![/bright_cyan]")
                animate_text("Follow me for tech updates!")
            else:
                console.print("[red]❌ Failed to open Twitter[/red]")
        else:
            console.print("[yellow]Twitter profile not configured[/yellow]")


# Create action handlers instance
action_handlers = {
    "email": ActionHandlers.email,
    "view_resume": ActionHandlers.view_resume,
    "view_portfolio": ActionHandlers.view_portfolio,
    "view_github": ActionHandlers.view_github,
    "view_linkedin": ActionHandlers.view_linkedin,
    "view_twitter": ActionHandlers.view_twitter,
}
