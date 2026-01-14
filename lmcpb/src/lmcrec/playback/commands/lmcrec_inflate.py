#! /usr/bin/env python3

description = """
Inflate deflate(d) REST response, for instance one captured using:

    curl -H 'Accept-Encoding: deflate' -o OUT_FILE URL

and display it in indented JSON format, to make it more human readable (The JSON
body of the response a single, very long line).

Note that gunzip / gzip -d commands cannot be used directly on body response
file since they would fail with:
    
    gzip: unknown compression format

If the response was not deflated simply read its content as-is.

"""

import argparse
import json
import sys

from .help_formatter import CustomWidthFormatter
from .lmcrec_check_consistency import load_body_response


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
    )
    parser.add_argument(
        "-r",
        "--raw",
        action="store_true",
        help="""Disable JSON format, print the raw output raw. Useful to perform
        strictly inflation.""",
    )
    parser.add_argument(
        "response_body_file", help="""Response body file, potentially deflated."""
    )
    parser.add_argument(
        "out_file",
        nargs="?",
        help="""Output file, if not specified then it defaults to stdout.""",
    )
    args = parser.parse_args()
    raw = args.raw
    out_file = args.out_file

    body = load_body_response(args.response_body_file, raw=raw)
    if not raw:
        body = bytes(json.dumps(body, indent=2) + "\n", "utf-8")
    if out_file:
        with open(out_file, "wb") as f:
            f.write(body)
    else:
        sys.stdout.buffer.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
