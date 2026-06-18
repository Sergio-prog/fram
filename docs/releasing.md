# Releasing

Fram can be distributed through PyPI, the install script, and a Homebrew tap. The CLI is the primary release target.

## Prerequisites

- Python 3.11+
- `uv`
- FFmpeg for local media smoke tests
- A PyPI project named `fram`
- A Homebrew tap, for example `Sergio-prog/homebrew-fram`

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

After a PyPI release, the script can be pointed at the PyPI package:

```bash
FRAM_PACKAGE_SPEC=fram scripts/install.sh
```

## Hosting install.sh

The install endpoint can be a plain static file. It should serve the current `scripts/install.sh` over HTTPS.

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
}
```

Deploy the file:

```bash
sudo mkdir -p /srv/fram
sudo cp scripts/install.sh /srv/fram/install.sh
sudo chmod 0644 /srv/fram/install.sh
```

Smoke test:

```bash
curl -LsSf https://fram.serhiifotex.dev/install.sh | sh -s -- --help
```

For automatic deploys, add a small release job or server-side pull script that copies `scripts/install.sh` from the tagged release. Keep the endpoint boring: static file, HTTPS, short cache, no server-side logic.

## Homebrew

Homebrew is useful for macOS because the formula can declare FFmpeg as a required dependency.

The formula template lives at:

```text
packaging/homebrew/Formula/fram.rb
```

Release flow:

1. Publish the PyPI package.
2. Download or inspect the PyPI source distribution hash.
3. Replace `REPLACE_WITH_PYPI_SDIST_SHA256` in the formula.
4. Copy the formula to the tap repository, usually `Formula/fram.rb`.
5. Run Homebrew's Python resource generator inside the tap:

```bash
brew update-python-resources Formula/fram.rb
```

6. Test the formula locally:

```bash
brew install --build-from-source ./Formula/fram.rb
brew test fram
```

Expected user install:

```bash
brew tap Sergio-prog/fram
brew install fram
```

If the tap repository is named `homebrew-fram`, users still run `brew tap Sergio-prog/fram`; Homebrew strips the `homebrew-` prefix.
