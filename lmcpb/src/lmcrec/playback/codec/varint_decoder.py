from typing import BinaryIO


def decode_uvarint(stream: BinaryIO) -> int:
    """Decodes an unsigned varint from a byte stream."""
    value = 0
    shift = 0

    while True:
        data = stream.read(1)
        if not data:
            raise EOFError()
        byte = data[0]
        value |= (byte & 0x7F) << shift
        if value >> 64:
            raise RuntimeError("Value too big for uint64")
        if not (byte & 0x80):
            return value
        shift += 7


def decode_varint(stream: BinaryIO) -> int:
    """Decodes an signed varint from a byte stream."""
    value = decode_uvarint(stream)
    return (-value - 1 if (value & 1) else value) >> 1
