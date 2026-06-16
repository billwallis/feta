from __future__ import annotations

import argparse
import importlib.metadata
import pathlib
from collections.abc import Sequence

import feta.files

SUCCESS = 0
FAILURE = 1


def _get_version() -> str:
    return f"%(prog)s {importlib.metadata.version('feta')}"


def cmd_read(args: argparse.Namespace) -> int:
    for filename in args.filenames:
        path = pathlib.Path(filename).resolve()
        if path.suffix == ".csv":
            for row in feta.files.read_csv(path):
                print(row)
        else:
            print(path.read_text(encoding="utf-8"), end="")

    return SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    """
    Parse the arguments and run the command.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=_get_version(),
    )
    subparsers = parser.add_subparsers(dest="command")

    parser__foo = subparsers.add_parser("read")
    parser__foo.add_argument("filenames", nargs="+")

    args = parser.parse_args(argv)
    if args.command == "read":
        return cmd_read(args)

    parser.print_help()
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
