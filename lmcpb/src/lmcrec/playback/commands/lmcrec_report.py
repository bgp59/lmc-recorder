#! /usr/bin/env python3


description = f"""
Create a tar archive with the relevant files for a given instance and time
window. This is useful for sending the information to outside experts.

The command requires an instance and a time window; the archive will contain all
files covering an interval that intersects with the time window.

The archive name is ORG--INST--FIRST_TS--LAST_TS where:

    ORG                 = the organization name, normalized such that it can 
                          be used in file paths
    INST                = instance
    FIRST_TS, LAST_TS   = the first (oldest) and the last (newest) of the
                          timestamps from the selected files.

The content of the archive is as follows:

    ORG--INST--FIRST_TS--LAST_TS/YYYY-MM-DD/HH:MM:SS±HH:MM.lmcrec*
    ORG--INST--FIRST_TS--LAST_TS/LMCREC_TZ

The organization name is set by command line arg or it is picked from
the config file.

This naming schema is intended to be both self-descriptive and to avoid clashes
w/ other reports.
    
"""

import argparse
import os
import re
import sys
from shutil import rmtree

from codec import (
    INDEX_FILE_SUFFIX,
    INFO_FILE_SUFFIX,
)
from config import get_lmcrec_runtime, lookup_lmcrec_config_file
from misc.timeutils import format_ts, get_lmcrec_tz
from query import (
    build_lmcrec_file_chains,
    get_file_selection_arg_parser,
    process_file_selection_args,
)

from .help_formatter import CustomWidthFormatter

DEFAULT_ORG = "anon"


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
        parents=[get_file_selection_arg_parser()],
    )
    parser.add_argument(
        "-O",
        "--org-name",
        help=f"""
        The organization name, used to override the config file setting;
        is neither is set it defaults to {DEFAULT_ORG!r}
        """,
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="""
        Where to store the archive, default: $LMCREC_RUNTIME/report/INST
        """,
    )
    args = parser.parse_args()

    inst = args.inst
    if inst is None:
        print("Command requires --inst INST", file=sys.stderr)
        return 1

    record_files_dir, from_ts, to_ts = process_file_selection_args(args)
    if from_ts is None or to_ts is None:
        print("Command requires --from/--to time window", file=sys.stderr)
        return 1

    org_name = (
        args.org_name
        or lookup_lmcrec_config_file(inst, args.config, "organization")
        or DEFAULT_ORG
    )

    # Normalize org_name:
    org_name = re.sub(r"[^0-9a-z._-]+", "_", org_name.lower())
    if not re.match(r"[a-z0-9]", org_name):
        org_name = "_" + org_name

    lmcrec_file_chains = build_lmcrec_file_chains(record_files_dir, from_ts, to_ts)
    if not lmcrec_file_chains:
        print("No files match the time window", file=sys.stderr)
        return 0

    output_dir = args.output_dir
    if output_dir is None:
        output_dir = os.path.join(get_lmcrec_runtime(), "report", inst)
    report_files = []
    first_ts, last_ts = None, None

    strip_path = f"{record_files_dir}/"
    for entry in lmcrec_file_chains:
        while entry is not None:
            if first_ts is None:
                first_ts = entry.lmcrec_info.start_ts
            last_ts = entry.lmcrec_info.most_recent_ts
            lmcrec_file = entry.file_name
            report_files.append(os.path.relpath(lmcrec_file, strip_path))
            for suffix in [INDEX_FILE_SUFFIX, INFO_FILE_SUFFIX]:
                extra_file = lmcrec_file + suffix
                if os.path.exists(extra_file):
                    report_files.append(os.path.relpath(extra_file, strip_path))
            entry = entry.next

    if first_ts is None:
        print("Could not infer first timestamp from selection", file=sys.stderr)
        return 1
    if last_ts is None:
        print("Could not infer last timestamp from selection", file=sys.stderr)
        return 1

    archive_prefix = "--".join(
        [
            org_name,
            inst,
            format_ts(int(first_ts)).replace(":", "-"),
            format_ts(int(last_ts)).replace(":", "-"),
        ]
    )

    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)
    if os.path.exists(archive_prefix):
        rmtree(archive_prefix)

    # Stage
    src_files = []
    for f_path in report_files:
        rel_dir = os.path.dirname(f_path)
        if rel_dir and rel_dir != ".":
            to_dir = os.path.join(archive_prefix, "rec", rel_dir)
        else:
            to_dir = os.path.join(archive_prefix, "rec")
        os.makedirs(to_dir, exist_ok=True)
        from_file = os.path.join(record_files_dir, f_path)
        to_file = os.path.join(to_dir, os.path.basename(f_path))
        os.symlink(from_file, to_file)
        src_files.append(to_file)
    lmcrec_tz_file = os.path.join(archive_prefix, "LMCREC_TZ")
    with open(lmcrec_tz_file, "wt") as f:
        print(get_lmcrec_tz(), file=f)
    src_files.append(lmcrec_tz_file)
    archive_file = archive_prefix + ".lmcrec.tgz"
    exit_code = os.system(
        f'tar --dereference -czf {archive_file} {" ".join(src_files)}'
    )
    rmtree(archive_prefix)
    if exit_code == 0:
        print(f"{os.path.realpath(archive_file)} created", file=sys.stderr)
    return exit_code >> 8


if __name__ == "__main__":
    sys.exit(main())
