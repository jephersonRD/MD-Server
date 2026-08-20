import json
import urllib.request

MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
FABRIC_META = "https://meta.fabricmc.net/v2/versions/loader"
FABRIC_INSTALLER_URL = "https://meta.fabricmc.net/v2/versions/installer"
FORGE_INDEX = "https://files.minecraftforge.net/net/minecraftforge/forge/index.json"
FORGE_MAVEN = "https://maven.minecraftforge.net/net/minecraftforge/forge"
DEFAULT_VERSIONS = [
    "1.21.4", "1.21.1", "1.20.6", "1.20.4", "1.20.1", "1.19.4",
    "1.18.2", "1.16.5", "1.12.2", "1.8.9",
]


def _get_json(url, timeout=20):
    return json.loads(_get_raw(url, timeout))


def _get_raw(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "MD-Server/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")


def fetch_vanilla_versions() -> list:
    try:
        data = _get_json(MANIFEST_URL)
        versions = []
        for v in data.get("versions", []):
            if v.get("type") == "release":
                versions.append(v.get("id", ""))
        versions.sort(key=lambda s: [int(p) if p.isdigit() else p for p in s.split(".")], reverse=True)
        return versions or DEFAULT_VERSIONS
    except Exception:
        return DEFAULT_VERSIONS


def get_vanilla_server_info(version: str) -> dict:
    data = _get_json(MANIFEST_URL)
    for v in data.get("versions", []):
        if v.get("id") == version:
            vdata = _get_json(v["url"])
            server = vdata.get("downloads", {}).get("server", {})
            java_ver = vdata.get("javaVersion", {}).get("majorVersion", 17)
            return {"url": server.get("url"), "sha1": server.get("sha1"), "java": java_ver, "mainClass": "net.minecraft.server.Main"}
    raise RuntimeError(f"version_not_found:{version}")


def java_required(version: str) -> int:
    try:
        main = int(version.split(".")[1])
        if main >= 21:
            return 17
    except Exception:
        pass
    try:
        if int(version.split(".")[1]) >= 18:
            return 17
    except Exception:
        pass
    return 8


def java_21_required(version: str) -> bool:
    try:
        nums = version.split(".")
        if int(nums[0]) == 1:
            if int(nums[1]) >= 21:
                return True
        else:
            if int(nums[0]) >= 21:
                return True
        return False
    except Exception:
        return False


def fetch_fabric_versions(game_version: str) -> list:
    try:
        data = _get_json(f"{FABRIC_META}/{game_version}")
        return [d.get("loader", {}).get("version", "") for d in data]
    except Exception:
        return []


def fabric_installer_url() -> str:
    data = _get_json(FABRIC_INSTALLER_URL)
    return data[0].get("url")


def fabric_installer_name() -> str:
    data = _get_json(FABRIC_INSTALLER_URL)
    v = data[0].get("version", "")
    return f"fabric-installer-{v}.jar"


def fetch_forge_versions(game_version: str) -> list:
    try:
        data = _get_json(FORGE_INDEX)
        for entry in data:
            if entry.get("version") == game_version:
                games = entry.get("files", {}).get(list(entry["files"].keys())[0], [])
                out = []
                for f in games:
                    if f.get("version") and not f["version"].endswith("-1.20.6") and f["version"].count(".") <= 2:
                        out.append(f["version"])
                return sorted(set(out), key=lambda s: len(s), reverse=True)
    except Exception:
        pass
    # fallback: Maven metadata
    try:
        import xml.etree.ElementTree as ET
        xml = _get_raw(FORGE_MAVEN + "/maven-metadata.xml")
        root = ET.fromstring(xml)
        vers = [v.text for v in root.findall("versioning/versions/version") if v.text]
        prefix = game_version + "-"
        out = sorted({v[len(prefix):] for v in vers if v.startswith(prefix)})
        return out[::-1]
    except Exception:
        return []


def forge_installer_url(game_version: str, forge_version: str) -> str:
    return f"{FORGE_MAVEN}/{game_version}-{forge_version}/forge-{game_version}-{forge_version}-installer.jar"