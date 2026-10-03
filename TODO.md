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

1. A window with buttons, and a morning notification. The 1.27.0 review
   found the console itself is the main reason a non-technical employee
   would stop opening hello-world: a black window looks like an error, and
   typed command words have to be remembered. What the simulated user asked
   for: a normal window with large text, buttons for Done / Not yet / Skip /
   Close, a box to type the plan, and a once-a-morning Windows notification,
   "Yesterday you planned: X. Done?", that answers in one click.
   - The installed Python is the python.org embeddable zip, which has no
     tkinter. Choose between shipping Tcl/Tk with a pinned hash (simplest
     code; check which official python.org artifact carries `_tkinter` and
     the Tcl/Tk DLLs for the pinned version) and Win32 dialogs through
     `ctypes` (no new files; `TaskDialogIndirect` needs a common controls
     v6 activation context).
   - The notification needs an AppUserModelID on the Start menu shortcut,
     which `install.ps1` creates, and opens only once the employee turns it
     on, as the sign-in launcher does now.
   - Keep the console screens as they are, behind `--console` and a policy,
     for screen reader and keyboard users. They are the tested,
     Narrator-checked path.
   - The plan, saved file, lock, policies and installer don't change; only
     the screen does. Split `daily()` into what to ask and how to ask it
     first, so both front ends share one flow and one test suite.
   - Needs a person at a real Windows desktop: Narrator, Magnifier at 200%,
     high contrast, and five non-technical employees for a week.
2. A real native speaker's pass over the Spanish, French, Portuguese and
   German screens. The reviews in 1.25.0 and 1.26.0, and the strings changed
   in 1.27.0, were simulated.
3. Another language, if the organization asks for one. Adding one is a
   `LANGUAGES` block at the end of `hello.py`, its command words, its Windows
   language ID, and an ADML file.

## Later, when the problem shows up

- Find launchers through the Known Folder API, if any PCs use OneDrive Known
  Folder Move or folder redirection for the Startup folder.
- Ctrl+C stays as it is. Two presses in a row could end the visit if anyone
  asks.
