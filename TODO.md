# To do

Open work only. What's done is in `CHANGELOG.md`, the panel and money reviews
from October 2026 are in `docs/PANEL-2026-10.md`, and the pilots are in
`docs/PILOT.md`. Nothing is declined: every idea from a review, a pilot or the
owner is built, and anything that touches privacy or safety is built as an
opt-in setting or policy with the safe default kept.

## Building next

The owner's plan from the October 2026 persona review and the Profit
Maximizer memo, one round each. 1.44.0 built the first: notes locked to the
person's Windows account, so a plan can be personal.

1. Shared counts: an opt-in "212 people did today's tip" and emoji reactions
   to the thought, sending only anonymous counts to a server the
   organization runs and names by policy, with a small reference server in
   the repo. Plan text never leaves the PC.
2. Shift handoff notes for shared floor PCs (Denise, Rick; the strongest paid
   demand).
3. "I don't remember" as an answer, the day a plan was written ("On Monday you
   planned..."), and a big-print dated history (Harold).
4. Gentle mode: a plan with no follow-up and no due dates from words, and a
   static support-line link set by policy, never triggered by what is typed
   (Sam).
5. The sign-in reminder offered on the first day, with plan text left out of
   it on shared PCs (Jaylen, Priyanka, Rick).
6. Fun: a desk pet that sleeps and never dies, a plan graveyard with kind
   eulogies, a company boss fight on the shared counts (Jaylen, Skye).
7. For engineers: a command-line `hello plan`/`hello done`, todo.txt import,
   and a standup summary (Priyanka).
8. Paid tiers from the memo need a billing and licensing service outside
   this repo; noted, not buildable here.
9. A due date for one thing in a plan instead of the whole plan (Priya,
   Dana, Tom, round 68 pilot).
10. The notification leaves the plan out unless the person turns it on, the
   safe default for a shared screen (Mónica).
11. Delete everything says which settings it kept, and offers to reset them
   too (Mónica).
12. Someone back after 60 or more days sees the first-run welcome, since only
   60 days of visits are kept; base it on whether there was ever a plan or
   an answer instead (round 68 review).
13. Quieter screens: a shorter first welcome and fewer Options entries (Priya,
   Dana).
14. Plainer confirmations: "Done." also names the button, and lines such as
   "Well done. Take a short break..." read as filler (Tom, Mónica).
15. Within one day, things finished together list in plan order (Tom).
16. Read "by Friday" in Chinese, Japanese and Korean, where the deadline word
   comes after the date ("金曜まで") and often without a space; numeric dates
   and weekday names already work there (round 68 translation).

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
