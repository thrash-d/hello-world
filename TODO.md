# To do

Open work only. What's done is in `CHANGELOG.md`, the panel and money reviews
from October 2026 are in `docs/PANEL-2026-10.md`, and the pilots are in
`docs/PILOT.md`. Nothing is declined: every idea from a review, a pilot or the
owner is built, and anything that touches privacy or safety is built as an
opt-in setting or policy with the safe default kept.

## Building next

Employees:
- Built-in tips for shift and floor work, as a second list people can choose.
- Organization content per language: `content.es.json` and the rest.
- Regional variants: Canadian French, European Portuguese.
- Chinese, Japanese, Korean, Arabic and Hebrew in the window, which draws
  them, with the text screen staying in English for those.
- Translations in their own files next to `hello.py`.

For IT:
- Removing the program for one person without an administrator: hiding it
  from their Start menu and turning everything off.
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
