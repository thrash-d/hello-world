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
Windows. The reminder was already
offered on the first day, right after the first plan. Running a public
counts server for the individual package is the owner's step; the README says
how.

1. An outside review of the sync encryption, and of the push signing,
   before they're promoted widely.
2. Pro-only ideas from the memos (Discord and calendar reminders, presets for
   night shift, drive days, job hunts, shifts and rent, quarterly targets, a
   gift key card), now that Pro is in (1.59.0). Selling keys, and putting the
   public key in `hello.py`, are the owner's steps (`docs/PRO.md`).
3. A household list (Okiku): a separate list people put things on on
   purpose, anyone on it adds and ticks, personal plans never in it, no
   count of who did what, on its own opt-in encrypted sync code. With the
   family key; the hard rule against any view of someone else's plans
   stays.
4. Private letters to family (Mary): the phone's Draft text button already
    opens the phone's own messages; a letter written in hello-world, kept on
    the device and handed to the phone's own mail or messages to send, is
    the version that keeps hello-world from becoming a messaging service.
    The Profit Maximizer advised against more than that (abuse risk).
5. The household list (item 3) only with: each adult joining from their
    own device and leaving any time; a notice to everyone when someone joins
    or leaves; nobody adding another adult, setting their reminders or
    sending "I'm okay" for them (Rasputin); a new key for the group when
    anyone leaves (Torquemada); each item's own history of who added, ticked
    or removed it, visible to everyone on the list, and 30 days to restore a
    removed one (Caligula), with no totals or rankings per person; and the
    household code never on the fridge page or in a text. Built with the
    family key, after those protections, not before.
6. A list of the devices syncing with a code, without accounts: each device
    writes a name it's given ("Kitchen tablet") into the encrypted copy when
    it syncs, so the list is only readable with the code, and **Change my
    sync code** is how one is removed (Mielke). The Profit Maximizer had
    thought this needed accounts; this way doesn't.

Nothing from a review is cut (the owner, 2026-10-10): what a memo would
have dropped is built in the safe form named above.

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
