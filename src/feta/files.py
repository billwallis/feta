import csv
import json
import pathlib
import re
import zipfile
from collections.abc import Generator
from typing import Any, assert_never

HERE = pathlib.Path(__file__).resolve().parent
FILE_ENCODING = "utf-8"
CSV_DELIMITER = ","
CSV_QUOTE_CHAR = '"'
ZIP_DEFAULT_EXCLUDES = [
    r".*__pycache__/.*",
    r".*.venv/.*",
]

def _read_lines_from_csv(path: pathlib.Path) -> Generator:
    with open(path, "r", encoding=FILE_ENCODING) as f:
        reader = csv.reader(
            f.readlines(),
            delimiter=CSV_DELIMITER,
            quotechar=CSV_QUOTE_CHAR,
        )
        for line in reader:
            yield line


def read_csv(path: pathlib.Path, max_rows: int = -1) -> Generator:
    content = _read_lines_from_csv(path)
    headers, data = next(content), content
    col_len, i = len(headers), 0
    yield headers
    for row in data:
        i += 1
        if len(row) != col_len:
            raise AssertionError(
                f"Expected {col_len} columns, found {len(row)} on line {i}"
            )

        yield row

        if max_rows != -1 and i >= max_rows:
            break


def csv_to_json(csv_data: list[tuple]) -> list[dict[str, Any]]:
    header, *data = csv_data
    return [
        {k: v for k, v in zip(header, row, strict=True)}
        for row in data
    ]


def write_json(data: Any, path: pathlib.Path) -> None:
    with open(path, "w+", encoding=FILE_ENCODING) as f:
        json.dump(data, f, indent=2)


# def _filter_paths(
#     paths: list[pathlib.Path],
#     select: str,
#     exclude: str,
# ) -> list[pathlib.Path]:
#     return [
#         path
#         for path in paths
#         if (1 == 1
#             and re.match(select, str(path))
#             and not re.match(exclude, str(path))
#         )
#     ]


def zip_directory(target: pathlib.Path, select: str, exclude: str) -> zipfile.ZipFile:
    target = target.resolve()  # TODO: Does this change the original ref too?
    if not target.is_dir():
        raise ValueError(f"'{target}' is not a directory")

    def walk(path: pathlib.Path) -> Generator[pathlib.Path]:
        # If the path is a file...
        if path.is_file():
            # ...and matches the inclusion filters
            if (1 == 1
                and re.match(select, str(path))
                and not re.match(exclude, str(path))
                and not any(re.match(e, str(path)) for e in ZIP_DEFAULT_EXCLUDES)
            ):
                # ...then yield the path
                yield path.resolve()
        # ...else, walk dirs
        elif path.is_dir():
            try:
                children = path.iterdir()
            except PermissionError:  # pragma: no cover
                return

            for child in children:
                yield from walk(child)
        else:
            raise NotImplementedError()  #  pragma: no cover

    # TODO: Make this atomic
    archive = pathlib.Path(f"{target}.zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zipf:
        # `list(...)` to make sure we can walk the dir before taking any action
        for file in list(walk(target)):
            zipf.write(
                filename=file,
                arcname=file.relative_to(target),
            )

    return zipf
