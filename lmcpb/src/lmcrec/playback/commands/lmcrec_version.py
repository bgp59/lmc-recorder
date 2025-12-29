#! /usr/bin/env python3

description = """
Display version and git commit info
"""

import argparse
import sys

import buildinfo

from .help_formatter import CustomWidthFormatter


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
    )
    parser.add_argument(
        "-g", "--git-info", action="store_true", help="""Include git commit info"""
    )
    args = parser.parse_args()

    print(f"{buildinfo.version}", end="")
    if args.git_info:
        print(f", Git commit = {buildinfo.gitinfo}", end="")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
