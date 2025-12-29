#!/usr/bin/env python3

"""Wrap text w/ "<br>" for markdown columns"""

import sys
import textwrap

width = int(sys.argv[1] if len(sys.argv) > 1 else 72)
joiner = "<br>"

while True:
    try:
        line = input("line> ")
        line = line.replace(joiner, " ")
        print()
        print(joiner.join(textwrap.wrap(line, width)))
        print()
    except EOFError:
        break
print()
