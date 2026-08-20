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
            opts.append((f"■ {t('menu.stop')}",))
            opts.append((f"↻ {t('menu.restart')}",))
            opts.append((f"⌥ {t('console.title')}",))
        else:
            opts.append((f"▶ {t('menu.start')}",))
            opts.append((f"[dim]↻ {t('menu.restart')}[/dim]",))
            opts.append((f"[dim]⌥ {t('console.title')}[/dim]",))

        srv_type = meta.get("type", "?")
        opts.append((f"🌍 {t('menu.world')}",))
        opts.append((f"🧩 {t('menu.mods')}",))
        opts.append((f"🔌 {t('menu.plugins')}",))
        opts.append((f"⚙ {t('menu.settings')}",))
        opts.append((f"💾 {t('menu.backups')}",))
        opts.append((f"📊 {t('menu.monitor')}",))
        opts.append((f"🌐 {t('menu.connection')}",))
        opts.append((f"📁 {t('menu.filemgr')}",))
        opts.append((t("change_lang"),))
        opts.append((f"← {t('menu.back')}",))
        opts.append((t("menu.quit"),))
        N_ACTIONS = 12

        console.print(Panel(header, border_style="bright_cyan",
                            title=f"[bold]MD SERVER — {name}[/bold]", padding=(0, 1)))
        choice = menus.ask(t("menu.main_title"), opts)
        n = int(choice)
        if n == N_ACTIONS + 1:
            return
        if n == N_ACTIONS + 2:
            console.print(f"[bold cyan]{t('exit.bye')}[/bold cyan]")
            raise SystemExit(0)

        if n == 1:
            if server_manager.get_process(name):
                server_manager.stop_server(name)
                menus.success(t("stop.done"))
            else:
                menus.info(t("start.starting"))
                if server_manager.start_server(name):
                    run_console(name)
                else:
                    menus.error("Failed to start (server.jar missing / RAM too low?)")
        elif n == 2:
            if not server_manager.get_process(name):
                menus.warning(t("console.not_running"))
                continue
            menus.info(t("restart.restarting"))
            server_manager.restart_server(name)
            run_console(name)
        elif n == 3:
            if not server_manager.get_process(name):
                menus.warning(t("console.not_running"))
                continue
            run_console(name)
        elif n == 4:
            world_menu(name)
        elif n == 5:
            from managers import mod_manager
            mod_menu(name, mod_manager)
        elif n == 6:
            from managers import plugin_manager
            plugin_menu(name, srv_type, plugin_manager)
        elif n == 7:
            settings_menu(name)
        elif n == 8:
            backup_menu(name)
        elif n == 9:
            monitor(name, meta)
        elif n == 10:
            connection(name, meta)
        elif n == 11:
            file_manager(name)
        elif n == 12:
            change_language()


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
            opts = [(x,) for x in worlds] + [(t("common.cancel"),)]
            n = int(menus.ask(t("world.delete"), opts))
            if n == len(worlds) + 1:
                continue
            w = worlds[n - 1]
            if menus.confirm(f"{t('world.deleted_confirm')} [bold]{w}[/bold]"):
                if world_manager.delete_world(name, w):
                    menus.success(t("world.deleted"))
        elif choice == "4":
            worlds = world_manager.list_worlds(name)
            if not worlds:
                menus.info(t("world.none"))
                continue
            opts = [(x,) for x in worlds] + [(t("common.cancel"),)]
            n = int(menus.ask(t("world.backup"), opts))
            if n == len(worlds) + 1:
                continue
            w = worlds[n - 1]
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
            opts = [(a,) for a in arcs] + [(t("common.cancel"),)]
            n = int(menus.ask(t("world.restore"), opts))
            if n == len(arcs) + 1:
                continue
            arc = arcs[n - 1]
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
            opts = [(x,) for x in worlds] + [(t("common.cancel"),)]
            n = int(menus.ask(t("world.active"), opts))
            if n == len(worlds) + 1:
                continue
            w = worlds[n - 1]
            world_manager.set_active_world(name, w)
            menus.success(f"{t('world.set_active')} {w}")
            menus.info(t("key.saved"))
        elif choice == "7":
            return


def mod_menu(name, mod_manager):
    srv_type = config.load_server_meta(name).get("type", "?")
    if srv_type == "vanilla":
        menus.info(t("plugin.unsupported").replace("plugin", "mod"))
        return
    while True:
        opts = [
            (t("mod.install"),),
            (t("mod.remove"),),
            (t("mod.list"),),
            (t("mod.open"),),
            (t("mod.import"),),
            (f"← {t('menu.back')}",),
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
            opts = [(x,) for x in mods] + [(t("common.cancel"),)]
            n = int(menus.ask(t("mod.remove"), opts))
            if n == len(mods) + 1:
                continue
            m = mods[n - 1]
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
        elif choice == "6":
            return


def plugin_menu(name, srv_type, plugin_manager):
    if not plugin_manager.supports_plugins(name):
        menus.warning(t("plugin.unsupported"))
        return
    while True:
        opts = [
            (t("mod.install"),),
            (t("mod.remove"),),
            (t("mod.list"),),
            (t("mod.open"),),
            (t("mod.import"),),
            (f"← {t('menu.back')}",),
        ]
        choice = menus.ask(f"🔌 {t('plugin.title')}", opts)
        if choice in ("1", "4"):
            menus.info(plugin_manager.plugins_dir(name))
        elif choice == "2":
            pl = plugin_manager.list_plugins(name)
            if not pl:
                menus.info(t("mod.none"))
                continue
            opts = [(x,) for x in pl] + [(t("common.cancel"),)]
            n = int(menus.ask(t("mod.remove"), opts))
            if n == len(pl) + 1:
                continue
            p = pl[n - 1]
            if menus.confirm(t("mod.remove")):
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
        elif choice == "6":
            return


def change_language():
    from core import i18n
    opts = [(f"🇪🇸  {t('lang_es')}",), (f"🇺🇸  {t('lang_en')}",)]
    lang = "es" if menus.ask(t("lang_title"), opts) == "1" else "en"
    i18n.load(lang)
    menus.success(t("lang.changed"))