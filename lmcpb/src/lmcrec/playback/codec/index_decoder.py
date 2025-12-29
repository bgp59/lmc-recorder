from typing import BinaryIO, Optional, Tuple

from .decoder import INDEX_FILE_SUFFIX
from .varint_decoder import decode_varint


class LmcrecIndexDecoder:
    def __init__(self, stream: BinaryIO):
        self._stream = stream

    def next_checkpoint(self) -> Tuple[float, int]:
        return decode_varint(self._stream) / 1_000_000, decode_varint(self._stream)

    def last_checkpoint(self, from_ts: float) -> Tuple[Optional[float], Optional[int]]:
        """Locate latest checkpoint preceding or at from_ts, best effort"""
        chkpt_ts, chkpt_off = None, None
        while True:
            try:
                ts, off = self.next_checkpoint()
                if ts <= from_ts:
                    chkpt_ts, chkpt_off = ts, off
                if chkpt_ts >= from_ts:
                    break
            except (EOFError, ValueError, RuntimeError, TypeError):
                break
        return chkpt_ts, chkpt_off


class LmcrecIndexFileDecoder(LmcrecIndexDecoder):
    _stream = None

    def __init__(self, file_name: str):
        self._stream = open(file_name, "rb")

    def close(self):
        if self._stream is not None:
            self._stream.close()
            self._stream = None

    def __del__(self):
        self.close()


def locate_checkpoint(
    lmcrec_file, from_ts: Optional[float] = None
) -> Tuple[Optional[float], Optional[int]]:
    """Locate last checkpoint for lmcrec file before from_ts."""

    chkpt_ts, chkpt_off = None, None
    if from_ts is not None:
        index_decoder = LmcrecIndexFileDecoder(lmcrec_file + INDEX_FILE_SUFFIX)
        chkpt_ts, chkpt_off = index_decoder.last_checkpoint(from_ts)
    return chkpt_ts, chkpt_off
