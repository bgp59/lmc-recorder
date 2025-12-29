import time
from dataclasses import dataclass, field
from typing import List, Tuple

import pytest
import yaml
from tzlocal import get_localzone

from lmcrec.playback.commands.lmcrec_export import LmcrecDbMapping

# pytest collect somehow sets the timezone to UTC, the next call is a hack to
# restore it:
get_localzone()


@dataclass
class LmcrecDbTimestampMappingTestCase:
    name: str = ""
    description: str = ""
    db_mapping: str = ""
    expect_timestamps: List[Tuple[float, str]] = field(default_factory=list)


test_cases = [
    LmcrecDbTimestampMappingTestCase(
        name="LocaltimeMappingSec",
        db_mapping="""
            timestamp_col:
                name: lmcrec_ts
                col_type: datetime
                strftime: "%d %b, %Y %I:%M:%S%p"
        """,
        expect_timestamps=[
            (100000, time.strftime("%d %b, %Y %I:%M:%S%p", time.localtime(100000))),
        ],
    ),
    LmcrecDbTimestampMappingTestCase(
        name="LocaltimeMappingMicrosec",
        db_mapping="""
            timestamp_col:
                name: lmcrec_ts
                col_type: datetime
                strftime: "%Y-%m-%d %H:%M:%S.%f"
        """,
        expect_timestamps=[
            (
                100.123,
                time.strftime("%Y-%m-%d %H:%M:%S.123000", time.localtime(100.123)),
            ),
            (100, time.strftime("%Y-%m-%d %H:%M:%S.000000", time.localtime(100))),
        ],
    ),
    LmcrecDbTimestampMappingTestCase(
        name="GmtMappingSec",
        db_mapping="""
            timestamp_col:
                name: lmcrec_ts
                col_type: datetime
                strftime: "%d %b, %Y %I:%M:%S%p"
                use_gmt: true
        """,
        expect_timestamps=[
            (123456, time.strftime("%d %b, %Y %I:%M:%S%p", time.gmtime(123456))),
        ],
    ),
]


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_lmcrec_db_mapping_timestamp(tc: LmcrecDbTimestampMappingTestCase):
    lmcrec_db_mapping = LmcrecDbMapping(dict(), yaml.safe_load(tc.db_mapping))
    for ts, expect_val in tc.expect_timestamps:
        assert lmcrec_db_mapping.datetime_from_ts(ts) == expect_val
