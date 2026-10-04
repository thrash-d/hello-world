# Changelog

## 2026-10-03: the window's settings in the text menu, and concrete tips

Version 1.39.0. This round built the queue the fourth pilot left.

- The text menu has option 12, **More settings...**, with what only the
  window had: the reminder times and the reminder's switches, Greet me by
  name, floor and shift tips, This week, My numbers, Save my plans to a file,
  Keep a longer history and Forget the earlier plan. The window and the text
  menu share one list of reminder switches and one way to flip a setting.
- Fifteen tips that read like office posters, such as "roll your shoulders"
  and "share a small, harmless joke", are now things to do with an end, such
  as "Raise your screen so its top edge is at eye level" and "In your next
  request, say why you need it and by when." All ten translations follow.
- In the text menu, Enter that leaves a question without a change now always
  says "Enter to go back", where it said "keep them all" or "keep it" before.
- Arabic and Hebrew were checked on a real screen: the window is laid out
  right to left as it should be. The mirrored title in the pilot's screenshot
  came from `PrintWindow`, which copies a right-to-left window mirrored, and
  the pilot tool now flips such screenshots back.

Still queued in `TODO.md`: whether the window a timed reminder opens outlives
the scheduled task's time limit, which needs a throwaway scheduled task.

## 2026-10-03: one way to tick things off, and the review's fixes

Version 1.38.0. A fourth simulated pilot ran on 1.37.0 alongside a code and
security review of it. Ratings: Dana 4, Rafael 4, Mónica 6, Tom 6, Priya 6.

From the review:
- "After an upgrade, a timed reminder can't be turned off, not even by
  policy." 1.37.0 renamed the task to carry the domain, and nothing looked
  for the old name. hello-world now moves a task under the old name to the
  new one at the same time, or removes it under `DisableSignInLauncher`, and
  `uninstall-user.ps1` removes both names.
- "`Visit.finish_parts` uses tick indexes from a plan that may have changed."
  The window now finishes things by their words, checked against the plan as
  saved, and changes nothing when another window has changed it.
- "Turning My numbers back on wipes the earlier counts." It keeps them.
- "Redrawing the window throws away what was typed." What was typed and
  ticked comes back after a redraw, and a redraw isn't logged as another
  opening under `ReportUsage`.
- "`language_fits` still lets through a translation file that crashes the
  program." An empty or wrong `tips_floor`, or a translation whose `{names}`
  differ from the English, now skips that language.
- "`release.yml` can publish a package under a tag that points at a different
  commit." The release stops when the tag exists at another commit.
- "`dependabot-automerge.yml` checks only one tests run." It waits for every
  run on the commit, and `.github/dependabot.yml` now asks for weekly action
  updates, so the workflow has something to merge.
- "Forget removes every identical row but takes back only one done." It
  removes one, in the window and the text menu.
- "`uninstall.ps1` leaves each user's protocol and notification
  registrations." It removes them where they point at the install it removes.
- "Emptying the box and clicking I did it finishes a multi-part plan without
  asking." It asks now, as part of the tick boxes below.

From the pilot:
- Today's plan of a few things has a tick box for each under the plan box;
  tick what you finished and click **I did it**. The Yes or No box per thing
  is gone, and nothing ticked asks before marking everything.
- The morning-after question says "Tick the ones you did, then click Done."
  and no longer says that nothing ticked means all of them.
- A notification about a plan of a few things offers Open instead of Done.
- A plan holds up to ten things and 400 characters, and a cut plan says so.
  A part with nothing in it but dashes or punctuation isn't a thing to do.
- Finishing several things says how many: "Good. 2 things are off your list."
- The question shows the plan's date: "Your plan from Monday, 5 October".
- Saving a new plan while the old one is unanswered asks whether to keep the
  old one for today too.
- The done count is kept only with **My numbers** on. The finished list stays
  either way.
- **My saved notes > Forget the earlier plan** clears what `same` brings back.
- **This week** shows last week too, My numbers says what a run is, and the
  saved summary says why "Last opened" is kept.
- Save with an empty box says to type a plan first instead of closing.
- The reminder settings each say what changed, Keep a longer history says the
  usual is 14 days, **Use the text screen** shows a tick when it's on, and
  **More options** is now **Open the text menu**, which is what it does.
- The text menu's help says "see" the options, not "hear".

Still queued in `TODO.md`: tips that read like office posters, the window's
settings in the text menu, one wording for Enter in the text menu, and two
checks on real hardware.

The pilot tool now follows the window when it redraws, which is why the
display settings seemed to close it, and ticks up to ten boxes.

Every new string is translated into the ten other languages by three agents.
Tests: the old task name moved, ticks from a changed plan refused, the
notification for several things, last week, forgetting one of two identical
rows, numbers kept when turned on again, a wrong placeholder or empty floor
tips skipped, the done count only with My numbers, the empty Save and a cut
plan. 262 run here on Windows: all pass but 2 POSIX-only ones.

## 2026-10-03: a review, a third pilot, and everything they found

Version 1.37.0. With the queue empty, round 62 reviewed 1.36.0: one code and security reviewer, and the five simulated employees again, fresh, on the new features. The pilot ratings were Dana 3, Rafael 3, Mónica 4, Tom 5 and Priya 6, down from the last round, and the reasons were records they couldn't trust and a menu that had grown to sixteen items.

From the code review:
- `uninstall.ps1` dropped `-RemoveNotes` when it restarted itself in 64-bit PowerShell, which is how Intune runs it, so nobody's notes were deleted while the result said they were. It is passed on now.
- A notification's Done answered whatever plan was current, so an old notification in Action Center, or a `hello-world:done` link from anywhere, could finish a plan it never asked about. Each answer link now carries the plan's date and a digest of its words, and anything else is refused.
- `LeaveDamagedFile` and `DisableSignInLauncher` weren't honoured at sign-in, which is where they matter: a damaged file was set aside with nobody there, and a reminder at a set time kept coming under the policy. Both are honoured, and the policy removes the timed task too.
- When the notification can't be shown, the window opens in a process of its own, outside the scheduled task's five-minute limit.
- `uninstall-user.ps1` removed the Apps entry before it knew the folder could go; it renames the folder aside first now, so an open window leaves everything as it was.
- The uninstaller found no Entra ID users' sign-in values, and one schtasks error could stop it removing the rest; both fixed, and it removes only what points at the install it removes, so a per-user install keeps its own.
- A translation file that didn't fit could stop the program at start; it is skipped now, as the 1.36.0 notes said.
- Reminder tasks carry the domain as well as the user name, `export_plans` uses the real Documents folder, a release by hand runs only from main, and Dependabot merges wait for the Windows and installer tests too.

From the pilot:
- "With none ticked, Done means all of them" finished plans people hadn't done. Done with nothing ticked asks first now, and **I did it** asks about each thing in a plan of several.
- "This week" held only the last seven finished things, which a few multi-part plans fill in two days. Finished plans are kept for 14 days now, or 90 with a longer history, so the week is always whole.
- With the days-in-a-row message off, the summary said "Days you opened it: 1" after a week of visits; it says "Last opened" now, since that is all that is kept.
- A plan answered the next morning counts on its own day again, which four of the five expected.
- Forgetting a finished plan takes its done back, and the window can forget one too, under My plans.
- Options has eight items, with the rest in What the window shows, My plans, My saved notes and Language. Turning something on that changes the window redraws it at once: the thought and tip, the floor tips, the greeting and the language. Each says what changed rather than "Saved.".
- Picking a language mid-session changed the window one choice late; the language is now read once per window and the window redraws.
- My numbers asks to start when it is off, counts today from that moment, and says nothing about `--set`.
- The window asks "What do you want to get done today?", which fits a list, under the `;` hint.
- **Leave my plan out of the reminder**, for shared PCs, and a `FloorTips` policy that sets the floor and shift tips for a whole site.
- Close asks to save only text that could be saved.

The pilot tool had two faults of its own: its clicks never ticked a tick box, so every partial answer looked like "all of them", and it created a real reminder task and registry links on the PC it ran on. Both are fixed, and the task and keys were removed.

Every new string is translated into the ten other languages by three agents. Tests: the link key, a stale link refused, the policies at sign-in, a broken translation file skipped, the language read once, two weeks of finished plans, finishing some parts of today's plan, forgetting from the window, numbers counting today, "Last opened", and the FloorTips policy. 256 run here on Windows: 254 pass and 2 are POSIX-only.

## 2026-10-03: translations in their own files, and the queue emptied

Version 1.36.0. Builds the last items in `TODO.md`.

- The translations moved out of `hello.py` into one file per language, `hello.<language>.json`, which `hello.py` reads at start. A file that can't be read or doesn't fit is skipped and that language shows English. A regional file names its base language and holds only what differs. `hello.py` went from 11,492 lines to under 4,000, and a script compared every string, list and date before and after the move: identical. The installer, the per-user install and the package builder carry and check the files like `hello.py`, and CI checks the installed program loads every one.
- An organization can ship content per language, `content.<language>.json`, which that language shows in place of `content.json`; a regional language falls back to its base language's file first. `-ContentFile` takes several files, and the installer checks each one.
- **Tips for floor and shift work**: a second list of 40 tips for warehouses, factories and shifts, chosen under Options or with `--set floor_tips on`, for Dana from the 1.29.0 pilot. Three agents translated it into the ten other languages, using the words people on a floor use, such as douchette, ヒヤリハット and חפיפה.
- The pre-1.23 Startup launcher is found through the Known Folder API as well as `APPDATA`, so a redirected profile is cleaned up too.
- A `LICENSE` (MIT, Thrash'd) and a `CODEOWNERS` file.
- Every action in every workflow is pinned to a commit. hello-world keeps its own `auto-tag` and `dependabot-automerge`, opting out of the shared kit's copies with `.devkit/no-auto-workflows`; `devkit-quality` is pinned here and needs pinning again after a kit update.
- Tags and releases wait for the tests: `auto-tag` and `release` start when the tests workflow finishes successfully on a push to main, from that commit, instead of on the push.

`TODO.md` now has only what waits on the deploying organization: its signing certificate and a real pilot.

Tests: translations loading from files with a broken and an unknown one skipped and a regional one merged, content per language with its fallback, the floor tips in English and Spanish, every language's floor tips, and the Startup folder from the Known Folder API. 246 run here on Windows: 244 pass and 2 are POSIX-only.

## 2026-10-03: installer hardening, and an install for one person

Version 1.35.0. Builds the installer items in `TODO.md`, which earlier rounds left for a test on a spare PC as administrator. CI is that PC: every change here runs there as administrator, and the new standard-user and per-user checks run there too.

- `install-user.ps1` installs for one person with no administrator, from the same release package and package hash, into `%LOCALAPPDATA%\Programs\hello-world`, with that person's Start menu and Settings > Apps entries. `uninstall-user.ps1` removes it and its reminder. The simulated pilot's laptop user and the old "remove it without an administrator" item both asked for this. The install folder is in the person's own profile, which the README says plainly.
- `tools\reinstall.ps1` does the git clone steps in one command.
- The installer reads the architecture from the operating system rather than `PROCESSOR_ARCHITECTURE`, and stops on Windows before 10 version 1809, which the window needs.
- Domain Admins and Enterprise Admins pass its permission checks.
- Its folder walk never goes into a junction, and it checks that only administrators can change the all-users Start menu folder.
- `git hash-object --no-filters`, so no filter configuration can change what the commit check sees.
- Proxy credentials for the Python download, `NO_COLOR`, and the names of open hello-world programs when a file in use blocks an upgrade or uninstall.
- The bundled Python leaves out more modules hello.py never loads: `_lzma`, `_bz2`, `_elementtree`, `pyexpat`, `winsound`, `_multiprocessing`, `_overlapped`, `_asyncio`, `_zoneinfo`, `_decimal` and the test modules. CI draws the window, builds a reminder task and checks content with the trimmed copy.
- CI verifies the pinned Python zip's sigstore signature, runs the installed program as a standard user and checks that user can't write into the install, and installs and removes the per-user install. A weekly `python-pin` workflow checks the pinned hash and fails when a newer patch release is out.

Already done and removed from `TODO.md`: rolling back when step 6 fails, the "dubious ownership" message and `GIT_CONFIG_GLOBAL=NUL` were already there, and each release's notes already name the commit it was built from.

## 2026-10-03: seven more languages

Version 1.34.0. Builds the language items in `TODO.md`, which earlier rounds had held back: the window now speaks Simplified Chinese, Japanese, Korean, Arabic and Hebrew, and France and Brazil get company from Canadian French and European Portuguese.

- Each new language was translated by its own agent from the English, with the reviewed Spanish and French as references, then reviewed by the same agent as a native speaker. They changed 51 entries in Chinese, 34 in Japanese, 33 in Korean, 25 in Arabic and 28 in Hebrew on review, such as a feminine noun given masculine status words in Hebrew, "show" read as software in Korean, and a word order error in Chinese. A checker held every file to the exact English keys, placeholders, prompt endings and Alt-key letters. The Japanese window was drawn and checked, and the Arabic one checked mirrored.
- The register follows each language's Windows: 您 in Chinese, です/ます in Japanese, 해요체 in Korean, and gender-neutral phrasing in Arabic and Hebrew. Command words people type stay in English inside the translations. Buttons use the Windows Alt-key form, such as 完了(&D).
- Arabic and Hebrew mirror the window, its menus and its message boxes right to left.
- The text screen shows English for these five, since older consoles draw them as `?` and run right-to-left text backwards. The window and notifications show them.
- Simplified Chinese follows China and Singapore; Traditional Chinese PCs keep English until there is a translation for them.
- Canadian French changes 19 strings and 12 thoughts and tips from the France text: fin de semaine, courriel, dîner for lunch, no space before ? and !. European Portuguese is a full translation: ecrã, ficheiro, guardar, no você. Both follow the whole Windows language ID, so other French and Portuguese PCs keep the France and Brazil texts.
- The window allows for characters that take two columns when it sizes text, after the Japanese instruction line was cut short.
- Group Policy templates come in fr-CA, pt-PT, zh-CN, ja-JP, ko-KR, ar-SA and he-IL. The `ForceEnglish` help no longer lists four languages; it says the screens follow the Windows display language when there is a translation, and points to `docs/ENTERPRISE.md`, which lists them. The Hebrew and Korean translators caught the old list.
- Options > Language lists all twelve, each in its own words.

Tests: every language has every string, list and date, and a template with every policy string; the five scripts show in the window and English in the text screen; the regional variants follow the whole language ID; a whole day in each language that the text screen shows, with no English left; and the window opens and closes in all twelve. 242 run here on Windows: 240 pass and 2 are POSIX-only.

## 2026-10-03: history, numbers, and choices for the text screen

Version 1.33.0. Builds the rest of the employee items in `TODO.md` that need no new language or installer work. Most of them were declined in earlier rounds as against the design; each is now a choice that is off until someone turns it on.

In the window's Options:
- **This week...**: what was finished since Monday.
- **My numbers...** with **Keep my numbers**: days opened, the longest run of days, plans finished. Counted only while it's on, so nothing is counted for anyone who doesn't ask.
- **Save my plans to a file**: the current and finished plans as Markdown in Documents.
- **Keep a longer history**: 60 finished plans instead of 7.

Every on-or-off choice also has `--set NAME on|off`, which is how the text screen reaches the ones without a menu line: `hide_finished`, `expire_same` (`same` lets go of an earlier plan after 30 days), `no_count`, `close_after_done` and `colon_prompts` (prompts ending in `:`, which the simulated NVDA user asked for in 1.21.0). `--week`, `--numbers` and `--export` do the same as the window from a command line.

Also:
- The text menu's option 11 marks today's plan done.
- The status line and the answer to "Did you do it?" are UI Automation live regions, set through the Dynamic Annotation API, so screen readers announce them when they change. This was declined in 1.28.0 as needing more than `ctypes` could reach.
- Left-to-right and right-to-left marks stay in plan text; the override characters are still removed.
- `--utf8` writes UTF-8 whatever the console's code page, and `--plain-local` prints the greeting in the person's language. `--check-content FILE --local` answers in the Windows display language; without it, the answers stay in English for administrators' tickets.
- `retomar` works as `same` too, as the Spanish reviewer suggested in 1.25.0.
- A sign-in value from 1.23.0 to 1.27.0, which opened a console, is rewritten to the current one the next time hello-world opens.
- Placeholders in a translation may come in a different order from the English; the test now checks the set.

Tests: the longer history, numbers and the weekly list over nine days, the export file, no done count and no finished list, `same` expiring, colon prompts, closing after the next plan, direction marks, `--check-content --local` and `--plain-local`, Mark done from the menu, and the old sign-in value rewritten. 240 run here on Windows: 238 pass and 2 are POSIX-only.

## 2026-10-03: options for IT, and one reminder task per user

Version 1.32.0. Builds the IT items the old backlog had declined as against the design. Each is opt-in by Group Policy, and none of them sends anything over a network or writes plan text anywhere new.

Bug: 1.31.0 named every person's reminder task `hello-world reminder` in the task folder every user shares, so on a PC with several users one person's reminder time replaced another's, or failed to save. Each task now carries the user name.

Policies, with ADMX and ADML strings in all five languages:
- `ReportUsage`: one Application event, source `hello-world`, ID 2000, for each open, plan set and plan finished.
- `LogErrors`: `errors.log` in the person's data folder with the time, version, error type and `hello.py` line numbers, under 100 KB.
- `FeedbackAddress`: Options > Send feedback... opens a new mail to that address in the person's own mail program. Only a plain address is accepted, so the policy can't add recipients or a body.
- `TimestampBackups` and `MaxBackups`: backups of a damaged file named by date and time, and a cap on how many are kept.
- `LeaveDamagedFile`: a run with nobody at the keyboard leaves a damaged file for the next visit to set aside.

Also:
- `notes.json` carries `"schema": 1`. `load()` still checks every field by type.
- `--count-sign-in off` leaves sign-in runs out of the days-in-a-row count.
- `uninstall.ps1` turns off every user's reminder, removing only Run values whose data runs `hello.py` or `hello.cmd` with `--startup`, and every reminder task. `-RemoveNotes` deletes each profile's notes files, checking for links before each delete; the script's help names the race that check can't close, which is why 1.23.0 withdrew it, and why it is a switch, not the default. CI runs it as administrator and checks that the notes, the Run value and the task go, and an unrelated file stays.

Tests: usage events only under the policy and with no plan text, the error log with no plan text, feedback addresses refused and accepted, timestamped and capped backups, a damaged file left alone with nobody there, sign-in runs left out of the count, the per-user task name, the frozen list of saved keys with every key added since 1.28.0, and policies with values in the template check. 232 run here on Windows: 230 pass and 2 are POSIX-only.

## 2026-10-03: reminder choices, days off, and a greeting by name

Version 1.31.0. Builds the reminder and greeting items from the queue in `TODO.md`, which the pilots asked for and the old backlog had declined.

- **Options > Reminder settings** in the window:
  - **At sign-in** (as before), or **At 8:00**, **9:00**, **10:00** or **13:00**. A set time is a scheduled task in the person's own task folder, so it needs no administrator. It runs at the next sign-in when the PC was off at that time. Picking sign-in, or turning the reminder off, removes it. ("I don't know what time I'll get in" was the 1.28.0 user's reason for sign-in; now both are there.)
  - **Also on days with no plan**: "One thing to get done today? Open hello-world to plan it." with an Open button. (Dana and Priya, 1.29.0 pilot: "once you miss a day it quietly stops nudging you.")
  - **Open hello-world after I answer**, instead of the thank-you.
  - **Not on weekends**.
- `content.json` can list `"holidays"`, days the reminder stays quiet (Mónica and Rafael, on 12 October), and a `"title"` that replaces "Hello, world!" at the top of the window and text screen (Dana, Rafael). `--plain` still prints "Hello, world!". `--check-content` checks both.
- **Options > Greet me by name** puts the person's first name from Windows at the top: "Hello, Ana!". It falls back to the title on a PC outside a domain.
- The new `TurnOnReminder` policy turns the reminder on for everyone who hasn't answered the reminder question yet; anyone can still turn it off, and it stays off. ADML strings in all five languages.
- `docs/ENTERPRISE.md` lists the scheduled task for persistence allow-lists, and the new content keys.

Every new string is translated. Tests: the no-plan reminder, weekends, holidays and the title from `content.json`, the content checks for the new keys, a set time replacing sign-in and back, opening after an answer, the greeting by name, the policy turning the reminder on once and staying off after, and on Windows a real scheduled task created and removed as the signed-in user. 226 run here on Windows: 224 pass and 2 are POSIX-only.

## 2026-10-03: several things in one plan, and nothing declined

Version 1.30.0. The owner set a new rule for this project: nothing is declined. Every idea from a review, a pilot or the owner gets built, and anything that touches privacy or safety is built as an opt-in setting or policy that keeps the safe default. `BACKLOG.md`, the list of declined ideas, is gone. Its items are the build queue in `TODO.md`, and its "turned out wrong" notes are under "Checked and already fine" there. This round builds the pilot's asks first.

- A plan can be a few things with `;` between them: "Call Ana; send the report". Rafael typed "1) ... 2) ... 3)" into one line all week. Each thing is finished on its own and gets its own line in the finished list and its own done.
- Partly done. The window shows a tick box for each thing in yesterday's plan; Done finishes the ticked ones and keeps the rest for today, saying "The rest is kept for today." With none ticked, Done means all. The text screen lists them by number, and `1 3` finishes the first and third. (Priya, Rafael)
- The window's empty status line says "A few things? Put ; between them." `;` doesn't get the "more than one thing" note, since the list is on purpose. A plan can be 200 characters, up from 120, to fit a short list.
- The notification has Skip as well as Done and Not yet. (Priya)
- Reaching the length limit in the box says "A plan can be up to 200 characters." instead of just stopping. (Tom)
- Delete everything keeps the person's settings (the days-in-a-row message, the thought and tip, window or text screen, the reminder question and the language) and says "Your settings were kept." (Mónica)
- A language other than the Windows one, per person: Options > Language in the window, or menu option 10 in the text screen. Each language is listed in its own words. `ForceEnglish` still wins. The menu prompts say 1 to 10.
- Pressing Ctrl+C twice within two seconds closes the text screen. Once still skips the question.

Every new string is translated into Spanish, French, Portuguese and German; one French and one Portuguese line were shortened to fit 72 columns.

Tests: splitting a plan, finishing some parts from the text screen and the window, all of them, a wrong answer, Skip on the notification, settings kept through delete, choosing a language and `ForceEnglish` over it, and Ctrl+C once and twice. 220 run here on Windows with Python 3.13: 218 pass and 2 are POSIX-only. The window with three tick boxes, one with `&` in it, was drawn and checked.

## 2026-10-03: a simulated week with five people, twice

Version 1.29.0. The owner's assistive technology checks of the window and the notification passed: Narrator, NVDA, JAWS, Magnifier at 200 percent and high contrast. The native speaker review of the translations passed too. Both are recorded in `docs/ACCESSIBILITY.md`. The owner then asked for five employees simulated by fresh agents, each with only a persona and a tool that drives the real window: a warehouse shift lead on a shared PC, an accounts receivable analyst in Portuguese, a support agent with ADHD, an HR coordinator in Spanish who checks privacy, and a developer who pokes at everything. Each ran a work week, then all five ran it again on the fixes. `docs/PILOT.md` has who found what.

Bugs:
- **I did it** marked the old plan done when the box had been edited. The words in the box are what's finished now. (Priya: "it marked the old plan as done and threw away my edit.")
- Saving a new plan while yesterday's question was still showing, then clicking Done, said "The other open window changed the plan, so its plan is kept." with no other window open. Saving a new plan now removes the question, and the old plan is kept for `same`. (Tom)
- Turning off the thought and tip said "Done. The thought and tip are off." while they stayed on screen. They go at once now; turning them on says they show next time. (Dana, Tom)
- Tab went right to left across the bottom buttons. They are in reading order now, with a test that every control is.
- The text menu named the reminder "open once a day at sign-in" and "Opens by itself at sign-in", though with the window it is a notification. It says "reminder when you sign in" now, unless the person chose the text screen. (Priya, Rafael, Tom)
- The text menu opened from the window said "Enter  Back to the last prompt"; it says "Enter  Close".
- "You have opened this 3 times in a row" counted days, not opens. It says days, in English and French. (Dana, Priya)

Changes:
- Save says "Saved." and leaves the window open, with "That looks like more than one thing" when it does; Enter again closes. In 1.28.0 it closed at once and two people couldn't tell whether it had saved. (Dana, Priya)
- Esc or Close with an edited plan asks "Save your plan before closing?". (Tom)
- Emptying the box and clicking Save asks "Clear today's plan?", the first way to drop a plan in the window. (Tom)
- After **I did it** the box is labelled "Next plan, if you want one:" and the button says Close, not "Not today". (Dana, Rafael)
- The cursor goes to the end of the plan instead of selecting it, so a stray key adds instead of replacing. (Priya)
- Options can show what is saved, in words with the file's location, and delete everything, without the black text menu. (Mónica, Rafael; then Dana, Priya and Rafael on the first version, which showed the raw file.)
- Done on the notification brings a short notification with a done line. (Priya: "it just disappeared. No little 'nice!' at all.")
- Done in the window or on the notification counts on the day it was said, which is the date the finished list shows. Three people read the plan's own date as wrong. (Mónica, Priya, Tom)
- The days-in-a-row message is off until someone turns it on, under Options or with menu option 3, and with it off the file keeps only the latest visit date, not 60 days of them. Files saved before 1.29.0 keep it on, since they recorded it as on. This was in `BACKLOG.md` as "revisit if real employees read it as being counted"; two of five simulated employees did, one of them twice. (Mónica: "To a coworker that reads as 'it counts my attendance.'") It is removed from the backlog.

Declined, with reasons in `BACKLOG.md`: a checklist of several plans, "partly done", Skip on the notification, public holidays, a different title, tips for shift work (`content.json` covers it), a warning at the 120-character limit, and keeping settings through Delete everything.

The pilot tool itself had three bugs, none in the program. Its windows took keyboard focus while off screen, so typing on the real desktop most likely landed in their plan boxes as "th", "s s" and "fix"; it now runs them on a desktop of its own. It couldn't click OK on a message box, so all five stalled on "Show what is saved" until it was fixed and they reran the step. And one sign-in in text-screen mode opened a real console; the owner's own data folder was checked and nothing was written.

TODO: the native speaker and assistive technology items are done, and the employee week was simulated twice. A real pilot stays, for when the organization is ready.

Tests: I did it with edited words, a refused number, Saved and the several-things note, the save result for each kind of input, clearing a plan, showing and deleting what is saved, the days-in-a-row message off by default with one date kept and on for old files, the reminder named by what it does in each mode, Enter closing the text menu opened from the window, the thank-you notification on Done only, the finished date, and the window's controls in reading order. 213 run here on Windows with Python 3.13: 211 pass and 2 are POSIX-only.

## 2026-10-03: a window with buttons, and a sign-in reminder

Version 1.28.0. The 1.27.0 review gave the console to a simulated new user, 64, accounts payable, 25 years of Outlook and Excel, who rated the chance of still opening it in two weeks at 2 out of 10: "a black window looks like an error", and typed words have to be remembered. `TODO.md` planned a window and a morning notification. Each open decision went back to the same simulated user, and their answers decided it.

The window:
- The Start menu shortcut now runs `pythonw.exe -I hello.py --window`, which opens a standard Windows dialog: "Hello, world!" in large type, the date, the thought and tip, one box for today's plan, and buttons. No console appears. Asked to choose between this and a custom Tk window, the simulated user picked "exactly like the other small Windows boxes", because if it looks different "I'll think something's wrong with my computer".
- Yesterday's plan comes with **Done**, **Not yet** and **Skip**. Not yet keeps it for today, as Enter does at the text screen. Finishing counts on the plan's own day.
- Enter saves the plan and closes ("like clicking OK. If the window stays open I'll wonder if I did it right"). **Not today** closes without one, which the simulated user asked for so a skipped day "doesn't feel like homework". A command word or a number in the box is refused with the same message as the text screen, and the window stays open.
- With today's plan set, **I did it** finishes it and the box takes the next one.
- **Options** turns the sign-in reminder on or off, hides the thought and tip, switches to the text screen, or opens the text menu for everything else.
- It is drawn with `ctypes` from a dialog template built in memory, with the current Windows look, per-monitor DPI and the system colours, so high contrast applies. A PC where it can't be drawn gets the text screens in a console instead.

The reminder:
- After the first plan in the window, it asks once: "Want a reminder when you sign in?". The simulated user: "Ask me once, nicely."
- With it on, the sign-in launcher runs `pythonw.exe` instead of `cmd.exe`. At the first sign-in of the day, and only when there is a plan to ask about, it shows a Windows notification: "Last time you planned: ... Did you do it?" with **Done** and **Not yet**. A click answers it and nothing else opens. With no plan it stays quiet ("too many pop-ups and I'll start ignoring all of them"). It comes once a day at most, and not after the window was opened that day.
- The notification is shown through Windows PowerShell with the XML passed as base64, under the name `hello-world`, registered in `HKCU\Software\Classes\AppUserModelId`. Its buttons open `hello-world:done` and `hello-world:notyet` links, registered for the user, which run `hello.py --answer` and accept nothing else. Where PowerShell can't show it, such as in Constrained Language Mode, the window opens at sign-in instead.

The text screen:
- `hello.cmd` runs it as before. Menu option 9 and the window's Options switch the Start menu between the window and the text screen, saved as `"text": true` in `notes.json`. The new `UseTextScreen` policy sets the text screen for everyone, with ADML strings in all five languages.
- With the text screen chosen, the window and the sign-in launcher open the text screens in a console, so screen reader users keep the checked path.
- `notes.json` can also hold `"notified"`, the date of the last reminder.

Every new string is translated into Spanish, French, Portuguese and German. `docs/ENTERPRISE.md` lists the new Run value and registry keys for persistence allow-lists. `docs/ACCESSIBILITY.md` has a section on the window and says it hasn't been checked with assistive technology yet.

The simulated user's rating with the window and reminder: 7 out of 10. "I'll still forget about it some weeks, but I would open it." They also said not to add a language until someone asks, so that stays in `TODO.md` under "When an organization asks".

Tests: the window's answers, saves, refusals and "I did it" through the `Visit` class it draws, the reminder once a day and only with a plan, valid notification XML with an escaped `&`, the `--answer` links and refused ones, menu option 9 and the policy, the saved `text` and `notified` fields, the Run value and the reminder keys in a test registry key, and on Windows the window opening and closing by itself in every language, with and without a plan to ask about. CI also checks that the installed shortcut targets `pythonw.exe --window` and that the bundled embeddable Python draws the window. The window was also drawn and captured here on Windows 11 at 100 percent in English and German, after Done and after Not yet, and a French notification was shown with a plan containing `<` and `&`.

## 2026-10-03: plain answers, and the menu where people look for it

Version 1.27.0. A review of 1.26.0 drove the screens with typed answers in all five languages, then gave a two-day transcript to a simulated new user: 64, accounts payable, 25 years of Outlook and Excel, never opened a command prompt. They rated the chance of still opening it in two weeks at 2 out of 10. The biggest reasons were the console window itself and the command words. The fixes here are the ones the text screens can make. The window is planned in `TODO.md`.

Bugs from the review:
- A menu number typed at the plan question was saved as the plan. Typing `m` there said "The menu comes at the last prompt", asked again, and a following `1` replaced "Write the report" with "1". A plan with no letters, only digits and punctuation, is now refused with "A plan needs a word or two, so nothing was saved." A plan like "Call 3 clients" is still fine.
- In English, `s`, `o` and `j` finished a plan, because the shared word table held the one-letter yes of Spanish and Portuguese, French and German. Someone typing `s` for "skip" at "Did you do it?" got "Nice. It is good to finish something.", and a finished plan is never offered back. One-letter yes words now work only in their own language, in `LETTER_YES`. Whole words such as `sí`, `oui` and `ja` still work everywhere.

From the simulated user:
- `ok`, `okay`, `yup`, `sure`, `did it`, `i did`, `done it` and `finished` now count as yes at "Did you do it?". `ok`, `okay`, `yup` and `sure` also count at the other yes-or-no questions, along with `vale`, `claro`, `d'accord` and `klar`. `nah`, `not really` and `not done` count as not yet. "ok" was refused before, which "made me feel like I was taking a test".
- `menu` at the plan question opens the menu, rather than saying where the menu lives and asking again. The sign-in offer waits for another visit then, so it doesn't come between the two.
- "That was not one of the choices: "ok"." is now "Sorry, "ok" is not one of the choices."
- The last prompt no longer names `q`: "Type done, plan or menu, or Enter to close". Nobody could tell what `q` meant. `q`, `x`, `quit` and the rest still close.
- The welcome said "IT staff could read them, so skip private details", which made a wellbeing tool read like monitoring. It now says "Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks." The full statement of who can read the file stays in the README, option 1 and `docs/ROLLOUT.md`.
- "Type menu at the last prompt" is now "Type menu at the end". The simulated user didn't know what a prompt was.

Every changed string is translated into Spanish, French, Portuguese and German, and the 72-column and no-English tests cover them.

Tests: one-letter yes per language, the natural yes and no words, a number refused as a plan, `menu` at the plan question opening the menu and leaving the plan alone, and `q` working though it isn't named. 192 pass here on Linux with Python 3.11, and ruff is clean.

## 2026-10-03: French, Portuguese and German

Version 1.26.0. The owner asked to keep going with languages after Spanish shipped. French, Brazilian Portuguese and German are the most common Windows display languages after English and Spanish in large multinational companies, so all three were added.

The translations are data now, not Spanish-shaped code. Each language is a `LANGUAGES` block at the end of `hello.py` with its text table, thoughts, tips, done lines, day and month names, and date format. `language()` maps the Windows display language to a block through `WINDOWS_LANGUAGES`, and `ForceEnglish` still wins. Adding a language is one block, its command words, its Windows language ID and an ADML file.

Each language was translated from the English with the reviewed Spanish as a second reference, then reviewed by a simulated native speaker who walked the screens with the visit tool. The French uses vous, the German Sie, and the Portuguese você. All three stay gender-neutral where the English is. Reviews found and fixed about 27 problems in the Portuguese, 40 in the French and 40 in the German, most of them literal English phrasing. The real errors were a German accusative ("Gedanke" for "Gedanken"), a German line that read as if the program would switch the reminder on by itself, and French and Portuguese lines where "il" or "ele" pointed at nothing.

The French review found three things that only a code change could fix:
- The menu's last line printed the English key name "Enter". It is now translated: "Entrée", "Eingabetaste".
- Dates in the finished list were followed by a hard-coded ": ". French needs " : ", so the label is translated too.
- The first of the month reads "1er" in French and "1º" in Portuguese.

Command words now live in one table and work in every language: done is also `hecho`, `fait`, `feito` and `erledigt`, quit is also `salir`, `quitter`, `sair` and `beenden`, and same is also `repetir`, `reprendre` and `wieder`. A test checks that no word means two things. The German screens put „…" around command words so "wieder" doesn't read as "again", so typed words now ignore quote marks around them.

Group Policy templates come in `fr-FR`, `pt-BR` and `de-DE` too. The `ForceEnglish` description names all four languages. The topic list that keeps two lines about the same body part off one screen has stems in every language.

Tests now loop over every language: every screen string translated, placeholders and prompt endings kept, raw lines within 72 columns (66 for menu lines), the lists the same length as the English, a whole day shown with no English left, the done word of each language finishing a plan, the help and menu fitting 72 columns, and an ADML per language with every string.

Declined, with reasons in `BACKLOG.md`: regional variants, scripts a console can't draw reliably, and a file per language.

Tested here: 187 tests pass on Windows 11, Python 3.13, and ruff is clean. The menus and a first day were checked by eye in each language with the visit tool.

## 2026-10-03: organization content, Spanish, and JAWS

Version 1.25.0. The owner reported that the JAWS check passed, asked for a sample content file for testing, and asked for a second language, leaving the choice open. These were the three "Next to build" items from the product review of 1.23.0.

Product review, item 1, "A content file the organization supplies": `tools\build-package.ps1 -ContentFile` adds the organization's thoughts and tips to the package as `content.json`, listed in `SHA256SUMS`, so the package hash covers it. The build checks the file with the Python it ships and stops on any problem. `install.ps1` installs `content.json` only when `SHA256SUMS` lists it, or, from a clone, only when the reviewed commit has it, and checks it again after the test run. `hello.py --check-content FILE` lists what is wrong: the shape, 7 to 200 lines per list, 10 to 120 characters per line, no control characters, no links or addresses, and no dates or month names in English or Spanish, so the file can't become an announcement channel. The program falls back to its own lists when the file is missing or breaks a rule. `examples/content.json` is a sample with 20 thoughts and 20 tips about teamwork and work habits. A CI step builds a package with it, checks that an edited `content.json` is refused, and checks that the installed program shows the sample tips. `todays_pair()` now stops after one pass through the thoughts, so a list where every thought shares the tip's topic can't loop forever.

Product review, item 2, "A second language": Spanish, the most widely spoken language after English among likely users. The program shows Spanish when the Windows display language is Spanish. A new `ForceEnglish` policy keeps it in English, with ADMX and ADML entries and a Spanish ADML in `policy/es-ES`. Every screen string goes through `tr()`, keyed by the English text. The Spanish table, the 101 thoughts, 100 tips and done lines, the help and the dates ("lunes, 5 de octubre de 2026") are in `hello.py`, so the install still copies one file. Spanish command words work in both languages: `hecho`, `s`, `sí`, `menú`, `ayuda`, `repetir`, `salir`, `todo`. Translations avoid gendered forms where the English is neutral. A simulated native-speaker review walked the screens and found 39 phrasing problems, among them "para ahora no", "Hecho." used both as a confirmation and as the command word, and a gender clash in the error message. All 39 were fixed. New tests check that every translated string has Spanish, that the placeholders match, that no screen string skips the translation, and that lines printed without wrapping fit the window.

While translating, three English messages turned out to print as one line of over 72 characters instead of wrapping: "That looks like a command, not a plan...", the saved-plan notice, and "The menu comes at the last prompt...". They and the other single-sentence messages now wrap to the window, which matters at high magnification.

Product review, item 3: `docs/ACCESSIBILITY.md` records the owner's JAWS pass on 1.24.0.

`TODO.md` had a backspace byte in place of `\b` in `tools\build-package.ps1`, left by an earlier editing script. Fixed.

Declined, with reasons in `BACKLOG.md`: Spanish for `--plain` and `--check-content`, `retomar` for `same`, content files per language, and a per-person language setting.

Tested here: 184 tests pass on Windows 11, Python 3.13, and ruff is clean. A content package built locally, and a bad content file stopped the build with its problems listed. The real install of the content package runs in CI, since this shell isn't elevated.

## 2026-10-03: signed packages, a records policy, and a rollout kit

Version 1.24.0. The owner reported that all pending manual tests passed on 1.23.0, including the NVDA check of the prompts and a pilot-ring deployment, and asked for the organization's side to be taken as far as possible. A product review of 1.23.0 ranked what to build next.

Signing: `tools\build-package.ps1 -CertificateThumbprint` signs `install.ps1` and `uninstall.ps1` with SHA-256, with an optional timestamp server, checks both signatures, then hashes. A new CI job creates a throwaway code-signing certificate, trusts it, builds a signed package and an unsigned one, and sets the runner to AllSigned. With no `-ExecutionPolicy Bypass` it checks that the unsigned package is refused, the signed one installs and runs, the installed uninstaller keeps its signature, and the uninstall works.

Product review, item 1, "Records and works-council controls": a new `DisablePlans` policy. With it, the program never asks for or follows up a plan, the last prompt and menu say plans are turned off, and plan text, finished plans and the done count are dropped from the file at each person's next visit. With `HideDaysInARow`, only the latest visit date is kept. The ADMX and ADML have the new setting.

Product review, bugs:
- "When the HideThoughtAndTip policy is on, the first-run welcome still says 'Each day you get one thought and one small thing to try'". The welcome is now built from what this PC shows.
- "The welcome ends with 'Type menu for the options', and the very next prompt rejects menu". Typing menu at the first plan question now says where the menu is and asks the plan question again, and the welcome says "Type menu at the last prompt".

Product review, items 2 and 3: `docs/ACCESSIBILITY.md` records how the program meets accessibility expectations and how each check was done, including the owner's NVDA pass. `docs/ROLLOUT.md` has an announcement email, an employee FAQ, and a page for privacy and records reviewers. The NVDA pass settles the `>` question in `BACKLOG.md`: the prompts stay as they are.

`TODO.md` now lists only open work. The panel and money reviews moved to `docs/PANEL-2026-10.md` as a record.

Tested here: all 170 tests pass on Windows 11, Python 3.13, and ruff is clean. On CI, the new signed job and the unsigned install job both pass.

## 2026-10-03: ready for enterprise deployment: an offline package, Group Policy, and a launcher that can't be hijacked

Version 1.23.0. The owner asked for the program to be ready for enterprises of 5,000 users and more. Two reviews ran first: an enterprise endpoint architect's gap review and a security threat review for that setting.

Deployment, from the architect's blockers:
- "The install can't be packaged": `install.ps1 -PackageHash` installs from an offline release package with no Git and no internet. The package hash is the SHA-256 of `SHA256SUMS`, which lists every file. All are checked before anything changes, and Python is also checked against the pin in the verified `install.ps1`. `tools/build-package.ps1` builds the package and a CycloneDX bill of materials, the same way every time, so anyone can rebuild a release from its commit and compare hashes. A new `release.yml` publishes the package for each new version on main.
- "Upgrades fail whenever the program is open": the CI install test showed this isn't so. Windows renames a folder that a running program came from, so the upgrade goes ahead, the open window keeps its old copy, and the next install removes it. What does block the rename is a file held open without delete sharing, as antivirus or a backup agent can do. Any rename that still fails after retries now exits 1618, which Intune and MECM retry later, and the uninstaller does the same with nothing changed.
- Detection: a first install that fails at step 6 removes its Apps entry and shortcut, so detection doesn't count it as installed.
- Logs go to `%WINDIR%\Logs\hello-world`, admin-only and created that way before anything is written. Install and uninstall results go to the Application event log (events 1000 to 1003). This replaces the copy of the log in the install folder.
- Both scripts start themselves again in 64-bit PowerShell when Intune runs them in 32-bit. Windows 11 on ARM64 is allowed. An older version is refused unless `-AllowDowngrade` is passed, and `-Publisher` names the publisher. The Apps entry records the package hash or commit and the bundled Python version.
- OpenSSL and SQLite are removed from the bundled Python after it's unpacked, since the program uses neither and scanners would flag every PC.
- Group Policy: `hello.py` reads `DisableSignInLauncher`, `HideThoughtAndTip` and `HideDaysInARow` from `SOFTWARE\Policies\hello-world` in HKLM or HKCU. ADMX and ADML templates are in `policy/`, and a test keeps them in step with the program.
- `docs/ENTERPRISE.md` covers Intune and MECM settings, detection, return codes, signing and application control, what EDR will see, VDI and roaming profiles, data handling, the security model, keeping Python patched, and help desk answers.

Security, from the threat review:
- Medium, "any standard user can break uninstall for everyone" and "per-profile operations check only the last path component": the sign-in launcher is now a value named hello-world under the user's HKCU Run key. It runs `cmd /d /c if exist "...\hello.cmd" start ...`, so it starts the admin-only install and does nothing once that's gone. The uninstaller no longer has to clean launchers out of every profile. An old Startup `.cmd` becomes the Run value the next time its owner opens the program. For anyone who never does, the uninstaller's sweep deletes only a plain file with the exact name, after checking every folder on the path for a link. It handles one profile at a time and runs before anything else is removed.
- The uninstaller's `-RemoveNotes`, added in 1.22.0, is withdrawn: deleting inside user profiles as an administrator can't be made safe against a link a user controls. `BACKLOG.md` says why.
- "Git config the admin process doesn't control can run code": a clone install sets `GIT_CONFIG_GLOBAL=NUL` and `GIT_ATTR_NOSYSTEM=1`, which Git 2.51 honors. The test run goes through `cmd /d`, and the Archive module loads from `$PSHOME` by full path.
- "Any user can block an upgrade or half-break an uninstall": the uninstaller renames the install folder aside first, so an open file stops it before anything changes.
- "The launcher works as a persistence vector": fixed by the Run value above. `docs/ENTERPRISE.md` gives EDR teams the exact value to allow.
- The review's point on `release.yml` publishing a hash that vouches for itself: the package is reproducible, and the guide says to rebuild from the reviewed commit and record that hash in the change ticket.

CI: a new step builds the package and really installs it on the Windows runner. It checks the Apps entry, the stripped libraries, the log and the event. Then it reinstalls, refuses a wrong hash and a downgrade, upgrades while a hello-world process runs and clears the old copy on the next install, returns 1618 from both scripts while a file is held open, and uninstalls.

Declined (see `BACKLOG.md`): deleting notes from the uninstaller, and signing in this repository. Still open in `TODO.md`: signing with the organization's certificate, a pilot ring through Intune or MECM, an NVDA check, and pinning the shared kit's workflows.

Tested here: all 167 tests pass on Windows 11, Python 3.13, including the HKCU Run value and the move from an old launcher against a throwaway registry key. ruff is clean. All three PowerShell scripts parse in Windows PowerShell 5.1, and the package builds with a stable hash. The CI install job is the first real run of the installer and uninstaller changes.

## 2026-10-03: no attendance log, a lock against lost deletes, prompts that fit a magnified window

Version 1.22.0. Three sources: a security and robustness review of `hello.py`, a review of the installer, CI and tests, and a third simulated pilot round with three new people (`docs/PILOT.md`).

Security and robustness review:
- Medium, "a reset in another window can be undone by a save already in progress": a small `notes.lock` is now held while any change reads and writes the file, and while Delete everything runs. A second process can't take it meanwhile, and a test checks that with a real second process. The lock gives up after about five seconds, so a stuck window can't freeze another one. The backlog's "no lock file" entry is updated.
- "epoch is the one string from the file that is never cleaned": only hex is kept.
- "A missing file looks like 'deleted in another window'": a file that is gone, deleted by hand or set aside as damaged, no longer blocks the next save. Only a changed marker means Delete everything ran.
- "Emoji newer than the pinned Python's Unicode data are silently removed": `tidy()` now drops only controls, format marks, private-use and surrogate characters, and keeps unassigned ones. "Combining-mark floods" are capped at four per letter.
- "The launcher's temp file is written inside the Startup folder": it has the process ID in its name, and stale ones are cleared on turning the reminder on or off, and on uninstall.

Installer, CI and tests review:
- Medium, "the step 6 rollback stops halfway when step 6 fails before the shortcut code runs": a bug from round 46. The shortcut backup is now set before anything in step 6 can fail. A stale backup is cleared first and removed after a rollback too.
- "If the second rollback rename fails, nothing is left at $dir": the new install is put back instead.
- The restored shortcut is checked for admin-only access, like a new one.
- "Ctrl+C in step 2 leaves the admin's window changed": the Git environment changes now happen inside the try whose finally restores them.
- "-Quiet prints more than the help text says": the SHA-256 line is quiet now, and the help says a failure adds where the log is.
- "Every user on the PC can read the copied log": the copy is admin-only.
- Medium, "CI never runs the installer's logic": a new step reads the pinned Python URL and hash from `install.ps1`, downloads the zip, checks the hash, and runs `hello.py --plain` and `--version` on it. pytest and PSScriptAnalyzer are pinned, checkouts drop their token, and jobs time out after 15 minutes.
- Tests: the pair test now checks real pairs, the two-process test shows window A's errors, Ctrl+C skipping one prompt has a test, and every temp folder the tests make is removed at exit (71 calls).

Simulated pilot, third round:
- The file now keeps visit dates for 60 days, not 400, so it can't read as an attendance record (Priya). The "That is N done so far" tally after each finish is gone; the count stays in option 1. Option 1 says whether the sign-in opening is on. `uninstall.ps1` asks whether to delete every user's notes, and `-RemoveNotes` does it without asking.
- Prompts longer than the window are wrapped, with only the last line left for the answer, so the choices are never off a magnified screen (Glenn). "When did you finish it?" lists the days since the plan by number, because `y` there clashed with the `y` just typed (Glenn, Amara). "Still open since ..." puts the plan on its own line.
- Plain words for the praise lines, "Left as it was" (now "Your plan is still open."), and nine thoughts and tips Amara quoted. The in-a-row line is called the days-in-a-row message.

Declined (see `BACKLOG.md`): the days-in-a-row message off by default, and removing the program without an administrator. The README now says how to stop using it without IT.

Tested here: all 162 tests pass on Windows 11, Python 3.13, under both pytest and the plain runner, and ruff is clean. Both PowerShell scripts parse in Windows PowerShell 5.1 and are ASCII. The new CI step ran on this PC: the pinned zip's hash matched, and 1.22.0 printed its greeting and version on that Python. Not tested: the installer and uninstaller themselves, including the reworked rollback and `-RemoveNotes`.

## 2026-10-03: a deleted plan stays deleted, q closes from every question, a late yes asks which day

Version 1.21.0. Two sources this round: a fresh correctness review of the code, and the simulated pilot's second round on 1.20.0 (`docs/PILOT.md`).

From the review:
- Medium, "a plan deleted in another window comes back": answering y at "Did you do it?" after another window ran Delete everything wrote the old plan back under the new marker. The failed save now takes the plan from the state, not from a copy held earlier. Test: a delete during that question.
- "A second identical finish on the same day loses its row": `commit()` now counts finished rows as a multiset, so the same words finished twice in a day are two rows and a count of two. Test.
- "'q closes from any question' is false": `q`, `x` and `close` now close from every question. That covers the menu, a plan prompt, option 7's number, and the delete confirmation, where `q` also cancels. Typing `close` at the first plan question no longer saves "close" as the plan. One catch around the last prompt replaces the menu-only one. Tests for each.
- "HELP says done lists your last 7": it says 3, and it says option 8 hides the thought and tip.
- "The installer's step 6 rollback can leave things worse": the old Start menu shortcut is copied into the admin-only setup folder before it's overwritten, and restored on rollback. The failed new folder is renamed to `.failed` instead of deleted, so a file held open can't leave a half-deleted folder in the old install's way. A rollback that fails reports itself and keeps the original error. The next run and the uninstaller clear `.failed`.

From the pilot's second round:
- A plan confirmed days later was dated to the plan day (Marcus, Jun). A plan more than a day old now asks once which day it was finished: Enter for the plan's day, `y` for yesterday, `t` for today.
- A typo fixed with `plan` came back as "Earlier plan" (Jun). Changing today's plan replaces it; only a plan from an earlier day is kept for `same`.
- A second open the same day skipped an unanswered question (Sam). The question is asked until answered, and two Enter skips stop it. The plan then shows as "Still open from ..." with `done` offered. The skip count lives inside the plan.
- The finished list after every yes was too much (Ruth, Dana). A yes gets the praise and the count; the list comes with `done`, always under "Finished lately:".
- Menu option 8 hides the thought and tip (Dana), saved as `tips`. Forget names the plan it removed (Jun). A plan joined with "and", "&" or "+" gets one line that finishing the first part still counts (Sam). The first-day welcome is one paragraph (Ruth). The count reads "That is 2 done so far." (Dana).

Declined (see `BACKLOG.md`): closing right after `done` and a new plan, and a `same` that knows the parts of a plan were done separately. The `>` question still waits on a real NVDA check.

Tested here: all 153 tests pass on Windows 11, Python 3.13, under both pytest and the plain runner, and ruff is clean. Both PowerShell scripts parse in Windows PowerShell 5.1. Not tested: the new rollback path in a real failed upgrade.

## 2026-10-02: the pilot's round. Finished plans stay finished, a yes is answered at once, and q closes from anywhere

Version 1.20.0. A simulated 30-day pilot (`docs/PILOT.md`) ran five simulated employees, one of them an NVDA user, through the real 1.19.0 from 5 October to 3 November. This round answers what they found. The owner also ran the spare-PC gate for 1.19.0, and it passed; `PLAN.md` records it.

Found while building the pilot's tool: on the first visit, after the sign-in question, the last prompt dropped `done`. The offer re-reads the file, which replaced the plan the prompt was checking for. The tests ran with no Startup folder, so the offer never came up there. `daily()` now picks up the plan again after the offer, and a test with a Startup folder covers it.

From the pilot, by how many of the five hit it:

- "Earlier plan" offered back a plan they had just finished (all five). `finish_plan()` no longer keeps the words for `same`, and drops them if `same` held the same plan. `same` now only brings back a plan that wasn't finished.
- Two "not yet" answers put a plan away when they were waiting on someone else (four, while Sam wanted it sooner). The `waits` count is gone. A kept plan now carries `since`, the day it was first set, and the two-week cleanup counts from that date. A plan can wait as long as it needs, and one carried for two weeks still goes.
- A yes to "Did you do it?" got no answer until after the next question (four). A yes is now saved at once and answered with the praise and the last three finished plans, the same as `done`.
- A finished plan was dated the day it was confirmed (three). It's now dated the day the plan was for.
- A Friday off broke the "in a row" line, though the README said days off don't (three). `in_a_row()` now allows a four-day gap.
- The thought and the tip were both about shoulders on one day (three). `todays_pair()` moves the thought on when it shares a body topic with the tip, and a test checks every pair across a full cycle.
- The menu was read again after every choice, and Help repeated it (Ruth, Jun). The menu is listed once, `m` lists it again, and Help explains `done`, `plan`, `same`, "not yet" and `q`.
- A full file path was read out (Ruth, Sam). The menu summary says "Saved in your own user folder", and turning on the sign-in opening says "choose option 2 in the menu" without a path. `--stats` keeps the path for IT.
- The sign-in question came back three days running (Jun). It's asked once.
- `q` didn't work at the yes or no questions (Sam). `q` now closes from any question in the morning flow, the menu included, and the visit still counts.
- Wording (Dana, Ruth): "Cleared. Type same at a plan prompt if you want it back.", "it asks next time you open this", "Earlier plan (for same)", and two thoughts that assumed afternoon or a quiet desk.

Declined (see `BACKLOG.md`): ending prompts in something other than `>`, until a real NVDA user confirms it's read as "greater", and reaching people on a site laptop, which is an install question.

Tested here: all 144 tests pass on Windows 11, Python 3.13, under both pytest and the plain runner, and ruff is clean. I read a real day-2 screen: the yes is answered before the thought, dated the day before, and the finished plan isn't offered back. Not tested: a real NVDA pass on the new prompts.

## 2026-10-02: review rounds keep running

No code change, so the version stays 1.19.0. The owner overruled the panel's "Stop the review rounds" item and the kill metric's "freeze the program": the project exists for steady improvement through review, and the rounds cost nothing. `PLAN.md` now says the rounds keep running on their schedule, and a weak pilot steers what the next rounds work on instead of freezing the program. `TODO.md` drops "turn off the schedule", and `BACKLOG.md` records the decision.

## 2026-10-02: the panel's round, an upgrade that fails at step 6 puts the old install back

Version 1.19.0. This round answers `TODO.md`, the result of a six-voice panel (engineer, employee, salesperson, profit maximizer, IT admin, accessibility user) on the backlog.

Content (panel item 3, "Give an 'or' option to every tip and thought that assumes sight", "Replace some stretches with practical work tips"): nine tips and thoughts that assumed sight now offer another way in. Six stretches and eye exercises became work tips, such as pinning the most-used document, muting a group chat, or learning one shortcut. There are still 100 tips and 101 thoughts.

Prompts (item 4, "End every prompt with 'Enter to <outcome>' and drop '='"): every prompt now ends by saying what Enter does, and no prompt uses "=". A test keeps "Enter = " out of the code. The welcome and the expired-plan message are wrapped by paragraph by a new `para()`, not broken by hand mid-sentence. Both places that save a plan say "Saved. Type done when you finish it, or it asks tomorrow." The first run opens with "Press Enter at each question to skip it, and once more to close. That's it." and says everyone sees the same thought and tip on the same day.

Item 5, "After `done`, show the last three finished plans": after `done` and on welcome back it reads out three, and says option 1 lists all of them. Item 6, "After two 'not yet' answers, stop asking": the plan carries a small `waits` count, and the second "not yet" puts it away as `same` with a message. The count sits inside the plan, so `commit()` has no new key to merge.

Item 7, engineer cleanups: a new test runs two real windows as separate processes. Window A waits at "Did you do it?" while window B finishes the same plan, then A finishes it too. The test checks one row, a count of one, A's new plan, and the "other window" message. It passed on its first run. Another test freezes the set of saved keys, so a new key fails it until someone writes its merge rule. Visits dated after today are now dropped on load instead of carried in a `future` list, which removes that key and half of `file_form()`.

Item 8, "Cut the employee part of the README roughly in half" and "Keep the 'what is saved' paragraph in one place": the employee section went from about 88 lines to about 55. `PLAN.md` and the why-doc now link to the README's list of what is saved instead of keeping their own copies.

Installer (item 2, "Defer `Remove-Tree $old` and roll back when step 6 fails, and name the open windows in the rename error"): the old install now stays as `.old` until step 6 has worked. If step 6 fails during an upgrade, the new folder goes, the old one comes back, and the old Apps entry is restored with its value types. A first install that fails there keeps its files, as before. A rename that keeps failing names how many hello-world windows are running from the install folder. From the panel's "Later" list, which IT wanted now: the Apps entry records `Commit` and `InstallDate` and gets a `QuietUninstallString`, and a copy of `install.log` stays in the install folder, so deleting the setup folder no longer loses it. It goes in the install folder rather than ProgramData because the install folder is already admin-only.

Item 1, "Stop the review rounds and run the pilot": `PLAN.md` now has the stop rule, a Pilot section with an assistive-tech user, in-person check-ins on day 14 and day 30, and the kill metric. No routine on this account runs the review rounds, so turning off that schedule is left to the owner.

Tested here: all 137 tests pass on Windows 11, Python 3.13, under both pytest and the plain runner, and ruff is clean. `install.ps1` and `uninstall.ps1` parse in Windows PowerShell 5.1 and are ASCII. The rollback's registry restore was run against a throwaway key under HKCU, and the string and DWORD values came back with their types. Not tested: the installer itself, the step 6 rollback on a real upgrade, and a standard-user smoke run. `TODO.md` lists them for a spare PC.

## 2026-10-02: backlog sweep, tests in CI on Windows, --version, a blocked save is tried again

Version 1.18.0. The owner asked for every backlog entry to be fixed. The backlog had about 150 entries from 43 rounds, many repeated. Each was checked against the current code. Fixed now:

- A save that Windows refuses for a moment, because antivirus or another window has the file open, is tried again up to five times (Round 39 lead 2a, "Retry in `save()` on Windows file locks"). Test: a replace that fails twice, then works.
- `--version` and `-v` print the version (Rounds 32, 33 and 37, "`--version`"). The version lives in `hello.py`, and a test keeps it equal to `VERSION`.
- `--help` lists the exit codes (Round 40 lead 15, "`HELP` exit codes").
- Menu option 1 says when the file could not be read and the summary may be out of date (Round 28 L1, "Say 'could not read' in option 1 when the file is locked").
- The sign-in launcher is written to a temp file and moved into place, so a sign-in never runs half of one (Round 33, "launcher atomic rewrite").
- Four tips no longer assume sight or hearing (Rounds 39 to 41, "Tips that assume sight or hearing"). The glance at something green, the smile at a plant, the pleasant sound and the wave on a video call now offer other senses or plain words.
- `uninstall.ps1` waits for its elevated copy and exits with its code, so a `-Quiet` run from a management tool sees a failure (Rounds 31 to 33, "uninstall `-Wait` and exit code"). It also skips a user's Startup folder that is a link (Round 38, "Junction-safe delete of the sign-in launcher").
- A test that changed `shutil.get_terminal_size` for every later test now puts it back (Round 40 lead 16, "test hygiene for `get_terminal_size`").
- New `.github/workflows/tests.yml` runs both test runners on Windows and Linux with Python 3.11 and 3.14. It also parses both scripts under Windows PowerShell 5.1 and runs PSScriptAnalyzer at error level. Its actions are pinned to a commit. This answers the Windows CI, Python 3.14, PSScriptAnalyzer and SHA-pin entries from Rounds 26 to 40. Those entries were declined only because the scheduled routine could not change `.github/`.
- Ruff flagged a `zip()` without `strict=` in the in-a-row count. Both lists always have the same length, so `strict=True` is right.

Taken out as already done by a later round: the temp-file sweep, `fsync`, re-reading before a menu save, unknown keys, two-window saving, the cut-plan notice, non-zero exit codes, wrapping to the window, `GetConsoleMode` argument types, Windows test isolation, the `interactive()` check on Windows, the 101st thought, the finished-plans list, the screen-reader pass and the Windows install pass.

What is left in `BACKLOG.md` is grouped by why it stays: against the design on purpose (no network, no scores, no default reminder), claims that were wrong, GitHub settings and owner process, and installer changes that need an administrator test run on a spare PC. Two entries still need someone else's hands. The three shared kit workflows need their pins changed where the kit is kept. The installer items need an admin test run.

Tested here: all 131 tests pass on Windows 11, Python 3.13, under both pytest and the plain runner, and ruff is clean. `uninstall.ps1` parses in Windows PowerShell 5.1. The new workflow is checked by its first run on this branch. Not tested: `uninstall.ps1` elevated for real.

## 2026-10-02: the sign-in launcher works from a folder with brackets, stale temp copies are swept

Version 1.17.0. Round 43 review (`reviews/round-43.md`), one reviewer, 2 High, 1 Medium, 1 Low, 3 Part 2 items.

Launcher. Finding 1.2, "If the directory path where hello-world is installed contains characters like ) or , (e.g., C:\Tools (x86)\hello-world), execution of hello-world-daily.cmd inside cmd.exe fails": true, though not for the reason given. `start` runs a `.cmd` through `cmd /k`, and `cmd` strips the outer quotes from a command line with `(` or `@` in it, so the path broke at its first space. A test on Windows 11 confirmed it: the old launcher never opened hello from `Tools (x86), a=b @~ c`, and the new one does. The launcher now passes the folder with `start /d` and runs `hello.cmd` by name, so the folder never reaches `cmd /k`. The installed copy under `Program Files` was never affected. The suggested fix (`start ""` and doubled quotes) was not used, because quotes are already refused and were not the problem. A `.lnk` would need COM, which the bundled Python does not have. Test: the launcher line for a folder with brackets, a comma, `=`, `@` and `~`.

Temp copies. Finding 1.4, "standard startup and normal operations do not prune stale .tmp files": every save now removes `notes.json.*.tmp` copies over a day old first. A younger one may belong to another window's save in progress, so it is left. Test: a two-day-old copy goes and a new one stays.

Finding 1.1, "unknown or arbitrary JSON keys present in notes.json are loaded into state": not so. `load()` builds a fresh state and copies in only the keys it knows, each type-checked, so an unknown key never reaches `commit()`. No code change. A new test feeds a file with an unknown nested key and a wrong type for every known key, and checks that the program runs, `--stats` works, and the unknown key is gone from the file.

Part 2 item 3, "Provide explicit status warnings when active plan state changes are made by another background window": already done in Round 42. A save says "The other open window had also finished a plan." or "The other open window changed the plan, so its plan is kept."

Declined (see `BACKLOG.md`, Round 43): finding 1.3 and Part 2 items 1 and 2.

Tested here: all 126 tests pass on Windows 11, Python 3.13, under both pytest and the plain runner. The launcher was also run for real from `Tools (x86), a=b @~ c` and from a plain folder, old line and new. Not tested: the installed copy at a real sign-in, and ruff.

## 2026-10-02: record the install and two-window pass on 1.16.0

No code change, so the version stays 1.16.0. Round 42 Part 2 item 2, "Prove the two-window story on a real console": the owner ran 1.16.0 in a sandbox through an install, a reinstall, an interrupted install, an uninstall, and two real windows that both finished a plan while one used Delete everything. All passed. It is out of `BACKLOG.md`. `PLAN.md` now has a "Tested" section with the gate to run again before a release that changes saving or the installer, and the why-doc matches. Three checks are not recorded either way: console input outside ASCII, the shortcut's pause line, and removing launchers from several user profiles.

## 2026-10-02: delete everything sticks across windows, tidying a plan never overwrites the other window's, a repeated finish counts once

Version 1.16.0, still. Round 42 review (`reviews/round-42.md`) of the unmerged Round 41 branch, one reviewer, no Critical, 2 High, 5 Medium, 6 Low, 6 Part 2 items. 1.16.0 was never tagged, so both rounds ship as one release.

Delete everything. High 1, "'Delete everything' is undone by the other open window", and Part 2 item 1, "Make delete stick, then say what survived": Delete everything now leaves `notes.json` holding only an empty state and a new random `epoch`. `commit()` refuses to save when the file's epoch differs from the one this window read, says why, and leaves this window empty too. So a window left open at a prompt can't write deleted notes back. The delete ends with "Another open hello-world window cannot put it back.", or says to close the other windows when the marker could not be written. Tests: a delete in one window, then a save from the other, then a later save from the deleting window.

Saves from two windows. High 2, "The opening screen records clock cleanup as this window's edit": a plan the opening screen only tidied (a future date made today, a plan over two weeks old cleared) is now a soft change. `commit()` applies it only when the other window has not changed the plan meanwhile, and says so when it keeps the other window's plan. Medium 3: `--streak` now saves through `commit()`. Medium 6: menu option 2 and the morning save call `undo()` when the save fails. Medium 7 and Part 2 item 5, "Identical same-day finishes inflate the count": a finish the other window already saved with the same words and date adds nothing to the count, and the count is now called "times you marked a plan done". Part 2 item 3, "Say when the other window changed the file": when both windows finished a plan it says "The other open window had also finished a plan." Low 8: option 1 re-reads the file before the summary and before the full file. Low 11: the file holds at most 400 dates, real visits first. Tests for each.

Forget one finished plan. Medium 4, "Forgetting a line can still clear same after the line is already gone", and Part 2 item 4, "leave same only when they ask": option 7 now asks before also forgetting the words for `same`, with no as the default. When the line is already gone it says so and changes nothing. Low 9: a wrong number says "Type a number from 1 to N, or press Enter to keep them all." and asks again. Tests for each.

Other fixes: Medium 5, "Uninstall still follows reparse points in the live install folder": `uninstall.ps1` checks the install folder and each file in it for a link, and removes each subfolder with `Remove-Tree`. Low 10: the launcher refuses a folder with `!`. Low 12: `--help` and the README list `x` and `close` as ways to close. Low 13: the README's run-on paragraph is now four short ones, and it says where Enter closes and that forgetting a plan leaves the count. Part 2 item 2: `PLAN.md` names the release gate, a clean-PC install pass with two real windows. README, `PLAN.md` and the why-doc say what the delete leaves behind.

Part 2 item 6, "Do the screen-reader pass": the owner ran 1.16.0 in a real console with Narrator in a sandbox, and it passed. It is out of `BACKLOG.md`, and `PLAN.md`, the README and the why-doc say so. Not done: Part 2 item 2, the clean-PC install pass with two real windows.

Tested here: all 123 tests pass on Windows 11, Python 3.13, under both pytest and the plain runner. `uninstall.ps1` parses in Windows PowerShell 5.1. I piped option 7 and Delete everything through and read the screens and the marker file. Not tested: a real console, two real windows, a screen reader, the installer and uninstaller themselves, and ruff.

## 2026-10-02: every save merges with the file, one finished plan can be forgotten, the menu says where Enter goes

Version 1.16.0. Round 41 review (`reviews/round-41.md`), one reviewer, no Critical, 2 High, 6 Medium, 7 Low, 6 Part 2 items.

Saves from two windows. High 1, "sync() replaces the finished list instead of merging it", Medium 6, "set_plan / mark_done_now are not on the sync path", Low 11, "sync() applies a negative done delta", and Low 12, "Offer skip and reminder state are last-write": `sync()` is replaced by one `commit()` that every save of a change goes through: the follow-up screen, `done`, `plan`, menu options 2, 3, 6 and 7, and the sign-in offer. It re-reads the file just before writing, with no prompt in between. Visits are merged. Finished plans are merged by date and words, and one this window forgot stays forgotten. `done` and `offer_skips` add only what this window added, never less. Any other key is taken from this window only when this window changed it. A failed save puts the window back as it was through one `undo()`, instead of a hand rollback at each caller. The done line and count are now shown after the save, with the merged count. Tests: two windows both finishing, two windows both skipping the offer, a lower count that must not subtract.

Retention change. Part 2 item 2, "Let them drop one line without Delete everything": menu option 7 lists the finished plans by number and forgets the one you pick. When those words are also the earlier plan kept for `same`, that goes too, so the plan really leaves the file. Low 9 and Part 2 item 3, "First finished plan is invisible": the list now shows after the first `done`. Tests for both.

Accessibility change. High 2, "The live menu still says Enter closes": the menu line now reads "Enter  Back to the last prompt" and its prompt "Enter = back". Medium 4, "'See you tomorrow.' runs on skip words too", and Part 2 item 4: after `done`, only Enter and the quit words close, and the line is "Closing.". `no`, `none`, `nothing`, `skip` and `n` there now go back to the last prompt. Low 10: `--help` now says where `same` works, that Enter at the menu goes back, and where the finished list shows. Tests for each.

Other fixes: Medium 3, "A yes on the sign-in offer is final even when the launcher write fails": the offer is closed only once the launcher is written, and a failure names menu option 2. Medium 8, "Finished dates are trusted once they parse": a finished date before 2000 or more than a year ahead is dropped on load. Low 13, "Launcher script rejects \" and % only": `&`, `^`, `<`, `>` and `|` are refused too. Medium 7, "Uninstall still removes $dir.new and $dir.old with Remove-Item -Recurse and no reparse check": `uninstall.ps1` now uses the installer's `Assert-NotLink` and `Remove-Tree`, with a pointer comment on both copies. Medium 5 and Part 2 item 5, "Decision records contradict the file": README, `PLAN.md` and `docs/WHY-DAILY-ACTIONS.md` now carry the same paragraph on what the file holds, what shows it, what deletes it, and that uninstall leaves it. Low 14: the screen test no longer bans `!`, and the "Not tested" lines now name this Windows run.

The tests failed on Windows: 8 of 105 broke because a test with no Startup folder fell through to the real one in `%APPDATA%`, so the sign-in offer ate the typed input. `STARTUP_DIR = ""` now means no Startup folder, every test passes it unless it sets one, and the seven copies of the module loader in the tests are now `_load_hello()`. This also answers Part 2 item 6, "Prove it on a Windows console once", as far as a test run can.

Declined (see `BACKLOG.md`, Round 41): Low 15, Dependabot can't see the tests.

Tested here: all 115 tests pass on Windows 11, Python 3.13, with both pytest and the plain runner. Both PowerShell scripts parse in Windows PowerShell 5.1. I ran plan, `done`, next plan, `done`, `no`, the menu and option 7 through piped input and read the output. Not tested: a real console, a screen reader, the installer and uninstaller themselves, and ruff (not installed on this machine).

## 2026-10-02: the last seven finished plans come back, Enter really closes after done, a window left open can't undo a newer save

Version 1.15.0. Round 40 review (`reviews/round-40.md`), no Critical, 1 High, about 12 Medium, about 25 Low, about 25 Part 2 items across four reviewers (lead, security, usability and retention, accessibility).

**Retention change.** Usability, "Finished lately" retention feature, and lead Part 2 item 6, "Finished this week ... a visible payoff": the program now keeps the last seven finished plans (words and date) in `notes.json`. After you finish a second plan it lists them ("Finished lately (the last 7 are kept, only on this computer)"). The same list shows under "Welcome back" after a week away (usability 9, "it never shows what they did before leaving") and in menu option 1 and `--stats`. It leaves with Delete everything. A bad or hostile list in the file is dropped, not shown. Removed from `BACKLOG.md`: the Round 39 "Finished this week" entry. `PLAN.md` now says history is kept, and how much. Tests: list after done, cap of seven, after a gap, in the summary, damaged list.

**Accessibility change.** Accessibility M1, lead 3, "Enter = close ... does not close": after `done`, one Enter now closes with "Closing. See you tomorrow." (so do `q`, `no`, `none` and end of input), and "Nothing changed." is gone from that flow. The test that hid this passed on two Enters; the new one feeds exactly one and checks the last prompt is not shown again. Lead 2, "the menu falls through to `break`": Enter at the menu now returns to the last prompt, as the notes claimed, so a plan set in the menu can be finished in the same sitting; `MENU_HELP` says so. Accessibility M5 and lead 10, "circular or misleading" command message: at a plan prompt it now says "Type your plan, or press Enter to go back."; at the first prompt it says "at the last prompt" (not "the end of this screen"); `no`, `none`, `nothing`, `skip` and `n` are quietly taken as no plan, not lectured. Accessibility M7: three unclear answers at the sign-in offer say so. The plan-saved line says "Saved." not "Done." and tells you how to finish it later (usability 5). `HELP` lists `same` and `m`.

Other fixes: lead 1 (High) and security 6, "the stale-state fix refreshes before the prompt, not after": `set_plan` re-reads the file after the prompt, the sign-in offer re-reads before saving, and `daily()` now re-reads and replays only what that window changed (visits, plan, previous, done count and so on) instead of saving a stale copy; tests simulate a second window saving between the prompt and the save. Lead 6, "the sign-in offer comes back after the person turned the launcher off": turning it on or off from menu option 2 now ends the offer. Lead 14: the set-plan prompt now shows an older open plan with its date before "Enter = keep". `PLAN.md` says several plans can be set in a day.

Declined (see `BACKLOG.md`, Round 40): launcher pause, installer, CI and README clone-step Git hardening (Windows or `.github/`); simple numbered mode, one prompt normaliser, wrapping all prose, a left-off note, more content, `clear`, shorter first run (design decisions for the pilot); save-edge cases and test hygiene; content that assumes sight or hearing; a switch for the finished list.

Tested here: all tests pass on Linux, Python 3.11, with the plain runner, and ruff is clean. I ran the retention path (plan, `done`, next plan, `done`, then a later day after a gap) and the accessibility path (one Enter after `done`, menu then Enter then `done`, `no` at the plan prompt, a command word at the plan prompt) through piped input and read the output. Not tested: anything on Windows or Python 3.14, a real screen reader, a real second window (simulated by saving from a second state inside the prompt), and pytest (not installed here).

## 2026-10-02: finishing a plan leads to the next one, no prompt closes on typed text, two windows can't overwrite each other

Version 1.14.0. Round 39 review (`reviews/round-39.md`), no Critical, 2 High, about 20 Medium, about 25 Low, about 25 Part 2 items across four reviewers (lead, security, usability and retention, accessibility).

**Retention change.** Usability 6, "After `done` the session dead-ends ... Someone who finishes a task and wants to set the next one cannot do so", and the lead's "plan loop" direction: after `done` it now asks "Type the next plan, same to reuse the earlier plan, or Enter = close", so finishing one thing sets up the next in the same sitting, and Enter still closes. Lead 7, "All content repeats every 100 days, and the pairing repeats with it": there is now one more thought than tips, so the same thought and tip pair only returns after about 10,000 days. Lead 3, "Command words typed at the first plan prompt become the plan ... a bad second session": `menu`, `done`, `q`, `skip`, `no` and similar words are no longer saved as a plan, at either plan prompt; it says so. Tests: next plan after done, Enter closes, command words, pair length.

**Accessibility change.** Accessibility H1, "After `done` or `plan` ... any typed text closes the window": after `done`, `plan` and the menu the full last prompt comes back below the result, so typing `plan`, `menu` or a typo no longer closes the window and the result stays on screen; the second "Press Enter to close" is gone. Accessibility M5 and lead 5, "Hard-wrapped lines at 72 columns do not reflow": wrapping follows the window width (30 to 72). Accessibility M6, "embeds the previous plan in the prompt string": the earlier plan is printed wrapped on its own line and the prompt is short. Accessibility M1, "Three wrong answers end in silence": it says "That was not understood. Your plan is left as it was." Accessibility M3, "`done` counts as a yes at Keep it for today?": `done` is now named as not a choice there. Tests for each.

Other fixes: lead 1 (High), "Stale in-memory state overwrites newer saves": `done`, `plan` and menu option 3 re-read the file before changing it; tested with two states on one file. Lead 4, accessibility M4, usability 5, "success is printed before the save": the done line and count are shown only after the save works; a failed save says the plan is still open (and the follow-up path says "Your answer was not counted"); tested. Security 4, "privacy text inconsistent": `PLAN.md` now says the file lists the last 400 dates opened. `HELP` lists `done` and `q`. Removed from `BACKLOG.md`: stale-state overwrite from a second window.

Declined (see `BACKLOG.md`, Round 39): the weekly "Finished this week" list, moving the sign-in offer and shortening the first run (wait for pilot feedback); CI, Dependabot, installer, signing and uninstall findings (`.github/`, Windows); screen-reader pass, Python 3.14 run and a real Windows install (need Windows); shorter visit history, forgetting the earlier plan, tip rewording, menu order (product decisions).

Tested here: all tests pass with the plain runner on Linux, Python 3.11, and ruff is clean. I ran the retention path (plan, `done`, next plan, then `plan` and `menu` at the returning prompt) and the accessibility path (command word at the plan prompt, three wrong answers, a narrow-window wrap) through piped input and read the output. Not tested: anything on Windows or Python 3.14, a real screen reader, a real second window (simulated with two states on one file), and pytest (not installed here).

## 2026-10-02: done counts the moment you finish, every typo is named and asked again, the privacy line is true

Version 1.13.0. Round 38 review (`reviews/round-38.md`), no Critical, 2 High, about 20 Medium, about 25 Low, about 20 Part 2 items across four reviewers (lead, security, usability and retention, accessibility).

**Retention change.** Lead 2 and usability H1, "A plan can only be marked done the next morning ... The natural return moment has nothing to reward": while a plan is on screen the last prompt now reads "Press Enter to close, or type done, plan, menu or q >". Typing `done` counts the plan at once (the done line, the count, the plan kept for `same`) and tomorrow does not ask "Did you do it?" about it. Typing `done` with no plan says so and does nothing. Tests: done the same day, no question the next day, done with no plan, a failed save is rolled back by the same code path as `plan`.

**Accessibility change.** Accessibility 2 and 3, lead 3, "The fix was applied at one prompt only ... Typos at the other prompts are silently misread": one helper now names the typed word and lists the choices at "Did you do it?", "Keep it for today?", the sign-in offer and the menu, and asks again (three tries, then it leaves things as they were). A typo at the sign-in offer no longer counts as a skip, and "never", "stop" and "no thanks" are a clear no. The menu accepts `q`, `quit`, `exit`, `help` and `?`, and its error names the word. Long words are cut with "..." and keep their case. Tests for each.

Other fixes: accessibility 6 and lead 1, "'Only you can see this' is false": option 1 now says IT staff who can read the files could read it, and the old test that asserted the false line is changed. Accessibility 4, usability H4 and lead 8, "`same` with no previous plan saves the literal plan 'same'": it now says there is no earlier plan and saves nothing, at the plan prompt, under `plan`, and on the daily screen (the last was a crash for no-console runs, found by the tests and fixed). Lead 8, "'not yet' at 'Keep it for today?' clears the plan": it keeps it. Accessibility 5: the earlier plan is printed wrapped on its own line, and the plan prompt is short ("Type today's plan, same to reuse the earlier plan, or Enter = keep"). Security M1 and lead 5, "'Cleared.' is not true": it says "Cleared. It stays as same until you delete everything." Accessibility 7, 10, 11, lead 7: the garbled README bullet is rewritten, the last-prompt choices are a short list, the error text lists `q`, `MENU_HELP` describes the summary and `full`. Usability L3: the expiry message says "Type same at the plan prompt". Lead 1, security M1, usability M4, accessibility 7: `PLAN.md` and `docs/WHY-DAILY-ACTIONS.md` no longer say a done count is never saved; they say that it is, why, and that it leaves with Delete everything.

Declined (see `BACKLOG.md`, Round 38): CI, Dependabot and repository-setting findings; uninstall junction and Windows ACL hardening; expiring or switching off `previous` and `done`; weekly recap, last-five plans and the first-run reshuffle; a screen-reader pass and the interactive installer smoke test; the rest as product decisions for the pilot or needing Windows.

Tested here: all tests pass with the plain runner on Linux, Python 3.11, and ruff is clean. I ran the retention path (plan, `done`, then a later day with no follow-up question and `same` offered) and the accessibility path (a wrong word in the menu then `q`, a mistyped yes then y, `same` with nothing remembered) through piped input and read the output. Not tested: anything on Windows or Python 3.14, a real screen reader, whether the console reads the new prompts well, and pytest (not installed here).

## 2026-10-02: a plan you repeat is one word, errors list the choices, option 1 is a summary

Version 1.12.0. Round 37 review (`reviews/round-37.md`), no Critical, 3 High, about 25 Medium, about 30 Low, about 25 Part 2 items across four reviewers.

**Retention change.** Usability finding 5, "the second session is not faster than the first ... Retyping a recurring plan ... is the exact friction that kills habit", Critical 1, "no personal asset accrues", and lead 1, "nothing here pulls a person back": hello-world now remembers, privately and only in `notes.json`, the plan before the current one (`previous`) and how many plans were marked done (`done`). The plan prompt says `type same for: "..."`, and typing `same` reuses it, at the prompt and under `plan`. After a yes it says "That is N plans you have finished." from the second one on. Option 1 shows the count and the previous plan. Lead 9, "a plan left unanswered becomes invisible for the rest of the day": reopening the same day shows "Still open from ...". Lead 10 and usability 9, silent expiry: a plan over two weeks old is cleared with a message and kept as `same`. Tests: same at the prompt and under `plan`, done count and its privacy, same-day reopen, expiry.

**Accessibility change.** Accessibility M1 and lead 15, "Error identification ... does not say what the choices are ... Two typos ending the session is harsh": a wrong word at the last prompt now names the word and lists the choices, and the prompt comes back until Enter; "Closing now" is gone. `q`, `quit`, `exit` close and `help` and `?` open the menu. Accessibility M3 and usability 11, raw JSON in option 1: option 1 now prints a short summary in sentences, and the whole file only when you type `full` (`--stats` still prints everything for scripts). Accessibility L1: prompts say what Enter does ("Enter = keep", "Enter = cancel"), and delete needs a clear yes, not "done". Tests for each.

Other fixes: lead 11, "'not yet' at the sign-in offer counts as a permanent no" (it asks again now; test added); lead 12 and security 7, no fsync and a world-readable temp file: `save()` creates the file 0600, never through a link, and flushes it before replacing (test on POSIX). README, PLAN: the screen-reader claim now reads "designed for, not yet verified" (accessibility H1 wording). Removed from `BACKLOG.md`: same-as-last-time, option 1 without raw JSON, the 14-day expiry notice, POSIX file modes.

Declined (see `BACKLOG.md`, Round 37): CI, workflow and repository-setting findings; installer, launcher and Windows-only findings; prompt endings, console-width wrapping, menu renumbering, `--version`, first-run shortening, the full multi-item "My list" and weekly look-back, content changes: need Windows, a real screen reader, or the owner's pilot. The review packet's developer notes came through empty; that is a packet-building slip in this routine, not a repository fault.

Tested here: all tests pass with the plain runner on Linux, Python 3.11, and ruff is clean. I ran the retention path (done, then `same` on a later day, then option 1) and the accessibility path (wrong words, `q`, `?`, option 1 and `full`) through the test runner with piped input. Not tested: anything on Windows or Python 3.14, a real screen reader, whether the console reads the new prompts well, and pytest (not installed here).

## 2026-10-02: sign-in offer at the moment of commitment, results stay on screen until Enter

Version 1.11.0. Round 36 review (`reviews/round-36.md`), no Critical, one High, about twenty Medium, about twenty Low, about twenty Part 2 items across four reviewers.

**Retention change.** Usability finding 1, "The return mechanism is offered after the moment it is needed", findings 2 and 3 ("A reflexive Enter ... is recorded as a permanent no", "Users who already have the app never get the offer"), and lead finding 1, "the sign-in offer never reaches existing users": the opt-in sign-in offer now comes right after the first plan is saved, and also on any later visit from the second on, so people already using 1.9 or earlier are asked too. Only a clear no is final. Enter or an unclear answer asks again on a later visit, three times at most (`offer_skips` in `notes.json`). "done" no longer counts as yes there (security L7). Nothing starts without a clear yes. Tests: first-plan offer, existing user with five visits, Enter then no, "done".

**Accessibility change.** Accessibility H1, "Confirmations and errors vanish because the window closes right after them": after `plan` and after a second wrong answer the screen now waits at "Press Enter to close >", and the second wrong answer says "Closing now. Nothing was changed." Also M1 (a plan typed on any day is now confirmed with "Saved. Tomorrow it will ask how this went."), M4 and lead 8 (menu option 5 now explains the menu in employee terms; `--help` prints the folder `hello.cmd` is in), lead 7 (menu toggles say the action: "Turn on: ... (now off)"), L2 (Ctrl+C starts a clean line), L4 (first-run line says "plan or menu"). Tests added for each.

Other fixes: lead 16 (`plan` uses the date the window opened, not midnight-crossed), lead 17 (thought no longer names Tuesday), lead 18 (content no longer splits on hyphens), lead 4 (the plan prompt says a new plan replaces the old one when yesterday's was left as it was), lead 9 (README now lists every saved field), security L5 (data folder created 0700 on POSIX), README: backup names, English-only and untested-with-a-screen-reader notes.

Declined (see `BACKLOG.md`): dependabot, CI, SHA-pin, checksum and workflow findings (`.github/`, which this routine does not change); installer colour, progress, bootstrap and junction findings (need Windows); same-day "done yet?", multi-item plans, Start entry rename, `q` to quit, plain-words option 1, error log, sign-in startup-mode visit counting, content tags: product decisions for the owner.

Tested here: all tests pass with the plain runner on Linux, Python 3.11, including the first-plan offer, the existing-user offer, the Enter-then-no sequence and the Enter-to-close waits. Not tested: anything on Windows or Python 3.14, a real screen reader, whether the Startup folder launcher fires after sleep, and pytest (not installed here).

## 2026-10-02: say what tomorrow holds, offer the sign-in reminder once, plain-word prompts

Version 1.10.0. Round 35 review (`reviews/round-35.md`), no Critical, no High, ten Medium, about fifteen Low, nine Part 2 items.

**Retention change.** Usability finding 1, "The hook is never explained at first run", and finding 3, "The sign-in reminder is the retention lever and is buried": the first-run screen now says a typed plan gets asked about tomorrow, and a first saved plan prints "Saved. Tomorrow it will ask how this went." On the second visit it asks once, "Want it to open once a day when you sign in? (y/n)". The answer is remembered in `notes.json` (`offered`), so a no is never asked again, and it still starts nothing without a yes. Tests added for first run, ask-once, yes and no.

**Accessibility change.** Accessibility M1, "The damaged-file notice names the wrong file": the notice now names the real backup (`notes.json.bak2` and so on), shows the folder, says in plain words that earlier days and plan could not be read, and is followed by a blank line before the greeting. M5, "single letters": the closing prompt and first-run line now say "type plan or menu" (`p` and `m` still work). M2, "silently does something": an unrecognised answer at the closing prompt says so and asks once more; "Did you do it?" and "Keep it for today?" now echo "Kept for today.", "Cleared." or "Left as it was." L1, HELP wrapped to 72 columns, with a test. L2, an unknown option is named, and `--remind` or `--streak` alone says it needs on or off. L10, wrapping no longer splits "hello-world" or long words.

Declined (see `BACKLOG.md`): workflow and installer findings (CI, Dependabot, checksums, SHA pins, installer progress, junction checks, focus at sign-in) need Windows or `.github/` changes I can't run here; a note to tomorrow, same-as-last-time, clearing a plan, raw JSON in option 1, Ctrl+C quits, time-of-day content tags, `extra.txt`, `.prev` backup and a renamed Start entry are product decisions for the owner.

Tested here: all tests pass with the plain runner on Linux, Python 3.11, including the sign-in offer with a temporary startup folder. Not tested: anything on Windows or Python 3.14, a real screen reader, and pytest (not installed here).

## 2026-10-02: damaged-file notice wrapped and named, `--reset` folder-listing message

Version 1.9.7. Round 34 review (`reviews/round-34.md`), no Critical, no High, three Medium, ten Low, eight Part 2 items.

- Finding 4, "the new damaged-file notice breaks the program's own screen rules": the notice is wrapped to 72 columns, names `notes.json.bak` and says menu option 4 deletes it. Test now checks the name and line width. (Moving it after the greeting is not done: `load()` runs before the greeting is printed.)
- Finding 8, "`reset()` handles a folder-listing failure poorly": a failed listing now says "Could not list the folder, so backup copies may remain" instead of offering the whole folder as something to delete. Still exits 1.
- Finding 10, "Python version requirement isn't stated": README says Python 3.11 or later for the tests.
- Installer example tag in README and `install.ps1` is v1.9.7.

Declined (see `BACKLOG.md`): findings 1, 2, 3, 13 and Part 2 items 2 and 4 (CI, Windows or workflow work I can't run here); 5, 6, 7, 9, 11, 12 (behaviour changes weighed in earlier rounds or low value: Ctrl+C handling, save retry, error log, race note, launcher pause); Part 2 items 1, 3, 5, 6, 8 (owner decisions or already covered). Part 2 item 7, a content count test, is already covered by existing content tests.

Tested here: all tests pass with the plain runner on Linux, Python 3.11. Not tested: anything on Windows or Python 3.14, and pytest (not installed here).

## 2026-10-02: `--reset` tries every file, a set-aside file is announced

Version 1.9.6. Round 33 review (`reviews/round-33.md`), no Critical, no High, four Medium, eight Low, ten Part 2 items.

- L5, "`reset()` is incomplete... stops at the first failed delete": it now tries every file, lists every failure, and returns False (exit 1) if listing the folder failed too. The unused `load` call in `--reset` was already gone in 1.9.5, so nothing to drop. Test added.
- M3 and Part 2 item 7, "When `load()` moves a file aside, print one line": a damaged file moved to a backup now prints one plain line saying so. Test added. The `fsync` and first-run-screen parts stay declined.
- L10, "docstring lists exit codes 0, 1 and 2": the `hello.py` docstring now says 1 also covers a failed command.
- README and installer example tag are v1.9.6.

Declined (see `BACKLOG.md`): M1, M2, M4, L6, L7, L8, L11, L12 and the rest of Part 2, same reasons as earlier rounds (CI and Windows, PowerShell I can't run here, or a decision for the owner). L9, wording: not changed this round.

Tested here: all tests pass with the plain runner on Linux, Python 3.11. Not tested: anything on Windows or Python 3.14, and pytest (not installed here).

## 2026-10-02: Failed `--reset` exits 1, read-only commands leave a damaged file alone

Version 1.9.5. Round 32 review (`reviews/round-32.md`), no Critical, two High, six Medium, eleven Low, nine Part 2 items.

- M2, "`--reset` exits 0 even when deletion fails": `reset()` now returns True (deleted), False (a delete failed) or None (declined); `--reset` exits 1 only on False. Answering no stays 0. Test added.
- M3, "Read-only commands change files": `load(repair=False)` leaves a damaged `notes.json` where it is. `--stats` and `--reset` use it, and `--stats` says "The saved file can't be read right now, or it is damaged", exits 1 and changes nothing instead of printing an empty history. An unknown option no longer reads the file. Test added. This also removes the "make `--stats` read-only" and "failed `--reset` exit code" items from the backlog.
- README and installer example tag are v1.9.5.

Declined (see `BACKLOG.md`): H1, H2, M4, M5, M6 (CI and Windows, same reasons as before); M1 is wrong, the files it calls missing are committed (`CHANGELOG.md`, `BACKLOG.md`, `reviews/`, `.devkit/kit/*`; the reviewer was not given them by design). L3: the launcher uses `start`, which returns at once, so `|| pause` would not see a failure.

Tested here: all tests pass with the plain runner on Linux, Python 3.11. Not tested: anything on Windows or Python 3.14, and pytest (not installed here).

## 2026-10-02: `--streak` exits 0 on success, failed `--remind` exits 1, no half-written launcher

Version 1.9.4. Round 31 review (`reviews/round-31.md`), no Critical, no High, five Medium, twelve Low, nine Part 2 items.

- M1, "`--streak on|off` always exits 1, even on success": a regression from 1.9.3. Confirmed by reading the code: `return 1` sat after the if/else. It now returns 0 on success and 1 only when the choice can't be saved. Tests added for both.
- M1 (related), "`--remind` returns 0 even when it prints 'Could not set up the reminder.'": `remind()` now returns True or False and `--remind` exits 1 on failure. Test added for the success case.
- L7, "`remind(True)` can leave a partial launcher": the file is removed if writing it fails.
- README and installer example tag are v1.9.4.

Declined (see `BACKLOG.md`): the rest. `--reset` keeps exit 0 when the person answers no, since that is their choice.

Tested here: all tests pass with the plain runner on Linux, Python 3.11. Not tested: anything on Windows or Python 3.14, the failed-write launcher cleanup, and pytest (not installed here).

## 2026-10-02: Delete-everything removes every backup, cut plans end cleanly, failed --streak exits 1

Version 1.9.3. Round 30 review (`reviews/round-30.md`), no Critical, one High, three Medium, five Low, seven Part 2 items.

- M2, "'Delete everything' does not delete the numbered backups": `reset()` now removes `notes.json`, every `notes.json.bak*` and the `.tmp` copies. The test now has a `.bak2` present.
- L6, "Truncating to 120 characters ... can leave a trailing space or joiner": `clean()` strips spaces and joiners after the cut. Test added.
- L6, "`--streak on|off` ... return 0 even when they fail": returns 1 when the choice can't be saved. `--remind` still returns 0; its messages are unchanged.
- README and installer example tag are v1.9.3.

Declined (see `BACKLOG.md`): the rest.

Tested here: all tests pass with the plain runner on Linux, Python 3.11. Not tested: anything on Windows or Python 3.14, and pytest (not installed here).

## 2026-10-02: Windows console check fails open, future-dated visits kept, plan cut notice, numbered backups

Version 1.9.2. Round 29 review (`reviews/round-29.md`), one High, five Medium, fourteen Low, eight Part 2 items.

- H1, "`interactive()` ... imports outside any `try`": the imports and the `GetConsoleMode` call now sit inside `try`, and an unexpected failure falls back to the `isatty()` answer ("yes") instead of "something went wrong" or a screen that closes at once. A real "no console" answer (a NUL device) is unchanged. Add a mocked test for it only when a Windows run exists; a test of the fallback needs `os.name == "nt"`.
- M1, "Dropping future-dated visits on load destroys real history": they are still left out of every count, but `save()` writes them back, so a clock that was wrong once loses nothing.
- M2, "A plan longer than 120 characters is cut silently, and a plan of only joiners can be saved": the screen now says "Shortened to 120 characters.", and text with nothing but joiners counts as empty.
- Low 1, "A second damaged file overwrites the earlier `.bak`": the second becomes `notes.json.bak2`, and so on. The read-only `--stats` still moves a damaged file aside, which is what lets option 1 show a clean state.
- Low 3, "Uncaught decode error": `ask()` treats it as no answer.
- Low 10, "The environment variables are ignored test proves little": it also checks the output for the ignored date.
- README and installer example tag are v1.9.2.

Declined (see `BACKLOG.md`).

Tested here: all 51 tests pass with the plain runner on Linux, Python 3.11. Not tested: anything on Windows, including the new `interactive()` fallback, and pytest (not installed here).

## 2026-10-02: Console check made safe, joiner characters kept, future-dated visits dropped, honest wording

Version 1.9.1. Round 28 review (`reviews/round-28.md`), one High, five Medium, nine Low.

- M2, "`GetConsoleMode` is called without `argtypes` or `restype`": the call declares `HANDLE`, `LPDWORD` and `BOOL`, and any failure counts as no console instead of "something went wrong".
- L4, "`clean()` damages some non-English text": U+200C and U+200D are kept; the bidi controls are still removed.
- L2, "Future-dated visits": visits after today are dropped on load, so a wrong clock once can't hide real history.
- L1, "Option 1 and `--stats` say more than they know": the screen says "After tidying, the file holds only this:" and shows non-ASCII text as typed.
- L8, "`HELP` omits `p`": added.
- L9, "`.gitignore` lacks `install.log` and `*.zip`": added, with `.ruff_cache/`.
- L7, "No test asserts the `.ps1` files are ASCII" and "No test checks that the README and installer tag match `VERSION`": both added, plus tests for the two code changes. The README and installer tag are v1.9.1.

Declined (see `BACKLOG.md`).

Tested here: all 47 tests pass with the plain runner on Linux, Python 3.11. Not tested: anything on Windows, including the new `GetConsoleMode` declaration, and pytest (not installed here).

## 2026-10-02: Plan shortcut on the first screen, byte-order-mark files, tests that can fail, docs made accurate

Version 1.9.0. Round 27 review (`reviews/round-27.md`), no Critical or High findings.

- Part 2 item 4, "Add a set-or-change-plan shortcut and mention it on screen": the last prompt reads "Press Enter to close, p for today's plan, m for options". `p` runs the same step as menu option 6.
- Part 1 item 2, "Two regression tests pass whether or not the bug exists": both now use a visit that would be the 3rd in a row, so they fail if `--streak off` is ignored. Checked by hand: the old tests could not see this.
- Part 1 item 7, "Some pairs of 'thought' and 'try this' lines are duplicates": the thought that repeated the water tip is reworded, and a test checks every pairing for it.
- Low, "UTF-8 BOM": `notes.json` is read as `utf-8-sig`, so a file saved by Notepad is no longer moved to `.bak`.
- Low, "`isatty()` raises ValueError": a closed stdin counts as no person at the keyboard.
- Low, "Failed saves can leave a temp file": removed on failure.
- Low, "test touches the real data folder": that test now points `HOME`, `LOCALAPPDATA`, `APPDATA` and `XDG_DATA_HOME` at a temp folder.
- Part 1 item 3 and Low, "README tag": README, PLAN and the WHY doc now mention the in-a-row setting, say option 1 shows a tidied copy, and say the tests last ran on Windows for 1.7.1. The example tag is v1.9.0 in README and the installer help (comment text only).
- New tests: `p` at the last prompt, BOM file, thought/tip pairing. The first two fail against 1.8.0's `hello.py`.

Declined (see `BACKLOG.md`).

Tested here: all 43 tests pass with the plain runner and with pytest, on Linux, Python 3.11. Not tested: anything on Windows, including the console check and PowerShell.

## 2026-10-02: Keep the plan on Enter, honour the unreadable-file rule in the menu, make reset complete, add a plan option

Version 1.8.0. Round 26 review (`reviews/round-26.md`), no Critical or High findings.

- M1, "Pressing Enter at 'Keep it for today? (y/n)' silently deletes the plan": only an explicit no drops the plan now. Enter, Ctrl-C and end of input keep it.
- M2, "Menu option 3 can overwrite a notes file the program decided it must not touch": the menu gets `can_save` and refuses to save when it is false, as `--streak` already did. Tested with a notes path that can't be opened.
- M3, "'Delete everything saved' leaves plan text behind": reset also removes `notes.json.bak` and any leftover temp copy.
- L9, "Concurrent runs can race on notes.json.tmp": the temp file name includes the process id.
- L8, "Ctrl-C outside input()": a Ctrl-C anywhere exits 1 quietly instead of "something went wrong".
- Part 2 item 2, "Let people use the plan any time": menu option 6 sets or changes today's plan; Enter keeps what is there.
- L1, stale docs: the example tag in `README.md` and the `install.ps1` help is v1.7.1. `PLAN.md` and `docs/WHY-DAILY-ACTIONS.md` no longer say nothing has run on Windows. Part 2 item 6 is only partly done: the facts still live in several files.
- M4 and M5, docs only: the README's "If something fails" now says a failure at step 6 leaves the new files in place (run the installer again), and that open hello-world windows block replacing the folder. I did not change the installer's code or messages because I can't run PowerShell here.
- README describes option 6 and that reset removes backup copies.
- New tests: Enter and n at keep-for-today, option 6, reset removing backup and temp copies, and the menu not saving over an unreadable file. All four fail against 1.7.1's `hello.py`.

Declined (see `BACKLOG.md`): the other items, with reasons there.

Tested here: all 40 tests pass with the plain runner on Linux, Python 3. pytest isn't installed here, so the pytest runner was not run. Not tested: anything on Windows (the console, PowerShell, the installer, the uninstaller, the reset on a locked file), and the installer code is unchanged apart from the help example.

## 2026-10-01: Fix the console check on Windows and leave the admin's window as it was

Version 1.7.1. A Windows test run of 1.7.0 found these. The scheduled review rounds can't run PowerShell or Windows Python, so none of them had been seen.

- `hello.py` no longer treats the NUL device as a person at the keyboard. Windows reports NUL as a terminal, so a run with its input from NUL printed every question and recorded the day as a visit, which used up that day's plan question. It now also asks Windows for a console mode, which only a real console has. Two tests failed under pytest on Windows because of this.
- The tests no longer depend on the runner's own stdin. A run with no typed text now gets the null device explicitly. Before, it inherited the runner's stdin, so pytest (which points it at NUL) failed two tests that the plain runner, started from a shell with a pipe for stdin, passed. The plain runner was already exiting 1 on a failed assert; it now also counts any other exception as a failure, keeps running the remaining tests, and lists every failed test before exiting 1.
- `install.ps1` puts the admin's window back the way it found it, on success, on an early failure, and on a failure after the log starts. It had left `GIT_CONFIG_NOSYSTEM` set and `HOME`, `XDG_CONFIG_HOME` and the admin's `GIT_*` variables deleted. Git in that window then lost Git for Windows' system config, including `credential.helper = manager`, so the README's reinstall, which clones the private repo again in the same window, would ask for a username and password. The TLS setting it widens is restored too.
- The tests run the program in Python's UTF-8 mode and exchange text with it as UTF-8. On Windows a child process reads piped text in the console's code page, which is UTF-8 in a PowerShell window and cp1252 in Git Bash, while the test wrote cp1252. So the non-English plan test and the pasted-spaces test passed from Git Bash and failed from PowerShell, on Python 3.13 and on the bundled 3.14.8. Employees type into a real console, which Python reads as Unicode, so the program itself was not affected.
- `hello.py` reads no `HELLO_*` environment variables. The test date, data folder, Startup folder and typed input are module values that the tests set after importing it. A new test checks that the variables are ignored.
- Only a failed write to stdout is reported as "cannot write to stdout". Other errors now give "something went wrong" with the error type. Before, any `OSError` or `ValueError` anywhere in the program got the stdout message. A new test covers it.
- Removed the `install.ps1` block commented as adding every member of the local Administrators group. It only looked up the Administrators group's own SID, which was already in the list, so it changed nothing.
- The paste-in steps in the `install.ps1` help and the README have no line over 90 characters. The `$icacls`/`$git` line was 132 characters, and the setup folder line 99; both are now two lines each.

Tested on Windows:
- Tests: 35 pass and the POSIX-only test skips on Python 3.13 and on the bundled Python 3.14.8, from PowerShell 7, Windows PowerShell 5.1 and Git Bash, with the plain runner (stdin from NUL) and with pytest. The three new tests fail against the 1.7.0 `hello.py`, and the plain runner then lists every failure and exits 1.
- `install.ps1` under Windows PowerShell 5.1, in one window with `HOME`, `XDG_CONFIG_HOME` and a `GIT_TRACE` set beforehand: a run that fails the setup folder check, a run that fails the commit check, and a successful install. After each, all three variables, `GIT_CONFIG_NOSYSTEM` (unset) and the TLS setting matched their values from before the run, and git still found `credential.helper = manager`. The installs used a test copy pointed at test folders, the current user's registry and a test Start menu folder, since the test account isn't an administrator.
- The installed `hello.cmd` with stdin from NUL asks nothing, saves nothing and exits 0.
- `uninstall.ps1`, from the same kind of test copy, removed the install folder, the shortcut, the Apps entry and a real sign-in launcher in the current user's Startup folder.
- Not tested: typing into a real console, including non-English text; the real all-users Start menu, HKLM and the administrator prompt; more than one user profile; and the launcher at an actual sign-in.

## 2026-10-01: Make hello-world a daily-use program

Version 1.7.0. Answers the business value read-through: "this program is for the user. this program must reinforce user retention." A behavioural design review (read-only) shaped it: lead with real value, keep counters quiet, be honest about privacy, and never shame.

Changes:
- `hello.py` is now a daily moment: greeting and date, a thought and a small thing to try (100 of each, original, chosen by date), an optional plan for the day, and a follow-up the next day with a keep-for-today choice. First-run welcome, welcome back after a gap, and an in-a-row line from the third visit that can be turned off. A menu (type `m`) shows saved data, turns the sign-in launcher on or off, toggles the in-a-row line, and deletes everything. Options: `--plain`, `--stats`, `--reset`, `--remind on|off`, `--streak on|off`, `--startup`, `--help`.
- Saved data is one small file in the user's folder (visit dates, current plan, one setting). A missing, damaged or unwritable file never stops the greeting. No network use.
- The Quiet-mode and polish items from the earlier usability pass still apply. In `install.ps1`, `hello.cmd` passes its options on, the installer's test run uses `--plain` so it leaves no notes in the admin's profile, and the shortcut no longer pauses unless `hello.cmd` fails, because `hello.py` waits for Enter itself. The shortcut description says what the program does.
- "Double-clicking hello.cmd directly closes the window instantly": no longer true, since `hello.py` waits for Enter. Removed from the backlog.
- `uninstall.ps1` removes each profile's sign-in launcher, which would otherwise show an error at every sign-in, and says the users' own notes stay.
- `test_hello.py` grew from 5 to 34 tests: first run, same-day reopen, follow-up, carry-over, in-a-row line, long gap, damaged and unwritable files, non-English text, stats, reset, menu, launcher, silent startup, unknown option, and the dead-stdout cases.
- `README.md` and `PLAN.md` describe the program for employees and what is saved. `docs/WHY-DAILY-ACTIONS.md` records the reasoning for turning a greeting into a daily program.
- A tester agent ran the program as three kinds of user for ten simulated days each and tried hostile notes files. Fixed from its report: terminal escape codes in a planted notes file reached the screen ("clean" now runs on loaded text); deeply nested JSON crashed it; pressing Enter at "Did you do it?" silently deleted the plan (now only a clear yes or no changes it, and "yep", "ya", "done" count as yes); tabs and non-breaking spaces from pasted text were deleted instead of becoming spaces; a run with no terminal used up the day's questions (it now shows the screen and records nothing); long plans ran past 72 columns; a damaged file was overwritten without a copy (kept as `notes.json.bak`) and an unreadable one could be overwritten (it isn't saved over); a bad plan date turned the in-a-row line back on; odd date spellings were not normalised; the help text had an exclamation mark; `/?`, `-?` and upper-case options gave exit 2; a plan dated in the future was never shown. The in-a-row line now shows only at the 3rd, 7th and 14th visit, then every 30th, because the tester found a daily climbing number read as pressure.

Not tested: `pwsh` is not installed here, and nothing ran on Windows. Untested there: the console's handling of Unicode input, the sign-in launcher (`start` with a quoted path), the `if errorlevel 1 pause` shortcut line, the removal of launchers across profiles, and the icon and title. `python test_hello.py` passes and `ruff check` is clean.

## 2026-10-01: Usability pass on the installer, uninstaller and docs

Version 1.6.0. Answers a usability read-through and a business value read-through of the program, both done by hand. There is no review file for this change.

Changes:
- "There is no README": added `README.md` with the audience split, the install steps, update and failure notes.
- "Placeholders break if pasted": the install steps in `README.md` and in the installer help use `$tag` and `$commit` variables.
- "Permission checks are silent for minutes", "numbered steps": `install.ps1` prints `[1/6]` to `[6/6]` and shows a progress bar during the permission walks.
- "Failures print a raw error block": a `trap` and the final `catch` print one `FAILED:` line and exit 1. The full text is in `install.log`.
- "Success line is cluttered and out of date": the result says the version and whether it was a new install, a reinstall or an upgrade, then a next step. The stale LF/CRLF note is gone.
- "No unattended mode": added `-Quiet` to `install.ps1`. It prints only warnings, errors and the result.
- "Colors are inconsistent": green for success and red for failure in both scripts.
- "The Settings > Apps entry is thin": added Publisher, DisplayIcon and EstimatedSize.
- "Shortcut has no icon or description", "no title": the shortcut has the Python icon, a description and a window title. The docs say "hello-world".
- "Errors read like developer output": `hello.py`'s message ends with "(contact IT if this keeps happening)". The tests still pass.
- "Failure message gives no next step": `uninstall.ps1` says to close windows and retry, then ask IT. The admin-rights failure says to ask IT.
- Added `PLAN.md` with the value, retention and rollout plan.

Declined, added to the backlog: pausing `hello.cmd`, a one-step reinstall helper, and splitting the payload from the installer.

Not tested: `pwsh` is not installed here, so neither script was parsed. None of it ran on Windows. Untested: the `trap`, `exit 1` inside the catch, `-Quiet`, `Write-Progress`, the Python icon on the shortcut and in Apps, the shortcut's `title` command line, the `EstimatedSize` value, and the upgrade message. `python test_hello.py` passes.

## 2026-10-01: Round 25: ASCII-only strings, line endings pinned for the file check

Version 1.5.13. Answers the twenty-fifth review (`reviews/round-25.md`).

Changes:
- H1, "Em dashes in two double-quoted strings can break parsing on Windows PowerShell 5.1": replaced the three em dashes in `install.ps1` with `-`. The file has no BOM, and 5.1 reads it as Windows-1252, where the last byte of an em dash is a curly closing quote. `install.ps1` and `uninstall.ps1` now hold only ASCII.
- H2, "`GIT_CONFIG_NOSYSTEM=1` plus `git hash-object` will probably make the file check fail": confirmed on Linux. A clone made with `core.autocrlf=true` has CRLF in `hello.py` and `VERSION`, and `hash-object` with that setting skipped gives a different hash than `HEAD:file`. `.gitattributes` already pinned CRLF for `.ps1`, so those matched. Added `*.py text eol=lf` and `VERSION text eol=lf`. A test clone with `core.autocrlf=true` now matches on all four checked files. This replaces the round 10 backlog assumption that the check matches on either setting.
- M2, "The ProgramData Git check ... does not say how to fix it": the error now includes an `icacls` command that restricts the folder to administrators and gives Users read and run.
- M3, "The environment-clearing comment overstates what it does": corrected the comment. Setting `GIT_CONFIG_GLOBAL` is declined, see backlog.
- M4, "`Test-Path .git` also passes when `.git` is a file": `.git` must now be a folder.
- L3, "`cmd.exe /c` is used without `/d`": added `/d` in `Remove-Tree` and the shortcut.

Declined, added to the backlog: H3, M1, the rest of M4, L1, L2, L4 to L8.

Not tested: `pwsh` is not installed here, so `install.ps1` was not parsed. None of it ran on Windows, so the ACL checks, the `-PathType Container` test, the `/d` flag in the shortcut, and the new error text are untested. The `.gitattributes` change was checked only with Linux git. `python test_hello.py` passes.

## 2026-10-01: Add section headers and clarify installation flow

Version 1.5.12. Improved code organization and navigation.

Changes:
- Added clear section headers marking major phases of installation:
  - RECOVERY: Handle interrupted installations
  - VERIFICATION: Validate the setup environment
  - COMMIT VERIFICATION: Ensure correct commit
  - DOWNLOAD AND BUILD: Fetch Python and build
  - FINALIZATION: Register installation
- Headers make it easier to navigate the script and understand the sequence of checks and operations.

Not tested: install.ps1 not run on Windows. `python test_hello.py` passes.

## 2026-10-01: Improve permission check comments and add diagnostic output

Version 1.5.11. Better observability and code clarity for permission verification.

Changes:
- Enhanced comments in `Assert-AdminOnly` explaining ACL logic and the purpose of each check (owner, Allow ACEs, InheritOnly propagation flags).
- Better comments in parent folder checks explaining why they're needed and what happens at drive root.
- Add diagnostic output: `Assert-AdminOnlyTree` now reports how many items were checked and confirms all parents are admin-only.
- Clearer error message guidance ("Restrict write access to administrators only").

These improvements help administrators understand permission check output during installation and aid debugging if issues arise.

Not tested: install.ps1 not run on Windows. `python test_hello.py` passes.

## 2026-10-01: Harden Git environment and improve error messages

Version 1.5.10. Additional security and usability improvements.

Changes:
- Set `GIT_CONFIG_NOSYSTEM=1` to prevent Git from reading system-wide config files, ensuring full isolation from admin environment. Partial fulfillment of tenth review suggestions.
- Improved error messages throughout to guide admins when things go wrong:
  - File modification detection now advises to re-clone from the reviewed tag
  - Link/junction detection explains the security risk they pose
  - Permission and Git configuration errors provide more actionable guidance
- Permission checks now report more timing detail ("several minutes" on Git for Windows, not just "a minute")
- More explanatory comments in code for complex checks

Not tested: install.ps1 not run on Windows. `python test_hello.py` passes on Linux.

## 2026-10-01: Resolve backlog improvements: SID names, admin trust, environment isolation

Version 1.5.9. Code improvements addressing multiple backlog items. No new review findings.

Changes:
- Error messages now show friendly account names ("Administrators", "SYSTEM") instead of cryptic SIDs (S-1-5-32-544, etc.), via new `SID-ToName` function. Addresses backlog item from nineteenth review L5.
- Explicitly clear `HOME` and `XDG_CONFIG_HOME` environment variables before calling Git, improving isolation guarantee. Addresses backlog item from nineteenth review L6.
- Trust all members of the local Administrators group, not just the account running the installer. Allows any admin to run the installer even if a different admin installed Git. Addresses backlog item from line 14 of BACKLOG.md.
- Better error messages for Git for Windows installation issues, with actionable guidance on reinstalling for all users.
- Improved `.NOTES` help text to clarify permission check timing and document the ProgramData\Git folder. Addresses backlog item from nineteenth review L5.

Removed from BACKLOG.md (now addressed):
- Show account names instead of SIDs (nineteenth review L5)
- Clear HOME and XDG_CONFIG_HOME (nineteenth review L6)
- Trust every local administrator's SID (line 14)
- ProgramData\Git documentation in help (nineteenth review L5)

Not tested: install.ps1 was not run or parsed on Windows. `python test_hello.py` passes on Linux.

## 2026-10-01: Say "several minutes" where the operator sees it, and set the reinstall commands on their own lines

The twenty-fourth review, of 1.5.7, answered here. Version 1.5.8. It found no Critical, High or Medium issues, 3 Low; saved in `reviews/round-24.md`. Only a console message and help text changed.

- The permission-check message now says it can take several minutes on Git for Windows.
- The reinstall help puts `cd \` and `Remove-Item -Recurse -Force $d` on their own lines.

Declined (in BACKLOG.md):
- L3: `Get-Help` check and `uninstall.ps1` review are process items listed in earlier rounds.
- Info: pinned Python URL and hash fail closed; the pilot install is already listed.

Tested: `python test_hello.py` passes on Linux. Not tested: `install.ps1` (pwsh not installed here).

