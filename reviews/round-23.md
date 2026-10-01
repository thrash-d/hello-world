# Round 23

- Date: 2026-10-01
- Commit reviewed: cb598fc (version 1.5.6)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION, plus the newest changelog entry as developer's notes

---

Review of 1.5.6, done by reading the text only. I ran nothing, so I could not test install.ps1 or check the Python URL and hash.

**Result: no Critical, High or Medium findings.**

The 1.5.6 change is correct and safe. Telling people to `cd \` before deleting the setup folder fixes the "folder in use" failure. I found no `#>` or other sequence that would close the comment-based help early. A help-only edit cannot change the script's behaviour or break parsing.

I re-checked these parts of the code and found no defect:
- **ACL checks:**
  - The rights masks are correct.
  - The inherit-only handling is correct.
  - The TrustedInstaller SID is correct.
  - The drive-root exemption for Delete is correct.
  - Reparse-point rejection is in place.
  - The owner check is in place.
- **Source pinning:** The 40-hex commit pin and the per-file `hash-object` versus `HEAD:file` comparison are sound.
- **Python download:** The SHA-256 is checked before the old install is touched.
- **Install swap and recovery:** The `.new`/`.old` swap and its recovery logic are sound.
- **Quoting:** The `rmdir` quoting is correct on both PowerShell 5.1 and PowerShell 7. The `"`:"` escape in the error message and the shortcut's `/c ""…" & pause"` quoting are both right.
- **Test run:** The test run happens after the tree check.
- **hello.py and test_hello.py:** No bugs. The exit 1 path via `os._exit` is correct, and the tests cover the failure cases.

**Low (all operational; none block deployment)**

1. **install.ps1 has not been run or parsed.**
   - Because only comments changed, the risk is small.
   - Before the rollout, run `[System.Management.Automation.Language.Parser]::ParseFile` on it.
   - Then do one full pilot install on a real workstation.
   - Confirm in the pilot that the pinned python-3.14.8 URL and hash still resolve and match, and that uninstall works.
   - I cannot verify the URL or hash from here.
2. **`ProgramData\Git` will probably block installs on real machines.**
   - It typically inherits Users write from `C:\ProgramData`, so `Assert-AdminOnlyTree` throws.
   - Failing closed is the right security behaviour, but it can make all 5 installs fail.
   - Add a one-line `icacls` hardening step to the help, or make the error message say what to run.
   - Do this only if the pilot shows it happens.
3. **The Git tree walk is slow and can fail on long paths.**
   - `Get-ChildItem -Recurse` plus `Get-Acl` on the whole Git for Windows install can take several minutes, not "a minute".
   - On Windows PowerShell 5.1 it can also hit PathTooLong errors, which fail closed.
   - Mention this in the help so nobody kills the run.

**Info**

- **Reinstall help:** The help says to `cd` out and then `Remove-Item -Recurse -Force`, but gives no target. Add "`Remove-Item -Recurse -Force $d`". That works only in the same window where `$d` was set. Otherwise, give the literal path.
- **Environment cleaning:** Only `GIT_*` variables are removed. `HOME`, `XDG_CONFIG_HOME` and the admin's global `.gitconfig` still apply to git. That config belongs to the admin and is trusted, so this is acceptable. State that assumption.
- **No Python update path:** The Python 3.14.x embed is pinned and never auto-patched. You declined this as a process matter, which is fine. Its exposure is tiny, since it only runs hello.py from an admin-only folder. Put a calendar reminder on the pin.
- **Design size:** The installer is far more complex than printing one line needs, and every extra line adds maintenance risk. This is not a defect.
