# Round 19

- Date: 2026-10-01
- Commit reviewed: ab86ea0 (version 1.5.2)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION, plus the newest changelog entry as developer's notes
- Redactions: none

---

  Review of 1.5.2 (hello.py, install.ps1, test_hello.py, VERSION)
  
  Scope and limits: I read the code only. Nothing was run or parsed. I did not see uninstall.ps1, BACKLOG.md or reviews/round-18.md, and I could not verify the Python 3.14.8 URL or SHA-256 pin from here.
  
  Verdict: I found no Critical or High issues. The 18th-round fixes (M1, M2, L1-L4) are applied correctly where they were applied, apart from the gaps in finding 3 below. I found no syntax errors on reading. The transcript try/finally nests correctly with the inner try/finally and try/catch, and the unindented body is valid.
  
  The biggest remaining risk is practical, not a code defect (finding 1). Everything below is Medium or Low.
  
  MEDIUM
  
  1. install.ps1 has never been executed or parsed.
  - Per your notes, it was not run or parsed. The transcript start/stop, a second run in one window, Assert-NotLink, the ACL checks on real Git, ProgramData and Start Menu folders, and the shortcut quoting are all unobserved. Several of these fail closed (they throw), so an untested assumption shows up as a failed install on all 5 PCs.
  - Fix: before the 5-PC rollout, run `[System.Management.Automation.Language.Parser]::ParseFile(...)` plus PSScriptAnalyzer on any Windows box. Then do one run on a VM or one spare PC, then a second run to cover upgrade, `.old` handling and transcript append. You declined the pilot as process (L5). I would still do at least this one run; it costs minutes.
  
  2. A failed run's error message probably never reaches install.log (not verified).
  - A terminating `throw` at script level is rendered by the host after the `finally` blocks run. Stop-Transcript has already run by then, so the log would show the steps before the failure but not why it failed. That is the case where you need the log.
  - Separately, if Stop-Transcript itself throws under `$ErrorActionPreference='Stop'`, it replaces the original error.
  - Fix: add a `catch { Write-Host "FAILED: $($_ | Out-String)"; throw }` between the `try` and the `finally`. Make the stop `Stop-Transcript -ErrorAction SilentlyContinue | Out-Null`. Confirm the behavior on Windows.
  
  LOW
  
  3. The L1 fix is incomplete. Two recursive deletes still have no link check.
  - The `finally` block runs `Remove-Item "$dir.new" -Recurse -Force`. If the download fails before the leftover loop, this deletes a pre-existing `.new` that was never passed through Assert-NotLink.
  - The post-swap `Remove-Item $old -Recurse` checks only the top level. In Windows PowerShell 5.1, `-Recurse` can follow directory links nested inside the tree.
  - Only administrators can plant links under Program Files, so this is low risk.
  - Fix: make one `Remove-Tree` helper that calls Assert-NotLink on the root and deletes with `cmd /c rmdir /s /q`, which does not follow links. Use it in all four places, and use `$new` instead of `"$dir.new"`.
  
  4. The log is not a full record of the run.
  - The `.old` restore, its warnings, and the Git, ProgramData and clone permission checks all run before Start-Transcript. The header comment says the log is "a record of what this run checked and did", which overstates it.
  - The log also omits any failure in the pre-transcript steps.
  - Fix: either say in the comment that only the steps from the commit check onward are logged, or Write-Host a one-line summary of the earlier results after the transcript starts.
  
  5. Checks that throw can reject a normal machine, and the message is hard to act on.
  - C:\ProgramData normally gives Users inheritable WriteData and AppendData. If `C:\ProgramData\Git` exists with inherited ACEs, `Assert-AdminOnlyTree $gitData` throws. That is the correct fail-closed result, but the help gives no remedy.
  - The same applies to the Start Menu shortcut check. A failure there happens after the install is live, so it leaves Apps and Start menu entries inconsistent.
  - The error text lists raw SIDs such as S-1-5-32-545.
  - Fix: translate SIDs to names in the message (`.Translate([NTAccount])` in try/catch). Add a help line explaining how to lock down `ProgramData\Git`. Test the shortcut check once on Windows.
  
  6. Git can still read config from places the script does not check.
  - Only `GIT_*` variables are cleared. Git also honors `HOME` and `XDG_CONFIG_HOME` and reads the elevated account's `~/.gitconfig`.
  - `rev-parse` and `hash-object` run no hooks, but `hash-object` applies `filter.*.clean` if the reviewed `.gitattributes` names one.
  - Exploitability is low because the account is the admin's own.
  - Fix: also clear `HOME` and `XDG_CONFIG_HOME`, or pass `-c` to neutralize `core.fsmonitor` and `filter.*`. A simpler option is to set `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_NOSYSTEM`-style isolation after the tree checks.
  
  7. Comment and help cosmetics.
  - The comment "Antivirus scans and a running hello.cmd can hold a file open..." now sits above Assert-NotLink. It belongs above Rename-Retry. This was misplaced when Assert-NotLink was inserted.
  - In `.NOTES`, a wrapped line begins with `.old folders`. The comment-help parser may read that as an unknown `.OLD` keyword, so check `Get-Help .\install.ps1`. Reflow the text so no line starts with `.`.
  - Start-Transcript and Stop-Transcript output goes to Out-Null, so the console never shows where the log is. Consider printing the log path once.
  
  8. Ctrl+C or a hung Get-ChildItem on a link loop can leave the transcript in a poor state.
  - Assert-AdminOnlyTree collects the whole `Get-ChildItem -Recurse` result before checking any item for a link. In 5.1, recursing into a link first can be slow or loop.
  - Only administrators can place links there, so this is a hang or noise risk, not a security hole.
  
  Out of scope or not verifiable
  - uninstall.ps1 was not provided. It runs elevated from Settings > Apps, so review it separately for how it deletes (`.new`, `.old`, shortcut, registry key) and whether it follows links.
  - I could not confirm the python-3.14.8-embed-amd64.zip URL or the SHA-256. Confirm it against the .sigstore file once more before rollout.
  - hello.py and test_hello.py: I found no defects. The os._exit(1) plus explicit stderr flush is correct, and the exit codes are consistent with the tests.
  - The declined items ($env:PROCESSOR_ARCHITECTURE and the pilot) are your call. The first is fail-closed. The second is the one I would reconsider, per finding 1.
