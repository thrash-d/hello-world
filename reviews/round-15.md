# Round 15 review

- Date: 2026-10-01
- Commit reviewed: a2c5a64 (Round 14: shortcut working directory and retryable uninstall)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION (plus the newest changelog entry as developer's notes). The reviewer also read uninstall.ps1, BACKLOG.md and .gitattributes from the working tree on its own.
- Redactions: none

---

**Review of 1.4.2: no Critical, no High, 1 Medium, 6 Low.**

**What I did and didn't check.** `uninstall.ps1` wasn't in your paste, so I read it from the repo at commit a2c5a64 (the 1.4.2 change). I couldn't run or parse any PowerShell here, and I couldn't download the Python zip to check the pinned SHA-256 (the proxy returned 403). Everything below is from reading the code. None of it has been run on Windows.

The installer's trust model holds up. I found no new way to run an employee's code as admin or to swap files in the install folder. The fixes you listed (shortcut working directory, uninstall order, try/catch/finally with a pause, `-LiteralPath`, the 64-bit check) are present and do what the notes say. The one real miss is in the retry design (M1).

## Medium

**M1. A failed uninstall can still leave no way to retry, which is the round-14 M2 problem again.**
- `uninstall.ps1` deletes `$dir` first, then `$dir.new`, then `$dir.old`. The Apps entry's `UninstallString` points at `$dir\uninstall.ps1`, inside `$dir`.
- If `$dir` deletes cleanly and `.old` or `.new` then fails (antivirus lock, or an interrupted install's leftovers), the catch prints the error and the script ends.
- The Apps entry and shortcut are still there, but the script they point to is gone. The Uninstall button now does nothing.
- Fix: delete `.new` and `.old` first and `$dir` last. Better, delete everything in `$dir` except `uninstall.ps1`, then the script and folder at the very end. Today the retry only works by luck: `python\` sorts before `uninstall.ps1` in enumeration order.
```powershell
foreach ($f in "$dir.new", "$dir.old") { if (Test-Path -LiteralPath $f) { Remove-Item -LiteralPath $f -Recurse -Force } }
if (Test-Path -LiteralPath $dir) {
    Get-ChildItem -LiteralPath $dir -Force | Where-Object Name -ne 'uninstall.ps1' | Remove-Item -Recurse -Force
    Remove-Item -LiteralPath $dir -Recurse -Force   # removes the script last
}
```

## Low

**L1. Uninstall can report success when the shortcut or Apps entry wasn't removed.**
- Both removals use `-ErrorAction SilentlyContinue` to tolerate "not found". That also hides real failures such as a locked file or denied access.
- The script then prints "hello-world is uninstalled." anyway, and a dead shortcut stays in the Start menu.
- Fix: guard with `Test-Path` and use `-ErrorAction Stop` so the catch reports it.

**L2. Uninstall errors that happen outside the `try` are never seen.**
- The 64-bit throw and the `Start-Process -Verb RunAs` call sit outside the `try`. If the employee cancels UAC, or the elevation fails, the non-elevated console closes before anyone can read the error.
- The 64-bit check is effectively dead code, because Settings starts the System32 `powershell.exe` by full path.
- Fix: move the elevation into a try/catch that also waits for Enter, or drop the dead check.

**L3. Uninstall always exits 0 and always waits for Enter.**
- A failed uninstall still exits 0, and `Read-Host` hangs forever if the script is ever run non-interactively (RMM, SYSTEM, a scheduled task).
- This doesn't matter for 5 hand-run machines. If you ever script it, add `exit 1` in the catch and a `-Quiet` switch that skips the prompt.

**L4. `Set-Location` may not release the process's working directory.**
- I believe PowerShell's `Set-Location` doesn't always change the process's own working directory. I'm not certain.
- It only matters if an admin runs `uninstall.ps1` from inside the install folder. Cheap fix: also set `[Environment]::CurrentDirectory = $env:SystemRoot`.

**L5. `install.ps1` can leave a half-finished install.**
- The shortcut is saved before the Apps entry. If `Save()` or the COM call throws, the install is live with no Uninstall button. Your L1 fix only covered the ACL check.
- If the final `Assert-AdminOnly $lnk` throws, the shortcut stays in every user's Start menu even though it failed the check.
- Fix: write the Apps entry first, then the shortcut. On ACL failure, delete the shortcut before rethrowing.

**L6. The Git `ProgramData` config question is still open, and neither of us has verified it.**
- I agree with declining a Git version check. The notes admit the "older than 2.35.2" claim is from memory, and the same goes for my own recollection of how Git reads that config.
- If you ever want a guard, `Assert-AdminOnlyTree 'C:\ProgramData\Git'` when the folder exists is a few lines. It isn't needed to deploy.

## Not code

- **The unpinned guarantee.** I couldn't confirm that `A93ABE45…A310` matches the real 3.14.8 amd64 embed zip. Check it by hand against python.org's `.sigstore` record before deploying.
- **Run it once on a Windows PC.** Nothing here was parsed or run, so syntax slips are possible. Run the installer on one spare machine, ideally with a hello-world window left at the `pause` during an upgrade and again during an uninstall.
- **Uninstall needs an admin.** The Uninstall button prompts for UAC, so a standard-user employee can't remove it without admin credentials. That seems intended, but tell the staff.

**Hello.py and the tests:** no issues. The exit codes, the `os._exit(1)` handling, and the `None`/closed stdout cases are correct. The `hello.cmd` quoting and the shortcut's `cmd /c ""…" & pause"` quoting both work.
