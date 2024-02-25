import logging
import shutil
import sys
from pathlib import Path

import click

from . import cache, deps, proxy, resolver


def makefile_option(exists=True):
    return click.option(
        "-f",
        "--file",
        "--makefile",
        "makefile",
        type=click.Path(exists=exists, file_okay=True, dir_okay=False, path_type=Path),
        default="Makefile",
        show_default=True,
        help="Path to Makefile",
    )


def validate_makefile(path: Path):
    if not path.is_file():
        raise click.BadParameter(f"File {path} does not exist")


def verbose_option(with_short_flag=True):
    flags = ["-v", "--verbose"] if with_short_flag else ["--verbose"]
    return click.option(
        *flags,
        is_flag=True,
        default=False,
        expose_value=False,
        help="Enable verbose output",
        callback=lambda ctx, param, value: setup_logging(value),
    )


def print_header():
    click.echo("You are using ExtMake wrapper for make.")
    click.echo("See https://github.com/candidtim/extmake")


def setup_logging(verbose):
    if verbose:
        print_header()
    logging.basicConfig(
        format="%(message)s", level=logging.DEBUG if verbose else logging.INFO
    )


@click.command(
    context_settings={
        "ignore_unknown_options": True,
        "help_option_names": [],
    }
)
@makefile_option(exists=False)
@verbose_option(with_short_flag=False)
@click.option("-h", "--help", "show_help", is_flag=True, default=False)
@click.argument("make_args", nargs=-1, type=click.UNPROCESSED)
def main(makefile, show_help, make_args):
    if show_help:
        print_header()
        click.echo(
            "Original make help is below. "
            "More information about ExtMake follows after.\n"
        )
        proxy.run_make(makefile, args=["--help"])
        click.echo("\nAdditional options provided by ExtMake:")
        click.echo("  --verbose                   Enable verbose output")
    else:
        validate_makefile(makefile)
        resolved_path = resolver.resolve_makefile(makefile)
        result = proxy.run_make(resolved_path, make_args)
        sys.exit(result.returncode)


@click.group()
def edit():
    pass


@edit.command("print", help="Print the resolved Makefile")
@makefile_option()
@verbose_option()
def _print(makefile):
    resolved_path = resolver.resolve_makefile(makefile)
    click.echo_via_pager(resolved_path.read_text())


@edit.command(help="Overwrite the Makefile with the resolved content")
@click.confirmation_option(prompt="Are you sure you want to eject?")
@makefile_option()
@verbose_option()
def eject(makefile):
    resolved_path = resolver.resolve_makefile(makefile)
    shutil.copyfile(resolved_path, makefile)


@edit.command(help="Pull the new versions of the include files")
@makefile_option()
@verbose_option()
def update(makefile):
    resolver.clear_cache(makefile)  # FIXME: leaky resolver abstraction
    for spec in resolver.dependencies(makefile):
        deps.update(spec)


@edit.group("cache", help="Cache management")
def _cache():
    pass


@_cache.command(help="Show the location of the local cache directory")
def show():
    click.echo(cache.cache_root())


@_cache.command(help="Clear the cache")
@makefile_option(exists=False)
@verbose_option()
@click.confirmation_option(prompt="Are you sure you want to clear the cache?")
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
        validate_makefile(makefile)
        resolver.clear_cache(makefile)
        for spec in resolver.dependencies(makefile):
            deps.clear_cache(spec)
