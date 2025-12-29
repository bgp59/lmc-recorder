# /usr/bin/env python3

"""Unit tests for LmcrecQuerySelector"""

import re

import pytest
import yaml

from lmcrec.playback.query.query_selector import LmcrecQuerySelector

from .query_selector_def import (
    LmcrecQuerySelectorInitTestCase,
    LmcrecQuerySelectorRunTestCase,
    LmcrecQuerySelectorUpdateTestCase,
)
from .query_selector_init_test_cases import init_test_cases
from .query_selector_run_test_cases import run_test_cases
from .query_selector_update_test_cases import update_test_cases


def names_are_equal(name1: str, name2: str) -> bool:
    return re.sub(r"[^\w]+", "", name1).lower() == re.sub(r"[^\w]+", "", name2).lower()


def _run_test_query_selector_init(tc: LmcrecQuerySelectorInitTestCase):
    query_selector = LmcrecQuerySelector(yaml.safe_load(tc.query))

    assert names_are_equal(query_selector.name, tc.name)

    assert query_selector.needs_prev == tc.expect_needs_prev

    assert sorted(query_selector._query_full_inst_names) == sorted(
        tc.expect_query_full_inst_names
    )
    assert sorted(query_selector._query_prefix_inst_names) == sorted(
        tc.expect_query_prefix_inst_names
    )
    assert sorted(p.pattern for p in query_selector._query_inst_re) == sorted(
        tc.expect_query_inst_re
    )

    assert query_selector._query_class_name == tc.expect_query_class_name

    assert query_selector._include_types == tc.expect_query_include_types
    assert query_selector._exclude_types == tc.expect_query_exclude_types

    assert query_selector._include_vars == tc.expect_query_include_vars
    assert query_selector._exclude_vars == tc.expect_query_exclude_vars


@pytest.mark.parametrize("tc", init_test_cases, ids=lambda tc: tc.name)
def test_lmcrec_query_selector_init(tc):
    _run_test_query_selector_init(tc)


def _run_test_query_selector_update(tc: LmcrecQuerySelectorUpdateTestCase):

    query_selector = LmcrecQuerySelector(yaml.safe_load(tc.query))
    if tc.selector_primer is not None:
        query_selector.selector_update(tc.selector_primer(is_primer=True))
    query_state_cache = tc.query_state_cache()
    if tc.expect_exception is not None:
        with pytest.raises(tc.expect_exception) as ex:
            query_selector.selector_update(query_state_cache)
            if tc.expect_exception_str:
                assert tc.expect_exception_str in str(ex)
    else:
        query_selector.selector_update(query_state_cache)
        assert query_selector.selector == tc.expect_selector


@pytest.mark.parametrize("tc", update_test_cases, ids=lambda tc: tc.name)
def test_lmcrec_query_selector_update(tc):
    _run_test_query_selector_update(tc)


def _run_test_lmcrec_query_selector_run(tc: LmcrecQuerySelectorRunTestCase):
    query_selector = LmcrecQuerySelector(yaml.safe_load(tc.query))
    query_state_cache = tc.query_state_cache(is_primer=True)
    result = query_selector.run(query_state_cache)
    assert result == tc.expect_result


@pytest.mark.parametrize("tc", run_test_cases, ids=lambda tc: tc.name)
def test_lmcrec_query_selector_run(tc):
    _run_test_lmcrec_query_selector_run(tc)
