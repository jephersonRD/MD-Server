#!/usr/bin/env bash
# ============================================================
#  MD Server — Minecraft Java Server Manager for Termux/Android
#  Installer
# ============================================================
set -e

INFO='\033[0;36m'
OK='\033[0;32m'
WARN='\033[0;33m'
ERR='\033[0;31m'
NC='\033[0m'

echo -e "${INFO}╔════════════════════════════════════════════╗${NC}"
echo -e "${INFO}║         MD SERVER install script          ║${NC}"
echo -e "${INFO}╚════════════════════════════════════════════╝${NC}"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

detect_pkg() {
    if command -v pkg >/dev/null 2>&1 && [[ "$PREFIX" == *termux* ]]; then
        echo "pkg"
    elif command -v apt-get >/dev/null 2>&1; then
        echo "apt-get"
    elif command -v apk >/dev/null 2>&1; then
        echo "apk"
    else
        echo ""
    fi
}

PKG=$(detect_pkg)
PYTHON="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON="python"
fi

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo -e "${WARN}[i] Python not found. Installing...${NC}"
    if [[ "$PKG" == "pkg" ]]; then
        pkg install -y python || { echo -e "${ERR}[x] Could not install python.${NC}"; exit 1; }
    elif [[ "$PKG" == "apt-get" ]]; then
        sudo apt-get update -y && sudo apt-get install -y python3 || { echo -e "${ERR}[x] Could not install python.${NC}"; exit 1; }
    elif [[ "$PKG" == "apk" ]]; then
        apk add python3 || { echo -e "${ERR}[x] Could not install python.${NC}"; exit 1; }
    else
        echo -e "${ERR}[x] Unsupported system. Install Python 3 manually.${NC}"
        exit 1
    fi
fi

echo -e "${INFO}[i] Installing Python packages (rich, requests) ...${NC}"
"$PYTHON" -m pip install --upgrade pip >/dev/null 2>&1 || true
"$PYTHON" -m pip install -r "${REPO_DIR}/requirements.txt" || "$PYTHON" -m pip install rich requests

# Global command
BIN_DIR="${PREFIX:-/usr/local}/bin"
mkdir -p "$BIN_DIR"
ln -sf "${REPO_DIR}/main.py" "$BIN_DIR/mdserver"
chmod +x "${REPO_DIR}/main.py"
chmod +x "$BIN_DIR/mdserver"

echo
echo -e "${OK}✓ MD Server installed!${NC}"
echo
echo -e "${INFO}  Run with:${NC} ${OK}mdserver${NC}"
echo -e "${INFO}  Or:       ${OK}${REPO_DIR}/main.py${NC}"
echo