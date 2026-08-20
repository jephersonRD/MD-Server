#!/usr/bin/env python3
import os
import sys

__version__ = "1.1.4-beta"
__repo__ = "jephersonRD/MD-Server"
__branch__ = "main"

APP_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, APP_DIR)

from rich.console import Console
from rich.panel import Panel

from core import config, device_info, i18n
from core.i18n import t
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
            capture_output=True, text=True, timeout=10,
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
        sys.stdout.flush()
        sys.stderr.flush()
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


def main_menu():
    while True:
        console.clear()
        banner.show(console)
        choice = menus.ask(
            t("main.title"),
            [(f"✚ {t('main.create')}",),
             (f"🖥 {t('main.my_servers')}",),
             (f"⚙ {t('main.settings')}",),
             (t("menu.quit"),)],
        )
        n = int(choice)
        if n == 4:
            console.print(f"[bold cyan]{t('exit.bye')}[/bold cyan]")
            return
        if n == 3:
            global_settings_menu()
            continue
        if n == 2:
            from ui.my_servers import my_servers_menu
            while True:
                target = my_servers_menu()
                if not target:
                    break
                console.clear()
                banner.show(console)
                dashboard(target)
            continue
        if n == 1:
            from wizard import run_wizard
            name, _ = run_wizard()
            if name and name in config.list_servers():
                console.clear()
                banner.show(console)
                dashboard(name)
            continue


def global_settings_menu():
    while True:
        console.clear()
        banner.show(console)
        choice = menus.ask(
            t("main.settings"),
            [(f"🌐 {t('change_lang')}",),
             (f"🖥 {t('device_title')}",),
             (f"🔄 {t('main.check_updates')}",),
             (f"← {t('menu.back')}",)],
        )
        n = int(choice)
        if n == 1:
            choose_language()
        elif n == 2:
            show_device_analysis()
            console.input("Enter ")
        elif n == 3:
            auto_update(["--check-update"], verbose=True)
            console.input("Enter ")
        else:
            return


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

        if first_run:
            welcome()
            show_device_analysis()
            config.set_config("first_run_done", True)
            console.print("[dim]Press Enter to continue ...[/dim]", end="")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                pass

        main_menu()
    except KeyboardInterrupt:
        console.print(f"\n[bold cyan]{i18n.t('exit.bye')}[/bold cyan]")
        sys.exit(0)


if __name__ == "__main__":
    main()