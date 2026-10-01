# Backlog

Changes considered and declined, with the reason.

- Drop the OS error text from the stderr message: the review rated it acceptable, and the errno is what someone debugging a dead stdout needs.
- Support Python 2 or versions before 3.6: f-strings already fail closed with a `SyntaxError`, which the review rated fine.
- Keep `_silence()` and add the review's `try/finally os.close` and exception shield: `os._exit(1)` removes the need for it, with less code.
- Launch with `py -3 hello.py` as the review wrote it: `py -3` also picks per-user Python installs the employee can replace, so `hello.cmd` pins the all-users interpreter.
- Application control, such as AppLocker or WDAC rules or signing the script: Group Policy on the workstations, not code in this repo.
- A scheduled hash check of the installed file: only administrators can change it, and `install.ps1` prints the hash for a manual check.
- Bake hello.py's SHA-256 into `install.ps1`: anyone who can swap hello.py can swap `install.ps1` too. The source folder check covers both files.
- A smoke run as a standard user through `runas` or a scheduled task: it needs a standard account's credentials on each workstation. The ACL check after install proves the same access.
- Detect a stale pinned interpreter: `hello.cmd` fails closed when `python.exe` is gone, and the script help says to run the installer again after a Python change.
- Find Python in `Program Files (x86)`, the Store, or an embeddable zip: refusing is the intended fail-closed path.
- Refuse a junction at `Program Files\hello-world` before deleting it: only administrators can create one there.
- Test `hello.cmd`, `-I`, and the ACLs in CI: CI runs on Linux, and the installer checks these itself on each workstation.
