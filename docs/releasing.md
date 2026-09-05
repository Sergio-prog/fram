# Releasing

Fram can be distributed through PyPI, the install script, and a Homebrew tap. The CLI is the primary release target.

## Prerequisites

- Python 3.11+
- `uv`
- FFmpeg for local media smoke tests
- A PyPI project named `fram`
- The Homebrew tap [Sergio-prog/homebrew-tap](https://github.com/Sergio-prog/homebrew-tap) and a `TAP_GITHUB_TOKEN` repository secret with push access to it

## PyPI

Build locally before cutting a tag:

```bash
uv build
uv run --all-extras --group dev python -m pytest
uv run --all-extras --group dev ruff check .
```

The GitHub Actions publish workflow runs on version tags. It builds the package, creates a GitHub Release with generated notes and the `dist/` artifacts, then publishes to PyPI:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Configure PyPI trusted publishing for the GitHub repository and the `pypi` environment before pushing the first release tag. The workflow publishes the files from `dist/` without storing a PyPI token in the repository.

`fram update --check` and the lightweight command/TUI update notices read the latest GitHub Release, so every public release needs a `vX.Y.Z` GitHub Release. Set `FRAM_UPDATE_CHECK=0` to disable automatic checks locally.

After publishing, test the package in an isolated CLI environment:

```bash
uv tool install --force fram
fram --help
```

Equivalent `pipx` smoke test:

```bash
pipx install --force fram
fram --help
```

## Install Script

The install script supports both source installs and released package installs.

From the public install endpoint:

```bash
curl -LsSf https://fram.serhiifotex.dev/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://fram.serhiifotex.dev/install.ps1 | iex"
```

After a PyPI release, the script can be pointed at the PyPI package:

```bash
FRAM_PACKAGE_SPEC=fram scripts/install.sh
```

```powershell
$env:FRAM_PACKAGE_SPEC = "fram"; irm https://fram.serhiifotex.dev/install.ps1 | iex
```

## Hosting install scripts

The install endpoint can be a plain static file. It should serve the current
`scripts/install.sh` and `scripts/install.ps1` over HTTPS.

DNS:

```text
fram.serhiifotex.dev  A     <VPS_IPV4>
fram.serhiifotex.dev  AAAA  <VPS_IPV6>
```

Caddy example:

```caddyfile
fram.serhiifotex.dev {
  root * /srv/fram
  file_server

  header /install.sh Content-Type "text/x-shellscript; charset=utf-8"
  header /install.ps1 Content-Type "text/plain; charset=utf-8"
}
```

nginx example:

```nginx
server {
    listen 80;
    server_name fram.serhiifotex.dev;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name fram.serhiifotex.dev;

    root /srv/fram;

    location = /install.sh {
        default_type text/x-shellscript;
        add_header Cache-Control "public, max-age=300";
        try_files /install.sh =404;
    }

    location = /install.ps1 {
        default_type text/plain;
        add_header Cache-Control "public, max-age=300";
        try_files /install.ps1 =404;
    }
}
```

Deploy the file:

```bash
sudo mkdir -p /srv/fram
sudo cp scripts/install.sh /srv/fram/install.sh
sudo cp scripts/install.ps1 /srv/fram/install.ps1
sudo chmod 0644 /srv/fram/install.sh
sudo chmod 0644 /srv/fram/install.ps1
```

Smoke test:

```bash
curl -LsSf https://fram.serhiifotex.dev/install.sh | sh -s -- --help
```

```powershell
powershell -ExecutionPolicy Bypass -c "$script = irm https://fram.serhiifotex.dev/install.ps1; & ([scriptblock]::Create($script)) -Help"
```

For automatic deploys, add a small release job or server-side pull script that copies
`scripts/install.sh` and `scripts/install.ps1` from the tagged release. Keep the endpoint
boring: static file, HTTPS, short cache, no server-side logic.

## Homebrew

The formula lives in [Sergio-prog/homebrew-tap](https://github.com/Sergio-prog/homebrew-tap) as `Formula/fram.rb`. It builds from the GitHub tag tarball, so it does not depend on PyPI, and declares FFmpeg as a dependency.

The `homebrew` job in the publish workflow regenerates the formula on every version tag: it renders `packaging/homebrew/fram.rb.tmpl` with the tarball URL and sha256 via `scripts/update_tap_formula.py`, then commits `Formula/fram.rb` to the tap using `TAP_GITHUB_TOKEN`.

To update the tap manually:

```bash
python3 scripts/update_tap_formula.py 0.1.0 ../homebrew-tap/Formula/fram.rb
```

To test a formula before pushing, copy it into the local tap checkout and install from there (Homebrew refuses standalone formula files):

```bash
cp ../homebrew-tap/Formula/fram.rb "$(brew --repository sergio-prog/tap)/Formula/"
brew install --build-from-source sergio-prog/tap/fram
brew test sergio-prog/tap/fram
```

User install:

```bash
brew install sergio-prog/tap/fram
```
