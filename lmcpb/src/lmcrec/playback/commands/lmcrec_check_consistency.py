#! /usr/bin/env python3

description = """
Check the consistency between a number of sample files captured by
snap-samples.sh and the state cache updated from the record file generated
from those samples. This is an end-to-end sanity check for the recording +
playback tools.

The sample files are sorted in ascending order of their sample# suffix. After
each sample file is loaded, the state cache is updated with the next scan (which
was based on that very file) and the loaded data is compared against the cache.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from http.client import parse_headers
from typing import Any, Dict, List, Optional, Tuple

from cache import LmcrecScanRetCode, LmcrecStateCache
from codec import LmcrecFileDecoder, LmcVarType
from misc.deflate import Inflate
from misc.timeutils import format_ts
from tabulate import SEPARATING_LINE, tabulate

from .help_formatter import CustomWidthFormatter

# The following definitions should match lmcrec/recorder/sample_recorder.go:
SAMPLE_RESPONSE_BODY_FILE_PREFIX = "response-body"
SAMPLE_RESPONSE_HEADERS_FILE_PREFIX = "response-headers"
SAMPLE_RECORDER_FILE_PREFIX = "samples.lmcrec"
SAMPLE_RECORDER_FILE_SUFFIX = ".gz"

# The recorder uses the file mtime converted to microseconds (Time.UnixMicro())
# and the playback will converted it back to a float. This tool uses mtime
# directly as reference so there may be slight differences when comparing them,
# allow for the 2 timestamps to differ, in absolute value, by up to the next
# limit:
TIMESTAMP_MAX_DIFF_SEC = 0.00001  # 10 microsec


def underline(title, file=sys.stdout):
    print(title, file=file)
    print("=" * len(title), file=file)
    print(file=file)


# Map LMC REST -> parser type, should match lmcrec/parser/parser.go:
lmc_var_type_map = {
    "Boolean": LmcVarType.BOOLEAN,
    "Boolean Config": LmcVarType.BOOLEAN_CONFIG,
    "Counter": LmcVarType.COUNTER,
    "Gauge": LmcVarType.GAUGE,
    "Gauge Config": LmcVarType.GAUGE_CONFIG,
    "Numeric": LmcVarType.NUMERIC,
    "Large Numeric": LmcVarType.LARGE_NUMERIC,
    "Numeric Range": LmcVarType.NUMERIC_RANGE,
    "Numeric Config": LmcVarType.NUMERIC_CONFIG,
    "String": LmcVarType.STRING,
    "String Config": LmcVarType.STRING_CONFIG,
}


def extract_numeric_range(val: str) -> int:
    """'N (MIN..MAX)' -> N"""
    return int(val.split(None, 2)[0])


extract_val_fn_by_type = {"Numeric Range": extract_numeric_range}


def load_sample_file(
    sample_file: str, force_compressed: bool = False
) -> Tuple[List[Dict[str, Any]], int]:

    header_file = sample_file.replace(
        SAMPLE_RESPONSE_BODY_FILE_PREFIX, SAMPLE_RESPONSE_HEADERS_FILE_PREFIX
    )
    content_length, compressed = -1, sample_file.endswith(".gz")
    if os.path.exists(header_file):
        compressed = False
        with open(header_file, "rb") as f:
            f.readline()
            headers_message = parse_headers(f)
            for hdr, val in headers_message.items():
                if hdr == "Content-Encoding":
                    compressed = val == "deflate"
                elif hdr == "Content-Length":
                    content_length = int(val)

    if force_compressed or compressed:
        f = Inflate(sample_file)
    else:
        f = open(sample_file, "rb")
    sample_inst_list = json.load(f)
    f.close()
    return sample_inst_list, content_length


def compare_instances(
    sample_inst_list: List[Dict[str, Any]], state_cache: LmcrecStateCache
) -> Tuple[bool, int, int]:

    sample_instances = set()
    sample_classes = set()

    missing_instances = set()
    instances_without_class = set()
    instances_with_wrong_class = dict()  # value: (want, got)
    instances_with_wrong_parent = dict()  # value: (want, got)
    instances_with_var_diffs = (
        dict()
    )  # value: list[(var_name, occur#/total#, what, want, got)]
    classes_with_missing_vars = defaultdict(set)

    scan_in_inst_var_count = [0, 0]

    def cmp_inst(
        sample_inst: Dict[str, Any], sample_parent: Optional[Dict[str, Any]] = None
    ):
        sample_inst_name = sample_inst["Instance"]
        sample_class_name = sample_inst["Class"]
        sample_variables = sample_inst["Variables"]

        scan_in_inst_var_count[0] += 1
        scan_in_inst_var_count[1] += len(sample_variables)

        sample_instances.add(sample_inst_name)
        sample_classes.add(sample_class_name)

        cache_inst = state_cache.inst_by_name.get(sample_inst_name)
        if cache_inst is None:
            missing_instances.add(sample_inst_name)
            return False

        sample_inst_parent_name = (
            sample_parent["Instance"] if sample_parent is not None else None
        )
        cache_inst_parent_name = None
        if cache_inst.parent_inst_id:
            cache_parent_inst = state_cache.inst_by_id.get(cache_inst.parent_inst_id)
            if cache_parent_inst is not None:
                cache_inst_parent_name = cache_parent_inst.name
        if sample_inst_parent_name != cache_inst_parent_name:
            instances_with_wrong_parent[sample_inst_name] = (
                sample_inst_parent_name,
                cache_inst_parent_name,
            )

        cache_inst_class = state_cache.class_by_id.get(cache_inst.class_id)
        if cache_inst_class is None:
            instances_without_class.add(sample_inst_name)
            return False

        want, got = sample_class_name, cache_inst_class.name
        if want != got:
            instances_with_wrong_class[sample_inst_name] = (want, got)
            return False
        cache_class_var_info = cache_inst_class.var_info_by_name

        cache_variables = cache_inst.vars
        var_occur_cnt = defaultdict(int)
        diffs = []
        sample_variables = set()
        for var in sample_variables:
            var_name, var_type, var_val = var["Name"], var["Type"], var["Value"]
            sample_variables.add(var_name)
            extract_val_fn = extract_val_fn_by_type.get(var_type)
            if extract_val_fn is not None:
                var_val = extract_val_fn(var_val)
            var_occur_cnt[var_name] += 1

            cache_var_info = cache_class_var_info.get(var_name)
            if cache_var_info is None:
                classes_with_missing_vars[sample_class_name].add(var_name)
                continue
            what = "Type"
            want, got = lmc_var_type_map[var_type], cache_var_info.var_type
            if want == got:
                what = "Value"
                want, got = var_val, cache_variables.get(cache_var_info.var_id)
            if want != got:
                diffs.append((var_name, var_occur_cnt[var_name], what, want, got))
        if diffs:
            report_diffs = []
            for var_name, var_occur, what, want, got in diffs:
                total_occur_cnt = var_occur_cnt[var_name]
                var_occur = (
                    f"{var_occur}/{total_occur_cnt}" if total_occur_cnt > 1 else ""
                )
                report_diffs.append((var_name, var_occur, what, want, got))
            instances_with_var_diffs[sample_inst_name] = report_diffs

        return

    def cmp_inst_list(
        sample_inst_list: List[Dict[str, Any]], sample_parent: Optional[str] = None
    ):
        for sample_inst in sample_inst_list:
            cmp_inst(sample_inst, sample_parent)
            cmp_inst_list(sample_inst["Children"], sample_inst)
        return

    cmp_inst_list(sample_inst_list)

    cmp_ok = True

    if missing_instances:
        underline("Missing Instances")
        for sample_inst_name in sorted(missing_instances):
            print(f"  {sample_inst_name}")
        print()
        cmp_ok = False

    if instances_with_wrong_parent:
        rows = sorted(
            (sample_inst_name, want, got)
            for sample_inst_name, (want, got) in instances_with_wrong_class.items()
        )
        underline("Instances With Wrong Parent")
        print(tabulate(rows, headers=["Instance", "Want", "Got"]))
        print()
        cmp_ok = False

    if instances_without_class:
        underline("Instances Without Class")
        for sample_inst_name in sorted(instances_without_class):
            print(f"  {sample_inst_name}")
        print()
        cmp_ok = False

    if instances_with_wrong_class:
        rows = sorted(
            (sample_inst_name, want, got)
            for sample_inst_name, (want, got) in instances_with_wrong_class.items()
        )
        underline("Instances With Wrong Class")
        print(tabulate(rows, headers=["Instance", "Want", "Got"]))
        print()
        cmp_ok = False

    unexpected_instances = set(state_cache.inst_by_name) - sample_instances
    if unexpected_instances:
        underline("Unexpected Instances")
        for sample_inst_name in sorted(unexpected_instances):
            print(f"  {sample_inst_name}")
        print()
        cmp_ok = False

    if instances_with_var_diffs:
        underline("Instances With Variable Differences")
        rows = []
        for sample_inst_name in sorted(instances_with_var_diffs):
            diffs = sorted(instances_with_var_diffs[sample_inst_name])
            row = [sample_inst_name] + [None] * 5
            for i in range(5):
                row[i + 1] = "\n".join(map(str, (d[i] for d in diffs)))
            rows.append(row)
            rows.append(SEPARATING_LINE)
        print(
            tabulate(
                rows, headers=["Instance", "Variable", "Occur", "What", "Want", "Got"]
            )
        )
        print()
        cmp_ok = False

    if classes_with_missing_vars:
        underline("Classes With Missing Variables ")
        rows = []
        for sample_class_name in sorted(classes_with_missing_vars):
            rows.append(
                (sample_class_name),
                "\n".join(sorted(classes_with_missing_vars[sample_class_name])),
            )
            rows.append(SEPARATING_LINE)
        print(tabulate(rows, headers=["Class", "Missing"]))
        cmp_ok = False

    # Classes without instances are not removed from state cache on the
    # assumption that instances with such classes may reappear in the future.
    # Exclude such classes from unexpected classes check.
    unexpected_classes = [
        c
        for c in set(state_cache.class_by_name) - sample_classes
        if state_cache.inst_by_class_name.get(c)
    ]
    if unexpected_classes:
        underline("Unexpected Classes")
        for sample_class_name in sorted(unexpected_classes):
            print(f"  {sample_class_name}")
        print()
        cmp_ok = False

    return cmp_ok, scan_in_inst_var_count[0], scan_in_inst_var_count[1]


def run_consistency_check(
    sample_file_list: List[str],
    state_cache: LmcrecStateCache,
    no_timestamp_check: bool = False,
) -> bool:
    sample_num = 0
    all_ok = True
    for sample_file in sample_file_list:
        sample_num += 1
        print(f"Load sample#{sample_num} from {sample_file!r}")
        sample_inst_list, content_length = load_sample_file(sample_file)
        print("Apply next scan to the state cache")
        state_code = state_cache.apply_next_scan()
        if state_code != LmcrecScanRetCode.COMPLETE:
            raise RuntimeError(
                f"want: {LmcrecScanRetCode.COMPLETE!r}, got {state_code!r}"
            )
        if sample_num != state_cache.num_scans:
            raise RuntimeError(
                f"state_cache.num_scans: want: {sample_num}, got: {state_cache.num_scans}"
            )

        print("Check consistency")
        check_ok = True
        if not no_timestamp_check:
            want_ts = os.stat(sample_file).st_mtime
            got_ts = state_cache.ts
            d_ts = abs(want_ts - got_ts)
            if d_ts > TIMESTAMP_MAX_DIFF_SEC:
                print(
                    f"timestamp difference: want <= {TIMESTAMP_MAX_DIFF_SEC:.06f}, got: {d_ts:.06f} sec"
                )
                print(
                    f"   want: {format_ts(want_ts)} ({want_ts})\n    got: {format_ts(got_ts)} ({got_ts})"
                )
                check_ok = False

        cmp_ok, scan_in_inst_count, scan_in_var_count = compare_instances(
            sample_inst_list, state_cache
        )
        if not cmp_ok:
            check_ok = False

        for what, want, got in [
            ("byte count", content_length, state_cache.scan_tally.scan_in_byte_count),
            (
                "sample_inst count",
                scan_in_inst_count,
                state_cache.scan_tally.scan_in_inst_count,
            ),
            ("var count", scan_in_var_count, state_cache.scan_tally.scan_in_var_count),
        ]:
            if want != got:
                print(f"{what}: want: {want}, got: {got}")
                check_ok = False
        if check_ok:
            print("OK")
        else:
            all_ok = False
        print()

    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
    )
    parser.add_argument(
        "-s",
        "--start-sample-num",
        type=int,
        default=1,
        help="""Start sample#, default: %(default)d""",
    )
    parser.add_argument(
        "-e",
        "--end-sample-num",
        type=int,
        default=-1,
        help="""End sample#, if different than last. Use -1 for last, default:
             %(default)d""",
    )
    parser.add_argument(
        "-T",
        "--no-timestamp-check",
        action="store_true",
        help="""Disable timestamp check. The timestamp is inferred from mtime of
             the sample files and if the latter were altered by accident then
             the check is not possible anymore.""",
    )

    parser.add_argument("sample_dir")
    args = parser.parse_args()
    os.chdir(args.sample_dir)

    start_sample_num = args.start_sample_num
    if start_sample_num < 1:
        start_sample_num = 1
    end_sample_num = args.end_sample_num
    if end_sample_num > 0 and end_sample_num < start_sample_num:
        print(
            f"end sample# {end_sample_num} < {start_sample_num} start sample#, nothing to check",
            file=sys.stderr,
        )
        return 1

    want_range = start_sample_num > 1 or end_sample_num > 0
    sample_files = dict()
    min_sample_num, max_sample_num = -1, -1
    for fname in os.listdir("."):
        m = re.match(f"{SAMPLE_RESPONSE_BODY_FILE_PREFIX}.(\d+)$", fname)
        if not m:
            continue
        sample_num = int(m.group(1))
        if want_range:
            if (
                sample_num < start_sample_num
                or end_sample_num > 0
                and end_sample_num < sample_num
            ):
                continue
            if min_sample_num == -1 or sample_num < min_sample_num:
                min_sample_num = sample_num
            if max_sample_num == -1 or sample_num > max_sample_num:
                max_sample_num = sample_num
        sample_files[sample_num] = fname

    if not sample_files:
        print("Empty sample file list, nothing to check")
        return 0

    sample_file_list = [sample_files[sample_num] for sample_num in sorted(sample_files)]

    recorder_file_prefix = SAMPLE_RECORDER_FILE_PREFIX
    if min_sample_num != -1:
        recorder_file_prefix += f".{min_sample_num}"
        if min_sample_num < max_sample_num:
            recorder_file_prefix += f"-{max_sample_num}"
    recorder_file = recorder_file_prefix + SAMPLE_RECORDER_FILE_SUFFIX
    print(f"Using recorder file {recorder_file!r}\n")
    state_cache = LmcrecStateCache(LmcrecFileDecoder(recorder_file))
    all_ok = run_consistency_check(sample_file_list, state_cache)

    if all_ok:
        print("All OK")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
