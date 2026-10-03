# To do

Open work only. What's done is in `CHANGELOG.md`, the panel and money reviews
from October 2026 are in `docs/PANEL-2026-10.md`, and declined ideas with
their reasons are in `BACKLOG.md`.

## Needs the deploying organization

1. Sign the package with the organization's code-signing certificate:
   `tools\build-package.ps1 -CertificateThumbprint <thumbprint> -TimestampServer <URL>`.
   CI already proves a signed package installs under AllSigned.
2. Pin the actions in the three workflows the shared kit installs
   (`auto-tag`, `devkit-quality`, `dependabot-automerge`), where the kit is
   kept.

## Needs a person

- A real pilot with employees, when the deploying organization is ready.
  `docs/PILOT.md` has the simulated ones: three on the text screen and two
  rounds on the window. The owner's assistive technology checks and the
  native speaker review of the translations passed for 1.28.0.

## When an organization asks

- Another language. Adding one is a `LANGUAGES` block at the end of
  `hello.py`, its command words, its Windows language ID, and an ADML file.
  The simulated user said not to add one until someone asks.

## Later, when the problem shows up

- Find launchers through the Known Folder API, if any PCs use OneDrive Known
  Folder Move or folder redirection for the Startup folder.
- Ctrl+C stays as it is. Two presses in a row could end the visit if anyone
  asks.
