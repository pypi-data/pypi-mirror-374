"""Utility functions for animations and effects."""

import time
from contextlib import contextmanager

from rich.console import Console

console = Console()


def sleep(seconds: float) -> None:
    """Sleep for given seconds."""
    time.sleep(seconds)


@contextmanager
def animated_spinner(text: str, duration: float = 0.5):
    """Create an animated spinner context manager."""
    with console.status(text, spinner="dots"):
        sleep(duration)
        yield


def animate_text(text: str, speed: float = 0.01) -> None:
    """Animate text by printing character by character."""
    console.print()
    for char in text:
        console.print(char, end="")
        sleep(speed)
    console.print()


def clear_screen() -> None:
    """Clear the terminal screen."""
    console.clear()


def gradient_text(text: str, style: str = "bold blue") -> str:
    """Apply gradient-like styling to text using Rich."""
    return f"[{style}]{text}[/{style}]"
