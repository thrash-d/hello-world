# Backlog

Changes considered and declined, with the reason.

- Drop the OS error text from the stderr message: the review rated it acceptable, and the errno is what someone debugging a dead stdout needs.
- Support Python 2 or versions before 3.6: f-strings already fail closed with a `SyntaxError`, which the review rated fine.
- Keep `_silence()` and add the review's `try/finally os.close` and exception shield: `os._exit(1)` removes the need for it, with less code.
- Launch with `py -3 hello.py` as the review wrote it: `py -3` also picks per-user Python installs the employee can replace, so `hello.cmd` pins the all-users interpreter.
- Application control, such as AppLocker or WDAC rules or signing the script: Group Policy on the workstations, not code in this repo.
- A scheduled hash check of the installed file: only administrators can change it, and `install.ps1` prints the hash for a manual check.
