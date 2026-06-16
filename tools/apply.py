#!/usr/bin/env python

import argparse
import dataclasses
import logging
import pathlib
import re
import shutil
from collections.abc import Sequence

SUCCESS = 0
FAILURE = 1
ROOT = pathlib.Path(__file__).resolve().parent.parent
THIS_REPO_NAME = "python-template"
FILES_TO_COPY = [
    ".github/workflows/tests.yaml",
    ".gitignore",
    ".pre-commit-config.yaml",
    "LICENSE",
    "pyproject.toml",
    "README.md",
]


@dataclasses.dataclass
class Context:
    dry_run: bool | None
    target_repo: pathlib.Path | None


def _select_files(
    files: list[str],
    include: list[str],
    exclude: list[str],
) -> list[str]:
    return [
        file
        for file in files
        if any(re.match(i, file) for i in include)
        and not all(re.match(e, file) for e in exclude)
    ]


def _apply_template(target: pathlib.Path, context: Context) -> None:
    # Right now, this just replaces `python-template` with the name of the
    # target repo, but this could be extended to, say, apply Jinja templates
    assert context.target_repo is not None  # noqa: S101
    target.write_text(
        (
            target.read_text(encoding="utf-8").replace(
                THIS_REPO_NAME, context.target_repo.name
            )
        ),
        encoding="utf-8",
    )


def _copy_file_to_target(
    source: pathlib.Path,
    destination: pathlib.Path,
    context: Context,
) -> None:
    if context.dry_run:
        print(f"Copying '{source}' to '{destination}")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        # This is not atomic: it copies, then modifies. For atomicity, we should
        # modify in transit or modify a temporary intermediate file
        shutil.copy(source, destination)
        _apply_template(destination, context)


def copy_files_to_target(
    target: pathlib.Path,
    files: list[str],
    dry_run: bool,
) -> int:
    if not target.exists():
        logging.error(f"target {target} does not exist")
        return FAILURE
    if not target.is_dir():
        logging.error(f"target {target} is not a directory")
        return FAILURE

    ret = SUCCESS
    for file in files:
        try:
            _copy_file_to_target(
                source=ROOT / file,
                destination=target / file,
                context=Context(
                    dry_run=dry_run,
                    target_repo=target,
                ),
            )
        except Exception as e:
            logging.error(str(e))
            ret = FAILURE

    return ret


def main(argv: Sequence[str] | None = None) -> int:
    """
    Parse the arguments and run the command.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("targets", nargs="*")
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument("--include", nargs="*", default=[".*"])
    parser.add_argument("--exclude", nargs="*", default=["^$"])

    args = parser.parse_args(argv)
    ret = SUCCESS
    if not args.targets:
        parser.print_help()
    for target in args.targets:
        ret |= copy_files_to_target(
            target=pathlib.Path(target).resolve(),
            files=_select_files(FILES_TO_COPY, args.include, args.exclude),
            dry_run=args.dry_run,
        )

    return ret


if __name__ == "__main__":
    # python -m tools.apply <target>
    raise SystemExit(main())
