# Backlog

Changes considered and declined, with the reason. On 2 October 2026 the list from rounds 1 to 43 was swept. Everything a later round had fixed, or that could be done and tested here, was done and is in the 1.18.0 changelog entry. What is left is grouped by why it stays.

## Against the design on purpose

- Usage reporting to IT, feedback built into the program, an error log file, or network access of any kind: the program makes no network calls and keeps nothing but `notes.json`, so people can trust it. Ask the employees directly.
- Visit counts, a best streak, scores, or a lifetime visit count past 400 days: a count isn't value, and a record at work feels like being checked on.
- A sign-in reminder that is on by default, or closing the window after a period of no input: a window that appears or vanishes on its own is intrusive on a work PC.
- A longer plan history, a weekly recap, a list of several plans, or a Markdown export: the program keeps seven short finished plans on purpose.
- A switch to hide the finished list, expiring `same` after 30 days, or an opt-in done count: option 7 forgets one plan, and option 4 deletes everything.
- A timestamped `.bak`, or a cap on `.bak` copies: numbered backups keep every damaged file, and a cap would delete someone's data.
- A lock file or a schema version: `commit()` merges every save, and the delete marker covers Delete everything.
- Not counting the sign-in `--startup` window as a visit: it would change what "in a row" means.
- Skip repairing a damaged file when nobody can see the screen: the file is set aside as a backup, never deleted.
- Ctrl+C ending the whole visit: Ctrl+C skips one prompt, which is safer for someone who pressed it by accident.
- Prompts that end in `:` instead of ` > `: the Narrator pass on 1.16.0 passed with the current prompts. The simulated pilot's NVDA user said `>` is spoken as "greater". It's unclear whether NVDA does that at its default punctuation level, so a real NVDA check decides it before every prompt changes.
- Renumbering the menu or a "Mark done" menu item: renumbering breaks saved habits, and `done` at the last prompt covers it.
- Keeping direction marks in plan text: they can reorder text on screen.
- Forcing UTF-8 output: Python already writes Unicode to a Windows console whatever the code page, and forcing it would change the bytes piped output and the tests read.
- Stopping the review rounds, or freezing the program after a weak pilot (Round 44 panel): the project exists for steady improvement through review, and the rounds cost nothing. A weak pilot steers what the next rounds work on.
- Python 2, or Python before 3.6: f-strings fail closed with a `SyntaxError`.

- Reaching people on their laptop on site days (simulated pilot): installing it on the laptop is IT's call, not a program change.

## Claims that turned out wrong or already true

- Drop the OS error text from the stderr message: the errno is what someone debugging a dead stdout needs.
- Keep `_silence()` with a `try/finally`: `os._exit(1)` does the job with less code.
- Replace the hex masks in `Assert-AdminOnly`: `GENERIC_WRITE` is bit 30 and positive as an int32, and testing showed every write grant refused.
- Drop `VERSION` from the installer: it drives the auto-tag workflow.
- Accept an uppercase `-Commit`: it already works.
- Bake the file hash or commit into `install.ps1`: a commit can't hold its own hash. The installer checks both files against `-Commit`.
- Add TrustedInstaller to the installed folder's access list: nothing needs it there.
- Test `LinkType` instead of the reparse-point attribute: the attribute check fails closed.
- Add WriteAttributes to the rights masks: it doesn't change file contents.
- `exit /b %ERRORLEVEL%` in `hello.cmd`, or `|| pause` in the launcher: the exit code already passes through, and `start` doesn't wait.
- Make the Apps Uninstall button elevate: `uninstall.ps1` already restarts itself elevated.
- Restore `$ProgressPreference` after install: the script sets it in its own scope, so it never reaches the admin's window.
- Check `hello.cmd` exists before writing the launcher: a clone has none, and the installer creates it.
- Unknown keys in `notes.json`, the Dependabot check missing the tests, a looser access list on the data folder: Round 43 showed each is already handled.

## Settings and process, not code in this repo

- Branch protection, 2FA, required checks, signed tags, `CODEOWNERS`, `LICENSE`, and where the reviewed commit hash is published: GitHub settings and owner decisions, made outside this repo.
- AppLocker or WDAC rules, Authenticode signing, Intune or MSI packaging, a scoped allow rule and patch reminders for the bundled Python: Group Policy and deployment work.
- Pinning the actions and checksums in `devkit-quality.yml`, `dependabot-automerge.yml` and `auto-tag.yml`, patch-only Dependabot merges, and tagging only after the tests pass: those three come from a shared kit and are overwritten when it updates, so they change where the kit is kept, not here. This repo's own `tests.yml` is pinned.
- Pilot questions: success criteria, a content file for IT, editable or more content, weekday or time-of-day tips, languages, a rename, a desktop icon, a shorter first run, when the sign-in offer comes, "another one", and UK or US spelling. Wait for what the five pilot employees ask for, as `PLAN.md` says.

## Installer changes that need an administrator test run

These touch `install.ps1` on paths only an administrator can reach, and a mistake can leave a PC without a working install. Do them with a test install on a spare PC.

- Defer `Remove-Tree $old` and roll back when step 6 fails, and name the open windows in the rename error.
- Installer colours and `NO_COLOR`, the Start Menu folder access list, Domain Admins in the access check.
- ARM64 PowerShell, reading the architecture from `RuntimeInformation`, a Windows version check.
- More Git hardening (`GIT_CONFIG_GLOBAL=NUL`, `--no-filters`), proxy credentials, the "dubious ownership" message.
- Walking the tree without descending into junctions: only administrators can plant one, and the walk fails closed.
- Finding launchers in redirected profiles through the Known Folder API.
- A standard-user smoke run, committing the Python zip, a sigstore check, a scheduled hash check, a trimmed bundled Python.
- A one-step reinstall helper, and splitting the payload from the installer once a second tool exists.
