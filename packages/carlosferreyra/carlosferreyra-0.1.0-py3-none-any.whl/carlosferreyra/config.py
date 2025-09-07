"""Configuration for the CLI business card."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PersonalInfo:
    name: str
    title: str
    company: Optional[str]
    location: str
    skills: List[str]


@dataclass
class URLs:
    email: str
    resume: str
    portfolio: str
    github: str
    linkedin: str
    twitter: Optional[str]


@dataclass
class ThemeConfig:
    border_color: str
    background_color: str
    animation_speed: dict


@dataclass
class AppConfig:
    personal_info: PersonalInfo
    urls: URLs
    theme: ThemeConfig


# Configuration instance
CONFIG = AppConfig(
    personal_info=PersonalInfo(
        name="Carlos Ferreyra",
        title="Software Engineer & Developer",
        company="Self Employed",
        location="United States",
        skills=["TypeScript", "React", "Node.js", "Python", "GCP", "DevOps"],
    ),
    urls=URLs(
        email="mailto:eduferreyraok@gmail.com",
        resume="https://www.carlosferreyra.me/resume.pdf",
        portfolio="https://www.carlosferreyra.me",
        github="https://github.com/carlosferreyra",
        linkedin="https://linkedin.com/in/eduferreyraok",
        twitter="https://twitter.com/eduferreyraok",
    ),
    theme=ThemeConfig(
        border_color="cyan",
        background_color="#1a1a2e",
        animation_speed={"fast": 0.01, "medium": 0.025, "slow": 0.04},
    ),
)
