# To do

Open work only. What's done is in `CHANGELOG.md`, the panel and money reviews
from October 2026 are in `docs/PANEL-2026-10.md`, and the pilots are in
`docs/PILOT.md`, and the persona reviews and their track record in
`docs/PERSONAS-2026-10.md`. Nothing is declined: every idea from a review, a pilot or the
owner is built, and anything that touches privacy or safety is built as an
opt-in setting or policy with the safe default kept.

## Building next

The owner's plan from the October 2026 persona review and the Profit
Maximizer memo, one round each. 1.44.0 locked notes to the person's Windows
account; 1.45.0 added the shared tip count and its reference server;
1.46.0 added shift handoff notes; 1.47.0 added "I'm not sure", dated
questions, What I did, large text, no follow-up questions, the support line
and a plan-free reminder by default; 1.48.0 added reactions to the thought,
a window that doesn't wait for the server, and handoff that opens by itself,
with policies for shared logins and signed notes; 1.49.0 added the command
line, todo.txt import and the standup; 1.50.0 added the desk pet, plans put
aside and the weekly boss; 1.51.0 finished the polish list; 1.52.0 added the
tray icon and the portable zip; 1.53.0 added the phone web app; 1.54.0 added opt-in encrypted sync; 1.55.0 added the scam shield, a
day start of your own and "the day went sideways"; 1.56.0 brought the
phone a reminder that arrives, the family buttons, a daily repeat and a
fridge page; 1.57.0 brought the daily repeat and the fridge page to
Windows. 1.66.0 adds streak notes, offered to a placeholder address until an
operator points them at their own counts server, and stub receipts that do
not bill. The October panel and the personas in `docs/PERSONAS-2026-10.md`
are retired as of round 50. The sitting panel is Bex Calder, Vance Harlow,
Nico Paredes, Reed Mallory, Amina Soule, and Edith Cho. 1.67.0 adds `hello
kazoo`, `hello ai` (it says it is not a model), and a $4.99 Priority Hello
stub that does not bill. 1.68.0 is Reed Mallory's security pass: the
reminder thread survives a bad push address, a stored sync copy requires
`If-Match`, the counts files are not left to the umask, and a symlink is not
treated as the notes, the handoff file, or a sync copy. The ledger records
an upload without the plan. 1.69.0 closes the residuals he had signed:
P-256 uses libcrypto, uninstall deletes through an open handle, the phone
keeps sync keys as non-extractable browser keys, and a Windows open refuses
a reparse point. The internal review of the sync encryption is
`docs/SYNC-CRYPTO-REVIEW.md`. It is not an outside audit. 1.70.0 keeps
the household list after the phone's keys move to the browser, and the
death sentence names the run that stopped. `hello trombone` prints and
does not save. The phone may start a tone and says whether it did.
`hello encore` is a $3.99 local stub. The trombone stays free. Nothing was
removed. The reminder was already
offered on the first day, right after the first plan. Running a public
counts server for the individual package is the owner's step; the README says
how.

1. Pro-only ideas from the memos (Discord and calendar reminders, presets for
   night shift, drive days, job hunts, shifts and rent, quarterly targets, a
   gift key card), now that Pro is in (1.59.0). Selling keys, and putting the
   public key in `hello.py`, are the owner's steps (`docs/PRO.md`).
Nothing from a review is cut (the owner, 2026-10-10): what a memo would
have dropped is built in the safe form named above.

## Needs the deploying organization

1. Sign the package with the organization's code-signing certificate:
   `tools\build-package.ps1 -CertificateThumbprint <thumbprint> -TimestampServer <URL>`,
   or sign the four scripts with `tools\sign-scripts.ps1`. CI already proves a
   signed package installs under AllSigned. An unsigned copy names this
   organization, not Reed Mallory (`docs/transfers/code-signing.md`).
2. Sign the outside review of the sync encryption and of the push signing
   before they're promoted widely. The internal review is done
   (`docs/SYNC-CRYPTO-REVIEW.md`). The signature is
   `docs/transfers/sync-external-review.md`. Reed Mallory does not sign it.
3. A real pilot with employees. `docs/PILOT.md` has the simulated ones.

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
- The window a timed reminder opens with `DETACHED_PROCESS` outlives the
  scheduled task's time limit; the owner checked it with a throwaway task.
- Unknown keys in `notes.json`, the Dependabot check, and the data folder's
  access list were already handled in Round 43.
