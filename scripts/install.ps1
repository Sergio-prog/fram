[CmdletBinding()]
param(
    [Alias("h")]
    [switch]$Help,
    [Alias("From")]
    [string]$PackageSpec,
    [string]$CliName = $env:FRAM_CLI_NAME
)

$ErrorActionPreference = "Stop"

$DefaultPackageSpec = "git+https://github.com/Sergio-prog/fram.git"
if (-not $PackageSpec) {
    if ($env:FRAM_PACKAGE_SPEC) {
        $PackageSpec = $env:FRAM_PACKAGE_SPEC
    } elseif ((Test-Path "pyproject.toml") -and (Test-Path "fram" -PathType Container)) {
        $PackageSpec = "."
    } else {
        $PackageSpec = $DefaultPackageSpec
    }
}

if (-not $CliName) {
    $CliName = "fram"
}

$UseColor = -not $env:NO_COLOR -and -not [Console]::IsOutputRedirected

function Write-Styled {
    param(
        [string]$Message,
        [ConsoleColor]$Color = [ConsoleColor]::Gray,
        [switch]$NoNewline
    )

    if ($UseColor) {
        Write-Host $Message -ForegroundColor $Color -NoNewline:$NoNewline
    } else {
        Write-Host $Message -NoNewline:$NoNewline
    }
}

function Write-Step {
    param([string]$Message)
    Write-Styled $Message ([ConsoleColor]::White)
}

function Write-Success {
    param([string]$Message)
    Write-Styled "$([char]0x2713) $Message" ([ConsoleColor]::Green)
}

function Write-WarningLine {
    param([string]$Message)
    Write-Styled "warning:" ([ConsoleColor]::Yellow) -NoNewline
    Write-Host " $Message"
}

function Stop-Install {
    param([string]$Message)
    Write-Styled "error:" ([ConsoleColor]::Red) -NoNewline
    Write-Host " $Message"
    exit 1
}

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-ToolInstall {
    param(
        [string]$Tool,
        [string[]]$Arguments
    )

    & $Tool @Arguments
    if ($LASTEXITCODE -ne 0) {
        Stop-Install "$Tool failed with exit code $LASTEXITCODE"
    }
}

if ($Help) {
    @"
Install the Fram CLI globally.

Usage:
  powershell -ExecutionPolicy Bypass -File scripts/install.ps1 [-PackageSpec PACKAGE_SPEC]

Examples:
  powershell -ExecutionPolicy Bypass -c "irm https://fram.serhiifotex.dev/install.ps1 | iex"
  powershell -ExecutionPolicy Bypass -File scripts/install.ps1
  powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -PackageSpec git+https://github.com/Sergio-prog/fram.git
  `$env:FRAM_PACKAGE_SPEC = "git+https://github.com/Sergio-prog/fram.git"; irm https://fram.serhiifotex.dev/install.ps1 | iex

The installer prefers uv tool install, then pipx. Python 3.11+ and FFmpeg are required.
"@
    exit 0
}

if (-not (Test-Command "ffmpeg")) {
    Write-WarningLine "ffmpeg was not found on PATH."
    @"
Fram can install, but media processing will fail until FFmpeg is installed.

Windows:
  winget install Gyan.FFmpeg
  choco install ffmpeg
"@
}

if (Test-Command "uv") {
    Write-Step "Installing $CliName with uv tool install"
    Write-Host "Source: $PackageSpec"
    Invoke-ToolInstall "uv" @("tool", "install", "--force", $PackageSpec)
} elseif (Test-Command "pipx") {
    Write-Step "Installing $CliName with pipx"
    Write-Host "Source: $PackageSpec"
    Invoke-ToolInstall "pipx" @("install", "--force", $PackageSpec)
} else {
    Stop-Install "install uv or pipx first, then rerun this script"
}

if (Test-Command $CliName) {
    & $CliName --help *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "$CliName installed successfully."
    } else {
        Write-WarningLine "$CliName is on PATH, but '$CliName --help' failed."
    }
} else {
    Write-WarningLine "$CliName was installed, but it is not on PATH yet."
    @"
Add your Python tool bin directory to PATH, then run:
  $CliName --help
"@
}
