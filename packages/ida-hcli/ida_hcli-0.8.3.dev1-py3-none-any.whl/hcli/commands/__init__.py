from __future__ import annotations

import rich_click as click


def register_commands(cli: click.Group) -> None:
    """Register all commands to the CLI group."""
    from .commands import commands
    from .download import download
    from .login import login
    from .logout import logout
    from .open import open_url
    from .setup import setup
    from .update import update
    from .whoami import whoami
    # placeholder for more commands

    cli.add_command(login)
    cli.add_command(logout)
    cli.add_command(setup)
    cli.add_command(whoami)
    cli.add_command(update)
    cli.add_command(download)
    cli.add_command(commands)
    cli.add_command(open_url)

    # groups
    from .auth import auth
    from .extension import extension
    from .ida import ida
    from .license import license
    from .share import share

    cli.add_command(auth)
    cli.add_command(ida)
    cli.add_command(share)
    cli.add_command(license)
    cli.add_command(extension)
