# Round 11 review

- Date: 2026-10-01
- Commit reviewed: 14efb790a0eb25c0bc26259eb88d4515ae785619
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION (plus the newest changelog entry as developer's notes)
- Redactions: none

---

# Review of 1.3.1

**Verdict:** I found no Critical or High issues. I read every line, but I ran nothing, and the script has still never been parsed or run on Windows. That is the largest risk, so pilot it on one machine first (Medium 1). I read each of the six changes below against the code, and each does what the notes claim.

## What I checked in this round's changes

- **Commit gate:**
  - It is now fail-closed. `$actualOk` is captured straight after `hash-object`, so a failed call, empty output or a non-40-hex output all throw.
  - A failing `rev-parse HEAD:$f` is caught by `$LASTEXITCODE`.
  - A multi-line `$expected` can't slip through, because both sides are stringified before `-ne`.
- **Build-then-swap:**
  - If the first rename fails, nothing has changed and the script throws.
  - If the second rename fails, the old folder is restored.
  - Both are correct.
  - The `.new` and `.old` leftovers are cleared at the start of the next run.
- **Tree and Users checks before the test run:** they now run on `$new`, and the parent-chain check on `$new` covers `Program Files`. The ordering is right.
- **Zip cleanup, timeout and TLS:**
  - The `finally` block deletes the zip on both success and failure.
  - `-bor Tls12` is correct.
- **Parse risks:** I looked for places where PowerShell would misparse the script.
  - The `$LASTEXITCODE` backtick in the throw message is correct.
  - The `-bnot` precedence is correct.
  - The `@(...) + @(... | ...) | Where-Object` precedence works as intended.
  - The hex rights masks match the Windows constants.
  - The `$trusted` array continuation is correct.
- **`hello.py`:**
  - The `None` check is correct.
  - `os._exit(1)` after an explicit stderr flush is correct.
  - If stderr is also `None`, `print(file=None)` falls back to `sys.stdout`, which is `None`, so it does nothing and does not crash.
  - `test_closed_stdout_exits_1` should pass on Linux. I expect Python to leave `sys.stdout` as `None` when fd 1 is closed at startup.

## Critical

None.

## High

None.

## Medium

**1. `install.ps1` is entirely unexecuted, and the pinned hash is unconfirmed.**
- Nothing in the script has been parsed by PowerShell, and the swap, the ACL walk, the Git calls and the download have never run.
- I cannot confirm from here that `3.14.8` exists at that URL, or that `A93ABE45…` is its SHA-256.
- A wrong hash fails closed, so it is a nuisance rather than a security hole.
- Fix before rolling out to five machines:
  1. Run `[scriptblock]::Create((Get-Content .\install.ps1 -Raw))` or `Get-Command .\install.ps1 -Syntax` for a parse check.
  2. Do a full install on one disposable Windows 10/11 x64 VM.
  3. Run it a second time over the existing install to exercise the swap.
  4. Hold `hello.cmd` open (for example, `python.exe` sleeping) during a third run to exercise the failed-rename path.
  5. Check the zip's SHA-256 by hand against python.org's `.sigstore` file or release page.
- Until someone does step 5, the pin is a trust-on-first-use value I wrote down, not a verified one. The notes say M3 needs a second person, and I agree.

**2. The security model assumes employees are not local administrators.**
- `$trusted` includes the running admin's own SID. If an employee's daily account is a local admin, every "only administrators can change this" guarantee means nothing against that person.
- Confirm that the five users are standard users. State this precondition in the docs.

## Low

**3. An interrupted swap can destroy the only good install.**
- If power or the session is lost between the two renames, `hello-world` is gone and `hello-world.old` is the only working copy.
- The next run deletes `.old` at the very start, before the new build has succeeded.
- Fix: at the start of the next run, if `$dir` is missing and `$old` exists, rename `$old` back to `$dir` first. Only then clear leftovers.
- The window is milliseconds wide, but this change was meant to remove exactly this kind of exposure.

**4. The directory rename has no retry.**
- Renaming a folder fails if any file under it is open without share-delete. This can happen with Defender scanning the freshly extracted Python, or an employee running `hello.cmd` at that moment.
- The script fails closed and leaves the old install working, so a rerun fixes it.
- Fix: wrap each `Rename-Item` in 3 to 5 tries with a 1-second sleep.

**5. A failure after the swap reports as a failed install.**
- If `Remove-Item $old` fails because a file is in use, the new install is already live, but the script throws and never prints the "Installed" line.
- Fix: catch that error, call `Write-Warning`, and continue. The next run cleans `.old`.

**6. Failed runs leave `hello-world.new`, and the uninstall instructions miss it.**
- The `.NOTES` text says the installer "makes nothing outside these two folders". That is now untrue after any failed or interrupted run.
- The uninstall line also does not remove `hello-world.new` or `hello-world.old`.
- Fix: delete `$new` in the failure path, and add both folders to the uninstall line.

**7. The commit check is filter-normalized, not byte-exact.**
- `git hash-object <file>` applies `core.autocrlf` and attribute filters.
- Git for Windows defaults to `autocrlf=true`, so the working file is CRLF while the blob is LF. The check passes anyway.
- That is needed for the check to work at all on Windows. It means the SHA-256 printed at the end is of the working-tree bytes, not of the Git blob.
- Nothing is wrong functionally. Just do not describe it as byte-identical.
- The M1 hardening you declined (a clean Git config and environment) would also resolve this, since Git still reads the admin's global config and `GIT_*` variables.

**8. A few paths come from environment variables.**
- `$env:SystemRoot` (for icacls) and `$env:ProgramFiles` come from the process environment.
- This only matters if a non-admin can set them in the admin's session, which is the same account problem as finding 2.
- `[Environment]::GetFolderPath('System')` and `GetFolderPath('ProgramFiles')` are slightly more robust.

**9. The architecture check is a heuristic.**
- A native ARM64 PowerShell reports `ARM64` and is refused, even though Windows 11 ARM64 could run the x64 Python under emulation.
- An x64 PowerShell on ARM64 reports `AMD64` and passes. That is fine on Windows 11, where the test run will pass.
- This is acceptable and fails safe.

**10. The reparse-point check can reject legitimate files.**
- Files compressed with Compact OS (WOF) may carry the reparse attribute. If the Git tree has any, the installer throws a "is a link" error.
- It fails closed, and the message names the file. You declined this one (M5/L5) already.

**11. `hello.py` catches only `OSError`.**
- A closed but non-`None` `sys.stdout` object raises `ValueError`, which would produce a traceback and exit code 1. The exit code happens to be right, but there is no clean message.
- This is unreachable from a normal shell. If you want it tidy, use `except (OSError, ValueError)`.

**12. The closed-stdout test silently passes on Windows.**
- It returns early, so it reports success without testing anything. The only platform that matters has no coverage of this path.
- Use `pytest.skip` or an explicit "SKIPPED" line so the gap is visible.
- This is the CI item you declined (L8).

**13. Smaller notes.**
- The `ValidatePattern` regex `$` also matches before a trailing newline. A command line cannot realistically supply that.
- Python 3.14 requires Windows 10 or later. A Windows 8.1 or Server 2012 R2 machine will fail the test run, which is the correct outcome.
- The pinned Python gets no automatic security updates. This is your declined M6; put a calendar reminder on the version bump.

## Bottom line

Nothing here should block deployment once the pilot run passes. The security-critical logic reads as correct: the ACL walk, the commit gate, the hash pin and the build order. Items 3 to 6 are the worthwhile ones to fix, because they are small and they cover the failure paths this release was meant to harden.
