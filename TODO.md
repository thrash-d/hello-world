# To do

Open work only. What's done is in `CHANGELOG.md`, the panel and money reviews
from October 2026 are in `docs/PANEL-2026-10.md`, and the pilots are in
`docs/PILOT.md`. Nothing is declined: every idea from a review, a pilot or the
owner is built, and anything that touches privacy or safety is built as an
opt-in setting or policy with the safe default kept.

## Building next

Employees:
- Built-in tips for shift and floor work, as a second list people can choose.
- A longer history of finished plans, a weekly recap, and a Markdown export.
- A switch to hide the finished list, `same` that expires after 30 days, and
  the done count as an opt-in.
- Visit counts, a best run of days, and a total, as opt-in "my numbers".
- Closing the text screen after `done` and the next plan, as an option.
- Window messages announced to screen readers as they change (UI Automation
  live region).
- `same` that knows which parts of an earlier plan were finished.
- Prompts ending in `:` instead of ` > `, as a setting.
- A "Mark done" item in the text menu.
- Left-to-right and right-to-left marks kept in plan text, with the override
  characters still removed.
- `--utf8` to force UTF-8 output.
- `--plain` and `--check-content` in the person's language, behind an option.
- `retomar` as a second Spanish word for `same`.
- Organization content per language: `content.es.json` and the rest.
- Regional variants: Canadian French, European Portuguese.
- Chinese, Japanese, Korean, Arabic and Hebrew in the window, which draws
  them, with the text screen staying in English for those.
- Translations in their own files next to `hello.py`.
- Rewriting a 1.23.0 to 1.27.0 sign-in value to the current one.

For IT:
- Usage reporting, as an opt-in policy: a count of visits per day written to
  the Application event log, with no plan text, and nothing sent over a
  network.
- An error log, as an opt-in policy.
- Feedback from the window, as a mail to an address the organization sets.
- A schema version in `notes.json`.
- Timestamped backups of a damaged file, and a cap set by policy.
- Removing the program for one person without an administrator: hiding it
  from their Start menu and turning everything off.
- `uninstall.ps1 -RemoveNotes`, deleting each profile's notes only through
  paths with no links, and removing each user's reminder keys.
- Counting the sign-in `--startup` run as a visit, as an option.
- Skipping the repair of a damaged file when nobody can see the screen, as an
  option.
- Reaching people on laptops: a per-user install for PCs where IT allows it.

Installer, tested as administrator in CI:
- Defer removing the old copy and roll back when step 6 fails, and name the
  open windows in the rename error.
- Installer colours and `NO_COLOR`, the Start menu folder access list, Domain
  Admins in the access check.
- ARM64 PowerShell, the architecture from `RuntimeInformation`, a Windows
  version check.
- More Git hardening (`GIT_CONFIG_GLOBAL=NUL`, `--no-filters`), proxy
  credentials, and the "dubious ownership" message.
- Walking the tree without descending into junctions.
- Finding launchers in redirected profiles through the Known Folder API.
- A standard-user smoke run, a sigstore check, a scheduled hash check, and a
  trimmed bundled Python.
- A one-step reinstall helper.

Repository:
- A `LICENSE`, `CODEOWNERS`, and the reviewed commit hash in each release.
- Pinning the shared kit's workflows where the kit is kept, and tagging only
  after the tests pass.

## Needs the deploying organization

1. Sign the package with the organization's code-signing certificate:
   `tools\build-package.ps1 -CertificateThumbprint <thumbprint> -TimestampServer <URL>`.
   CI already proves a signed package installs under AllSigned.
2. A real pilot with employees. `docs/PILOT.md` has the simulated ones.

## Checked and already fine

Review findings that turned out wrong or already handled, kept so they aren't
re-checked:
- The OS error text in the stderr message is what someone debugging a dead
  stdout needs.
- `GENERIC_WRITE` in `Assert-AdminOnly` is bit 30 and positive as an int32,
  and testing showed every write grant refused.
- `VERSION` drives the auto-tag workflow, so the installer keeps it.
- An uppercase `-Commit` already works.
- The exit code already passes through `hello.cmd`.
- `uninstall.ps1` already restarts itself elevated.
- `$ProgressPreference` is set in the script's own scope.
- Unknown keys in `notes.json`, the Dependabot check, and the data folder's
  access list were already handled in Round 43.
