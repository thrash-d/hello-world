# Round 38 review

- Date: 2026-10-02
- Commit reviewed: c7be1a1 (main after Round 37, version 1.12.0)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1, plus the newest CHANGELOG entry as developer's notes. Excluded as instructed: BACKLOG.md, CHANGELOG.md (except the newest entry), reviews/, .git/, .devkit/. Every reviewer got the whole packet.
- Agents that ran: lead, security, usability and retention, accessibility.
- Redactions: none needed; no reply named a model or vendor.

---

## Lead reviewer

# Review of hello-world 1.12.0

I read the whole packet: the notes, `hello.py`, `install.ps1`, `uninstall.ps1`, `test_hello.py`, the README, PLAN and WHY docs, and the workflows. I ran nothing, so every finding comes from reading the code and tests. The packet does not include `CHANGELOG.md`, `BACKLOG.md`, `reviews/` or the generated `hello.cmd`. I could not check the BACKLOG edits the notes claim.

The round-37 changes work as described. `same` is wired correctly in both paths, and the rollback in `set_plan` is sound. I found no data-loss bug in `load` or `save`. I found no Critical issues, and I have 2 High findings.

## Part 1: Findings, most severe first

### High

**1. A completion record now exists, and the UI says "Only you can see this." (security/trust, bug in docs and UI)**
- The new `done` count is a record of whether plans were finished.
- PLAN.md ("What was kept out", line 435) says the program saves only the current plan, the dates opened and the in-a-row setting. It lists "any record of whether a plan was done" as deliberately excluded.
- WHY-DAILY-ACTIONS §5 gives the reason: "At work that feels like being checked on". WHY §6 and PLAN "Trust" still describe the old data set. PLAN also says "A count is not value", and the README says "no scores".
- `show_saved` prints "Only you can see this. It never leaves this computer." That is false. Admins, SYSTEM and IT can read the file, and the README itself says so. `test_plans_done_are_counted_and_shown_privately` asserts the false sentence.
- The 0600 mode only exists on POSIX. On Windows the file inherits the profile ACL.
- Fix:
  - Reword the line to "Other people who can read this computer's files, such as IT staff, could read this."
  - Either update PLAN and WHY to admit the new fields and why they changed, or drop `done`.
  - If you keep `done`, name the tradeoff in the README.

**2. A plan can only be marked done the next morning, and `done` is rejected at the final prompt (retention, ease of use)**
- The only completion question is "Did you do it?" on the next visit.
- If you finish the plan at 3pm, you can't say so then. Typing `done` at the final prompt gets "That was not one of the choices", even though `done` is in `YES`.
- If you press Enter at "Did you do it?", that day's chance is gone, and reopening shows "Still open from…" with no way to close it. The menu has no "mark done" either.
- This drops the one moment when finishing feels good, and it delays the `done` count (which the programme's habit loop depends on) by a day.
- Fix:
  - Accept `done` and `y` at the final prompt and as a menu item, "Mark today's plan done".
  - Run the same code path as the follow-up: the `done` increment, `previous`, and the DONE_LINES reply.
  - Offer the new-plan prompt after it.

### Medium

**3. Typos at the other prompts are still silently misread (accessibility, WCAG 3.3.1)**
- The "name the word and list the choices" fix covers only the last prompt.
- At "Did you do it?", "yse", "yup" or "sure" prints "Left as it was." The word is not named, the choices are not repeated, and the question is not re-asked until tomorrow.
- At "Keep it for today?", any unrecognised word keeps the plan.
- At the sign-in offer, "never", "stop" and "don't" are treated as "ask me later".
- Fix: use one helper that re-asks up to 2 times with "I did not understand "yse". Type y or n, or Enter to skip." Treat anything starting with `n` and "never" or "stop" as a final no.

**4. The sign-in offer asks again without saying so (trust, ease of use)**
- After an unclear answer, the program says "Okay. Menu option 2 turns it on any time." It then asks again on up to two later visits.
- The README says "ask me later" but not that unclear words also count.
- The message on a skip should say "I will ask once or twice more. Type n to stop."

**5. "Cleared." is not true (trust)**
- Answering n at "Keep it?", replacing a plan, and the 14-day expiry all keep the old text as `previous`. It is shown in the next prompt's `type same for: "…"` hint and in menu option 1.
- Nothing but menu 4 (delete everything) removes it, and nothing says so.
- Someone who types something they regret and then "clears" it is shown it again on every plan prompt, including on a shared screen.
- Fix:
  - Say "Cleared. It stays as `same` until you replace it."
  - Add "Forget the remembered plan" to the menu, or an `x` at the plan prompt.

**6. The `done` counter has no off switch (accessibility/ease of use, retention)**
- "That is N plans you have finished." appears on every yes. Menu option 3 hides only the in-a-row line.
- Someone who finds a growing number pressuring can't turn it off.
- Fix: tie it to the same setting (rename it "Hide counters"), or make it a milestone message like in-a-row.

**7. The README sentence about the sign-in offer is garbled (accessibility/docs)**
- The bullet at lines 538-543 reads "…the next day it asks how it went. On right after you save your first plan…". A word is missing. This is the page employees are sent to.
- The Update section's `Remove-Item -Recurse -Force $d` also lacks the "in a new window, type the folder's path" note that install.ps1 has.

**8. "Not yet" at "Keep it for today?" clears the plan (bug, ease of use)**
- `is_no` includes "not yet". At the keep prompt it means keep to most people, but the code clears it.
- Use a strict n/no set for that destructive branch.
- Related: `same` typed when there is no previous plan is saved as the literal plan "same".

**9. The tip content contradicts the "assumes no ability" claim (accessibility)**
- The README and WHY say nothing assumes a level of ability or a job.
- Several tips and thoughts assume sight, hearing, a desk or an office:
  - "Name three things you can see, hear, and feel."
  - "Look at something far away", "Blink slowly", "Listen to one favorite song".
  - "Wave or smile … on your next video call", "Empty the recycling at your desk".
  - "Nothing in your inbox needs you at nine o'clock."
- Rewrite or tag these. At minimum, soften the README claim.

**10. The installer's smoke test never exercises the real interactive path (bug/test gap)**
- install.ps1 only runs `hello.cmd --plain` on the pinned Python 3.14.8.
- Everything new (`input()`, `fsync`, the console-mode check) has been exercised on 3.11 and Linux only, as the notes admit.
- Because `hello.py` degrades quietly (`except Exception: return True`), a Windows-specific failure would show up only as employee complaints.
- Fix: before the swap, run a non-interactive `--stats` or `--startup` with a test data folder. Check that the first Windows pilot covers the new prompts with Narrator or NVDA.

### Low

- **Menu consistency.** Typing `q`, `quit` or `help` inside the menu gives "Please type a number", but they work at the last prompt. Leaving the menu with Enter closes the whole window, not back to the prompt. The menu is re-printed in full after every action, which is a lot for a screen reader to re-read.
- **Menu option 6 prompt.** "Enter keeps it as it is" is shown even when there is no plan, or when the old plan is from a previous day and is not displayed. The `(…) (type same for: "…")` double parenthesis reads badly aloud.
- **`--reset` with no file.** It prints "Done. Everything saved was deleted." when nothing existed.
- **Stale-state overwrite.** State is loaded once at start. A window left open at the final prompt (for example one opened by the sign-in launcher) will overwrite later changes made in another window when you use the menu, because the whole file is rewritten from the old copy.
- **Other robustness gaps in `hello.py`.**
  - Unknown keys in `notes.json` are dropped on save.
  - Backup and `.tmp` files from crashes are never cleaned up except by reset.
  - `remind(True)` writes a launcher pointing at a `hello.cmd` that doesn't exist when run from a source checkout.
  - `help_text` says "hello.cmd is in this folder" even then.
- **Sign-in launcher.** The launcher opens a console that flashes shut on days you've already opened it.
- **Uninstall and elevated deletes.** `uninstall.ps1` deletes `hello-world-daily.cmd` from each profile as admin without checking for junctions. Only that fixed filename is at risk, so the impact is minimal, but the installer rejects links everywhere else. Roaming or redirected profiles not in ProfileList keep their launcher.
- **Weak test.** `test_same_brings_back…` ends with an `or` assertion that can't fail on the menu path. Nothing tests a typo at "Did you do it?", the day-14 versus day-15 boundary, or `same` with no previous plan.
- **CI, declined in the notes but worth a line.**
  - Dependabot auto-merges major updates after a test run that doesn't exercise GitHub Actions at all.
  - Actions are pinned by tag, not SHA.
  - `osv-scanner`, `gitleaks` and `vale` are downloaded with `curl` and never checksum-verified. That is the opposite of the installer's hash-checked ethos.

## Part 2: Improvements, most important first

1. **Retention change: capture completion when it happens, and make recurring plans one keystroke.**
   - Add `done` at the final prompt and a "Mark today's plan done" menu item (see finding 2).
   - Keep the last five distinct plans, not just one. At the plan prompt show "type same, or 1 to 5 to pick an older one."
   - Why: the habit is the plan. Finishing is the reward, and typing for a recurring chore is the cost. At the moment only one plan is remembered.
2. **Accessibility change: make error handling uniform and verified.**
   - Use one prompt helper everywhere that names the unrecognised word, lists the choices and re-asks. Add `help` and `q` inside the menu.
   - Have someone run the program with NVDA or Narrator on the Windows install before widening the rollout.
   - Add a menu item "Turn off counters".
   - Why: a person who makes a typo is currently told nothing at three of the four prompts, and nobody has yet heard this on a real screen reader.
3. **Give the person a reason to come back that is theirs.**
   - A private "This week" line on request (menu option 1 or `--stats`): "3 plans finished, 4 days opened."
   - Offer it as opt-in, in keeping with the "no checking" principle.
   - A plain-text "export my notes" lets people keep their own record and gives the owner a way to ask pilot users about it.
   - Why: nothing here accumulates for the person, and 200 content items repeating every 100 days will feel stale by month four. A small number of new items per release, or a way to "save this tip", would help.
4. **Product direction.** The purpose is clear: a 20-second daily moment for non-technical Windows office staff, deployed by IT. The weak point is that it is a console window people must remember to open. Decide, with the five pilot users, whether the sign-in launcher should be offered earlier or in a different form. Measure with a short owner-led interview at weeks 2 and 6. The "reports nothing" rule means you can't see retention otherwise.
5. **Consistency pass on docs and trust.** Make README, PLAN, WHY and the in-program text say the same thing about what is saved (`previous`, `done`, `offered`, `offer_skips`), who can read it, and how to erase just part of it. Fix the garbled README bullet (finding 7).
6. **Ease of use.**
   - Accept more yes and no words ("yup", "sure", "ok", "never") and mention `q` and `done` in the final prompt line.
   - Give "Welcome back" and the expiry message a single combined notice.
   - Tell the person before the plan is cleared at day 14, for example on day 12 ("Your plan will be cleared in 2 days. Keep it? y/n").

---

## Security reviewer

SECURITY REVIEW, hello-world 1.12.0

Scope: I read the whole packet: hello.py, install.ps1, uninstall.ps1, test_hello.py, the three workflows, the README, PLAN.md and the docs. I did not run anything. Findings are ranked within each tier.

Bottom line: there is no Critical or High finding in the application code or the installer. The real issues are one privacy-commitment problem, a supply-chain gap in CI, and some local-hardening gaps. The installer and the untrusted-input handling in hello.py are better than most code I see.

MEDIUM

M1. The privacy promise no longer matches what is stored, and "Cleared" is not clearing (CWE-359, CWE-212, CWE-1295 on misleading data-handling claims; NIST SP 800-53 PT-5, SI-12).
- 1.12.0 now persists `previous` (the plan text before the current one) and `done` (a count of completed plans).
- PLAN.md still says "Any record of whether a plan was done" is kept out on purpose.
- docs/WHY-DAILY-ACTIONS.md sections 5 and 6 still say only the dates and the current plan are saved, and that a done record "feels like being checked on."
- Only README.md was updated. IT and employees reading the other two documents are told something false.
- Messages and docs say "Cleared." (n then n at the keep prompt) and "plan ... was cleared" (expiry), but hello.py copies the text into `state["previous"]` and writes it to disk. The text stays until the person finds menu option 4. A person who types "n" to remove a sensitive plan has not removed it.
- `previous` is kept indefinitely, with no age limit. `done` is a per-person productivity metric stored in plaintext in a file the README says IT can read.
- Fix:
  - Reconcile PLAN.md and WHY-DAILY-ACTIONS.md with the README, or drop the claim.
  - Change the wording to "Cleared. Kept as 'same' until you delete everything", or stop saving a plan the person explicitly clears.
  - Expire `previous` (for example after 30 days).
  - Make `done` opt-in, or at least tell people at the point it starts counting.

M2. Dependabot auto-merge is gated by tests that cannot detect a bad update (CWE-1357, CWE-829; NIST SP 800-53 SA-12, SR-3; ATT&CK T1195.001/.002).
- The workflow merges any Dependabot PR, majors included, to main when the check job passes.
- This repo has no package.json and no requirements file. The only gate is `pip install pytest && pytest` on test_hello.py. That suite does not exercise workflows, actions or the installer.
- A compromised or malicious new major of an action (Dependabot's github-actions ecosystem) therefore auto-merges to main. The auto-tag workflow, which has `contents: write`, runs next.
- Mitigations already present: IT installs by a reviewed 40-character commit hash, and the check job has a read-only token. The blast radius is therefore "main and workflows", not "workstations".
- Actions are pinned to major tags (`@v5`, `@v6`), not commit SHAs. `pip install pytest` is unpinned.
- Fix:
  - Restrict auto-merge to patch and minor updates, and exclude the github-actions ecosystem.
  - Pin actions by full SHA.
  - Require branch protection with a human approval on `.github/**` changes.
  - Pin pytest with a hash.

M3. CI downloads and executes unverified third-party binaries (CWE-494, CWE-829; NIST SP 800-53 SI-7, SA-12).
- devkit-quality.yml `curl`s osv-scanner, gitleaks and vale release artifacts and runs them, with no checksum or signature check. Versions are pinned but the bytes are not.
- `npx --yes jscpd@5.3.2` pulls unpinned transitive dependencies on every run.
- The token is read-only, so the damage is limited to a poisoned CI result (a false "clean" from the secret scanner).
- Fix:
  - Verify the published SHA-256 or sigstore bundle for each download.
  - Use a lockfile for jscpd.

M4. Repo-controlled files can switch off the secret scanner (CWE-693; NIST SP 800-53 SI-4).
- gitleaks reads `.devkit/gitleaks.toml` and `.gitleaksignore` from the PR's own tree. A PR can allowlist its own leak.
- `DEVKIT_BLOCKING` is off by default, so osv-scanner, ruff and the other checks are advisory only. That is an insecure default.
- The always-failing secrets check is good, but its config is not trusted input.
- Fix:
  - Load the gitleaks config and ignore file from the base branch (`git show $base:...`).
  - Flip the blocking default to on.

LOW

L1. Elevated uninstall can delete a file through a user-controlled junction (CWE-59, CWE-367; ATT&CK T1574).
- uninstall.ps1 runs as admin. For every profile in ProfileList it runs `Remove-Item -Force` on `<profile>\AppData\Roaming\...\Startup\hello-world-daily.cmd`.
- A standard user owns that path tree and can make `AppData\Roaming` or `Startup` a junction to another directory.
- The admin then deletes a file named exactly `hello-world-daily.cmd` in an attacker-chosen directory. The name is fixed, so impact is narrow, but it is still an arbitrary-directory delete primitive running as admin.
- Fix: before deleting, walk each path component and skip any reparse point (you already have `Assert-NotLink`). Alternatively, load each user's hive and use `[Environment]::GetFolderPath` per user.

L2. File mode and link protections are weaker than the notes imply (CWE-732, CWE-379, CWE-59).
- `os.makedirs(mode=0o700)` does not tighten a folder that already exists.
- `os.replace` keeps the mode of the old file's replacement only because the new file is 0600. Pre-1.12 files and any `.bak` copies keep their old permissions, which on POSIX is usually the umask default of 0644.
- On Windows, `O_NOFOLLOW` does not exist and the 0o600 mode is ignored. The "never through a link, private" claim is POSIX-only. Privacy on Windows depends only on inherited folder ACLs, and the README should say so. The test only runs on POSIX.
- The temp name `notes.json.<pid>.tmp` is predictable. `os.remove` followed by `O_EXCL` is safe in a user-owned directory, but only there.
- Fix: `os.chmod(dir, 0o700)` and chmod existing files on POSIX. On Windows, set an explicit ACL, or document that the folder ACL is the only protection.

L3. Plan text is shown on screen at every open, including at sign-in (CWE-200, shoulder-surfing/screen-share exposure).
- The launcher opens at sign-in and prints `Still open from ...: <plan>` and `type same for: "<previous plan>"`. A plan the person typed once is displayed again, and a screen-share or projector shows it.
- The README warns people not to type private details, which partly covers this.
- Fix: truncate the hint, or show `previous` only on request.

L4. The embedded Python is pinned with no update path (CWE-1104; NIST SP 800-53 SI-2).
- The hash-pinned python-3.14.8 embed zip never auto-updates, and no CVE watch is described. Pinning is correct, but there is no process to move the pin.
- Fix: document who bumps it and how often. The osv-scanner step cannot see it because it is not a lockfile entry.

L5. The sign-in launcher is a user-writable persistence point (ATT&CK T1547.001; CIS Control 2). It is opt-in and only writes a path under Program Files. EDR will flag any process that edits it, and another process running as the same user can retarget it. That is the same privilege level, so it is not an escalation. Not a bug. Tell IT it exists, and consider checking in `remind()` that the target still resolves to the admin-owned hello.cmd.

L6. Damaged-file backups can accumulate. `.bak`, `.bak2` and so on are never limited, only deleted by menu option 4. A process running as the same user can fill the disk this way. Minor. Cap the number of backups.

CHECKED AND CLEAN
- **Untrusted notes.json** (CWE-150, terminal injection):
  - Every string goes through `tidy()` and `clean()`.
  - `isprintable()` removes ESC, CR, bidi controls and other Cf characters, except the ZWJ/ZWNJ that are allowed deliberately.
  - Dates go through `fromisoformat` and are re-serialised.
  - `done` is an int capped at 99999 and `offer_skips` is capped.
  - The file is limited to 1 MB.
  - Deep nesting (RecursionError), huge integers and MemoryError are caught.
  - Future-dated visits are set aside rather than trusted.
  - A test covers ESC injection.
- **Typed input:** the echo of an unknown word is run through `tidy()` and cut to 30 characters. `same` only substitutes stored, already-cleaned text.
- **Deserialization and injection:** JSON only. No pickle, eval, exec, subprocess or shell in hello.py. No SQL. No network code (SSRF, XSS and CSRF do not apply to this program).
- **Test hooks:** TODAY, HOME and FORCE_INTERACTIVE are module globals and are not read from the environment. A test proves the HELLO_* variables are ignored.
- **Launcher generation:** `remind()` rejects `"` and `%` in the target. The target comes from `__file__` in an admin-only folder. The file is written as ASCII.
- **Installer (install.ps1):**
  - The clone must be at the given 40-character commit, and the four key files are hash-compared to that commit.
  - The whole setup folder, Git's folders and the install tree must be admin-only. Reparse points are rejected, and parent folders are checked.
  - Tools are called by full path. GIT_* variables and HOME are cleared. Python is SHA-256 pinned, built and tested beside the old install, then swapped with rollback.
  - hello.cmd runs `python -I`.
  - The Start menu shortcut is ACL-checked after creation.
  - I found no TOCTOU between the check and use that a non-admin could exploit.
- **Registry and uninstall:**
  - The UninstallString points into admin-only Program Files.
  - The self-elevation in uninstall.ps1 re-runs the same admin-only script.
- **Workflows:**
  - Permissions are least-privilege.
  - The Dependabot check job uses a read-only token and the merge job never checks out code.
  - In the merge job, `needs: check` means it is skipped for non-Dependabot authors.
  - Untrusted values (`BASE_PR` and the like) are passed through `env`, not interpolated into scripts. The `${{ }}` expansions in run blocks are step outcomes and variables, not attacker text.
  - The `v$v` tag cannot be turned into a git option.
- **Secrets:** .gitignore covers the usual classes. I found none in the packet. The commit hash in the README is an obvious placeholder.

Not verifiable from the packet: the real Windows ACL behavior of notes.json, and the junction behavior in L1.

---

## Usability and retention reviewer

# Product review: hello-world 1.12.0 (ease of use and retention)

I read the whole packet except the tail of the installer, the tail of the tests (past line 2562) and uninstall.ps1. Neither affects first-run or return behavior. I used no other source.

## Verdict

This round fixes real friction. `same` is one word, wrong words now name the choices, and option 1 is a summary. Day-2 behavior is the best part of the product.

The product still has three gaps:

- It is unclear who it is for. A work PC that IT installed is an odd place for a habit tool. The audience is "any employee, any role", and the installer is built for IT, not for the person who has to want it.
- The retention hook only exists for people who type a plan on day 1. A person who presses Enter three times sees a date-chosen quote and tip, which they have no reason to open a second time.
- The reward comes a day late. Finishing a plan at 3pm earns nothing until tomorrow's prompt.

Retention is a release gate. I would not call this ready on retention grounds unless the same-day done loop and the recap below ship this round. Section 1 gives the full ordering.

## Findings

### High

**H1. Retention. A plan can only be marked done the next morning.**
- The only path to `done`, and so to the count and the "That is N plans" line, is the next-day "Did you do it?" prompt.
- Someone who finishes the plan at 2pm and reopens at 4pm sees "Your plan for today: ..." with no way to say it is finished. The natural return moment has nothing to reward.
- The done count also undercounts. Anyone who skips the next-day prompt with Enter, or whose window is closed by a launcher, never gets credit.
- Fix:
  - When today's plan is on screen, the last prompt becomes `Press Enter to close, or type done, plan or menu >`.
  - `done` marks it finished, shows a done line and the count, and moves it to `previous`.
  - Skip the next-day question for a plan already marked done.

**H2. Retention. Nothing accrues that a person would miss.**
- The saved state is one `previous` plan, a bare number and dates. A count is not an asset, and the project's own docs say so.
- After 30 days the person has lost nothing and gained nothing if they stop.
- `same` is the right idea, but it holds one remembered plan, not a history.
- Fix: keep a short private list of finished plans (see the retention feature below).

**H3. Ease of use and retention. People who skip the plan on day 1 get no reason to return.**
- First run is a long privacy paragraph (about 7 lines), a quote, a tip, a plan prompt, a sign-in offer and a close prompt. That is up to four questions in the first session.
- A plan is the only personal hook, and it is the third thing on screen.
- Anyone who skipped it has nothing to follow up on tomorrow, so they have no reason to open the tool again.
- Fix:
  - Shorten the first-run welcome to two lines plus "Type privacy for details". Do not remove the facts, since trust matters here.
  - Put the plan prompt first.
  - Give day-1 skippers a different day-2 hook. Ask "Anything you want to get done today?" with the plan-of-the-day idea, or show the quote and tip first and the plan prompt after.
  - Do not offer the sign-in launcher in the same session as the first plan. Offer it on the second visit, after the person has seen the follow-up work.

**H4. Ease of use. The fast path for a repeat plan is still a typed word.**
- A second session is faster, but it is still `same` plus Enter, typed from memory.
- Nothing teaches `same` at the moment of need except the small hint in the prompt, and it is the only place it appears.
- `same` with no previous plan is saved as the literal plan "same". A new user who tries it gets a plan that says "same".
- Fix:
  - Accept `s` as well as `same`.
  - Add an opt-in "Enter keeps yesterday's plan" setting, which makes a recurring plan zero keystrokes.
  - Reject `same` when nothing is remembered ("Nothing to repeat yet. Type a plan instead.").

### Medium

**M1. Ease of use. Text typed at the final prompt is thrown away.**
- A person who skipped the plan prompt and then types "call the bank" at the last prompt gets `That was not one of the choices` and the prompt again.
- They typed what they wanted, so the tool should honor it.
- Fix: if the text is longer than about 12 characters or contains a space and matches no command, ask "Save that as today's plan? (y/n, Enter = no)".

**M2. Ease of use. The next-day answer prompt is not fully fixed.**
- "maybe" or any unrecognized answer yields `Left as it was.` with no list of choices. This is the same problem the packet fixes at the last prompt.
- The plan then stays open, and tomorrow shows the same question.
- Fix: re-ask once with "y = yes, n = not yet, Enter = skip".

**M3. Retention. A skipped follow-up leaves a stale plan that nags.**
- Pressing Enter at "Did you do it?" keeps the old plan. The same-day reopen shows "Still open from <date>".
- A person who never answers sees the same old plan every day for two weeks, then loses it.
- That is the opposite of "welcome, never guilt".
- Fix: after two skips, say "Want to clear that one? (Enter = keep)", or fold it into the existing 14-day expiry earlier.

**M4. Retention and trust. The docs now contradict the code.**
- `PLAN.md` and `docs/WHY-DAILY-ACTIONS.md` still say "Any record of whether a plan was done" is kept out on purpose and that only the current plan and the dates are saved.
- The code saves `done` and `previous`.
- The README was updated, so the three documents disagree, and an IT or privacy reviewer will notice.
- This decision is also in tension with "A count is not value". It may well be right, since it is private and quiet, but the decision record should say so.
- Fix: update both documents and state why the done count is allowed.

**M5. Ease of use. Destructive-action safety is good but has no way back.**
- The delete prompt needs a clear `y`, which is right.
- Delete takes the history and `same` with it. The prompt says "all saved notes, dates and plans" but not that this includes the remembered previous plan and the done count.
- Fix: list what goes (for example "5 days, 12 finished plans"), and offer to keep the finished-plans list when someone is only clearing today's plan.

**M6. Ease of use. Discoverability depends on one line.**
- `plan`, `menu`, `same` and soon `done` all live at the last prompt.
- A person who presses Enter every day never learns them, and it is probably most people.
- Fix: rotate one tip line onto the screen on the 3rd and 7th visit ("Tip: type plan to set today's plan"), shown once.

**M7. Ease of use. `Closing` and `q` are accepted but not listed.**
- `x` and `close` also work but are undocumented. Fine as aliases, but the wrong-word message only says "Type plan or menu, or press Enter to close".
- `q` and `?` are in the README only.
- Fix: say "Type plan, menu or q" in the error text.

### Low

**L1. Ease of use. The `plan` path needs a second Enter to close.** A person who sets a plan then waits at "Press Enter to close >". It is right for screen readers, but it adds one keystroke every time. Skip it when stdout is a terminal that stays open, or fold it into the Saved line.

**L2. Retention. The sign-in offer is only visible on the Windows launcher path.** A person who declines never hears about it again. The "stops after three Enters" rule is reasonable, but a person who typed "not yet" is asked again, so the exits are inconsistent. Say plainly in one line when it will stop asking.

**L3. Ease of use. The expiry message is accurate but hard to read.** "Menu option 6 can bring it back: type same." reads like two steps. Say "Type same at the plan prompt to bring it back."

**L4. Retention. The 100-day content cycle is a quiet ceiling.** Content repeats every 100 days, which is fine for year one but feels like a loop at day 101. It is also the same text for everyone. This is a later problem, not a gate.

**L5. Ease of use. "Days you opened hello-world: N" in option 1 is a visit count.** The plan says visit counts are out of scope. It is private and factual, so it is fine, but remove "(last 7 days: N)" if the intent is no scoring.

**L6. Ease of use. Menu numbering skips 5 for help and 6 for the plan, and "Choose 1 to 6" lists a different order than the menu.** Declined in the backlog. I would accept the decline.

## Who is it for?

It is unclear. The README says "any age, any role", but the install path is an IT admin at a Windows workstation with Git. The employee never chooses it, which means the first run happens to someone with no intent.

The most credible user is an office worker who likes a two-minute morning ritual. Say so in `PLAN.md`, and give the pilot five people a one-line brief saying what it is for and how to say whether it helped. The no-telemetry decision means you will otherwise learn nothing.

## Retention feature to build this round: "This week" recap with a same-day `done`

Build `done` (see H1) and a private list of the last 14 finished plans with dates. Show a one-line recap the first time a person opens hello-world in a new week, and in option 1:

> Last week you finished 4 plans: Send the invoice, Call the bank, Book travel, and 1 more. Type recap to see them.

Why the person would come back because of it:

- It answers a question they already have every Friday and Monday: what did I actually get done? That is the sentence they need for a stand-up, a 1:1 or a status email.
- It builds an asset that grows. After two weeks the list is something they would lose by stopping.
- It rewards the real behavior, which is finishing a plan, not opening the program. It stays private, with no scores, and it is gone when they choose Delete everything.
- It fits the existing trust story because it uses `previous` and `done` data you already store, local only, shown only to the person.
- It gives the sign-in launcher a reason to exist. "Open at sign-in so it can show last week's wins" is a better offer than "so it can ask about your plan".

Keep it opt-out and easy to hide, like the in-a-row line. It has no streak language, and it says nothing to a person who finished nothing.

## Highest-leverage changes, most important first

1. Add same-day `done` at the last prompt (H1). It is the smallest change and makes every return visit rewarding.
2. Keep a private finished-plans list and the weekly recap (the retention feature above, H2).
3. Move the plan prompt up, shorten the first-run welcome, and move the sign-in offer to visit 2 (H3).
4. Make repeating a plan zero or one keystroke: `s`, an Enter-keeps-it setting, and reject a bare `same` with nothing to repeat (H4).
5. Honor text typed at the last prompt as a plan offer (M1) and list the choices at the follow-up prompt (M2).
6. Fix the contradiction between `PLAN.md`, `docs/WHY-DAILY-ACTIONS.md` and the code about saving done counts (M4), and write down who the product is for.
7. Show what delete removes, with counts (M5).

## Not verified

I did not run the program. Everything above comes from reading the code, the tests (to line 2562) and the notes. The developer reports no testing on Windows, with a real screen reader, or with pytest, and nothing here changes that.

---

## Accessibility reviewer

ACCESSIBILITY REVIEW, hello-world 1.12.0 (WCAG 2.2 AA; interface is a Windows console program, its CLI help, plain-text output, and the README/PLAN docs)

Sources: only the packet. I read the developer notes, README, PLAN, docs/WHY-DAILY-ACTIONS.md, hello.py in full, and the install.ps1 shortcut and hello.cmd lines. I did not read test_hello.py, uninstall.ps1 or the CI files line by line; they are not user-facing. I ran nothing. Findings come from reading the code.

VERDICT: No Critical findings, and the round-37 fixes are real improvements. The wrong-word loop cannot trap anyone, because every ask() failure path returns "" and breaks out. One gap is High. The error-identification fix was applied at one prompt only, and several other prompts and the menu still fail the person silently or without naming the choices. I recommend shipping this round with the "ship this round" items at the end.

---- FINDINGS ----

1. HIGH (process gate). Screen-reader flow is unverified (WCAG 4.1.3, 1.3.1, 2.4.3).
The README and PLAN now honestly say "designed for, not yet verified". But the release gate is that a screen-reader user can complete the flow, and nobody has checked it. The risky parts are specific.
- input() prompts end without a newline, and some contain an embedded "\n" (the plan prompt). conhost and Windows Terminal announce these differently under NVDA, JAWS and Narrator.
- Prompts end in " > ", which may be read aloud as "greater than".
- The option-1 `full` JSON dump is read punctuation by punctuation.
Fix: before wide rollout to the five employees, run the full flow with NVDA and Narrator on conhost and Windows Terminal. The flow is first run, plan, same, wrong word, q, menu, 1, full, 4. Record the results in PLAN.md. Until then, keep the "not verified" wording and tell IT it applies. This is a release-process action, not a code change.

2. MEDIUM. Error identification is inconsistent: the menu still gives a generic error (WCAG 3.3.1, 3.3.3).
The final prompt now names the bad word and lists choices. The menu's else branch says only "Please type a number from 1 to 6, or press Enter." It does not name the word. It also rejects `q`, `quit`, `exit`, `help` and `?`, which the final prompt, README and the new error message teach people to use. A person who types `q` in the menu is told it was not a number. A person who types `help` in the menu does not get option 5.
Fix: in menu(), accept q/quit/exit as Enter and help/? as option 5. Change the error to `That was not one of the choices: "x". Type 1 to 6, or press Enter to close.` Use one shared helper for both loops.

3. MEDIUM. Unrecognised answers are silently treated as a choice at three y/n prompts (WCAG 3.3.1, 3.3.3, 3.3.4).
- "Did you do it?" Any word other than y/n (for example "yse" or "yes!!" typed wrongly) prints "Left as it was." and the plan is kept. The person is not told the answer was not understood and cannot retry. The prompt says "Enter = skip" but not what other words do.
- "Keep it for today?" Anything other than a no keeps the plan. This is safe but silent.
- The sign-in offer. A typo such as "yse" prints "Okay. Menu option 2 turns it on any time." It also counts toward the three-skip limit. The person believes they answered. The note's own lead 11 fixed "not yet" here; the typo case is the same shape.
Fix: for an unrecognised, non-empty answer, print `That was not one of the choices: "xyz". Type y or n, or press Enter to <skip/keep/ask later>.` and ask again, at most twice. Do not count it as a skip.

4. MEDIUM. Typing `same` with no previous plan saves the literal plan "same" (WCAG 3.3.1, 3.3.4).
reuse() returns the raw text when there is no previous plan, so the plan becomes the word "same". The hint only appears when previous exists, so this path is reachable by anyone who read the README first. Fix: if the word is "same" and there is no previous plan, say `There is no earlier plan to reuse.` and ask again. Do not save.

5. MEDIUM. The plan prompt is long, unwrapped, and has stacked parentheses (WCAG 1.4.10 reflow and 3.3.2 by analogy).
The prompt is `Type today's plan (Enter keeps it as it is) (type same for: "<up to 120 chars>") > `. It goes into input() as one line, so the console breaks it mid-word at any width or zoom. Zoomed or narrow windows and screen magnifiers get the worst of this. The daily-screen variant also puts the old plan after "type same for:" on a single line.
Fix: print the previous plan with say(wrapped('Earlier plan: ', ...)). Then use a short prompt: `Type a plan, same to reuse it, or Enter to keep > `.

6. MEDIUM. "Only you can see this" is false and contradicts the README (WCAG 3.3.2 and trust; understandable information).
show_saved() prints "Only you can see this. It never leaves this computer." The README, first-run welcome and PLAN say IT staff who can read the files could read it. Someone who hears only option 1 may type private details. This is the one place the person is checking privacy, and it contradicts the other statements.
Fix: `It never leaves this computer. Others who can read your files, such as IT staff, could read it.`

7. MEDIUM. Docs contradict the new behaviour, and the README paragraph is a wall of text (WCAG 3.1.5, 1.3.1 by analogy).
- PLAN.md says "Any record of whether a plan was done" is kept out and that the program saves only the current plan, the dates and the streak setting. That is now false, because `done` and `previous` are saved.
- PLAN.md and WHY-DAILY-ACTIONS.md say option 1 shows "a cleaned copy". It now shows a summary first.
- README line 511 packs about eight behaviours into one paragraph. The "Coming back" bullet is garbled: "On right after you save your first plan, and on later visits...". A word is missing, so the sentence cannot be understood. README line 534 has a nested parenthetical that is hard to follow with a screen reader.
Fix: update PLAN, WHY-DAILY-ACTIONS and CHANGELOG. Split README line 511 into a short list (close, plan, menu, quit, help). Repair the broken bullet. Move the saved-file list out of the parenthesis into bullets.

8. LOW. Prompt wording for Enter is inconsistent (WCAG 3.2.4 by analogy, 3.3.2).
The prompts say "Enter keeps it as it is", "Enter = keep", "Enter = skip", "Press Enter to skip", "Enter to ask me later" and "Press Enter to close". Pick one pattern, for example `Enter = <action>`, and use it everywhere. Also decide whether "Press" is part of it.

9. LOW. The error text echoes a lowercased, truncated word.
tidy(answer)[:30] shows the word after .lower(), and it is cut at 30 characters with no marker. Keep the original case, and add "..." when it is cut. If the person pasted a long line, tell them it was long.

10. LOW. The final prompt hides its own shortcuts.
The prompt advertises only plan and menu. q, quit, exit, help and ? are in the README and the error text only. This is acceptable, but add "or q" to the error message list, since that message is the discovery point.

11. LOW. Stale or missing menu help text.
MENU_HELP says option 1 "shows exactly what is saved", but it is now a summary and `full`. It omits the `full` option, omits q/help/?, and omits that option 5 exists. The summary omits the saved `offered` and `offer_skips` fields, so "exactly" is wrong for the summary. Say "shows a short summary, and the whole file if you type full".

12. LOW. `--stats` mixes prose and JSON for scripts (CLI interface, WCAG 4.1.2 equivalent).
The notes say `--stats` "prints everything for scripts", but show_saved(full=True) prints sentences and then the JSON. A script cannot parse the output. Either add `--stats --json` that prints only the JSON, or change the notes and README wording.

13. LOW. Language (WCAG 3.1.1, 3.1.2).
Console text has no language attribute. English only is stated in the README, so there is no violation. Keep the statement and note it in the screen-reader test results.

14. LOW. Installer colour (WCAG 1.4.1).
Write-Host uses Cyan for steps and Red for FAILED. The text "FAILED:" and "[n/6]" carry the meaning, so colour is not the sole cue. This is admin-facing and passes; no change needed. Keep the textual prefix.

Not applicable or passing:
- Target size, motion and timing: no pointer targets, no animation, no timeouts. Pass.
- Keyboard operability: everything is Enter and typed words, with Ctrl+C documented. Pass.
- Focus order: linear, with one prompt at a time. Pass.
- Non-colour cues: the program output is plain ASCII. Pass.
- Destructive action: delete needs a clear y and "done" no longer counts (WCAG 3.3.4). Pass.
- Windows window closing: the program holds the window with Enter, and the shortcut pauses on failure. Pass, still unverified on Windows.

---- ACCESSIBILITY IMPROVEMENTS TO SHIP THIS ROUND ----
1. Finding 2: make the menu accept q/quit/exit and help/?, and name the typed word in its error. Same helper as the final prompt. About ten lines, one test each.
2. Finding 3: name the word and re-ask at "Did you do it?", "Keep it for today?" and the sign-in offer. Do not count it as a skip.
3. Finding 6: correct "Only you can see this".
4. Finding 4: handle `same` with no previous plan.
5. Finding 7: fix the garbled README bullet and the PLAN/WHY-DAILY-ACTIONS statements that are now false.
6. Finding 5, if time allows.
Finding 1 (a screen-reader pass) is a gate before rollout, not a code change this round.

Files reviewed: the review packet (hello.py lines 755-1753, README lines 487-616, PLAN lines 408-485).
