# Round 40 review

- Date: 2026-10-02
- Commit reviewed: 56affef5422eeff208fe9fcffa11ba9e54ccf2bc
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1, plus the newest CHANGELOG entry as developer's notes. Every reviewer got the full packet.
- Agents that ran: lead, security, usability and retention, accessibility.
- Redactions: none needed; no reply named a model or vendor.

## Lead reviewer

# Review of hello-world 1.14.0 (round 40)

I read the whole packet. `CHANGELOG.md`, `BACKLOG.md`, `reviews/round-39.md`, `.devkit/*` and `hello.cmd` are cited in the notes and README but are not in it, so I could not check those claims. I also could not run anything. Everything below comes from reading the code and tests, and I traced the tests by hand.

The two flagship fixes are only partly delivered. The stale-state fix has a gap that makes it largely ineffective. The "last prompt comes back after the menu" claim is wrong for the menu.

## Part 1: Findings, most severe first

No Critical findings.

### 1. High, bug (data loss): the stale-state fix refreshes before the prompt, not after
- **Where:** `set_plan()` in `hello.py`, packet lines 1493-1528.
- **What happens:** `set_plan` calls `refresh()`, captures `old`, then blocks in `ask()` for however long the person takes to type. It then applies the change to that stale snapshot and saves.
  - A second window that saves during the prompt gets overwritten.
  - `daily()` is worse. Its main save (lines 1762-1766) and `offer_reminder`'s save never call `refresh()`.
- **Why it is likely:** The sign-in launcher opens a window at every sign-in, and it sits at the plan prompt until someone answers. If the person opens hello-world again from the Start menu and finishes there, the first window's later Enter silently overwrites the newer window's plan, `previous`, `done`, `offered` and `offer_skips` with its stale copy.
- **Why the test does not catch it:** `test_a_second_window_cannot_overwrite...` covers only `mark_done_now`, where refresh and save are back to back. Nothing exercises a change between refresh and save.
- **Fix:**
  - Re-read immediately before applying the change, after the prompt returns, and apply the change to the fresh state. Do the same in `daily()`'s save and in `offer_reminder`.
  - Better still, make a single `update(fn)` helper that does load, mutate, save with no prompt inside it.
  - Add a test that changes the file from a second state between prompt and save.
  - Until then, soften the README sentence "one window cannot overwrite the other".

### 2. Medium, bug: the menu falls through to `break`, so closing the menu closes the window
- **Where:** `daily()` last-prompt loop, lines 1798-1800.
- **What happens:** The `plan` and `done` branches end in `continue`. The menu branch does not, so after `menu()` returns the loop breaks and the program exits.
  - The `intent = state["intent"]` line after `menu()` is dead code, which suggests a missed `continue`.
- **Claim vs. code:** The developer notes say "after `done`, `plan` and the menu the full last prompt comes back". That is not true for the menu.
- **Consequences:**
  - Enter at the menu ends the session.
  - A plan set through menu option 6 cannot then be marked `done` in the same sitting.
  - The result of an action such as "Everything saved was deleted" is followed by one more menu redraw and then the window vanishes.
  - `MENU_HELP` says Enter "closes" the menu, so it is unclear which meaning applies.
- **Fix:** Add `continue` after `menu()`. Reword `MENU_HELP` to "Enter returns to the last prompt". Add a test where `m`, then Enter, is followed by `done`.

### 3. Medium, accessibility and ease of use: "Enter = close" at the next-plan prompt is false
- **Where:** `set_plan(after_done=True)`, line 1504, and README line 503.
- **What happens:** The prompt says `Type the next plan ... or Enter = close`. Enter prints "Nothing changed." and returns to the last prompt, so the window stays open until a second Enter.
- **Why it matters:** A screen-reader or keyboard-only user is told one thing and gets another. "Nothing changed." is also wrong right after a `done`.
- **Why the test hides it:** `test_after_done_enter_just_closes...` feeds two Enters. With one Enter, EOF would also close the window, so the label is never really tested.
- **Fix:** Either make Enter in the `after_done` flow close (have `set_plan` return a "close" flag), or change the prompt text to "Enter = go back". Drop "Nothing changed." in that flow, and fix the README and the test to match.

### 4. Medium, accessibility: the reflow claim is overstated
- **Where:** README lines 510-511 and the developer notes.
- **What is not reflowed:** Only `wrapped()` and `indent()` follow `width()`. These are hard-wrapped at 72 characters or by hand:
  - the first-run welcome and privacy text (lines 1679-1685);
  - the expired-plan notice;
  - the damaged-file notice (`textwrap.fill(..., 72)` at line 1163);
  - `HELP`, `MENU_HELP` and the menu lines;
  - the `show_saved` lines.
- **Long single lines left to the terminal:** `is_command`'s message (about 110 characters), the sign-in offer prompt, and other prompts.
- **Effect:** At a narrow window or large font, the privacy text and error messages are the ones that break raggedly mid-word.
- **Fix:** Route every multi-sentence message through one `say_wrapped()` helper that uses `width()`. Add a test at 40 columns over the first-run, help and menu output.

### 5. Medium, security (installer): the README clones with Git before the Git folders are checked
- **Where:** README lines 565-576. This is installer scope, which the notes decline for now.
- **What happens:** The admin runs `git clone` before `install.ps1` verifies that Git's folders and `C:\ProgramData\Git` are admin-only. It also runs with the admin's `GIT_*`, `HOME` and system config still in the environment.
  - A writable `C:\ProgramData\Git\config` could execute code as admin during the clone, which is earlier than any check.
  - `install.ps1` clears the environment and checks the ACLs only afterwards, which is too late for this step.
- **Fix:** Put a short ACL check on Git's folders (or a `-c core.fsmonitor= -c core.sshCommand=` hardening note) before the clone in the README steps. Or have the installer bootstrap from a one-liner that does both.

### 6. Medium, retention and ease of use: the sign-in offer comes back after the person turned the launcher off
- **Where:** `offer_reminder` (line 1585) and menu option 2.
- **What happens:** `remind(False)` does not set `state["offered"]`. Someone who turns the launcher on and then off through the menu, or through `--remind off`, before ever answering the offer is asked again on the next visit, up to the skip cap.
- **Why it matters:** The program overrides an explicit choice, which is the nagging the design says it avoids.
- **Fix:** Set `offered = True` whenever the person explicitly toggles the reminder through option 2 or the `--remind` command.

### 7. Medium, process: CI and Dependabot (declined in the notes, but in the packet)
- **Auto-tag:** `auto-tag.yml` tags any `main` push whose VERSION has no tag, with no test gate. A tag, and so a "reviewed release", can exist for a commit whose quality or tests failed.
- **Auto-merge:**
  - `dependabot-automerge.yml` auto-merges major updates by design. It runs the updated code on `pull_request`, which is acceptable with a read-only token.
  - Whether the merge job's write `permissions` are honored for Dependabot-triggered runs is something I could not verify. If they are not, merges fail silently.
  - There is no `dependabot.yml` in the packet, so the workflow may never fire.
- **Supply chain:** `devkit-quality.yml` downloads osv-scanner, gitleaks and vale binaries with `curl` and no checksum, and pins actions by tag, not by SHA.
- **Fix:**
  - Require the quality and test workflow to pass before tagging.
  - Verify downloaded binaries against published checksums.
  - Pin actions by SHA.
  - Confirm one Dependabot PR actually merges.

### 8. Low, retention and honesty: the content docs are stale
- **Where:** `hello.py` comment at line 785, `PLAN.md`, `README.md`, and `docs/WHY-DAILY-ACTIONS.md`.
- **What happens:** They still say "100 thoughts, repeat every 100 days". There are now 101 thoughts and 100 tips, so each list repeats on its own cycle and only the pairing is long.
- **Fix:** Update the docs.
- **Related test fragility:** `test_thoughts_and_tips_do_not_repeat_as_a_pair_every_100_days` asserts only `len() !=`. Adding two tips would give gcd 2 and a pair cycle of 5,100 days.
  - **Fix:** Assert `math.gcd == 1` instead.

### 9. Low, bug: the thought/tip duplicate guard test no longer tests what is shown
- **Where:** `test_thought_and_tip_never_repeat_each_other_on_one_screen`.
- **What happens:** It still pairs `TIPS[i]` with `THOUGHTS[(i+37)%len]`, which no longer matches the real pairing. Real pairs now vary over the 10,100-day cycle.
- **Examples:** "Close the tabs…" with "Close the browser tabs…", and "Unclench your jaw" with the same tip, can land together.
- **Impact:** Each such pair shows about once per 27 years, so the risk is small.
- **Fix:** Compute pairs the way the program does, and check them for keyword overlap.

### 10. Low, bug: the "command word" guard lectures people who answer "no" or "none"
- **Where:** `COMMAND_WORDS` and `is_command`.
- **What happens:** Someone who answers "What is one thing you want to get done today?" with "no", "none" or "nothing" is told "That looks like a command, not a plan, so nothing was saved. Type plan at the end…". That reads as an error. Typing `q` expecting to quit does not quit either.
- **Fix:** Treat no/none/nothing/skip/n silently as a skip. Keep the message only for menu/done/plan/help/q. Say "Typed q? Press Enter at the last prompt to close."

### 11. Low, ease of use: the last prompt is stricter than the other prompts
- **Where:** `daily()` last-prompt loop, line 1787.
- **What happens:** `Done.`, `DONE!` and `plan.` are rejected, because there is no `strip(" .!")` as in `is_yes`. `same` is rejected, even though the person was just told to type it. `x` and `close` work but are never listed.
- **Fix:** Normalise the same way everywhere. Accept `same` at the last prompt as a shortcut to `plan` followed by `same`.

### 12. Low, bug: Ctrl+C at a yes/no prompt is reported as "not understood"
- **Where:** `daily()`, line 1717.
- **What happens:** `ask()` returns `None` for Ctrl+C or EOF. `ask_choice` returns `None`, and `daily()` prints "That was not understood" for that case too.
- **Fix:** Distinguish a cancel from three misunderstood answers (a sentinel for each).

### 13. Low, bug: edge cases in save, can_save and refresh
- **`refresh()` ignores a damaged file:** `refresh()` returns silently when `load(repair=False)` reports damage, so `can_save` stays `True`. The next `save()` can then overwrite a file another process just damaged, with no backup.
- **`can_save` stays `False` after reset:** After `reset()` in the menu, `can_save` stays `False` if it started `False`. Saves are then refused even though the file is gone.
- **Windows save retry:** `os.replace` can fail briefly on Windows while antivirus holds the file, and there is no retry. The person sees "Could not save" on a transient lock.
- **Orphan `.tmp` files:** Killed saves leave `notes.json.<pid>.tmp`, which can hold plan text and is only removed by reset.
- **Fix:**
  - Propagate the refresh result to `can_save`.
  - Retry `os.replace` three times at 100 ms intervals.
  - Sweep stale `.tmp` files at load.

### 14. Low, bug: the plan is not shown when Enter keeps an older plan
- **Where:** `set_plan`.
- **What happens:** It prints "Your plan for today" only when `old["date"] == iso`. With an older open plan the prompt says `Enter = keep` while showing nothing to keep.
- **Fix:** Print the plan, with its date, in that case too.

### 15. Low, accessibility: fixed English-only content and wording
- `Cf` characters such as the RLM/ALM marks are stripped, which can damage right-to-left plans (`tidy`).
- A 120-character cut can split an emoji sequence.
- Text such as "biscuits" and "nine o'clock" is region-specific.
- **Fix:** Cut on grapheme boundaries if feasible. Keep RLM/LRM. Neutralise the regional examples.

### 16. Low, test hygiene
- `test_wrapping_follows_a_narrow_window` replaces `shutil.get_terminal_size` on the real global `shutil` module and never restores it. It leaks into later tests under pytest.
- `test_after_done_enter_just_closes` and `test_command_words...` pass for the wrong reasons.
- **Fix:** Use try/finally or monkeypatch for the leak. Use exact inputs that fail if Enter does not close.

### 17. Low, documentation and usage
- The README and `install.ps1` ship a dummy commit hash, which is safe because it fails. The doc test checks only the tag.
- `HELP` omits `m`, `?`, `same` and `--startup`.
- The menu numbering (1-5, then 6 for "plan") and the order are odd, and "Choose 1 to 6" is longer than needed.
- `Done.` after `done` is confusing in "Done. Your plan for today is saved."
- **Fix:** Use "Saved." there. Put plan first in the menu. Update `HELP`.

### 18. Low, installer (needs Windows to confirm)
- The pinned Python 3.14.8 embed zip and its SHA-256 are unverified, and the notes say 3.14 was never run. `install.ps1` runs only `--plain`, so the Windows `ctypes` and `msvcrt` branch in `interactive()` is never exercised. The code falls back to `isatty`, so the effect is limited.
- I could not verify the hash.
- The first real install on a clean PC is still the single biggest untested risk.

## Part 2: Improvements, most important first

1. **Retention: add a "where I left off" note (a new feature).**
   - **What to build:** One of the tips already says "Draft a short note to future you about where you left off today." Offer a one-line note at the closing prompt, store it (about 120 characters, listed in `--stats`), and show it above the thought next morning as "Note from yesterday". Treat `done` and the note as one small habit loop.
   - **Why it matters:** This is real personal value that exists only on the next visit, and it is a reason to come back that no content rotation provides. It is local, optional and low cost.

2. **Retention: lift the 100-day ceiling on content and make it refreshable.**
   - **What to build:** Grow the lists toward 365 or more with coprime lengths, and let IT drop an optional `extra-tips.txt` next to `hello.py` (admin-only folder) that is merged in. Show the date's weekday flavour such as "Friday wrap-up" for a little variety.
   - **Why it matters:** By day 100 a daily user has seen everything. An update today means an admin delete, re-clone and reinstall, which will not happen, so the content is effectively frozen.

3. **Accessibility: add a setting for a calmer, number-driven interface.**
   - **What to build:** A remembered "simple mode" (menu option and `--simple`). At the last prompt it uses one-key numbered choices (1 Close, 2 Plan, 3 Done, 4 Menu). It does not repeat the long prompt after each result. All text goes through the single reflow helper.
   - **Why it matters:** This removes the typed-word vocabulary for screen-reader, low-vision and motor-limited users. It also makes the Enter-closes behaviour trivially predictable.
   - **Verification:** Do a Narrator and NVDA pass on a real Windows machine before claiming it works.

4. **Accessibility: normalise and widen what the prompts accept.**
   - Accept `Done.`, `Same`, `x`, `close`, and `y/n` variants in one `normalize()` function used by every prompt.
   - List what is accepted.
   - Treat Enter the same way everywhere, with one rule, "Enter always leaves the current question".

5. **Ease of use: make "Enter closes" true everywhere, and shorten the loop.**
   - After `done`, the next plan prompt should close on Enter.
   - Print a one-line "Closing." as the last line so the exit is audible and visible.
   - Skip the redundant last prompt when nothing has changed since the previous one.

6. **Retention: revisit the declined weekly view in its smallest form.** Show "Finished this week: N" only inside the `done` message and in menu option 1. It adds no new prompt and no pressure, and it gives the plan loop a visible payoff beyond the current "That is 2 plans you have finished."

7. **Product direction.**
   - **What it is for:** It is a personal daily check-in for office employees, a thought plus one small thing plus one plan. That is clear enough.
   - **What is out of proportion:** About 650 lines of hardened PowerShell protect about 200 short strings. The retention levers are thin: static content, a plan that matters only if the person types it, and a window that exists only if someone opens it.
   - **What to do:**
     - Run the pilot with the five employees for two weeks with a fixed two-question check-in. The program cannot report, so this is the only measurement.
     - Decide with real data whether a terminal window is the right surface. A Start-menu page or toast would be easier for the least technical users.
     - Keep the scope small until the pilot says the content is wanted.

8. **Process.**
   - Fix findings 1-3 before shipping; they are small and each removes a claim the notes and README currently make but the code does not keep.
   - Add tests that assert the claims: the second-window change between prompt and save, the menu returning to the last prompt, and one Enter closing after `done`.
   - Run the real Windows install and the screen-reader pass before the pilot.

## Security reviewer

# Security review: hello-world 1.14.0

I read the whole packet: the developer notes, the 3 workflows, `hello.py`, `install.ps1`, `uninstall.ps1`, the tests and the docs. There are no Critical findings. There is 1 High, 3 Medium and 5 Low or Informational.

## Findings

### 1. High: the README clone step runs Git as admin before the installer's Git checks
- **Reference:** CWE-427, CWE-426, CWE-269. MITRE T1068 and T1574. NIST AC-6 and CM-5. CIS Windows hardening.
- **Where:** the README and the `install.ps1` `.EXAMPLE`. The sequence is `& $git clone ... $d`, then `cd $d; .\install.ps1`.
- **What goes wrong:** `install.ps1` is careful to prove Git's folders are admin-only, to clear `GIT_*`, `HOME` and `XDG_CONFIG_HOME`, and to set `GIT_CONFIG_NOSYSTEM`. All of that happens in step 1 of the installer. The `git clone` that fetches the installer runs earlier, as the elevated admin, with none of those protections.
- **Attack:** the stated threat model is a standard-user employee on the same PC. Git for Windows also reads `C:\ProgramData\Git\config`. If that folder is absent, a standard user can create it, because ProgramData lets Users create subfolders. A config there can set `init.templateDir` so a `post-checkout` hook runs during the clone, as admin. It can also set `core.sshCommand`, `http.proxy`, `url.*.insteadOf` or `credential.helper`. The admin's own `GIT_*` variables are also trusted.
- **Why the commit pin doesn't help:** the later commit-hash check stops a tampered source from being installed. It does not stop code execution at clone time, and the hooks stay in the clone's `.git`.
- **Fix:**
  - In the README, before the clone, set `$env:GIT_CONFIG_NOSYSTEM='1'`.
  - Remove the `GIT_*`, `HOME` and `XDG_CONFIG_HOME` variables.
  - Run the clone as `git -c core.hooksPath=NUL -c init.templateDir= clone --template= ...`.
  - Have the README verify that `$git` is under Program Files and that `C:\ProgramData\Git` is admin-only before running it. A small bootstrap script would be better than pasted lines.

### 2. Medium: Dependabot auto-merge gate proves nothing about the update
- **Reference:** CWE-494, CWE-1357. OWASP A06 and A08 (CI/CD supply chain). NIST SA-12 and SI-7.
- **Where:** `dependabot-automerge.yml`.
- **Problem 1:** it merges major updates immediately with `gh pr merge --squash`, with no `--auto`. The only gate is that `pytest` runs `test_hello.py`.
- **Problem 2:** this repo has no `package.json` or requirements file. `test_hello.py` imports no third-party code. So any Dependabot PR passes, including GitHub Actions major-version bumps if the `github-actions` ecosystem is enabled. The Python and Node paths in the check never run, and the code under test never exercises the dependency being changed.
- **Problem 3:** Dependabot-authored PRs are accepted by login only. Anyone with write access can push extra commits to a Dependabot branch and still get it merged.
- **Problem 4:** `actions/checkout` persists the token during `npm ci` and `pip install`, which run lifecycle and build scripts.
- **Problem 5:** `pip install pytest` and `pip install -r requirements.txt` are unpinned and have no hashes.
- **Fix:**
  - Don't auto-merge majors. Restrict to patch and minor using `dependabot/fetch-metadata` `update-type`.
  - Merge with `--auto` so required status checks and branch protection decide.
  - Add a ruleset on `main` that requires `devkit-quality`.
  - Never auto-merge changes under `.github/`.
  - Use `persist-credentials: false`, `npm ci --ignore-scripts`, and `pip install --require-hashes`.
  - Also check `github.actor == 'dependabot[bot]'`.

### 3. Medium: workflow actions are not pinned and `auto-tag` holds a write token
- **Reference:** CWE-829, CWE-494. OpenSSF Scorecard "Pinned-Dependencies". NIST SA-12.
- **Where:** `actions/checkout@v5`, `setup-node@v5` and `setup-python@v6` use mutable tags in all three workflows. `auto-tag.yml` runs with `contents: write` on every push to `main`.
- **Problem:** combined with finding 2, a retagged upstream action runs with write access, and a Dependabot PR can bump it with no human review.
- **Fix:** pin every action to a full commit SHA with a version comment. Keep Dependabot, but make it open the PR and require a human review for workflow files.

### 4. Medium: release tools are downloaded with no integrity check, and scanners fail open
- **Reference:** CWE-494, CWE-1188 (insecure default). NIST SI-7 and SA-12.
- **Where:** `devkit-quality.yml`.
- **Download problem:** `curl ... | tar -xz` fetches osv-scanner, gitleaks and vale release binaries by version only. There is no checksum or signature verification, and the gitleaks and vale archives are piped straight into `tar`. These binaries read the full git history, including anything gitleaks flags.
- **Fail-open problem:**
  - osv, ruff, lint, jscpd, dupes and Vale all use `continue-on-error: ${{ vars.DEVKIT_BLOCKING != 'true' }}`. A fresh repo is therefore report-only for known-vulnerable dependencies.
  - Separately, osv exits 128 when there are no lockfiles, which this workflow treats as success. This repo has no lockfiles, so the dependency scan checks nothing.
- **Fix:**
  - Download to a file, verify against a pinned SHA-256 (or `cosign` or `gh attestation verify`), then extract.
  - Default `DEVKIT_BLOCKING` to on, or make osv blocking regardless.
  - Add a lockfile, or record that this scan is a no-op here.

### 5. Low: the bundled Python 3.14.8 has no update or vulnerability tracking
- **Reference:** CWE-1104, CWE-1395. OWASP A06. NIST SI-2 and RA-5.
- **Where:** `$pyUrl` and `$pySha256` in `install.ps1`.
- **Problem:**
  - The runtime is a pinned embeddable zip, with its bundled OpenSSL, zlib and expat. Nothing in the repo notices a CVE in it. osv-scanner cannot see it, and Dependabot cannot update a hard-coded URL.
  - The hash is trusted as pasted. Nothing at install time verifies the `.sigstore` bundle it came from.
  - The developer notes say 3.14 was never run, only 3.11 on Linux.
- **Fix:** add a scheduled job that fails when 3.14.x is superseded or a CVE is listed for it. Verify the sigstore bundle when updating the pin. Run the test suite under 3.14 on Windows before release.

### 6. Low: "one window cannot overwrite the other" is overstated
- **Reference:** CWE-362, CWE-367. NIST SI-7. This is an integrity issue, not a confidentiality one.
- **Where:** `daily()` in `hello.py`.
- **Problem:**
  - `daily()` loads state once at the start. It then waits on prompts and saves the whole stale state at the final `save(state)` at line 1766. The `offer_reminder` save has the same problem.
  - The `refresh()` calls were added only on `done`, `plan` and menu option 3. There is no lock or version check, so the read-then-write window remains.
  - A concurrent second window's plan, done count or `previous` is overwritten by the first window's later save. The first-visit path is the most exposed.
  - `refresh()` silently keeps stale state when the file has become damaged (`ok` is False). The next `save()` then overwrites it with no `.bak` copy.
- **Fix:** re-read inside `save()` immediately before writing, and merge. Add a monotonic `rev` field that is compared before `os.replace`. Take a lock file or `msvcrt.locking`. At minimum, soften the README claim.

### 7. Low: elevated uninstall deletes files through user-controlled paths
- **Reference:** CWE-59, CWE-61, CWE-367. MITRE T1574.
- **Where:** `uninstall.ps1`, the profile loop.
- **Problem:** as admin it runs `Remove-Item -LiteralPath <profile>\AppData\...\Startup\hello-world-daily.cmd` in every profile. A standard user controls those directories and can replace a path component with a junction. The elevated process then deletes a file with that fixed name wherever the junction points.
- **Impact:** limited, because the filename is fixed. It is still an elevated filesystem operation on attacker-influenced paths.
- **Fix:** skip a candidate if any path component is a reparse point. Or use `-Force` only after checking `Attributes -band ReparsePoint` on each parent.

### 8. Low: sign-in launcher points at wherever `hello.py` happens to be
- **Reference:** CWE-426. MITRE T1547.001 (Startup folder). It is opt-in, and it is a per-user, same-privilege action.
- **Where:** `remind()` in `hello.py`.
- **Problem:**
  - It writes `start "hello-world" "<dir of __file__>\hello.cmd"` into the user's Startup folder. When the installed copy is used, the target is admin-owned, so this is fine.
  - If `hello.py` is run from a user-writable copy, the persistence entry points at user-writable code. The `"` and `%` guard is good, but it does not check that the target exists or lives under Program Files.
- **Fix:** only create the launcher when the target is the installed `%ProgramFiles%\hello-world\hello.cmd`.

### 9. Low / Informational: data at rest
- **Reference:** CWE-312, CWE-276, CWE-922. NIST SC-28.
- **Where:** `save()` and `data_dir()` in `hello.py`.
- **Problem:**
  - Plans are stored in plaintext and `.bak` and `.tmp` copies persist. This is documented honestly in the README.
  - `os.makedirs(mode=0o700)` and `0o600` do nothing on Windows. Privacy depends on `%LOCALAPPDATA%` ACL inheritance. If `LOCALAPPDATA` is unset, the path falls back to `~`, which may be a redirected or roaming share.
  - `O_NOFOLLOW` does not exist on Windows.
- **Fix:** prefer failing over falling back to `~` on Windows. Consider tightening the ACL on the folder with `icacls` at first save.
- **Also:** test hooks (`TODAY`, `HOME`, `STARTUP_DIR`, `FORCE_INTERACTIVE`) are module globals in production code. They are not reachable under `python -I`, and a test confirms the environment is ignored, but they widen the attack surface for any future importer.

## What I checked and found clean
- **Injection:**
  - `hello.py` has no `eval`, `exec`, `subprocess` or `os.system`. The `hello.cmd` and startup `.cmd` lines are built from fixed strings plus a path that is rejected if it contains `"` or `%`.
  - Terminal-escape injection from `notes.json`, plans and argv is neutralised by `tidy()`, which strips C0 and C1 controls and bidi characters. The JSON dump of controls is escaped, and there is a test for it.
- **Deserialization:** JSON only, with a 1 MB cap, `RecursionError` and `MemoryError` handling, integer caps, and strict validation of every field. Unknown keys are dropped, so there is no pickle, YAML or arbitrary-object path.
- **Path traversal and symlinks:** the data path is fixed. The temp file uses `O_EXCL` plus `O_NOFOLLOW` on POSIX. Reset only removes `notes.json`, `.bak*` and `.tmp` entries in its own folder. The installer rejects reparse points across the whole tree.
- **SSRF and network:** `hello.py` makes no network calls. The only fetch is the installer's fixed python.org URL, followed by SHA-256 verification.
- **Secrets:** none found in any file. The commit-hash value in the README is an obvious placeholder, and `.gitignore` covers `.env`, `*.key`, `*.pem` and `*.har`. gitleaks blocks regardless of `DEVKIT_BLOCKING`.
- **Installer integrity:**
  - Source is pinned by commit and each installed file is hash-compared with `HEAD`.
  - The Python download is hash-pinned.
  - Build and test happen in an admin-only side folder, and the swap rolls back on failure.
  - Python runs with `-I`, `hello.cmd` uses absolute paths, and the shortcut ACL is verified.
- **Web classes (XSS, CSRF, authn and authz):** there is no web surface, session, or multi-user service. The privilege boundary is the admin-owned install folder versus a user-owned data folder, covered above.
- **Workflow expression injection:** not present. Untrusted values are passed through `env:`, and the `${{ steps.*.outcome }}` interpolations are fixed enumerations.

## Usability and retention reviewer

# Product review: hello-world 1.14.0 (Round 39)

I read the whole packet: the developer notes, README, PLAN, WHY-DAILY-ACTIONS, hello.py, test_hello.py, the installer and uninstaller, and the CI files. The packet has no CHANGELOG.md, BACKLOG.md or `reviews/`, so I could not check the "declined" reasons beyond the developer's summary. Everything below is read from the code and tests. Nothing was run, and the developer says nothing has been run on Windows since 1.7.1.

## Verdict
There is no Critical issue. The core loop is sound: it opens fast, the plan carries over, `same` makes day two quicker, and saves are safe. Retention is not yet strong enough to be a release gate for anything wider than the five-person pilot. The reasons are:
- A person who never types a plan gets one generic line a day.
- That line repeats on a 100-day calendar cycle.
- Nothing pulls the person back except an opt-in Windows launcher.
- The rollout has no stated pass bar.

I recommend shipping to the pilot with the High items below fixed, and defining the pass bar first (finding 10).

## Who this is for
It is unclear, and I would say so in the README. Three possible audiences are in play:
- **Employees:** the text says "any age, any role, no technical skill."
- **IT:** the installer is a heavy, hardened deployment, and the Apps entry's publisher is "IT Department."
- **The pilot:** five people.

The job it does is also two things at once:
- a wellness nudge (water, stretch, thanks);
- a one-line to-do tracker (plan, then "Did you do it?").

An employee who got this installed by IT has no reason to open it on day 3 unless one of those two jobs matters to them. The design assumes the plan is the job. The first-run flow treats the plan as optional and the content as the draw. Pick one lead job for the pilot and test it. My recommendation is the plan, because it is the only personal feature.

## Findings

### High

**1. Retention: the only trigger back is an opt-in, Windows-only launcher with a weak ask.**
- Return depends on the person remembering to open it from the Start menu.
- The sign-in offer is one long question: "Want it to open once a day when you sign in so it can ask about your plan? (y, n, or Enter = ask me later)".
- Three Enters retires it forever (`MAX_OFFER_SKIPS`). A "no" is final too.
- It is asked on visit 1 right after a plan, when the person has had no value yet, and then only until three Enters.
- The launcher opens a console that waits for Enter. That is a lot to ask of someone who has not yet seen a reason to come back.

Fix:
- Shorten the ask: "Open this each morning when you sign in? y / n".
- Re-offer once at a moment of earned value: the first `done`, or the 3rd visit. Do this even after Enters, but never after an explicit n.
- Consider letting a startup launch close itself after about 60 seconds if untouched, with a note that it did.

**2. Retention: without a plan, the daily value is thin and finite.**
- One thought and one tip are chosen by `toordinal()`. The packet counts 100 tips and 101 thoughts. That is about 3 months of calendar days, or about 70 openings for a weekday user, before everything repeats.
- The pairing fix (101 vs 100) only delays the identical pair, and the pair is not what makes people notice repeats.
- The tips are also ordered by theme: roughly 27 body and eye tips first, then calm and mindfulness, then desk tidying, then social. A person opening daily gets about a month of "stretch your shoulders" before anything else.
- The README and PLAN still say lists "repeat every 100 days", which is correct. But the content never connects to the person, so a returning user sees nothing new about themselves.

Fix:
- Shuffle with a fixed permutation so neighbouring days differ in category.
- Grow the pool toward 365 before a wide rollout.
- Make the tip usable (see change 2 below).

**3. Ease of use / retention: the first run asks for a blank free-text answer after a wall of privacy text.**
- The Welcome block is 7 lines about files, IT staff, and passwords, and it comes before any value.
- Then a blank prompt follows: "What is one thing you want to get done today?"
- Typing the obvious next words (`menu`, `plan`, `none`, `skip`, `no`) is rejected with a message. That is correct for safety but a poor first moment.
- The developer declined "shortening the first run" and "moving the sign-in offer" until pilot feedback. I disagree. A first run happens once per person, so five pilot people cannot be re-run later.

Fix:
- Cut the welcome to two lines: what this is, and "Privacy: menu, then 1."
- Show an example in the prompt, such as "e.g. Send the invoice".
- Offer one-keystroke plan entry from the tip (change 2 below).
- Accept `none` and `no` quietly at the first prompt as "no plan." Do not lecture someone who is declining.

### Medium

**4. Ease of use: "Enter = close" after `done` does not close.**
- After `done`, the prompt says "Type the next plan, or Enter = close".
- Enter prints "Nothing changed." and then loops back to "Press Enter to close, or type…". That needs a second Enter.
- The tests encode it (`done\n\n\n`, two blank lines), so it is intended. But the label is wrong, and "Nothing changed." right after a celebration reads like a failure.

Fix:
- Make Enter at the after-done prompt really close, with one line such as "Done for today. See you tomorrow."
- Or relabel it "Enter = back".

**5. Retention: the `done` moment is mostly unreachable.**
- `done` is a hidden word at the last prompt of the morning window.
- People finish the thing hours later, when that window is closed and nothing prompts them to reopen it.
- The real finish loop is tomorrow's "Did you do it?" followed by the next-plan prompt.
- "Saved. Tomorrow it will ask how this went." appears only for a newly typed plan, and `done` is not explained at the moment a plan is saved.

Fix:
- On saving a plan, say in one line: "Finished it later? Open this again and type done."
- Make a same-day reopen with an open plan say the same thing.

**6. Retention: the nag path for an unanswered plan.**
- Enter at "Did you do it?" leaves the plan as it was.
- The next visit asks again, for up to 14 days. That is a daily question the person is avoiding, which is the shape of guilt the project says it avoids.

Fix:
- After the second skip, ask once: "Drop this one? y / Enter = keep asking".
- Or move it quietly to `same` after 3 days.

**7. Ease of use / destructive-action safety: no way to cancel or clear a plan, and delete shows no cost.**
- There is no `clear` word. `none` and `no` are rejected, so a plan can only be removed by replacing it or answering n the next day.
- Menu option 4 deletes everything after a single y.
- The prompt says what it deletes but not how much: 42 days, 17 finished plans, backup copies.
- There is no export before deleting.
- Option 4 is also placed between toggles, next to the common option 3.

Fix:
- Add `clear` for today's plan.
- Show counts at the delete prompt.
- Offer `full` (show it) before deleting.
- Separate "forget my plans" from "delete everything."
- Reorder the menu: plan first, delete last.

**8. Retention: the second session is fast, but only for people who plan, and progress is invisible.**
- `same` and the "Earlier plan" line are good.
- A returning user who does nothing still sits through three Enters: "Did you do it?", the plan prompt, and the close prompt. Fold the plan prompt into the final prompt when nothing is open.
- Progress shows only in the "in a row" line at the 3rd, 7th and 14th visit, then every 30th, and in "That is N plans you have finished." after a finish.
- On a day you do not finish anything, there is nothing to look back at. The weekly list was declined. See the retention feature below.

**9. Retention: welcome back does not re-orient the person.**
- After a gap of more than 7 days it says "Welcome back" and then asks about a plan that can be up to 14 days old, or says it was cleared.
- It never shows what they did before leaving, so coming back feels like starting over.
- Fix: the recap below.

**10. Retention: no way to know whether it works.**
- There is no reporting, by design, which I agree with.
- Measurement is "ask the five employees," and success is only defined as installs finishing without error.
- Install success says nothing about return.

Fix:
- Write a pass bar before the pilot starts. For example: at least 3 of 5 open on at least 8 of the first 14 working days without being reminded, and at least 2 of 5 have set a plan more than once after day 7.
- Check it at day 3, 7 and 14 by asking each person to read their own dates from menu option 1.
- Ask two questions at day 14: "What did you open it for?" and "When did you stop?"

**11. Ease of use: the real target has not been run.**
- Windows behaviour is untested since 1.7.1. The pinned Python is 3.14.8, and the tests ran on 3.11.
- Untested on the real target: the shortcut, the window title, whether Enter closes the window, console Unicode input, and the launcher.
- Run the first-install checklist from PLAN.md on a clean PC before the pilot. A broken first window is a one-shot failure.

### Low

**12. Ease of use: menu and help.**
- The numbering skips on purpose ("Choose 1 to 6", with 5 as help). The plan is option 6, after the delete.
- `HELP` and `MENU_HELP` do not mention `same` or `clear`.
- The README sign-in bullet is muddled: "if you type a plan, the next day it asks how it went."

**13. Docs drift.**
- PLAN.md still says "One optional plan a day". The next-plan loop now allows several.
- The README says the file lists "the last 400 dates", which is correct, but the "What is saved" paragraph is a very long single sentence.

**14. Content tone.**
- A few lines are regional ("share the biscuits", "kettle filled", "nine o'clock") against a "most generic person" goal.
- Both lists run on calendar days, so weekends get "Leave on time tonight" and "an inbox" lines.

**15. Sign-in window.**
- A console window that appears at sign-in and waits for Enter can feel intrusive, against the "nothing opens by itself unless you choose it" principle. The person did choose it, but there is no snooze and no idle close.

## What works and should stay
- Time to first value is instant, and it is plain ASCII with no colour.
- Saves are atomic and private. A damaged file becomes a named backup with an announcement, and a locked file is never overwritten.
- A failed save now says so and does not celebrate.
- Wrong answers are named and re-asked, not taken as a choice.
- The welcome-back copy has no guilt words.
- `done` is correctly not a yes at the sign-in offer and at "Keep it for today?".
- Re-reading the file before a change fixes the stale-window overwrite.
- The in-a-row line is quiet and can be switched off.

## Highest-leverage product changes, most important first
1. **Build the retention feature below: a private "Finished lately" recap.**
2. **Make a plan one keystroke.** Add `t` at the plan prompt to take today's tip as the plan, show an example in the prompt, and cut the first-run welcome to two lines. This removes the blank-prompt drop-off for first-time and no-plan users, and it makes the tip useful.
3. **Fix the Enter-to-close mismatch after `done`** and replace "Nothing changed." with a closing line (finding 4). It is a small change on the loop that was just built.
4. **Stop the unanswered-plan nag.** Ask once whether to drop it after the second skip (finding 6).
5. **Re-offer the sign-in launcher at the first `done` or the 3rd visit, shorter and once.** This is the only return trigger the product has (finding 1).
6. **Fix content freshness.** Shuffle the lists so neighbouring days differ in category, and grow toward 365 before a wide rollout (finding 2).
7. **Add `clear`, and show counts at the delete prompt.** Move delete to the bottom of the menu (finding 7).
8. **Write the pilot pass bar and run the Windows first-install checklist before the pilot starts** (findings 10 and 11).
9. **Fix the doc drift** (findings 12 and 13).

## Retention feature to build this round: "Finished lately"
**What it is.** Keep the last 7 finished plans (text and date) in the existing notes file.
- Show them as a short list right after `done`, for example "This week: 3 finished" followed by the plans.
- Show them again on the first open after a gap of more than 7 days, under "Welcome back", instead of only the stale plan.
- The list is shown on screen only, is switchable in the menu, and is removed by Delete everything.

**Why the person would come back because of it.** It gives them something they cannot get anywhere else: a private record of what they got done, for a weekly check-in or a stand-up, built in about five seconds a day. Finishing a plan then has a visible payoff beyond one line of praise. A person who returns after a gap picks up where they left off instead of facing a blank screen and an old question. That makes the second session more rewarding than the first, not just faster.

**On the developer's decision to wait for pilot feedback.** A five-person pilot cannot show appetite for a feature it does not contain, and the pilot is effectively one shot. I would build it now.

**Trust risk to handle.** This reverses the earlier "no history of plans" rule, and the file is readable by IT. Mitigate it in four ways:
- cap it at 7 entries;
- say plainly on first appearance that it is local and listed in menu option 1;
- keep it out of any reporting (there is none);
- let the person turn it off.

If the pilot group is uneasy, hide it by default and offer it after the first `done`.

## Accessibility reviewer

# Accessibility review: hello-world 1.14.0 (Round 39), WCAG 2.2 AA

I read all of the packet (lines 1-3326): the developer notes, `hello.py`, `test_hello.py`, `install.ps1`, `uninstall.ps1`, README, PLAN, docs, workflows and config. `CHANGELOG.md`, `BACKLOG.md`, `reviews/round-39.md` and `hello.cmd` are not in the packet. I could not check the notes' claims about them.

The interface is a Windows console program plus PowerShell scripts, so I applied the criteria by analogy. Reflow stands in for 1.4.10, name/role/value for 4.1.2, and so on.

**Verdict:** no Critical findings. I found one High, a release-gate verification gap rather than a coded defect. Every control I traced is reachable by keyboard alone, and Enter alone always works. The ship-now items are listed at the end.

What works and should stay:
- Plain ASCII output with no colour in `hello.py`.
- Labelled sections ("Thought for today:", "Try this today:").
- Prompts that say what Enter does.
- Wrong answers are named and the choices are listed.
- Delete needs a strict yes.
- State is shown in words ("now on", "now off").
- The unambiguous date.

## High

**H1. Screen-reader behaviour is unverified on the target platform (release gate).**
- Criteria: 4.1.2, 1.3.1, 4.1.3.
- The README and PLAN say the output is "designed so a screen reader reads it in order". The notes say the screen-reader pass is declined because it needs Windows.
- Nothing has been run in conhost or Windows Terminal with NVDA, Narrator or JAWS, or with a large font or 200% zoom. The tests run only on Linux through piped stdin.
- Things that only a real pass will show:
  - whether the prompt is announced before the typed echo;
  - whether the `>` glyph is read as "greater than";
  - whether the long first-run block is cut off when the new window takes focus;
  - how the menu re-reads eight lines on every loop.
- Fix: before the pilot goes to the five employees, run a scripted pass with NVDA and Narrator in both conhost and Windows Terminal. Cover first run, follow-up, `done`, the menu, the sign-in offer and the error paths. Record results in `reviews/`.
- The hedge in the docs ("not yet verified") is honest, so a pilot may proceed. Wider rollout may not.

## Medium

**M1. The prompt says "Enter = close" and does not close. The notes claim it does.**
- Criteria: 3.3.2, 3.2.4, 4.1.2.
- After `done`, `set_plan(after_done=True)` asks "Type the next plan..., or Enter = close >".
- On Enter it prints "Nothing changed." and returns to the `while True` loop in `daily()` (the `continue` on the `done` branch). The last prompt then appears again, so closing takes a second Enter.
- "Nothing changed." is also an unhelpful reply to a deliberate "close".
- `test_after_done_enter_just_closes_and_nothing_is_lost` supplies two Enters (`done\n\n\n`) and also ends in EOF. EOF makes `ask()` return None, which closes the window. The test therefore cannot detect the bug.
- Fix: when `after_done` is true and the answer is empty, close. Return a flag and `break` instead of `continue`, and say nothing. Alternatively, change the label to "Enter = go on". Make the test feed exactly one Enter and assert the program ends.

**M2. Prose is hard-wrapped at about 70 columns, so the "wrapping follows the window width" fix is partial.**
- Criteria: 1.4.10 (by analogy), 1.4.4.
- Only plans, thoughts and tips use `width()`. These stay hard-wrapped at fixed breaks (about 66 to 72 characters):
  - the first-run welcome;
  - the "plan cleared" notice;
  - the `show_saved` privacy lines;
  - `HELP` and `MENU_HELP`;
  - the damaged-file notice (`textwrap.fill(..., 72)`).
- At 30 to 40 columns, or with a large font, these re-wrap raggedly: a long line followed by a few stray words. This is exactly what M5 was meant to stop.
- Prompts and one-line messages are not wrapped at all. These are the offer prompt (about 110 characters), the delete prompt, and the `is_command` and `not_a_choice` messages. The console breaks them mid-word.
- `width()` also floors at 30, which overflows a narrower window.
- Fix: send all prose through one `say_wrapped()` helper, and build the help and welcome text as unbroken paragraphs. Wrap the prompt text before `input()`.
- Tests: run every screen under `COLUMNS=30`, 40 and 72 and assert every line fits. The current test checks only `wrapped()`.

**M3. The startup launcher hides its own errors.**
- Criteria: 3.3.1, 4.1.3.
- The Start menu shortcut adds `if errorlevel 1 pause`, so a failure stays readable.
- The sign-in launcher written by `remind()` is `start "hello-world" "<hello.cmd>" --startup`. It opens a separate window with no pause.
- Any "something went wrong" or "cannot write to stdout" message flashes and disappears at sign-in.
- That window is also the one that takes focus when assistive technology is still starting.
- Fix: write the launcher as `start "hello-world" cmd /d /c ""<hello.cmd>" --startup & if errorlevel 1 pause"`. Add a Windows test.
- The README and offer text should say "a window opens when you sign in".

**M4. The installer and uninstaller hard-code console colours, including on the key result lines.**
- Criteria: 1.4.3, 1.4.1.
- The scripts use `-ForegroundColor` Cyan (steps), Green (success) and Red (`FAILED:`).
- On light console themes, Cyan and Green fall to roughly 1.3 to 2:1 contrast. On the default blue PowerShell background, pure Red is only about 3.7:1.
- The result and failure lines are the ones an IT admin must read. The "FAILED:" and "Installed" wording gives a non-colour cue, so this is not 1.4.1, but contrast is the problem.
- The colours also override the user's own colour choices and high-contrast settings.
- Fix: drop the colours, or use them only as decoration and leave the default foreground.
- Related: `Write-Progress` redraws on every 200 items. That conflicts with PLAN.md's "no redrawing" and is noisy for screen readers. A single "still working" line every N items does better.

**M5. A command word at a plan prompt gets a circular or misleading message.**
- Criteria: 3.3.3, 3.3.1.
- `is_command()` always says "Type plan at the end of this screen to set one."
- When the person is already at the plan prompt (after `plan`, after `done`, or menu 6), the advice sends them back to where they are.
- Typing `q` or `no` at "Enter = close" is treated as a command and the window stays open.
- "At the end of this screen" is a visual-location phrase (1.3.3 spirit). The README says "last prompt".
- Fix: use context-specific text: "That looks like a command, so it was not saved as your plan. Type your plan, or press Enter to go back." Replace "end of this screen" with "the last prompt" in the welcome, `HELP` and `is_command` text.

**M6. A save failure gives no cause and no next step.**
- Criteria: 3.3.1, 3.3.3, 4.1.3.
- "Your notes could not be saved on this computer. This screen still works." and "Could not save that on this computer." name no reason.
- They give no path, no hint ("ask IT", "disk full", "file locked"), and no statement of what state the plan is in. Only the `done` path says "The plan is still open".
- When a locked file makes `load()` return `can_save=False`, the person also sees the first-run welcome as if nothing were saved. The cause is never shown.
- Fix: say what was kept ("Your plan is unchanged") and name the folder (`data_dir()`). Add one action ("close other hello-world windows, or ask IT").
- The generic stderr line "something went wrong (ValueError). Contact IT." identifies nothing. Add the failing step and a suggested action, or point to a log.

**M7. Silent or wrong status messages in the answer flows.**
- Criteria: 4.1.3, 3.3.1.
- `offer_reminder`: after three misunderstood answers `ask_choice` returns None and the function returns with nothing said. This is the same "silence" M1 of Round 39 fixed only for the follow-up.
- "Did you do it?" with Ctrl+C or EOF prints "That was not understood" (the `answer is None and person` branch). README says Ctrl+C simply skips the prompt.
- Three wrong answers at "Keep it for today?" end in "Kept for today.". That is safe, but it does not say the answers were not understood.
- Fix: print "That was not understood. It will ask again later." after three misses at the offer. Separate Ctrl+C or EOF from misunderstood in `ask_choice` (return a distinct value) and say "Skipped." for the former.

## Low

- **L1. Content assumes sight and hearing, against the project's own claim ("nothing assumes a level of ability").**
  - Criteria: 1.3.3 spirit, 3.1.5.
  - Tips and thoughts that assume sight:
    - "Look at something far away for twenty seconds";
    - "Gaze at something green or calm";
    - "Blink slowly";
    - "Cup your palms over closed eyes";
    - "Name three things you can see, hear, and feel";
    - "Looking out of a window".
  - Tips that assume hearing: "Listen to one favorite song", "Notice one pleasant sound".
  - A screen-reader audience will meet these. Add "or notice by touch or sound" alternatives, and correct the claim in `docs/WHY-DAILY-ACTIONS.md` (section 7, writers' rules).
- **L2. Non-ASCII plans print as `?` when the console cannot show them.**
  - Criteria: 3.1.1.
  - The program echoes the person's own words back as `????`. Python 3.14's console I/O may avoid this on a real console, so verify on Windows.
  - Also test a non-Latin plan echoed through the prompts and the "Last time you planned" line.
- **L3. The `>` prompt terminator is often read aloud ("greater than").** Prefer ":" or "?" as the final character. Needs the screen-reader pass (H1) to confirm.
- **L4. `done` is irreversible and has no confirmation.**
  - Criteria: 3.3.4 (analogy).
  - It is mitigated because the plan moves to `same`. State that after marking done: "Type same at the next plan prompt to bring it back."
- **L5. Errors and usage text for bad options go to stdout** ("Unknown option: ..."), exit 2. The lowercased echo of the option changes what the person typed. Send errors to stderr and echo the original text.
- **L6. `HELP` has gaps and loose wording.** It omits exit codes, `same`, and the `m`/`p`/`h`/`?` shorthand. "type plan for today's plan, done when you finish it, or menu for options" reads ambiguously aloud. Reword it as a list.
- **L7. The menu reprints all eight lines on every loop.** Offer "Type m to see the options again" after the first display, so a screen reader does not re-read it.
- **L8. `--stats` and the "full" view dump raw JSON.** Braces and quotes are read aloud. A summary comes first, so this is minor. Consider a plain "key: value" form as the default.
- **L9. The shortcut and Apps entry use python.exe's icon.** The name "hello-world" is clear and the description helps, so this is cosmetic.
- **L10. Documentation.**
  - The README "For employees" section is hard to follow: a bullet list, then an eight-sentence paragraph, then bullets. The line "Sign-in reminder: if you type a plan, the next day it asks how it went" sits under the wrong bullet.
  - PLAN.md, `docs/WHY-DAILY-ACTIONS.md` and the `hello.py` comment still say "100 thoughts, repeat every 100 days". The code now has 101 thoughts.
  - No channel is given for reporting an accessibility problem.
- **L11. Test hygiene.** `test_wrapping_follows_a_narrow_window` replaces `hello.shutil.get_terminal_size`, which is the global stdlib module. This leaks into later tests in the same process. Use `COLUMNS` in a subprocess instead. Most tests also end in EOF, which hides loop behaviour (see M1).

## Accessibility improvement to ship this round

- **Ship M1:** make "Enter = close" close after `done`, and make its test use exactly one Enter. It is a small change, it fixes a promise the notes say is already kept, and it protects keyboard-only users.
- **Ship M3:** add the pause on error to the sign-in launcher.
- **Ship M2 if time allows:** a single `say_wrapped()` for all prose, plus tests under `COLUMNS=30`, 40 and 72.
- **Pilot gate:** H1 stays open until the NVDA and Narrator pass is done on Windows.
