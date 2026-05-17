import subprocess

from fram.core.errors import ProcessingFailed


def run_command(args: list[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Command failed."
        raise ProcessingFailed(message)


def run_capture(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Command failed."
        raise ProcessingFailed(message)
    return result.stdout.strip()

