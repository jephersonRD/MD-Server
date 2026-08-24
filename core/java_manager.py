import json
import os
import re
import shutil
import subprocess
import time

from core.i18n import t
from rich.console import Console

console = Console()

# ============================================================
# Centralized Minecraft → Java compatibility rules
# ============================================================
# Each entry maps a Minecraft version to its REQUIRED Java major version.
# Order: latest rules first so future versions are easy to add.
# To add a new Minecraft version, just append an entry here.
# ============================================================

_JAVA_COMPAT: list[tuple[str, int]] = [
    # Java 25
    ("26.2", 25),
    ("26.1", 25),
    # Java 21
    ("1.21.11", 21),
    ("1.21.10", 21),
    ("1.21.9", 21),
    ("1.21.8", 21),
    ("1.21.7", 21),
    ("1.21.6", 21),
    ("1.21.5", 21),
    ("1.21.4", 21),
    ("1.21.3", 21),
    ("1.21.2", 21),
    ("1.21.1", 21),
    ("1.21", 21),
    ("1.20.6", 21),
    ("1.20.5", 21),
    # Java 17
    ("1.20.4", 17),
    ("1.20.3", 17),
    ("1.20.2", 17),
    ("1.20.1", 17),
    ("1.20", 17),
    ("1.19.4", 17),
    ("1.19.3", 17),
    ("1.19.2", 17),
    ("1.19.1", 17),
    ("1.19", 17),
    ("1.18.2", 17),
    ("1.18.1", 17),
    ("1.18", 17),
    # Java 16
    ("1.17.1", 16),
    ("1.17", 16),
    # Java 8
    ("1.16.5", 8),
    ("1.16.4", 8),
    ("1.16.3", 8),
    ("1.16.2", 8),
    ("1.16.1", 8),
    ("1.16", 8),
    ("1.15.2", 8),
    ("1.14.4", 8),
    ("1.13.2", 8),
    ("1.12.2", 8),
    ("1.11.2", 8),
    ("1.10.2", 8),
    ("1.9.4", 8),
    ("1.8.9", 8),
    ("1.7.10", 8),
]

# All known Java versions available for download (major version → display)
KNOWN_JAVA_VERSIONS = [8, 16, 17, 21, 25]

# ============================================================
# Package names for Termux
# ============================================================
TERMUX_JAVA_PACKAGES = {
    17: "openjdk-17",
    21: "openjdk-21",
    25: "openjdk-25",
}


def can_install_java(java_version: int) -> bool:
    """Check if a Java version can be installed via Termux pkg."""
    return java_version in TERMUX_JAVA_PACKAGES

# Java download URLs (Adoptium / Eclipse Temurin for Android/aarch64)
# These are real, maintained URLs for headless JDK builds.
_JAVA_DOWNLOAD_URLS: dict[int, dict] = {
    17: {
        "url": "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.13%2B11/OpenJDK17U-jdk_aarch64_linux_hotspot_17.0.13_11.tar.gz",
        "sha256": None,  # verified at download time
        "dir_name": "jdk-17",
    },
    21: {
        "url": "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.5%2B11/OpenJDK21U-jdk_aarch64_linux_hotspot_21.0.5_11.tar.gz",
        "sha256": None,
        "dir_name": "jdk-21",
    },
}


def _parse_version(version: str) -> list[int]:
    """Parse '1.20.1' or '26.1' into [1, 20, 1] or [26, 1]."""
    parts = []
    for p in version.strip().split("."):
        try:
            parts.append(int(p))
        except ValueError:
            break
    return parts


def _version_key(version: str) -> tuple:
    """Comparable key for sorting versions."""
    return tuple(_parse_version(version))


def get_recommended_java(minecraft_version: str) -> int:
    """Return the recommended Java major version for a Minecraft version.
    Defaults to 21 for truly unknown future versions.
    """
    mv = minecraft_version.strip()
    for pattern, jver in _JAVA_COMPAT:
        if mv == pattern:
            return jver
    # For versions not in the table, try to guess by prefix
    mv_parts = _parse_version(mv)
    if not mv_parts:
        return 21
    # If major > 1 (e.g. 26.x, 27.x), use latest Java
    if mv_parts[0] > 1:
        return 25
    # If 1.21+ range not explicitly listed, use 21
    if mv_parts[0] == 1 and len(mv_parts) >= 2:
        if mv_parts[1] >= 21:
            return 21
        if mv_parts[1] >= 18:
            return 17
        if mv_parts[1] >= 17:
            return 16
    return 8


def get_compatible_java_versions(minecraft_version: str) -> list[int]:
    """Return Java versions compatible with this Minecraft version, sorted by preference.
    Only includes versions >= recommended minimum. Recommended version is always first.
    """
    recommended = get_recommended_java(minecraft_version)
    compatible = []
    for jver in KNOWN_JAVA_VERSIONS:
        if jver >= recommended:
            compatible.append(jver)
    # Recommended first, then others
    result = [recommended] + [j for j in sorted(compatible) if j != recommended]
    return result


def is_java_compatible(minecraft_version: str, java_version: int) -> bool:
    """Check if a Java version is compatible with a Minecraft version."""
    recommended = get_recommended_java(minecraft_version)
    return java_version >= recommended


def java_label(minecraft_version: str, java_version: int) -> str:
    """Return a label like 'RECOMMENDADA', 'Compatible', or 'Incompatible'."""
    recommended = get_recommended_java(minecraft_version)
    if java_version == recommended:
        return "wizard.java_recommended"
    if java_version >= recommended:
        return "wizard.java_compatible"
    return "wizard.java_incompatible"


def get_java_executable(java_version: int) -> str | None:
    """Find the path to a specific Java executable.
    Checks: runtime dir, Termux packages, system PATH.
    Returns None if not found.
    """
    # 1. Check runtime dir in MD-Server
    runtime_dir = os.path.expanduser("~/mdserver/runtime")
    jdk_dir = os.path.join(runtime_dir, f"jdk-{java_version}")
    if os.path.isdir(jdk_dir):
        for root, dirs, files in os.walk(jdk_dir):
            if "java" in files:
                return os.path.join(root, "java")
            if "java.exe" in files:
                return os.path.join(root, "java.exe")

    # 2. Check Termux package
    pkg = TERMUX_JAVA_PACKAGES.get(java_version)
    if pkg:
        # Termux stores binaries in $PREFIX/bin
        prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
        pkg_bin = os.path.join(prefix, "bin", f"java-{java_version}")
        if os.path.exists(pkg_bin):
            return pkg_bin
        # Also check if the package provides a versioned symlink
        pkg_bin2 = os.path.join(prefix, "bin", f"java")
        # Some Termux packages install as 'java' directly
        # We need to check the version
        pass

    # 3. Check system PATH for a java that matches the version
    java_path = shutil.which("java")
    if java_path:
        detected = _detect_java_version_at(java_path)
        if detected == java_version:
            return java_path

    return None


def _detect_java_version_at(java_path: str) -> int | None:
    """Run 'java -version' at a given path and return the major version, or None."""
    try:
        r = subprocess.run([java_path, "-version"], capture_output=True, text=True, timeout=10)
        out = r.stderr or r.stdout
        m = re.search(r'"(\d+)', out)
        if m:
            v = int(m.group(1))
            if v == 1:
                m2 = re.search(r'"1\.(\d+)', out)
                v = int(m2.group(1)) if m2 else v
            return v
    except Exception:
        pass
    return None


def detect_installed_java() -> dict[int, str]:
    """Detect all installed Java versions and their paths.
    Returns {major_version: path} for each found Java.
    """
    found = {}

    prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")

    # 1. Check Termux bin for java-XX binaries (alternatives system)
    bin_dir = os.path.join(prefix, "bin")
    if os.path.isdir(bin_dir):
        for name in os.listdir(bin_dir):
            if name.startswith("java-") and name[5:].isdigit():
                jver = int(name[5:])
                path = os.path.join(bin_dir, name)
                if os.path.isfile(path) and os.access(path, os.X_OK):
                    found[jver] = path

    # 2. Check JDK directories in $PREFIX/lib/jvm/
    jvm_dir = os.path.join(prefix, "lib", "jvm")
    if os.path.isdir(jvm_dir):
        for entry in os.listdir(jvm_dir):
            match = re.match(r"java-(\d+)-openjdk", entry)
            if match:
                jver = int(match.group(1))
                if jver not in found:
                    java_bin = os.path.join(jvm_dir, entry, "bin", "java")
                    if os.path.isfile(java_bin) and os.access(java_bin, os.X_OK):
                        found[jver] = java_bin

    # 3. Check runtime dir (MD-Server managed JDKs)
    runtime_dir = os.path.expanduser("~/mdserver/runtime")
    if os.path.isdir(runtime_dir):
        for entry in os.listdir(runtime_dir):
            if entry.startswith("jdk-"):
                try:
                    jver = int(entry[4:])
                except ValueError:
                    continue
                if jver not in found:
                    jdk_dir = os.path.join(runtime_dir, entry)
                    for root, dirs, files in os.walk(jdk_dir):
                        if "java" in files:
                            found[jver] = os.path.join(root, "java")
                            break

    # 4. Check system java
    java_path = shutil.which("java")
    if java_path:
        jver = _detect_java_version_at(java_path)
        if jver and jver not in found:
            found[jver] = java_path

    return found


def verify_java_version(expected: int) -> tuple[bool, int | None, str | None]:
    """Verify that the installed Java matches the expected version.
    Returns (ok, detected_version, path).
    """
    installed = detect_installed_java()
    path = installed.get(expected)
    if path:
        detected = _detect_java_version_at(path)
        if detected == expected:
            return True, detected, path
    # Try system java
    java_path = shutil.which("java")
    if java_path:
        detected = _detect_java_version_at(java_path)
        if detected == expected:
            return True, detected, java_path
    return False, None, None


def ensure_java_for_server(minecraft_version: str, auto: bool = False) -> tuple[bool, str | None]:
    """Ensure the right Java is available for a Minecraft version.
    Returns (success, java_executable_path).
    """
    required = get_recommended_java(minecraft_version)
    installed = detect_installed_java()

    # Check if we already have a compatible version
    for jver in sorted(installed.keys(), reverse=True):
        if jver >= required:
            if auto:
                console.print(f"  [green]✓ Java {jver} found: {installed[jver]}[/green]")
            return True, installed[jver]

    # Need to install
    if not auto:
        console.print(f"[bold yellow]{t('install.java_missing')} → Java {required}[/bold yellow]")
        confirm = console.input(f"[bold]{t('common.confirm')} ({t('common.yes')}/{t('common.no')}): [/bold]").strip().lower()
        if confirm not in ("y", "yes", "s", "si", "sí"):
            return False, None

    success = install_java_version(required)
    if success:
        installed = detect_installed_java()
        path = installed.get(required)
        return True, path
    return False, None


def install_java_version(java_version: int) -> bool:
    """Install a specific Java version via Termux pkg.
    Returns True on success.
    """
    pkg = TERMUX_JAVA_PACKAGES.get(java_version)
    if not pkg:
        available = ", ".join(str(v) for v in sorted(TERMUX_JAVA_PACKAGES.keys()))
        console.print(f"[bold red][✗] Java {java_version} {t('wizard.java_not_available_termux')}[/bold red]")
        console.print(f"[dim]  {t('wizard.java_available_versions')}: {available}[/dim]")
        return False

    console.print()
    console.print(f"[bold yellow]{t('install.java_missing')} → [cyan]{pkg}[/cyan][/bold yellow]")
    console.print(f"[cyan]{t('install.pkg')} {pkg} ...[/cyan]")
    with console.status(t("status.installing_java")):
        r = subprocess.run(["pkg", "install", "-y", pkg], text=True)
    if r.returncode != 0:
        console.print(f"[bold red][✗] {t('common.error')}: pkg install {pkg}[/bold red]")
        return False

    # Verify installation
    installed = detect_installed_java()
    if java_version in installed:
        console.print(f"[green]✓ Java {java_version} {t('common.installed_success')}[/green]")
        return True

    console.print(f"[bold red][✗] Java {java_version} {t('wizard.java_failed')}[/bold red]")
    return False


def get_java_executable_for_server(name: str) -> str:
    """Get the Java executable path for a specific server.
    Reads from metadata; falls back to system java.
    """
    from core import config
    meta = config.load_server_meta(name)
    java_ver = meta.get("java_version")

    if java_ver:
        path = get_java_executable(java_ver)
        if path:
            return path

    # Fallback: try to detect from metadata java field or system
    java_ver = meta.get("java", 17)
    path = get_java_executable(java_ver)
    if path:
        return path

    # Final fallback: system java
    return shutil.which("java") or "java"


def check_java_before_start(name: str) -> tuple[bool, str | None]:
    """Check Java compatibility before starting a server.
    Returns (ok, error_message).
    """
    from core import config
    meta = config.load_server_meta(name)
    mc_version = meta.get("version", "")
    java_ver = meta.get("java_version") or meta.get("java", 17)

    if not mc_version:
        return True, None  # can't check without version info

    recommended = get_recommended_java(mc_version)
    if java_ver < recommended:
        msg = (
            f"⚠ {t('java.incompatible')}\n"
            f"  Minecraft: {mc_version}\n"
            f"  Java: {java_ver}\n"
            f"  {t('java.recommended')}: {recommended}"
        )
        return False, msg

    # Verify the executable actually matches
    path = get_java_executable(java_ver)
    if path:
        detected = _detect_java_version_at(path)
        if detected and detected != java_ver:
            msg = (
                f"⚠ {t('java.version_mismatch')}\n"
                f"  {t('java.selected')}: Java {java_ver}\n"
                f"  {t('java.found')}: Java {detected}"
            )
            return False, msg

    return True, None


def migrate_old_server_meta(name: str):
    """For servers created before v1.1.6-beta that lack java_version.
    Detect MC version and set java_version automatically.
    """
    from core import config
    meta = config.load_server_meta(name)
    if "java_version" in meta:
        return  # already migrated

    mc_version = meta.get("version", "")
    if mc_version:
        recommended = get_recommended_java(mc_version)
        meta["java_version"] = recommended
        meta["java"] = recommended
        config.save_server_meta(name, meta)
