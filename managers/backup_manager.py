import os
import shutil
import threading
import time
from pathlib import Path

from core import config

def backups_root(name) -> str:
    return os.path.join(config.BACKUPS_DIR, name)


def list_backups(name) -> list:
    root = backups_root(name)
    if not os.path.isdir(root):
        return []
    return sorted((os.path.join(root, f) for f in os.listdir(root) if f.endswith(".tar.gz")),
                  key=os.path.getmtime, reverse=True)


def human_size(path):
    s = os.path.getsize(path)
    for u in ("B", "KB", "MB", "GB"):
        if s < 1024:
            return f"{s:.1f} {u}"
        s /= 1024
    return f"{s:.1f} TB"


def create_backup(name, label=None, include_mods=True, include_config=True) -> str:
    sdir = config.server_dir(name)
    root = backups_root(name)
    Path(root).mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    label = (label or "").lower()
    safe = "".join(c for c in label if c.isalnum() or c in "_-")
    base = f"{stamp}" + (f"_{safe}" if safe else "")
    arc = os.path.join(root, f"{base}.tar.gz")

    files = []
    world = os.path.join(sdir, "world")
    if os.path.isdir(world):
        files.append("world")
    if os.path.exists(os.path.join(sdir, "server.properties")):
        files.append("server.properties")
    if os.path.exists(os.path.join(sdir, "eula.txt")):
        files.append("eula.txt")
    if include_config and os.path.isdir(os.path.join(sdir, "config")):
        files.append("config")
    if include_mods and os.path.isdir(os.path.join(sdir, "mods")):
        files.append("mods")

    if not files:
        # empty state backup
        Path(os.path.join(sdir, ".md-empty")).touch(exist_ok=True)
        files = [".md-empty"]

    _tar_subset(sdir, files, arc)
    return arc


def _tar_subset(sdir, items, arc):
    import tarfile
    with tarfile.open(arc, "w:gz") as tf:
        for it in items:
            tf.add(os.path.join(sdir, it), arcname=it, recursive=True)


def restore_backup(name, arc, confirm=True) -> bool:
    sdir = config.server_dir(name)
    files = ["world", "config", "mods", "plugins"]
    removed = []
    for f in files:
        p = os.path.join(sdir, f)
        if os.path.exists(p):
            shutil.move(p, p + ".bak_" + str(int(time.time())))
            removed.append(p + ".bak_" + str(int(time.time())))
    try:
        shutil.unpack_archive(arc, sdir)
        for bak in removed:
            if os.path.exists(bak):
                shutil.rmtree(bak)
        return True
    except Exception:
        for bak in removed:
            orig = bak.rsplit(".bak_", 1)[0]
            shutil.move(bak, orig)
        return False


def delete_backup(path) -> bool:
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


class AutoBackupScheduler:
    def __init__(self, name, interval_min):
        self.name = name
        self.interval = interval_min * 60
        self.stop_flag = threading.Event()
        self.t = None
        self.last = time.time()

    def start(self):
        self.t = threading.Thread(target=self._loop, daemon=True)
        self.t.start()

    def stop(self):
        self.stop_flag.set()

    def _loop(self):
        while not self.stop_flag.wait(self.interval):
            create_backup(self.name, label="auto")

    def is_alive(self):
        return self.t and self.t.is_alive()