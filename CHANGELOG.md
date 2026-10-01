# Changelog

## 2026-10-01: Make hello-world a daily-use program

Version 1.7.0. Answers the business value read-through: "this program is for the user. this program must reinforce user retention." A behavioural design review (read-only) shaped it: lead with real value, keep counters quiet, be honest about privacy, and never shame.

Changes:
- `hello.py` is now a daily moment: greeting and date, a thought and a small thing to try (100 of each, original, chosen by date), an optional plan for the day, and a follow-up the next day with a keep-for-today choice. First-run welcome, welcome back after a gap, and an in-a-row line from the third visit that can be turned off. A menu (type `m`) shows saved data, turns the sign-in launcher on or off, toggles the in-a-row line, and deletes everything. Options: `--plain`, `--stats`, `--reset`, `--remind on|off`, `--streak on|off`, `--startup`, `--help`.
- Saved data is one small file in the user's folder (visit dates, current plan, one setting). A missing, damaged or unwritable file never stops the greeting. No network use.
- The Quiet-mode and polish items from the earlier usability pass still apply. In `install.ps1`, `hello.cmd` passes its options on, the installer's test run uses `--plain` so it leaves no notes in the admin's profile, and the shortcut no longer pauses unless `hello.cmd` fails, because `hello.py` waits for Enter itself. The shortcut description says what the program does.
- "Double-clicking hello.cmd directly closes the window instantly": no longer true, since `hello.py` waits for Enter. Removed from the backlog.
- `uninstall.ps1` removes each profile's sign-in launcher, which would otherwise show an error at every sign-in, and says the users' own notes stay.
- `test_hello.py` grew from 5 to 34 tests: first run, same-day reopen, follow-up, carry-over, in-a-row line, long gap, damaged and unwritable files, non-English text, stats, reset, menu, launcher, silent startup, unknown option, and the dead-stdout cases.
- `README.md` and `PLAN.md` describe the program for employees and what is saved. `docs/WHY-DAILY-ACTIONS.md` records the reasoning for turning a greeting into a daily program.
- A tester agent ran the program as three kinds of user for ten simulated days each and tried hostile notes files. Fixed from its report: terminal escape codes in a planted notes file reached the screen ("clean" now runs on loaded text); deeply nested JSON crashed it; pressing Enter at "Did you do it?" silently deleted the plan (now only a clear yes or no changes it, and "yep", "ya", "done" count as yes); tabs and non-breaking spaces from pasted text were deleted instead of becoming spaces; a run with no terminal used up the day's questions (it now shows the screen and records nothing); long plans ran past 72 columns; a damaged file was overwritten without a copy (kept as `notes.json.bak`) and an unreadable one could be overwritten (it isn't saved over); a bad plan date turned the in-a-row line back on; odd date spellings were not normalised; the help text had an exclamation mark; `/?`, `-?` and upper-case options gave exit 2; a plan dated in the future was never shown. The in-a-row line now shows only at the 3rd, 7th and 14th visit, then every 30th, because the tester found a daily climbing number read as pressure.

Not tested: `pwsh` is not installed here, and nothing ran on Windows. Untested there: the console's handling of Unicode input, the sign-in launcher (`start` with a quoted path), the `if errorlevel 1 pause` shortcut line, the removal of launchers across profiles, and the icon and title. `python test_hello.py` passes and `ruff check` is clean.

## 2026-10-01: Usability pass on the installer, uninstaller and docs

Version 1.6.0. Answers a usability read-through and a business value read-through of the program, both done by hand. There is no review file for this change.

Changes:
- "There is no README": added `README.md` with the audience split, the install steps, update and failure notes.
- "Placeholders break if pasted": the install steps in `README.md` and in the installer help use `$tag` and `$commit` variables.
- "Permission checks are silent for minutes", "numbered steps": `install.ps1` prints `[1/6]` to `[6/6]` and shows a progress bar during the permission walks.
- "Failures print a raw error block": a `trap` and the final `catch` print one `FAILED:` line and exit 1. The full text is in `install.log`.
- "Success line is cluttered and out of date": the result says the version and whether it was a new install, a reinstall or an upgrade, then a next step. The stale LF/CRLF note is gone.
- "No unattended mode": added `-Quiet` to `install.ps1`. It prints only warnings, errors and the result.
- "Colors are inconsistent": green for success and red for failure in both scripts.
- "The Settings > Apps entry is thin": added Publisher, DisplayIcon and EstimatedSize.
- "Shortcut has no icon or description", "no title": the shortcut has the Python icon, a description and a window title. The docs say "hello-world".
- "Errors read like developer output": `hello.py`'s message ends with "(contact IT if this keeps happening)". The tests still pass.
- "Failure message gives no next step": `uninstall.ps1` says to close windows and retry, then ask IT. The admin-rights failure says to ask IT.
- Added `PLAN.md` with the value, retention and rollout plan.

Declined, added to the backlog: pausing `hello.cmd`, a one-step reinstall helper, and splitting the payload from the installer.

Not tested: `pwsh` is not installed here, so neither script was parsed. None of it ran on Windows. Untested: the `trap`, `exit 1` inside the catch, `-Quiet`, `Write-Progress`, the Python icon on the shortcut and in Apps, the shortcut's `title` command line, the `EstimatedSize` value, and the upgrade message. `python test_hello.py` passes.

## 2026-10-01: Round 25: ASCII-only strings, line endings pinned for the file check

Version 1.5.13. Answers the twenty-fifth review (`reviews/round-25.md`).

Changes:
- H1, "Em dashes in two double-quoted strings can break parsing on Windows PowerShell 5.1": replaced the three em dashes in `install.ps1` with `-`. The file has no BOM, and 5.1 reads it as Windows-1252, where the last byte of an em dash is a curly closing quote. `install.ps1` and `uninstall.ps1` now hold only ASCII.
- H2, "`GIT_CONFIG_NOSYSTEM=1` plus `git hash-object` will probably make the file check fail": confirmed on Linux. A clone made with `core.autocrlf=true` has CRLF in `hello.py` and `VERSION`, and `hash-object` with that setting skipped gives a different hash than `HEAD:file`. `.gitattributes` already pinned CRLF for `.ps1`, so those matched. Added `*.py text eol=lf` and `VERSION text eol=lf`. A test clone with `core.autocrlf=true` now matches on all four checked files. This replaces the round 10 backlog assumption that the check matches on either setting.
- M2, "The ProgramData Git check ... does not say how to fix it": the error now includes an `icacls` command that restricts the folder to administrators and gives Users read and run.
- M3, "The environment-clearing comment overstates what it does": corrected the comment. Setting `GIT_CONFIG_GLOBAL` is declined, see backlog.
- M4, "`Test-Path .git` also passes when `.git` is a file": `.git` must now be a folder.
- L3, "`cmd.exe /c` is used without `/d`": added `/d` in `Remove-Tree` and the shortcut.

Declined, added to the backlog: H3, M1, the rest of M4, L1, L2, L4 to L8.

Not tested: `pwsh` is not installed here, so `install.ps1` was not parsed. None of it ran on Windows, so the ACL checks, the `-PathType Container` test, the `/d` flag in the shortcut, and the new error text are untested. The `.gitattributes` change was checked only with Linux git. `python test_hello.py` passes.

## 2026-10-01: Add section headers and clarify installation flow

Version 1.5.12. Improved code organization and navigation.

Changes:
- Added clear section headers marking major phases of installation:
  - RECOVERY: Handle interrupted installations
  - VERIFICATION: Validate the setup environment
  - COMMIT VERIFICATION: Ensure correct commit
  - DOWNLOAD AND BUILD: Fetch Python and build
  - FINALIZATION: Register installation
- Headers make it easier to navigate the script and understand the sequence of checks and operations.

Not tested: install.ps1 not run on Windows. `python test_hello.py` passes.

## 2026-10-01: Improve permission check comments and add diagnostic output

Version 1.5.11. Better observability and code clarity for permission verification.

Changes:
- Enhanced comments in `Assert-AdminOnly` explaining ACL logic and the purpose of each check (owner, Allow ACEs, InheritOnly propagation flags).
- Better comments in parent folder checks explaining why they're needed and what happens at drive root.
- Add diagnostic output: `Assert-AdminOnlyTree` now reports how many items were checked and confirms all parents are admin-only.
- Clearer error message guidance ("Restrict write access to administrators only").

These improvements help administrators understand permission check output during installation and aid debugging if issues arise.

Not tested: install.ps1 not run on Windows. `python test_hello.py` passes.

## 2026-10-01: Harden Git environment and improve error messages

Version 1.5.10. Additional security and usability improvements.

Changes:
- Set `GIT_CONFIG_NOSYSTEM=1` to prevent Git from reading system-wide config files, ensuring full isolation from admin environment. Partial fulfillment of tenth review suggestions.
- Improved error messages throughout to guide admins when things go wrong:
  - File modification detection now advises to re-clone from the reviewed tag
  - Link/junction detection explains the security risk they pose
  - Permission and Git configuration errors provide more actionable guidance
- Permission checks now report more timing detail ("several minutes" on Git for Windows, not just "a minute")
- More explanatory comments in code for complex checks

Not tested: install.ps1 not run on Windows. `python test_hello.py` passes on Linux.

## 2026-10-01: Resolve backlog improvements: SID names, admin trust, environment isolation

Version 1.5.9. Code improvements addressing multiple backlog items. No new review findings.

Changes:
- Error messages now show friendly account names ("Administrators", "SYSTEM") instead of cryptic SIDs (S-1-5-32-544, etc.), via new `SID-ToName` function. Addresses backlog item from nineteenth review L5.
- Explicitly clear `HOME` and `XDG_CONFIG_HOME` environment variables before calling Git, improving isolation guarantee. Addresses backlog item from nineteenth review L6.
- Trust all members of the local Administrators group, not just the account running the installer. Allows any admin to run the installer even if a different admin installed Git. Addresses backlog item from line 14 of BACKLOG.md.
- Better error messages for Git for Windows installation issues, with actionable guidance on reinstalling for all users.
- Improved `.NOTES` help text to clarify permission check timing and document the ProgramData\Git folder. Addresses backlog item from nineteenth review L5.

Removed from BACKLOG.md (now addressed):
- Show account names instead of SIDs (nineteenth review L5)
- Clear HOME and XDG_CONFIG_HOME (nineteenth review L6)
- Trust every local administrator's SID (line 14)
- ProgramData\Git documentation in help (nineteenth review L5)

Not tested: install.ps1 was not run or parsed on Windows. `python test_hello.py` passes on Linux.

## 2026-10-01: Say "several minutes" where the operator sees it, and set the reinstall commands on their own lines

The twenty-fourth review, of 1.5.7, answered here. Version 1.5.8. It found no Critical, High or Medium issues, 3 Low; saved in `reviews/round-24.md`. Only a console message and help text changed.

- The permission-check message now says it can take several minutes on Git for Windows.
- The reinstall help puts `cd \` and `Remove-Item -Recurse -Force $d` on their own lines.

Declined (in BACKLOG.md):
- L3: `Get-Help` check and `uninstall.ps1` review are process items listed in earlier rounds.
- Info: pinned Python URL and hash fail closed; the pilot install is already listed.

Tested: `python test_hello.py` passes on Linux. Not tested: `install.ps1` (pwsh not installed here).

