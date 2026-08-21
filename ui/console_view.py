import re
import threading
import time

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core import config, network_manager, server_manager
from core.i18n import t

console = Console()

_INFO = "dim"
_WARN = "bold yellow"
_ERR = "bold red"
_INFO_OK = "bold green"

_PLAYER_RE = re.compile(r"[A-Za-z0-9_]{1,16}")


def _style_line(line: str):
    if re.search(r"\[(?:WARN|WARNING)\]", line, re.I):
        return _WARN
    if re.search(r"(ERROR|Exception|Failed|Caused by|SEVERE)", line, re.I):
        return _ERR
    if re.search(r"(Done \(|joined the game|\(!?\) )", line, re.I):
        return _INFO_OK
    return _INFO


def _timestamp():
    return time.strftime("[%H:%M:%S]")


_DONE_RE = re.compile(r"Done\s*\(.*\)\s*!?\s*For help, type \"help\"", re.I)


def _show_online_panel(name):
    meta = config.load_server_meta(name)
    port = server_manager.read_property(config.server_dir(name), "server-port", "25565")
    version = meta.get("version", "?")
    srv_type = meta.get("type", "?").title()
    lip = network_manager.local_ip()

    lines = [
        f"  🎮 {t('online.minecraft')}: [bold]{version}[/bold]",
        f"  ⚙ {t('online.type')}: [cyan]{srv_type}[/cyan]",
        f"  📡 {t('online.port')}: [bold]{port}[/bold]",
        "",
        f"  🏠 [bold]{t('online.this_device')}[/bold]",
        f"      [bold cyan]127.0.0.1:{port}[/bold cyan]",
        "",
        f"  📶 [bold]{t('online.lan')}[/bold]",
    ]
    if lip and lip != "0.0.0.0":
        lines.append(f"      [bold cyan]{lip}:{port}[/bold cyan]")
        lines.append("")
        lines.append(f"  💡 {t('online.tip_device').format(port=port)}")
        lines.append(f"  💡 {t('online.tip_lan')}")
    else:
        lines.append(f"  [bold yellow]⚠ {t('online.no_local_ip')}[/bold yellow]")
        lines.append(f"      {t('online.local_fallback').format(port=port)}")
    lines.append("")
    lines.append(f"  🌎 [bold]{t('online.internet')}[/bold]")
    lines.append(f"  [dim]{t('online.internet_desc')}[/dim]")

    console.print()
    console.print(Panel(
        "\n".join(lines),
        border_style="green",
        title=f"[bold green]✓ {t('online.title')}[/bold green]",
        padding=(1, 2),
    ))
    console.print()


_JOIN_LOGGED_RE = re.compile(r"<([A-Za-z0-9_]{1,16})>(?:\[[^\]]*\])?\s+(?:logged in|joined the game)", re.I)
_JOIN_UUID_RE = re.compile(r"UUID of player ([A-Za-z0-9_]{1,16}) is ", re.I)
_JOIN_BARE_RE = re.compile(r"([A-Za-z0-9_]{1,16})\s+(?:joined the game)", re.I)
_LEAVE_RE = re.compile(r"([A-Za-z0-9_]{1,16})\s+(?:left the game|left the server|disconnected|lost connection:|has disconnected)", re.I)
_ADDR_RE = re.compile(r"\[/?(?P<addr>(?:\d{1,3}\.){3}\d{1,3}:\d{1,5})\]")


def _extract_addr(line: str):
    m = _ADDR_RE.search(line)
    return m.group("addr") if m else None


def _player_event(line: str):
    """Detect join/leave events from Minecraft output.

    Returns (kind, name, addr) or None. Compatible with both modern and
    legacy formats (e.g. Minecraft 1.7.10: '<Steve>[/127.0.0.1:45902] logged in').
    """
    m = _JOIN_LOGGED_RE.search(line)
    if m:
        return ("join", m.group(1), _extract_addr(line))
    m = _JOIN_UUID_RE.search(line)
    if m:
        return ("join", m.group(1), None)
    m = _JOIN_BARE_RE.search(line.strip())
    if m:
        return ("join", m.group(1), None)
    m = _LEAVE_RE.search(line)
    if m:
        return ("leave", m.group(1), None)
    return None


def _show_player_panel(name, addr, kind):
    title = t("player.leave_title") if kind == "leave" else t("player.join_title")
    border = "red" if kind == "leave" else "blue"
    name_color = "bold red" if kind == "leave" else "bold"
    lines = [f"  👤 {t('player.user')}: [{name_color}]{name}[/{name_color}]"]
    if addr:
        lines.append(f"  📡 {t('player.address')}: [bold cyan]{addr}[/bold cyan]")
    msg = (t("player.left").format(name=name) if kind == "leave"
           else t("player.joined").format(name=name))
    lines.append("")
    lines.append(f"  ✓ [bold]{msg}[/bold]")
    console.print()
    console.print(Panel(
        "\n".join(lines),
        border_style=border,
        title=f"[bold {border}]{'🔴' if kind == 'leave' else '🔵'} {title}[/bold {border}]",
        padding=(1, 2),
    ))
    console.print()


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
    online_shown = False
    online_players = set()

    def reader():
        nonlocal online_shown
        for line in proc.stdout:
            if stop_flag.is_set():
                break
            if not line.strip():
                continue
            try:
                style = _style_line(line)
                # Server output is untrusted text: never let Rich interpret it as markup.
                console.print(f"{_timestamp()} {line.rstrip()}", style=style, highlight=False, markup=False)
                if not online_shown and _DONE_RE.search(line):
                    online_shown = True
                    _show_online_panel(name)
                ev = _player_event(line)
                if ev:
                    _handle_player_event(ev, online_players)
            except Exception as e:
                console.print(f"[bold yellow]⚠ {t('console.line_error')}: {e}[/bold yellow]")

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
            cmd = console.input(f"[bold][{t('console.command_prompt')}][/bold] > ").strip()
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


def _handle_player_event(ev, online_players):
    kind, name, addr = ev
    if kind == "join":
        if name in online_players:
            return  # avoid duplicate panels
        online_players.add(name)
        _show_player_panel(name, addr, "join")
    else:
        if name not in online_players:
            return  # only notify for players we saw join this session
        online_players.discard(name)
        _show_player_panel(name, None, "leave")