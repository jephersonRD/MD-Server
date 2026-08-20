import threading
import time

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from core.i18n import t
from core import downloader

console = Console()


def human(n: float) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    v = float(n)
    for u in units:
        if v < 1024 or u == units[-1]:
            return f"{v:.1f} {u}" if u != "B" else f"{int(v)} B"
        v /= 1024


def format_eta(seconds: float) -> str:
    if seconds is None or seconds < 0 or seconds != seconds:
        return "--:--"
    s = int(seconds)
    return f"{s // 60:02d}:{s % 60:02d}"


class DownloadPanel:
    """Renders a live professional download panel for one or many files."""

    def __init__(self, states: list):
        self.states = states
        self.live = None
        self._stop = threading.Event()

    def _render(self):
        panels = []
        for ds in self.states:
            lines = []
            pct = 0.0
            if ds.expected_size > 0:
                pct = min(ds.received / ds.expected_size * 100, 100)
            status = {
                "starting": t("download.status") + ": ...",
                "downloading": f"{t('download.status')}: [cyan]Downloading[/cyan]",
                "completed": f"{t('download.status')}: [bold green]✓ Complete[/bold green]",
                "failed": f"{t('download.status')}: [bold red]✗ Failed[/bold red]",
            }.get(ds.status, ds.status)

            if ds.status == "downloading":
                bar_widget = make_bar(ds, pct)
                lines.append(bar_widget)
                if ds.expected_size:
                    eta = format_eta((ds.expected_size - ds.received) / ds.speed) if ds.speed > 0 else "--:--"
                    lines.append(f"  {human(ds.received)} / {human(ds.expected_size)}   [cyan]{human(ds.speed)}/s[/cyan]   {t('download.eta')}: {eta}")
            elif ds.status == "completed":
                bar_widget = make_bar(ds, 100)
                lines.append(bar_widget)
                lines.append(f"  {human(ds.received)}  —  [green]{t('common.done')}[/green]")
            elif ds.status == "failed":
                lines.append(f"[bold red]✗ {ds.error}[/bold red]")
            elif ds.status == "starting":
                lines.append("[yellow]…[/yellow]")
            panels.append(Panel(Group(*([f"[bold cyan]{ds.label}[/bold cyan]"] + lines + [""])),
                                border_style="cyan", padding=(0, 1), expand=False))
        title = f"⬇ {t('download.progress')}"
        return Panel(Group(*panels), border_style="bright_cyan", title=title)


def make_bar(ds, pct: float) -> Text:
    filled = int(round(pct / 100 * 26))
    fill = "█" * filled
    rest = "░" * (26 - filled)
    return Text(f"  {fill}{rest} {pct:3.0f}%", style="cyan")


def run_download_ui(states: list, callback=None) -> dict:
    """Runs a live download panel for the given states until all are done/failed."""
    panel = DownloadPanel(states)
    with Live(panel._render(), console=console, refresh_per_second=6, transient=True) as live:
        panel.live = live
        last = time.time()
        while any(s.status in ("starting", "downloading") for s in states):
            if callback:
                callback()
            time.sleep(0.02)
            now = time.time()
            if now - last >= 0.25:
                live.update(panel._render())
                last = now
            if all(s.done or s.status == "failed" for s in states):
                if all(s.status == "failed" for s in states):
                    break
        live.update(panel._render())
        time.sleep(0.4)
    return {s.label: s for s in states}