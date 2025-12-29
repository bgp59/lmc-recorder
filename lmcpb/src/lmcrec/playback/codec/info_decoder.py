from dataclasses import dataclass
from enum import IntEnum
from typing import BinaryIO, Optional

from misc.timeutils import format_ts

from .varint_decoder import decode_uvarint, decode_varint


class LmcrecInfoState(IntEnum):
    # Should be assigned the same numbers as the constants in lmcrec/codec/encoder.go:
    UNINITIALIZED = 0
    ACTIVE = 1
    CLOSED = 2


@dataclass
class LmcrecInfo:
    version: Optional[str] = None
    prev_file_name: Optional[str] = None
    start_ts: Optional[float] = None
    state: Optional[LmcrecInfoState] = None
    most_recent_ts: Optional[float] = None
    total_in_num_bytes: Optional[int] = None
    total_in_num_inst: Optional[int] = None
    total_in_num_var: Optional[int] = None
    total_out_num_var: Optional[int] = None

    def __str__(self):
        return (
            f"{self.__class__.__name__}(\n  "
            + ",\n  ".join(
                [
                    f"version={self.version!r}",
                    f"prev_file_name={self.prev_file_name!r}",
                    f"start_ts={format_ts(self.start_ts)} ({self.start_ts:.06f})",
                    f"state={self.state!r}",
                    f"most_recent_ts={format_ts(self.most_recent_ts)} ({self.most_recent_ts:.06f})",
                    f"total_in_num_bytes={self.total_in_num_bytes}",
                    f"total_in_num_inst={self.total_in_num_inst}",
                    f"total_in_num_var={self.total_in_num_var}",
                    f"total_out_num_var={self.total_out_num_var}",
                ]
            )
            + "\n)"
        )


def decode_lmcrec_info(
    stream: BinaryIO, lmcrec_info: Optional[LmcrecInfo] = None
) -> LmcrecInfo:
    if lmcrec_info is None:
        lmcrec_info = LmcrecInfo()
    version_sz = decode_uvarint(stream)
    if version_sz > 0:
        data = stream.read(version_sz)
        if len(data) < version_sz:
            raise EOFError()
        lmcrec_info.version = str(data, "utf-8")
    else:
        lmcrec_info.version = ""
    prev_file_name_sz = decode_uvarint(stream)
    if prev_file_name_sz > 0:
        data = stream.read(prev_file_name_sz)
        if len(data) < prev_file_name_sz:
            raise EOFError()
        lmcrec_info.prev_file_name = str(data, "utf-8")
    else:
        lmcrec_info.prev_file_name = ""
    lmcrec_info.start_ts = decode_varint(stream) / 1_000_000
    data = stream.read(1)
    if len(data) < 1:
        raise EOFError()
    lmcrec_info.state = LmcrecInfoState(data[0])
    lmcrec_info.most_recent_ts = decode_varint(stream) / 1_000_000
    lmcrec_info.total_in_num_bytes = decode_uvarint(stream)
    lmcrec_info.total_in_num_inst = decode_uvarint(stream)
    lmcrec_info.total_in_num_var = decode_uvarint(stream)
    lmcrec_info.total_out_num_var = decode_uvarint(stream)
    return lmcrec_info


def decode_lmcrec_info_from_file(
    file_name: str, lmcrec_info: Optional[LmcrecInfo] = None
) -> LmcrecInfo:
    with open(file_name, "rb") as f:
        return decode_lmcrec_info(f, lmcrec_info)
