import sys

from .proxy import run_make
from .resolver import resolve_makefile


def main(args=sys.argv[1:]):
    resolved_path = resolve_makefile()
    run_make(resolved_path, args)


if __name__ == "__main__":
    main()
