# Why hello-world became a daily actions program

This is the decision record for turning a program that printed "Hello, world!"
into one that gives a person one useful thing each day. It covers what we
found, what we decided, why, and what we chose not to do. Version 1.7.0 is the
release that made the change.

## 1. Where it started

hello-world was a one-line program plus a hardened Windows installer. About 25
review rounds went into the installer: a pinned commit, a pinned and
hash-checked Python, folders only administrators can change, a tested swap
with rollback, and a clean uninstall. The payload did nothing but greet.

## 2. What the analysis found

Two read-throughs of version 1.5.x led to the change.

**Usability read-through.** The installer was hard to follow: no README, long
paste-in steps with placeholders that break when pasted, long silent waits,
raw error blocks, a cluttered success line, and a thin Settings > Apps entry.
For employees the shortcut looked like a system tool and the window said
nothing.

**Business value read-through.** The finding that mattered most:

- The value was in the deployment machinery, not the program. For employees it
  was close to zero. They got a window that said hello, and nobody has a reason
  to open that twice.
- Retention cannot be fixed by tuning a greeting. It needs a recurring job the
  person actually wants done, and output that changes.
- Anything artificial would backfire on work PCs: nudges, pop-ups, streak
  pressure, or opening by itself. Employees and security teams treat those as
  unwanted software, and it would erode the trust the hardened installer was
  built to earn.

## 3. The decision

The program is for the people who use it. It is not a test of the deployment.
So it should earn a place in a normal working day by being useful in under
twenty seconds, for the most generic possible person: any age, any role, no
technical skill.

The honest levers for retention are:

1. It costs nothing to open: instant, short, plain words.
2. A small concrete benefit each day.
3. Something fresh each day.
4. One thing with real personal use: a plan, then a follow-up.
5. A welcome, never guilt.
6. Easy to find again.

## 4. What was built, and why each piece is there

| Feature | Reason |
|---|---|
| One short screen: greeting, date, a thought, a small thing to try | Fast to read, and the daily change gives a reason to open it again. |
| 100 original thoughts and 100 small actions, chosen by date | Everyone sees the same line on the same day; the lists repeat every 100 days. Actions are safe, take under five minutes, and don't assume a desk, a car or a level of ability. |
| An optional daily plan with a next-day follow-up | The only feature with real personal use. Only a clear yes or no changes the plan, and "not yet" offers to keep it for today so nothing is retyped. |
| "Welcome back" after a gap; no word like missed, lost or broke | Returning feels good. Skipping everything is normal. |
| An in-a-row line at the 3rd, 7th and 14th visit, then every 30th | Quiet continuity without a number that climbs daily. A visit within three days of the last keeps it going, so weekends and days off don't matter. One menu choice turns it off. |
| A menu on `m`: see saved data, sign-in launcher on or off, in-a-row line, delete everything | People who never type commands can still reach every option. |
| An opt-in sign-in launcher in the user's own Startup folder | Helps people who want it, with no administrator rights, and is never on by default. |
| First-run welcome with a plain statement of what is saved | Honest from the first screen. |

## 5. What we left out on purpose

- Visit counts, "best streak" and scores. A count is not value.
- A reminder that is on by default, and anything that opens by itself without
  the person choosing it.
- Any record of whether plans were done. At work that feels like being
  checked on, so only the dates opened and the current plan are saved.
- Any network access, usage reporting to IT or managers, and in-program
  surveys. Trust matters more than a dashboard. Ask the employees directly.
- Translations and tone settings. Add a language file when someone asks.

## 6. Privacy and trust

- One small file, `notes.json`, in the user's own folder under `AppData\Local`.
  No name, no computer name, no times.
- Menu option 1 shows what is saved, tidied; it is not the raw file. Option 4 deletes it.
- The README says plainly that other people who can read the computer's files,
  such as IT staff, could read it, and to avoid passwords and private details.
- Uninstalling removes each user's sign-in launcher but leaves their notes.

## 7. How it was designed and checked

Independent reviewers were used so the author wasn't the only judge:

- A behavioural design review critiqued the first design. It ranked what brings
  people back, flagged the manipulative parts, and wrote sample screens. Result:
  lead with value, quiet the counters, cut vanity numbers, make the privacy
  statement honest.
- Two writers produced the 200 pieces of content under strict rules: plain
  ASCII, original wording, no quotes or attributions, no medical or religious
  content, nothing that assumes a job or ability.
- A tester ran the program as three kinds of user for ten simulated days each:
  someone who always presses Enter, someone who writes a plan daily and
  sometimes does it, and someone who skips days and returns. It also attacked
  the notes file with hostile input.

The tester's findings were fixed and each has a test. The ones that mattered:

- Terminal escape codes planted in the notes file reached the screen.
- Pressing Enter at "Did you do it?" silently deleted the plan.
- Pasted tabs and non-breaking spaces were dropped from plan text.
- A run with no terminal used up the day's questions.
- A damaged notes file was overwritten with no copy, and an unreadable one
  could be overwritten.
- A climbing in-a-row number read as pressure, so it moved to milestones only.

## 8. Limits and what is untested

- The tests were run on Windows for 1.7.1 only; later releases were tested on
  Linux, and the real install has not been run. Untested there: console Unicode input, the
  sign-in launcher, the shortcut's `if errorlevel 1 pause` line, removing
  launchers across profiles, the icon and the window title.
- No program can guarantee retention. These are the honest levers. Whether
  people come back is measured by asking them, since the program reports
  nothing by design.
- The installer's review rounds have diminishing returns until the code changes.

## 9. Related files

- `README.md`: the employee page, what is saved, and the install steps.
- `PLAN.md`: the findings, their status, and the rollout plan.
- `CHANGELOG.md`: what changed in each release and why.
- `BACKLOG.md`: changes considered and declined, with reasons.
- `reviews/`: the saved review of each installer round.
