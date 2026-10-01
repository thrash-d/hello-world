# Backlog

Changes considered and declined, with the reason.

- Drop the OS error text from the stderr message: the review rated it acceptable, and the errno is what someone debugging a dead stdout needs.
- Support Python 2 or versions before 3.6: f-strings already fail closed with a `SyntaxError`, which the review rated fine.
- Keep `_silence()` and add the review's `try/finally os.close` and exception shield: `os._exit(1)` removes the need for it, with less code.
- Application control, such as AppLocker or WDAC rules or signing the script: Group Policy on the workstations, not code in this repo.
- A scheduled hash check of the installed file: only administrators can change it, and `install.ps1` prints the hash for a manual check.
- Bake hello.py's SHA-256 or the expected commit into `install.ps1`: a commit can't hold its own hash, and a pinned file hash would need updating every release. The installer takes the reviewed commit as `-Commit` and checks both files against it instead.
- Replace the hex masks in `Assert-AdminOnly` with `FileSystemRights` names, as the fifth and sixth reviews asked: the sign-extension claim is wrong. `GENERIC_WRITE` is bit 30 and positive as an int32. Windows maps generic bits to specific rights on stored ACEs, and testing showed every write grant refused.
- Read `VERSION` in the installer, which the sixth review called dead weight: it drives the auto-tag workflow, and `-Commit` is the pin.
- Clear `GIT_DIR`, `GIT_OBJECT_DIRECTORY`, and other `GIT_*` variables before calling git: the installer's environment comes from the admin's own profile and the machine settings, and only administrators can change either.
- Accept uppercase in `-Commit`, as the ninth review asked: `ValidatePattern` and `-ne` both ignore case, so an uppercase hash already works.
- Catch every exception on the stderr write in hello.py, as the ninth review asked: stderr uses the `backslashreplace` error handler, so the `UnicodeEncodeError` it describes can't happen there.
- Make the help example find Git through the registry like the script does: if Git sits somewhere else, the clone step fails visibly.
- Trust every local administrator's SID along with the account running the installer: Git's first run leaves a few files in `Git\etc` owned by whoever installed it. If a different admin installed Git, the tree check refuses that account. Change this if a live install hits it.
- An `uninstall.ps1`: uninstalling is one line in the installer help.
- Leave the clone URL out of the installer help: the repo is private, and the URL names only the pseudonymous account.
- Add TrustedInstaller to the installed folder's ACL to match the source check: nothing needs it there. Trusting it on the source walk lets Program Files and System32 pass.
- Branch protection, 2FA, and force-push rules on GitHub: account settings, not repo files. Decide them in github-mog.
- A smoke run as a standard user through `runas` or a scheduled task: it needs a standard account's credentials on each workstation. The ACL check after install proves the same access.
- Refuse a junction at `Program Files\hello-world` before deleting it: only administrators can create one there.
- Test `hello.cmd`, `-I`, and the ACLs in CI: CI runs on Linux, and the installer checks these itself on each workstation.
- Commit the Python zip to the repo instead of downloading it: that's 12 MB of binary in history for each Python update, and the SHA-256 pinned in the reviewed commit gives the same guarantee.
- Verify the zip's sigstore signature in the installer: it needs a sigstore client on every workstation, and the pinned hash was checked against the sigstore record when it was set.
- Harden Git's environment and config, as the tenth review asked (clear `GIT_*`, `GIT_CONFIG_NOSYSTEM`, `--no-filters`, `core.autocrlf=false` on clone): the `GIT_*` part is declined above. `--no-filters` would refuse a clone with CRLF checkout, while the default clean filter makes the check match on either setting. Revisit `C:\ProgramData\Git\config` if the Git version in use predates its ownership check.
- Test `LinkType` instead of the reparse-point attribute, and check parents for links: the attribute check fails closed, and a loosened check could let a real link through. Change it if a live install stops on a CompactOS file. Replacing a parent with a link needs rights the parent ACL check already refuses.
- Proxy credentials, download retries, and Git's "dubious ownership" message: the install runs once per workstation, and failures are visible.
- `exit /b %ERRORLEVEL%` in `hello.cmd`: the exit code already passes through, and the install test run checks it.
- Run the tests on the pinned embeddable Python in CI: CI lives in `.github/`, which this routine doesn't change.
- A transcript of the install in the setup folder: the console output is enough for five machines.
- Patch reminders for the bundled Python and a scoped allow rule for it: process and Group Policy, not repo code. Updating means changing the URL and hash in `install.ps1`.
