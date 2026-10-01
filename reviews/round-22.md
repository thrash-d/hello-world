# Round 22

- Date: 2026-10-01
- Commit reviewed: 7e5e7b4 (version 1.5.5)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION, plus the newest changelog entry as developer's notes

---

Review of 1.5.5 (read from the text only, nothing run). Result: no Critical, High or Medium findings. I found 1 Low bug in the help text and 4 Low/Info items. I did not find new defects in hello.py, test_hello.py or the install logic. I can't execute anything, so the Python hash and the Windows-specific behaviour below are untested.

**Your two help-text fixes**
- **Remove-Item -Recurse -Force:** correct. Git's read-only object files do need -Force.
- **.NOTES wording:** accurate. The restore block and the Git/permission checks run before Start-Transcript, so "the steps after the permission checks" describes install.log correctly. Keeping Start-Transcript after the setup-folder check is the right call.
- **VERSION:** 1.5.5 matches.

**Declined items**
- **Junction walk (L1 from the last review):** I agree with declining it. Only an administrator can plant a junction there, and the worst case is a slow or hung check, not a wrong result.
- **uninstall.ps1:** I disagree with treating this as a non-issue. See L2 below.

**Low**
- **L1, help text:** the example ends with `cd $d`, then tells the user to delete the setup folder. Windows can't delete a folder that is a process's current directory, so `Remove-Item` fails with "in use" if they run it from that same window.
  - Fix: add "first `cd` out of it (for example `cd \`)" to the re-install sentence.
- **L2, uninstall.ps1 is unreviewed:** it is the one script a user can trigger that later runs with admin rights from the Apps entry. It deletes folders and the registry key and shortcut.
  - The installer's commit check proves the file matches the tagged commit. It says nothing about what the file does.
  - Leaving it out of the reviewer's files means nobody has reviewed that path.
  - Fix: include it in the next round.
- **L3, uninstall by a standard user is untested:** the UninstallString runs plain `powershell.exe`, which has no elevation manifest. Windows may not prompt for elevation for this kind of HKLM entry, in which case the script would fail with access denied or half-run.
  - Fix: click Uninstall on a standard-user test account. If it doesn't elevate, make uninstall.ps1 relaunch itself elevated or fail with a clear message.
- **L4, Python pin has no update path:** 3.14.8 is frozen with a pinned hash, and nothing in the repo says when to bump it. For `print("Hello, world!")` the exposure is small.
  - I can't verify the hash from the text. Re-check it against python.org's published digest before rollout.
- **L5, small gaps in the checks (Info):** the shortcut check covers the .lnk file but not the Start Menu Programs folder above it. `$new` is checked before the test run, not after. Both only matter if a default ACL has been loosened, and the first one also needs admin rights.
- **L6, operational note (Info):** `C:\ProgramData\Git` can inherit write rights for Users from `C:\ProgramData` on some machines. If so, the installer will correctly refuse to run. Fix it with `icacls`, not by weakening the check.

**hello.py and tests:** no bugs found. Dead stdout, closed stdout, stdout closed after start and dead stderr are handled. `os._exit(1)` after the stderr write gives the intended exit code, and the stderr failure is swallowed. The `preexec_fn` test is POSIX-only and skips elsewhere, which is fine.
