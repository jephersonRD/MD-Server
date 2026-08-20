import os

from core import config

PLUGIN_ENABLED_TYPES = {"paper", "spigot", "bukkit", "purpur", "fabric-plugin"}


def supports_plugins(server) -> bool:
    meta = config.load_server_meta(server)
    return meta.get("type", "").lower() in PLUGIN_ENABLED_TYPES


def plugins_dir(server) -> str:
    return os.path.join(config.server_dir(server), "plugins")


def list_plugins(server) -> list:
    d = plugins_dir(server)
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if f.endswith(".jar"))