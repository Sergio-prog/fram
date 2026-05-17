import asyncio

from fram.cli.interactive.app import FramInteractiveApp


def test_interactive_app_mounts() -> None:
    asyncio.run(_mount_app())


async def _mount_app() -> None:
    app = FramInteractiveApp()

    async with app.run_test():
        pass
