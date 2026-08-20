import json
import os
import shutil
import subprocess
from pathlib import Path

BASE_DIR = os.path.expanduser("~/mdserver")
SERVERS_DIR = os.path.join(BASE_DIR, "servers")
IMPORT_WORLDS = os.path.join(BASE_DIR, "import", "worlds")
IMPORT_MODS = os.path.join(BASE_DIR, "import", "mods")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
STATE_DIR = os.path.join(BASE_DIR, ".state")


def ensure_dirs():
    for d in (SERVERS_DIR, IMPORT_WORLDS, IMPORT_MODS, BACKUPS_DIR, CONFIG_DIR, STATE_DIR):
        Path(d).mkdir(parents=True, exist_ok=True)


def get_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def set_config(key, value):
    cfg = get_config()
    cfg[key] = value
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def get_state(server) -> dict:
    path = os.path.join(STATE_DIR, f"{safe_name(server)}.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def set_state(server, key, value):
    cfg = get_state(server)
    cfg[key] = value
    ensure_dirs()
    with open(os.path.join(STATE_DIR, f"{safe_name(server)}.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def safe_name(name: str) -> str:
    keep = ""
    for ch in name.strip().replace(" ", "_"):
        if ch.isalnum() or ch in ("_", "-", "."):
            keep += ch
    return keep or "server"


def server_dir(name: str) -> str:
    return os.path.join(SERVERS_DIR, safe_name(name))


def metadata_path(name: str) -> str:
    return os.path.join(server_dir(name), "mdserver.json")


def load_server_meta(name: str) -> dict:
    p = metadata_path(name)
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_server_meta(name: str, meta: dict):
    ensure_dirs()
    Path(server_dir(name)).mkdir(parents=True, exist_ok=True)
    with open(metadata_path(name), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def list_servers() -> list:
    ensure_dirs()
    out = []
    for d in sorted(os.listdir(SERVERS_DIR)):
        p = os.path.join(SERVERS_DIR, d)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "mdserver.json")):
            out.append(d)
    return out


def detect_type_from_files(sdir: str) -> str:
    """Detect server type from the real files when metadata is missing."""
    try:
        names = [f.lower() for f in os.listdir(sdir)]
    except Exception:
        return "unknown"
    for n in names:
        if n.endswith(".jar") and ("forge" in n):
            return "forge"
    for n in names:
        if n.endswith(".jar") and ("fabric" in n):
            return "fabric"
    if "server.jar" in names:
        return "vanilla"
    if os.path.isdir(os.path.join(sdir, "mods")):
        return "unknown"
    return "unknown"


def get_server_type(name: str) -> str:
    """Server type from metadata (migrating old servers automatically)."""
    meta = load_server_meta(name)
    t = meta.get("type")
    if t in ("vanilla", "fabric", "forge"):
        return t
    detected = detect_type_from_files(server_dir(name))
    if detected in ("vanilla", "fabric", "forge"):
        meta["type"] = detected
        save_server_meta(name, meta)
        return detected
    return "unknown"


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run_command(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)