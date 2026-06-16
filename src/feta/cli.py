from __future__ import annotations

import argparse
import importlib.metadata
import pathlib
import re
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


def cmd_zip(args: argparse.Namespace) -> int:
    try:
        feta.files.zip_directory(
            target=pathlib.Path(args.target),
            select=args.select,
            exclude=args.exclude,
        )
        return SUCCESS
    except Exception as e:
        print(f"error: {e}")
        return FAILURE


def _add_argument__select_exclude(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--select",
        help="regex pattern to include paths, matches full file path",
        default="",
    )
    parser.add_argument(
        "--exclude",
        help="regex pattern to exclude paths, matches full file path",
        default="^$",
    )


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

    parser__read = subparsers.add_parser("read")
    parser__read.add_argument("filenames", nargs="+")

    parser__zip = subparsers.add_parser("zip")
    parser__zip.add_argument("target")
    _add_argument__select_exclude(parser__zip)

    args = parser.parse_args(argv)
    if args.command == "read":
        return cmd_read(args)
    if args.command == "zip":
        return cmd_zip(args)

    parser.print_help()
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
