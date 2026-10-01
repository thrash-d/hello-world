#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print "Hello, world!".

On Windows run it as `py -3 hello.py`; the shebang only applies on Unix.
Exit 0 when the line was written, 1 when stdout could not be written.
"""
import os
import sys


def main():
    try:
        # flush so a dead stdout raises here, not at interpreter exit
        print("Hello, world!", flush=True)
    except OSError as e:
        try:
            print(f"hello.py: cannot write to stdout: {e}", file=sys.stderr,
                  flush=True)
        except OSError:
            pass
        # A failed write stays buffered, and the shutdown flush would fail
        # again and turn exit 1 into 120. _exit skips that flush.
        os._exit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
