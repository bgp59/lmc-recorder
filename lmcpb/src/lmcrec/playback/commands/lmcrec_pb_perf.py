#! /usr/bin/env python3

description = """
Measure the playback performance as the time for applying lmcrec file(s) to the
state cache
"""

import argparse
import os
import sys
import time
from typing import Tuple

from cache import LmcrecScanRetCode, LmcrecStateCache
from codec import LmcrecFileDecoder
from tabulate import SEPARATING_LINE, tabulate

from .help_formatter import CustomWidthFormatter


def perf(lmcrec_file, have_prev: bool = False) -> Tuple[int, float]:
    file_sz = os.stat(lmcrec_file).st_size
    start_ts = time.time()
    state_cache = LmcrecStateCache(LmcrecFileDecoder(lmcrec_file), have_prev=have_prev)
    while True:
        ret_code = state_cache.apply_next_scan()
        if ret_code == LmcrecScanRetCode.ATEOR:
            break
        if ret_code != LmcrecScanRetCode.COMPLETE:
            print(
                f"{lmcrec_file!r} ignored: apply_next_scan() ret_code: want: {LmcrecScanRetCode.COMPLETE!r}, got: {ret_code!r}",
                file=sys.stderr,
            )
            return None, None
    d_time = time.time() - start_ts
    return file_sz, d_time


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
    )
    parser.add_argument(
        "-p",
        "--have-prev",
        action="store_true",
        help="""Enable previous variable value state cache""",
    )
    parser.add_argument("lmcrec_file", nargs="+")
    args = parser.parse_args()

    rows = []
    total_file_sz, total_d_time = 0, 0

    def append_row(lmcrec_file, file_sz, d_time):
        file_sz_kib = file_sz / 1000
        rows.append(
            (
                lmcrec_file,
                f"{file_sz_kib:.01f}",
                f"{d_time:06f}",
                f"{file_sz_kib/d_time:.02f}",
            )
        )

    for lmcrec_file in args.lmcrec_file:
        file_sz, d_time = perf(lmcrec_file, have_prev=args.have_prev)
        if file_sz is not None and d_time is not None:
            total_file_sz += file_sz
            total_d_time += d_time
            append_row(lmcrec_file, file_sz, d_time)
    n = len(rows)
    if n > 0:
        file_sz, d_time = total_file_sz / n, total_d_time / n
        rows.append(SEPARATING_LINE)
        append_row("Average", file_sz, d_time)
        print()
        print(
            tabulate(
                rows, headers=["File", "Size (kB)", "Time (sec)", "Speed (kB/sec)"]
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
