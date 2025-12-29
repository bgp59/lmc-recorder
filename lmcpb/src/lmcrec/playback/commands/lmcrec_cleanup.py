#! /usr/bin/env python3

description = """
Cleanup older daily records for all instances in the config file
"""

import argparse
import os
import re
import shutil
import sys
import time

from config import (
    LMCREC_CONFIG_FILE_DEFAULT,
    LMCREC_CONFIG_FILE_ENV_VAR,
    LMCREC_CONFIG_RECORDERS_BY_INST_KEY,
    get_lmcrec_config_file,
    load_lmcrec_config,
    lookup_lmcrec_config,
)
from misc.timeutils import format_ts

from .help_formatter import CustomWidthFormatter

KEEP_N_DAYS_KEY = "keep_n_days"
RECORD_FILES_DIR_KEY = "record_files_dir"


def log(txt: str):
    print(format_ts(int(time.time())), "-", "lmcrec-cleanup", "-", txt, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
    )
    parser.add_argument(
        "-c",
        "--config",
        help=f"""
        Config file, it defaults to env var ${LMCREC_CONFIG_FILE_ENV_VAR}, or if
        the latter is not set, to {LMCREC_CONFIG_FILE_DEFAULT!r}.
        """,
    )
    parser.add_argument(
        "-n",
        "--keep-n-days-fallback",
        type=int,
        default=0,
        help=f"""
        If > 0, fallback for the {KEEP_N_DAYS_KEY} parameter from the config
        file for each instance.
        """,
    )
    parser.add_argument(
        "-N",
        "--keep-n-days-override",
        type=int,
        default=0,
        help=f"""
        If > 0, override for the {KEEP_N_DAYS_KEY} parameter from the config
        file for each instance.
        """,
    )

    args = parser.parse_args()
    keep_n_days_fallback = args.keep_n_days_fallback or 0
    keep_n_days_override = args.keep_n_days_override or 0
    config_file = get_lmcrec_config_file(args.config)
    log(f"Use config file {config_file!r}")
    config = load_lmcrec_config(config_file)
    config_by_inst = config.get(LMCREC_CONFIG_RECORDERS_BY_INST_KEY)
    if not config_by_inst:
        log("No instances found in config file {config_file!r}")
        return 0
    if keep_n_days_override > 0:
        log(f"{KEEP_N_DAYS_KEY} override: {keep_n_days_override}")
    elif keep_n_days_fallback:
        log(f"{KEEP_N_DAYS_KEY} fallback: {keep_n_days_fallback}")
    for inst in config_by_inst:
        record_files_dir = lookup_lmcrec_config(
            config, inst, RECORD_FILES_DIR_KEY, expand=True
        )
        if record_files_dir is None:
            log(f"Skip instance {inst!r}, no record files dir configured")
            continue
        inst_keep_n_days = (
            keep_n_days_override
            or lookup_lmcrec_config(config, inst, KEEP_N_DAYS_KEY)
            or keep_n_days_fallback
            or 0
        )
        if inst_keep_n_days <= 0:
            log(f"Cleanup disabled for instance {inst!r}")
            continue
        log(
            f"Keep at most {inst_keep_n_days} recording day(s) for instance {inst!r} under {record_files_dir!r}"
        )
        rec_day_dirs = {}
        for d in os.listdir(record_files_dir):
            if re.match(r"\d{4}-\d{2}-\d{2}", d):
                p = os.path.join(record_files_dir, d)
                if os.path.isdir(p):
                    rec_day_dirs[d] = p
        rec_days = sorted(rec_day_dirs)
        to_delete = rec_days[:-inst_keep_n_days]
        if to_delete:
            log(f"Remove {to_delete}")
            for d in to_delete:
                shutil.rmtree(rec_day_dirs[d])

    return 0


if __name__ == "__main__":
    sys.exit(main())
