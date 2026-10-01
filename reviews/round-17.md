# Round 17

- Date: 2026-10-01
- Commit reviewed: 0e767dee41bcf990ccc75cb73b942c04cacb3da5 (version 1.4.4)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION; the reviewer also read uninstall.ps1 and BACKLOG.md from the working tree on its own.
- Redactions: three local folder paths in the "Files:" and "What I read" lines were replaced with repo-relative names.

---

Review of 1.4.4 (commit 0e767de): no Critical or High findings. One new Medium in uninstall.ps1, one Medium that is process (the Windows trial run), and four Low items. Nothing here blocks a deploy to 5 PCs once the Windows trial run passes.

**What I read and what I couldn't check**
- Your paste left out uninstall.ps1, so I read it from uninstall.ps1. It is ASCII, and the working tree is clean.
- `python3 test_hello.py` prints "ok".
- pwsh isn't installed, so I could not parse or run either .ps1. Everything below comes from reading the code.
- I did not check the pinned Python 3.14.8 URL or its SHA-256. A wrong value stops the installer before it touches the existing install.
- I read the backlog. I don't re-raise anything declined there: the `GIT_*` variables and `C:\ProgramData\Git`, `$env:SystemRoot` and `$env:ProgramFiles` in install.ps1, the exit code and `-Quiet` switch, the junction at `$dir`, ARM64, and the retry loop around the final folder removal.

**Medium**

M1. uninstall.ps1 trusts `$env:ProgramFiles` and `$env:SystemRoot`, and its elevation path doesn't match the reason the backlog gives for declining this.
- The backlog declines `GetFolderPath` for install.ps1 because "changing those variables needs the admin's own session". That holds for install.ps1, which an admin starts in their own elevated window.
- It doesn't hold for uninstall.ps1. Settings > Apps starts it as the standard employee, and it then calls `Start-Process -Verb RunAs`. As I understand Windows, an elevated process started from a standard user's session inherits that user's environment block. Confirm this on your VM.
- The employee controls that environment. They could run `$env:ProgramFiles='C:\Users\me\x'` in their own window and start `powershell -File "C:\Program Files\hello-world\uninstall.ps1"`.
- If an admin then types credentials into the UAC prompt, the elevated script runs `Remove-Item -Recurse -Force` on `<attacker path>\hello-world`, `.new` and `.old`. If `hello-world` there is a junction, it can delete files the employee shouldn't be able to touch.
- A fake `SystemRoot` also changes which `powershell.exe` the relaunch runs. That one shows as an unknown publisher on the UAC prompt, so it is easier to notice.
- The attack needs an admin to approve a UAC prompt the employee started, which is the usual over-the-shoulder pattern. That is why it is Medium and not High.
- Fix, in uninstall.ps1 only:
  - `$dir = Join-Path ([Environment]::GetFolderPath('ProgramFiles')) 'hello-world'`
  - Use `[Environment]::SystemDirectory` in place of `$env:SystemRoot\System32` for the `powershell.exe` path.
  - Use `[Environment]::GetFolderPath('Windows')` in place of `$env:SystemRoot` in `Set-Location` and `CurrentDirectory`.
  - After elevation, add `if ($PSScriptRoot -ne $dir) { throw ... }`.
- Neither value comes from the environment: `GetFolderPath` reads the registry, and `SystemDirectory` is the OS system directory.

M2. The changes still haven't run or parsed on Windows (process, already in the backlog).
- This round touched the uninstall order and the 64-bit prompt. Neither has been run.
- Before all 5 machines, use one VM or spare PC with Git for Windows installed for all users:
  - Parse both scripts with `[System.Management.Automation.Language.Parser]::ParseFile`.
  - Run the install, then Uninstall from Settings > Apps as a standard user.
  - Install twice to exercise the upgrade.
  - Uninstall with a hello window open to see the failure path.
- The same pilot should confirm the pinned zip hash and URL.

**Low**

L1. The clone check doesn't confirm `.git` sits in `$PSScriptRoot`.
- `git -C $PSScriptRoot rev-parse HEAD` also finds a repository in a parent folder. If someone ran the installer from a folder with no `.git` of its own, git could use one above it, for example a planted `C:\ProgramData\.git`.
- That would only matter alongside the `C:\ProgramData\Git` config issue you accepted, and git's ownership check should refuse such a repository.
- Cheap hardening: `if ((& $git -C $PSScriptRoot rev-parse --show-toplevel) -replace '/','\' -ne $PSScriptRoot) { throw }`, or `Test-Path "$PSScriptRoot\.git"`.

L2. After creating the shortcut, install.ps1 checks only the .lnk file's ACL, not the Start Menu\Programs folder.
- Someone with delete rights on that folder could swap the shortcut.
- The default ACL is fine, but `Assert-AdminOnly (Split-Path $lnk) $swap` would confirm it on each machine.

L3. install.ps1 hashes the copied hello.py but not the copied uninstall.ps1.
- The source is verified against the commit and the destination is admin-only, so the risk is small.
- One more `Get-FileHash` comparison would cover it.

L4. The printed hello.py SHA-256 depends on line endings.
- `.gitattributes` sets `* text=auto`, so on Windows with the default Git for Windows autocrlf the installed file is CRLF.
- Its hash will not match `sha256sum` of the file on Linux. Compare it across the 5 machines, not against Linux. The commit check does not depend on this, because `hash-object` applies the clean filter.

**Checked and found correct**
- The new uninstall order (shortcut, `.new`/`.old`, folder contents except uninstall.ps1, the folder itself, then the Apps entry) matches the notes. A failure leaves the Apps entry in place as the way to try again.
- Deleting uninstall.ps1 while it runs is fine, since PowerShell reads the script first.
- `Set-Location` plus `[Environment]::CurrentDirectory` correctly keeps the process out of `$dir`.
- The 64-bit check now sits before the `try` and waits for Enter, so the message is visible. The exit code is 1 there and 0 elsewhere, as already in the backlog.
- A cancelled UAC prompt is caught.
- The `Where-Object Name -ne` filter and the pipeline into `Remove-Item` behave correctly.
- In install.ps1, the ACL masks, the parent walk, the drive-root exception, the rename and restore logic, the `cmd /c` quoting in the shortcut, the usersRX check, and the commit and hash checks all check out.
- hello.py and test_hello.py handle closed, dead and later-closed stdout correctly with exit 1.

Files: uninstall.ps1, install.ps1, BACKLOG.md
