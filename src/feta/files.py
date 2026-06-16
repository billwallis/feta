import csv
import json
import pathlib
from collections.abc import Generator
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
FILE_ENCODING = "utf-8"
CSV_DELIMITER = ","
CSV_QUOTE_CHAR = '"'


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
