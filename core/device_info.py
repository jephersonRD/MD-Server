import os
import platform
import re
import socket
import subprocess

from core import config


def read_proc_meminfo():
    data = {}
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    data[parts[0].strip()] = int(re.sub(r"\D", "", parts[1]))
    except Exception:
        pass
    return data


def ram_total_mb() -> int:
    mem = read_proc_meminfo()
    if "MemTotal" in mem:
        return mem["MemTotal"] // 1024
    try:
        n = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip()
        if n:
            return int(n) // 1048576
    except Exception:
        pass
    return 0


def ram_available_mb() -> int:
    mem = read_proc_meminfo()
    if "MemAvailable" in mem:
        return mem["MemAvailable"] // 1024
    if "MemFree" in mem and "Cached" in mem:
        return (mem["MemFree"] + mem["Cached"]) // 1024
    return 0


def cpu_cores() -> int:
    try:
        with open("/proc/cpuinfo", "r") as f:
            return f.read().count("processor")
    except Exception:
        pass
    try:
        return len(os.listdir("/sys/devices/system/cpu")) - 1
    except Exception:
        return os.cpu_count() or 1


def cpu_arch() -> str:
    arch = platform.machine().lower()
    mapping = {
        "aarch64": "ARM64",
        "armv8l": "ARM32 (v8)",
        "armv7l": "ARM32",
        "armv6l": "ARM32",
        "arm": "ARM32",
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "i686": "x86",
        "i386": "x86",
    }
    return mapping.get(arch, arch.upper())


def is_aarch64() -> bool:
    return platform.machine().lower() in ("aarch64", "arm64")


def android_version() -> str:
    try:
        r = subprocess.run(["getprop", "ro.build.version.release"], capture_output=True, text=True)
        v = r.stdout.strip()
        return v if v else "?"
    except Exception:
        return "?"


def termux_version() -> str:
    try:
        r = subprocess.run([os.environ.get("PREFIX", "/data/data/com.termux/files/usr") + "/bin/termux_version"],
                           capture_output=True, text=True)
        return r.stdout.strip() or "?"
    except Exception:
        return "?"


def is_termux() -> bool:
    return os.environ.get("TERMUX_VERSION") is not None or os.path.exists(
        "/data/data/com.termux/files/usr/etc/motd")


def storage_info(path=None):
    path = path or os.path.expanduser("~")
    try:
        st = os.statvfs(path)
        total = st.f_blocks * st.f_frsize
        free = st.f_bavail * st.f_frsize
        used = total - free
        return total, used, free
    except Exception:
        return 0, 0, 0


def java_version() -> str:
    import shutil
    p = shutil.which("java")
    if not p:
        return "not_installed"
    try:
        r = subprocess.run([p, "-version"], capture_output=True, text=True)
        out = r.stderr or r.stdout
        m = re.search(r'"(\d+)', out)
        if m:
            v = int(m.group(1))
            if v == 1:
                m2 = re.search(r'"1\.(\d+)', out)
                v = int(m2.group(1)) if m2 else v
            return str(v)
        return out.strip().splitlines()[0][:30] if out.strip() else "?"
    except Exception:
        return "?"


def python_version() -> str:
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def internet_available(timeout=5) -> bool:
    try:
        s = socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        s.close()
        return True
    except Exception:
        return False


def uptime_seconds():
    try:
        with open("/proc/uptime", "r") as f:
            return float(f.read().split()[0])
    except Exception:
        return 0


def collect() -> dict:
    return {
        "ram_total": ram_total_mb(),
        "ram_available": ram_available_mb(),
        "cpu_cores": cpu_cores(),
        "cpu_arch": cpu_arch(),
        "android": android_version(),
        "termux": termux_version(),
        "storage_total": storage_info()[0],
        "storage_used": storage_info()[1],
        "storage_free": storage_info()[2],
        "java": java_version(),
        "python": python_version(),
        "internet": internet_available(),
        "is_aarch64": is_aarch64(),
    }