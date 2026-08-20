import os

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core import config, server_manager
from core.i18n import t
from ui import menus
from ui.console_view import run_console
from managers import world_manager
from ui.manager_menus import (
    settings_menu, backup_menu, monitor, connection, file_manager,
)

console = Console()


def status_label(name):
    if server_manager.get_process(name):
        return f"[bold green]● {t('status.running')}[/bold green]"
    if config.get_state(name).get("state") == "error":
        return f"[bold red]✗ {t('status.error')}[/bold red]"
    return f"[dim]○ {t('status.stopped')}[/dim]"


def dashboard(name):
    meta = config.load_server_meta(name)
    while True:
        console.clear()
        header = Table(show_header=False, border_style="cyan", box=None, padding=(0, 2))
        header.add_row(t("dash.server"), f"[bold]{meta.get('name', name)}[/bold]")
        header.add_row(t("dash.minecraft"), meta.get("version", "?"))
        header.add_row(t("dash.type"), f"[cyan]{meta.get('type', '?').title()}[/cyan]")
        header.add_row(t("dash.ram"), f"{meta.get('ram_mb', '?')} MB")
        header.add_row(t("dash.players"), "0 (console)")
        header.add_row(t("dash.status"), status_label(name))

        opts = []
        if server_manager.get_process(name):
            opts.append(("1", f"■ {t('menu.stop')}"))
            opts.append(("2", f"↻ {t('menu.restart')}"))
            opts.append(("3", f"⌥ {t('console.title')}"))
        else:
            opts.append(("1", f"▶ {t('menu.start')}"))
            opts.append(("2", f"[dim]↻ {t('menu.restart')}[/dim]"))
            opts.append(("3", f"[dim]⌥ {t('console.title')}[/dim]"))

        srv_type = meta.get("type", "?")
        opts.append(("4", f"🌍 {t('menu.world')}"))
        opts.append(("5", f"🧩 {t('menu.mods')}"))
        opts.append(("6", f"🔌 {t('menu.plugins')}"))
        opts.append(("7", f"⚙ {t('menu.settings')}"))
        opts.append(("8", f"💾 {t('menu.backups')}"))
        opts.append(("9", f"📊 {t('menu.monitor')}"))
        opts.append(("10", f"🌐 {t('menu.connection')}"))
        opts.append(("11", f"📁 {t('menu.filemgr')}"))
        opts.append(("12", t("change_lang")))
        opts.append(("b", f"← {t('menu.back')}"))
        opts.append(("q", t("menu.quit")))

        console.print(Panel(header, border_style="bright_cyan",
                            title=f"[bold]MD SERVER — {name}[/bold]", padding=(0, 1)))
        choice = menus.ask(t("menu.main_title"), opts)

        if choice == "1":
            if server_manager.get_process(name):
                server_manager.stop_server(name)
                menus.success(t("stop.done"))
            else:
                menus.info(t("start.starting"))
                if server_manager.start_server(name):
                    run_console(name)
                else:
                    menus.error("Failed to start (server.jar missing / RAM too low?)")
        elif choice == "2":
            if not server_manager.get_process(name):
                menus.warning(t("console.not_running"))
                continue
            menus.info(t("restart.restarting"))
            server_manager.restart_server(name)
            run_console(name)
        elif choice == "3":
            if not server_manager.get_process(name):
                menus.warning(t("console.not_running"))
                continue
            run_console(name)
        elif choice == "4":
            world_menu(name)
        elif choice == "5":
            from managers import mod_manager
            mod_menu(name, mod_manager)
        elif choice == "6":
            from managers import plugin_manager
            plugin_menu(name, srv_type, plugin_manager)
        elif choice == "7":
            settings_menu(name)
        elif choice == "8":
            backup_menu(name)
        elif choice == "9":
            monitor(name, meta)
        elif choice == "10":
            connection(name, meta)
        elif choice == "11":
            file_manager(name)
        elif choice == "12":
            change_language()
        elif choice == "b":
            return
        elif choice == "q":
            console.print(f"[bold cyan]{t('exit.bye')}[/bold cyan]")
            raise SystemExit(0)


def world_menu(name):
    while True:
        opts = [
            ("1", t("world.create")),
            ("2", t("world.import")),
            ("3", t("world.delete")),
            ("4", t("world.backup")),
            ("5", t("world.restore")),
            ("6", t("world.active")),
            ("b", f"← {t('menu.back')}"),
        ]
        choice = menus.ask(f"🌍 {t('world.title')}", opts)
        if choice == "1":
            w = menus.input_text(t("world.empty_world"), default="world")
            safe = config.safe_name(w)
            world_manager.create_world(name, safe)
            world_manager.set_active_world(name, safe)
            menus.success(f"{t('world.created')}: {safe}")
        elif choice == "2":
            menus.info(t("world.import_hint"))
            menus.info(f"[bold]{t('world.import_folder')}:[/bold] {config.IMPORT_WORLDS}")
            menus.info(t("world.import_search"))
            imported = world_manager.import_from_folder(name)
            if not imported:
                menus.warning(t("world.import_none"))
                menus.info(config.IMPORT_WORLDS)
            else:
                for w in imported:
                    world_manager.set_active_world(name, w)
                    menus.success(f"{t('world.imported')}: {w}")
        elif choice == "3":
            worlds = world_manager.list_worlds(name) or [world_manager.active_world(name)]
            if not worlds:
                menus.info(t("world.none"))
                continue
            w = menus.ask(t("world.delete"), [(x, x) for x in worlds] + [("b", t("common.cancel"))])
            if w == "b":
                continue
            if menus.confirm(f"{t('world.deleted_confirm')} [bold]{w}[/bold]"):
                if world_manager.delete_world(name, w):
                    menus.success(t("world.deleted"))
        elif choice == "4":
            worlds = world_manager.list_worlds(name)
            if not worlds:
                menus.info(t("world.none"))
                continue
            w = menus.ask(t("world.backup"), [(x, x) for x in worlds] + [("b", t("common.cancel"))])
            if w == "b":
                continue
            arc = world_manager.backup_world(name, w, config.BACKUPS_DIR)
            menus.success(f"{t('backup.created')}: {os.path.basename(arc)}")
        elif choice == "5":
            src_dir = os.path.join(config.BACKUPS_DIR, name, "worlds")
            if not os.path.isdir(src_dir):
                menus.warning(t("backup.none"))
                continue
            arcs = sorted(f for f in os.listdir(src_dir) if f.endswith(".tar.gz"))
            if not arcs:
                menus.warning(t("backup.none"))
                continue
            arc = menus.ask(t("world.restore"), [(a, a) for a in arcs] + [("b", t("common.cancel"))])
            if arc == "b":
                continue
            target = config.safe_name(arc.split("_")[0])
            if menus.confirm(f"{t('world.restore')}: {arc}"):
                if world_manager.restore_world(name, target, os.path.join(src_dir, arc)):
                    menus.success(t("backup.restored"))
        elif choice == "6":
            worlds = world_manager.list_worlds(name)
            if not worlds:
                worlds = [d for d in os.listdir(config.server_dir(name))
                          if os.path.isdir(os.path.join(config.server_dir(name), d))]
            if not worlds:
                menus.info(t("world.none"))
                continue
            w = menus.ask(t("world.active"), [(x, x) for x in worlds] + [("b", t("common.cancel"))])
            if w == "b":
                continue
            world_manager.set_active_world(name, w)
            menus.success(f"{t('world.set_active')} {w}")
            menus.info(t("key.saved"))
        elif choice == "b":
            return


def mod_menu(name, mod_manager):
    srv_type = config.load_server_meta(name).get("type", "?")
    if srv_type == "vanilla":
        menus.info(t("plugin.unsupported").replace("plugin", "mod"))
        return
    while True:
        opts = [
            ("1", t("mod.install")),
            ("2", t("mod.remove")),
            ("3", t("mod.list")),
            ("4", t("mod.open")),
            ("5", t("mod.import")),
            ("b", f"← {t('menu.back')}"),
        ]
        choice = menus.ask(f"🧩 {t('mod.title')}", opts)
        if choice == "1":
            menus.info(t("mod.install_hint"))
            menus.info(mod_manager.mods_dir(name))
        elif choice == "2":
            mods = mod_manager.list_mods(name)
            if not mods:
                menus.info(t("mod.none"))
                continue
            m = menus.ask(t("mod.remove"), [(x, x) for x in mods] + [("b", t("common.cancel"))])
            if m == "b":
                continue
            if mod_manager.remove_mod(name, m):
                menus.success(f"{t('mod.removed')}: {m}")
        elif choice == "3":
            mods = mod_manager.list_mods(name)
            if not mods:
                menus.info(t("mod.none"))
            else:
                from core import version_manager
                meta = config.load_server_meta(name)
                for m in mods:
                    ok, warn = mod_manager.validate_mod(meta.get("version", ""), meta.get("type", ""), m)
                    line = f"  [cyan]{m}[/cyan]"
                    if warn:
                        menus.warning(warn)
                    console.print(line)
        elif choice == "4":
            menus.info(t("mod.path"))
            menus.info(f"[bold cyan]{mod_manager.mods_dir(name)}[/bold cyan]")
        elif choice == "5":
            menus.info(t("mod.install_hint"))
            menus.info(f"[bold]{t('mod.import_folder')}:[/bold] {config.IMPORT_MODS}")
            imported = mod_manager.import_mods(name)
            if not imported:
                menus.warning(t("mod.import_none"))
                menus.info(config.IMPORT_MODS)
            else:
                menus.success(f"{len(imported)} {t('mod.imported')}")
        elif choice == "b":
            return


def plugin_menu(name, srv_type, plugin_manager):
    if not plugin_manager.supports_plugins(name):
        menus.warning(t("plugin.unsupported"))
        return
    while True:
        opts = [
            ("1", t("mod.install")),
            ("2", t("mod.remove")),
            ("3", t("mod.list")),
            ("4", t("mod.open")),
            ("5", t("mod.import")),
            ("b", f"← {t('menu.back')}"),
        ]
        choice = menus.ask(f"🔌 {t('plugin.title')}", opts)
        if choice in ("1", "4"):
            menus.info(plugin_manager.plugins_dir(name))
        elif choice == "2":
            pl = plugin_manager.list_plugins(name)
            if not pl:
                menus.info(t("mod.none"))
                continue
            p = menus.ask(t("mod.remove"), [(x, x) for x in pl] + [("b", t("common.cancel"))])
            if p != "b" and menus.confirm(t("mod.remove")):
                os.remove(os.path.join(plugin_manager.plugins_dir(name), p))
                menus.success(t("mod.removed"))
        elif choice == "3":
            pl = plugin_manager.list_plugins(name)
            for p in pl:
                console.print(f"  [cyan]{p}[/cyan]")
            if not pl:
                menus.info(t("mod.none"))
        elif choice == "5":
            menus.info(t("mod.install_hint"))
            menus.info(plugin_manager.plugins_dir(name))
        elif choice == "b":
            return


def change_language():
    from core import i18n
    opts = [("es", t("lang_es")), ("en", t("lang_en"))]
    lang = menus.ask(t("lang_title"), opts)
    i18n.load(lang)
    menus.success(t("lang.changed"))