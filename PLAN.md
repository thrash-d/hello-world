# Plan: value, usability and retention

hello-world exists for the people who use it. This plan says what makes it
worth opening every working day, what was built for that, and what is left.
Status: "Done" is in this release.

## What brings a generic person back

Ranked from a design review of the first version, then built:

| Reason to return | What was built | Status |
|---|---|---|
| It costs nothing to open: under a second, readable in under 20 seconds | One short screen, about 14 lines, plain words, ASCII only, no colour, no waiting except for Enter | Done |
| A small, concrete benefit each day | 100 original "small things to try" (a stretch, a glass of water, closing extra tabs, thanking a colleague), chosen by date | Done |
| Something fresh and warm | 100 original short thoughts, chosen by date; they repeat every 100 days | Done |
| One thing with real personal use: a plan, then a follow-up | One optional plan a day, and more after `done`. Next day: "Did you do it?" with y, n or Enter. "Not yet" offers to keep it for today, so nothing is retyped | Done |
| Welcome, never guilt | After a gap of more than a week it says "Welcome back". No word like missed, lost or broke appears. Skipping everything is normal | Done |
| A quiet sense of continuity | A days-in-a-row message at the 3rd, 7th and 14th visit, then every 30th, counting any visit within four days of the last. Off until the employee turns it on, since 1.29.0, after simulated employees read it as being counted | Done |
| It is easy to find | Start menu entry with an icon and description, and an optional once-a-day sign-in launcher that the employee turns on and off themselves | Done |

## What was kept out on purpose

- Visit counts, "best streak" and scores. A count is not value.
- A long history of plans or a score. What it does keep is deliberate and
  small, and the README's "What is saved, and who can see it" section is the
  one list of it. Nothing reports any of it.
- Any view of a person's plans for IT, managers or a team, leaderboards, and
  mood tracking. Seven simulated users in October 2026 said each of these
  would make them uninstall and tell their team.
- Plan text leaving the PC. Network features (owner's decision, October 2026)
  send only anonymous counts, are opt-in, and say on screen what they send.

The owner dropped two earlier rules in October 2026: "no network access of
any kind" and "nothing opens by itself", so shared counts and a sign-in
reminder offered on the first day can be built.

## Trust

Saved data is one small file in the user's own folder. Option 1 in the menu
shows a short summary of what is saved (the tidied file if you type `full`), and option 4 deletes it. The README says plainly that
IT staff who can read the computer's files could read it, and tells people not
to type passwords or private details.

## Accessibility and inclusion

- The Start menu opens a window of standard Windows controls: large text,
  buttons, one box for the plan, and system colours for high contrast. The
  text screen stays for anyone who prefers it.
- The text screen is linear plain text laid out for a screen reader to read
  top to bottom, with no art, no progress bars and no redrawing. Checked with
  Narrator in a real console for 1.16.0.
- No reliance on colour, short lines, short sentences, an unambiguous date
  ("Thursday, 1 October 2026").
- Everything works with the keyboard and with Enter alone. Typed letters other
  than ASCII are kept, and a console that can't show them prints `?` instead of
  failing.
- Streak language is optional, and nothing assumes a Monday to Friday week.

## Rollout and measuring

- Rollout is in `README.md`: the installer steps, an employee page and a plain
  statement of what is saved.
- The program reports nothing, so there is no usage dashboard, by design.
  Retention is measured by asking the five employees, or by employees
  choosing option 1 to show their own dates. Neither needs anything added to
  the program.
- Rollout success: installs that finish without error, out of five, from
  `install.log` and the exit code.

## Tested

The test suite was last run on Windows 11 for 1.16.0, with Python 3.13 and
piped input. For 1.16.0 the owner also ran the release gate by hand in a
sandbox, and it passed:

- A real console with Narrator.
- One install, one reinstall, an interrupted install and an uninstall.
- Two real windows that both finish a plan while one of them uses Delete
  everything. Since 1.19.0 an automated test also runs two real processes at
  once.

For 1.19.0 the owner ran the spare-PC gate, and it passed: an install of
1.18.0, an upgrade to 1.19.0 with the commit and install date in the Apps
entry, a forced step 6 failure that put the old install back, and a smoke run
as a standard user.

On 3 October 2026 the owner reported that all pending manual tests passed
on 1.23.0, including the NVDA check of the prompts and a pilot-ring deployment.
CI now also installs, upgrades, refuses and uninstalls the package on every
push, signed and unsigned.

Run the same gate again before a release that changes saving, the installer
or the uninstaller. Not recorded as checked: console input outside ASCII, the
shortcut's `if errorlevel 1 pause` line, and removing launchers from several
user profiles.

## Pilot

A simulated 30-day pilot ran on 1.19.0, and 1.20.0 answers what it found.
`docs/PILOT.md` has the method, the findings and the changes. A pilot with
real employees can still follow, run the same way:

Five employees use it for 30 days, and at least one of them uses NVDA,
Magnifier or voice control.

- Before the clock starts, write down what counts as success. The floor is the
  kill metric below.
- On day 14 and day 30, ask each person in person, never through the program,
  how often they opened it and what annoyed them. Ask the assistive-tech user
  whether anything was read twice, out of order, or too long.
- If fewer than three of the five open it most days by day 30, the next
  review rounds work on why before anything new is added.
- What the five ask for goes to the front of the next rounds.

## Later

- If employees ask for it: another language, a different tone, or a
  desktop icon. Each is a small change to `hello.py` or the installer.
- If a second tool is added, split the payload from the installer then, with
  both tools in hand and a Windows test run.
- Review rounds keep running on their schedule. The point of the project is
  steady improvement through review, and the rounds cost nothing.

## Round 49

The room voted 3–2 to ship streak notes. Casey, Jules Navarro, and Profit
Maximizer were for them. Helen Park and Idris Khan were against them. Ruth
Okonkwo and Dave Pell were not in the room, and they did not vote. The notes
default to `https://insights.example.invalid/v1/growth`. An operator may point
that address at their own counts server. Payments for the $2.99 repair and
the $9.99 a month Pro+ flag are local stub receipts. `reviews/round-49.md`
has the dissent, including that gentle mode hides the spoken nag and still
records the events when the notes were accepted.

## Round 50

The October panel and every persona named in `docs/PERSONAS-2026-10.md` are
retired. The record stays in those files and in `reviews/`. The sitting
panel has not read those rounds. It is Bex Calder, Vance Harlow, Nico
Paredes, Reed Mallory, Amina Soule, and Edith Cho. `reviews/round-50.md`
has the vote.

What they shipped: `hello kazoo`, `hello ai` (the screen says it is not a
model and nothing is sent), and a $4.99 Priority Hello stub whose receipt
is written only after the notes save succeeds. The morning screen and the
printed page do not gain a line. The sponsored line stays. Reed Mallory
does not veto. His conditions are in the code: the growth folder is not a
symlink and is mode 0700, a bad queue does not crash the visit, the ledger
`feature-audit.jsonl` has no plan text, and a failed save does not write a
receipt. The death sentence now matches the run on the next continued day.
Vance Harlow wanted that sentence to stay until someone paid. He lost, 5–1.

## Round 51

Reed Mallory led a security assessment of the program as it stood in 1.67.0.
He does not veto. He asked for the findings in `reviews/round-51.md` to be
hardened and written down so his name is on the sign-off. The fixes are in
1.68.0.

A bad push address can no longer end the reminder thread. A sync copy that
is already stored requires `If-Match`. The counts folder, the sync folder,
and the day files are mode `0700` or `0600`, and a symlink is not followed.
The shared handoff file is not opened through a link. The notes file is not
either. The phone service worker caches only this app's own files, and not
after a redirect. The counts server sends `nosniff`, `no-referrer`, and a
content security policy on the phone page. A streak-note upload appends one
ledger line with the host and the result, and without the plan. Nothing was
removed. The morning screen and the printed page do not gain a line. The
default upload is still the placeholder. This is not the outside review of
the sync encryption. That review's internal half is round 52.

## Round 52

Reed Mallory will not accept a residual. The three cells he marked accepted
in round 51, and the residuals named on that sign-off, are fixed or moved
off his name. The record is `reviews/round-52.md`. The version is 1.69.0.

P-256 signing and verification go through libcrypto. A pure-Python ladder
stays in the file and does not run unless an operator who is not Reed
Mallory turns it on in writing. Uninstall deletes through a directory handle
opened so a junction is the node, not the target. If that code cannot be
loaded, the folder is left in place. The four install scripts can be signed
with `tools\sign-scripts.ps1` or the package build. An unsigned run names the
deploying organization. The sync scheme has an internal review in
`docs/SYNC-CRYPTO-REVIEW.md`. The outside signature is still the deploying
organization's, and Reed does not sign the word audited. Phone sync keys
move to non-extractable browser keys. Windows opens of notes, handoff, and
the counts secrets refuse a reparse point. A notes folder on Windows gets an
owner-only access list, and a volume that refuses it gets a transfer file
for the operator. Nothing was removed. The morning screen and the printed
page do not gain a line. The default upload is still the placeholder.

## Round 53

The same six. Reed Mallory still accepts no residual, and he does not veto.
The record is `reviews/round-53.md`. The version is 1.70.0.

The phone's household list survives a refresh after the keys have moved to
non-extractable browser keys. The death sentence names the run that stopped.
When the longest run is a different number, the sentence says that too.
`hello growth` in gentle mode no longer says a dead run is still going. The
morning screen still hides that line. A bad streak number in the queue does
not crash the visit. The transfer file is opened without following a
reparse point, and a name that is Reed Mallory, or that starts with his
name after spaces are folded, does not open the gate.

What they added: `hello trombone` (free, not the morning, not a recording)
and `hello encore`, a $3.99 local stub. The trombone stays free. The
morning screen and the printed page do not gain a line. The default upload
is still the placeholder. He did not sign the word audited.

## Round 54

The same six. Reed Mallory still accepts no residual, and he does not veto.
The record is `reviews/round-54.md`. The version is 1.71.0.

The visit line said "last 60 days" for a window that keeps today and the
day 60 days earlier, which is 61 calendar days. It now says 61. A
certificate subject with a doubled space in Reed Mallory's name could
still sign, and the package build did not check the subject. Both use
`tools/reed-name.ps1`. The phone no longer turns 3.9 into 3. A repair
line names the number it wrote. The Cowbell button does not put the plan
on the event it offers.

What they added: `hello airhorn` (free, not the morning, not a recording)
and `hello spotlight`, a $7.99 local stub. The airhorn stays free. The
morning screen and the printed page do not gain a line. The default upload
is still the placeholder. He did not sign the word audited.

## Round 55

The same six. Reed Mallory still accepts no residual, and he does not veto.
The record is `reviews/round-55.md`. The version is 1.72.0.

A run that stopped at 1, with a longest of 5, said it was 5. The sentence
now names 1, and names 5 only as the longest. A certificate-style name,
`CN=Reed Mallory`, still opened the variable-time gate, still kept raw
phone sync keys, and was still printed as the unsigned-script acceptor.
Those checks now use the same name-by-name rule as the signer. A joke
event stored by the counts server no longer keeps the plan. The comment
that said visits are kept 60 days now says 61 calendar days.

What they added: `hello bell` (free, not the morning, not a recording)
and `hello ring`, a $6.99 local stub. The bell stays free. The morning
screen and the printed page do not gain a line. The default upload is
still the placeholder. He did not sign the word audited.

## Round 56

The same six. Reed Mallory still accepts no residual, and he does not veto.
The record is `reviews/round-56.md`. The version is 1.73.0.

The nag said the streak dies tomorrow. A gap of 4 days still counts, and a
gap of 5 ends it. My numbers said three for that same comparison. Both
sentences now say 4 and 5. On a dead run, the phone's Keep button repeats
the death sentence. A quoted `CN="Reed Mallory"`
does not open the variable-time gate. `hello ai` reads the saved day start
and still does not write the notes.

What they added: words after `hello ai` are not read, not saved, and not
sent, and the screen says so. The duck's line is still the one for that
date. There is no fifth noise and no new stub. Vance Harlow asked for a
$14.99 Hello Audience with the duck behind it. He lost, 1 to 5. The morning
screen and the printed page do not gain a line. The default upload is
still the placeholder. He did not sign the word audited.
