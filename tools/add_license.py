"""
Add a LICENSE file to the specified repos.

Note intended to be reused: just kept for posterity.
"""

import argparse
import pathlib
import shutil
import subprocess
import textwrap
import webbrowser
from collections.abc import Iterable, Sequence

FEATURE_BRANCH = "add-license"
COMMIT_MESSAGE = "feat: add license"
NEW_PR_LINK = r"https://github.com/billwallis/{repository}/pull/new/{branch}"
# ruff: noqa: E101
EXPECTED_GIT_STATUS = textwrap.dedent(
    """\
    On branch add-license
    Untracked files:
      (use "git add <file>..." to include in what will be committed)
    	LICENSE

    nothing added to commit but untracked files present (use "git add" to track)
    """
).rstrip()
HERE = pathlib.Path(__file__).parent
assert HERE.parent.name == "python-template"  # noqa: S101
LICENSE_FILE = HERE.parent / "LICENSE"


def git(
    args: Iterable[str],
    git_dir: pathlib.Path,
) -> str:
    proc = subprocess.run(
        args=("git", "-C", git_dir, *args),
        check=False,  # DON'T raise an exception on non-zero return codes
        capture_output=True,
    )

    assert isinstance(proc.stdout, bytes)  # noqa: S101
    assert isinstance(proc.stderr, bytes)  # noqa: S101

    out = proc.stdout.decode().rstrip()
    err = proc.stderr.decode().rstrip()

    if proc.returncode != 0:
        raise RuntimeError(f"exit code {proc.returncode}:\n{err}")

    return out


def _checkout_branch(
    repository: pathlib.Path,
    branch: str,
    create: bool = False,
) -> None:
    args = ("-c", branch) if create else (branch,)
    git(("switch", *args), git_dir=repository)


def _delete_branch(repository: pathlib.Path, branch: str) -> None:
    git(("branch", "--delete", branch), git_dir=repository)


def _push_current_branch(repository: pathlib.Path) -> None:
    git(("push",), git_dir=repository)


def _add_license_file(repository: pathlib.Path) -> None:
    shutil.copy(
        src=LICENSE_FILE,
        dst=repository / LICENSE_FILE.name,
    )
    out = git(("status",), git_dir=repository)

    assert out == EXPECTED_GIT_STATUS, f"`{out}`\n!=\n`{EXPECTED_GIT_STATUS}`"  # noqa: S101


def _commit_license_file(repository: pathlib.Path) -> None:
    git(("add", LICENSE_FILE.name), git_dir=repository)
    git(("commit", "-m", COMMIT_MESSAGE), git_dir=repository)


def _open_pull_request(repository: pathlib.Path) -> None:
    webbrowser.open(
        NEW_PR_LINK.format(
            repository=repository.name,
            branch=FEATURE_BRANCH,
        )
    )


def add_license(repository: pathlib.Path) -> int:
    print(f"Adding license to '{repository}'")
    if not repository.exists():
        print(f"\tRepo does not exist at {repository}")
        return 1

    # gross and lazy massive try block
    try:
        print("\tCheckout feature branch")
        _checkout_branch(repository, FEATURE_BRANCH, create=True)
        print("\tAdd licence file")
        _add_license_file(repository)
        print("\tCommit licence file")
        _commit_license_file(repository)
        print("\tPush changes")
        _push_current_branch(repository)
        print("\tOpen pull request")
        _open_pull_request(repository)
        print("\tCheckout main branch")
        _checkout_branch(repository, "main")
        print("\tDelete feature branch")
        _delete_branch(repository, FEATURE_BRANCH)
        return 0
    except RuntimeError as e:
        print(e)
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    """
    Parse the arguments and run the hook.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("repositories", nargs="*")
    args = parser.parse_args(argv)

    outcome = 0
    for repository in args.repositories:
        outcome |= add_license(pathlib.Path(repository).resolve())
    return outcome


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
