"""Business card display with Rich formatting."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .config import CONFIG

console = Console()


def create_profile_card() -> None:
    """Create and display the profile business card."""

    # Create card content
    card_lines = []

    # Name and title
    name_text = Text(CONFIG.personal_info.name, style="bold bright_magenta")
    title_text = Text(CONFIG.personal_info.title, style="white")
    card_lines.extend([name_text, title_text, ""])

    # Company and location
    if CONFIG.personal_info.company:
        company_text = Text("Working at ", style="white") + Text(
            CONFIG.personal_info.company, style="bright_yellow"
        )
        card_lines.append(company_text)

    location_text = Text(f"📍 {CONFIG.personal_info.location}", style="dim white")
    card_lines.extend([location_text, ""])

    # Skills
    skills_text = Text("⚡ Skills: ", style="white") + Text(
        " | ".join(CONFIG.personal_info.skills), style="bright_cyan"
    )
    card_lines.extend([skills_text, ""])

    # Social links
    github_text = (
        Text("📦 GitHub:    ", style="white")
        + Text("{ ")
        + Text("github.com/", style="dim")
        + Text("carlosferreyra", style="bright_green")
        + Text(" }")
    )
    linkedin_text = (
        Text("💼 LinkedIn:  ", style="white")
        + Text("{ ")
        + Text("linkedin.com/in/", style="dim")
        + Text("carlosferreyra", style="bright_blue")
        + Text(" }")
    )

    card_lines.extend([github_text, linkedin_text])

    if CONFIG.urls.twitter:
        twitter_text = (
            Text("🐦 Twitter:   ", style="white")
            + Text("{ ")
            + Text("twitter.com/", style="dim")
            + Text("carlosferreyra", style="bright_cyan")
            + Text(" }")
        )
        card_lines.append(twitter_text)

    web_text = (
        Text("🌐 Website:   ", style="white")
        + Text("{ ")
        + Text(CONFIG.urls.portfolio.replace("https://", ""), style="bright_cyan")
        + Text(" }")
    )
    card_lines.append(web_text)

    card_lines.append("")

    # CLI command
    cli_text = (
        Text("📇 Card:      ", style="white")
        + Text("uvx ", style="bright_red")
        + Text("carlosferreyra", style="white")
    )
    card_lines.extend([cli_text, ""])

    # Call to action
    cta1 = Text(
        "🚀 Available for exciting opportunities and collaborations!",
        style="bold bright_red",
    )
    cta2 = Text(
        "💭 Let's connect and create something amazing together!",
        style="bold bright_cyan",
    )
    card_lines.extend([cta1, cta2])

    # Create the panel
    card_content = Text()
    for i, line in enumerate(card_lines):
        if i > 0:
            card_content.append("\n")
        if isinstance(line, str):
            card_content.append(line)
        else:
            card_content.append_text(line)

    panel = Panel(
        card_content,
        title=f"[bold cyan]{CONFIG.personal_info.name}'s Business Card[/bold cyan]",
        title_align="center",
        border_style="cyan",
        padding=(1, 2),
    )

    # Display the panel properly
    console.print(panel)
