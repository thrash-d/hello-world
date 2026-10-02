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
| One thing with real personal use: a plan, then a follow-up | One optional plan a day. Next day: "Did you do it?" with y, n or Enter. "Not yet" offers to keep it for today, so nothing is retyped | Done |
| Welcome, never guilt | After a gap of more than a week it says "Welcome back". No word like missed, lost or broke appears. Skipping everything is normal | Done |
| A quiet sense of continuity | An "in a row" line at the 3rd, 7th and 14th visit, then every 30th, counting any visit within three days of the last. Off with one menu choice | Done |
| It is easy to find | Start menu entry with an icon and description, and an optional once-a-day sign-in launcher that the employee turns on and off themselves | Done |

## What was kept out on purpose

- Visit counts, "best streak" and scores. A count is not value.
- A reminder that is on by default, pop-ups, sounds or anything that opens by
  itself without the employee choosing it.
- A history of plans or a score. Since version 1.12 the program does save the
  plan before the current one (so `same` is one word) and a bare count of
  plans marked done. That is a deliberate change: it makes the second day
  faster, it is shown only to the person, in menu option 1 and after they
  finish a plan, and it leaves with Delete everything. It is not a record of
  which days or which plans, and nothing reports it.
- Network access of any kind, and any report of use to IT or managers.

## Trust

Saved data is one small file in the user's own folder. Option 1 in the menu
shows a short summary of what is saved (the tidied file if you type `full`), and option 4 deletes it. The README says plainly that
IT staff who can read the computer's files could read it, and tells people not
to type passwords or private details.

## Accessibility and inclusion

- Linear plain text laid out for a screen reader to read top to bottom, with
  no art, no progress bars and no redrawing. Designed for, not yet verified
  with a real screen reader.
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

## Not tested

The tests were run on Windows for 1.7.1 only (see the changelog); 1.8.0 and later were tested on Linux, and the real
all-users install has not. The first install should be one install, one
reinstall, an interrupted install and an uninstall on a clean PC. Check the
shortcut icon, the window title, that Enter closes the window, that the
sign-in launcher opens once, and that uninstall removes the launcher.

## Later

- If employees ask for it: a second language file, a different tone, or a
  desktop icon. Each is a small change to `hello.py` or the installer.
- If a second tool is added, split the payload from the installer then, with
  both tools in hand and a Windows test run.
- The installer's review rounds can pause until the code changes again. The
  schedule that runs them is outside this repo.
