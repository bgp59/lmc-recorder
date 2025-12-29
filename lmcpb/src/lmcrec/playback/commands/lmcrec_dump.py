#! /usr/bin/env python3

description = """
Dump lmcrec recording, info or index file
"""

import argparse
import sys

from codec import (
    INDEX_FILE_SUFFIX,
    INFO_FILE_SUFFIX,
    LmcrecFileDecoder,
    LmcrecIndexFileDecoder,
    LmcrecType,
    decode_lmcrec_info_from_file,
)
from misc.timeutils import format_ts

from .help_formatter import CustomWidthFormatter

record_types = set(
    rt.name.lower()
    for rt in [
        LmcrecType.CLASS_INFO,
        LmcrecType.DELETE_INST_ID,
        LmcrecType.DURATION_USEC,
        LmcrecType.EOR,
        LmcrecType.INST_INFO,
        LmcrecType.SCAN_TALLY,
        LmcrecType.SET_INST_ID,
        LmcrecType.TIMESTAMP_USEC,
        LmcrecType.VAR_INFO,
        LmcrecType.VAR_VALUE,
    ]
)


def dump_lmcrec_info_file(file_name: str) -> int:
    lmcrec_info = decode_lmcrec_info_from_file(file_name)
    print(lmcrec_info)
    return 0


def dump_lmcrec_index_file(file_name: str) -> int:
    decoder = LmcrecIndexFileDecoder(file_name)
    while True:
        try:
            ts, offset = decoder.next_checkpoint()
            print(format_ts(ts), f"+{offset}")
        except EOFError:
            break
    return 0


def dump_lmcrec_file(file_name: str, record_types: str = "") -> int:
    selected_record_types = set()
    if record_types:
        for rt in record_types.split(","):
            rt = rt.strip().lower()
            if rt not in record_types:
                print(
                    f"{rt!r}: invalid record type, must be one of {sorted(record_types)}\n",
                    file=sys.stderr,
                )
                return 1
            selected_record_types.add(LmcrecType[rt.upper()])

    decoder = LmcrecFileDecoder(file_name)
    while True:
        record = decoder.next_record()
        if not selected_record_types or record.record_type in selected_record_types:
            print(record)
        if (
            record.record_type == LmcrecType.DURATION_USEC
            and len(selected_record_types) != 1
        ):
            print()
        if record.record_type == LmcrecType.EOR:
            break
    return 0


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
    )
    parser.add_argument(
        "-t",
        "--record-type",
        help=f"""
        Comma separated list of record types to dump, valid choices: {sorted(record_types)}
        """,
    )
    parser.add_argument(
        "file",
        help=f"""
        Recording, info ({INFO_FILE_SUFFIX!r} suffix) or index ({INDEX_FILE_SUFFIX!r} suffix) file.
        """,
    )
    args = parser.parse_args()
    file_name = args.file

    if file_name.endswith(INFO_FILE_SUFFIX):
        ret_code = dump_lmcrec_info_file(file_name)
    elif file_name.endswith(INDEX_FILE_SUFFIX):
        ret_code = dump_lmcrec_index_file(file_name)
    else:
        ret_code = dump_lmcrec_file(file_name, args.record_type)
    return ret_code
