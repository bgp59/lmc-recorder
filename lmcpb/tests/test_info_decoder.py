#! /usr/bin/env python3

import io
import os
import time

import pytest

from lmcrec.playback.codec.info_decoder import decode_lmcrec_info

from .info_decoder_test_cases import test_cases

os.environ["TZ"] = "UTC"
time.tzset()


def test_lmcrec_info_decoder():
    print()
    for data, want in test_cases:
        got = decode_lmcrec_info(io.BytesIO(data))
        assert want == got
        print(got)


def test_lmcrec_info_decoder_wrong_state():
    data = [0] * 256  # some large buffer
    # +0 version_sz == 0 -> empty string
    # +1 prev_file_name_sz == 0 -> empty string
    # +2 start_ts == 0
    # +3 state
    data[3] = 123
    with pytest.raises(ValueError):
        decode_lmcrec_info(io.BytesIO(bytes(data)))


def test_lmcrec_info_decoder_eof():
    data = bytes([0] * 7)
    with pytest.raises(EOFError):
        decode_lmcrec_info(io.BytesIO(data))
