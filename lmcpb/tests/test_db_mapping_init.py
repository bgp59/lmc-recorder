"""Unit test for LmcrecDbMapping init"""

import pytest
import yaml

from lmcrec.playback.commands.lmcrec_export import LmcrecDbMapping

from .db_mapping_init_test_cases import LmcrecDbMappingInitTestCase, test_cases


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_db_mapping_init(tc: LmcrecDbMappingInitTestCase):
    lmcrec_schema = yaml.safe_load(tc.lmcrec_schema) if tc.lmcrec_schema else dict()
    db_mapping = yaml.safe_load(tc.db_mapping) if tc.db_mapping else None
    if tc.expect_exception is not None:
        with pytest.raises(tc.expect_exception) as ex:
            LmcrecDbMapping(lmcrec_schema, db_mapping)
            if tc.expect_exception_str:
                assert tc.expect_exception_str in str(ex)
    else:
        lmcrec_db_mapping = LmcrecDbMapping(lmcrec_schema, db_mapping)
        assert lmcrec_db_mapping.tables == tc.expect_tables
        assert lmcrec_db_mapping.lmc_classes == tc.expect_lmc_classes
