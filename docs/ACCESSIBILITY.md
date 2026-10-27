# Accessibility

A summary of how hello-world meets common accessibility expectations, and how
that was checked. It isn't a formal conformance report, but it gives
procurement what one would be built from. Since 1.28.0 the Start menu opens a
window, and the console program described here is the text screen, which
each person can switch to under Options and Group Policy can set for
everyone. Web criteria apply only where they carry over.

## How it was checked

| Check | Version | Result |
|---|---|---|
| Narrator in a real console, by the owner | 1.16.0 | Passed |
| NVDA, including how the prompts read, by the owner | 1.23.0 | Passed |
| Simulated 30-day pilot with an NVDA user, a Magnifier user at 200 to 300 percent, an ADHD user and a second-language reader | 1.19.0 to 1.21.0 | Findings fixed in 1.20.0 to 1.22.0; see `docs/PILOT.md` |
| JAWS, by the owner | 1.24.0 | Passed |
| Spanish screens, simulated review by a native speaker | 1.25.0 | Findings fixed in 1.25.0 |
| French, Portuguese and German screens, simulated review by native speakers | 1.26.0 | Findings fixed in 1.26.0 |
| The window, drawn on Windows 11 at 100 percent scaling in English and German, and opened and closed in every language by the tests | 1.28.0 | Passed |
| The window and the sign-in notification with Narrator, NVDA, JAWS, Magnifier at 200 percent and a high contrast theme, by the owner | 1.28.0 | Passed |
| Spanish, French, Portuguese and German screens, native speaker review, by the owner's reviewers | 1.28.0 | Passed |

## What it does

- Keyboard only: everything works with typed words and Enter, and Enter alone
  gets through every screen.
- One top-to-bottom flow of plain text: no colors, no cursor movement,
  nothing redrawn, so a screen reader reads it in order. A picture of
  characters can follow the days-in-a-row line, and only if the person types
  pic. Enter skips it. From 1.65.0, `q` at that question, and at Enter to
  continue after the picture, closes the visit.
- Every prompt ends by saying what Enter does, such as "Enter to close".
  From 1.63.0 the prompt itself ends in a colon, unless `colon_prompts` is off.
  From 1.64.0 that includes a cue with no space before the greater-than sign,
  which is how some Chinese and Japanese prompts are written. The sentence
  "Prefer no follow-up questions? Options > What the window shows." is not a
  prompt, and it still says greater. A joke line never replaces Hello, world!. Morse is a command,
  not the morning. `hello shift` is a command too. It prints the greeting and one plain sentence, it does not read the clock, and it is not on the phone.
- Long prompts and paragraphs wrap to the window width, down to 30 columns,
  so nothing runs off a magnified screen.
- No time limits: no prompt times out and nothing closes by itself.
- Mistakes are named: a word the prompt doesn't accept is quoted back with the
  choices, and the question is asked again.
- Choices that could clash use numbers, as in the menu and "When did you
  finish it?".
- Plain words: idioms were replaced after the second-language reader's review.
- The menu is read once and listed again only on request, and Help explains
  the words rather than repeating the menu.
- Tips that assumed sight offer another way to do them.
- `q` closes from any question, including the picture, and Ctrl+C skips just one prompt, so an
  accidental key press doesn't end the visit. From 1.66.0 the streak-note question says "Enter to accept, or type no to decline". Enter on that question accepts. q still closes, and it does not accept. One Ctrl+C skips it and asks again next time.
- The phone's streak-note banner is not a focus trap. Tab still reaches the plan box. Not now hides the banner. If focus was inside it, focus moves on, the same way a hidden Skip button does. This was not checked with NVDA.
- Group Policy and menu settings remove content people don't want read every
  day: the thought and tip, and the days-in-a-row message.

## The window

- Standard Windows controls only: static labels, one edit box, push buttons,
  a popup menu and a standard message box, so screen readers get their names
  and roles from Windows.
- Each label sits just before the control it names, so the plan box is read
  as "What is one thing you want to get done today?".
- Every button has an Alt key, Enter saves the plan and closes, and Esc
  closes without saving. Tab moves through the buttons in reading order.
- It uses the system font at 12 points and scales with the display, and its
  colours are the system's window colours, so high contrast themes apply.
- A message after a button, such as "Kept for today.", changes a label's text.
  Screen readers don't announce that by themselves; focus moves to the plan
  box next, and the message sits just above it.

## The phone

- After the first Skip the question is still there, and focus stays on that
  button. The status line is live, so the words are announced without leaving
  the button. A second Skip hides the question. Focus then goes to the status
  line, and to the plan box when that box is on screen. This was not checked
  with NVDA.

## Known limits

- English, Spanish, French (France and Canada), Portuguese (Brazil and Portugal), German, Simplified Chinese, Japanese, Korean, Arabic and Hebrew, chosen from the Windows display language or by
  the person. The text screen shows English for Chinese, Japanese, Korean,
  Arabic and Hebrew, which the window draws, Arabic and Hebrew right to left.
- The program shows text that a console can't draw, such as some scripts and
  emoji on older consoles, as `?`.
