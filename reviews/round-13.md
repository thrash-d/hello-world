# Round 13 review

- Date: 2026-10-01
- Commit reviewed: 624b8bf (Restore an interrupted install before any check that can fail, and make skipped tests visible)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION (plus the newest changelog entry as developer's notes)
- Redactions: none

---

Code review of 1.3.3. Verdict: no Critical and no High findings. The 1.3.3 changes are correct as far as I can tell by reading them. I'm not certain the installer works, because I could only read it.

What I did and did not verify:
- `python3 test_hello.py` on Linux prints "ok" and exits 0.
- `pwsh` is not installed, so `install.ps1` was never run or parsed. I read it line by line for syntax, precedence and cmdlet-parameter errors and found none.
- I could not check the pinned Python hash. The egress proxy blocked www.python.org, so I could not download the zip.

## Medium

**M1. `install.ps1` has never run or parsed anywhere. Treat the first Windows run as a pilot.**
- The script has never executed, and the release notes say so. Most of it is hard to test any other way.
- The risky parts are the ACL walks over the Git tree, the clone and the new `$new` tree, the `Rename-Retry` swap, and the early recovery.
- Failures should fail closed (throw before changing anything). The worst realistic outcome is a first run that throws on every machine for a reason you can't predict from Linux.
- Fix:
  - Run `[scriptblock]::Create((Get-Content .\install.ps1 -Raw))` or `Invoke-ScriptAnalyzer` on any Windows box.
  - Install on one VM or one workstation first, then the other four.
  - Also test on that machine: kill the run mid-swap and rerun, run with the network unplugged and an existing install, and run twice in a row.
  - Compare the Python hash yourself by downloading the zip and running `Get-FileHash`. If the hash or version is wrong, all five installs fail at the download step. That wastes time but does no harm.

**M2. Git runs as admin and trusts configuration outside the tree the script checks.**
- `Assert-AdminOnlyTree` covers the Git install folder and the clone, including `.git/config`.
- It does not cover three other sources git reads when run as admin:
  - the admin's environment variables (`GIT_DIR`, `GIT_CONFIG_*`, `GIT_EXEC_PATH` and similar);
  - the admin's own `~/.gitconfig`;
  - Git for Windows' `C:\ProgramData\Git\config`.
- The `C:\ProgramData` point matters because a standard user can create new folders in `C:\ProgramData`. I am not sure whether your Git version reads that file when its owner isn't an admin; please verify.
- `git hash-object $f` runs clean filters. A `filter.<x>.clean` command in a config source you don't control, combined with `core.attributesFile`, would run a program as admin.
- Fix: before the first git call, set `$env:GIT_CONFIG_NOSYSTEM='1'`, `$env:GIT_CONFIG_GLOBAL='NUL'`, and `$env:GIT_CONFIG_SYSTEM='NUL'` (the last two need git 2.32 or later). Clear any `GIT_*` variables. Or call `git -c core.fsmonitor= -c core.attributesFile=NUL ...`.
- Weigh this against the `-C` flag and `core.autocrlf`: if you add `--no-filters`, a CRLF checkout fails the hash match. A `.gitattributes` with `* text eol=lf` in the reviewed commit solves that.
- Exposure is low if the admin account is a separate account and nobody else can set machine-wide variables.

## Low

**L1. `.old` is restored before any trust check (your declined L4, now more exposed).**
- Early recovery renames `hello-world.old` to `hello-world` with no check of its contents or ACL. Exploiting this needs write access to `Program Files`, which standard users don't have, and the installer never runs the restored folder.
- The risk is that a planted `.old` could become the live install. Cheap hardening: after the restore, run `Assert-AdminOnlyTree $dir` and warn, or only restore after checking the ACL.

**L2. Paths and the account running the installer come from the environment.**
- The script uses `$env:ProgramFiles` and `$env:SystemRoot` for the install path and for `icacls`. `[Environment]::GetFolderPath('ProgramFiles')` and `[Environment]::SystemDirectory` come from the OS and cannot be overridden by a user-level variable.
- This is irrelevant if the admin is a separate account.
- Separately, `$trusted` includes the SID of whoever is running. If a different admin made the clone and the default owner is "object creator", the owner check throws. That fails closed, not open.

**L3. Two renames are not atomic.**
- Between `$dir` to `.old` and `.new` to `$dir` there is a few-millisecond window with no install. Any `hello.cmd` started in that window fails. This is acceptable for 5 PCs.
- There is no mutex, so two simultaneous installs would collide. Also acceptable.

**L4. A rerun after success needs a manual cleanup.**
- The documented flow does `New-Item $d` and `git clone` into it. A second run fails because the folder exists and isn't empty.
- Add a line to the help: run the uninstall one-liner first, or `git fetch` and `checkout` the new commit in place.

**L5. The architecture gate may refuse Windows 11 ARM64 laptops.**
- The `PROCESSOR_ARCHITECTURE -ne 'AMD64'` check blocks native ARM64 PowerShell on Windows 11 ARM64. Those machines can run x64 Python under emulation.
- The check is correct for Windows 10 ARM64, so only change it if you have such machines.

**L6. A Windows 10 build older than 1809 may lack the UCRT runtime the embeddable Python needs, so the test run fails. Informational. A corporate proxy that needs authentication would also make `Invoke-WebRequest` fail, because no `-Proxy` or `-UseDefaultCredentials` is passed.**

**L7. Smaller points, all non-security:**
- `ValidatePattern` is case-insensitive, so an uppercase hash passes validation. That is harmless, because the `-ne` comparison is case-insensitive too.
- `Set-Content` uses `-Path` (wildcard interpretation) for a path with no brackets, so it is harmless, but `-LiteralPath` would be consistent.
- A null owner would slip through `if ($others)`, because `@($null)` evaluates to false. This is practically unreachable.
- `Get-ChildItem -Recurse` in Windows PowerShell 5.1 follows junctions before the link check throws, which only wastes time.

## Tests and `hello.py`

- `hello.py` is correct. I checked every path:
  - Stdout is None: the `OSError` is caught and exit is 1.
  - Stdout closed later: the `ValueError` is caught and exit is 1.
  - Dead pipe: the flush raises, `os._exit(1)` skips the shutdown flush, and stderr was flushed explicitly.
  - Stderr dead or None: the inner `except` swallows the error.
  - The `{e}` text is safe on stderr, because the stream uses `backslashreplace`.
- `test_hello.py` is correct.
  - `unittest.SkipTest` is honored as a skip by pytest and by the plain runner.
  - The new test genuinely exercises the `ValueError` path.
  - The plain runner prints "ok" even when everything is skipped, and it only reports assertion failures through the traceback exit code. This is cosmetic.
- The tests only cover the Linux/posix behavior of dead stdout. They do not cover the installed Windows path, so the installer's one test run, which checks for the exact string "Hello, world!", is your only Windows check.

## Your release notes

I checked each of the 1.3.3 changes against the code.
- Early recovery runs before the Git, ACL and download steps, and uses `Rename-Retry`, as the notes say.
- The `-LiteralPath` changes are valid. `Get-FileHash`, `Copy-Item` and `Expand-Archive` all have that parameter in Windows PowerShell 5.1.
- The Group Policy note is in the help text.

The scenarios I walked through for the swap and recovery logic all end with a working install: `.old` restored, a leftover `.old` deleted, and a swap that fails and rolls back.

Files reviewed:
- /home/user/hello-world/install.ps1
- /home/user/hello-world/hello.py
- /home/user/hello-world/test_hello.py
