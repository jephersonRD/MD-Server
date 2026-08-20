import os
import shutil

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core import config, network_manager, server_manager
from core.i18n import t
from managers import backup_manager
from ui import banner, menus

console = Console()


def _meta(name):
    return config.load_server_meta(name)


def _running(name):
    return server_manager.get_process(name) is not None


def _status_icon(name):
    return "●" if _running(name) else "○"


def my_servers_menu():
    """Lists all created servers and returns the selected server folder, or None."""
    servers = config.list_servers()
    if not servers:
        console.clear()
        banner.show(console)
        menus.info(t("ms.no_servers"))
        console.input("Enter ")
        return None
    while True:
        console.clear()
        banner.show(console)
        opts = []
        for s in servers:
            meta = _meta(s)
            display = meta.get("name") or s
            st = t("status.running") if _running(s) else t("status.stopped")
            desc = f"{t('ms.minecraft').format(version=meta.get('version', '?'), type=(meta.get('type', '?')).title())} · {st}"
            opts.append((f"{_status_icon(s)} {display}", desc))
        opts.append((f"← {t('menu.back')}",))
        choice = menus.ask(t("ms.title"), opts)
        n = int(choice)
        if n == len(servers) + 1:
            return None
        return servers[n - 1]


def server_info(name):
    meta = _meta(name)
    display = meta.get("name") or name
    sdir = config.server_dir(name)
    port = server_manager.read_property(sdir, "server-port", "25565")
    running = _running(name)
    status = f"[bold green]● {t('status.running')}[/bold green]" if running else f"[dim]○ {t('status.stopped')}[/dim]"
    table = Table(show_header=False, border_style="cyan", box=None, expand=False, padding=(0, 2))
    table.add_row(t("info.name"), f"[bold]{display}[/bold]")
    table.add_row(t("info.minecraft"), meta.get("version", "?"))
    table.add_row(t("info.type"), f"[cyan]{meta.get('type', '?').title()}[/cyan]")
    table.add_row(t("info.status"), status)
    table.add_row(t("info.port"), port)
    table.add_row(t("info.folder"), sdir)
    console.print(Panel(table, border_style="cyan", title=f"[bold]{t('info.title')}[/bold]", padding=(0, 1)))
    if running:
        lip = network_manager.local_ip()
        console.print()
        console.print(f"[cyan]{t('info.local')}:[/cyan] [bold]127.0.0.1:{port}[/bold]")
        console.print(f"[cyan]{t('info.lan')}:[/cyan] [bold cyan]{lip}:{port}[/bold cyan]")
        console.print(f"[cyan]{t('info.internet')}:[/cyan] ...")
        with console.status(t("net.get_public") + " ..."):
            pip = network_manager.public_ip(timeout=5)
        if pip:
            console.print(f"[cyan]{t('info.internet')}:[/cyan] [bold]{pip}:{port}[/bold]")
        else:
            menus.info(t("info.tunnel_hint"))
    console.input("Enter ")


def rename_server(name):
    meta = _meta(name)
    display = meta.get("name") or name
    menus.title(t("rename.title"))
    new = menus.input_text(t("rename.prompt"), default=display)
    new = new.strip()
    if not new or new == display:
        return
    meta["name"] = new
    config.save_server_meta(name, meta)
    menus.success(t("rename.done"))
    menus.info(t("rename.display").format(name=new))


def delete_server(name):
    """Deletes a single server after explicit double confirmation. Returns True if deleted."""
    meta = _meta(name)
    display = meta.get("name") or name
    version = meta.get("version", "?")
    srv_type = meta.get("type", "?").title()

    if _running(name):
        menus.warning(t("del.running"))
        choice = menus.ask(t("del.running_q"), [(t("del.stop_and_continue"),), (t("common.cancel"),)])
        if choice == "2":
            menus.success(t("del.cancelled"))
            return False
        menus.info(t("stop.stopping") + " ...")
        server_manager.stop_server(name)

    lines = [
        t("del.intro"),
        "",
        f"  [bold]{t('del.server')}:[/bold] {display}",
        f"  [bold]{t('del.minecraft')}:[/bold] {version}",
        f"  [bold]{t('del.type')}:[/bold] {srv_type}",
        "",
        t("del.deletes"),
        f"  • {t('del.world')}",
        f"  • {t('del.config')}",
        f"  • {t('del.mods')}",
        f"  • {t('del.plugins')}",
        f"  • {t('del.files')}",
        "",
        f"[bold red]⚠ {t('del.irreversible')}[/bold red]",
    ]
    console.print(Panel("\n".join(lines), border_style="red", title=f"[bold]⚠ {t('del.title')}[/bold]", padding=(1, 2)))
    choice = menus.ask(t("del.continue_q"), [(t("del.yes"),), (t("del.cancel"),)])
    if choice == "2":
        menus.success(t("del.cancelled"))
        return False

    typed = menus.input_text(t("del.type_confirm"))
    if typed.strip().upper() != "ELIMINAR":
        menus.success(t("del.cancelled"))
        return False

    from ui.manager_menus import _stop_auto
    _stop_auto(name)

    sdir = config.server_dir(name)
    shutil.rmtree(sdir, ignore_errors=True)
    state_file = os.path.join(config.STATE_DIR, f"{config.safe_name(name)}.json")
    if os.path.exists(state_file):
        os.remove(state_file)
    broot = backup_manager.backups_root(name)
    if os.path.isdir(broot):
        shutil.rmtree(broot, ignore_errors=True)

    menus.success(t("del.done"))
    menus.info(t("del.done_desc").format(name=display))
    return True