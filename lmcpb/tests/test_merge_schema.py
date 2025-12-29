from copy import deepcopy

import pytest
import yaml

from lmcrec.playback.commands.lmcrec_schema import merge_lmcrec_schema

from .merge_schema_test_cases import (
    SAME_AS_INTO_SCHEMA,
    SAME_AS_NEW_SCHEMA,
    test_cases,
)


@pytest.mark.parametrize("tc", test_cases, ids=lambda tc: tc.name)
def test_merge_lmcrec_schema(tc):
    into_schema = yaml.safe_load(tc.into_schema) if tc.into_schema else dict()
    new_schema = yaml.safe_load(tc.new_schema) if tc.new_schema else dict()
    if tc.expect_schema is SAME_AS_INTO_SCHEMA:
        expect_schema = deepcopy(into_schema)
    elif tc.expect_schema is SAME_AS_NEW_SCHEMA:
        expect_schema = deepcopy(new_schema)
    elif tc.expect_schema:
        expect_schema = yaml.safe_load(tc.expect_schema)
    else:
        expect_schema = dict()
    if tc.expect_exception is not None:
        with pytest.raises(tc.expect_exception) as ex:
            merge_lmcrec_schema(into_schema, new_schema)
            if tc.expect_exception_str:
                assert tc.expect_exception_str in str(ex)
    else:
        updated = merge_lmcrec_schema(into_schema, new_schema)
        assert into_schema == expect_schema
        assert updated == tc.expect_updated
