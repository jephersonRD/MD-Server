import os
import time
from pathlib import Path

from rich.console import Console

from core import config, device_info, java_manager, memory_manager, server_manager, version_manager
from core import downloader
from core.i18n import t
from ui import menus, progress

console = Console()


def run_wizard(auto_ram=None):
    """Guided server creation. Returns (server_name, meta)."""
    menus.title(t("wizard.title"))

    srv_type = menus.ask(
        t("wizard.type"),
        [
            ("vanilla", t("wizard.vanilla"), t("wizard.vanilla_desc")),
            ("fabric", t("wizard.fabric"), t("wizard.fabric_desc")),
            ("forge", t("wizard.forge"), t("wizard.forge_desc")),
        ],
    )

    # versions
    console.print(f"[dim]{t('wizard.version_fetching')}[/dim]")
    with console.status(t("wizard.version_fetching")):
        if srv_type == "vanilla":
            versions = version_manager.fetch_vanilla_versions()
        else:
            versions = version_manager.fetch_vanilla_versions()[:30]
    version = menus.ask(t("wizard.version"), [(v, v) for v in versions[:40]], prompt="> ")

    # RAM
    dev = device_info.collect()
    if auto_ram is None:
        auto_ram = memory_manager.recommend_ram(dev["ram_total"], dev["ram_available"])
    ram_mb = None
    if auto_ram > 0:
        choice = menus.ask(
            f"{t('wizard.ram_title')}: [bold cyan]{auto_ram} MB[/bold cyan]",
            [("rec", t("wizard.ram_recommended")), ("manual", t("wizard.ram_manual"))],
        )
        if choice == "rec":
            ram_mb = auto_ram
    if ram_mb is None:
        ram_mb = menus.input_int(t("wizard.ram_prompt"), default=auto_ram or 2048, minimum=1024)
        if memory_manager.is_dangerous(ram_mb, dev["ram_total"], dev["ram_available"]):
            menus.warning(t("wizard.ram_warning"))
        elif memory_manager.is_too_low(ram_mb, version):
            menus.warning(t("wizard.ram_low"))

    name = menus.input_text(t("wizard.server_name"), default="MyServer", validate=lambda s: bool(config.safe_name(s)))
    safe = config.safe_name(name)
    name = safe

    # EULA
    menus.info(t("wizard.eula"))
    if not menus.confirm(t("wizard.eula_agree")):
        menus.error(t("common.cancel"))
        return None, None

    # Java check
    required_java = version_manager.java_21_required(version) and 21 or 17
    if srv_type == "vanilla":
        try:
            req = version_manager.get_vanilla_server_info(version).get("java", required_java)
            required_java = req if isinstance(req, int) else required_java
        except Exception:
            pass
    menus.info(f"Java {required_java}+ required")
    if not java_manager.ensure_java(required_java, auto=True):
        menus.error("Java installation failed")
        return None, None

    # internet check
    if not device_info.internet_available():
        menus.error(t("download.error_internet"))
        return None, None

    # Folders
    sdir = config.server_dir(name)
    if os.path.exists(sdir) and os.listdir(sdir):
        menus.error(f"{t('common.error')}: {t('wizard.server_name')} '{name}' {t('common.name')} already exists")
        return None, None
    Path(sdir).mkdir(parents=True, exist_ok=True)
    server_manager.create_folder_structure(sdir, srv_type)
    server_manager.write_eula(sdir, True)
    server_manager.write_properties(sdir, name, server_manager.default_properties(name))

    meta = {
        "name": name,
        "type": srv_type,
        "version": version,
        "ram_mb": ram_mb,
        "jar": "server.jar",
        "created": time.time(),
        "loader": None,
    }
    config.save_server_meta(name, meta)

    # Download / install the server distribution
    menus.info(t("wizard.checking"))
    try:
        if srv_type == "vanilla":
            info = version_manager.get_vanilla_server_info(version)
            dest = os.path.join(sdir, "server.jar")
            free = device_info.storage_info(sdir)[2]
            size = int(info.get("size", 0) or 0)
            if free and size and free < size + 512 * 1024 * 1024:
                raise RuntimeError(t("download.error_space"))
            ds = downloader.DownloadState(f"Minecraft {version} (server.jar)", info["url"], dest,
                                          sha1=info.get("sha1"), expected_size=size)
            th = downloader.background_download(ds)
            progress.run_download_ui([ds])
            th.join()
            if not ds.success:
                raise RuntimeError(ds.error or "download_failed")
            result = {"jar": "server.jar", "java": info.get("java", 17)}
        elif srv_type == "fabric":
            loaders = version_manager.fetch_fabric_versions(version)
            loader = loaders[0] if loaders else "0.16.10"
            result = server_manager.install_fabric(sdir, version, loader, progress_cb=None)
            meta["loader"] = loader
        else:
            forges = version_manager.fetch_forge_versions(version)
            if not forges:
                raise RuntimeError(t("wizard.version_error") + f" {version}")
            forge = forges[0]
            result = server_manager.install_forge(sdir, version, forge, progress_cb=None)
            meta["forge"] = forge
    except RuntimeError as e:
        menus.error(str(e))
        return None, None
    except Exception as e:
        menus.error(str(e))
        return None, None

    meta.update(result)
    config.save_server_meta(name, meta)

    menus.success(t("wizard.created"))
    menus.header_table({
        t("dash.server"): name,
        t("dash.minecraft"): version,
        t("dash.type"): srv_type.title(),
        t("dash.ram"): f"{ram_mb} MB",
    })

    if menus.confirm(t("wizard.start_now")):
        if server_manager.start_server(name):
            from ui.console_view import run_console
            run_console(name)
    return name, meta