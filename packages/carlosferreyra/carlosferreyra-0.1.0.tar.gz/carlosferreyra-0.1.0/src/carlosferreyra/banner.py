"""Welcome banner with ASCII art."""

import pyfiglet
from rich.console import Console
from rich.text import Text

from .config import CONFIG
from .utils import animate_text, animated_spinner, sleep

console = Console()


def welcome_banner() -> None:
    """Display the welcome banner with ASCII art."""
    console.clear()
    console.print()

    with animated_spinner("Initializing...", 0.3):
        pass

    # Create ASCII art
    ascii_art = pyfiglet.figlet_format(CONFIG.personal_info.name, font="big")

    # Print each line with rainbow effect
    lines = ascii_art.split("\n")
    for line in lines:
        if line.strip():  # Skip empty lines
            text = Text(line)
            text.stylize("bold magenta")
            console.print(text)
            sleep(CONFIG.theme.animation_speed["medium"])

    # Animate the title
    title_text = f"{{ {CONFIG.personal_info.title} }}"
    animate_text(title_text, CONFIG.theme.animation_speed["slow"])
