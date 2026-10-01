# Round 10 review

- Date: 2026-10-01
- Commit reviewed: c013d62168bc10af2f642c6266d24c51f0c40690
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION (plus the newest changelog entry as developer's notes)
- Redactions: none

---

REVIEW OF hello-world 1.3.0 (install.ps1, hello.py, test_hello.py)

Limits first. I read the code but did not run it. I can't verify that python-3.14.8-embed-amd64.zip exists at that URL, or that the pinned SHA-256 (A93ABE45...A310) is the real digest. Check both yourself before rollout (see M3).

Overall verdict: I found no Critical or High issues. The new design is sound. The installer checks Git, the clone and the pinned Python by ACL and hash, and the employee-run interpreter lives in an admin-only folder. I traced the PowerShell syntax, quoting and scoping, the SID and rights-mask logic, the parent-chain check and the icacls grants. I found no functional bug on a clean machine with a stock Git for Windows. The findings below are Medium and Low.

CRITICAL: none.
HIGH: none.

MEDIUM

M1. Git, run as admin, reads configuration outside the two trees you verify.
- The tree checks cover the Git install folder and the clone. Git also reads these:
  - %PROGRAMDATA%\Git\config. Any user can create C:\ProgramData\Git, and current Git for Windows ignores a non-admin-owned file there. That fix is version-dependent, so I'd still close it.
  - The admin's global and XDG gitconfig.
  - GIT_* environment variables (GIT_DIR, GIT_EXEC_PATH, GIT_CONFIG_*, GIT_EXTERNAL_DIFF and similar) inherited by the elevated shell.
- hash-object also applies clean filters and core.autocrlf from that config, so any of them can change what the comparison sees or run a command as admin.
- There is a second, practical problem. Git for Windows sets core.autocrlf=true by default, so the check currently depends on the machine's config for correctness.
- Fix, in three parts:
  - Before any git call, remove GIT_* variables from the environment, then set GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL=NUL and GIT_CONFIG_SYSTEM=NUL (the last two need Git 2.32 or later).
  - Add -c core.autocrlf=false to the documented clone command so the checkout is LF.
  - Use hash-object --no-filters in the installer.

M2. The replace step is destructive and not atomic.
- Remove-Item $dir runs after the hash check but before the new install is built or tested.
- If Expand-Archive, the test run or the ACL check fails, the old working install is gone. That is a real outage on 5 machines.
- Remove-Item also fails halfway if an employee is running hello.cmd or python.exe (a locked file), leaving a half-deleted folder. AV scanning the new files can cause the same kind of failure.
- Fix:
  - Build and verify in a sibling staging folder, for example "Program Files\hello-world.new". hello.cmd uses %~dp0, so it is relocatable.
  - Then rename the old folder to .old, rename .new into place, and delete .old on success.
  - On failure, roll back the rename.
  - Wrap this in try/catch.

M3. Provenance of the pin.
- A digest read from the .sigstore bundle, which comes from the same python.org origin as the zip, adds nothing beyond TLS. The bundle's digest is also base64, so you converted it by hand.
- Verify the signature itself once, on a separate machine, with `sigstore verify identity`. Use the release manager's identity and issuer from python.org/downloads/release/python-3148/.
- Cross-check against the SHA-256 in python.org's Windows package index, if you can reach it.
- Optionally add `Get-AuthenticodeSignature` on python.exe and the DLLs (Subject should be Python Software Foundation, Status Valid). That is cheap defense in depth.
- If the pin is wrong, the script throws before touching the old install, so it fails safe.

M4. The commit-versus-file check can fail open.
- The check is `(git hash-object $f) -ne (git rev-parse "HEAD:$f")`, with no exit-code or empty-output test. If both commands fail and print nothing, `$null -ne $null` is False and the gate passes.
- This is hard to trigger in practice, because rev-parse HEAD must have succeeded just before. But a security gate should fail closed.
- Fix: capture both values, require `$LASTEXITCODE -eq 0` after each, require each to match ^[0-9a-f]{40}$, then compare.

M5. The reparse-point test over-blocks.
- `Attributes -band ReparsePoint` is also set on WOF/CompactOS-compressed files and on cloud-placeholder or dedup files.
- Machines with CompactOS (common on small-SSD OEM laptops) can fail "is a link" inside Git or Program Files. It fails closed, so it is a deployment blocker, not a hole.
- Fix: test `$i.LinkType -in 'SymbolicLink','Junction'`. Alternatively inspect the reparse tag.
- Also, `@(Get-ChildItem -Recurse)` is fully enumerated before any link check, so a junction loop would hang first. Add -Attributes !ReparsePoint handling, or iterate manually without recursing into links.

M6. Lifecycle and exposure of the bundled Python.
- The embeddable Python never auto-updates. You now own CPython security patching on these machines: set a recurring reminder and a process for bumping the URL and hash.
- Employees get RX on python.exe, so they now have a general-purpose interpreter inside Program Files. If you run AppLocker or WDAC with the default Program Files allow rule, that is a script-control bypass.
- The copy will also show up in vulnerability scans as an unmanaged runtime. Document it, and consider a deny or allow rule scoped to hello.cmd.

LOW

L1. The test run executes as admin before Assert-AdminOnlyTree $dir. The ACL is already locked and the content is hash-pinned, so this is not exploitable. Still, move the tree check before the run for ordering hygiene and to match the comment.

L2. Network robustness.
- Invoke-WebRequest has no -TimeoutSec and no retry.
- Authenticated corporate proxies need -Proxy or -ProxyUseDefaultCredentials, or the download fails with a 407.
- Setting SecurityProtocol = Tls12 overwrites other flags. Use -bor.
- python-embed.zip is left behind in the clone after success. Delete it in a finally block.

L3. Architecture. Is64BitProcess is also true on ARM64. The amd64 zip needs x64 emulation, which Windows 10 on ARM lacks. The failure is loud, at the test run. Check PROCESSOR_ARCHITECTURE -eq AMD64 explicitly.

L4. Git discovery.
- StartsWith is case-sensitive, so a differently-cased registry path fails. Use -like or normalize.
- Test-Path should be -LiteralPath.
- If the installing admin is not the current admin, ACE or owner SIDs for that other admin are flagged as non-admin. This is a false positive that fails closed.
- Git's "dubious ownership" error gives an empty $head and a confusing message. Print git's stderr and add `rev-parse --show-toplevel -eq $PSScriptRoot`.

L5. Parent-chain check. It verifies ACLs but not whether a parent is a junction or symlink. Add the same LinkType test in the loop.

L6. hello.cmd. Add `exit /b %ERRORLEVEL%` for explicit exit-code propagation. It currently works, but this is clearer.

L7. hello.py.
- If stdout is closed or None (for example fd 1 closed), print() silently succeeds and returns 0. That contradicts "exit 1 when stdout could not be written". Treat `sys.stdout is None` as a failure. Also catch ValueError.
- The docstring still says to run it as `py -3 hello.py`. That is stale given hello.cmd and the pinned Python.

L8. Tests. They run on the developer's Python, not the pinned 3.14.8 embeddable. Add one CI or smoke run with the exact embeddable zip, using `python.exe -I test_hello.py`, since embeddable Python has no pytest.

L9. There is no transcript or log. For 5 machines, Start-Transcript to a file in the admin-only setup folder gives you an audit trail and debuggability.

What I checked and found correct:
- The icacls grants and inheritance.
- The $swap and $edit masks, including the drive-root exemption.
- The InheritOnly handling.
- The owner check.
- The TrustedInstaller SID.
- The LiteralPath use for Git's "[.exe".
- `-ne` hash case-insensitivity.
- Fail-closed behavior when the Git path is missing.
- The ordering of the download and hash check ahead of the delete.
- The ._pth plus -I combination, which keeps sys.path to the install folder and the stdlib zip.
- The os._exit(1) flow, and the tests' pipe technique on Windows.
- The race on the freshly created setup folder: planted files are owner-flagged, so the tree check throws.

Suggested order of fixes before rollout: M3 (verify the pin), M2 (staging and rollback), M1 and M4 (Git hardening), M5, then the Low items.
