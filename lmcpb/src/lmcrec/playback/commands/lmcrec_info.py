#! /usr/bin/env python3

description = """
Display information about the record files.
"""

import argparse
import os
import sys
from typing import List, Tuple

from codec import (
    LmcrecInfo,
)
from misc.timeutils import format_ts
from query import (
    build_lmcrec_file_chains,
    get_file_selection_arg_parser,
    process_file_selection_args,
)
from tabulate import SEPARATING_LINE, tabulate

from .help_formatter import CustomWidthFormatter

headers = [
    "File",
    "Size",
    "Version",
    "Prev File",
    "State",
    "From",
    "To",
    "Total\nIn Byte#",
    "Total\nIn Inst#",
    "Total\nIn Var#",
    "Total\nOut Var#",
    "Byte#\nIn/Out",
]


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
        parents=[get_file_selection_arg_parser()],
    )
    parser.add_argument(
        "-u",
        "--display-usec",
        action="store_true",
        help="""Display microseconds for timestamps""",
    )
    args = parser.parse_args()
    display_usec = args.display_usec
    record_files_dir, from_ts, to_ts = process_file_selection_args(args)
    lmcrec_file_chains = build_lmcrec_file_chains(record_files_dir, from_ts, to_ts)

    if not lmcrec_file_chains:
        print("No recorded data available", file=sys.stderr)
        return 1

    lmcrec_info_list: List[Tuple[str, int, LmcrecInfo]] = []
    record_files_dir = None
    for entry in lmcrec_file_chains:
        while entry is not None:
            lmcrec_file_name = entry.file_name
            f_size = os.stat(lmcrec_file_name).st_size
            # Keep the last sub-dir since the recorder creates
            # yyy-mm-dd/HH:MM:SS±HH:MM files under the instance's record
            # file dir:
            i = lmcrec_file_name.rfind("/")
            if i >= 0:
                i = lmcrec_file_name.rfind("/", 0, i)
            if i >= 0:
                if record_files_dir is None:
                    record_files_dir = lmcrec_file_name[:i]
                lmcrec_file_name = lmcrec_file_name[i + 1 :]
            lmcrec_info_list.append((lmcrec_file_name, f_size, entry.lmcrec_info))
            entry = entry.next

    print()
    rows = []
    total_in_num_bytes, total_f_size = 0, 0
    for file_name, f_size, lmcrec_info in lmcrec_info_list:
        row = (file_name, f_size)
        if lmcrec_info is not None:
            total_in_num_bytes += lmcrec_info.total_in_num_bytes
            total_f_size += f_size
            start_ts, most_recent_ts = lmcrec_info.start_ts, lmcrec_info.most_recent_ts
            if not display_usec:
                start_ts, most_recent_ts = int(start_ts), int(most_recent_ts)
            row += (
                lmcrec_info.version,
                lmcrec_info.prev_file_name,
                lmcrec_info.state.name,
                format_ts(start_ts),
                format_ts(most_recent_ts),
                lmcrec_info.total_in_num_bytes,
                lmcrec_info.total_in_num_inst,
                lmcrec_info.total_in_num_var,
                lmcrec_info.total_out_num_var,
                (f"{lmcrec_info.total_in_num_bytes/f_size:.01f}" if f_size > 0 else 0),
            )
        else:
            row += tuple(["N/A"] * (len(headers) - 2))
        rows.append(row)
    rows.append(SEPARATING_LINE)
    avg = f"{total_in_num_bytes/total_f_size if total_f_size > 0 else 0:.01f}"
    rows.append([""] * (len(headers) - 2) + ["Avg", avg])
    print(
        tabulate(
            rows,
            headers=headers,
        )
    )
    if record_files_dir:
        print(f"All paths relative to {record_files_dir!r}\n")

    print("Contiguous time spans:")
    global_start_ts, global_last_ts = None, None
    for entry in lmcrec_file_chains:
        start_ts = int(entry.lmcrec_info.start_ts)
        if global_start_ts is None:
            global_start_ts = start_ts
        while entry is not None:
            last_ts = int(entry.lmcrec_info.most_recent_ts)
            entry = entry.next
        global_last_ts = last_ts
        print(f"  {format_ts(start_ts)} - {format_ts(last_ts)}")
    print("Global time span:")
    print(f"  {format_ts(global_start_ts)} - {format_ts(global_last_ts)}")
    print()
