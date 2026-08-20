#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel

from core import config, device_info, i18n
from ui import banner, menus
from ui.dashboard import dashboard
from ui.progress import human

console = Console()


def choose_language():
    lang = menus.ask(
        i18n.t("lang_title", "Select language / Selecciona el idioma"),
        [("es", i18n.t("lang_es", "Español") + "  🇪🇸"),
         ("en", i18n.t("lang_en", "English") + "  🇺🇸")],
    )
    i18n.load(lang)


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
        [("no", i18n.t("firstrun.no_existing")),
         ("yes", i18n.t("firstrun.yes_new"))],
    )
    return choice == "yes"


def select_server_or_new():
    servers = config.list_servers()
    while True:
        console.clear()
        banner.show(console)
        if not servers:
            menu_opt = [("n", i18n.t("menu.create_new")),
                        ("l", i18n.t("change_lang")),
                        ("q", i18n.t("menu.quit"))]
        else:
            menu_opt = [("r", f"▶ {i18n.t('firstrun.no_existing')}")]
            for s in servers:
                meta = config.load_server_meta(s)
                st = "●" if _server_running(s) else "○"
                menu_opt.append((s, f"{st} {s}  [dim]{meta.get('version','?')} · {meta.get('type','?').title()}[/dim]"))
            menu_opt.append(("n", f"+ {i18n.t('menu.create_new')}"))
            menu_opt.append(("l", i18n.t("change_lang")))
            menu_opt.append(("q", i18n.t("menu.quit")))
        choice = menus.ask(i18n.t("menu.select_server"), menu_opt)
        if choice in ("q", "quit", "exit"):
            console.print(f"[bold cyan]{i18n.t('exit.bye')}[/bold cyan]")
            return None
        if choice == "n":
            from wizard import run_wizard
            name, meta = run_wizard()
            if name and name in config.list_servers():
                return name
            continue
        if choice == "l":
            choose_language()
            continue
        if choice == "r" and servers:
            # resume most recently modified server
            _resume(servers)
            return None
        if choice in servers:
            return choice


def _server_running(name):
    from core import server_manager
    return server_manager.get_process(name) is not None


def _latest_server(servers):
    import os
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
            # they want a brand-new server
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