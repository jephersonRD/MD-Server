import os
import re
import shutil
from pathlib import Path

from core import config


def mods_dir(server) -> str:
    return os.path.join(config.server_dir(server), "mods")


def list_mods(server) -> list:
    d = mods_dir(server)
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if f.endswith(".jar"))


def import_mods(server) -> list:
    d = mods_dir(server)
    Path(d).mkdir(parents=True, exist_ok=True)
    imported = []
    if not os.path.isdir(config.IMPORT_MODS):
        return imported
    for f in sorted(os.listdir(config.IMPORT_MODS)):
        if f.endswith(".jar"):
            dst = os.path.join(d, f)
            if not os.path.exists(dst):
                shutil.copy2(os.path.join(config.IMPORT_MODS, f), dst)
            imported.append(f)
    return imported


def remove_mod(server, mod: str) -> bool:
    p = os.path.join(mods_dir(server), mod)
    if os.path.exists(p):
        os.remove(p)
        return True
    return False


def validate_mod(mc_version: str, loader: str, mod_name: str) -> tuple:
    """Best-effort validation of a mod name against MC version. Returns (ok, warning)."""
    warnings = []
    low = mod_name.lower()
    found_version = None
    # Pattern 1: "mod-1.0.0+1.21.1" → game version after "+"
    m = re.search(r"\+(\d+(?:.\d+){1,3})", low)
    if m:
        found_version = m.group(1)
    if not found_version:
        for part in low.replace(".jar", "").replace("_", "-").split("-"):
            if part[:1].isdigit() and "." in part:
                nums = part.split(".")
                if len(nums) >= 2 and all(n.replace("+", "").isdigit() for n in nums):
                    found_version = part
                    break
    if found_version:
        fparts = found_version.split(".")
        mparts = mc_version.split(".")
        if len(fparts) >= 2 and len(mparts) >= 2 and len(fparts) <= 3:
            if fparts[0] != mparts[0] or fparts[1] != mparts[1]:
                warnings.append(f"{mod_name} → MC {found_version} ≠ server {mc_version}")
    return (not warnings), "; ".join(warnings)