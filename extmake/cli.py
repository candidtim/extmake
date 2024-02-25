import shutil
import sys
from pathlib import Path

import click

from . import cache
from .proxy import run_make
from .resolver import clear_cache, resolve_makefile, update_cache

makefile_option = click.option(
    "-f",
    "--file",
    "--makefile",
    "makefile",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default="Makefile",
    show_default=True,
    help="Path to Makefile",
)


@click.command(
    context_settings={
        "ignore_unknown_options": True,
        "help_option_names": [],
    }
)
@makefile_option
@click.option("-h", "--help", "show_help", is_flag=True, default=False)
@click.argument("make_args", nargs=-1, type=click.UNPROCESSED)
def main(makefile, show_help, make_args):
    if show_help:
        click.echo("You are using ExtMake wrapper for make.")
        click.echo("See https://github.com/candidtim/extmake")
        click.echo("Original make help is below.")
        click.echo()
        make_args = ["--help"]
    resolved_path = resolve_makefile(makefile)
    result = run_make(resolved_path, make_args)
    sys.exit(result.returncode)


@click.group()
def edit():
    pass


@edit.command("print", help="Print the resolved Makefile")
@makefile_option
def _print(makefile):
    resolved_path = resolve_makefile(makefile)
    click.echo_via_pager(resolved_path.read_text())


@edit.command(help="Overwrite the Makefile with the resolved content")
@click.confirmation_option(prompt="Are you sure you want to eject?")
@makefile_option
def eject(makefile):
    resolved_path = resolve_makefile(makefile)
    shutil.copyfile(resolved_path, makefile)


@edit.command(help="Pull the new versions of the include files")
@makefile_option
def update(makefile):
    update_cache(makefile)


@edit.group(help="Cache management")
def _cache():
    pass


@_cache.command(help="Show the location of the local cache directory")
def show():
    click.echo(cache.cache_root())


@_cache.command(help="Clear the cache")
@click.confirmation_option(prompt="Are you sure you want to clear the cache?")
@makefile_option
@click.option(
    "--all",
    "clear_all",
    is_flag=True,
    default=False,
    help="Delete all cached files",
)
def clear(clear_all, makefile):
    if clear_all:
        cache.clear_all()
    else:
        clear_cache(makefile)
