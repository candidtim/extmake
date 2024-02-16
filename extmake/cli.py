import shutil
import sys

import click

from .proxy import run_make
from .resolver import clear_cache, resolve_makefile


# extmake main entry point
# passes the arguments as-is
def main(args=sys.argv[1:]):
    resolved_path = resolve_makefile()
    run_make(resolved_path, args)


@click.group()
def edit():
    pass


@edit.command(help="Print the resolved Makefile")
def print():
    resolved_path = resolve_makefile()
    click.echo_via_pager(resolved_path.read_text())


@edit.command(help="Overwrite the Makefile with the resolved content")
@click.confirmation_option(prompt="Are you sure you want to eject?")
def eject():
    resolved_path = resolve_makefile()
    if resolved_path.is_file():
        shutil.copyfile(resolve_makefile(), "Makefile")
    else:
        click.echo("Makefile not found")
        sys.exit(2)


@edit.group(help="Cache management")
def cache():
    pass


@cache.command(help="Clear all cache")
@click.confirmation_option(prompt="Are you sure you want to clear all cache?")
def clear():
    clear_cache()
