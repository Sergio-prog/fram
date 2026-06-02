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

usage() {
  cat <<'EOF'
Install the Fram CLI globally.

Usage:
  scripts/install.sh [--from PACKAGE_SPEC]

Examples:
  curl -LsSf https://raw.githubusercontent.com/Sergio-prog/fram/main/scripts/install.sh | sh
  scripts/install.sh
  scripts/install.sh --from git+https://github.com/Sergio-prog/fram.git
  FRAM_PACKAGE_SPEC=git+https://github.com/Sergio-prog/fram.git scripts/install.sh

The installer prefers uv tool install, then pipx. Python 3.11+ and FFmpeg are required.
EOF
}

fail() {
  printf 'error: %s\n' "$1" >&2
  exit 1
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
  cat >&2 <<'EOF'
warning: ffmpeg was not found on PATH.
Fram can install, but media processing will fail until FFmpeg is installed.

macOS:
  brew install ffmpeg

Debian/Ubuntu:
  sudo apt-get install ffmpeg
EOF
fi

if has_command uv; then
  printf 'Installing %s with uv tool install from %s\n' "$CLI_NAME" "$PACKAGE_SPEC"
  uv tool install --force "$PACKAGE_SPEC"
elif has_command pipx; then
  printf 'Installing %s with pipx from %s\n' "$CLI_NAME" "$PACKAGE_SPEC"
  pipx install --force "$PACKAGE_SPEC"
else
  fail "install uv or pipx first, then rerun this script"
fi

if has_command "$CLI_NAME"; then
  "$CLI_NAME" --help >/dev/null
  printf '%s installed successfully.\n' "$CLI_NAME"
else
  cat >&2 <<EOF
warning: $CLI_NAME was installed, but it is not on PATH yet.
Add your tool bin directory to PATH, then run:
  $CLI_NAME --help
EOF
fi
