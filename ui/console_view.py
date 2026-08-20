import re
import threading
import time

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core import server_manager
from core.i18n import t

console = Console()

_INFO = "dim"
_WARN = "bold yellow"
_ERR = "bold red"
_INFO_OK = "bold green"


def _style_line(line: str):
    if re.search(r"\[(?:WARN|WARNING)\]", line, re.I):
        return _WARN
    if re.search(r"(ERROR|Exception|Failed|Caused by|SEVERE)", line, re.I):
        return _ERR
    if re.search(r"(Done \(|joined the game|\(!\)? )", line, re.I):
        return _INFO_OK
    return _INFO


def _timestamp():
    return time.strftime("[%H:%M:%S]")


def run_console(name: str):
    proc = server_manager.get_process(name)
    if not proc:
        console.print(Panel(f"[bold yellow]{t('console.not_running')}[/bold yellow]", border_style="yellow"))
        return

    console.clear()
    header = Panel(
        f"[bold cyan]{t('console.title')}[/bold cyan]  —  [bold white]{name}[/bold white]  "
        f"[dim]{t('console.hint')}[/dim]",
        border_style="cyan",
    )
    console.print(header)

    stop_flag = threading.Event()

    def reader():
        for line in proc.stdout:
            if stop_flag.is_set():
                break
            if not line.strip():
                continue
            style = _style_line(line)
            tl = f"{_timestamp()} {line.rstrip()}"
            console.print(tl, style=style, highlight=False)

    th = threading.Thread(target=reader, daemon=True)
    th.start()

    leftover_errors = 0
    while True:
        if proc.poll() is not None and proc is not server_manager.get_process(name):
            # died
            server_manager.check_dead(name)
            console.print(f"[bold red]{t('console.server_stopped')}[/bold red]")
            break
        try:
            cmd = console.input("[bold][Command][/bold] > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        low = cmd.lower()
        if low in ("exit", "quit", "salir", "q"):
            break
        if low in ("stop", "end", "detener"):
            server_manager.stop_server(name)
            console.print(f"[bold yellow]{t('console.left')}[/bold yellow] {t('stop.done')}")
            break
        if cmd:
            server_manager.send_command(name, cmd)

    stop_flag.set()
    if th.is_alive():
        time.sleep(0.3)