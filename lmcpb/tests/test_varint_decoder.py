#! /usr/bin/env python3

import io

import pytest

from lmcrec.playback.codec.varint_decoder import (
    decode_uvarint,
    decode_varint,
)

from .varint_decoder_test_cases import (
    uvarint_test_cases,
    varint_test_cases,
)


def test_decode_uvarint():
    for data, want in uvarint_test_cases:
        got = decode_uvarint(io.BytesIO(data))
        assert want == got


def test_decode_varint():
    for data, want in varint_test_cases:
        got = decode_varint(io.BytesIO(data))
        assert want == got


def test_decode_varint_eof():
    for data in [
        # Empty:
        bytes(),
        # Missing last byte (bit#7 == 0):
        bytes([0xFF]),
        bytes([0xFF, 0xFF]),
    ]:
        with pytest.raises(EOFError):
            decode_uvarint(io.BytesIO(data))


def test_decode_varint_too_long():
    with pytest.raises(RuntimeError):
        decode_uvarint(
            io.BytesIO(
                bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x02])
            )
        )
