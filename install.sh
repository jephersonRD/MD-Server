#!/usr/bin/env bash
# ============================================================
#  MD Server — Minecraft Java Server Manager for Termux/Android
#  Idempotent installer / updater
#
#  Works from:
#    - a fresh clone  (bash install.sh)
#    - an existing/old install  (auto-updates in place)
#    - a damaged/incomplete folder  (repairs safely)
#    - anywhere via:  curl -fsSL <URL> | bash
#  Never deletes user data (servers, worlds, mods, config live
#  in ~/mdserver, NOT inside the MD-Server code folder).
# ============================================================
set -euo pipefail

# ---------- colors ----------
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
RED='\033[0;31m'; MAGENTA='\033[0;35m'; WHITE='\033[1;37m'
GRAY='\033[0;90m'; BOLD='\033[1m'; NC='\033[0m'

# ---------- helpers ----------
msg()   { echo -e "  ${CYAN}→${NC} $1"; }
ok()    { echo -e "  ${GREEN}✓${NC} $1"; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $1"; }
die()   { echo -e "  ${RED}✗${NC} $1" >&2; exit 1; }

BOX_W=60
box_line() {
    local char="$1"
    local line=""
    for ((i=0; i<BOX_W; i++)); do line+="$char"; done
    echo -e "$line"
}

section() {
    echo
    echo -e "${CYAN}╭${NC}$(box_line "─")${CYAN}╮${NC}"
    echo -e "${CYAN}│${NC}  ${BOLD}$1${NC}"
    echo -e "${CYAN}├${NC}$(box_line "─")${CYAN}┤${NC}"
}

section_end() {
    echo -e "${CYAN}╰${NC}$(box_line "─")${CYAN}╯${NC}"
}

center_text() {
    local text="$1"
    local visible_len=${#text}
    local total=$((BOX_W - 2))
    local pad=$(( (total - visible_len) / 2 ))
    local pad_r=$(( total - visible_len - pad ))
    printf "%${pad}s""${text}""%${pad_r}s" "" ""
}

# ---------- project info ----------
GITHUB_REPO="jephersonRD/MD-Server"
GITHUB_URL="https://github.com/${GITHUB_REPO}.git"
BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/${GITHUB_REPO}/${BRANCH}"
INSTALL_DIR="${MD_SERVER_HOME:-$HOME}/MD-Server"

# ---------- banner ----------
clear
echo
echo -e "${CYAN}╭${NC}$(box_line "─")${CYAN}╮${NC}"
echo -e "${CYAN}│${NC}                                                              ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}   ${WHITE}███╗   ███╗██████╗   ███████╗███████╗██████╗ ██╗   ██╗${NC}   ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}   ${WHITE}████╗ ████║██╔══██╗  ██╔════╝██╔════╝██╔══██╗██║   ██║${NC}   ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}   ${WHITE}██╔████╔██║██║  ██║  ███████╗█████╗  ██████╔╝██║   ██║${NC}   ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}   ${WHITE}██║╚██╔╝██║██║  ██║  ╚════██║██╔══╝  ██╔══██╗██║   ██║${NC}   ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}   ${WHITE}██║ ╚═╝ ██║██████╔╝  ███████║███████╗██║  ██║╚██████╔╝${NC}   ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}   ${WHITE}╚═╝     ╚═╝╚═════╝   ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ${NC}   ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}                                                              ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}        ${GRAY}Minecraft Java Server Manager for Termux${NC}              ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}              ${MAGENTA}v1.1.8-beta${NC}  ${GRAY}·  Install / Update / Repair${NC}     ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}                                                              ${CYAN}│${NC}"
echo -e "${CYAN}╰${NC}$(box_line "─")${CYAN}╯${NC}"
echo

# ---------- are we running from inside the repo? ----------
SCRIPT_SRC="${BASH_SOURCE[0]:-}"
RUNNING_FROM_REPO=0
REPO_DIR=""
if [ -n "$SCRIPT_SRC" ] && [ "$SCRIPT_SRC" != "bash" ] && [ -f "${SCRIPT_SRC}" ]; then
    REPO_DIR="$(cd "$(dirname "$SCRIPT_SRC")" && pwd)"
    if [ -f "${REPO_DIR}/main.py" ] && [ -f "${REPO_DIR}/install.sh" ]; then
        RUNNING_FROM_REPO=1
    fi
fi
# Running via curl | bash  -> BASH_SOURCE is empty or stdin
if [ "$RUNNING_FROM_REPO" -eq 0 ]; then
    REPO_DIR="$INSTALL_DIR"
fi

# ---------- network check ----------
check_net() {
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL -o /dev/null --connect-timeout 8 --max-time 15 "https://github.com" 2>/dev/null && return 0
    fi
    if command -v wget >/dev/null 2>&1; then
        wget -q --spider --timeout=8 --tries=1 "https://github.com" 2>/dev/null && return 0
    fi
    return 1
}

section "Network Check"
if check_net; then
    ok "Internet connection available."
else
    warn "No internet connection detected."
    if [ -f "${REPO_DIR}/main.py" ]; then
        warn "Continuing with the already-installed files..."
    else
        section_end
        die "Internet connection required to install MD Server."
    fi
fi
section_end

# ---------- package manager detection ----------
detect_pkg() {
    if command -v pkg >/dev/null 2>&1 && [[ "${PREFIX:-}" == *termux* ]]; then echo "pkg"
    elif command -v apt-get >/dev/null 2>&1; then echo "apt-get"
    elif command -v apk >/dev/null 2>&1; then echo "apk"
    elif command -v dnf >/dev/null 2>&1; then echo "dnf"
    elif command -v yum >/dev/null 2>&1; then echo "yum"
    elif command -v pacman >/dev/null 2>&1; then echo "pacman"
    else echo ""; fi
}
PKG="$(detect_pkg)"

install_pkg() {
    local pkgname="$1"
    case "$PKG" in
        pkg)     pkg install -y "$pkgname" || pkg install -y "$pkgname" ;;
        apt-get) sudo apt-get update -y >/dev/null 2>&1 || true
                 sudo apt-get install -y "$pkgname" ;;
        apk)     apk add --no-cache "$pkgname" ;;
        dnf)     sudo dnf install -y "$pkgname" ;;
        yum)     sudo yum install -y "$pkgname" ;;
        pacman)  sudo pacman -S --noconfirm "$pkgname" ;;
        *)       return 1 ;;
    esac
}

have_cmd() { command -v "$1" >/dev/null 2>&1; }

# ---------- dependencies ----------
section "Checking Dependencies"

if have_cmd git; then
    ok "git is already installed."
else
    msg "Installing git..."
    install_pkg git || die "Could not install git. Install it manually and re-run."
    ok "git installed."
fi

PYTHON=""
for c in python3 python; do
    if have_cmd "$c"; then PYTHON="$c"; break; fi
done
if [ -z "$PYTHON" ]; then
    msg "Installing Python..."
    if [ "$PKG" = "pkg" ]; then
        pkg install -y python || die "Could not install python."
        PYTHON="python"
    else
        install_pkg python3 || die "Could not install python3."
        PYTHON="python3"
    fi
    ok "Python installed."
else
    ok "Python found: ${PYTHON}"
fi

if have_cmd curl || have_cmd wget; then
    ok "Network tools available."
else
    msg "Installing curl..."
    install_pkg curl || warn "Could not install curl; will try without it."
fi

section_end

# ---------- (re)obtain / update the code ----------
STATE="installed"   # installed | updated | up_to_date | repaired

ensure_repo() {
    if [ -d "${REPO_DIR}/.git" ]; then
        local old_head
        old_head="$(git -C "$REPO_DIR" rev-parse HEAD 2>/dev/null || echo none)"
        msg "Updating existing installation..."
        git -C "$REPO_DIR" fetch --depth 1 "origin" "$BRANCH" >/dev/null 2>&1 || \
            git -C "$REPO_DIR" fetch origin "$BRANCH" >/dev/null 2>&1 || true
        if git -C "$REPO_DIR" rev-parse --verify "origin/${BRANCH}" >/dev/null 2>&1; then
            if git -C "$REPO_DIR" rev-parse --verify "HEAD" >/dev/null 2>&1; then
                git -C "$REPO_DIR" reset --hard "origin/${BRANCH}" >/dev/null 2>&1 || \
                    git -C "$REPO_DIR" pull --ff-only origin "$BRANCH" >/dev/null 2>&1 || true
            else
                git -C "$REPO_DIR" checkout -f "${BRANCH}" >/dev/null 2>&1 || true
            fi
        fi
        local new_head
        new_head="$(git -C "$REPO_DIR" rev-parse HEAD 2>/dev/null || echo none)"
        if [ "$old_head" = "$new_head" ] || [ "$old_head" = "none" ]; then
            STATE="up_to_date"
        else
            STATE="updated"
        fi
    elif [ -d "$REPO_DIR" ]; then
        if [ -f "${REPO_DIR}/main.py" ] && [ -f "${REPO_DIR}/install.sh" ]; then
            msg "Converting existing folder into a git repository..."
            git -C "$REPO_DIR" init -q 2>/dev/null || true
            git -C "$REPO_DIR" remote remove origin 2>/dev/null || true
            git -C "$REPO_DIR" remote add origin "$GITHUB_URL"
            git -C "$REPO_DIR" fetch --depth 1 origin "$BRANCH" >/dev/null 2>&1 || true
            if git -C "$REPO_DIR" rev-parse --verify "origin/${BRANCH}" >/dev/null 2>&1; then
                git -C "$REPO_DIR" checkout -f -B "${BRANCH}" "origin/${BRANCH}" >/dev/null 2>&1 || true
            fi
            STATE="repaired"
        else
            local backup="${REPO_DIR}.old-$(date +%Y%m%d-%H%M%S)"
            warn "The folder '${REPO_DIR}' is damaged or is not MD Server."
            warn "Moving it to: ${backup}"
            mv "$REPO_DIR" "$backup"
            ok "Your files were preserved at: ${backup}"
            clone_fresh
            STATE="repaired"
        fi
    else
        clone_fresh
        STATE="installed"
    fi
}

clone_fresh() {
    msg "Downloading MD Server..."
    if have_cmd git; then
        git clone --depth 1 --branch "$BRANCH" "$GITHUB_URL" "$REPO_DIR" || die "Clone failed. Check your connection and re-run."
    else
        mkdir -p "$REPO_DIR"
        if have_cmd curl; then
            curl -fsSL "${RAW_BASE}/.gitignore" -o "${REPO_DIR}/.gitignore" || true
            curl -fsSL "${RAW_BASE}/main.py" -o "${REPO_DIR}/main.py" || die "Download failed."
        elif have_cmd wget; then
            wget -q "${RAW_BASE}/main.py" -O "${REPO_DIR}/main.py" || die "Download failed."
        else
            die "Neither git, curl nor wget are available."
        fi
    fi
    ok "MD Server downloaded."
}

section "Repository Status"
ensure_repo
case "$STATE" in
    installed)  ok "Fresh installation completed." ;;
    updated)    ok "Updated to latest version." ;;
    up_to_date) ok "Already up to date." ;;
    repaired)   ok "Installation repaired successfully." ;;
esac
section_end

# ---------- python dependencies ----------
install_pydeps() {
    local req="${REPO_DIR}/requirements.txt"
    msg "Installing Python packages..."
    if [ -f "$req" ]; then
        "$PYTHON" -m pip install -r "$req" >/dev/null 2>&1 || \
        "$PYTHON" -m pip install --break-system-packages -r "$req" >/dev/null 2>&1 || \
        "$PYTHON" -m pip install rich requests >/dev/null 2>&1 || \
        "$PYTHON" -m pip install --break-system-packages rich requests >/dev/null 2>&1 || \
            die "Could not install Python dependencies. Run: $PYTHON -m pip install -r $req"
    else
        "$PYTHON" -m pip install rich requests >/dev/null 2>&1 || \
        "$PYTHON" -m pip install --break-system-packages rich requests >/dev/null 2>&1 || \
            die "Could not install Python dependencies."
    fi
    ok "Python dependencies ready."
}

section "Python Dependencies"
install_pydeps
section_end

# ---------- global command ----------
make_executable() { chmod +x "$1" 2>/dev/null || true; }
make_executable "${REPO_DIR}/main.py"
make_executable "${REPO_DIR}/install.sh"

if [ -n "${PREFIX:-}" ] && [[ "$PREFIX" == *termux* ]]; then
    BIN_DIR="${PREFIX}/bin"
elif [ -n "$HOME" ]; then
    BIN_DIR="${HOME}/.local/bin"
else
    BIN_DIR="/usr/local/bin"
fi
mkdir -p "$BIN_DIR"

[ -e "$BIN_DIR/mdserver" ] && [ ! -L "$BIN_DIR/mdserver" ] && rm -f "$BIN_DIR/mdserver"
ln -sf "${REPO_DIR}/main.py" "$BIN_DIR/mdserver"

section "System Integration"
ok "Global command 'mdserver' created."

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)  profile=""
        if [ -f "${HOME}/.profile" ]; then profile="${HOME}/.profile"
        elif [ -f "${HOME}/.bashrc" ]; then profile="${HOME}/.bashrc"; fi
        if [ -n "$profile" ]; then
            printf '\n# Added by MD Server installer\nexport PATH="%s:$PATH"\n' "$BIN_DIR" >> "$profile"
            warn "Added ${BIN_DIR} to PATH in ${profile}."
            warn "Re-open the terminal or run: export PATH=\"${BIN_DIR}:\$PATH\""
        else
            warn "Add this to your shell profile to use 'mdserver' from anywhere:"
            warn "  export PATH=\"${BIN_DIR}:\$PATH\""
        fi
        ;;
esac
section_end

# ---------- done ----------
echo
case "$STATE" in
    updated)
        echo -e "${GREEN}╭${NC}$(box_line "─")${GREEN}╮${NC}"
        echo -e "${GREEN}│${NC}  ${WHITE}✓  MD SERVER UPDATED SUCCESSFULLY${NC}                           ${GREEN}│${NC}"
        echo -e "${GREEN}╰${NC}$(box_line "─")${GREEN}╯${NC}"
        ;;
    repaired)
        echo -e "${GREEN}╭${NC}$(box_line "─")${GREEN}╮${NC}"
        echo -e "${GREEN}│${NC}  ${WHITE}✓  MD SERVER REPAIRED AND UPDATED${NC}                           ${GREEN}│${NC}"
        echo -e "${GREEN}╰${NC}$(box_line "─")${GREEN}╯${NC}"
        ;;
    up_to_date)
        echo -e "${GREEN}╭${NC}$(box_line "─")${GREEN}╮${NC}"
        echo -e "${GREEN}│${NC}  ${WHITE}✓  MD SERVER IS ALREADY UP TO DATE${NC}                           ${GREEN}│${NC}"
        echo -e "${GREEN}╰${NC}$(box_line "─")${GREEN}╯${NC}"
        ;;
    *)
        echo -e "${GREEN}╭${NC}$(box_line "─")${GREEN}╮${NC}"
        echo -e "${GREEN}│${NC}  ${WHITE}✓  MD SERVER READY TO USE${NC}                                    ${GREEN}│${NC}"
        echo -e "${GREEN}╰${NC}$(box_line "─")${GREEN}╯${NC}"
        ;;
esac
echo

# ---------- next steps ----------
echo -e "${CYAN}╭${NC}$(box_line "─")${CYAN}╮${NC}"
echo -e "${CYAN}│${NC}  ${BOLD}Next Steps${NC}                                                    ${CYAN}│${NC}"
echo -e "${CYAN}├${NC}$(box_line "─")${CYAN}┤${NC}"
echo -e "${CYAN}│${NC}                                                              ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}  To start MD Server run this command:                        ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}                                                              ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}    ${GREEN}${BOLD}mdserver${NC}                                                  ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}                                                              ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}  ${GRAY}You can run it from any folder. The wizard will guide you.${NC}  ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}                                                              ${CYAN}│${NC}"
if [ -f "${REPO_DIR}/main.py" ]; then
    echo -e "${CYAN}│${NC}  ${GRAY}Installed at: ${BOLD}${REPO_DIR}${NC}                                 ${CYAN}│${NC}"
    echo -e "${CYAN}│${NC}                                                              ${CYAN}│${NC}"
fi
echo -e "${CYAN}╰${NC}$(box_line "─")${CYAN}╯${NC}"
echo
