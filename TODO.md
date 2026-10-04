# To do

Open work only. What's done is in `CHANGELOG.md`, the panel and money reviews
from October 2026 are in `docs/PANEL-2026-10.md`, and the pilots are in
`docs/PILOT.md`. Nothing is declined: every idea from a review, a pilot or the
owner is built, and anything that touches privacy or safety is built as an
opt-in setting or policy with the safe default kept.

## Building next

1. Rewrite the tips that read like office posters, such as "roll your
   shoulders" and "share a harmless joke", into concrete actions (Tom, round
   63 pilot). The new text goes to all ten translations.
2. Give the text menu the settings the window has: the reminder times, Not on
   weekends, Greet me by name, My numbers, Keep a longer history and Save my
   plans to a file (Tom). The window now says "Open the text menu" instead of
   "More options", so it doesn't promise them.
3. Use one wording for "Enter goes back" in the text menu's prompts (Tom).
4. Check that the window started by a timed reminder, with
   `DETACHED_PROCESS`, survives the scheduled task's five-minute end (round
   63 review).
5. Check an Arabic or Hebrew window on a real screen. The pilot tool's
   screenshot showed the title mirrored, which is most likely how
   `PrintWindow` copies a right-to-left window (Tom).

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
