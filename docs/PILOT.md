# Pilot, October 2026

This was a simulated pilot. Five simulated employees, each with a made-up name
and a written background, used the real program from Monday 5 October to
Tuesday 3 November 2026. Each kept a diary and answered check-in questions on
day 14 and day 30. None of them was told it was a simulation.

The people and the feedback are simulated, but the program was not. Each
visit ran the real `hello.py` 1.19.0 on its date, with that person's own
`notes.json` carried from day to day, so every screen and saved file in their
diaries is what the program really did. Treat the feedback as strong leads,
not as proof of what real employees want.

## Who took part

- Dana, accounts payable. Organized and skeptical of wellness software. Never
  turned on the sign-in opening.
- Marcus, field support. At a desk about three days a week, often away.
- Jun, IT helpdesk. Tried every option, including two windows and Delete
  everything.
- Ruth, receptionist. Blind, and uses NVDA every day.
- Sam, marketing. Has ADHD and works Monday to Thursday.

## How often they opened it

| Person | Opened | Notes |
|---|---|---|
| Dana | 19 of 21 workdays | A habit, without the sign-in opening |
| Marcus | 11 of 30 days | Every desk day, no site days |
| Jun | 22 days | Every workday but one, plus an on-call Saturday |
| Ruth | 20 of 22 workdays | All from the sign-in opening |
| Sam | 13 of 18 workdays | Forgot it for ten days after turning off the sign-in opening |

All five would keep using it. Four said the sign-in opening is what made it
stick.

## What they liked

- Under half a minute a day, the same order every time.
- Privacy they could check: Jun read `notes.json` and it held exactly what the
  README says.
- The next-day "Did you do it?", which twice caught something Marcus had
  forgotten.
- Typing `done` and seeing the last few finished plans. Jun used the list as a
  work log.
- "Welcome back. Glad you are here." after a gap, with no guilt. Sam said
  that screen is why they came back.
- Everyone seeing the same tip, which gave people something to talk about.

## What went wrong, and what 1.20.0 does about it

| Finding | Who | In 1.20.0 |
|---|---|---|
| A finished plan was offered back as "Earlier plan" for `same` | All five | `same` holds only unfinished plans |
| Two "not yet" answers put a plan away, though waiting on someone isn't failing | Four (Sam wanted the opposite) | "Not yet" keeps a plan as long as needed; a plan first set over two weeks ago is put away |
| A yes to "Did you do it?" got no answer until after the next question | Four | A yes is saved and answered at once, with the finished list |
| A finished plan was dated the day it was confirmed | Three | Dated the day the plan was for |
| A Friday off broke the "in a row" line, though the README said days off don't | Three | A gap of up to four days counts |
| The thought and the tip were both about shoulders on one day | Three | The thought moves on when they share a body topic |
| The menu was read again after every choice, and Help repeated it | Ruth, Jun | The menu is read once; `m` lists it again; Help explains the words |
| A full file path was read out, backslash by backslash | Ruth, Sam | No path in the menu or after turning on the sign-in opening |
| The sign-in question came back three days running | Jun | Asked once |
| `q` didn't work at the yes or no questions | Sam | `q` closes from any question, and the visit still counts |
| The last prompt dropped `done` after the sign-in question on the first day | Found by the tool before the pilot | The prompt picks up the saved plan again |
| "Cleared. It stays as same until you delete everything." and "it asks tomorrow" on a Friday | Dana | Reworded |
| A thought assumed it was afternoon, and one assumed a quiet desk | Ruth | Reworded |

## Second round, on 1.20.0

The same five used 1.20.0 from 4 to 17 November, with fresh notes. Before
that round they had been told that IT updated the program. All five said the
fixes above landed: finished plans stay finished, "not yet" no longer puts a
plan away, a yes is answered at once, and `q` closes the morning questions.
All five would keep using it.

| Finding | Who | In 1.21.0 |
|---|---|---|
| A plan confirmed days later was dated to the plan day, not the day it was done | Marcus, Jun | A plan more than a day old asks which day it was finished |
| A typo fixed with `plan` came back as "Earlier plan" after `done` | Jun | Changing today's plan replaces it; only a plan from an earlier day is kept for `same` |
| `q` at the menu went back instead of closing | Jun | `q`, `x` and `close` close from every question, the menu included |
| After `q` at "Did you do it?", a second open the same day skipped the question | Sam | The question is asked until it is answered |
| Skipping the question every day kept it coming back | Sam | Two skips stop the question; the plan shows as still open |
| The finished list after every yes was too much each morning, under a changing heading | Ruth, Dana | A yes gets the praise only; the list comes with `done`, under one heading |
| No way to turn off the thought and tip | Dana | Menu option 8 |
| Forget didn't say which plan it removed | Jun | It names the plan |
| Plans of several things joined with "and" or "+" | Sam | One gentle line that finishing the first part still counts |
| The first-day welcome was long | Ruth | One paragraph |
| "That is 2 times you have marked a plan done" read clumsily | Dana | "That is 2 done so far." |

Their notes starting fresh was part of how the simulation was run, not
something the program does: an update keeps `notes.json`.

## Third round, on 1.21.0, with three new people

Three new simulated people used 1.21.0 from 18 November to 1 December:

- Amara, a new operations assistant whose first language isn't English.
- Glenn, a purchasing officer with low vision who uses Windows Magnifier at
  200 to 300 percent.
- Priya, the operations manager, who would decide whether to roll it out to
  all 40 people.

All three would keep using it. Priya would roll it out as optional, after the
changes below.

| Finding | Who | In 1.22.0 |
|---|---|---|
| The file kept up to 400 dates someone opened it, which reads as an attendance record if anyone pulled it | Priya | Only the last 60 days are kept |
| "That is 4 done so far" after each finish felt like scoring | Priya | The tally is gone; the count stays in option 1 |
| Option 1 didn't show whether the sign-in opening is on | Priya | It does |
| Uninstalling left everyone's notes | Priya | 1.22.0 let the uninstaller delete them; 1.23.0 withdrew that after a security review showed a user could redirect the delete. Users delete their own with option 4 |
| Long prompts ran past a magnified window, with the choices at the far end | Glenn | Prompts wrap to the window, and only the last line waits for the answer |
| In "When did you finish it?", `y` meant yesterday right after `y` meant yes | Glenn, Amara | The days since the plan are listed by number |
| The plan sat after a long date label | Glenn | "Still open since ..." puts the plan on its own line |
| About fifteen idioms were hard to follow, such as "put that one down", "leave lighter" and "Left as it was" | Amara | The praise lines, that reply and the nine quoted thoughts and tips are in plain words |
| "In-a-row line" didn't say what it was | Amara | It's called the days-in-a-row message |

Not changed: the days-in-a-row message stays on by default, and removing the
program still needs an administrator. `TODO.md` has the work. Two of
Glenn's points, an answer and the next question sharing a line, came from how
the simulation fed in answers without echoing them; a real console starts a
new line after Enter.

## The window, two simulated rounds in October 2026

In October 2026 the window and sign-in reminder had a simulated week with
five more people, each a fresh agent given only a persona and a tool that
drives the real window: a warehouse shift lead on a shared PC (Dana), an
accounts receivable analyst in Portuguese (Rafael), a support agent with ADHD
(Priya), an HR coordinator in Spanish who checks privacy (Mónica), and a
developer who pokes at everything (Tom). Each ran Monday 5 to Monday 12
October, signing in each morning and opening hello-world only when that
person would. They ran twice: on 1.28.0, then on the fixes below.

The first round found:
- **I did it** marked the old plan done when the box had been edited (Priya).
- Turning off the thought and tip said "off" while they stayed on screen
  (Dana, Tom).
- Save and Enter closed with no sign anything was saved (Dana, Priya).
- Esc and Close dropped an edited plan without asking (Tom).
- Tab went right to left across the bottom buttons (found while building
  the tool).
- "You have opened this 3 times in a row" counted days, not opens (Dana,
  Priya).
- Showing or deleting what is saved needed the black text menu (Mónica,
  Rafael).
- The text menu called the reminder "open once a day at sign-in" (Priya,
  Rafael, Tom).

The second round found:
- Saving a new plan and then clicking Done on the old one said "The other open
  window changed the plan", with no other window (Tom).
- There was no way to drop a plan (Tom).
- "Show what is saved" showed the raw file (Dana, Priya, Rafael).
- The days-in-a-row message read as being counted, and the program kept 60
  days of dates for it even when it was hidden (Dana, Mónica).
- The finished list dated a plan by the day it was set, not the day it was
  marked done (Mónica, Priya, Tom).
- Done on the notification had no reply (Priya).
- After **I did it**, the box asked for another plan as if one were owed
  (Dana, Rafael).

1.29.0 fixes all of these. Ratings, first round then second: Dana 6 and 5,
Rafael 6 and 6, Priya 5 and 6, Mónica 5 and 5, Tom 6 and 6. Every one of them
named the sign-in notification as the part they'd keep.

What they asked for that 1.29.0 didn't build went to `TODO.md`, and 1.30.0
started on it: a checklist of
several plans (Rafael), "partly done" (Priya, Rafael), tips for shift work
(Dana; an organization content file does that), public holidays (Mónica,
Rafael), a different title than "Hello, world!" (Dana, Rafael), and Skip on
the notification (Priya).

## Third and fourth rounds, on 1.36.0 and 1.37.0

The same five ran again, fresh each time, on the new features. Ratings, third
round then fourth: Dana 3 and 4, Rafael 3 and 4, Mónica 4 and 6, Tom 5 and 6,
Priya 6 and 6.

The third round's complaints were records they couldn't trust and a menu of
sixteen items; 1.37.0 answers them. The fourth round found:
- Marking things done took a different path in each place: tick boxes the
  morning after, a Yes or No box per thing under **I did it**, and an
  all-or-nothing Done on the notification (all five).
- "With none ticked, Done means all of them" was a trap (Tom, Priya).
- A plan of more than five things had its last ones merged, and a long plan
  was cut at 200 characters with only "Saved." (Rafael, Tom).
- "That is done" after finishing two things (Tom).
- An unanswered plan moved silently to `same` when a new one was saved (Dana).
- A count of finished plans they never asked for (Mónica).
- Save with an empty box closed the window without a word (Tom).
- The display settings seemed to close the window. That was the pilot tool,
  which didn't follow the window when it redrew; it does now.

1.38.0 fixes all of these.

## Not changed, and why

- NVDA saying "greater" at the end of every prompt (Ruth). It's unclear
  whether NVDA reads `>` at its default punctuation level, and a simulated user
  saying so isn't enough to change every prompt. A real NVDA check decides it.
  See `TODO.md`.
- Reaching people on their laptop on site days (Marcus). That is where IT
  installs it, not a program change.
- Closing after `done` and the next plan (Marcus). The last prompt comes back
  on purpose, so the result can be read before the window closes.
- A smarter `same` that knows when the parts of an earlier plan were done
  separately (Sam). The program can't tell, and option 7 or a new plan clears
  it.
