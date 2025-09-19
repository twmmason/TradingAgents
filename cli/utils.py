import questionary
from typing import List, Optional, Tuple, Dict
from rich.console import Console

from cli.models import AnalystType

console = Console()

ANALYST_ORDER = [
    ("Market Analyst", AnalystType.MARKET),
    ("Social Media Analyst", AnalystType.SOCIAL),
    ("News Analyst", AnalystType.NEWS),
    ("Fundamentals Analyst", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        "Enter the ticker symbol to analyze:",
        validate=lambda x: len(x.strip()) > 0 or "Please enter a valid ticker symbol.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        console.print("\n[red]No ticker symbol provided. Exiting...[/red]")
        exit(1)

    return ticker.strip().upper()


def get_analysis_date() -> str:
    """Prompt the user to enter a date in YYYY-MM-DD format."""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "Enter the analysis date (YYYY-MM-DD):",
        validate=lambda x: validate_date(x.strip())
        or "Please enter a valid date in YYYY-MM-DD format.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        console.print("\n[red]No date provided. Exiting...[/red]")
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""
    choices = questionary.checkbox(
        "Select Your [Analysts Team]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        instruction="\n- Press Space to select/unselect analysts\n- Press 'a' to select/unselect all\n- Press Enter when done",
        validate=lambda x: len(x) > 0 or "You must select at least one analyst.",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        console.print("\n[red]No analysts selected. Exiting...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        ("Shallow - Quick research, few debate and strategy discussion rounds", 1),
        ("Medium - Middle ground, moderate debate rounds and strategy discussion", 3),
        ("Deep - Comprehensive research, in depth debate and strategy discussion", 5),
    ]

    choice = questionary.select(
        "Select Your [Research Depth]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No research depth selected. Exiting...[/red]")
        exit(1)

    return choice


def select_shallow_thinking_agent(provider=None) -> str:
    """Select shallow thinking llm engine using an interactive selection."""

    # Google Gemini models only - including latest 2.5 models
    GOOGLE_SHALLOW_OPTIONS = [
        ("Gemini 2.5 Flash - Latest generation with enhanced capabilities", "gemini-2.5-flash"),
        ("Gemini 2.5 Flash Lite - Lightweight version for fast responses", "gemini-2.5-flash-lite"),
        ("Gemini 2.0 Flash-Exp - Experimental fast model with grounding", "gemini-2.0-flash-exp"),
        ("Gemini 2.0 Flash - Next generation features, speed, and thinking", "gemini-2.0-flash"),
        ("Gemini 1.5 Flash - Fast and efficient for quick tasks", "gemini-1.5-flash"),
        ("Gemini 1.5 Pro - Standard model with solid capabilities", "gemini-1.5-pro"),
    ]

    choice = questionary.select(
        "Select Your [Quick-Thinking Google Gemini Model]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in GOOGLE_SHALLOW_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(
            "\n[red]No shallow thinking llm engine selected. Exiting...[/red]"
        )
        exit(1)

    return choice


def select_deep_thinking_agent(provider=None) -> str:
    """Select deep thinking llm engine using an interactive selection."""

    # Google Gemini models only - including latest 2.5 models
    GOOGLE_DEEP_OPTIONS = [
        ("Gemini 2.5 Pro - Most advanced model with superior reasoning", "gemini-2.5-pro"),
        ("Gemini 2.5 Flash - Latest generation with enhanced capabilities", "gemini-2.5-flash"),
        ("Gemini 2.0 Flash-Exp - Experimental model with advanced reasoning", "gemini-2.0-flash-exp"),
        ("Gemini 2.0 Flash - Next generation features and deep thinking", "gemini-2.0-flash"),
        ("Gemini 1.5 Pro - Powerful model for complex tasks", "gemini-1.5-pro"),
        ("Gemini Pro - Premier reasoning and problem-solving model", "gemini-pro"),
    ]
    
    choice = questionary.select(
        "Select Your [Deep-Thinking Google Gemini Model]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in GOOGLE_DEEP_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No deep thinking llm engine selected. Exiting...[/red]")
        exit(1)

    return choice

# Function no longer needed as we're hardcoding to Google
# def select_llm_provider() -> tuple[str, str]:
#     """Select the OpenAI api url using interactive selection."""
#     # Always return Google
#     return "google", "https://generativelanguage.googleapis.com/v1"
