import pathlib
import textwrap
import zipfile
from typing import Any

import pytest

from feta import files


@pytest.fixture
def csv_file(tmp_path: pathlib.Path) -> pathlib.Path:
    path = tmp_path / "fixture.csv"
    path.write_text(
        data=textwrap.dedent(
            """\
            a,b,c,d
            1,foo,true,2026-01-01
            2,bar,false,2026-01-02
            3,"baz qux",,
            """
        ),
        encoding="utf-8",
        newline="\n",
    )

    return path


@pytest.fixture
def json_file(tmp_path: pathlib.Path) -> pathlib.Path:
    path = tmp_path / "fixture.json"
    path.write_text(
        data=textwrap.dedent(
            """\
            [
              {
                "a": "1",
                "b": "foo",
                "c": "true",
                "d": "2026-01-01"
              },
              {
                "a": "2",
                "b": "bar",
                "c": "false",
                "d": "2026-01-02"
              },
              {
                "a": "3",
                "b": "baz qux",
                "c": "",
                "d": ""
              }
            ]
            """.rstrip()
        ),
        encoding="utf-8",
        newline="\n",
    )

    return path


@pytest.fixture
def dict_data() -> list[dict[str, Any]]:
    return [
        {
            "a": "1",
            "b": "foo",
            "c": "true",
            "d": "2026-01-01",
        },
        {
            "a": "2",
            "b": "bar",
            "c": "false",
            "d": "2026-01-02",
        },
        {
            "a": "3",
            "b": "baz qux",
            "c": "",
            "d": "",
        },
    ]


def test__read_csv__happy_path(
    csv_file: pathlib.Path,
):
    assert list(files.read_csv(csv_file)) == [
        ["a", "b", "c", "d"],
        ["1", "foo", "true", "2026-01-01"],
        ["2", "bar", "false", "2026-01-02"],
        ["3", "baz qux", "", ""],
    ]


def test__read_csv__max_rows_limits_reading(
    csv_file: pathlib.Path,
):
    assert list(files.read_csv(csv_file, max_rows=1)) == [
        ["a", "b", "c", "d"],
        ["1", "foo", "true", "2026-01-01"],
    ]


def test__csv_to_json__happy_path(
    csv_file: pathlib.Path,
    dict_data: list[dict[str, Any]],
):
    assert files.csv_to_json(list(files.read_csv(csv_file))) == dict_data


def test__write_json__happy_path(
    tmp_path: pathlib.Path,
    json_file: pathlib.Path,
    dict_data: list[dict[str, Any]],
):
    target = tmp_path / "target.json"
    files.write_json(dict_data, target)

    assert target.read_text() == json_file.read_text()


@pytest.mark.parametrize(
    "select, exclude, expected",
    [
        ("", "^$", ["baz.json", "bar.txt", "foo.py"]),
        (".*(baz.json|foo.py)$", "^$", ["baz.json", "foo.py"]),
        ("", ".*.json$", ["bar.txt", "foo.py"]),
        (".*ba[rz].*", ".*.txt$", ["baz.json"]),
    ],
)
def test__zip__happy_path(
    tmp_path: pathlib.Path,
    select: str,
    exclude: str,
    expected: list[str],
):
    target = tmp_path / "target"
    target.mkdir(parents=True)
    (target / "foo.py").touch()
    (target / "bar.txt").touch()
    (target / "baz.json").touch()

    archive = files.zip_directory(target, select=select, exclude=exclude)
    assert sorted(archive.namelist()) == sorted(expected)


def test__zip__fails_on_non_directory():
    with pytest.raises(ValueError):
        files.zip_directory(
            target=pathlib.Path(__file__),
            select="",
            exclude="^$",
        )
