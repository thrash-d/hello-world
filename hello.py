#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys


def main():
    try:
        # flush so a dead stdout raises here, not at interpreter exit
        print("Hello, world!", flush=True)
    except OSError as e:
        print(f"hello.py: cannot write to stdout: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
