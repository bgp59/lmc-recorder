from copy import deepcopy
from unittest.mock import MagicMock

import pytest

from lmcrec.playback.cache.state_cache import LmcrecScanRetCode, LmcrecStateCache

from .state_cache_def import LmcrecStateCacheTestCase
from .state_cache_test_cases_err import test_cases_err
from .state_cache_test_cases_ok import test_cases_ok


def _run_test_case(tc: LmcrecStateCacheTestCase):
    state_cache = LmcrecStateCache(decoder=None, have_prev=tc.have_prev)
    expect_prev_ts = None
    if tc.prime_next_records:
        decoder = MagicMock()
        decoder.next_record.side_effect = tc.prime_next_records
        state_cache.set_decoder(decoder)
        retcode = state_cache.apply_next_scan()
        if tc.have_prev:
            expect_prev_ts = tc.prime_next_records[0].value
        assert retcode == LmcrecScanRetCode.COMPLETE

    decoder = MagicMock()
    decoder.next_record.side_effect = tc.next_records
    state_cache.set_decoder(decoder)

    if tc.expect_exception is not None:
        with pytest.raises(tc.expect_exception) as ex:
            state_cache.apply_next_scan()
        if tc.expect_exception_str:
            assert tc.expect_exception_str in str(ex)
        return

    expect_ts = tc.next_records[0].value
    state_cache.set_decoder(decoder)
    retcode = state_cache.apply_next_scan()
    assert retcode == LmcrecScanRetCode.COMPLETE

    for class_info in tc.expect_class_cache:
        class_info = deepcopy(class_info)
        for var_info in class_info.var_info_by_id.values():
            class_info.var_info_by_name[var_info.name] = var_info
        assert state_cache.class_by_id[class_info.class_id] == class_info
        assert state_cache.class_by_name[class_info.name] == class_info

    unexpected = set(state_cache.class_by_id) - set(
        class_info.class_id for class_info in tc.expect_class_cache
    )
    assert not unexpected, "Unexpected class IDs"
    unexpected = set(state_cache.class_by_name) - set(
        class_info.name for class_info in tc.expect_class_cache
    )
    assert not unexpected, "Unexpected class names"

    for inst in tc.expect_inst_cache:
        assert state_cache.inst_by_id[inst.inst_id] == inst
        assert state_cache.inst_by_name[inst.name] == inst
    unexpected = set(state_cache.inst_by_id) - set(
        inst.inst_id for inst in tc.expect_inst_cache
    )
    assert not unexpected, "Unexpected inst IDs"
    unexpected = set(state_cache.inst_by_name) - set(
        inst.name for inst in tc.expect_inst_cache
    )
    assert not unexpected, "Unexpected inst names"

    assert state_cache.inst_by_class_name == tc.expect_inst_by_class_name

    assert state_cache.new_inst == tc.expect_new_inst
    assert state_cache.deleted_inst == tc.expect_deleted_inst
    assert state_cache.new_class_def == tc.expect_new_class_def

    assert state_cache.ts == expect_ts
    assert state_cache.prev_ts == expect_prev_ts


@pytest.mark.parametrize("tc", test_cases_ok, ids=lambda tc: tc.name)
def test_lmcrec_state_cache_ok(tc: LmcrecStateCacheTestCase):
    _run_test_case(tc)


@pytest.mark.parametrize("tc", test_cases_err, ids=lambda tc: tc.name)
def test_lmcrec_state_cache_err(tc: LmcrecStateCacheTestCase):
    _run_test_case(tc)
