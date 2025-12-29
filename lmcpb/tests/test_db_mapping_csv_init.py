import csv
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import pytest
import yaml

from lmcrec.playback.commands.lmcrec_export import LmcrecDbMapping


@dataclass
class LmcrecDbMappingCsvInitTestCase:
    name: str = ""
    description: str = ""
    db_mapping: str = ""
    expect_dialect_params: Optional[Union[csv.Dialect, Dict[str, Any]]] = None
    expect_csv_include_header: Optional[bool] = None
    expect_csv_max_rows_per_file: Optional[int] = None


test_cases = [
    LmcrecDbMappingCsvInitTestCase(
        name="BuiltinDefault",
        expect_dialect_params=csv.get_dialect("unix"),
        expect_csv_include_header=True,
        expect_csv_max_rows_per_file=10000,
    ),
    LmcrecDbMappingCsvInitTestCase(
        name="ExcelDialect",
        db_mapping=r"""
        csv:
            dialect: excel
        """,
        expect_dialect_params=csv.get_dialect("excel"),
    ),
    LmcrecDbMappingCsvInitTestCase(
        name="CustomDialect",
        db_mapping=r"""
        csv:
            dialect_params:
                delimiter: "%"
                doublequote: false
                escapechar: "\x0e"
                lineterminator: "\r\n"
                quotechar: "'"
                quoting: minimal
        """,
        expect_dialect_params=dict(
            delimiter="%",
            doublequote=False,
            escapechar="\x0e",
            lineterminator="\r\n",
            quotechar="'",
            quoting=csv.QUOTE_MINIMAL,
        ),
    ),
    LmcrecDbMappingCsvInitTestCase(
        name="HeaderAndMaxLines",
        db_mapping=r"""
        csv:
            include_header: false
            max_rows_per_file: 1234

        """,
        expect_csv_include_header=False,
        expect_csv_max_rows_per_file=1234,
    ),
]


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_lmcrec_db_mapping_csv_init(tc: LmcrecDbMappingCsvInitTestCase):
    lmcrec_db_mapping = LmcrecDbMapping(dict(), yaml.safe_load(tc.db_mapping))
    csv_dialect = lmcrec_db_mapping.csv_dialect
    expect_dialect_params = tc.expect_dialect_params
    if isinstance(expect_dialect_params, csv.Dialect):
        for attr in expect_dialect_params.__dir__():
            if not attr.startswith("_"):
                assert getattr(csv_dialect, attr) == getattr(
                    expect_dialect_params, attr
                )
    elif isinstance(expect_dialect_params, dict):
        for param, expect_val in expect_dialect_params.items():
            assert getattr(csv_dialect, param) == expect_val, param
    if tc.expect_csv_include_header is not None:
        assert lmcrec_db_mapping.csv_include_header == tc.expect_csv_include_header
    if tc.expect_csv_max_rows_per_file is not None:
        assert (
            lmcrec_db_mapping.csv_max_rows_per_file == tc.expect_csv_max_rows_per_file
        )
