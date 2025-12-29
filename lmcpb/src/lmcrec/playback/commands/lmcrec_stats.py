#! /usr/bin/env python3

description = """
Given a (list of) record file(s) display stats regarding in/out instance and
variable count and scan time. This information can be used for fine tuning the
scan interval, e.g. using 10 x 90 percentile duration value. 
"""

import argparse
import statistics
import sys
from typing import Iterable, Tuple, Union

from tabulate import tabulate

Number = Union[float, int]

from codec import LmcrecFileDecoder, LmcrecType
from query import (
    build_lmcrec_file_chains,
    chain_to_file_list,
    get_file_selection_arg_parser,
    process_file_selection_args,
)

from .help_formatter import CustomWidthFormatter

# Number of quantiles per line:
Q_PER_LINE = 10


def underline(title: str, fh=sys.stdout) -> str:
    print(title, file=fh)
    print("=" * len(title), file=fh)


def get_stats(
    data: Iterable[Number],
    what: str = "",
    precision: int = 0,
) -> Tuple[str, Number, Number, Number, Number, Number, Number]:
    return (
        what,
        len(data),
        min(data),
        max(data),
        round(statistics.mean(data), precision),
        round(statistics.median(data), precision),
        round(statistics.stdev(data), precision),
    )


def build_quantiles(
    data: Iterable[Number],
    q_n: int = 10,
    precision: int = 0,
    q_method: str = "exclusive",
) -> Tuple[Iterable[str], Iterable[Number]]:
    pcts = tuple(f"{i/q_n * 100:.0f}%" for i in range(1, q_n))
    quants = tuple(
        round(q, precision) for q in statistics.quantiles(data, n=q_n, method=q_method)
    )
    return pcts, quants


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
        parents=[get_file_selection_arg_parser()],
    )
    parser.add_argument(
        "-q",
        "--quantiles",
        type=int,
        default=10,
        help="""
        The number of quantiles, use 0 to disable, default: %(default)d.
        Applicable for scan duration only.
        """,
    )
    parser.add_argument(
        "lmcrec_file",
        nargs="*",
        help="""
        Specific lmcrec file(s) for which to collect the stats, they override
        the query style selection
        """,
    )
    args = parser.parse_args()

    q_n = min(args.quantiles, 100)

    lmcrec_files = args.lmcrec_file

    if not lmcrec_files:
        record_files_dir, from_ts, to_ts = process_file_selection_args(args)
        lmcrec_file_chains = build_lmcrec_file_chains(record_files_dir, from_ts, to_ts)
        lmcrec_files = chain_to_file_list(lmcrec_file_chains)

    durations = []
    in_byte_counts = []
    scan_in_inst_counts = []
    scan_in_var_counts = []
    scan_out_var_counts = []
    for lmcrec_file in lmcrec_files:
        print(f"Processing {lmcrec_file!r} ... ", end="", file=sys.stderr)
        try:
            decoder = LmcrecFileDecoder(lmcrec_file)
            while True:
                record = decoder.next_record()
                if record.record_type == LmcrecType.DURATION_USEC:
                    durations.append(record.value)
                elif record.record_type == LmcrecType.SCAN_TALLY:
                    in_byte_counts.append(record.scan_in_byte_count)
                    scan_in_inst_counts.append(record.scan_in_inst_count)
                    scan_in_var_counts.append(record.scan_in_var_count)
                    scan_out_var_counts.append(record.scan_out_var_count)
                elif record.record_type == LmcrecType.EOR:
                    print("OK", file=sys.stderr)
                    break
        except (EOFError, RuntimeError, ValueError) as e:
            print(e, file=sys.stderr)

    headers = ("", "# points", "min", "max", "mean", "median", "stdev")

    rows = []
    for data, what, precision in [
        (in_byte_counts, "in byte#", 0),
        (scan_in_inst_counts, "in inst#", 0),
        (scan_in_var_counts, "in var#", 0),
        (scan_out_var_counts, "out var#", 0),
    ]:
        rows.append(get_stats(data, what, precision))

    print()
    underline("In/Out Stats")
    print(tabulate(rows, headers=headers))
    print()

    rows = []
    for data, what, precision in [
        (durations, "scan duration (sec)", 6),
    ]:
        rows.append(get_stats(data, what, precision))
    print()
    underline("Scan Duration Stats")
    print(tabulate(rows, headers=headers))
    print()

    if q_n > 0:
        rows = []
        pcts, quants = build_quantiles(
            durations,
            q_n=q_n,
            precision=6,
        )
        n = len(quants)
        print()
        print("Quantile:")
        for i in range(0, n, Q_PER_LINE):
            print(
                tabulate(
                    [quants[i : i + Q_PER_LINE]],
                    headers=pcts[i : i + Q_PER_LINE],
                    tablefmt="plain",
                    floatfmt=".06f",
                )
            )
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
