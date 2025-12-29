#! /usr/bin/env python3

description = """
Verify index consistency. 

The index file consists of TIMESTAMP,OFFSET pairs and this tool check that by
skipping OFFSET bytes (after decompression) at the beginning of the lmcrec file,
the next record is timestamp with TIMESTAMP value.
"""

import argparse
import os
import sys

from codec import (
    INDEX_FILE_SUFFIX,
    LmcrecFileDecoder,
    LmcrecIndexFileDecoder,
    LmcrecType,
)
from misc.timeutils import format_ts
from query import (
    build_lmcrec_file_chains,
    get_file_selection_arg_parser,
    process_file_selection_args,
)

from .help_formatter import CustomWidthFormatter


def check_index(lmcrec_file) -> bool:
    lmcrec_index_file = lmcrec_file + INDEX_FILE_SUFFIX
    if os.path.exists(lmcrec_index_file):
        index_decoder = LmcrecIndexFileDecoder(lmcrec_index_file)
        chkpt_num = 0
        while True:
            try:
                ts, offset = index_decoder.next_checkpoint()
            except EOFError:
                break
            chkpt_num += 1
            try:
                decoder = LmcrecFileDecoder(lmcrec_file)
                decoder.goto(offset)
                record = decoder.next_record()
                if record.record_type != LmcrecType.TIMESTAMP_USEC:
                    print(
                        f"chkpt# {chkpt_num}: ({format_ts(ts)}, +{offset}): want: {LmcrecType.TIMESTAMP_USEC!r}, got: {record.record_type!r}"
                    )
                    return False
                if record.value != ts:
                    print(
                        f"chkpt# {chkpt_num}: ({format_ts(ts)}, +{offset}): got: {format_ts(record.value)}"
                    )
                    return False
            except Exception as e:
                print(
                    f"chkpt# {chkpt_num}: ({format_ts(ts)}, +{offset}): next_record() raised {e!r}"
                )
                return False
    else:
        print(f"No {INDEX_FILE_SUFFIX} found")
    return True


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
        parents=[get_file_selection_arg_parser()],
    )
    parser.add_argument(
        "file",
        nargs="*",
        help="""
            Specific lmcrec file(s) to test,  they override the query style
            selection.
        """,
    )

    args = parser.parse_args()
    if args.file:
        file_list = args.file
    else:
        record_files_dir, from_ts, to_ts = process_file_selection_args(args)
        chain_list = build_lmcrec_file_chains(record_files_dir, from_ts, to_ts)
        file_list = []
        for entry in chain_list:
            while entry is not None:
                file_list.append(entry.file_name)
                entry = entry.next

    retval = 0
    for lmcrec_file in file_list:
        print(f"Checking {lmcrec_file!r}")
        if check_index(lmcrec_file):
            print("Ok")
        else:
            retval = 1
        print()

    return retval


if __name__ == "__main__":
    sys.exit(main())
