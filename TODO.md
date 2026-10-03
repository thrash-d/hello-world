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

1. Check the window at a real desktop: Narrator, NVDA and JAWS reading the
   labels, buttons and plan box; Magnifier at 200 percent; a high contrast
   theme; and the sign-in notification answered from the screen and from
   notification center. The tests open and close it in every language, and it
   was drawn on Windows 11 at 100 percent in English and German, but nobody
   has used it with assistive technology yet.
2. Five non-technical employees using the window for a week. The simulated
   user who rated 1.27.0 at 2 out of 10 rated the window at 7.
3. A real native speaker's pass over the Spanish, French, Portuguese and
   German screens. The reviews in 1.25.0 and 1.26.0, and the strings added in
   1.27.0 and 1.28.0, were simulated or written without a native reviewer.

## When an organization asks

- Another language. Adding one is a `LANGUAGES` block at the end of
  `hello.py`, its command words, its Windows language ID, and an ADML file.
  The simulated user said not to add one until someone asks.

## Later, when the problem shows up

- Find launchers through the Known Folder API, if any PCs use OneDrive Known
  Folder Move or folder redirection for the Startup folder.
- Ctrl+C stays as it is. Two presses in a row could end the visit if anyone
  asks.
