# Round 42 review

- Date: 2026-10-02
- Commit reviewed: 4f877fe (the unmerged Round 41 branch, version 1.16.0)
- Agents that ran: one reviewer, pasted in by hand.
- Redactions: none needed.

## Part 1: findings

### High

1. "Delete everything" is undone by the other open window. Menu option 4 and --reset remove notes.json and clear only this process. commit() treats a missing file as an empty file it may write (load() returns a fresh state with can_save=True). The other window then re-reads that empty file, applies its own diff (plan, finished lines, previous, streak), and recreates the file. A person who just deleted passwords or private details from the notes can have them written back by a window they left at the last prompt.

Fix: put a tombstone on the sync path. After a successful delete, write a small marker the next commit() will honor ({"deleted": true} or an empty file plus a generation counter), and have commit() refuse to resurrect keys when the file is gone and this window did not itself delete it. reset() should refresh() first, then delete, then set this window's base to empty so a later save in that same window cannot replay the old diff.

2. The opening screen records clock cleanup as this window's edit, so it clobbers the other window's plan. daily() copies base, then mutates intent before any prompt: a future date is rewritten to today, and a plan older than 14 days is cleared and stored as previous. Those keys now differ from base, so the later commit() writes this window's intent and previous over whatever the other window saved during "Did you do it?" or the plan prompt. Visits merge; the plan does not. That breaks the guarantee this release just added.

Fix: do not treat normalization as a change against base. Either apply expiry only inside commit() onto the freshly read file (and only if that file's plan is still the expired one), or re-copy base after normalization and before the prompts, and have commit() overwrite intent only when the typed answer or set_plan actually changed it.

### Medium

3. --streak still replaces the file. Menu option 3 goes through commit(). --streak on|off does load() then save() of the whole state. A plan or finished line saved by the other window between those two calls is dropped. Route it through the same commit() as option 3.

4. Forgetting a line can still clear same after the line is already gone. forget_finished() remembers the chosen item, re-reads, then always does state.pop("previous") when previous equals that item's text, even if the re-read no longer contains the item. Two finished lines with the same words, or a forget that lost the race, wipe the earlier-plan memory the other window still needed. Pop previous only when this call actually removed a row.

5. Uninstall still follows reparse points in the live install folder. $dir.new and $dir.old go through Assert-NotLink and Remove-Tree. The live tree does not:

```powershell
Get-ChildItem -LiteralPath $dir -Force | Where-Object Name -ne 'uninstall.ps1' |
    Remove-Item -Recurse -Force
```

Remove-Item -Recurse follows a junction. Only an administrator can plant one under Program Files, which is the same trust boundary the installer already states, but this is the path you just closed for .new and .old. Remove children with Remove-Tree, or reject a reparse point on each child before Remove-Item.

6. Menu option 2 never calls undo(). A failed commit() after a successful launcher write leaves offered=True in this window's memory. The next refresh drops it, and the launcher file keeps the offer from coming back, so this is not the old "yes is final even when the write failed" bug. It is still the only save path that does not restore state from base. Call undo() there, and on the failed daily() save, so a later action in the same process cannot persist a choice the file rejected.

7. Identical same-day finishes inflate the count. Finished rows compare equal on text and date, so the merge keeps one row. done adds each window's delta, so two windows finishing the same words on the same day store one line and done == 2. Either dedupe the increment when the merged row was already present, or accept it and say so in option 1 ("times you marked done", not "plans finished").

### Low

8. Option 1 can show a stale file. show_saved() does not refresh(). With two windows, the summary can omit a finish the other window just saved. Re-read before the summary and the full dump.

9. A bad number at option 7 is worded like a choice list. not_a_choice(choice, "Nothing changed.") prints That was not one of the choices: "x". Nothing changed. Say Type a number from 1 to N, or press Enter to keep them all.

10. The launcher blocklist still misses !. remind() refuses "%&^<>|. A path containing ! is still written into a .cmd file; delayed expansion can rewrite it. Refuse ! as well, or write the launcher with delayed expansion off (setlocal DisableDelayedExpansion).

11. file_form() never trims the visit union. load() keeps 400 current and 400 future dates; save() writes both. A hostile file can sit near 800 dates until something rewrites it. Trim the union to MAX_VISITS in file_form(), keeping the newest current dates and the future ones you still want to preserve.

12. After done, x and close close, and the help text does not say so. Enter, q, quit, and exit are documented. x and close also close. Either list them in HELP or stop treating them as quit words.

13. Docs still disagree with the screen in small ways. README says uninstall leaves the file; the uninstaller also says that. PLAN and WHY now match. The employee paragraph in README is one run-on that still says both "Enter at the menu goes back" and "Enter there closes" without saying "there" is the last prompt. Split that paragraph. Option 7 does not decrement done; option 1 will keep showing the old count after a forget. Say that next to option 7.

## Part 2: what would make it more useful

The audience is clear: an employee who wants a twenty-second daily prompt and an optional plan, and IT who need a hardened all-users install. The file story is now the same in README, PLAN, and WHY. Do not add scores, network, or a default reminder.

1. Make delete stick, then say what survived. After the High 1 fix, option 4 should end with one line: everything in the file is gone, the other open window cannot put it back, and the backup copies are gone or still listed. That is the difference between a control they trust and a control that only works if they remember to close the other window.

2. Prove the two-window story on a real console, not only under pytest. The suite now keeps tests off the real Startup folder, which is why the last Windows run went green. Still untested, by your own notes: a real console, a screen reader, and the installer. The merge bugs above will not show up in piped tests that never leave a second process at a prompt. One install, one reinstall, an interrupted install, and an uninstall on a clean PC, plus two real windows both finishing and one of them using option 4, is the release gate.

3. Say when the other window changed the file. After a merged save, if the finished count or the plan text is not what this window just wrote, one line is enough: Saved. The other open window had also finished a plan. Right now the merged count appears with no reason, which reads as the program losing track.

4. Let option 7 forget the line without a lecture, and leave same only when they ask. Forgetting a finished line currently also drops previous whenever the words match. Some people want the line off the welcome-back list and still want same. Ask: Forget it from the list only, or forget it for same too? Default to list only.

5. Stop counting a finish that was not new. The private count is the only number that climbs. If it climbs when two windows finish the same plan, option 1 becomes a tally they cannot explain. Keep the count as "times you marked done" and show the seven lines as the real history.

6. Do the screen-reader pass before adding anything else. The flow is already one column, Enter is labeled, and the menu no longer says Enter closes. What is left is verification: NVDA or Narrator on the real hello.cmd window, including the post-done prompt, option 7's numbered list, and a damaged-file notice. PLAN already says it is designed for this and not verified. That verification is worth more than a second language file.
