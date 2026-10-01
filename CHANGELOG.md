# Changelog

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

