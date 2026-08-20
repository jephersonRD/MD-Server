import os
import shutil
import time
from pathlib import Path

from core import config

_SKIP = {"logs", "config", "libraries", "mods", "plugins", "backups", "cache", "world_old"}


def list_worlds(server):
    sdir = config.server_dir(server)
    out = []
    if not os.path.isdir(sdir):
        return out
    for d in sorted(os.listdir(sdir)):
        p = os.path.join(sdir, d)
        if os.path.isdir(p) and d not in _SKIP and not d.startswith("."):
            # a real world has level.dat or a `level` subfolder and region data
            if os.path.exists(os.path.join(p, "level.dat")) or os.path.exists(os.path.join(p, "level.dat_mcr")) or os.path.exists(os.path.join(p, "region")) or os.path.exists(os.path.join(p, os.path.join(p, "level"))):
                out.append(d)
    return out or _fallback_worlds(server)


def _fallback_worlds(server):
    active = active_world(server)
    sdir = config.server_dir(server)
    out = []
    for d in sorted(os.listdir(sdir)):
        p = os.path.join(sdir, d)
        if os.path.isdir(p) and d not in _SKIP and d.startswith("world"):
            out.append(d)
    return out


def active_world(server) -> str:
    from core.server_manager import read_property
    return read_property(config.server_dir(server), "level-name", "world")


def set_active_world(server, world: str) -> bool:
    from core.server_manager import read_property, write_properties
    sdir = config.server_dir(server)
    props = {}
    for line in open(os.path.join(sdir, "server.properties"), encoding="utf-8", errors="ignore"):
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            props[k.strip()] = v.strip()
    props["level-name"] = world
    write_properties(sdir, server, props)
    return True


def create_world(server, name: str) -> bool:
    sdir = config.server_dir(server)
    world_dir = os.path.join(sdir, name)
    Path(world_dir).mkdir(parents=True, exist_ok=True)
    # An empty level-name dir makes the server generate a fresh world on start
    return True


def import_from_folder(server) -> list:
    sdir = config.server_dir(server)
    imported = []
    if not os.path.isdir(config.IMPORT_WORLDS):
        return imported
    for d in sorted(os.listdir(config.IMPORT_WORLDS)):
        src = os.path.join(config.IMPORT_WORLDS, d)
        if not os.path.isdir(src):
            continue
        dst = os.path.join(sdir, d)
        if os.path.exists(dst):
            dst = os.path.join(sdir, f"{d}_{int(time.time())}")
        shutil.copytree(src, dst)
        imported.append(os.path.basename(dst))
    return imported


def delete_world(server, world: str) -> bool:
    sdir = config.server_dir(server)
    target = os.path.join(sdir, world)
    if os.path.isdir(target):
        shutil.rmtree(target)
        return True
    return False


def backup_world(server, world: str, backups_root: str) -> str:
    sdir = config.server_dir(server)
    src = os.path.join(sdir, world)
    dst_dir = os.path.join(backups_root, "worlds")
    Path(dst_dir).mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(dst_dir, f"{world}_{stamp}.tar.gz")
    if os.path.isdir(src):
        shutil.make_archive(dst[:-7], "gztar", root_dir=sdir, base_dir=world)
    elif os.path.exists(src + ".tar.gz"):
        shutil.copy2(src + ".tar.gz", dst)
    return dst


def restore_world(server, world: str, arc: str) -> bool:
    sdir = config.server_dir(server)
    target = os.path.join(sdir, world)
    if os.path.isdir(target):
        shutil.rmtree(target)
    shutil.unpack_archive(arc, sdir)
    return True