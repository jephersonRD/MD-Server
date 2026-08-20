import re
import socket
import subprocess

import requests

PUBLIC_IP_URLS = ["https://api.ipify.org", "https://ifconfig.me/ip"]


def local_ip() -> str:
    methods = []
    try:
        r = subprocess.run(["ip", "-4", "addr", "show"], capture_output=True, text=True)
        if r.returncode == 0:
            for m in re.finditer(r"inet\s+(\d+\.\d+\.\d+\.\d+)", r.stdout):
                ip = m.group(1)
                if not ip.startswith("127."):
                    methods.append(ip)
    except Exception:
        pass
    # fallback: socket trick
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        methods.append(ip)
    except Exception:
        pass
    # fallback: hostname -I
    try:
        r = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
        if r.returncode == 0:
            methods.extend(r.stdout.split())
    except Exception:
        pass
    for ip in methods:
        if ip and not ip.startswith("127."):
            return ip
    return "0.0.0.0"


def public_ip(timeout=8) -> str:
    for url in PUBLIC_IP_URLS:
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": "MD-Server/1.0"})
            if r.status_code == 200:
                ip = r.text.strip()
                if re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):
                    return ip
        except Exception:
            continue
    return ""


def tool_installed(name: str) -> bool:
    for path in ("/data/data/com.termux/files/usr/bin", "/usr/local/bin", "/usr/bin"):
        import os
        if os.path.exists(os.path.join(path, name)):
            return True
    import shutil
    return shutil.which(name) is not None