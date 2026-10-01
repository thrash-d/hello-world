# Round 21

- Date: 2026-10-01
- Commit reviewed: be3e4da (version 1.5.4)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION, plus the newest changelog entry as developer's notes
- Redactions: none

---

  # Review of 1.5.4 (hello.py, install.ps1, test_hello.py)

  I found no Critical, High or Medium issues. I found three Low issues and a few notes. I read the code statically only. I can't run PowerShell here, and `uninstall.ps1` wasn't in the bundle.

  ## Your three fixes

  - **Remove-Tree (M1): fixed.** `Test-Path` after `rmdir` is the right check. Both callers handle the new throw correctly:
    - The `$old` removal at line 308 only warns, because the new install is already live.
    - The `$new` removal in `finally` only warns.
    - At line 268 a failed removal aborts the run before anything is swapped, which is the safe outcome.
    - The quoting passed to `cmd /c rmdir` is already a quoted string, so Windows PowerShell 5.1 passes it through as written.
  - **Start-Transcript (L2): fixed.** The throw is outside the outer `try`, so no `Stop-Transcript` is needed on that path. If a transcript is already running, the existing one is not stopped.
  - **rev-parse message (L3): fixed.** The `$LASTEXITCODE` check comes before the `$head -ne $Commit` comparison, so the message now points at the real problem.

  ## Low

  1. **`Get-ChildItem -Recurse` can follow junctions before the link check runs (line 162).**
     - Windows PowerShell 5.1 follows directory junctions when recursing. The whole listing is built inside `@(...)` before the loop checks for `ReparsePoint`.
     - A junction loop or a junction to a huge tree under the setup folder or the Git folder would make the "is a link" refusal hang or take very long. It would not produce a wrong result.
     - Only an administrator can plant such a junction, so the risk is small.
     - Fix: walk the tree yourself, checking each directory's attributes and not descending into reparse points.
  2. **The restore block and the early checks aren't in the log.** The transcript starts at line 228, after the `.old` restore (lines 198-205) and after the permission checks. A restore that went wrong on one PC leaves no record. Either state this in the docs or move `Start-Transcript` before the restore. Moving it would mean the log opens before `Assert-AdminOnlyTree $PSScriptRoot` has run.
  3. **The "delete the setup folder first" instruction can fail on a Git clone.** The files under `.git\objects` are read-only. `Remove-Item -Recurse` without `-Force` fails on them. Document `Remove-Item -Recurse -Force` or `cmd /c rmdir /s /q`.

  ## Notes

  - **`uninstall.ps1` is not in this bundle.** I can't confirm your claim for the declined L4, that it self-elevates with `Start-Process -Verb RunAs`. It is the one script that a non-admin's button click turns into an elevated run, so it deserves its own review. The same goes for the claim that it removes the `.new` and `.old` folders.
  - **Pinned Python hash.** I can't check the SHA-256 or the existence of 3.14.8 from here. Compare the hash against the `.sigstore` file on python.org yourself, ideally from a second machine.
  - **Windows is untested.** You have run none of the `install.ps1` paths. Before all 5 PCs, do a full run on one clean machine, a second run to exercise the upgrade path, and one forced failure such as a wrong `-Commit`. Watch the new `rmdir` check and the swap and restore logic in particular.
  - **Parts that look correct to me:**
    - The ACL masks and the parent-folder walk.
    - The `hash-object` check. It applies `autocrlf`, which your note about LF versus CRLF covers.
    - The swap and restore sequence.
    - hello.py's `os._exit(1)` path and its tests. The Linux behaviour matches what the tests assert.
    - The shortcut's quoting.
