#!/usr/bin/env sh
set -eu

DEFAULT_PACKAGE_SPEC="git+https://github.com/Sergio-prog/fram.git"
if [ -n "${FRAM_PACKAGE_SPEC:-}" ]; then
  PACKAGE_SPEC="$FRAM_PACKAGE_SPEC"
elif [ -f "pyproject.toml" ] && [ -d "fram" ]; then
  PACKAGE_SPEC="."
else
  PACKAGE_SPEC="$DEFAULT_PACKAGE_SPEC"
fi
CLI_NAME="${FRAM_CLI_NAME:-fram}"

if [ -z "${NO_COLOR:-}" ] && [ -t 1 ]; then
  BOLD="$(printf '\033[1m')"
  GREEN="$(printf '\033[32m')"
  RESET="$(printf '\033[0m')"
else
  BOLD=""
  GREEN=""
  RESET=""
fi

if [ -z "${NO_COLOR:-}" ] && [ -t 2 ]; then
  RED_ERR="$(printf '\033[31m')"
  YELLOW_ERR="$(printf '\033[33m')"
  RESET_ERR="$(printf '\033[0m')"
else
  RED_ERR=""
  YELLOW_ERR=""
  RESET_ERR=""
fi

usage() {
  cat <<'EOF'
Install the Fram CLI globally.

Usage:
  scripts/install.sh [--from PACKAGE_SPEC]

Examples:
  curl -LsSf https://fram.serhiifotex.dev/install.sh | sh
  scripts/install.sh
  scripts/install.sh --from git+https://github.com/Sergio-prog/fram.git
  FRAM_PACKAGE_SPEC=git+https://github.com/Sergio-prog/fram.git scripts/install.sh

The installer prefers uv tool install, then pipx. Python 3.11+ and FFmpeg are required.
EOF
}

fail() {
  printf '%serror:%s %s\n' "$RED_ERR" "$RESET_ERR" "$1" >&2
  exit 1
}

warn() {
  printf '%swarning:%s %s\n' "$YELLOW_ERR" "$RESET_ERR" "$1" >&2
}

info() {
  printf '%s\n' "$1"
}

success() {
  printf '%s%s%s\n' "$GREEN" "$1" "$RESET"
}

has_command() {
  command -v "$1" >/dev/null 2>&1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --from)
      [ "$#" -ge 2 ] || fail "--from requires a package spec"
      PACKAGE_SPEC="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

if ! has_command ffmpeg; then
  warn "ffmpeg was not found on PATH."
  cat >&2 <<'EOF'
Fram can install, but media processing will fail until FFmpeg is installed.

macOS:
  brew install ffmpeg

Debian/Ubuntu:
  sudo apt-get install ffmpeg
EOF
fi

if has_command uv; then
  info "${BOLD}Installing $CLI_NAME with uv tool install${RESET}"
  info "Source: $PACKAGE_SPEC"
  uv tool install --force "$PACKAGE_SPEC"
elif has_command pipx; then
  info "${BOLD}Installing $CLI_NAME with pipx${RESET}"
  info "Source: $PACKAGE_SPEC"
  pipx install --force "$PACKAGE_SPEC"
else
  fail "install uv or pipx first, then rerun this script"
fi

if has_command "$CLI_NAME"; then
  "$CLI_NAME" --help >/dev/null
  success "$CLI_NAME installed successfully."
else
  warn "$CLI_NAME was installed, but it is not on PATH yet."
  cat >&2 <<EOF
Add your tool bin directory to PATH, then run:
  $CLI_NAME --help
EOF
fi
