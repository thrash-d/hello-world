# Round 25

- Date: 2026-10-01
- Commit reviewed: 1931462 (version 1.5.12)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION, plus the newest changelog entry as developer's notes

---

CODE REVIEW: hello-world v1.5.12 (install.ps1, hello.py, test_hello.py)

I reviewed this by reading it only. I did not run it, and I have no Windows machine here. The notes say install.ps1 has never been run, so treat everything below as a static review, not a pass.

The overall design is sound: it uses ACL checks on the whole tree, a pinned commit, a pinned hash, and a build-test-swap with recovery. The findings below are in the order to fix them. I could not confirm findings 1 and 2 without running the script, so test those first.

=== CRITICAL ===
None found. No path lets a standard user gain admin through the installer, as long as the ACL checks work as intended.

=== HIGH ===

H1. Em dashes in two double-quoted strings can break parsing on Windows PowerShell 5.1.
- Where: `Write-Host "Checked $checked items in $Root — all admin-only"` and `Write-Host "Checked parent folders of $Root ... — all parent directories ..."`. The other em dashes are inside the `<# #>` help block and are harmless.
- Why it breaks: Windows PowerShell 5.1 reads a .ps1 file with no BOM as Windows-1252. The UTF-8 bytes E2 80 94 then decode to "â€”" followed by a curly quote (U+201D). PowerShell treats U+201D as a closing double quote. The string ends early, the trailing text is parsed as code, and the script fails with a parse error before anything runs. That includes the `#Requires` check.
- Why you may not have seen it: git checkouts add no BOM, and PowerShell 7 reads UTF-8 by default. Your docs and the `powershell.exe` UninstallString both point at 5.1.
- Fix: replace every non-ASCII character in executable code with ASCII (`-`). Better, add a CI check that fails on any byte above 0x7F in .ps1 files. Check uninstall.ps1 the same way.
- Alternative: save the file as UTF-8 with BOM, but that is fragile.

H2. `GIT_CONFIG_NOSYSTEM=1` plus `git hash-object` will probably make the file check fail on default Git for Windows clones.
- `git hash-object <file>` applies the clean filter and EOL conversion. With the stock `core.autocrlf=true` (set in Git's system config), the working copy is CRLF and hash-object converts it back to LF, which matches the blob.
- The script sets `GIT_CONFIG_NOSYSTEM=1` before this check. If the system config is skipped, no conversion happens, a CRLF file hashes differently from `HEAD:file`, and the installer throws "differs from commit" on every file.
- Your final message ("differs between LF and CRLF checkouts") shows CRLF checkouts are expected.
- Fix, most robust first:
  - Commit a `.gitattributes` containing `* text=auto eol=lf`. Checkouts become deterministic and the installed hello.py hash stops depending on the checkout.
  - Or clone with `-c core.autocrlf=false` and use `hash-object --no-filters`.
  - Or compare with `git diff --quiet HEAD -- <files>` and `git status --porcelain` run with an explicit `-c core.autocrlf=false`.
- Test this on a stock Git install on a real Windows machine.

H3. Nothing has been run on Windows, and the stated change is "section headers only".
- I cannot see the diff, so I cannot confirm that only comments changed.
- Before touching 5 production PCs, parse-check the file: `[System.Management.Automation.Language.Parser]::ParseFile(...)` under powershell.exe 5.1, and run PSScriptAnalyzer.
- Then do a full install, re-install, interrupted-install and uninstall cycle on a clean Windows 10 or 11 VM with standard Git for Windows.
- uninstall.ps1 was not included. It runs elevated from the Settings Uninstall button, so it needs the same review.

=== MEDIUM ===

M1. The documented bootstrap runs git as admin before git is verified.
- The example runs `git clone` before install.ps1 checks that Git's folders are admin-only. A user-writable Git install would already be exploited by then.
- Fix: put the Git ACL check in a small standalone step that runs first, or say plainly in the docs that Git must be verified first.

M2. The ProgramData Git check will likely fail on a stock machine, and the error does not say how to fix it.
- The default `C:\ProgramData` ACL gives Users `(CI)(WD,AD)`. That is inherited by `C:\ProgramData\Git`, and it matches your `$edit` mask (WriteData and AppendData). On many PCs the installer will refuse and the operator will not know why.
- A user who could create `ProgramData\Git\config` would be planting a config that git reads.
- Fix: add the exact remediation to the error message, for example `icacls "C:\ProgramData\Git" /inheritance:r /grant:r *S-1-5-32-544:(OI)(CI)F *S-1-5-18:(OI)(CI)F *S-1-5-32-545:(OI)(CI)RX`.
- Also verify whether Git for Windows still reads that file when NOSYSTEM is set. If it does not, the check is redundant, but keeping it does no harm.

M3. The environment-clearing comment overstates what it does.
- It says git "uses only the reviewed clone and pinned configuration".
- Removing HOME and XDG_CONFIG_HOME makes Git for Windows fall back to HOMEDRIVE+HOMEPATH or USERPROFILE. The elevated user's `~/.gitconfig` is still read.
- That file is normally admin-only, but if the admin runs as a different account, or the profile is redirected, it is not controlled by the installer.
- Fix: set `GIT_CONFIG_GLOBAL=NUL` after the GIT_* purge, which needs Git 2.32 or later. Or pass `-c` overrides on every call (`core.fsmonitor=`, `core.hooksPath=NUL`, `core.autocrlf=...`). Correct the comment either way.

M4. Source integrity checks cover only 4 files, and the `.git` check is shallow.
- `Test-Path .git` also passes when `.git` is a file containing `gitdir: <elsewhere>`, or when `.git` uses `objects/info/alternates` or `commondir` that point outside the checked tree.
- Only an admin can create these, so this is social-engineering risk, not an attack by standard users.
- Fix: require `.git` to be a real directory, and check it has no `alternates` or `commondir`. Also run `git status --porcelain --untracked-files=all` and fail on any output, so extra or modified files are caught.

=== LOW ===

L1. The parent-folder walk does not reject reparse points.
- A junction in an ancestor path means the ACLs checked are not the physical ones. Check `Attributes -band ReparsePoint` on each parent and on `$PSScriptRoot` itself.

L2. Tree enumeration happens fully before any link check.
- `Get-ChildItem -Recurse` on 5.1 descends junctions, so a loop or a very deep link could hang or error before the reparse check fires. It fails closed, only admins can create such links, and impact is low.
- Fix: use manual recursion that does not descend into reparse points.

L3. `cmd.exe /c` is used without `/d` (Remove-Tree, and the shortcut's cmd.exe). cmd then honors AutoRun registry values.
- For the elevated admin this is the admin's own HKCU, so it is a weak issue. For the employee shortcut it is the employee's own session. Add `/d` anyway.

L4. git runs inheriting the PowerShell current directory, which the script never sets. The DLL search path and relative-path surprises depend on where the admin launched from.
- Fix: `Set-Location -LiteralPath $PSScriptRoot` early, or use a trusted cwd.

L5. `$git.StartsWith("$pf\")` is a string prefix check with no path normalisation, so `..` segments would pass. The registry is admin-only, so this is hardening only.
- Fix: call `[IO.Path]::GetFullPath` first.

L6. The rights masks omit WriteAttributes and WriteExtendedAttributes (0x100 and 0x10). Probably acceptable, but note it if you advertise "cannot modify".

L7. The install can end half-finished. If the registry or shortcut step fails after the folder swap, the new install is live but unregistered. The comments call this intentional.
- Consider a cleanup trap that removes the Apps key and shortcut on failure, or a clear message telling the operator to re-run.

L8. Smaller operational points:
- The restore failure in the swap `catch` can mask the original error (the throw from the restore replaces it).
- The Python download has no proxy support (`-Proxy` or `-UseDefaultCredentials`) for corporate networks.
- Python 3.14.x gets no automatic patching, so plan a process for bumping the pin.
- I could not verify that the 3.14.8 URL and SHA-256 are correct. Independently download the zip, compare the hash, and verify the sigstore bundle once before relying on the pin.
- `ServicePointManager` and `$ProgressPreference` changes persist in the operator's session, which is cosmetic.

=== hello.py and test_hello.py ===
No bugs found.
- The None stdout, closed-fd, ValueError and dead-stderr paths are handled. `os._exit(1)` after flushing stderr is correct for avoiding exit code 120.
- Tests: `preexec_fn` is POSIX-only, and the test file mixes pytest-style functions with a hand-rolled runner. Neither is a defect.
- Windows behaviour of the dead-pipe tests is untested, but the installer only needs the happy path.

=== Things I checked and found correct ===
- String interpolation such as `"$dir.new"`, `"$dir."` and `` `: `` escapes.
- `ValidatePattern` is case-insensitive and `-ne` is too, so uppercase hashes still work.
- The InheritOnly handling, `-LiteralPath` use and trusted-SID list.
- The shortcut quoting `/c ""…hello.cmd" & pause"`.
- The Users read-and-execute grant does not overlap `$edit`.
- try/catch/finally nesting and transcript handling.
- The rename-based swap with recovery.

RECOMMENDATION: do not deploy until H1 and H2 are fixed and the full install cycle has been run on a Windows 10 or 11 VM. Fix H3 by doing that VM run. After that, M1 to M4 are worth doing before a wider rollout, but with 5 PCs they are not blockers.
