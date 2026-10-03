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

## Next to build

The three items from the product review of 1.23.0 shipped in 1.25.0.

1. A real native speaker's pass over the Spanish, French, Portuguese and
   German screens. The reviews in 1.25.0 and 1.26.0 were simulated.
2. Another language, if the organization asks for one. Adding one is a
   `LANGUAGES` block at the end of `hello.py`, its command words, its Windows
   language ID, and an ADML file.

## Later, when the problem shows up

- Find launchers through the Known Folder API, if any PCs use OneDrive Known
  Folder Move or folder redirection for the Startup folder.
- Ctrl+C stays as it is. Two presses in a row could end the visit if anyone
  asks.
