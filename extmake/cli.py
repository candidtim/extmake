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


@edit.group()
def cache():
    pass


@cache.command()
def clear():
    if click.confirm("Are you sure you want to clear all cache?"):
        clear_cache()
