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

## Not changed, and why

- NVDA saying "greater" at the end of every prompt (Ruth). It's unclear
  whether NVDA reads `>` at its default punctuation level, and a simulated user
  saying so isn't enough to change every prompt. A real NVDA check decides it.
  See `BACKLOG.md`.
- Reaching people on their laptop on site days (Marcus). That is where IT
  installs it, not a program change.
