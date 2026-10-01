# Changelog

## 2026-09-30: Version 1.0.0 and install from a release tag

The fifth review, for five workstations, answered here.

- New `VERSION` file at 1.0.0. The existing auto-tag workflow tags `v1.0.0` on push, and each bump after that gets its own tag. The review said: "Tag a release, install that tag, record the commit on the five machines."
- The `install.ps1` help now says to clone a release tag into a new folder under `C:\ProgramData` as administrator, check `git rev-parse HEAD` against the reviewed commit, and run the installer there. The review said: "clone or copy a **pinned tag/commit** to an admin-only directory, then run `.\install.ps1`."

Finding 2, "`FileSystemRights` bitmask is not trustworthy", needed no change; see `BACKLOG.md`. Tested by storing ACEs with generic rights on a file, through icacls and through SDDL. Windows mapped them to specific rights both times, and the check refused every grant that included write: GW, GA, and GR with GW. GR alone and GR with GX passed. `GENERIC_WRITE` is bit 30, not the sign bit, and widening a negative int32 to int64 keeps the low 32 bits, so no write bit is lost.

Also tested: a folder created under `C:\ProgramData` and the two copied files passed the source check. The only account flagged was the creator, a standard user in the test. When an administrator creates the folder, that entry is Administrators. `python test_hello.py` passes.

## 2026-09-30: Refuse an installer source that non-admins can change

The fourth review, covering hello.py, install.ps1, and test_hello.py, answered here.

- `install.ps1` now refuses to run when a non-administrator can change `install.ps1`, `hello.py`, or any folder above them up to the drive root. It also refuses when such an account owns one of them. The review said: "If an admin right-clicks `install.ps1` in `Downloads` / Desktop / a share the user can write, another process can swap `hello.py` (or the script) before `Copy-Item`."
- The pinned Python path must now match `Program Files\Python3*\python.exe` with no `"`, `%`, or `&`. The review said: "A PEP 514 `ExecutablePath` that contained `&`, `%`, or `"` would break quoting or, in ugly cases, run extra commands."
- After installing, the same check runs on the install folder, `hello.py`, and `hello.cmd`, and Users must have read and run access to each. The review said: "The smoke test runs as SYSTEM/Administrator. It does not prove Users-only `RX`" and "You do not verify the resulting DACL contains exactly those three SIDs."
- The test-run output is compared as one string. The review said: "`& hello.cmd` sometimes yields an array or a trailing CR."
- `test_hello.py` compares stderr as bytes. The review said: "A localized `OSError` string can theoretically trip the 'starts with / one line' asserts."

Tested without admin rights on a dev machine by loading the check from `install.ps1`. It refused the repo folder once the account running it wasn't the folder's owner. It also refused the repo folder for its owner, because an orphaned account SID has write access on a folder above it. It passed `Program Files\Git` up to `C:\` and `System32\notepad.exe`. On a scratch folder with the installer's three access entries, the post-install check passed; after Authenticated Users got modify on `hello.py`, it refused. The path pattern accepted `Program Files\Python313` and `Python313-arm64`, and rejected `C:\Python313`, `&`, `"`, and a nested folder. `python test_hello.py` passes. The full installer has not yet run as administrator.

## 2026-09-30: Skip the shutdown flush and add a locked-down installer

The third hello.py review answered here.

- `_silence()` is gone. The error path now calls `os._exit(1)` after the stderr message, which skips the shutdown flush that `_silence()` existed to defuse. That closes three findings at once, because the code they point at no longer exists:
  - "Leaked file descriptor. `os.open(...)` returns a new fd. ... the original fd from `os.open` is never `os.close`d."
  - "`_silence` is unguarded. `fileno()`, `os.open`, or `dup2` can still raise ... That exception escapes `main()`."
  - "Process-wide fd replacement. After `_silence`, anything else in this process that still holds fd 1 or 2 writes to null."
- The stderr message is flushed explicitly, since `os._exit` skips every flush.
- New `test_hello.py` runs the script against a closed pipe as stdout, then as stdout and stderr, and checks for exit 1. It fails on the round 2 code that exited 120. CI's dependabot check runs `test_*.py` files with pytest.
- New `install.ps1` does the deployment controls that `BACKLOG.md` had declined as rollout steps. The review said: "Ship it as `py -3 hello.py` from a locked-down path." The script installs to `Program Files\hello-world` with write access for Administrators and SYSTEM only. It writes `hello.cmd`, which pins the all-users Python 3 instead of calling `py -3`, because `py -3` also selects per-user installs that the employee can replace. The launcher runs Python with `-I`, so `PYTHON*` variables and user site-packages can't inject code. The script refuses to install if no all-users Python is under Program Files.

Review finding 3, "Wrong object silenced on some failures", needed nothing beyond the `_silence()` removal. Findings 5 and 6 and the PEP 8 note needed no change; the file already has two blank lines around top-level definitions.

Tested with `python test_hello.py` on the new code and on the round 2 code, where it fails as it should. `install.ps1` was run unelevated on a dev machine. Its guard refused there, since that machine has only a per-user Python. A copy pointed at a scratch folder installed, ran `hello.cmd`, and matched the source hash. With only the Users grant left, writes and new files in the folder were denied. It has not yet run as administrator against the real `Program Files`.

## 2026-09-30: Exit 1 on dead stdout or stderr instead of 120

The second hello.py review answered here.

- A failed stderr write in the error handler is now caught. The review said: "If stdout is dead *and* stderr is also unusable, the handler's `print(..., file=sys.stderr)` raises a second `OSError` that is not caught."
- After a failed write, the stream's fd is pointed at devnull. Testing the finding above showed a worse bug the review missed: with only stdout dead, the script exited 120, not 1. The failed text stays buffered, and Python's shutdown flush fails a second time. The both-dead case also exited 120.
- A module docstring now gives the Windows invocation and the exit codes. The review said: "operators must still call an explicit interpreter" and "Exit-code contract is implicit. ... Document it if this is used as a health check."

Tested by running the script against a pipe with a closed read end, as stdout alone and then as both stdout and stderr. Both cases now exit 1, and the normal and redirected runs still print the line and exit 0.
