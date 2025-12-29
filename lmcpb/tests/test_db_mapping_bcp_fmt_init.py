from dataclasses import dataclass
from typing import Optional

import pytest
import yaml

from lmcrec.playback.commands.lmcrec_export import LmcrecDbMapping


@dataclass
class LmcrecDbMappingBcpFmtInitTestCase:
    name: str = ""
    description: str = ""
    db_mapping: str = ""
    expect_bcp_version: str = ""
    expect_bcp_host_data_type: str = ""
    expect_bcp_host_data_length: int = 0
    expect_bcp_string_collation: Optional[str] = None


test_cases = [
    LmcrecDbMappingBcpFmtInitTestCase(
        name="BuiltinDefault",
        expect_bcp_version="10.0",
        expect_bcp_host_data_type="SYBCHAR",
        expect_bcp_host_data_length=1024,
        expect_bcp_string_collation=None,
    ),
    LmcrecDbMappingBcpFmtInitTestCase(
        name="Mapping",
        db_mapping=r"""
        bcp_fmt:
            version: version
            host_data_type: host_data_type
            host_data_length: 512
            string_collation: ""
        """,
        expect_bcp_version="version",
        expect_bcp_host_data_type="host_data_type",
        expect_bcp_host_data_length=512,
        expect_bcp_string_collation="",
    ),
]


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_lmcrec_db_mapping_bcp_fmt_init(tc: LmcrecDbMappingBcpFmtInitTestCase):
    lmcrec_db_mapping = LmcrecDbMapping(dict(), yaml.safe_load(tc.db_mapping))
    assert lmcrec_db_mapping.bcp_version == tc.expect_bcp_version
    assert lmcrec_db_mapping.bcp_host_data_type == tc.expect_bcp_host_data_type
    assert lmcrec_db_mapping.bcp_host_data_length == tc.expect_bcp_host_data_length
    assert lmcrec_db_mapping.bcp_string_collation == tc.expect_bcp_string_collation
