# Round 16 review

- Date: 2026-10-01
- Commit reviewed: 48fad55 (Round 15: keep uninstall.ps1 until last, Apps entry before shortcut)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION (plus the newest changelog entry as developer's notes). The reviewer also read uninstall.ps1 from the working tree on its own.
- Redactions: one local home-folder path to uninstall.ps1 in the reviewer's opening notes, replaced with `<repo>/uninstall.ps1`.

---

**Review of 1.4.3 (commit 48fad55): no Critical or High findings, and nothing I'd stop you deploying for. One Medium (process, not code) and four Low items.**

**What I read and what I couldn't check**
- The paste left out `uninstall.ps1`, the file that changed most this round. I read it from the repo at `<repo>/uninstall.ps1`.
- `install.ps1` and `uninstall.ps1` are ASCII with CRLF, and the braces and parentheses balance. That is a rough check only. `pwsh` isn't installed, so I could not parse or run either script.
- I tried to download the pinned Python zip and check its hash. The sandbox proxy returned 403 for www.python.org, so the hash and the 3.14.8 URL are unverified, as in the earlier rounds. If either is wrong, the installer stops with "doesn't match the pinned SHA-256" before it touches the existing install.

**Medium**

M1. This round's changes have never run on Windows.
- Nothing has run or parsed `install.ps1` or `uninstall.ps1` since the order changed.
- The self-deleting uninstall, the elevation hand-off, and the shortcut removal on a failed ACL check are all new this round. Each could fail in a way the Linux tests can't show.
- Fix, before all 5 machines: use one Windows VM or spare PC, with Git for Windows installed for all users, as a standard-account setup.
  1. Parse both scripts with `[System.Management.Automation.Language.Parser]::ParseFile`.
  2. Run the install, then the installed Uninstall button from Settings > Apps as a standard user, so the elevation prompt appears.
  3. Run it again to confirm the second uninstall succeeds when nothing is left.
  4. Install twice to exercise the in-place upgrade and the `.old` cleanup.
  5. Run an uninstall with a hello window open to see the failure path.
- This is the same pilot your backlog has declined several times. It is the only step that tests the code you're about to ship.

**Low**

L1. The retry gap moved rather than closed (`uninstall.ps1`).
- Step 2 deletes `uninstall.ps1` along with the folder. Step 3 removes the shortcut and the Apps entry afterwards.
- If step 3 fails, or `Remove-Item $dir` removes the script and then fails on the folder (Explorer or antivirus holding it), the Apps entry stays and points at a script that no longer exists.
- Re-running `install.ps1` repairs it, because it restores `uninstall.ps1`, so this is recoverable.
- Cheap fix: remove the shortcut before the folder, since it almost never fails and a leftover one is harmless. Then remove the folder, then the Apps entry last. Or wrap the final folder removal in the same retry loop as `Rename-Retry`.

L2. The 64-bit check in `uninstall.ps1` runs before the `try`.
- If it ever fired, the window would close immediately and nobody would see the message.
- It can't realistically fire, because `UninstallString` names the 64-bit `powershell.exe` by full path. It is harmless dead code; moving it inside the `try` makes it visible.

L3. The setup-folder example has a short window before the lock.
- `New-Item` creates `C:\ProgramData\hello-setup` with the inherited ACL, which lets Users write into it. `icacls` locks it a line later.
- A file planted in that window makes `git clone` fail on a non-empty folder, and `Assert-AdminOnlyTree` would also reject it, so it fails closed. Creating the folder under `Program Files` (admin-only by inheritance) would remove the window.

L4. The `C:\ProgramData\Git` config issue stays accepted.
- Concrete mechanism: a planted system config could set `core.attributesFile` and a `filter.*.clean` command, and `git hash-object` would run it as admin.
- Current Git for Windows checks ownership of that config. Run `git --version` on the deploy machine to confirm it is current.
- I agree with your backlog entry. `GIT_CONFIG_NOSYSTEM=1` in the installer would close it in one line if you ever want it.

**Checked and found correct**
- `hello.py`: handles a closed stdout, a dead stdout, and a stdout closed after start, with exit 1 and `os._exit` to skip the shutdown flush. The tests match that behavior.
- `Assert-AdminOnly` and `Assert-AdminOnlyTree`: the rights masks, owner check, InheritOnly skip, and drive-root handling are right. The tree walk fails closed on links.
- `git hash-object` against `HEAD:file` is correct under `* text=auto` and `*.ps1 eol=crlf`.
- The `hello.cmd` write, the `cmd /c` quoting in the shortcut, and `"$dir.new"` string expansion are right.
- Backlog item L5 is fixed correctly: the Apps entry is written before the shortcut, and a failed ACL check deletes the shortcut.
- The rename and restore logic holds up, including the case where the first rename fails before anything has moved.
- The elevation try/catch in `uninstall.ps1` covers a cancelled UAC prompt.
- Deleting a running script works in PowerShell, since it reads the script fully before running it.
