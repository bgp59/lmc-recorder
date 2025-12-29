#! /usr/bin/env python3

"""LMC Schema Merger"""


description = """
Merge multiple LMC schemas built by lmcrec-inventory commands into a common one.

This is needed when importing lmcrec data from multiple instances of LSEG
components (e.g. adh or ads) into the same database. 

LMC classes are mapped into DB tables and their variables are mapped into
columns. Each instance, depending on its specific configuration and/or operating
condition may have only a subset of the classes and variables. If the data comes
from multiple instances then the DB lmcrec_schema should be the superset of each
individual one. 
"""

import argparse
import os
import sys

import yaml

from .help_formatter import CustomWidthFormatter
from .lmcrec_schema import LmcrecSchema, merge_lmcrec_schema


def save_schema(lmcrec_schema: LmcrecSchema, fh=sys.stdout):
    yaml.safe_dump(lmcrec_schema, fh, indent=2, sort_keys=True)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
    )
    parser.add_argument(
        "-m",
        "--merge-into",
        metavar="MERGED_SCHEMA_FILE",
        help="""
        Destination .yaml file for the merged schemas. If the file exists then
        it updated as needed with new information, if not then it is created. If
        not specified then the merged info is displayed to stdout.
        """,
    )
    parser.add_argument(
        "schema_file",
        metavar="SCHEMA_FILE",
        nargs="+",
        help="""Lmcrec schema file from the inventory""",
    )
    args = parser.parse_args()
    merge_into = args.merge_into

    if merge_into and os.path.exists(merge_into):
        with open(merge_into, "rt") as f:
            into_schema = yaml.safe_load(f)
    else:
        into_schema = None

    updated = False
    for schema_file in args.schema_file:
        with open(schema_file, "rt") as f:
            new_schema = yaml.safe_load(f)
        if into_schema is None:
            into_schema = new_schema
            continue
        if merge_lmcrec_schema(into_schema, new_schema):
            updated = True

    if not merge_into:
        save_schema(into_schema)
    elif updated:
        os.makedirs(os.path.dirname(merge_into), exist_ok=True)
        with open(merge_into, "wt") as fh:
            save_schema(into_schema, fh)
        print(f"{merge_into!r} updated", file=sys.stderr)
    else:
        print(f"{merge_into!r} was up-to-date", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
