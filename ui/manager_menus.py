import os
import threading
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core import config, device_info, network_manager, server_manager
from core.i18n import t
from managers import backup_manager
from ui import menus
from ui.progress import human

console = Console()
_auto_schedulers = {}


def process_stats(name):
    pid = server_manager.process_pid(name)
    if not pid:
        return None
    try:
        with open(f"/proc/{pid}/stat", "r") as f:
            parts = f.read().split()
            utime = int(parts[13]) + int(parts[14]) + int(parts[15]) + int(parts[16])
        with open(f"/proc/{pid}/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS"):
                    rss_kb = int(line.split()[1])
                    break
        jiffy = os.sysconf("SC_CLK_TCK")
        cpus = device_info.cpu_cores()
        utime_prev = getattr(process_stats, "_prev_utime", (pid, utime, time.time())) if False else None
        return {"rss_mb": rss_kb / 1024, "cpu_jiffies": utime, "jiffy": jiffy, "cpus": cpus}
    except Exception:
        return None


def _read_stat():
    global _stat_last
    if not hasattr(_read_stat, "last"):
        _read_stat.last = {}
    out = {}
    try:
        for name in config.list_servers():
            pid = server_manager.process_pid(name)
            if not pid or not os.path.exists(f"/proc/{pid}"):
                continue
            with open(f"/proc/{pid}/stat", "r") as f:
                parts = f.read().split()
            utime = int(parts[13]) + int(parts[14]) + int(parts[15]) + int(parts[16])
            out[name] = (pid, utime, time.time())
    except Exception:
        pass
    return out


def cpu_usage(name, interval=1.0):
    global _last_stats
    if not hasattr(cpu_usage, "last"):
        cpu_usage.last = {}
    now_stat = {}
    pid = server_manager.process_pid(name)
    if not pid or not os.path.exists(f"/proc/{pid}"):
        return 0.0
    with open(f"/proc/{pid}/stat", "r") as f:
        parts = f.read().split()
    utime = int(parts[13]) + int(parts[14]) + int(parts[15]) + int(parts[16])
    ts = time.time()
    prev = cpu_usage.last.get(name)
    cpu_usage.last[name] = (pid, utime, ts)
    if not prev or prev[0] != pid:
        return 0.0
    dt = ts - prev[2]
    if dt <= 0:
        return 0.0
    jiffy = os.sysconf("SC_CLK_TCK")
    cpus = device_info.cpu_cores() or 1
    pct = (utime - prev[1]) / jiffy / dt / cpus * 100
    return max(0.0, min(100.0, pct))


def rss_mb(name):
    pid = server_manager.process_pid(name)
    if not pid or not os.path.exists(f"/proc/{pid}/status"):
        return 0.0
    try:
        for line in open(f"/proc/{pid}/status"):
            if line.startswith("VmRSS"):
                return int(line.split()[1]) / 1024
    except Exception:
        pass
    return 0.0


def monitor(name, meta):
    menus.title(t("monitor.title"), border="green")
    if server_manager.get_process(name):
        p1 = _read_stat()
        time.sleep(1.0)
        p2 = _read_stat()
        cpu = cpu_usage(name)
        ram = rss_mb(name)
        uptime = server_manager.process_uptime(name)
        st = device_info.storage_info(config.server_dir(name))
        table = Table(show_header=False, border_style="green", box=None, expand=False, padding=(0, 2))
        table.add_row(t("monitor.cpu"), f"[cyan]{cpu:.1f}%[/cyan]")
        table.add_row(t("monitor.ram"), f"[cyan]{ram:.0f} MB[/cyan] / {meta.get('ram_mb', '?')} MB")
        table.add_row(t("monitor.tps"), "[dim]ideal ~20 — see console[/dim]")
        table.add_row(t("monitor.players"), "[dim]see console[/dim]")
        table.add_row(t("monitor.uptime"), f"{int(uptime // 3600):02d}:{int(uptime // 60 % 60):02d}:{int(uptime % 60):02d}")
        table.add_row(t("monitor.storage"), f"{human(st[2])} free / {human(st[0])}")
        console.print(Panel(table, border_style="green", title=f"[bold]● {t('monitor.active')}[/bold]", padding=(0, 1)))
    else:
        console.print(Panel(f"[dim]{t('monitor.stopped')}[/dim]", border_style="yellow", padding=(0, 1)))
    console.input("Enter ")


def connection(name, meta):
    port = server_manager.read_property(config.server_dir(name), "server-port", "25565")
    lip = network_manager.local_ip()
    menus.title(t("net.title"))
    table = Table(show_header=False, border_style="cyan", box=None, expand=False, padding=(0, 2))
    table.add_row(t("net.local_ip"), f"[bold]{lip}[/bold]")
    table.add_row(t("net.port"), port)
    table.add_row(t("net.lan"), f"[bold cyan]{lip}:{port}[/bold cyan]")
    console.print(Panel(table, border_style="cyan", padding=(0, 1)))
    consoles = [t("net.same_network")]
    if config.get_config().get("language") == "es":
        consoles.insert(1, t("net.same_network_es"))
    for line in consoles:
        console.print(f"[cyan]{line}[/cyan]")
    console.print()
    menus.info(t("net.get_public") + " ...")
    pip = network_manager.public_ip()
    if pip:
        console.print(f"[bold]{t('net.public_ip')}: {pip}[/bold]")
    else:
        menus.warning(t("net.public_error"))
    menus.warning(t("net.nat"))
    menus.info(t("net.nat2"))
    console.print()
    external(name, port)


def external(name, port):
    menus.title(t("net.external"), border="green")
    console.print(f"[dim]{t('net.external_desc')}[/dim]")
    ts = network_manager.tool_installed("tailscale")
    pi = network_manager.tool_installed("playit")
    if ts:
        console.print(f"[green]✓[/green] {t('net.tailscale_installed')}")
        open_steps(t("net.tailscale_how"), t("net.tailscale_steps"))
        return
    if pi:
        console.print(f"[green]✓[/green] {t('net.playit_installed')}")
        open_steps(t("net.playit_how"), t("net.playit_steps"))
        return
    menus.info(t("net.none_installed"))
    choice = menus.ask(t("net.external_desc"), [("pi", t("net.install_playit")), ("ts", t("net.install_tailscale")), ("b", t("common.cancel"))])
    if choice == "b":
        return
    with console.status(f"{t('install.pkg')} ..."):
        r = os.system(f"pkg install -y {'playit-by-playit' if choice == 'pi' else 'tailscale'}")
    if r == 0:
        menus.success("Installed")
        open_steps(t("net.playit_how"), t("net.playit_steps"))


def open_steps(title, steps):
    console.print(f"[bold green]▸ {title}[/bold green]")
    for i, s in enumerate(steps, 1):
        console.print(f"  [cyan]{i}.[/cyan] {s}")


def settings_menu(name):
    sdir = config.server_dir(name)
    menus.title(t("settings.title"))
    if server_manager.get_process(name):
        menus.warning(t("key.saved"))
    p = lambda k, d: server_manager.read_property(sdir, k, d)
    opts = [
        ("1", f"{t('settings.motd')}: [dim]{p('motd', '')}[/dim]"),
        ("2", f"{t('settings.max_players')}: [dim]{p('max-players', '10')}[/dim]"),
        ("3", f"{t('settings.gamemode')}: [dim]{p('gamemode', 'survival')}[/dim]"),
        ("4", f"{t('settings.difficulty')}: [dim]{p('difficulty', 'easy')}[/dim]"),
        ("5", f"{t('settings.pvp')}: [dim]{p('pvp', 'true')}[/dim]"),
        ("6", f"{t('settings.online_mode')}: [dim]{p('online-mode', 'false')}[/dim]"),
        ("7", t("settings.open_properties")),
        ("b", f"← {t('menu.back')}"),
    ]
    choice = menus.ask(t("settings.title"), opts)
    props = {}
    if choice == "1":
        props["motd"] = menus.input_text(t("settings.motd"), default=p("motd", ""))
    elif choice == "2":
        props["max-players"] = menus.input_int(t("settings.max_players"), default=int(p("max-players", "10")), minimum=1, maximum=100)
    elif choice == "3":
        g = menus.ask(t("settings.gamemode"), [("survival", "Survival"), ("creative", "Creative"), ("adventure", "Adventure"), ("spectator", "Spectator")])
        props["gamemode"] = g
    elif choice == "4":
        d = menus.ask(t("settings.difficulty"), [("peaceful", "Peaceful"), ("easy", "Easy"), ("normal", "Normal"), ("hard", "Hard")])
        props["difficulty"] = d
    elif choice == "5":
        props["pvp"] = menus.confirm(t("settings.pvp"), default_yes=p("pvp", "true") == "true")
        props["pvp"] = "true" if props["pvp"] else "false"
    elif choice == "6":
        props["online-mode"] = menus.confirm(t("settings.online_mode"), default_yes=p("online-mode", "false") == "true")
        props["online-mode"] = "true" if props["online-mode"] else "false"
    elif choice == "7":
        print_path = os.path.join(sdir, "server.properties")
        menus.info(print_path)
        return
    elif choice == "b":
        return
    if props:
        server_manager.write_properties(sdir, name, props)
        menus.success(t("settings.saved"))
        menus.info(t("key.saved"))


def backup_menu(name):
    while True:
        opts = [
            ("1", t("backup.create")),
            ("2", t("backup.restore")),
            ("3", t("backup.delete")),
            ("4", t("backup.auto")),
            ("b", f"← {t('menu.back')}"),
        ]
        choice = menus.ask(f"💾 {t('backup.title')}", opts)
        if choice == "1":
            label = menus.input_text(t("backup.name"), default="manual")
            arc = backup_manager.create_backup(name, label=label)
            menus.success(f"{t('backup.created')}: {os.path.basename(arc)}")
        elif choice == "2":
            if server_manager.get_process(name):
                menus.warning(t("stop.stopping") + " ...")
                server_manager.stop_server(name)
            backups = backup_manager.list_backups(name)
            if not backups:
                menus.info(t("backup.none"))
                continue
            items = [(os.path.basename(b), f"{os.path.basename(b)}  [dim]{backup_manager.human_size(b)}[/dim]") for b in backups]
            b = menus.ask(t("backup.restore"), items + [("b", t("common.cancel"))])
            if b == "b":
                continue
            target = next((x for x in backups if os.path.basename(x) == b), None)
            if target and menus.confirm(t("backup.restore_confirm")):
                if backup_manager.restore_backup(name, target):
                    menus.success(t("backup.restored"))
                else:
                    menus.error(t("common.error"))
        elif choice == "3":
            backups = backup_manager.list_backups(name)
            if not backups:
                menus.info(t("backup.none"))
                continue
            items = [(os.path.basename(b), os.path.basename(b)) for b in backups]
            b = menus.ask(t("backup.delete"), items + [("b", t("common.cancel"))])
            if b == "b":
                continue
            target = next((x for x in backups if os.path.basename(x) == b), None)
            if target and menus.confirm(t("backup.delete")):
                backup_manager.delete_backup(target)
                menus.success(t("backup.deleted"))
        elif choice == "4":
            meta = config.load_server_meta(name)
            cur = meta.get("auto_backup_min")
            if cur:
                menus.info(f"{t('backup.auto_enabled')} {cur} min")
                if menus.confirm(t("backup.auto_disabled") + "?", default_yes=False):
                    _stop_auto(name)
                    meta["auto_backup_min"] = None
                    config.save_server_meta(name, meta)
                    menus.success(t("backup.auto_disabled"))
            else:
                mins = menus.input_int(t("backup.auto_prompt"), default=60, minimum=5)
                meta["auto_backup_min"] = mins
                config.save_server_meta(name, meta)
                _start_auto(name, mins)
                menus.success(f"{t('backup.auto_enabled')} {mins} min")
        elif choice == "b":
            return


def _start_auto(name, mins):
    _stop_auto(name)
    s = backup_manager.AutoBackupScheduler(name, mins)
    s.start()
    _auto_schedulers[name] = s


def _stop_auto(name):
    s = _auto_schedulers.pop(name, None)
    if s:
        s.stop()


def file_manager(name):
    menus.title(t("filemgr.title"))
    console.print(f"[bold]MD Server[/bold]: {config.BASE_DIR}")
    console.print(f"[bold]{t('filemgr.server')}[/bold]: {config.server_dir(name)}")
    console.print(f"[bold]{t('filemgr.backups')}[/bold]: {backup_manager.backups_root(name)}")
    console.print()
    menus.info("~ cd " + config.server_dir(name))
    console.input("Enter ")