from dataclasses import dataclass
from typing import Any, Iterable, List, Optional
from unittest.mock import call, patch

import pytest

from lmcrec.playback.commands.lmcrec_export import CsvExportWriter

DUMMY_OUT_DIR = "test_csv_export_writer"
CSV_DIALECT = "excel"


@dataclass
class CsvExportWriterTestCase:
    name: str = ""
    description: str = ""
    max_rows_per_file: int = 0
    header: Optional[Iterable[str]] = None
    rows: Optional[Iterable[Any]] = None
    close: bool = False
    expect_calls: Optional[List[Any]] = None


test_cases = [
    CsvExportWriterTestCase(
        name="OW",
        description="open, write; no header",
        rows=[
            ("col1", 1, True),
        ],
        expect_calls=[
            call(f"{DUMMY_OUT_DIR}/batch.csv", mode="wt"),
            call().write("col1,1,True\r\n"),
        ],
    ),
    CsvExportWriterTestCase(
        name="OWWCOW",
        description="open, write, write, close, open write; no header",
        max_rows_per_file=2,
        rows=[
            ("col1", 1, True),
            ("col2", 2, False),
            ("col21", 21, True),
        ],
        expect_calls=[
            call(f"{DUMMY_OUT_DIR}/batch-000000.csv", mode="wt"),
            call().write("col1,1,True\r\n"),
            call().write("col2,2,False\r\n"),
            call().close(),
            call(f"{DUMMY_OUT_DIR}/batch-000001.csv", mode="wt"),
            call().write("col21,21,True\r\n"),
        ],
    ),
    CsvExportWriterTestCase(
        name="OHW",
        description="open, write (header), write",
        header=("Hdr1", "Hdr2", "Hdr3"),
        rows=[
            ("col1", 1, True),
        ],
        expect_calls=[
            call(f"{DUMMY_OUT_DIR}/batch.csv", mode="wt"),
            call().write("Hdr1,Hdr2,Hdr3\r\n"),
            call().write("col1,1,True\r\n"),
        ],
    ),
    CsvExportWriterTestCase(
        name="OHWC",
        description="open, write (header), write, close",
        header=("Hdr1", "Hdr2", "Hdr3"),
        rows=[
            ("col1", 1, True),
        ],
        close=True,
        expect_calls=[
            call(f"{DUMMY_OUT_DIR}/batch.csv", mode="wt"),
            call().write("Hdr1,Hdr2,Hdr3\r\n"),
            call().write("col1,1,True\r\n"),
            call().close(),
        ],
    ),
]


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_csv_export_writer(tc: CsvExportWriterTestCase):
    with (
        patch("lmcrec.playback.commands.lmcrec_export.os.makedirs"),
        patch("lmcrec.playback.commands.lmcrec_export.open") as open_mock,
    ):
        csv_writer = CsvExportWriter(
            DUMMY_OUT_DIR,
            CSV_DIALECT,
            header=tc.header,
            max_rows_per_file=tc.max_rows_per_file,
        )
        for row in tc.rows:
            csv_writer.write(row)
        if tc.close:
            csv_writer.close()
        if tc.expect_calls:
            open_mock.assert_has_calls(tc.expect_calls)
