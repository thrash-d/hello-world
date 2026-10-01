# Round 12 review

- Date: 2026-10-01
- Commit reviewed: 490ddcb (Recover an interrupted install swap and retry the folder rename)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION (plus the newest changelog entry as developer's notes)
- Redactions: none

---

REVIEW OF 1.3.2 (hello.py, install.ps1, test_hello.py)

Scope and limits: this is a read-through only. I could not run any PowerShell (no pwsh here), and I could not check the pinned Python hash. The sandbox proxy blocked www.python.org, so the A93ABE45... value is unverified by me. The 1.3.2 changes for interrupted-swap recovery, rename retry, the late-failure warning, `.new` cleanup and the uninstall line are all untested on Windows. I traced them by hand and found no logic error in the swap, rollback or retry code itself. The one real gap is where recovery sits, which is finding M1 below.

Summary: no Critical or High findings. There are 2 Medium and 5 Low findings, plus a few informational notes. Your ACL-checking logic reads as correct. I checked the rights masks, the owner check, the InheritOnly skip, the drive-root `-bnot 0x10000` handling, the `+` versus `|` precedence in `Assert-AdminOnly`, and the line-continued `$trusted` array.

MEDIUM

M1. Interrupted-swap recovery runs too late, so an offline or failed run leaves the workstation with no install.
- Where: install.ps1, the recovery line inside `try`. It runs after the git and ACL checks, the commit check and the 10 MB download.
- If power was lost between the two renames, `hello-world` is missing and `.old` is the only working copy. Any failure before that line leaves it that way. Examples: no network, python.org unreachable, a proxy, a TLS problem, an ACL assertion failing, or the commit check failing.
- Employees stay without hello until someone gets a fully successful run. Recovery doesn't depend on any of those checks, because `.old` sits in Program Files, which only administrators can write.
- Fix: move recovery to the top of the script, right after `$dir`, `$new` and `$old` are defined and before any check or download. Use `Rename-Retry` there too, since it currently uses plain `Rename-Item`.
```
if (-not (Test-Path -LiteralPath $dir) -and (Test-Path -LiteralPath $old)) { Rename-Retry $old (Split-Path $dir -Leaf) }
```
- The cleanup of `.new` and `.old` can stay where it is.

M2. The SKIPPED print in `test_closed_stdout_exits_1` is invisible under pytest.
- pytest captures stdout and reports the test as passed. A Windows run of `pytest` shows a green pass for a test that never ran. Your own `__main__` runner shows the line, but pytest users won't see it. The review asked for a visible gap, and this only half delivers that.
- Fix: raise `unittest.SkipTest("needs preexec_fn, posix only")` instead of printing and returning. pytest reports it as skipped. Have the `__main__` runner catch `unittest.SkipTest` and print `SKIPPED name: reason`. Don't use `@pytest.mark.skipif` alone, because the plain runner would then run the test anyway.

LOW

L1. The new `except (OSError, ValueError)` path has no regression test.
- You checked it by hand, but nothing in the suite covers it. Add a cross-platform test that runs `[sys.executable, "-c", "import sys, runpy; sys.stdout.close(); runpy.run_path(r'<HELLO>', run_name='__main__')"]`, with `<HELLO>` filled in from the test's `HELLO` path. Assert exit 1 and a stderr that starts with `hello.py: cannot write to stdout:`. The test environment makes `run_path` raise `SystemExit` on `os._exit`, so the exit code check must be on the subprocess, which it is.

L2. Wildcard-interpreting cmdlets are used on paths that could contain `[`.
- Affected calls are `Get-FileHash $zip`, `Get-FileHash (Join-Path ...)` and `Copy-Item (Join-Path $PSScriptRoot 'hello.py') $new`. The script already uses `-LiteralPath` elsewhere because Git ships `[.exe`. A clone path containing `[` or `]` would fail or hash the wrong thing.
- Fix: add `-LiteralPath` to all of them.

L3. The permission walk over the whole Git tree is slow and fragile.
- `Get-ChildItem -Recurse` plus `Get-Acl` on every Git for Windows file takes minutes, and it runs on every install. Windows PowerShell 5.1 also throws on paths over 260 characters, which `$ErrorActionPreference = 'Stop'` makes fatal. The result is a false failure on a legitimate Git install.
- Fix: warn the operator that it is slow. Test on a pilot machine first (you declined this as M1 last round, so I am noting only the risk, not re-raising it). If it fails on long paths, catch that case and report the path.

L4. Recovery restores `.old` without checking it is intact.
- `.old` could be half-deleted if a previous `Remove-Item` failed partway, and then be restored by recovery after someone removed `hello-world` by hand. The same run then replaces it with a tested install, so this matters only if that run also fails. That is very unlikely, so this is low.
- Fix, optional: after recovery, check that `python\python.exe` and `hello.cmd` exist, or run the test line against it.

L5. The uninstall line hides failures.
- `-ErrorAction SilentlyContinue` means an install folder held open by a running hello.cmd, or an access problem, produces a silent partial uninstall. Drop it, or follow with a `Test-Path` check that prints what is left.

L6. A pinned Python gets no patching.
- 3.14.8 embedded never updates itself. Someone has to bump both constants, and there is no reminder to do it. Put a review date in the help text or in BACKLOG.md.

L7. The example's `Set-ExecutionPolicy -Scope Process Bypass -Force` fails with an error if a Group Policy execution policy is set (MachinePolicy or UserPolicy). Mention that in the help.

INFORMATIONAL (no change needed)
- `hello.py` is correct. stdout None, ValueError from a closed stdout, a dead pipe, and the `os._exit(1)` path that avoids exit code 120 all behave as stated. If both stdout and stderr are None, the inner `print(file=None)` silently does nothing and exit is still 1, which is fine.
- `hello.cmd` exit codes propagate to `$LASTEXITCODE` when called from PowerShell, so the test-run check works. Output with CRLF compares cleanly after `"$out"`.
- A rename failing because an employee has hello.cmd running fails loudly after about 4 seconds with nothing changed. That is correct. The raw IOException message is unfriendly. Consider catching it and printing "Close any running hello.cmd and rerun".
- A rollback failure rethrows a different exception than the original, which hides the first error. The state is still recoverable (see M1). Optionally write the original error with `Write-Warning` before rolling back.
- `hash-object` applies CRLF/autocrlf filters, so a line-ending-only change passes the check. This is the already-declined L7, so no action.
- The "Installed" line is correct on the late `.old` removal failure. `Write-Warning` is not turned into a terminating error by `$ErrorActionPreference = 'Stop'`.

Before deploying: do M1 and M2 (a few lines each), then run it on one Windows machine. That machine would be the first place to see the rename retry, the recovery, the Git tree walk time and the uninstall line. I understand the pilot is declined, but those paths are the ones nobody has run.
