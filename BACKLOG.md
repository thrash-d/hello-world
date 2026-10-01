# Backlog

Changes considered and declined, with the reason.

- Drop the OS error text from the stderr message: the review rated it acceptable, and the errno is what someone debugging a dead stdout needs.
- Support Python 2 or versions before 3.6: f-strings already fail closed with a `SyntaxError`, which the review rated fine.
- Keep `_silence()` and add the review's `try/finally os.close` and exception shield: `os._exit(1)` removes the need for it, with less code.
- Launch with `py -3 hello.py` as the review wrote it: `py -3` also picks per-user Python installs the employee can replace, so `hello.cmd` pins the all-users interpreter.
- Application control, such as AppLocker or WDAC rules or signing the script: Group Policy on the workstations, not code in this repo.
- A scheduled hash check of the installed file: only administrators can change it, and `install.ps1` prints the hash for a manual check.
- Bake hello.py's SHA-256 or the expected commit into `install.ps1`: a commit can't hold its own hash, and a pinned file hash would need updating every release. The installer takes the reviewed commit as `-Commit` and checks both files against it instead.
- Replace the hex masks in `Assert-AdminOnly` with `FileSystemRights` names, as the fifth and sixth reviews asked: the sign-extension claim is wrong. `GENERIC_WRITE` is bit 30 and positive as an int32. Windows maps generic bits to specific rights on stored ACEs, and testing showed every write grant refused.
- Read `VERSION` in the installer, which the sixth review called dead weight: it drives the auto-tag workflow, and `-Commit` is the pin.
- Clear `GIT_DIR`, `GIT_OBJECT_DIRECTORY`, and other `GIT_*` variables before calling git: the installer's environment comes from the admin's own profile and the machine settings, and only administrators can change either.
- Fall back to an older working Python when the newest registered one is broken: refusing tells the admin to repair it, and silently picking another version would hide the broken install.
- Shrink `PATH` in `hello.cmd`: with Python's DLLs required next to `python.exe`, Windows finds them there first. The employee's own PATH can only affect the employee's own run.
- Print exit codes as `[uint32]` in hex: `$LASTEXITCODE` is an int32, so `{0:X8}` already prints `C0000135`.
- Tie `ExecutablePath` to the registry key's `InstallPath`, as the ninth review asked: changing HKLM takes admin, and the path pattern, link refusal, and tree check already cover where it points.
- Accept uppercase in `-Commit`, as the ninth review asked: `ValidatePattern` and `-ne` both ignore case, so an uppercase hash already works.
- Catch every exception on the stderr write in hello.py, as the ninth review asked: stderr uses the `backslashreplace` error handler, so the `UnicodeEncodeError` it describes can't happen there.
- Make the help example find Git through the registry like the script does: if Git sits somewhere else, the clone step fails visibly.
- Trust every local administrator's SID, not only the account running the installer: Git's first run leaves a few files in `Git\etc` owned by whoever installed it. If a different admin installed Git, the tree check refuses that account. Change this if a live install hits it.
- An `uninstall.ps1`: uninstalling is one line in the installer help.
- Leave the clone URL out of the installer help: the repo is private, and the URL names only the pseudonymous account.
- Add TrustedInstaller to the installed folder's ACL to match the source check: nothing needs it there. Trusting it on the source walk lets Program Files and System32 pass.
- Check the Authenticode signature on the pinned `python.exe`: replacing it under Program Files already takes admin rights.
- Branch protection, 2FA, and force-push rules on GitHub: account settings, not repo files. Decide them in github-mog.
- A smoke run as a standard user through `runas` or a scheduled task: it needs a standard account's credentials on each workstation. The ACL check after install proves the same access.
- Detect a stale pinned interpreter: `hello.cmd` fails closed when `python.exe` is gone, and the script help says to run the installer again after a Python change.
- Find Python in `Program Files (x86)`, the Store, or an embeddable zip: refusing is the intended fail-closed path.
- Refuse a junction at `Program Files\hello-world` before deleting it: only administrators can create one there.
- Test `hello.cmd`, `-I`, and the ACLs in CI: CI runs on Linux, and the installer checks these itself on each workstation.
