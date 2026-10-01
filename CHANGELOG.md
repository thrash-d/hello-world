# Changelog

## 2026-09-30: Exit 1 on dead stdout or stderr instead of 120

The second hello.py review answered here.

- A failed stderr write in the error handler is now caught. The review said: "If stdout is dead *and* stderr is also unusable, the handler's `print(..., file=sys.stderr)` raises a second `OSError` that is not caught."
- After a failed write, the stream's fd is pointed at devnull. Testing the finding above showed a worse bug the review missed: with only stdout dead, the script exited 120, not 1. The failed text stays buffered, and Python's shutdown flush fails a second time. The both-dead case also exited 120.
- A module docstring now gives the Windows invocation and the exit codes. The review said: "operators must still call an explicit interpreter" and "Exit-code contract is implicit. ... Document it if this is used as a health check."

Tested by running the script against a pipe with a closed read end, as stdout alone and then as both stdout and stderr. Both cases now exit 1, and the normal and redirected runs still print the line and exit 0.
