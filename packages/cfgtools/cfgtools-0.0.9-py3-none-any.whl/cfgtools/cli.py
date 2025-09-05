"""
Contains the cli api of cfgtools.

NOTE: this module is private. All functions and objects are available in the main
`cfgtools` namespace - use that instead.

"""

import click

from .core import read


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("filename")
def run(filename: str) -> None:
    """Run command."""
    print(read(filename))
