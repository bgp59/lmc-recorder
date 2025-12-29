import gzip
import os
from dataclasses import dataclass
from enum import IntEnum
from typing import BinaryIO, Optional

from misc.timeutils import format_ts

from .varint_decoder import (
    decode_uvarint,
    decode_varint,
)

# Must match the homonymous constants in lmcrec/codec/encoder.go:
LMCREC_FILE_SUFFIX = ".lmcrec"
GZIP_FILE_SUFFIX = ".gz"
INFO_FILE_SUFFIX = ".info"
INDEX_FILE_SUFFIX = ".index"


class LmcrecType(IntEnum):
    # Should be assigned the same numbers as the constants in lmcrec/codec/encoder.go:
    UNDEFINED = 0
    CLASS_INFO = 1
    INST_INFO = 2
    VAR_INFO = 3
    SET_INST_ID = 4
    VAR_BOOL_FALSE = 5
    VAR_BOOL_TRUE = 6
    VAR_UINT_VAL = 7
    VAR_SINT_VAL = 8
    VAR_ZERO_VAL = 9
    VAR_STRING_VAL = 10
    VAR_EMPTY_STRING = 11
    DELETE_INST_ID = 12
    SCAN_TALLY = 13
    TIMESTAMP_USEC = 14
    DURATION_USEC = 15
    EOR = 16
    # All RMV_VAR_..._VALUE will be reported as a unified type:
    VAR_VALUE = 17


class LmcVarType(IntEnum):
    UNDEFINED = 0
    BOOLEAN = 1
    BOOLEAN_CONFIG = 2
    COUNTER = 3
    GAUGE = 4
    GAUGE_CONFIG = 5
    NUMERIC = 6
    LARGE_NUMERIC = 7
    NUMERIC_RANGE = 8
    NUMERIC_CONFIG = 9
    STRING = 10
    STRING_CONFIG = 11


@dataclass
class LmcRecord:
    record_type: Optional[LmcrecType] = None
    file_record_type: Optional[LmcrecType] = (
        None  # the original type, if different than record_type, e.g. VAR_NUM_VAL != VAR_VALUE
    )
    class_id: Optional[int] = None
    inst_id: Optional[int] = None
    parent_inst_id: Optional[int] = None
    var_id: Optional[int] = None
    lmc_var_type: Optional[LmcVarType] = None
    name: Optional[str] = None
    value: Optional[any] = None
    scan_in_byte_count: Optional[int] = None
    scan_in_inst_count: Optional[int] = None
    scan_in_var_count: Optional[int] = None
    scan_out_var_count: Optional[int] = None

    def __str__(self):
        record_type = self.record_type

        def to_str(*attr_list: str) -> str:
            as_str = f"{self.__class__.__name__}(record_type={record_type!r}"
            for attr in attr_list:
                as_str += f", {attr}={getattr(self, attr)!r}"
            as_str += ")"
            return as_str

        if record_type == LmcrecType.VAR_VALUE:
            return to_str("var_id", "value", "file_record_type")
        if record_type == LmcrecType.SET_INST_ID:
            return to_str("inst_id")
        if record_type == LmcrecType.INST_INFO:
            return to_str("class_id", "inst_id", "parent_inst_id", "name")
        if record_type == LmcrecType.CLASS_INFO:
            return to_str("class_id", "name")
        if record_type == LmcrecType.VAR_INFO:
            return to_str("class_id", "var_id", "lmc_var_type", "name")
        if record_type == LmcrecType.DELETE_INST_ID:
            return to_str("inst_id")
        if record_type == LmcrecType.SCAN_TALLY:
            return to_str(
                "scan_in_byte_count",
                "scan_in_inst_count",
                "scan_in_var_count",
                "scan_out_var_count",
            )
        if record_type == LmcrecType.TIMESTAMP_USEC:
            return (
                f"{self.__class__.__name__}("
                f"record_type={record_type!r}, "
                f"value={format_ts(self.value)} ({self.value:.06f})"
                ")"
            )
        if record_type == LmcrecType.DURATION_USEC:
            return (
                f"{self.__class__.__name__}("
                f"record_type={record_type!r}, "
                f"value={self.value:.06f}s"
                ")"
            )
        return to_str()


class LmcrecDecoder:
    def __init__(self, stream: BinaryIO):
        self._stream = stream

    def _read_string(self) -> str:
        l = decode_uvarint(self._stream)
        data = self._stream.read(l)
        if len(data) != l:
            raise RuntimeError(
                f"not enough bytes for string, want: {l}, got: {len(data)}"
            )
        return str(data, "utf-8")

    def next_record(self, lmc_record: Optional[LmcRecord] = None) -> LmcRecord:
        record_type = LmcrecType(decode_uvarint(self._stream))
        if lmc_record is None:
            lmc_record = LmcRecord(record_type=record_type)
        else:
            lmc_record.record_type = record_type
            lmc_record.file_record_type = None

        # Order the tests below in decreasing order of expected frequency
        # (performance improvement):
        if record_type == LmcrecType.VAR_UINT_VAL:
            lmc_record.var_id = decode_uvarint(self._stream)
            lmc_record.value = decode_uvarint(self._stream)
            lmc_record.record_type = LmcrecType.VAR_VALUE
            lmc_record.file_record_type = record_type
        elif record_type == LmcrecType.VAR_SINT_VAL:
            lmc_record.var_id = decode_uvarint(self._stream)
            lmc_record.value = decode_varint(self._stream)
            lmc_record.record_type = LmcrecType.VAR_VALUE
            lmc_record.file_record_type = record_type
        elif record_type == LmcrecType.VAR_STRING_VAL:
            lmc_record.var_id = decode_uvarint(self._stream)
            lmc_record.value = self._read_string()
            lmc_record.record_type = LmcrecType.VAR_VALUE
            lmc_record.file_record_type = record_type
        elif record_type == LmcrecType.VAR_ZERO_VAL:
            lmc_record.var_id = decode_uvarint(self._stream)
            lmc_record.value = 0
            lmc_record.record_type = LmcrecType.VAR_VALUE
            lmc_record.file_record_type = record_type
        elif record_type == LmcrecType.VAR_BOOL_FALSE:
            lmc_record.var_id = decode_uvarint(self._stream)
            lmc_record.value = False
            lmc_record.record_type = LmcrecType.VAR_VALUE
            lmc_record.file_record_type = record_type
        elif record_type == LmcrecType.VAR_BOOL_TRUE:
            lmc_record.var_id = decode_uvarint(self._stream)
            lmc_record.value = True
            lmc_record.record_type = LmcrecType.VAR_VALUE
            lmc_record.file_record_type = record_type
        elif record_type == LmcrecType.VAR_EMPTY_STRING:
            lmc_record.var_id = decode_uvarint(self._stream)
            lmc_record.value = ""
            lmc_record.record_type = LmcrecType.VAR_VALUE
            lmc_record.file_record_type = record_type
        elif record_type == LmcrecType.SET_INST_ID:
            lmc_record.inst_id = decode_uvarint(self._stream)
        elif record_type == LmcrecType.INST_INFO:
            lmc_record.class_id = decode_uvarint(self._stream)
            lmc_record.inst_id = decode_uvarint(self._stream)
            lmc_record.parent_inst_id = decode_uvarint(self._stream)
            lmc_record.name = self._read_string()
        elif record_type == LmcrecType.CLASS_INFO:
            lmc_record.class_id = decode_uvarint(self._stream)
            lmc_record.name = self._read_string()
        elif record_type == LmcrecType.VAR_INFO:
            lmc_record.class_id = decode_uvarint(self._stream)
            lmc_record.var_id = decode_uvarint(self._stream)
            lmc_record.lmc_var_type = LmcVarType(decode_uvarint(self._stream))
            lmc_record.name = self._read_string()
        elif record_type == LmcrecType.DELETE_INST_ID:
            lmc_record.inst_id = decode_uvarint(self._stream)
        elif record_type == LmcrecType.SCAN_TALLY:
            lmc_record.scan_in_byte_count = decode_uvarint(self._stream)
            lmc_record.scan_in_inst_count = decode_uvarint(self._stream)
            lmc_record.scan_in_var_count = decode_uvarint(self._stream)
            lmc_record.scan_out_var_count = decode_uvarint(self._stream)
        elif record_type == LmcrecType.TIMESTAMP_USEC:
            lmc_record.value = decode_varint(self._stream) / 1_000_000
        elif record_type == LmcrecType.DURATION_USEC:
            lmc_record.value = decode_varint(self._stream) / 1_000_000

        return lmc_record


class LmcrecFileDecoder(LmcrecDecoder):
    _stream = None
    SEEK_CHUNK = 0x10000  # 64k

    def __init__(self, fname: str):
        if fname.endswith(GZIP_FILE_SUFFIX):
            self._stream = gzip.open(fname, "rb")
        else:
            self._stream = open(fname, "rb")

    def goto(self, offset: int):
        if hasattr(self._stream, "seek"):
            self._stream.seek(offset, os.SEEK_SET)
        else:
            while offset > 0:
                data = self._stream.read(min(offset, self.SEEK_CHUNK))
                n = len(data)
                if n == 0:
                    break
                offset -= n

    def close(self):
        if self._stream is not None:
            self._stream.close()
            self._stream = None

    def __del__(self):
        self.close()
