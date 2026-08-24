import os
import re
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from core import config, device_info, java_manager, memory_manager, server_manager, version_manager
from core import downloader
from core.i18n import t
from ui import menus, progress

console = Console()

_VERSION_RE = re.compile(r"^v?\d+(\.\d+){1,3}(-[0-9A-Za-z.]+)?$|^\d{2}w\d{2}[a-z]$")


def _is_valid_version(v: str) -> bool:
    return bool(_VERSION_RE.match(v.strip()))


def _pick_version(versions):
    PAGE = 30
    offset = 0
    while True:
        chunk = versions[offset:offset + PAGE]
        opts = [(v,) for v in chunk]
        more = offset + PAGE < len(versions)
        if more:
            opts.append((t("wizard.older_versions"),))
        opts.append((t("wizard.custom_version"),))
        if offset > 0:
            opts.append((t("wizard.back_newer"),))
        choice = menus.ask(t("wizard.version"), opts, allow_custom=True)
        if not choice.isdigit():
            if _is_valid_version(choice):
                menus.success(f"{t('wizard.version_selected')}: {choice}")
                return choice
            menus.error(t("wizard.custom_version_invalid"))
            continue
        i = int(choice)
        if i <= len(chunk):
            return chunk[i - 1]
        idx = i - len(chunk)
        if more:
            if idx == 1:
                offset += PAGE
                continue
            if idx == 2:
                v = menus.input_text(t("wizard.custom_version_prompt"), validate=_is_valid_version)
                menus.success(f"{t('wizard.version_selected')}: {v}")
                return v
            offset = max(0, offset - PAGE)
            continue
        if idx == 1:
            v = menus.input_text(t("wizard.custom_version_prompt"), validate=_is_valid_version)
            menus.success(f"{t('wizard.version_selected')}: {v}")
            return v
        if idx == 2:
            offset = max(0, offset - PAGE)
            continue


def _pick_type():
    opts = [
        (t("wizard.vanilla"), t("wizard.vanilla_desc")),
        (f"[yellow dim]{t('wizard.fabric')} — {t('wizard.coming_soon')}[/yellow dim]",),
        (f"[yellow dim]{t('wizard.forge')} — {t('wizard.coming_soon')}[/yellow dim]",),
    ]
    while True:
        i = int(menus.ask(t("wizard.type"), opts))
        if i == 1:
            return "vanilla"
        loader = t("wizard.fabric") if i == 2 else t("wizard.forge")
        menus.warning(t("wizard.soon_alert").format(loader=loader))
        continue


def _pick_java(minecraft_version: str) -> int | None:
    """Show Java selection screen. Returns chosen Java major version or None to go back."""
    recommended = java_manager.get_recommended_java(minecraft_version)
    compatible = java_manager.get_compatible_java_versions(minecraft_version)
    installed = java_manager.detect_installed_java()

    while True:
        console.print()
        lines = []
        lines.append(f"  {t('wizard.java_minecraft')}: [bold]{minecraft_version}[/bold]")
        lines.append("")
        lines.append(f"  ☕ {t('wizard.java_recommended_label')}: [bold green]{t('wizard.java_version')} {recommended}[/bold green]")
        lines.append("")

        opts = []
        for idx, jver in enumerate(compatible, 1):
            label_key = java_manager.java_label(minecraft_version, jver)
            label = t(label_key)
            status_parts = [f"Java {jver}"]
            if jver == recommended:
                status_parts.append(f"[bold green]— {t('wizard.java_recommended')}[/bold green]")
            elif jver > recommended:
                status_parts.append(f"[cyan]— {t('wizard.java_compatible')}[/cyan]")
            else:
                status_parts.append(f"[red]— {t('wizard.java_incompatible')}[/red]")

            if jver in installed:
                status_parts.append(f" [dim]({t('common.installed')})[/dim]")

            opts.append((" ".join(status_parts),))

        opts.append((f"← {t('wizard.back')}",))

        console.print(Panel(
            "\n".join(lines),
            border_style="cyan",
            title=f"[bold cyan]{t('wizard.java_title')}[/bold cyan]",
            padding=(0, 1),
        ))

        choice = menus.ask(t("wizard.java_select"), opts)

        if not choice.isdigit():
            menus.error(t("common.invalid_option"))
            continue

        i = int(choice)
        if i == len(opts):
            return None  # go back

        if i < 1 or i > len(compatible):
            menus.error(t("common.invalid_option"))
            continue

        chosen_java = compatible[i - 1]

        # Check if incompatible
        if not java_manager.is_java_compatible(minecraft_version, chosen_java):
            menus.warning(t("wizard.java_incompatible_warning").format(
                java=chosen_java, minecraft=minecraft_version
            ))
            continue

        return chosen_java


def run_wizard(auto_ram=None):
    """Guided server creation. Returns (server_name, meta)."""
    menus.title(t("wizard.title"))

    srv_type = _pick_type()

    # versions
    console.print(f"[dim]{t('wizard.version_fetching')}[/dim]")
    with console.status(t("wizard.version_fetching")):
        if srv_type == "vanilla":
            versions = version_manager.fetch_vanilla_versions()
        else:
            versions = version_manager.fetch_vanilla_versions()[:30]
    if version_manager.last_used_fallback:
        menus.warning(t("wizard.versions_fallback"))
    version = _pick_version(versions)

    # Clear warning for very old versions that need Java 8 (not available in Termux)
    if java_manager.get_recommended_java(version) == 8:
        if not menus.confirm(t("wizard.old_java_warning").format(version=version)):
            menus.info(t("common.cancel"))
            return None, None

    # Java selection screen
    chosen_java = None
    while True:
        result = _pick_java(version)
        if result is None:
            # User pressed back — go back to type selection
            return run_wizard(auto_ram=auto_ram)
        chosen_java = result
        break

    # Ensure Java is installed
    installed = java_manager.detect_installed_java()
    java_path = installed.get(chosen_java)
    if not java_path:
        menus.info(t("wizard.java_downloading").format(java=chosen_java))
        success = java_manager.install_java_version(chosen_java)
        if not success:
            menus.error(t("wizard.java_failed"))
            return None, None
        installed = java_manager.detect_installed_java()
        java_path = installed.get(chosen_java)
        if not java_path:
            menus.error(t("wizard.java_failed"))
            return None, None

    # Verify Java version
    ok, detected, path = java_manager.verify_java_version(chosen_java)
    if not ok:
        menus.error(t("wizard.java_verify_failed").format(expected=chosen_java, found=detected))
        return None, None

    menus.success(f"Java {chosen_java} ✓ ({path})")

    # RAM
    dev = device_info.collect()
    if auto_ram is None:
        auto_ram = memory_manager.recommend_ram(dev["ram_total"], dev["ram_available"])
    ram_mb = None
    if auto_ram > 0:
        i = int(menus.ask(
            f"{t('wizard.ram_title')}: [bold cyan]{auto_ram} MB[/bold cyan]",
            [(f"{t('wizard.ram_recommended')} ({auto_ram} MB)",),
             (t("wizard.ram_manual"),)],
        ))
        if i == 1:
            ram_mb = auto_ram
    if ram_mb is None:
        ram_mb = menus.input_int(t("wizard.ram_prompt") + " (MB)", default=auto_ram or 2048, minimum=1024)
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

    # internet check
    if not device_info.internet_available():
        menus.error(t("download.error_internet"))
        return None, None

    # Folders
    sdir = config.server_dir(name)
    if os.path.exists(sdir) and os.listdir(sdir):
        menus.error(f"{t('common.error')}: {t('wizard.already_exists')} '{name}'")
        return None, None
    Path(sdir).mkdir(parents=True, exist_ok=True)
    server_manager.create_folder_structure(sdir, srv_type)
    server_manager.write_eula(sdir, True)
    server_manager.write_properties(sdir, name, server_manager.default_properties(name))

    meta = {
        "name": name,
        "type": srv_type,
        "version": version,
        "java_version": chosen_java,
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
            result = {"jar": "server.jar", "java": info.get("java", chosen_java)}
        elif srv_type == "fabric":
            loaders = version_manager.fetch_fabric_versions(version)
            if not loaders:
                raise RuntimeError(t("wizard.unsupported_loader").format(loader=t("wizard.fabric"), version=version))
            loader = loaders[0]
            result = server_manager.install_fabric(sdir, version, loader, progress_cb=None)
            meta["loader"] = loader
        else:
            forges = version_manager.fetch_forge_versions(version)
            if not forges:
                raise RuntimeError(t("wizard.unsupported_loader").format(loader=t("wizard.forge"), version=version))
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
    meta["java_version"] = chosen_java
    config.save_server_meta(name, meta)

    menus.success(t("wizard.created"))
    menus.header_table({
        t("dash.server"): name,
        t("dash.minecraft"): version,
        t("dash.type"): srv_type.title(),
        t("dash.ram"): f"{ram_mb} MB",
        t("dash.java"): f"Java {chosen_java}",
    })

    if menus.confirm(t("wizard.start_now")):
        if server_manager.start_server(name):
            from ui.console_view import run_console
            run_console(name)
    return name, meta
