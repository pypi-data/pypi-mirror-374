#!/usr/bin/env python3
"""
Command-line interface for KiCad Library Manager
"""

import click

from . import __version__
from .commands.add_3d import add_3d
from .commands.add_hook import add_hook
from .commands.config import config
from .commands.init import init
from .commands.list_libraries import list_cmd
from .commands.pin import pin
from .commands.setup import setup
from .commands.status import status
from .commands.template import template
from .commands.unpin import unpin
from .commands.update import update


@click.group()
@click.version_option(version=__version__)
def main():
    """KiCad Library Manager - Manage KiCad libraries

    This tool helps configure and manage KiCad libraries across your projects.
    """
    pass


# Register commands
main.add_command(setup)
main.add_command(list_cmd, name="list")
main.add_command(status)
main.add_command(pin)
main.add_command(unpin)
main.add_command(init)
main.add_command(add_3d)
main.add_command(config)
main.add_command(update)
main.add_command(add_hook, name="add-hook")
main.add_command(template)


if __name__ == "__main__":
    main()
