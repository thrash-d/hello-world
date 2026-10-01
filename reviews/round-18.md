# Round 18

- Date: 2026-10-01
- Commit reviewed: 844d981 (version 1.5.1)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION, plus the newest changelog entry as developer's notes
- Redactions: none

---

# Review of v1.5.1

I read the code statically and did not run it. I found no syntax errors in install.ps1. I found no Critical or High issues. The two new features, the GetFolderPath change and the link guard, are correct. The transcript is the weak part. Nothing in hello.py or test_hello.py needs fixing.

## Medium

**M1. The transcript is opened before the script checks that its own folder is trustworthy (install.ps1 line 126).**
- `Start-Transcript -LiteralPath ...\install.log -Force` runs as admin at line 126. The first check that $PSScriptRoot is admin-only is at line 208.
- The installer promises to refuse a run from an employee-writable folder such as Downloads. That refusal now comes after the elevated process has already written and truncated install.log there.
- `-Force` overwrites read-only files. A standard user can pre-plant install.log as a hardlink, or redirect it with a junction or object-manager symlink. The admin run then overwrites a file the user chose, such as a config file. The content is mostly fixed text, so the damage is mainly clobbering and denial of service.
- The check at line 208 then throws, but the write has already happened.
- Fix: move Start-Transcript to just after `Assert-AdminOnlyTree $PSScriptRoot`, and use `-Append` instead of `-Force`:
  ```powershell
  Assert-AdminOnlyTree $PSScriptRoot
  Start-Transcript -LiteralPath (Join-Path $PSScriptRoot 'install.log') -Append | Out-Null
  ```
- The cost is that failures before that point are not logged. They still print to the console.

**M2. Stop-Transcript is never called.**
- The transcript stays active in the admin's window after the script ends or throws.
- install.log stays open and locked. The notes and help say the setup folder can be deleted after install. That fails with "file in use" until the window is closed. The documented reinstall step ("delete the setup folder first") breaks the same way.
- Everything the admin types afterward in that window is also written to the log. That includes any pasted credentials or secrets.
- Running the script a second time in the same window will likely fail at Start-Transcript because one is already active. I believe Windows PowerShell 5.1 throws here, but I'm not certain, so check it on Windows.
- `-Force` overwrites the log on each run, so a failed run's log is lost on retry. `-Append` fixes that.
- Fix: put everything after Start-Transcript in `try { ... } finally { Stop-Transcript | Out-Null }`. Alternatively call Stop-Transcript in the existing `finally` and in a `trap`.

## Low

**L1. The link guard is narrower than the notes suggest.**
- Only $dir is checked, and only at line 277, which is after the test run.
- $new and $old are removed with `Remove-Item -Recurse -Force` at lines 244 and 292 with no reparse-point check. Windows PowerShell 5.1 has a history of following junctions and deleting the target's contents.
- The restore at line 186 renames $old into place without checking it is a link. Line 277 catches it afterward, so this is only an ordering issue.
- Only administrators can create these in Program Files, so the risk is low.
- Fix: add one small helper that throws if a path is a reparse point. Call it before each of the three operations.

**L2. The move to [Environment] is incomplete.**
- `$env:PROCESSOR_ARCHITECTURE` is still read at line 119, in the same session whose environment line 120 says can't be trusted. Use `[Runtime.InteropServices.RuntimeInformation]::OSArchitecture` or `[Environment]::Is64BitOperatingSystem` plus a CPU check.
- The help example still uses `$env:ProgramFiles` and `$env:SystemRoot`. It runs icacls from that path before any of the script's protections apply.
- I could not check the claim that uninstall.ps1 does the same, because it was not provided.

**L3. The log is stored in a folder the docs tell you to delete.**
- The log disappears with the setup folder. Either say so in the notes or copy it somewhere admin-only, such as `%ProgramData%\hello-world-install.log`.

**L4. Redundant hash checks (lines 257-258 and 260-262).**
- The first check on hello.py is repeated in the loop. Harmless, but you can drop the first and compute $hash once.

**L5. Unverified items to test on one workstation before rolling out to all 5.**
- I couldn't verify the pinned Python 3.14.8 URL and SHA-256 here. Confirm them against the .sigstore file.
- Parse the script on Windows with `[System.Management.Automation.Language.Parser]::ParseFile` and run it once end to end. This also exercises the transcript and GetFolderPath code, which you have not run.
- Click Uninstall in Settings as a standard user and check that it prompts for elevation. uninstall.ps1 was not provided.

## Files
- the review package supplied to the reviewer
