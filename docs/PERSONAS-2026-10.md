# Simulated personas, October 2026

How simulated users were used to decide what to build, what they said, what
was checked, and what came of it. The prompts and the brief they read are in
`docs/personas/`, so the same review can be run again on a later version.

Everything a persona said is a simulation by an AI agent, not a real person.
It is treated as a source of leads, never as evidence about real employees.
`docs/PILOT.md` has the earlier simulated pilots, which ran the real program
day by day; these personas read a transcript instead.

## Method

1. **Capture the real program.** The screens in the brief came from running
   the real `hello.py` through the test harness on fixed dates with typed
   input, so nothing the personas reacted to was made up. For 1.43.0 that was
   two days: a plan of two things with a weekday in it, then the next day's
   follow-up with one of them done.
2. **Write one brief.** `docs/personas/brief-1.43.md`: what the product does
   in plain words, who deploys it, what is saved, and the transcript. The same
   brief went to every persona.
3. **Spawn one fresh agent per persona.** No project memory, no repository,
   one file to read and no other tools, so no persona could see the code,
   the changelog or the other personas.
4. **Vary the people on purpose.** Competence, energy, trust, age, attention
   and mood, from a cynical staff engineer to a 79-year-old with memory slips
   and an employee in a depressive low. Characters that could become
   caricatures were told to be portrayed with respect.
5. **Ask the same questions.** Two weeks of use, what would keep them, what
   they would pay personally and per seat, ideas from sensible to absurd and
   which one they'd pay for, one sentence to the developer, and three
   out-of-character insights.
6. **Run them in parallel**, then read every answer in full.
7. **Check every claim against the code** before acting on it (below). A
   persona can misread a transcript; the program decides.
8. **Ask an adversarial advisor.** A Profit Maximizer agent got the summary
   and the owner's goals and was told to maximize paying users.
9. **Review each design before building it.** From round 72 on, the plan
   for a round goes back to the personas who asked for it, the same agents
   with their earlier answers in memory, in under 300 words. Where they
   disagree, the round says which way it went and why, and queues the other.
10. **Filter, then plan rounds.** Ideas went into numbered rounds in
   `TODO.md`. Each round is one pull request with tests and a changelog entry
   that names the persona it came from. Things that would make the personas
   uninstall, by their own account, were kept out; things that need hardware
   or services this repository can't reach were noted, not built.

## What was checked against the code

| Persona claim | Checked | Result |
|---|---|---|
| Missing a weekend breaks the days-in-a-row count (Sam) | `in_a_row()` counts any visit within 4 days of the last | Wrong. And the message is off by default since 1.29.0 |
| Three mornings a week never counts as "in a row" (Harold) | Same function; Mon, Wed, Fri are each within 4 days | Wrong |
| A shared PC shows other people's plans (Denise, Rick) | Notes live under each Windows login's `LOCALAPPDATA` | Only true where staff share one Windows login, which is common on hospital carts and warehouse terminals. Kept as a real issue for that case |
| Formulas typed into a plan run in the spreadsheet export (Skye) | Saved `=HYPERLINK(...)`, `+1+1`, `@SUM(A1)` as a plan and exported | **True.** The `.csv` holds them as live formulas. Fixed in 1.46.1 |
| `31/02` or several dates in one plan (Skye) | `typed_due()` | `31/02` is ignored; several dates take the earliest without saying so. Noted |
| `;;;;` makes empty things (Skye) | Typed it | Refused: "A plan needs a word or two" |

## Results, version 1.43.0

| Persona | Two weeks | Pay personally | Employer per seat | Would pay for |
|---|---|---|---|---|
| Priyanka, cynical engineer | ~8 opens, faded week 2 | $0 ($5 one-time for a CLI) | $0.50–1 a year | Standup from done items, commits and tickets, $3–5/month |
| Denise, nurse manager | Quit day 6 | $0 | $0 now; $1–2/month with team features | Shift handoff notes; a recognition jar |
| Jaylen, ADHD marketer | 7 opens, cliff at day 4 | $0 (maybe $2) | $1–4/month as a culture tool | Desk pet and plan graveyard, $5 one-time |
| Harold, 79 | Stopped planning in week 2 | $0 | $1–2/month | Big-print "what did I do yesterday", $3/month |
| Rick, wary supervisor | Every other day, then twice | $0 ($5 phone version) | $1–3 a year | Shift handoff notes, $3–5/month |
| Skye, intern | Daily one week, then the notification only | $0 ($2 tip) | $0.50–1 | Desk pet; a company boss fight |
| Sam, low period | ~4 opens in week 2 | $0 ($3 for gentle mode) | $1–3 a year | Gentle mode with no follow-up |

All seven would pay nothing for 1.43.0 themselves. Patterns:

- The sign-in notification with Done and Not yet was the only part four of
  seven kept using after week one; it was off by default and hard to find.
- Everyone seeing the same tip was the strongest idea, with nothing built on
  it ("Wordle without the grid share").
- The honest "not secret" line built trust and made every plan shallow.
- The 12-entry menu put five of seven off.
- Tips assume spare social energy that tired or night-shift people don't have.
- People with a list elsewhere (todo.txt, Jira, a steno pad, a vest pocket)
  won't type it twice.

Hard noes, in their words: a manager or team view of anyone's plans,
leaderboards, mood tracking on a work PC, streak-loss guilt, more than one
ping a day, fake cheerfulness.

## The Profit Maximizer

It put the money in employers, per seat, with a small personal tier: Team $2
per seat a month, Frontline $3 per shared device a month, Personal Pro $4
one-time, a developer add-on $3 per seat a month. Its top features: shift
handoff notes, the notification on by default, company tips with anonymous
counts, the standup, a boss fight, a recognition jar, the desk pet and
graveyard, a big-print history. It kept almost every hard no: "one angry
engineer kills a 2,000-seat renewal." One suggestion was left out on purpose:
making the boss-fight dragon "escape" when a trial ends so employees pressure
IT, which is the guilt the personas said drives them away.

The owner then asked to reach individuals outside companies too.

## Street research, 1.51.0

Five fresh agents on a smaller model, each a person met on a New York street
(a halal cart vendor, a junior bank analyst, a retired teacher, a delivery
rider, an indie game developer with ADHD), heard a one-paragraph pitch and
answered: first reaction, would they use it, what they'd pay, what would make
them use it. Three of five couldn't use it at all: two have only a phone, and
one has a locked-down work PC. All five singled out the daily "Did you do
it?". Four would pay $0 to $5 once; one would pay $5 a month only for study
help. The Profit Maximizer then ranked: a way to pay ($5 once, offline key),
a phone app, and a tray icon with a portable build, and said to freeze new
Windows-only features until those ship.

The designs went back to them before building:
- The game developer: the tray dot alone gets ignored by 11am, so one nudge
  at a chosen time; keep pets free and charge for history and reminders, not
  cosmetics.
- The analyst: a bundled interpreter or a USB stick on a bank PC means a
  compliance meeting; and say clearly where phone notes live.
- The teacher: a key pasted once with no sign-in is fair; nagging after "Not
  yet" would make her delete it.
- The rider: no default reminders, his phone already buzzes all day; no PC
  sync for him.
- The cart vendor: giant buttons, works with no signal, a reminder at 6:15,
  and Arabic for his cousin.

## Track record

What each simulated review found, and what happened to it. Status is as of
the pull request named.

| Review | Finding | Source | Outcome |
|---|---|---|---|
| Round 52, one persona on 1.26.0 | A menu number typed at the plan question became the plan | Own test run while preparing the persona | Fixed in 1.27.0 (#52) |
| Round 52 | `s`, `o`, `j` finished plans in English | Own test run | Fixed in 1.27.0 (#52) |
| Round 52 | "ok" refused; "prompt" and `q` not understood; the privacy line read as monitoring | Persona, 64, never used a console | Fixed in 1.27.0 (#52) |
| Round 52 | The console itself is the barrier; wants buttons and a morning notification | Same persona | Built by the owner's later rounds (the window in 1.28.0, the notification after) |
| Review of 1.43.0 | A date already past made a new plan overdue at once; fractions became due dates | Own test run | Fixed in 1.43.1 (#69) |
| Personas, 1.43.0 | Self-censoring because IT could read the notes | All seven | Notes locked to the Windows account, 1.44.0 (#70) |
| Personas, 1.43.0 | Nothing built on the shared tip | Skye, Jaylen | Shared tip count and reference server, 1.45.0 (#71) |
| Design review, round 75 | Reactions love, ha, dead, eyeroll, not a thumbs-up; counts hidden until you react; yesterday's top reaction; say how one-a-PC is counted without an ID | Skye | Built in 1.48.0 |
| Personas, 1.43.0 | Plan text shown on a shared screen | Denise, Rick | Queued: plan-free notification on shared PCs (`TODO.md`) |
| Personas, 1.43.0 | Shift handoff notes | Denise, Rick, Profit Maximizer | Built in 1.46.0 (#72) after a design review with both |
| Design review of handoff | Ages not times; hours set per site; keep until cleared; not a safety record; a unit-wide folder | Denise, Rick | Built in 1.46.0 |
| Design review of handoff | Signed by default (Denise) vs. never automatic (Rick) | Disagreement | Unsigned with a hint; a signing policy queued |
| Design review of handoff | Open by itself at sign-in on handoff PCs | Rick | Built in 1.48.0 (round 75) |
| Design review, round 75 | Your own note isn't new; a policy for one shared login that opens every time and never signs; Enter leaves the note and says the time; names never added to older notes; the box says the name will show | Rick | Built in 1.48.0 |
| Design review, round 75 | Signed notes for units that want them | Denise | Built in 1.48.0 as a policy, off by default (Rick's side of the earlier disagreement) |
| Personas, 1.43.0 | "I don't remember", the day a plan was written, big print | Harold | Built in 1.47.0 (round 74) after a design review |
| Personas, 1.43.0 | Gentle mode, a static support link | Sam | Built in 1.47.0 (round 74) after a design review |
| Design review, round 74 | "I'm not sure" not "I don't remember"; `?` not `r`; the date with the day; "not sure" kept as itself; Print; take back a Done | Harold | Built in 1.47.0 |
| Design review, round 74 | Old plans fold away; no label saying a mode is on; offered once after a "not yet"; "If things feel heavy, someone to talk to"; nothing logged | Sam | Built in 1.47.0 |
| Design review, round 74 | "Not in" for days Harold wasn't at work | Harold | Not possible without keeping every visit date, which is off by default for privacy; shown as "nothing noted" |
| Design review, round 74 | A family member seeing the history | Harold | Not built: it would send plans off the PC |
| Personas, 1.43.0 | Desk pet, plan graveyard, boss fight | Jaylen, Skye | Built in 1.50.0 (round 77) after a design review |
| Design review, round 77 | Rotating pet lines; reacts to more than open and done; a countdown to the next thing; never pushes the plan down; mixed bosses; say plainly how the boss is counted | Jaylen | Built in 1.50.0 |
| Design review, round 77 | Things visible on the pet; boss hit points from last week (70%, floor 20); the same trophy on every pet when it falls; absurd bosses, no corporate puns | Skye | Built in 1.50.0 |
| Design review, round 77 | "Graveyard" and eulogies hurt in a low patch; plain "put aside" list for everyone, jokes opt-in | Sam | Built in 1.50.0: plain list, funny farewells a switch, off with no follow-up questions |
| Design review, round 77 | Funny eulogies by default (Jaylen) vs. no death framing (Sam) | Disagreement | Sam's way by default, Jaylen's as a switch with no death words |
| Personas, 1.43.0 | Command line, todo.txt, standup | Priyanka | Built in 1.49.0 (round 76) after a design review |
| Design review, round 76 | WSL and Git Bash decide it; commits from several repos and emails; `--git` opt-in with a remembered default; bare `done` refuses several things; last workday spelled out; import safe to run twice; plain-text export to grep | Priyanka | Built in 1.49.0 |
| Design review, round 76 | `hello` with no words printing only the plan | Priyanka | Not built: it would change the daily screen for everyone; `hello plan` does it |
| Design review, round 78 | Due date named with its thing; keep a kind word in the done lines; Large text and Language at the top of Options; "Welcome back" and the open list after months; no second question while deleting | Harold | Built in 1.51.0 |
| Design review, round 78 | Break the JSON to objects with a version, `n`, `done` and an ISO-or-null `due`; the menu's single date must not overwrite per-thing dates silently | Priyanka | Built in 1.51.0 |
| Design review, round 78 | Strip "by Friday" from the text once read | Priyanka | Not built: the words are the person's own |
| Design review, round 78 | Offer to reset kept settings on delete (Mónica, pilot) vs. no second question (Harold) | Disagreement | Harold's way; the kept settings are named, with where to change them |
| Street research, 1.51.0 | Tray icon; one nudge at a chosen time, not a pop-up | Indie developer | Built in 1.52.0; the timed reminder is the nudge |
| Street research, 1.51.0 | No-install build | Bank analyst | Built in 1.52.0 for personal PCs only, after the analyst said it would break a bank's rules on a work PC |
| Street research, 1.51.0 | A way to pay, offline, no sign-in | Profit Maximizer, teacher, indie developer | Queued: round 80 |
| Street research, 1.51.0 | A phone version, Spanish, big buttons, offline | Cart vendor, rider, analyst | Built in 1.53.0 as an offline web app; sync queued |
| Design review, round 81 | No reminder by default; 6:15 for the cart; Arabic; say where phone notes live | Rider, cart vendor, analyst | Built in 1.53.0 |
| Design review, round 80 | Charge for pets and themes (Profit Maximizer) vs. keep pets free, charge for history and reminders (indie developer) | Disagreement | Pets stay free; Pro is history, a second reminder and themes |
| Personas, 1.43.0 | Formulas run in the spreadsheet export | Skye, confirmed in code | Fixed in 1.46.1 |
| Personas, 1.43.0 | Forklift horns, bakery orders, badge login, a supply locator, an email "lie detector" | Rick, Harold, Denise | Not buildable here: they need hardware or outside services |

Of 7 claims checked against the code, 2 were wrong, 1 was true only for
shared Windows logins, and 1 (the export formulas) was a real security issue
nobody had looked for.

## Limits

- Agents simulate people; they agree with each other more than people do,
  and none of them had to use the product on a bad morning for real.
- They read a transcript of the text screen, not the window, so the window's
  layout went unreviewed.
- Prices are guesses by agents with no budget. Treat them as an order of
  magnitude.
- Translations made in these rounds are simulated too and need a native
  speaker, as `TODO.md` says.

## Running it again

Capture a fresh two-day transcript from the current version with the test
harness, update the brief, and send the same prompts from
`docs/personas/prompts.md` to fresh agents. Check every claim against the
code before acting, and add a row to the track record for each finding.
