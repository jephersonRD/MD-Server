#!/usr/bin/env python3
import os
import sys

__version__ = "1.1.0"
__repo__ = "jephersonRD/MD-Server"
__branch__ = "main"

APP_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, APP_DIR)

from rich.console import Console
from rich.panel import Panel

from core import config, device_info, i18n
from ui import banner, menus
from ui.dashboard import dashboard
from ui.progress import human

console = Console()


def auto_update(argv=None, verbose=False):
    """Check for updates on GitHub and apply them before starting."""
    argv = argv if argv is not None else sys.argv[1:]
    if "--no-update" in argv or os.environ.get("MD_SERVER_NO_UPDATE") == "1":
        return
    if os.environ.get("MD_SERVER_UPDATED") == "1":
        return
    import subprocess
    if not os.path.isdir(os.path.join(APP_DIR, ".git")):
        return  # not a git install (e.g. tarball) — nothing to update
    try:
        subprocess.run(
            ["git", "-C", APP_DIR, "fetch", "--depth", "1", "origin", __branch__],
            capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return  # offline or git error — run anyway
    try:
        head = subprocess.run(["git", "-C", APP_DIR, "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=10).stdout.strip()
        remote = subprocess.run(["git", "-C", APP_DIR, "rev-parse", "origin/" + __branch__],
                                capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return
    if not remote or remote == head:
        if verbose:
            print(f"\033[0;32m✓ MD Server está actualizado | up to date (v{__version__})\033[0m")
        return  # already up to date
    try:
        subprocess.run(["git", "-C", APP_DIR, "reset", "--hard", "origin/" + __branch__],
                       capture_output=True, text=True, timeout=60)
        subprocess.run(["git", "-C", APP_DIR, "clean", "-fd"],
                       capture_output=True, text=True, timeout=60)
    except Exception:
        pass
    print("\n\033[1;36m🔄 MD Server updated to the latest version.\033[0m\n")
    os.environ["MD_SERVER_UPDATED"] = "1"
    try:
        os.execv(sys.executable, [sys.executable, os.path.realpath(__file__)] + argv)
    except Exception:
        pass


def choose_language():
    lang = menus.ask(
        i18n.t("lang_title", "Select language / Selecciona el idioma"),
        [("🇪🇸  Español",), ("🇺🇸  English",)],
    )
    i18n.load("es" if lang == "1" else "en")


def show_device_analysis():
    menus.title(i18n.t("device_title"))
    with console.status(i18n.t("common.loading") + " ..."):
        dev = device_info.collect()
    internet = i18n.t("device.connected") if dev["internet"] else i18n.t("device.disconnected")
    status = "[green]✓" if dev["internet"] else "[red]✗"
    java = dev["java"] if dev["java"] != "not_installed" else i18n.t("device.not_installed")
    pairs = [
        (i18n.t("device.ram_total"), f"{human(dev['ram_total'] * 1048576)}"),
        (i18n.t("device.ram_available"), f"{human(dev['ram_available'] * 1048576)}"),
        (i18n.t("device.cpu_cores"), f"{dev['cpu_cores']} cores"),
        (i18n.t("device.cpu_arch"), dev["cpu_arch"]),
        (i18n.t("device.android"), dev["android"]),
        (i18n.t("device.termux"), dev["termux"]),
        (i18n.t("device.storage_total"), human(dev["storage_total"])),
        (i18n.t("device.storage_free"), human(dev["storage_free"])),
        (i18n.t("device.java"), java),
        (i18n.t("device.python"), dev["python"]),
        (i18n.t("device.internet"), f"{internet}{status}[/]"),
    ]
    lines = "".join(f"  [cyan]{k:<14}[/cyan] {v}\n" for k, v in pairs)
    console.print(Panel(lines.rstrip("\n"), border_style="cyan", title="[bold]" + i18n.t("device_title") + "[/bold]", padding=(0, 1)))
    console.print()


def welcome():
    console.print(Panel(
        f"[bold]{i18n.t('welcome_fst')}[/bold]\n\n{i18n.t('welcome_1st')}\n\n[dim]{i18n.t('welcome_2nd')}[/dim]",
        border_style="cyan", padding=(1, 2),
    ))
    console.print()


def first_run_question():
    """Asks returning users whether to resume an existing server or start fresh."""
    console.print(Panel(f"[bold]{i18n.t('firstrun.title')}[/bold]\n\n{i18n.t('firstrun.question')}",
                        border_style="magenta", padding=(1, 2)))
    choice = menus.ask(
        i18n.t("firstrun.title"),
        [(i18n.t("firstrun.no_existing"),),
         (i18n.t("firstrun.yes_new"),)],
    )
    return choice == "2"


def select_server_or_new():
    servers = config.list_servers()
    while True:
        console.clear()
        banner.show(console)
        menu_opt = []
        idx_resume = None
        if servers:
            menu_opt.append((f"▶ {i18n.t('firstrun.no_existing')} ({servers[0]})",))
            idx_resume = 1
            for s in servers:
                meta = config.load_server_meta(s)
                st = "●" if _server_running(s) else "○"
                menu_opt.append((f"{st} {s}  [dim]{meta.get('version','?')} · {meta.get('type','?').title()}[/dim]",))
        menu_opt.append((f"✚ {i18n.t('menu.create_new')}",))
        idx_new = len(menu_opt)
        menu_opt.append((i18n.t("change_lang"),))
        idx_lang = len(menu_opt)
        menu_opt.append((i18n.t("menu.quit"),))
        idx_quit = len(menu_opt)

        choice = menus.ask(i18n.t("menu.select_server"), menu_opt)
        n = int(choice)
        if n == idx_quit:
            console.print(f"[bold cyan]{i18n.t('exit.bye')}[/bold cyan]")
            return None
        if n == idx_lang:
            choose_language()
            continue
        if n == idx_new:
            from wizard import run_wizard
            name, meta = run_wizard()
            if name and name in config.list_servers():
                return name
            continue
        if idx_resume and n == idx_resume:
            _resume(servers)
            return None
        if servers and 2 <= n < idx_new:
            return servers[n - 2]


def _server_running(name):
    from core import server_manager
    return server_manager.get_process(name) is not None


def _latest_server(servers):
    return max(servers, key=lambda s: os.path.getmtime(os.path.join(config.SERVERS_DIR, s, "mdserver.json")) or 0)


def _resume(servers):
    target = _latest_server(servers)
    print()
    console.print(f"[cyan]◈ [/cyan][bold]{target}[/bold]")
    from core import server_manager
    from ui.console_view import run_console
    if not server_manager.start_server(target):
        menus.error("Could not start the server.")
    else:
        run_console(target)


def main():
    argv = sys.argv[1:]
    if "--version" in argv or "-v" in argv:
        print(f"MD Server v{__version__}")
        sys.exit(0)
    if "--check-update" in argv:
        auto_update(argv, verbose=True)
        sys.exit(0)

    auto_update(argv)

    config.ensure_dirs()
    cfg = config.get_config()

    try:
        console.clear()
        banner.show(console)
        if not cfg.get("language"):
            choose_language()
        else:
            i18n.load(cfg.get("language", "es"))

        first_run = not cfg.get("first_run_done")
        has_servers = bool(config.list_servers())

        if first_run:
            welcome()
            show_device_analysis()
            config.set_config("first_run_done", True)
            console.print("[dim]Press Enter to continue ...[/dim]", end="")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                pass

        # First-use question per requirement: returning users may only want to boot an old server
        if has_servers and first_run_question():
            from wizard import run_wizard
            name, _ = run_wizard()
            if name in config.list_servers():
                console.clear()
                banner.show(console)
                dashboard(name)
            return

        if has_servers:
            target = select_server_or_new()
            if not target:
                return
            console.clear()
            banner.show(console)
            dashboard(target)
        else:
            # No servers: straight into the create wizard
            from wizard import run_wizard
            name, _ = run_wizard()
            if name in config.list_servers():
                console.clear()
                banner.show(console)
                dashboard(name)
    except KeyboardInterrupt:
        console.print(f"\n[bold cyan]{i18n.t('exit.bye')}[/bold cyan]")
        sys.exit(0)


if __name__ == "__main__":
    main()