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
- Translations in their own files next to `hello.py`.

For IT:

- Finding a pre-1.23 launcher in a redirected Startup folder through the Known
  Folder API.

Repository:
- A `LICENSE` and `CODEOWNERS`.
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
