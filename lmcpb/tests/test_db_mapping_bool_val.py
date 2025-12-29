from dataclasses import dataclass
from typing import Any

import pytest
import yaml

from lmcrec.playback.commands.lmcrec_export import LmcrecDbMapping


@dataclass
class LmcrecDbBoolValMappingTestCase:
    name: str = ""
    description: str = ""
    db_mapping: str = ""
    expect_true: Any = 1
    expect_false: Any = 0


test_cases = [
    LmcrecDbBoolValMappingTestCase(
        name="TF",
        db_mapping="""
            data_type_mapping:
                boolean:
                    true_value: T
                    false_value: F

        """,
        expect_true="T",
        expect_false="F",
    ),
    LmcrecDbBoolValMappingTestCase(
        name="truefalse",
        db_mapping="""
            data_type_mapping:
                boolean:
                    true_value: "true"
                    false_value: "false"

        """,
        expect_true="true",
        expect_false="false",
    ),
    LmcrecDbBoolValMappingTestCase(
        name="bit01",
        db_mapping="""
            data_type_mapping:
                boolean:
                    col_type: bit
                    true_value: 1
                    false_value: 0

        """,
        expect_true=1,
        expect_false=0,
    ),
]


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_lmcrec_db_mapping_bool_val(tc: LmcrecDbBoolValMappingTestCase):
    lmcrec_db_mapping = LmcrecDbMapping(dict(), yaml.safe_load(tc.db_mapping))
    assert lmcrec_db_mapping.bool_val(True) == tc.expect_true
    assert lmcrec_db_mapping.bool_val(False) == tc.expect_false
