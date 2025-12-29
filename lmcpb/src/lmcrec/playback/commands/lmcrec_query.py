#! /usr/bin/env python3

description = """
Run queries against recorded data.

For query syntax see:
    https://github.com/bgp59/lmc-recorder/docs/QueryDescription.md


For additional help with the command see:
    https://github.com/bgp59/lmc-recorder/docs/Commands.md#lmcrec-query


"""

import argparse
import gzip
import os
import re
import sys
from shutil import rmtree
from typing import List, Optional, TextIO, Tuple
from uuid import uuid4
from zlib import Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION

from cache import LmcrecScanRetCode
from config import get_lmcrec_runtime
from misc.timeutils import format_ts
from query import (
    QUERY_FROM_FILE_SUFFIX,
    LmcrecQuery,
    LmcrecQueryClassResult,
    LmcrecQueryIntervalStateCache,
    LmcrecQueryResult,
    get_file_selection_arg_parser,
    process_file_selection_args,
)
from tabulate import SEPARATING_LINE, tabulate

from .help_formatter import CustomWidthFormatter

GZIP_FILE_SUFFIX = ".gz"


def box(txt: str, fh=sys.stdout):
    line = "+" + "-" * (len(txt) + 2) + "+"
    print(file=fh)
    print(line, file=fh)
    print("| " + txt + " |", file=fh)
    print(line, file=fh)
    print(file=fh)


def build_non_null_table(
    class_result: LmcrecQueryClassResult,
) -> Tuple[List[str], List[List[str]]]:
    """Build header and rows for type non-null columns"""

    # Build the list of column indices and instance names having at leas one
    # type non-null value:
    non_null_indices, non_null_inst_names = set(), set()
    vals_by_inst = class_result.vals_by_inst
    for inst_name, vals in vals_by_inst.items():
        for i, val in enumerate(vals):
            if val or isinstance(val, bool):
                non_null_inst_names.add(inst_name)
                non_null_indices.add(i)

    if not non_null_indices:
        return [], []

    non_null_indices = sorted(non_null_indices)

    var_names = [class_result.var_names[i] for i in non_null_indices]
    rows = []
    for inst_name in sorted(non_null_inst_names):
        vals = vals_by_inst[inst_name]
        rows.append([inst_name] + [vals[i] for i in non_null_indices])
    return ["Instance"] + var_names, rows


def build_table(
    class_result: LmcrecQueryClassResult,
) -> Tuple[List[str], List[List[str]]]:
    """Build header and rows for all columns"""

    vals_by_inst = class_result.vals_by_inst
    rows = []
    for inst_name in sorted(vals_by_inst):
        rows.append([inst_name] + vals_by_inst[inst_name])
    return ["Instance"] + class_result.var_names, rows


class FileTableFormatter:
    def __init__(
        self,
        output_dir: str,
        compress_level: Optional[int] = None,
        full_data: bool = False,
    ):
        self._output_dir = output_dir
        self._compress_level = compress_level
        self._build_table = build_table if full_data else build_non_null_table
        self._fh_by_query_class = dict()

    def _get_fh_for_query_class(self, query_name: str, class_name: str) -> TextIO:
        fh = self._fh_by_query_class.get((query_name, class_name))
        if fh is None:
            result_dir = os.path.join(
                self._output_dir,
                re.sub(r"[^a-zA-Z0-9._-]+", "_", query_name.lower()),
            )
            os.makedirs(result_dir)
            file_path = os.path.join(
                result_dir,
                re.sub(r"[^a-zA-Z0-9._-]+", "_", class_name) + ".txt",
            )
            if (
                self._compress_level is not None
                and self._compress_level != Z_NO_COMPRESSION
            ):
                fh = gzip.open(file_path + GZIP_FILE_SUFFIX, "wt")
            else:
                fh = open(file_path, "wt")
            self._fh_by_query_class[(query_name, class_name)] = fh
        return self._fh_by_query_class[(query_name, class_name)]

    def __call__(
        self,
        result: LmcrecQueryResult,
        query_state_cache: LmcrecQueryIntervalStateCache,
    ) -> bool:
        timestamp = format_ts(query_state_cache.ts)
        if not self._output_dir:
            fh = sys.stdout
        for query_name in sorted(result):
            if not self._output_dir:
                box(f"Query: {query_name}")
            query_result = result[query_name]
            for class_name in sorted(query_result):
                class_result = query_result[class_name]
                if self._output_dir:
                    fh = self._get_fh_for_query_class(query_name, class_name)
                print(f"[{timestamp}] Class: {class_name}", file=fh)
                headers, rows = self._build_table(class_result)
                rows.append(SEPARATING_LINE)
                print(tabulate(rows, headers), file=fh)
                print(file=fh)
        return True

    def close(self):
        for query_class in list(self._fh_by_query_class):
            self._fh_by_query_class[query_class].close()
            del self._fh_by_query_class[query_class]

    def __del__(self):
        self.close()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
        parents=[get_file_selection_arg_parser()],
    )
    parser.add_argument(
        "-F",
        "--full-data",
        action="store_true",
        help="""
        Display all data instead of only the rows and columns that have at least
        one value which is neither None nor the default for the type: 0 for
        numbers, "" for strings; booleans are always displayed.
        """,
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        metavar="OUTPUT_DIR",
        help=f"""
        Save the information under OUTPUT_DIR
        QUERY/CLASS_NAME.txt[{GZIP_FILE_SUFFIX}] files. The directory will be
        created as needed. If OUTPUT_DIR is specified as "auto" then it will
        default to $LMCREC_RUNTIME/query/INST/FIRST_TIMESTAMP--LAST_TIMESTAMP
        """,
    )
    parser.add_argument(
        "-z",
        "--compress-level",
        nargs="?",
        type=int,
        const=Z_DEFAULT_COMPRESSION,
        help=f"""
        Indicate that the output is to be compressed and optionally set the
        compression level, if it other than
        Z_DEFAULT_COMPRESSION={Z_DEFAULT_COMPRESSION}. 
        """,
    )
    parser.add_argument(
        "query_or_files",
        metavar="QUERY_OR_FILE",
        nargs="+",
        help=f"""
        query or query_file, the latter if it has {QUERY_FROM_FILE_SUFFIX!r} suffix
        """,
    )

    args = parser.parse_args()
    record_files_dir, from_ts, to_ts = process_file_selection_args(args)
    lmcrec_query = LmcrecQuery(
        record_files_dir,
        *args.query_or_files,
        from_ts=from_ts,
        to_ts=to_ts,
    )

    full_data = args.full_data
    output_dir = args.output_dir
    tmp_output_dir = None
    if output_dir == "auto":
        # First and last timestamps are not know until after the query: use a
        # temp dir and rename at the end:
        parent_output_dir = os.path.join(
            get_lmcrec_runtime(), "query", args.inst or "unknown"
        )
        tmp_output_dir = os.path.join(parent_output_dir, str(uuid4()))
        output_dir = tmp_output_dir

    output_formatter = FileTableFormatter(
        output_dir, compress_level=args.compress_level, full_data=full_data
    )

    exit_code = 0
    try:
        ret_code = lmcrec_query.run_with_callback(output_formatter)
        if ret_code != LmcrecScanRetCode.ATEOR:
            exit_code = 1
            print(
                f"Warning: query_state_cache returned {ret_code!r}, the results may be incomplete",
                file=sys.stderr,
            )

        if output_dir is not None:
            output_formatter.close()
            if tmp_output_dir is not None:
                first_ts = lmcrec_query.first_ts
                if first_ts is None:
                    first_ts = lmcrec_query.from_ts
                first_ts = (
                    format_ts(int(first_ts)) if first_ts is not None else "oldest"
                )
                last_ts = lmcrec_query.last_ts
                if last_ts is None:
                    last_ts = lmcrec_query.to_ts
                last_ts = format_ts(int(last_ts)) if last_ts is not None else "newest"
                output_dir = os.path.join(
                    parent_output_dir, "--".join([first_ts, last_ts])
                )
                os.makedirs(output_dir, exist_ok=True)
                print("Results saved under:", file=sys.stderr)
                for d in os.listdir(tmp_output_dir):
                    if d in {".", ".."}:
                        continue
                    tmp_d = os.path.join(tmp_output_dir, d)
                    if not os.path.isdir(tmp_d):
                        continue
                    final_d = os.path.join(output_dir, d)
                    if os.path.exists(final_d):
                        rmtree(final_d)
                    os.rename(tmp_d, final_d)
                    print(f"  {final_d!r}", file=sys.stderr)
                rmtree(tmp_output_dir)
                tmp_output_dir = None
    finally:
        if tmp_output_dir is not None:
            rmtree(tmp_output_dir)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
