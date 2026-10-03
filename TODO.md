# To do

Open work only. What's done is in `CHANGELOG.md`, the panel and money reviews
from October 2026 are in `docs/PANEL-2026-10.md`, and declined ideas with
their reasons are in `BACKLOG.md`.

## Needs the deploying organization

1. Sign the package with the organization's code-signing certificate:
   `toolsuild-package.ps1 -CertificateThumbprint <thumbprint> -TimestampServer <URL>`.
   CI already proves a signed package installs under AllSigned.
2. Pin the actions in the three workflows the shared kit installs
   (`auto-tag`, `devkit-quality`, `dependabot-automerge`), where the kit is
   kept.

## Next to build

From the product review of 1.23.0, in order:

1. A content file the organization supplies: up to 100 tips and thoughts in
   a file that ships inside the signed package and replaces the built-in
   lists. A build-time check enforces length, plain text and no dates or
   links, so it can't become an announcement channel.
2. A second language as a complete file, reviewed by a native speaker, chosen
   from the Windows display language, with a policy to force English.
3. A JAWS pass, to add to `docs/ACCESSIBILITY.md`.

## Later, when the problem shows up

- Find launchers through the Known Folder API, if any PCs use OneDrive Known
  Folder Move or folder redirection for the Startup folder.
- Ctrl+C stays as it is. Two presses in a row could end the visit if anyone
  asks.
