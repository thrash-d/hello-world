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
the sync encryption that `TODO.md` still lists.
