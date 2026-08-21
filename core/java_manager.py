import json
import os
import subprocess
import time

from core import config, device_info
from core.i18n import t
from rich.console import Console

console = Console()


def java_ok(required: int = 17) -> bool:
    v = device_info.java_version()
    if v == "not_installed":
        return False
    try:
        return int(v) >= required
    except Exception:
        return True


def package_for(required: int) -> str:
    return "openjdk-21" if required >= 17 else "openjdk-17"


def install_java(required: int = 17, auto: bool = False):
    pkg = package_for(required)
    console.print()
    console.print(f"[bold yellow]{t('install.java_missing')} → [cyan]{pkg}[/cyan][/bold yellow]")
    if not auto:
        if not console.input(f"[bold]{t('common.confirm')} ({t('common.yes')}/{t('common.no')}): [/bold]").strip().lower() in ("y", "yes", "s", "si", "sí"):
            return False
    console.print(f"[cyan]{t('install.pkg')} {pkg} ...[/cyan]")
    with console.status(t("status.installing_java")):
        r = subprocess.run(["pkg", "install", "-y", pkg], text=True)
    if r.returncode != 0:
        console.print(f"[bold red][✗] {t('common.error')}: pkg install {pkg}[/bold red]")
        return False
    return device_info.java_version() != "not_installed"


def ensure_java(required: int = 17, auto: bool = False) -> bool:
    if java_ok(required):
        return True
    return install_java(required, auto=auto)