#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print "Hello, world!".

On Windows run it as `py -3 hello.py`; the shebang only applies on Unix.
Exit 0 when the line was written, 1 when stdout could not be written.
"""
import os
import sys


def _silence(stream):
    # A failed write leaves its text buffered, and the shutdown flush fails
    # again and turns the exit code into 120. Point the fd at devnull instead.
    os.dup2(os.open(os.devnull, os.O_WRONLY), stream.fileno())


def main():
    try:
        # flush so a dead stdout raises here, not at interpreter exit
        print("Hello, world!", flush=True)
    except OSError as e:
        _silence(sys.stdout)
        try:
            print(f"hello.py: cannot write to stdout: {e}", file=sys.stderr)
        except OSError:
            _silence(sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
