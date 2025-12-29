#! /usr/bin/env python3

import io

from lmcrec.playback.codec.decoder import LmcrecDecoder

from .decoder_test_cases import test_cases


def test_lmcrec_decoder():
    for data, want in test_cases:
        decoder = LmcrecDecoder(io.BytesIO(data))
        got = decoder.next_record()
        assert got == want


def test_lmcrec_decoder_multi():
    data = bytes()
    want_list = []
    for d, want in test_cases:
        data += d
        want_list.append(want)
    decoder = LmcrecDecoder(io.BytesIO(data))
    for want in want_list:
        got = decoder.next_record()
        assert got == want


def test_lmcrec_decoder_print():
    print()
    for _, lmcrec in test_cases:
        print(lmcrec)
