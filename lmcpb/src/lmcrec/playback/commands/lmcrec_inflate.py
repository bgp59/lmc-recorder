#! /usr/bin/env python3

description = """
Inflate deflate(d) REST response, for instance one captured using:

    curl -H 'Accept-Encoding: deflate' -o OUT_FILE URL

Notes:

    1. It should be used only if the response contains the following header:

        Content-Encoding: deflate
    
    2. gunzip / gzip -d commands cannot be used directly on that file since they
       would fail with:

            gzip: unknown compression format

       error

    3. The JSON body of the response is not formatted (one single very, very
       long line, that is), so is best passed through `jq':

            lmcrec-inflate RESP_FILE | jq

"""

import argparse
import sys

from misc.deflate import Inflate

from .help_formatter import CustomWidthFormatter


def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomWidthFormatter,
        description=description,
    )
    parser.add_argument("deflate_file")
    parser.add_argument(
        "out_file",
        nargs="?",
        help="""Output file, if not specified then it defaults to stdout. Since
        the original content is not indented or line separated, it is advisable
        to pipe the output through `jq'
        """,
    )
    args = parser.parse_args()
    out_file = args.out_file

    in_f = Inflate(args.deflate_file)
    if out_file:
        out_f = open(out_file, "wb")
    else:
        out_f = sys.stdout.buffer

    while True:
        data = in_f.read(65536)
        if not data:
            break
        out_f.write(data)

    if out_file:
        out_f.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
