from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def ask(question: str, options: list, prompt="> ", allow_custom=False, multiple=False):
    """Simple interactive menu. options: list of (key, label) or list of (key, label, desc)."""
    console.print()
    console.print(Panel(f"[bold]{question}[/bold]", border_style="cyan", padding=(0, 1)))
    for idx, opt in enumerate(options, 1):
        key = opt[0]
        label = opt[1]
        desc = opt[2] if len(opt) > 2 else ""
        mark = "●" if is_running_marker(key) else "○"
        if len(opt) > 2:
            console.print(f"  [bold cyan][{key}][/bold cyan] {label}  [dim]- {desc}[/dim]")
        else:
            console.print(f"  [bold cyan][{key}][/bold cyan] {label}")
    console.print()
    while True:
        choice = console.input(f"[bold cyan]{prompt}[/bold cyan]").strip().lower()
        if allow_custom:
            return choice
        for opt in options:
            if opt[0].lower() == choice:
                return opt[0]
        console.print("[red]Invalid option.[/red]")


def is_running_marker(key: str) -> bool:
    return False


def confirm(msg: str, default_yes=True) -> bool:
    suffix = "[Y/n]" if default_yes else "[y/N]"
    ans = console.input(f"[bold]{msg}[/bold] {suffix}: ").strip().lower()
    if not ans:
        return default_yes
    return ans in ("y", "yes", "s", "si", "sí", "1")


def input_text(prompt: str, default: str = None, validate=None) -> str:
    while True:
        if default:
            ans = console.input(f"[bold]{prompt}[/bold] [dim]({default})[/dim]: ").strip()
        else:
            ans = console.input(f"[bold]{prompt}[/bold]: ").strip()
        if not ans and default:
            ans = default
        if not ans:
            console.print("[red]This field cannot be empty.[/red]")
            continue
        if validate and not validate(ans):
            console.print("[red]Invalid value.[/red]")
            continue
        return ans


def input_int(prompt: str, default: int = None, minimum: int = None, maximum: int = None) -> int:
    while True:
        if default is not None:
            ans = console.input(f"[bold]{prompt}[/bold] [dim]({default})[/dim]: ").strip()
        else:
            ans = console.input(f"[bold]{prompt}[/bold]: ").strip()
        if not ans and default is not None:
            return default
        try:
            val = int(ans)
        except ValueError:
            console.print("[red]Enter a number.[/red]")
            continue
        if minimum is not None and val < minimum:
            console.print(f"[red]Min value: {minimum}[/red]")
            continue
        if maximum is not None and val > maximum:
            console.print(f"[red]Max value: {maximum}[/red]")
            continue
        return val


def error(msg: str, detail: str = None):
    console.print(f"[bold red]✗ {msg}[/bold red]")
    if detail:
        console.print(Panel(detail, title="[View technical details]", border_style="red", expand=False))


def success(msg: str):
    console.print(f"[bold green]✓ {msg}[/bold green]")


def warning(msg: str):
    console.print(f"[bold yellow]⚠ {msg}[/bold yellow]")


def info(msg: str):
    console.print(f"[cyan]{msg}[/cyan]")


def title(text: str, border="cyan"):
    console.print(Panel(f"[bold]{text}[/bold]", border_style=border, padding=(0, 1), expand=False))


def header_table(pairs: dict, title=None, border="cyan"):
    table = Table(show_header=False, border_style=border, box=None, expand=False, padding=(0, 2))
    for k, v in pairs.items():
        table.add_row(f"[bold]{k}[/bold]", f"{v}")
    console.print(Panel(table, border_style=border, title=title, padding=(0, 1)))