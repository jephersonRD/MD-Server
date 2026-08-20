from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from core.i18n import t

ART = [
    "   ███╗   ███╗██████╗   ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ ",
    "   ████╗ ████║██╔══██╗  ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗",
    "   ██╔████╔██║██║  ██║  ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝",
    "   ██║╚██╔╝██║██║  ██║  ╚════██║██╔══╝  ██╔══██╗██║   ██║██╔══╝  ██╔══██╗",
    "   ██║ ╚═╝ ██║██████╔╝  ███████║███████╗██║  ██║╚██████╔╝███████╗██║  ██║",
    "   ╚═╝     ╚═╝╚═════╝   ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝",
]

COLORS = ["cyan", "dark_cyan", "blue", "cyan"]


def banner_text(title: str = None) -> Text:
    title = title or "M D   S E R V E R"
    lines = [t("banner_subtitle", "Minecraft Java Server Manager")] + ART
    text = Text()
    for i, line in enumerate(lines):
        if i == 0:
            text.append(line, style="bold bright_white")
        elif i <= len(ART):  # art gradient
            color = COLORS[(i - 1) % len(COLORS)]
            text.append(line, style=f"bold {color}")
        text.append("\n")
    text.append(title, style="bold white on dark_blue")
    text.append("\n")
    return text


def show(console: Console = None):
    console = console or Console()
    console.print()
    console.print(Panel(banner_text(), border_style="cyan", expand=False, padding=(1, 2)))