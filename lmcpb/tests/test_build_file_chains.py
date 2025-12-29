# /usr/bin/env python3

"""Test cases for build_lmcrec_file_chains"""

import os
from datetime import datetime
from typing import Dict, Iterable, List, Tuple
from unittest.mock import patch

import pytest

from lmcrec.playback.codec import LmcrecInfo
from lmcrec.playback.query.file_selector import build_lmcrec_file_chains

from .build_file_chains_def import BuildLmcrecFileChainsTestCase
from .build_file_chains_test_cases_err import test_cases_err
from .build_file_chains_test_cases_ok import test_cases_ok

if "LMCREC_TZ" in os.environ:
    del os.environ["LMCREC_TZ"]


class OsPathAbspathMock:
    def __init__(self, ret_vals: Dict[str, str]):
        self._org_abspath = os.path.abspath
        self._ret_vals = ret_vals or dict()

    def __call__(self, path: str) -> str:
        return self._ret_vals.get(path, self._org_abspath(path))


class OsPathIsdirMock:
    def __init__(self, dir_list: Iterable[str]):
        self._dir_list = set(dir_list) if dir_list else set()

    def __call__(self, path: str) -> bool:
        return path in self._dir_list


class OsListdirMock:
    def __init__(self, ret_vals: Dict[str, List[str]]):
        self._ret_vals = ret_vals if ret_vals else dict()

    def __call__(self, path: str) -> List[str]:
        if path in self._ret_vals:
            return self._ret_vals[path]
        raise FileNotFoundError(f"[Errno 2] No such file or directory: {path!r}")


class DecodeLmcrecInfoFromFileMock:
    def __init__(
        self,
        ret_vals: Dict[str, Tuple[str, float, float]],
    ):
        self._ret_vals = dict()
        if not ret_vals:
            return
        for path, (prev_file_name, start_ts, most_recent_ts) in ret_vals.items():
            self._ret_vals[path] = LmcrecInfo(
                prev_file_name=prev_file_name,
                start_ts=datetime.fromisoformat(start_ts).timestamp(),
                most_recent_ts=datetime.fromisoformat(most_recent_ts).timestamp(),
            )

    def __call__(self, path: str) -> LmcrecInfo:
        if path in self._ret_vals:
            return self._ret_vals[path]
        raise FileNotFoundError(f"[Errno 2] No such file or directory: {path!r}")


def get_tc_id(tc: BuildLmcrecFileChainsTestCase) -> str:
    return tc.name


def _run_test_case(tc: BuildLmcrecFileChainsTestCase):
    with (
        patch(
            "lmcrec.playback.query.file_selector.os.path.abspath",
            OsPathAbspathMock(tc.abspath_ret_vals),
        ),
        patch(
            "lmcrec.playback.query.file_selector.os.path.isdir",
            OsPathIsdirMock(tc.isdir_list),
        ),
        patch(
            "lmcrec.playback.query.file_selector.os.listdir",
            OsListdirMock(tc.listdir_ret_vals),
        ),
        patch(
            "lmcrec.playback.query.file_selector.decode_lmcrec_info_from_file",
            DecodeLmcrecInfoFromFileMock(tc.decode_lmcrec_info_from_file_ret_vals),
        ),
    ):
        record_files_dir = tc.record_files_dir
        from_ts = (
            datetime.fromisoformat(tc.from_ts).timestamp()
            if tc.from_ts is not None
            else None
        )
        to_ts = (
            datetime.fromisoformat(tc.to_ts).timestamp()
            if tc.to_ts is not None
            else None
        )
        if tc.expect_exception is not None:
            with pytest.raises(tc.expect_exception) as ex:
                build_lmcrec_file_chains(record_files_dir, from_ts, to_ts)
            if tc.expect_exception_str:
                assert tc.expect_exception_str in str(ex)
            return
        chain_list = build_lmcrec_file_chains(record_files_dir, from_ts, to_ts)
        if not tc.expect_file_chains:
            assert not chain_list
            return
        assert chain_list
        assert len(tc.expect_file_chains) == len(chain_list)
        for i, expect_file_names in enumerate(tc.expect_file_chains):
            entry = chain_list[i]
            for file_name in expect_file_names:
                assert entry is not None
                assert file_name == entry.file_name
                entry = entry.next
            assert entry is None


@pytest.mark.parametrize("tc", test_cases_ok, ids=get_tc_id)
def test_build_lmcrec_file_chains_ok(tc):
    _run_test_case(tc)


@pytest.mark.parametrize("tc", test_cases_err, ids=get_tc_id)
def test_build_lmcrec_file_chains_err(tc):
    _run_test_case(tc)
