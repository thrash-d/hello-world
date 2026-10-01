# Round 14 review

- Date: 2026-10-01
- Commit reviewed: a940b78 (Make the hello.cmd write literal and document reinstalling)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION (plus the newest changelog entry as developer's notes). The reviewer also read uninstall.ps1, BACKLOG.md, CHANGELOG.md and reviews/round-13.md from the working tree on its own.
- Redactions: none

---

## Review of hello-world 1.4.1 (round 14)

I found no Critical or High issues: 2 Medium and 4 Low. Both 1.4.1 changes are correct. The `-LiteralPath` swap on `Set-Content` is the only code change; the working tree differs from HEAD only in line endings (CRLF). The new help text about installing again is accurate.

**What I checked:** I read `hello.py`, `install.ps1`, `uninstall.ps1`, `test_hello.py`, `VERSION`, `BACKLOG.md`, `CHANGELOG.md` and `reviews/round-13.md` in `/home/user/hello-world`. `python3 test_hello.py` passes. I couldn't run any PowerShell, and the sandbox proxy blocked python.org, so the pinned SHA-256 (`A93ABE45…`) is still unverified by me.

**Gap in what was submitted:** round 13 reviewed 1.3.3. The 1.4.0 additions (the Start menu shortcut, the Settings > Apps entry and `uninstall.ps1`) have never been reviewed. `uninstall.ps1` runs as admin and wasn't in the files you pasted; I read it from the repo. Most of the findings below are in that unreviewed code.

### Medium

**M1. While an employee has the hello-world window open, upgrades and uninstalls fail.**
- The shortcut sets `WorkingDirectory = $dir` and ends in `& pause`. The window stays open, with `Program Files\hello-world` as its current directory, until a key is pressed.
- Windows won't rename or delete a folder that is any process's current directory. Any user's forgotten window, on any session, therefore makes the installer's `Rename-Retry $dir` fail after 5 tries.
- The 1.4.0 Windows test already saw what follows: the error says "Access to the path ... is denied", which doesn't point at the open window.
- It fails safe, but before 1.4.0 this was a brief race. Now it's a likely, open-ended state.
- **Fix:** `hello.cmd` uses `%~dp0` and doesn't need its working directory. Set `$shortcut.WorkingDirectory = $env:SystemRoot` (or leave it empty).

**M2. `uninstall.ps1` removes the Apps entry first, so a failed uninstall leaves no way to retry, and its error is never seen.**
- The order is: shortcut, then the Apps registry key, then `Remove-Item -Recurse` of the folder.
- If the folder delete fails (the M1 open window, or antivirus holding a file), `Remove-Item -Recurse` has already deleted some of the files. You're left with a half-deleted `Program Files\hello-world` and no Apps entry to try again from.
- The elevated copy runs in its own window, started by `Start-Process -Verb RunAs`. That window closes as soon as the script throws, so the admin sees neither the error nor the "uninstalled" line.
- **Fix:**
  - Delete the folders first, then the shortcut and the registry key last. If a folder is still there, throw before removing them.
  - Wrap the body in `try { ... } catch { Write-Error $_ } finally { Read-Host 'Press Enter' }`, or start the elevated copy with `-NoExit`.
  - Add `uninstall.ps1` to the files you paste for review.

### Low

**L1. If the shortcut's ACL check throws, the install is left with no Apps entry.**
- `Assert-AdminOnly $lnk` runs after the folder swap and the shortcut write, but before the registry entry.
- A throw there leaves a live install and a shortcut with no Uninstall button.
- **Fix:** write the registry entry before the shortcut check, or delete `$lnk` before rethrowing.

**L2. Round 13's L7 fix was applied in only one place.**
- `uninstall.ps1` still calls `Remove-Item` with `-Path` (wildcard matching) on the shortcut and the registry key.
- It's harmless, since neither path has brackets.
- **Fix:** use `-LiteralPath` there too, to match the installer.

**L3. `uninstall.ps1` has no 64-bit check.**
- The installer refuses a 32-bit host, but the uninstaller doesn't.
- Started from a 32-bit process, `System32\powershell.exe` is redirected to the SysWOW64 copy. `$env:ProgramFiles` and HKLM then point at the x86 locations. The script removes the shortcut, misses the folder and the Apps entry, and still prints "hello-world is uninstalled."
- Settings and Control Panel are 64-bit, so this is unlikely.
- **Fix:** add the same `[Environment]::Is64BitProcess` throw.

**L4. The `C:\ProgramData\Git\config` risk has no code check (repeat).**
- Your backlog says to revisit this "if the Git version in use predates its ownership check", but nothing checks the version.
- A standard user can create `C:\ProgramData\Git`. On Git for Windows older than 2.35.2 (from memory, please confirm), a config file there could set `core.hooksPath` or `core.attributesFile` plus a clean filter. That would run code as admin during the help's `git clone` or the installer's `hash-object`.
- This is cheaper than the declined hardening of Git's environment.
- **Fix:** either check the version (throw if `git --version` reports below 2.35.2), or require that `C:\ProgramData\Git` doesn't exist or passes `Assert-AdminOnly`.

### Checked and fine
- The reinstall path, including when a standard user recreates `C:\ProgramData\hello-setup` after the admin deletes it. The installer's owner check refuses it.
- The cmd quoting in the shortcut arguments.
- Commit and hash verification when git fails.
- Swap, rollback and restore ordering.
- The `hello.py` exit paths and the tests.

### Before deploying
Fix M1 (one line) and M2 (a reorder plus a pause), then run one upgrade and one uninstall on a Windows machine with the hello-world window left open.
