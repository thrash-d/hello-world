# Changelog

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

