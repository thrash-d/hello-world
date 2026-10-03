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
| A quiet sense of continuity | A days-in-a-row message at the 3rd, 7th and 14th visit, then every 30th, counting any visit within four days of the last. Off with one menu choice | Done |
| It is easy to find | Start menu entry with an icon and description, and an optional once-a-day sign-in launcher that the employee turns on and off themselves | Done |

## What was kept out on purpose

- Visit counts, "best streak" and scores. A count is not value.
- A reminder that is on by default, pop-ups, sounds or anything that opens by
  itself without the employee choosing it.
- A long history of plans or a score. What it does keep is deliberate and
  small, and the README's "What is saved, and who can see it" section is the
  one list of it. Nothing reports any of it.
- Network access of any kind, and any report of use to IT or managers.

## Trust

Saved data is one small file in the user's own folder. Option 1 in the menu
shows a short summary of what is saved (the tidied file if you type `full`), and option 4 deletes it. The README says plainly that
IT staff who can read the computer's files could read it, and tells people not
to type passwords or private details.

## Accessibility and inclusion

- Linear plain text laid out for a screen reader to read top to bottom, with
  no art, no progress bars and no redrawing. Checked with Narrator in a real
  console for 1.16.0.
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

- If employees ask for it: a second language file, a different tone, or a
  desktop icon. Each is a small change to `hello.py` or the installer.
- If a second tool is added, split the payload from the installer then, with
  both tools in hand and a Windows test run.
- Review rounds keep running on their schedule. The point of the project is
  steady improvement through review, and the rounds cost nothing.
