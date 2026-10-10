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
day start of your own and "the day went sideways". The reminder was already
offered on the first day, right after the first plan. Running a public
counts server for the individual package is the owner's step; the README says
how.

1. Pro, $5 once with an offline key and no account. Built and waiting for
   the owner's go-ahead to commit; selling it is the owner's step.
2. An outside review of the sync encryption before it's promoted widely.
3. Round 84, the phone: a free reminder that reaches it (web push with no
   content, through the counts server, which keeps only a random token, the
   push address and a UTC time, and deletes them when it's turned off), the
   scam shield and Change code, day start, plans put aside by number, "Draft
   a text to family" and "Call family" buttons that only open the phone's own
   screens, a daily repeat that is a reminder and not a medical device, a
   big-print fridge page that says anyone in the room can read it, and a file
   export.
4. Round 85, Windows: the daily repeat and the fridge page.
5. Pro-only ideas from the memos (Discord and calendar reminders, presets for
   night shift, drive days, job hunts, shifts and rent, quarterly targets, a
   gift key card) wait for Pro itself (item 1). A family key waits for a
   decision on children's privacy law.

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
- The window a timed reminder opens with `DETACHED_PROCESS` outlives the
  scheduled task's time limit; the owner checked it with a throwaway task.
- Unknown keys in `notes.json`, the Dependabot check, and the data folder's
  access list were already handled in Round 43.
