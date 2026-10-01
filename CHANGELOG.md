# Changelog

## 2026-10-01: Add a Start menu shortcut and an uninstall entry

Version 1.4.0. After the first successful live install, three problems came up. Opening `hello.cmd` from Explorer flashed a window that closed before the line could be read. Employees had no reasonable way to find the program inside Program Files. Uninstalling meant typing a command.

- `install.ps1` adds a hello-world shortcut to the all-users Start menu. It runs `cmd /c "hello.cmd" & pause`, so the window stays open until a key is pressed. `hello.cmd` itself doesn't pause, so the installer's test run and scripted use don't wait for a key. The shortcut is checked so only administrators can change it.
- `install.ps1` registers hello-world in Settings > Apps with its version from `VERSION`. The entry's Uninstall button runs the new `uninstall.ps1`, which asks for administrator rights. It then removes the shortcut, the Apps entry, and the install folder.
- The shortcut and the Apps entry are added only after every check passes, so a failed install doesn't show up anywhere.
- `uninstall.ps1` and `VERSION` are now checked against the reviewed commit along with `install.ps1` and `hello.py`.

`uninstall.ps1` also removes the `hello-world.new` and `hello-world.old` folders an interrupted install can leave, so the long uninstall line in the help is gone.

Removed from `BACKLOG.md`: the declined `uninstall.ps1`, which this change adds, and keeping `-ErrorAction SilentlyContinue` on the uninstall line, which no longer exists.

Tested under Windows PowerShell 5.1 by installing to a test folder with a space in its name, with the Start menu folder and the Apps entry moved somewhere an unelevated test could write. The install passed every check. The shortcut's exact command line printed the line and reached the pause, and the Apps entry showed version 1.4.0 with the expected Uninstall command. Running the uninstaller from inside the install folder removed the folder, the shortcut, and the entry. Unelevated, the uninstaller's administrator check reads false, so the real one asks for elevation.

Also tested on Windows: the 1.3.1 to 1.3.3 installer changes, which their entries below list as never run or parsed. It parses under Windows PowerShell 5.1 and PowerShell 7. Under 5.1 it installed fresh, and it upgraded over an existing install with no `.new` or `.old` left behind. With the install folder renamed to `.old` to fake an interrupted swap, a run that then failed the commit check still put the old install back, and it worked. With a file held open in the live install, the swap failed after its retries. The live install stayed in place and still ran, and `.new` was removed. In that case the error reads "Access to the path ... is denied", which doesn't say a file is open.

## 2026-10-01: Restore an interrupted swap before any check, and make the tests report skips

The twelfth review, of 1.3.2, answered here. Version 1.3.3. It found no Critical or High issues, 2 Medium and 5 Low; saved in `reviews/round-12.md`.

- The installer restores `hello-world.old` as `hello-world` right after the helper functions, before the Git, ACL, commit and download steps. The review said (M1): "Interrupted-swap recovery runs too late, so an offline or failed run leaves the workstation with no install." It uses `Rename-Retry`, as the review asked.
- A skipped test raises `unittest.SkipTest`, and the plain runner prints `SKIPPED <name>: <reason>`. The review said (M2): "pytest captures stdout and reports the test as passed."
- New test `test_stdout_closed_after_start_exits_1` covers the `ValueError` path. The review said (L1): "The new `except (OSError, ValueError)` path has no regression test." Checked by reverting `hello.py` to catch only `OSError`: the test fails.
- `Get-FileHash` and `Copy-Item` take `-LiteralPath`. The review said (L2): "Wildcard-interpreting cmdlets are used on paths that could contain `[`."
- The help notes that a Group Policy execution policy makes the `Set-ExecutionPolicy` line error. The review said (L7): "Mention that in the help."

Declined, and added to `BACKLOG.md`: the slow permission walk and long paths (L3), checking `.old` before restoring it (L4), the uninstall line's `SilentlyContinue` (L5), and the Python patch reminder (L6). The informational notes need no change.

Tested: `python test_hello.py` passes on Linux. Not tested: all of `install.ps1`. `pwsh` isn't installed here, so it wasn't even parsed. The earlier recovery, the `-LiteralPath` changes, and the help text need a Windows workstation.

## 2026-10-01: Recover an interrupted swap, retry the rename, and keep a late failure from failing the install

The eleventh review, of 1.3.1, answered here. Version 1.3.2. It found no Critical or High issues; saved in `reviews/round-11.md`.

- The installer puts `hello-world.old` back as `hello-world` at the start of a run if the install folder is missing, before it clears leftovers. The review said: "If power or the session is lost between the two renames, `hello-world` is gone and `hello-world.old` is the only working copy. The next run deletes `.old` at the very start."
- Each folder rename retries up to 5 times, a second apart. The review said: "Renaming a folder fails if any file under it is open without share-delete. This can happen with Defender scanning the freshly extracted Python."
- If removing `.old` fails after the new install is live, the installer warns and still prints the "Installed" line. The review said: "the new install is already live, but the script throws and never prints the 'Installed' line."
- A failed run deletes `hello-world.new`, and the uninstall line in the help now covers `.new` and `.old`. The review said: "The uninstall line also does not remove `hello-world.new` or `hello-world.old`."
- The help states that the guarantees hold only if employees use standard accounts. The review said: "State this precondition in the docs."
- `hello.py` also catches `ValueError`, which a stdout object closed after startup raises. The review said: "use `except (OSError, ValueError)`." Checked by closing `sys.stdout` before running it: exit 1 with the one-line message, where 1.3.1 gave a traceback.
- `test_hello.py` prints a SKIPPED line when the closed-stdout test can't run. The review said: "Use `pytest.skip` or an explicit 'SKIPPED' line so the gap is visible."

Declined, and added to `BACKLOG.md`: the pilot install and hand-checked zip hash (M1, process, not code), hashing exact bytes and cleaning Git's environment (L7, already declined as M1 last round), `GetFolderPath` in place of environment variables (L8), the architecture check (L9), and the reparse-point change (L10, already declined). L13 needs no change.

Tested: `python test_hello.py` passes on Linux, and the closed `sys.stdout` case above. Not tested: all of `install.ps1`. `pwsh` isn't installed here, so it wasn't even parsed. The interrupted-swap recovery, the rename retry, the late-failure warning, the `.new` cleanup, and the changed uninstall line need a Windows workstation.

## 2026-10-01: Build the new install beside the old one and fail closed on the commit check

The tenth review, of 1.3.0, answered here. Version 1.3.1. It found no Critical or High issues; saved in `reviews/round-10.md`.

- The installer builds and tests the new install in `Program Files\hello-world.new`, and only then renames it into place, putting the old folder back if the rename fails. The review said: "Remove-Item $dir runs after the hash check but before the new install is built or tested. If Expand-Archive, the test run or the ACL check fails, the old working install is gone." Leftover `.new` or `.old` folders from an interrupted run are cleared at the start of the next one.
- The per-file commit check requires each git call to succeed and print a 40-character hash. The review said: "If both commands fail and print nothing, `$null -ne $null` is False and the gate passes."
- The tree and Users read-and-run checks now run on the new folder before the test run. The review said: "The test run executes as admin before Assert-AdminOnlyTree $dir."
- The zip is deleted after the run, pass or fail, and the download has a 300-second timeout. TLS 1.2 is added to the protocol flags instead of replacing them. The review said: "Setting SecurityProtocol = Tls12 overwrites other flags. Use -bor." and "python-embed.zip is left behind in the clone after success."
- The installer refuses unless `PROCESSOR_ARCHITECTURE` is `AMD64`. The review said: "Is64BitProcess is also true on ARM64. The amd64 zip needs x64 emulation."
- The Git path check ignores case, and `Test-Path` takes `-LiteralPath`. The review said: "StartsWith is case-sensitive."
- `hello.py` exits 1 when `sys.stdout` is `None`. The review said: "If stdout is closed or None (for example fd 1 closed), print() silently succeeds and returns 0." New test `test_closed_stdout_exits_1`, which fails on 1.3.0 (exit 0). The docstring no longer says to run it with `py -3`.

Declined, and added to `BACKLOG.md`: the Git config and environment hardening (M1), the reparse-point test change (M5, L5), the proxy, retry, and Git ownership messages (L2, L4), `exit /b` in `hello.cmd` (L6), a CI run on the embeddable Python (L8), a transcript (L9), and the Python patching and application control notes (M6). M3, checking the pinned hash against a signature, is not code. It needs a person on another machine.

Tested: `python test_hello.py` passes on Linux. Not tested: all of `install.ps1`. `pwsh` isn't installed here, so it wasn't even parsed. The rename swap and rollback, the ACL and tree checks, the download, the architecture check, and the Git calls need a Windows workstation. This sandbox's proxy blocked python.org, so the pinned zip hash wasn't re-checked either.

## 2026-10-01: Bring a pinned Python instead of using the workstation's

Version 1.3.0. Three live installs in a row stopped on the workstation's own Python: first a missing `python314.dll`, then no all-users Python registered at all while it was being reinstalled. Each fix to the discovery code exposed the next way a machine's Python can be wrong.

- `install.ps1` no longer looks for an installed Python. It downloads the python.org embeddable Python 3.14.8 for 64-bit Windows. It checks the zip against a SHA-256 pinned in the script before touching the old install, then unpacks it into `Program Files\hello-world\python`. The pinned hash matches the digest in python.org's `.sigstore` file for that zip.
- `hello.cmd` runs `%~dp0python\python.exe`, a path inside the install folder. No interpreter path is written into the cmd line anymore.
- The permission check after install covers the whole install folder, Python included.
- Removed: the PEP 514 registry lookup, the Program Files path pattern, the DLL list, the tree check on the system Python, and the start check. The zip ships all four DLLs next to `python.exe`, and the tree check on the install folder covers them.
- Workstations now need Git for Windows and internet access, but no Python. Updating Python means changing the URL and hash in `install.ps1`.

Removed from `BACKLOG.md` because the change makes them moot: launching with `py -3`, falling back to an older Python, shrinking `PATH` in `hello.cmd`, printing exit codes as `uint32`, tying `ExecutablePath` to `InstallPath`, an Authenticode check on the pinned `python.exe`, stale-interpreter detection, and finding Python outside Program Files.

## 2026-09-30: Refuse with a clear message when no Python is registered

Version 1.2.5. The third live install stopped with "Cannot bind argument to parameter 'Path' because it is null." No all-users Python was registered on that workstation while Python was being reinstalled. In Windows PowerShell 5.1, the empty result of `$python = if ($key) { ... }` makes `-notmatch` return nothing, which reads as false. The "Need Python 3" guard never fired, and `Split-Path` got the missing value. The guard now tests for a missing value first. It failed closed either way, but with a message that pointed at the wrong step.

Tested by running the installer from a `v1.2.4` clone in `C:\ProgramData` under Windows PowerShell 5.1 on a machine with no all-users Python. That gave the same error as the workstation. With the fix it stops with "Need Python 3 installed for all users in C:\Program Files\Python3*. Found: ''". The Git tree and clone checks passed on the way there.

## 2026-09-30: Check the whole Git and Python trees before running them

The ninth review, of 1.2.3, answered here. Version 1.2.4.

- New `Assert-AdminOnlyTree` checks a folder, everything under it, and every folder above it, and refuses links anywhere in the tree. It runs on the Git install, the Python install, and the clone, which now includes `.git`. The review said: "It never runs `Assert-AdminOnly` on `python.exe`, those DLLs, or the install directory." The gap was wider than the review's fix: the start check and the test run load Python's standard library as admin, and the installer runs git as admin. One employee-writable file anywhere in either tree was enough.
- `python3.dll` and `vcruntime140_1.dll` must also sit next to `python.exe`. The review said: "Official Windows CPython also ships `python3.dll` next to `python.exe`. Many current VC++ runtimes also need `vcruntime140_1.dll`."
- The installer refuses to run from 32-bit PowerShell. The review said: "A 32-bit elevated host reads `WOW6432Node` and `$env:ProgramFiles` is `C:\Program Files (x86)`."
- `Assert-AdminOnly` reads ACLs with `-LiteralPath`. Git ships a file named `[.exe`, and `Get-Acl` read the bracket as a wildcard and failed. Found while testing the tree check.
- The help has a one-line uninstall. The installer creates only the install folder and the setup folder.

Tested: the Git tree, 10,101 items, was accepted in about 11 seconds. A folder holding one file with Modify for Authenticated Users was refused, and so was a junction. `[Environment]::Is64BitProcess` is false under the 32-bit Windows PowerShell host. The script parses under Windows PowerShell 5.1.

## 2026-09-30: Require Python's DLLs next to python.exe

The eighth review, of 1.2.2, answered here. Version 1.2.3.

- `install.ps1` refuses unless `python3XX.dll`, named from the registry key, and `vcruntime140.dll` sit in the same folder as the pinned `python.exe`. The review said: "If `python.exe` is present and `python314.dll` is **not** beside it, Windows will search `PATH`. An employee-writable `PATH` entry can supply that DLL, the preflight can pass, and both the admin test and later `hello.cmd` load that DLL into whoever runs it." The start check added in 1.2.2 would have loaded that DLL as admin.
- The help example clones `<release tag>` instead of a fixed tag. The review said: "Help still clones `v1.2.0`. ... A tag/name mismatch is how you install the wrong tree if `-Commit` is copied from an old note."

Tested on a copy of `python.exe` without `python313.dll`, which was refused, and on one without `vcruntime140.dll`, also refused. The real install was accepted. The script parses under Windows PowerShell 5.1.

## 2026-09-30: Start the pinned Python before replacing the install

Version 1.2.2. The second live install failed its test run with exit -1073741515, `0xC0000135`, a missing DLL. The pinned `C:\Program Files\Python314` had `python.exe` but no `python314.dll` or `python3.dll`, so that Python install is broken. The installer only found out after it had deleted and rebuilt `Program Files\hello-world`. On a machine with a working earlier install, that would leave a launcher that can't run. It now starts the pinned Python with `-I -c pass` before changing anything. It refuses with the exit code in hex and says what `0xC0000135` means.

Tested by copying `python.exe` and the VC runtime DLLs without `python313.dll`, with Python folders taken off PATH, since Windows also searches PATH for DLLs. The copy exited `0xC0000135`, the same as the workstation, and the check refused it. A working Python was accepted. The script parses under Windows PowerShell 5.1.

## 2026-09-30: Ignore Delete on the drive root

Version 1.2.1. The first live install refused with "Non-administrators can change C:\ (S-1-5-11)". That workstation grants Authenticated Users Modify on `C:\` itself, where the Windows default is create-folders only. Modify includes Delete, which the parent walk refuses. A drive root can't be deleted or renamed, so the walk now ignores Delete on the root and still refuses every other swap right there. Modify doesn't include DeleteChild, so no user can move `ProgramData` or `Program Files` out from under the root.

Tested: Modify on the root now passes, Full Control on the root is still refused, and the walk from a Program Files folder up to `C:\` passes. The script parses under Windows PowerShell 5.1.

## 2026-09-30: Split the install example into short lines

The second live attempt never ran. The 300-character one-line example hard-wrapped in the terminal it was copied from, and each fragment failed to parse. The help example is now six short lines, run one at a time in the same window. Help text only, so no version bump.

## 2026-09-30: Allow scripts in the install example

The first live install stopped at `.\install.ps1` with "running scripts is disabled on this system", because Windows clients default to the Restricted execution policy. The help example now runs `Set-ExecutionPolicy -Scope Process Bypass -Force` first, which lasts only for that PowerShell window. Help text only, so no version bump.

The live run was in Windows PowerShell 5.1. The installer parses cleanly there, and its ACL check and git pin behave the same as in PowerShell 7.

## 2026-09-30: Run git and icacls by full path

The seventh review, of 1.1.0, answered here. Version 1.2.0.

- `install.ps1` runs git from the all-users Git for Windows install, read from `HKLM\SOFTWARE\GitForWindows`, and refuses when that's missing or outside Program Files. It runs icacls from System32. The review said: "Commit and blob checks are only as strong as the `git.exe` that answers `rev-parse` / `hash-object`. Admin `PATH` can still start with a user-writable directory." The risk was larger than a lying git: anything the installer finds on PATH runs as admin. That applies to icacls too.
- The help example calls both tools by full path, clones `v1.2.0`, and says to pass the full commit hash, never a tag name. The review said: "Keep using the full hash, not the tag name, in `-Commit`."

The review withdrew the sign-extension finding.

Tested with a fake `git.cmd` first on PATH that printed the expected commit. Given a wrong `-Commit`, the installer's check still refused, because it used the pinned git. The right commit was accepted and a wrong one refused. No bare `git` or `icacls` calls are left in the script.

## 2026-09-30: Require the reviewed commit and a locked clone folder

The sixth review, of the v1.0.0 tree, answered here. Version 1.1.0.

- `install.ps1` takes a mandatory `-Commit`, the full hash that was reviewed. It refuses when the clone's HEAD is another commit, or when `install.ps1` or `hello.py` differ from that commit's blobs. The review said: "Installer does not pin SHA-256 or `git rev-parse HEAD`. A moved tag or a swap after you looked at HEAD still installs" and "The human `rev-parse` check is the real control; the script does not enforce it."
- The clone folder itself must now be closed to everyone but administrators, including adding files. Its parents still only need to be safe from a swap. Without that rule, someone could add git objects to the clone that fool the commit check. The help example locks the folder before cloning into it. The review said: "Create the setup directory yourself, tighten its ACL **before** clone, then clone into that empty locked folder."

Finding 1, the sign-extension claim, came back unchanged and still needed no change. `GENERIC_WRITE` (`0x40000000`) is positive as an int32. Widening `0xC0000000` to int64 gives `0xFFFFFFFFC0000000`, which still has bit 30. The value in the review, `0xFFFFFFFF80000000`, is `GENERIC_READ`. See `BACKLOG.md` and the entry below.

Tested against a local clone. The right commit was accepted. A wrong commit, an edited `hello.py`, an edited `install.ps1`, and a folder with no clone were each refused, and `-Commit HEAD` failed the hash pattern. A default folder under `C:\ProgramData` was refused because Users can add files to it; one locked as in the help example was accepted.

## 2026-09-30: Version 1.0.0 and install from a release tag

The fifth review, for five workstations, answered here.

- New `VERSION` file at 1.0.0. The existing auto-tag workflow tags `v1.0.0` on push, and each bump after that gets its own tag. The review said: "Tag a release, install that tag, record the commit on the five machines."
- The `install.ps1` help now says to clone a release tag into a new folder under `C:\ProgramData` as administrator, check `git rev-parse HEAD` against the reviewed commit, and run the installer there. The review said: "clone or copy a **pinned tag/commit** to an admin-only directory, then run `.\install.ps1`."

Finding 2, "`FileSystemRights` bitmask is not trustworthy", needed no change; see `BACKLOG.md`. Tested by storing ACEs with generic rights on a file, through icacls and through SDDL. Windows mapped them to specific rights both times, and the check refused every grant that included write: GW, GA, and GR with GW. GR alone and GR with GX passed. `GENERIC_WRITE` is bit 30, not the sign bit, and widening a negative int32 to int64 keeps the low 32 bits, so no write bit is lost.

Also tested: a folder created under `C:\ProgramData` and the two copied files passed the source check. The only account flagged was the creator, a standard user in the test. When an administrator creates the folder, that entry is Administrators. `python test_hello.py` passes.

## 2026-09-30: Refuse an installer source that non-admins can change

The fourth review, covering hello.py, install.ps1, and test_hello.py, answered here.

- `install.ps1` now refuses to run when a non-administrator can change `install.ps1`, `hello.py`, or any folder above them up to the drive root. It also refuses when such an account owns one of them. The review said: "If an admin right-clicks `install.ps1` in `Downloads` / Desktop / a share the user can write, another process can swap `hello.py` (or the script) before `Copy-Item`."
- The pinned Python path must now match `Program Files\Python3*\python.exe` with no `"`, `%`, or `&`. The review said: "A PEP 514 `ExecutablePath` that contained `&`, `%`, or `"` would break quoting or, in ugly cases, run extra commands."
- After installing, the same check runs on the install folder, `hello.py`, and `hello.cmd`, and Users must have read and run access to each. The review said: "The smoke test runs as SYSTEM/Administrator. It does not prove Users-only `RX`" and "You do not verify the resulting DACL contains exactly those three SIDs."
- The test-run output is compared as one string. The review said: "`& hello.cmd` sometimes yields an array or a trailing CR."
- `test_hello.py` compares stderr as bytes. The review said: "A localized `OSError` string can theoretically trip the 'starts with / one line' asserts."

Tested without admin rights on a dev machine by loading the check from `install.ps1`. It refused the repo folder once the account running it wasn't the folder's owner. It also refused the repo folder for its owner, because an orphaned account SID has write access on a folder above it. It passed `Program Files\Git` up to `C:\` and `System32\notepad.exe`. On a scratch folder with the installer's three access entries, the post-install check passed; after Authenticated Users got modify on `hello.py`, it refused. The path pattern accepted `Program Files\Python313` and `Python313-arm64`, and rejected `C:\Python313`, `&`, `"`, and a nested folder. `python test_hello.py` passes. The full installer has not yet run as administrator.

## 2026-09-30: Skip the shutdown flush and add a locked-down installer

The third hello.py review answered here.

- `_silence()` is gone. The error path now calls `os._exit(1)` after the stderr message, which skips the shutdown flush that `_silence()` existed to defuse. That closes three findings at once, because the code they point at no longer exists:
  - "Leaked file descriptor. `os.open(...)` returns a new fd. ... the original fd from `os.open` is never `os.close`d."
  - "`_silence` is unguarded. `fileno()`, `os.open`, or `dup2` can still raise ... That exception escapes `main()`."
  - "Process-wide fd replacement. After `_silence`, anything else in this process that still holds fd 1 or 2 writes to null."
- The stderr message is flushed explicitly, since `os._exit` skips every flush.
- New `test_hello.py` runs the script against a closed pipe as stdout, then as stdout and stderr, and checks for exit 1. It fails on the round 2 code that exited 120. CI's dependabot check runs `test_*.py` files with pytest.
- New `install.ps1` does the deployment controls that `BACKLOG.md` had declined as rollout steps. The review said: "Ship it as `py -3 hello.py` from a locked-down path." The script installs to `Program Files\hello-world` with write access for Administrators and SYSTEM only. It writes `hello.cmd`, which pins the all-users Python 3 instead of calling `py -3`, because `py -3` also selects per-user installs that the employee can replace. The launcher runs Python with `-I`, so `PYTHON*` variables and user site-packages can't inject code. The script refuses to install if no all-users Python is under Program Files.

Review finding 3, "Wrong object silenced on some failures", needed nothing beyond the `_silence()` removal. Findings 5 and 6 and the PEP 8 note needed no change; the file already has two blank lines around top-level definitions.

Tested with `python test_hello.py` on the new code and on the round 2 code, where it fails as it should. `install.ps1` was run unelevated on a dev machine. Its guard refused there, since that machine has only a per-user Python. A copy pointed at a scratch folder installed, ran `hello.cmd`, and matched the source hash. With only the Users grant left, writes and new files in the folder were denied. It has not yet run as administrator against the real `Program Files`.

## 2026-09-30: Exit 1 on dead stdout or stderr instead of 120

The second hello.py review answered here.

- A failed stderr write in the error handler is now caught. The review said: "If stdout is dead *and* stderr is also unusable, the handler's `print(..., file=sys.stderr)` raises a second `OSError` that is not caught."
- After a failed write, the stream's fd is pointed at devnull. Testing the finding above showed a worse bug the review missed: with only stdout dead, the script exited 120, not 1. The failed text stays buffered, and Python's shutdown flush fails a second time. The both-dead case also exited 120.
- A module docstring now gives the Windows invocation and the exit codes. The review said: "operators must still call an explicit interpreter" and "Exit-code contract is implicit. ... Document it if this is used as a health check."

Tested by running the script against a pipe with a closed read end, as stdout alone and then as both stdout and stderr. Both cases now exit 1, and the normal and redirected runs still print the line and exit 0.
