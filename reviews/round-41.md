# Round 41 review

- Date: 2026-10-02
- Commit reviewed: 4b7205b (main after Round 40, version 1.15.0)
- Agents that ran: one reviewer, pasted in by hand.
- Redactions: none needed.

## Part 1: findings

### High

1. sync() replaces the finished list instead of merging it.

daily() is the path that claims a window left open cannot undo a newer save. Visits are unioned and done is applied as a delta. finished is not. Any change versus base assigns this window's whole list onto the re-read file:

```python
if key in ("visits", "done", "future") or state.get(key) == base.get(key):
    continue
if key in state:
    fresh[key] = state[key]
```

Two sittings both finish a plan: the later sync() keeps its own finished and drops the other window's entries, while done still adds both increments. Menu option 1 and "Finished lately" then disagree with the count. previous has the same last-write behavior. mark_done_now and set_plan still refresh and then save() the whole object, so a save in the gap after refresh is also lost. The new test only injects done and previous during "Did you do it?", never a second finished list.

Fix: merge finished by (date, text), cap at 7, and never replace it. Do the same for previous only when this window actually changed it. After refresh, write a patched file (or re-read once more immediately before os.replace) instead of dumping the in-memory object.

2. The live menu still says Enter closes.

Option text is Enter  Close. Enter, q, quit, and exit all return to the last prompt. MENU_HELP and the README say that. The screen the person is looking at does not. That is the fall-through bug from last round, half-fixed: the help string moved, the control label did not. A screen reader reads "Close" and the window stays open.

Fix: print Enter  Back to the last prompt (and the same for q). Reserve "close" for the last prompt.

### Medium

3. A yes on the sign-in offer is final even when the launcher write fails.

offer_reminder sets offered before remind(True). If the Startup file cannot be written, the flag is still saved and the question never returns. Menu option 2 is the only way back, and the failure line does not say that.

Fix: set offered only after remind() returns true. On failure, leave the offer open and name option 2.

4. "See you tomorrow." runs on skip words too.

After done, Enter, q, no, none, nothing, skip, n, x, and close all close with that line. README mentions Enter, q, no, and none only. no at that prompt is not "no plan, stay here"; it exits. Fine if documented on the prompt. It is not. The prompt says Enter = close and nothing about no.

Fix: close only on Enter and the quit words. Treat no / skip as an empty plan and return to the last prompt, or list them on the prompt.

5. Decision records contradict the file.

PLAN.md says the last seven finished plans are kept, then says "It keeps no history of plans beyond that one." docs/WHY-DAILY-ACTIONS.md section 5 still says a history of finished plans was left out on purpose. Option 1 and --stats will show a history the decision record denies. That is a trust bug for a program whose pitch is "IT can read this file."

Fix: one sentence in both files: last seven finished plans (words and date), shown after the second finish, on welcome-back, and in option 1, deleted only by option 4.

6. set_plan / mark_done_now are not on the sync path.

Refresh-then-save copies every key, including finished, offer_skips, and streak. A menu plan or a same-day done can still roll back the other window's retention list. The tests stub ask and save before the call, so they never hit the gap after refresh.

Fix: one write function used by daily, set_plan, mark_done_now, and the offer: load, apply this change, replace.

7. Uninstall still removes $dir.new and $dir.old with Remove-Item -Recurse and no reparse check.

Install refuses junctions. Uninstall does not. An elevated uninstall that follows a junction planted in Program Files deletes the target. Admin-only, so not a user attack, but it breaks the installer's own rule.

Fix: Assert-NotLink before either recursive delete, and use the installer's Remove-Tree (cmd /c rmdir).

8. Finished dates are trusted once they parse.

load() keeps any fromisoformat date, including year 9999. show_finished prints it with no range check. A hostile notes.json can fill the welcome-back screen with seven long lines. Text is cleaned; the date is not bounded.

Fix: drop finished dates outside a sane window (for example more than a year ahead, or before 2000) the same way future visits are split out.

### Low

9. First finished plan is invisible.

show_finished returns unless len(items) >= 2. The payoff the retention change exists for does not appear on the first finish. The count line does. Easy to read as "it did not save."

10. HELP omits same, the finished list, and "Enter at the menu goes back."

MENU_HELP has the menu half. hello.cmd --help does not. README does.

11. sync() applies a negative done delta.

if gained: is true for negative numbers. Nothing in daily() decreases done, so this is latent. A reset-then-save through that helper would subtract.

12. Offer skip and reminder state are last-write.

Two windows answering the sign-in question can lose a skip or clear offered. Narrow, but it is the same class of bug as the finished list.

13. Launcher script rejects " and % only.

start "hello-world" "{target}" --startup is safe for the Program Files path the installer uses. A copy run from a folder whose path contains & or ^ breaks out of the command. Out of scope for the all-users install; still a footgun for a portable copy.

14. Stale comments and tests.

test_output_is_plain_ascii_and_short still bans ! outside the greeting, so a later DONE line with one fails a content test. PLAN.md "Not tested" still says Windows was last run at 1.7.1. Both will drift.

15. Dependabot automerge cannot see these tests.

test_hello.py is a script, not pytest. The workflow runs python -m pytest -q and treats "no tests" as failure, so it will not merge on a green hello suite. It also will not catch a regression. Not a ship blocker for the employee binary.

No Critical issue in this diff. Notes stay local, plan text is still cleaned, backups are still not overwritten, and the one-Enter-after-done path matches its test.

## Part 2: what would make it more valuable

1. Make the finished list survive the promise you already printed.

README says a second window cannot undo a newer save. Employees who open it at sign-in and again from the Start menu will hit that. Until finished merges, the new payoff is the least durable thing in the file. Ship the merge before anything else.

2. Let them drop one line without "Delete everything."

The last seven plans are the first sensitive history this program has kept. IT can read them; the README says so. There is no way to remove one embarrassing line without wiping visits, the reminder choice, and same. A "forget this one" on the list matters more than an eighth slot.

3. Show the first finish.

The list appears only after the second done. The person who finishes one thing and closes never sees the payoff the feature was added for. Show a single line the first time. Keep the cap of seven.

4. Fix the menu label and the "tomorrow" line.

Enter must say where it goes. "See you tomorrow." assumes a workday and a return. "Closing." is enough. Small, and it is the screen they read every time they finish something.

5. Align the privacy sentences with the file.

One paragraph, same in README, PLAN.md, and the why-doc: dates opened (last 400), current plan, previous plan, done count, last seven finished plans. Option 1 shows that. Option 4 deletes it. Uninstall does not. People decide what to type based on that paragraph.

6. Prove it on a Windows console once.

Retention and the one-Enter close were checked with pipes on Linux. The ship target is hello.cmd, a real console, and a screen reader. The untested list in PLAN.md is still the install, the shortcut pause, the launcher, and Narrator. One clean PC pass covers more than another logic round.
