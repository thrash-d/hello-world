import os
import subprocess
import sys

HELLO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hello.py")


def run(dead_stderr):
    # A pipe with its read end closed makes every write to it fail.
    r, w = os.pipe()
    os.close(r)
    try:
        return subprocess.run([sys.executable, HELLO], stdout=w,
                              stderr=w if dead_stderr else subprocess.PIPE)
    finally:
        os.close(w)


def test_prints_and_exits_0():
    p = subprocess.run([sys.executable, HELLO], capture_output=True, text=True)
    assert (p.returncode, p.stdout) == (0, "Hello, world!\n")


def test_dead_stdout_exits_1_with_one_line_on_stderr():
    p = run(dead_stderr=False)
    assert p.returncode == 1
    # bytes, since a localized OS error after the prefix may not be UTF-8
    assert p.stderr.startswith(b"hello.py: cannot write to stdout:")
    assert len(p.stderr.splitlines()) == 1


def test_dead_stdout_and_stderr_exits_1():
    assert run(dead_stderr=True).returncode == 1


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
