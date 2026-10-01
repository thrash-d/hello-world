# Round 20

- Date: 2026-10-01
- Commit reviewed: be92721 (version 1.5.3)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION, plus the newest changelog entry as developer's notes
- Redactions: the closing "Files:" line listed absolute paths that included a home folder; they are shortened to file names. Nothing else changed.

---

  Review of 1.5.3 (install.ps1, hello.py, test_hello.py). I found no Critical or High issues, one Medium and a few Low. I read the code only. I couldn't run install.ps1 (no pwsh here). I also couldn't re-check the pinned Python URL and SHA-256, because the sandbox proxy blocks www.python.org. Check the hash on a Windows machine, or against the .sigstore file, before rollout.
  
  All four fixes from round 19 look correct on reading.
  - The `catch` before `finally` is valid syntax. The error is written with Write-Host before Stop-Transcript runs, so it reaches install.log.
  - `Remove-Tree` quoting is right. The argument arrives as `cmd /c rmdir /s /q "C:\...\x"`, and cmd only strips quotes when the command line starts with one, which this one doesn't.
  - `rmdir /s` removes a link inside the tree without following it.
  - Every call site of `Remove-Tree` checks Test-Path first, so `Assert-NotLink` can't hit a missing path.
  - The `.NOTES` text has no line that begins with `.word`. The `.\install.ps1` line in `.EXAMPLE` begins with `.\`, which is not a keyword.
  
  ## Medium
  
  **M1. `Remove-Tree` trusts rmdir's exit code and never checks the folder is gone.**
  - `rmdir /s /q` has a long-reported habit of returning errorlevel 0 after failing to delete a locked or denied file. I'm going from memory on that, so test it.
  - If that happens to `$old` after the swap, the leftover is only a warning, or no warning at all, and the next run clears it. That is harmless.
  - If it happens to a leftover `$old` before the install, the later `Rename-Retry $dir $old` fails after 5 tries. It fails before the swap, so the working install is untouched.
  - If it happens to a leftover `$new`, the following `New-Item` fails loudly.
  - The result is a confusing "already exists" error instead of the real cause.
  - Fix: add `if (Test-Path -LiteralPath $Path) { throw "Couldn't remove $Path" }` after the `$LASTEXITCODE` check.
  
  ## Low
  
  **L1. The error prints twice on the console.** The catch writes `FAILED: ...`, and the host then prints the rethrown error. This is cosmetic and arguably wanted. If you want one copy, use `Write-Host` for the transcript only and keep the rethrow.
  
  **L2. `Start-Transcript -LiteralPath` is untested on Windows PowerShell 5.1.**
  - I believe 5.1 supports it, but I'm not certain.
  - If it doesn't, the failure is a parameter-binding error on every machine, and it happens before `try`, so there is no log.
  - It is also unguarded. If a transcript is already running in that window, `Start-Transcript` throws and the run stops with a cryptic error.
  - Fix: do a 30-second run on one Windows box. Optionally wrap the call in try/catch with a clearer message.
  
  **L3. Git's "dubious ownership" check produces a misleading message.**
  - If the clone was made by a different admin account, `rev-parse` fails.
  - The message you see is "Source is at '', not the reviewed commit". That points at the wrong problem.
  - It fails closed, so this is only a message problem.
  - Fix: print `$LASTEXITCODE` and git's stderr, or mention safe.directory in the message.
  
  **L4. The Settings > Apps Uninstall button may not work for employees.**
  - uninstall.ps1 was not in what you sent me, so this is outside what I reviewed.
  - Employees are standard users, and Settings runs `UninstallString` without elevation. If uninstall.ps1 has `#Requires -RunAsAdministrator`, it will flash and exit instead of prompting for UAC.
  - Check that it self-elevates, or document that an admin does uninstalls.
  
  **L5. Minor operational notes.**
  - Invoke-WebRequest uses the default proxy with no credentials. An authenticating proxy will fail all 3 download tries.
  - `Assert-AdminOnlyTree` on the Git folder is slow, which you already warn about.
  - On machines where `ProgramData\Git` exists with default inherited rights, Users may have create-file rights and the check will fail. That is the L5 you already put in the backlog, so no new action.
  
  ## Checked and found fine
  - The ACL logic: the rights masks, the InheritOnly handling, the owner check, and the ancestor walk with the drive-root exception.
  - The environment scrub, which removes `GIT_*` variables before git runs.
  - `hash-object` compared against `HEAD:file`.
  - The install, swap and rollback ordering, and the interrupted-swap recovery.
  - The shortcut quoting, `/c ""x" & pause"`.
  - The hello.cmd `-I` flag.
  - The post-write ACL check on the Start menu shortcut.
  - hello.py's exit paths: stdout None, dead stdout, closed stdout, and a dead stderr.
  - test_hello.py is sound on Linux. The tests that rely on fd inheritance and preexec are skipped or untested on Windows, which doesn't matter because the tests aren't deployed.
  
  ## Verdict
  Safe to roll out to 5 workstations after one real Windows run, and no Critical or High findings were open. The run should cover three things: a forced failure, to confirm the error lands in install.log, an upgrade over an existing install, and `Get-Help .\install.ps1 -Full`. Apply the M1 fix first. It is one line.
  
  Files: install.ps1, hello.py, test_hello.py
