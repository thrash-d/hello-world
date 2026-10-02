# Round 39 review

- Date: 2026-10-02
- Commit reviewed: d6f740c (main after Round 38, version 1.13.0)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1, plus the newest CHANGELOG entry as developer's notes. Excluded as instructed: BACKLOG.md, CHANGELOG.md (except the newest entry), reviews/, .git/, .devkit/. Every reviewer got the whole packet.
- Agents that ran: lead, security, usability and retention, accessibility.
- Redactions: none needed for model names; a scratch file path in two replies was replaced with "the review packet".

---

## Lead reviewer

# Review of hello-world 1.13.0

I read the whole packet (3163 lines). I ran nothing and modified nothing. I traced the new `done` and typo-handling code by hand against the tests. I found no Critical issues. The 1.13 changes work on the paths you tested. The main problems are around the new `done` feature: windows that stay open, the first prompt, and release confidence on Windows.

## Part 1: Findings, most severe first

**1. High | bug (data loss) | Stale in-memory state overwrites newer saves, and `done` makes this more likely.**
- `daily()` loads `state` once. Every later action (`done`, `plan`, menu 3, `same`) saves that old copy over the file.
- The new last prompt ("type done ... >") invites people to leave the window open until they finish the task. The optional sign-in launcher also opens a window every morning.
- Example: window A (sign-in) stays open. The person opens window B from the Start menu and changes the plan with `plan`. Back in A they type `done`. A counts the old plan, sets the plan to None and saves. B's new plan, its `previous` value and its visit are gone. The `done` count can also go backwards. Nothing is shown to the person.
- Fix: before every mutation (`mark_done_now`, `set_plan`, menu toggles, the offer), re-run `load()`, apply only that change to the fresh state, then save. A tiny lock file would also work. Add a test that runs two states against one file.

**2. High | process and bug risk | The whole 1.8 to 1.13 series has never run on Windows, and the shipped interpreter is Python 3.14.**
- The tests ran on Linux with Python 3.11. The installer pins the 3.14.8 embeddable build.
- The Windows-only `interactive()` code (ctypes `GetConsoleMode`, `msvcrt`) decides whether the program prompts and records visits at all. If it misjudges, the program silently never records anything.
- Also untested: the shortcut quoting, the Startup `.cmd`, console Unicode input and the embedded Python with `-I`.
- You say this plainly in PLAN.md. Treat it as a release gate anyway: do one real Windows 11 install with a screen reader pass before the five employees get it. Also run the test suite under 3.14.

**2a. Medium | bug | A file that exists but cannot be read gets a fake first-run, and the typed plan is lost.**
- `load()` returns `(fresh state, can_save=False)` when the file is locked (antivirus, OneDrive, another process).
- `daily()` then sees empty `visits`, so it prints the "Welcome." first-run text and asks for a plan.
- The person types a plan, and only at the end reads "Your notes could not be saved". The plan is lost.
- Fix: when `can_save` is False, say so at the top. Skip the plan and follow-up prompts, or retry the read two or three times first. Do not show the first-run welcome to someone who has data.

**3. Medium | ease of use and retention | Command words typed at the first plan prompt become the plan.**
- The welcome says "Type plan or menu at the end of this screen". A person who types `menu`, `help`, `?`, `q`, `quit`, `done`, `none`, `no`, `nothing` or `skip` at "What is one thing you want to get done today?" saves it as their plan.
- The next day: "Last time you planned: menu. Did you do it?" That is a bad second session, and the typed word is now also offered as `same`.
- Fix: at both plan prompts (the daily prompt and `set_plan`), intercept these words. Either route them to the menu or quit, or say "That looks like a command, not a plan. Enter = skip" and ask once more. Add tests.

**4. Medium | bug | `mark_done_now` prints success before the save, then contradicts itself.**
- `finish_plan` prints "Good. ..." and "That is N plans you have finished." before the save.
- If the save fails, the person sees the praise and the count, then "Could not save that on this computer."
- The rollback is correct, but the message is misleading.
- The same ordering applies to the "Did you do it?" path, which counts in memory and saves later.
- Fix: save first, then print the praise and count (or print a neutral "Could not save" only).
- The developer notes say there is a test that a failed `done` save is rolled back. There is none in the packet. The only failure-path tests cover `plan` and menu 3. Add one.

**5. Medium | accessibility | Output is hard-wrapped at 72 columns.**
- Low-vision users enlarge the console font or use a narrow window. Lines wrap a second time and read as ragged fragments, and some screen-magnifier users see half-lines.
- Fix: wrap at `min(72, shutil.get_terminal_size().columns - 2)`, with a floor of about 30. Also wrap the long `same for: "..."` prompt text, which can hold 120 characters on one line. Add a `--width`, or honor a `HELLO_WIDTH` setting if you want the opposite.

**6. Medium | privacy and ease of use | A plan's text is kept forever and cannot be removed on its own.**
- Every finished, replaced, cleared or expired plan stays as `previous` indefinitely.
- It is shown on every later day in the `same for: "..."` prompt, including after the plan is done.
- The only way to remove it is to delete everything, including the visit history.
- You disclosed this honestly ("Cleared. It stays as same until you delete everything"). It is still a trap: someone who typed a customer name or a private detail cannot erase just that.
- I know the developer declined "expiring or switching off previous". I still recommend a menu item "Forget the earlier plan", which is a tiny change. Also stop offering a plan that was marked done as `same` every morning. Offer `previous` only when it was cleared or expired, not done.

**7. Medium | retention | All content repeats every 100 days, and the pairing repeats with it.**
- There are 100 tips and 100 thoughts, both indexed from `toordinal()`. They advance together, so the exact same screen returns on day 101.
- For someone who opens it on working days only, that is under five months.
- Fix: use different list lengths, for example 100 and 97 or 101, so the combined screen repeats only after about 10,000 days. Add another 100 items over time. Possibly add a seasonal or weekday-aware line.

**8. Medium | security and deployability | The sign-in launcher writes a `.cmd` into the Startup folder.**
- Writing a script to Startup is the classic persistence technique (MITRE T1547.001). Defender for Endpoint or other EDR may flag it and block adoption.
- It is user-scope and opt-in, so the actual risk is low. Tell IT up front, and give them the exact file name and content for an allow-list.
- The Startup path is built from `%APPDATA%`. That is the user's own value, so this is fine.

**9. Medium | bug | Tests are weaker than the notes claim.**
- `test_done_at_the_last_prompt_counts_the_plan_the_same_day` contains `... or "done" in first.stdout`. The prompt text always contains "done", so that assertion can never fail and does not check the DONE line.
- `test_same_brings_back_...` has a similar `or` assertion.
- `test_done_does_not_turn_on_the_sign_in_reminder` types `done` at the sign-in prompt, where it is just an unrecognized answer. It does not test `done` at all.
- Missing, although the notes list them: the "..." cut for long words, `never`, `stop` and `no thanks` at the offer, and the "Cleared. It stays as same..." text.
- Fix: tighten those assertions and add the missing tests.

**10. Low-Medium | bug | Windows can fail `os.replace` transiently.**
- Antivirus, indexers or OneDrive can hold `notes.json`. `save()` returns False on the first failure and the person gets "Could not save".
- Fix: retry three to five times with a 100 ms sleep in `save()`, as the installer already does for renames.

**11. Low | bug | The Delete everything confirmation does not follow the new typo rule.**
- `reset()` uses a bare `ask`. A typo such as `yse` prints "Nothing was deleted." instead of being named and asked again.
- This is the safe direction, but the README says "the yes/no questions ... a mistyped answer is named and asked again". That is not true here. Use `ask_choice` with `STRICT_YES`, or fix the README.
- Delete everything also leaves the sign-in launcher in place and does not say so. Either remove it or add one line saying it stays.
- After a menu reset, the next `plan` or menu save rewrites `notes.json` with empty `visits`. Today is not recorded, so the next open the same day shows the first-run welcome again.

**12. Low | ease of use | Input handling is inconsistent between prompts.**
- The last prompt does not strip `. ! `, so `done.` or `q.` is "not a choice". `ask_choice` does strip them.
- The menu's "Press Enter to go on, or type full" ignores any other input without a word.
- Three unrecognised answers at "Did you do it?" end silently. Enter prints "Left as it was." Make them consistent.
- `set_plan` says "Enter = keep" even when there is no plan to keep.

**13. Low | ease of use | Smaller wording and accuracy points.**
- "You have opened this 3 times in a row" reads awkwardly.
- "Weekends and days off don't break it" is not true for a Thursday to Monday gap, which is 4 days against a 3-day limit. A long weekend breaks the count.
- The README bullet "Sign-in reminder: if you type a plan, the next day it asks how it went" mixes the reminder with the follow-up.
- An unreadable-file run that is not a person still prints "Type same at the plan prompt" with no prompt.

**14. Low | accessibility and inclusion | Some tips assume sight or hearing.**
- Examples: "Look at something far away", "Gaze at something green", "Cup your palms over closed eyes", "Listen to one favorite song", "Wave or smile ... on your next video call".
- Your own rule is that nothing assumes ability. Reword about 8 to 10 of them, or add "if you can".
- The README says the program has not been tried with a real screen reader. The design (linear text, no redraw, Enter always works, no timeouts) looks right. A pass with Narrator and NVDA is still the only way to know.

**15. Low | docs | README and PLAN.md reference files that were not in the packet.**
- They point to CHANGELOG.md, BACKLOG.md and reviews/. If those files are missing from the repo, the links are dead. If they exist, ignore this.
- The README install snippet does not guard against a missing Git for Windows registry key. `.InstallPath + '\cmd\git.exe'` becomes `\cmd\git.exe`, and the clone fails with a confusing message.

**16. Low | security and supply chain | CI and installer, noted but already declined.**
- Workflows are pinned by tag, not by commit SHA.
- devkit-quality downloads gitleaks, osv-scanner and vale binaries with `curl` and no checksum.
- dependabot-automerge merges major updates automatically after only a build and test run. Since the installer pins an admin-reviewed commit, the gate is review, so this does not weaken the installer.
- uninstall.ps1 deletes a file named `hello-world-daily.cmd` in each profile's Startup path. A standard user could point a junction there to make an elevated delete of that one file name land elsewhere. The impact is very low.

**What I checked and found fine:**
- Escape-code and control-character cleaning.
- The BOM and damaged-file backup logic.
- Future-dated visits and plans.
- Atomic save with `O_EXCL`.
- The `in_a_row` slicing.
- The offer-skip counting.
- Dead-stdout handling.
- The privacy text now matches the code. Option 1 and the README both say IT staff could read the file.

## Part 2: Improvements, most important first

**A. Retention change (required): do not let a returning person see a repeat, and make the plan loop the visible value.**
1. Make the two content lists coprime in length (for example 100 and 101), and add content in batches. This is a small change that removes the day-101 cliff described in finding 7.
2. At the start of each day, show one line from the plan loop before the thought: "Yesterday: finished" or "Yesterday's plan is still open". This is local and private, and it gives the day-two screen a reason to exist. It is not a streak or a report. Keep the done count private as you do now.
3. Add an option for a short private "last 7 days" line in menu option 1: how many days you opened it and how many plans you finished. It does not send anything and is deleted with Delete everything. I know the developer declined a weekly recap. A line inside option 1 is not a recap and is not pushed at the person.
4. Offer `previous` as `same` only when it was not marked done (finding 6), so the morning prompt stays relevant.

**B. Accessibility change (required): adapt layout to the person, and verify it with real tools.**
1. Wrap to the real console width and use a floor (finding 5).
2. Add `--plain` style variants that drop the "> " prompt noise for screen-reader users, or accept `HELLO_SIMPLE=1`. At minimum run a scripted session through Narrator and NVDA and record what it reads for each prompt.
3. Reword the sight and hearing tips (finding 14).
4. Keep the rule you already follow: every prompt works with Enter alone, and names the typed word when it is wrong.

**C. Ease of use.**
- Intercept command words at the plan prompts (finding 3).
- Re-read the file before every write so two windows cannot overwrite each other (finding 1). Print one line when the file was changed elsewhere.
- Show an up-front notice and skip the plan prompts if the file cannot be saved (finding 2a).
- Add a menu item "Forget the earlier plan" and a "Clear just my plan" choice that does not delete visits.
- Make every y/n question use one helper, including Delete everything (finding 11).

**D. Product direction.**
- The README says it is a small daily moment for employees, deployed by IT to five of them as a pilot. It is not yet clear who it serves beyond that or why they would open it a second time.
- The honest value is the plan loop (one thing today, one keystroke to carry it over, one keystroke to finish it). The tips and thoughts are generic wellness filler.
- I would define the product as "a 20-second start-of-day check-in: here is yesterday's open item, set today's one thing, done in one word". Keep the tips as a garnish.
- Measure it the way you already plan to, by asking the five employees. Add an optional local-only question after day 14, "Was this useful? y/n", whose answer shows in `--stats` so a person can choose to share it. That gives you a retention signal without any reporting.
- Before widening beyond five, decide who owns content updates, since a new release currently means a reinstall by an administrator.

**E. Release checklist before shipping.**
- One real Windows install, reinstall, interrupted install and uninstall on a clean PC.
- The test suite under Python 3.14.
- A pass with a real screen reader.
- Tell IT about the Startup `.cmd` before anyone opts in.

Files: all findings refer to the packet at `the review packet`. Line numbers there: `hello.py` is about lines 757 to 1831, `test_hello.py` about 2238 to 3078, and `install.ps1` and `uninstall.ps1` after them.

---

## Security

SECURITY REVIEW: hello-world 1.13.0 (hello.py, install.ps1, uninstall.ps1, workflows, docs, tests)

Scope: I read all 3163 lines of the packet and touched nothing else. I reviewed for vulnerabilities and abuse cases only.

Verdict: no Critical and no High. hello.py, the program that runs on every employee PC, is clean. The installer's trust chain is well built. The real exposure is in the CI supply chain, in the footprint the installer leaves on workstations, and in one privacy claim that is not true.

FINDINGS

1. MEDIUM. Dependabot auto-merge has no real gate and no human review. (.github/workflows/dependabot-automerge.yml; CWE-1357, CWE-829; NIST SA-12, SA-10, CM-3; OWASP A08; MITRE T1195.001/002)
- The repo has no runtime dependencies. hello.py uses only the standard library, and there is no package.json or requirements.txt. So the only things Dependabot can bump are GitHub Actions versions.
- For those PRs the "check" job finds test_hello.py and runs pytest. The tests never exercise the workflows, so the check always passes.
- The merge job then squash-merges the PR, major versions included, with no review.
- After the merge, auto-tag.yml runs the bumped action on main with `contents: write`. A hijacked action tag proposed by Dependabot therefore gets code execution with a write token, with nobody looking.
- Every action is pinned by mutable tag (`actions/checkout@v5`, `setup-node@v5`, `setup-python@v6`), not by SHA.
- The gate uses `github.event.pull_request.user.login`, not `github.actor` plus `dependabot/fetch-metadata`. Anyone with write access can push a commit onto a Dependabot branch. The PR author stays "dependabot[bot]", the tests pass, and it auto-merges.
- The merge job does not wait for devkit-quality (gitleaks, osv). If branch protection is absent, as the notes imply by declining repo settings, the merge happens regardless.
Fix:
- Drop auto-merge for the github-actions ecosystem and for major updates. Use fetch-metadata and allow only patch and minor updates.
- Pin every `uses:` to a full commit SHA, and let Dependabot bump the SHAs.
- Require review and required status checks in branch protection. Use `gh pr merge --auto` so it waits for them.
- Add a guard that the PR diff touches only the expected files.

2. MEDIUM. The installer puts a full, unpatched, world-executable Python on every workstation. (install.ps1; CWE-1104, CWE-269 by way of application-control bypass; NIST CM-7, CM-10, SI-2, CM-2; CIS Controls 2.5 and 2.7)
- It unpacks the whole embeddable Python 3.14.8 into Program Files with Users:RX. That includes ctypes, `_ssl`, libcrypto, `_sqlite3`, expat and the rest, and `-c` is available to anyone.
- Program Files is usually allowed by default AppLocker or WDAC path rules. Any standard user can run `...\python\python.exe -c "<anything>"`. That defeats script and interpreter restrictions the organization may have set.
- Nothing updates it. Windows Update does not patch embeddable Python, and the bundled DLLs will go stale.
- The installer, hello.cmd and python.exe are unsigned, but the Apps entry says `Publisher = 'IT Department'`. That is an unverified identity claim.
Fix:
- Remove unused modules and DLLs from the extracted tree (`_ssl`, `libcrypto`, `libssl`, `_sqlite3`, `_ctypes`).
- Replace the ctypes console check with something not needing ctypes.
- Authenticode-sign hello.cmd/hello.py, or publisher-allow them in WDAC, and drop the "IT Department" string unless it is true.
- Document an owner and cadence for bumping `$pyUrl` and `$pySha256`.
- Tell IT about the AppLocker implication.

3. LOW. The uninstaller does elevated deletes through user-controlled paths. (uninstall.ps1, the ProfileList loop; CWE-59, CWE-61, CWE-367; MITRE T1187 forced authentication; NIST AC-6, SI-10)
- Elevated, it runs `Remove-Item -LiteralPath <profile>\AppData\Roaming\...\Startup\hello-world-daily.cmd` for every profile. A standard user owns every directory in that path.
- Local variant: a junction or symlink makes the delete land elsewhere. It can only delete a file named hello-world-daily.cmd, so impact is minor.
- Remote variant: with Developer Mode or SeCreateSymbolicLink, a user can point a path component at `\\attacker\share`. The admin's elevated process then authenticates over SMB, which leaks an NTLMv2 hash if outbound SMB is open.
- The developer declined this finding (BACKLOG, "uninstall junction"). I agree it is low, but the UNC case is more than a nuisance.
Fix:
- The simplest option is to have the launcher guard itself, e.g. `@if not exist "<target>" exit /b` before `start`. Then uninstall never needs to touch user profiles.
- Otherwise, walk each path component first, skip anything with the ReparsePoint attribute, and never follow it.

4. LOW. The privacy text is inconsistent with the data kept. (PLAN.md vs hello.py; CWE-359, CWE-212; NIST PT-2, PT-5, SI-12; OWASP A04)
- PLAN.md says the file "is not a record of which days or which plans". `notes.json` stores up to 400 visit dates (`MAX_VISITS`), which is exactly a record of which days. The README is honest about this. PLAN.md is not.
- The file is readable by IT on a work PC. It is kept indefinitely and survives uninstall. Taken together it is a de facto attendance log.
- It is also minimized poorly. The streak logic needs a short chain or a counter, not a year of dates.
Fix:
- Correct the PLAN.md sentence.
- Cut `MAX_VISITS` to about 35, or store only `last_visit` and `run_length`.
- Consider an age-out of stored plan text.

5. LOW. CI hardening gaps. (.github/workflows/devkit-quality.yml; CWE-494, CWE-693; NIST SA-12, SI-7)
- osv-scanner, gitleaks and vale are fetched with `curl` and the tarballs are piped into tar with no checksum or signature check. The versions are pinned but the bytes are not. The job has only a read-only token, so impact is low.
- The gitleaks config comes from the PR's own `.devkit/gitleaks.toml` and `.gitleaksignore`. A PR can allowlist its own secret.
- Dependency findings (osv) do not block unless the repo variable DEVKIT_BLOCKING is set to true. That is an insecure default.
- The vale step passes `git diff --name-only` filenames without `--`, so a file named `--something.md` would be read as an option.
Fix:
- Verify SHA-256 sums for each download.
- Load the gitleaks config from the base branch.
- Default to blocking on findings.
- Add `--` before the file list.

6. LOW. Release trust depends on something outside the repo. (auto-tag.yml, README, install.ps1; CWE-345; NIST SA-12, SI-7)
- auto-tag.yml creates `v<VERSION>` on any push to main, using a write token. A tag therefore does not mean "reviewed".
- Real protection comes only from the commit hash the admin supplies. That is good, because `install.ps1` verifies HEAD and the hash of all four copied files against it. The hash must come from a source other than this repo's main branch.
- The README and the install.ps1 docstring ship the placeholder hash `0123456789abcdef...`. It fails closed. The test only checks that the tag matches VERSION, not the hash.
Fix:
- State in the README where the reviewed hash must come from, such as a signed tag or a ticket.
- Prefer a signed tag verified with `git verify-tag`.

7. LOW/INFO. The sign-in launcher is a Startup-folder persistence mechanism. (hello.py `remind()`; MITRE T1547.001; NIST CM-7)
- It is opt-in, lives in the user's own folder, and the target is admin-only. That is acceptable, but it looks like a text-book autostart artifact.
- The offer prompt can ask up to 3 times before it stops.
Fix:
- Tell the SOC and EDR owners to expect `hello-world-daily.cmd`.

WHAT I CHECKED AND FOUND CLEAN

Injection (command, shell, SQL, eval, template)
- There is no eval, exec, subprocess, pickle or shell use in hello.py.
- The launcher text interpolates only `__file__`'s directory, with `"` and `%` rejected, and ASCII-only encoding fails closed.
- hello.cmd's `%*` carries only the user's own arguments, and hello.py accepts a fixed set of options.

Deserialization and DoS
- Input is parsed only by `json.loads`, limited to 1 MB.
- Deep nesting (RecursionError), huge ints and bad dates are caught. The bad file is set aside as a backup.
- Unknown keys are dropped.
- Types and sizes are re-validated and clamped (plan length 120, done count at most 99999, visits at most 400).

Terminal escape and bidi injection
- Everything echoed goes through `tidy()`, which strips non-printable characters including ESC and U+202E, keeping only ZWJ/ZWNJ. Tests cover this.
- `not_a_choice` and the "Unknown option" echo are also sanitized.

Path traversal, link and race issues in hello.py
- The data path comes only from LOCALAPPDATA or the home directory, inside the user's own profile.
- `save()` writes a temp file with `O_EXCL|O_NOFOLLOW` and mode 0600, fsyncs, then renames atomically.
- `reset()` deletes only `notes.json`, `notes.json.*.tmp` and `notes.json.bak*`.

Secrets
- There are none in the code, the config or the docs.
- `.gitignore` covers env files, keys and `*.bak`.
- The installer's SHA-256 values are public integrity pins, not secrets.

Network, SSRF, XSS, CSRF
- hello.py makes no network connection.
- The installer fetches one hard-coded python.org URL over TLS 1.2 and checks a pinned SHA-256 before extraction. It also clones one hard-coded repo.
- There is no web surface, so there is no XSS or CSRF.

Test seams
- TODAY, HOME, STARTUP_DIR and FORCE_INTERACTIVE are module globals only. No environment variable can reach them, and a test proves it.

Installer privilege boundary
- It refuses unless the setup tree, Git's folders, ProgramData\Git and every parent folder are admin-only with no reparse points. The owner check, the allow-ACE rights masks and the InheritOnly handling are correct.
- git, icacls and cmd are called by full path.
- GIT_* variables are cleared, and HOME and XDG_CONFIG_HOME are removed.
- It requires a 40-hex commit and verifies HEAD plus the blob hashes of install.ps1, uninstall.ps1, hello.py and VERSION.
- It builds and tests beside the live install, with rollback. It runs the test only with `--plain`, which saves nothing.
- It re-verifies the installed tree and the shortcut ACL, and the shortcut is removed if the check fails.
- Python runs with `-I`, so PYTHON* variables and cwd do not load.
- The uninstall entry and script live in admin-only locations.

Workflow script injection
- No `${{ github.event.* }}` value is interpolated into a shell. The PR and push SHAs go through `env:`.
- The interpolated step outcomes and vars are fixed enums.
- Triggers are `pull_request`, not `pull_request_target`, so fork PRs get no secrets.
- The merge job is skipped when the check job is skipped, so non-Dependabot PRs cannot reach it.

Not tested by me: this was a read-only review, and I did not run any code. Windows behaviour (ACL edge cases, junction handling, git config scopes on Git for Windows) is judged from reading only.

---

## Usability and retention

## Review of hello-world 1.13.0: ease of use and retention

**Scope.** I read the whole packet. CHANGELOG.md, BACKLOG.md and reviews/ are referenced but not in it, so I judged the declined items only from the developer's notes. Nothing was run. This is a code and copy read.

### Verdict
The same-day `done` is the right move. It puts a reward at the moment of success. The typo handling and the honest privacy copy are real improvements.

I would not sign the retention gate yet, for three reasons:
1. Nothing accumulates for the person.
2. The return path is opt-in and weakly sold.
3. There is no way to learn whether anyone returned.

The new `done` also has several rough edges.

### Who is this for?
This is unclear, and it affects every retention decision.
- The README says "the most generic possible person", which is not a persona.
- The product is two things pulling in different directions. One is wellness and kindness micro-tips for anyone. The other is a one-line daily to-do tracker for people with a task.
- It is deployed by IT to five employees who did not choose it. Publisher is "IT Department". Nobody arrives with a need.
- Pick the lead. I recommend the plan loop (plan, done, same). It is the only feature with personal value. The tips should be the garnish.

### Findings

**1. High, retention. Nothing accumulates, so day 30 is the same as day 1.**
- The person's only artefact is a bare count ("That is 4 plans you have finished").
- Tips and thoughts are the same for everyone and repeat exactly every 100 days. Thought and tip are locked together by `+37`, so whole screens repeat.
- After about two weeks of reading, novelty is gone and nothing else has grown.
- A count with no dates is not felt as progress.
- Fix: build the retention feature below, "Finished this week".

**2. High, retention. The only return mechanism is off by default and weakly sold.**
- The sign-in launcher asks "so it can ask about your plan?" but never says what the person gets.
- It is asked right after the first plan, before the person has seen any value. An unexplained prompt there is likely to get "n". A "n" is final, and the option is then buried at menu 2.
- Without it, return depends on remembering to open Start-menu entry "hello-world".
- Fixes:
  - Move the offer to the first moment value lands, which is the first `done` or the first "Did you do it?" answer.
  - Reword it as "Open once a day when you sign in, so it can show what you finished and what is still open?"
  - Let a "n" be re-offered once, after the person's third finished plan.
  - Teach "pin to taskbar" on the README employee page.

**3. High, ease and retention. `done` is invisible until a plan exists, and it is not taught.**
- The first-run welcome never mentions `done`. The prompt only names it after a plan is typed.
- `done` is a hidden word. The prompt "done, plan, menu or q" is five options on one line, which is dense.
- The whole mental model people were taught is y/n/Enter at "Did you do it?". Typing `y`, `yes` or `finished` at the last prompt is "not one of the choices".
- Fix:
  - At the last prompt, when a plan is on screen, accept the same yes-words as "Did you do it?" (y, yes, yep, finished, did it) as done.
  - After the first plan, say once: "When you finish it, open this and type done."
  - Cut the prompt to "Enter = close, done = finished, menu".

**4. Medium, ease. Reserved words are saved as plans at the main plan prompt.**
- At "What is one thing you want to get done today?", typing `done`, `menu`, `q`, `plan`, `no`, `skip` or `none` is saved as the plan text. Only `same` is intercepted.
- That is worse after this release, because `done` is now a taught word and people will type it reflexively at the first prompt.
- Fix: treat these as commands or as a skip, and confirm "Save 'done' as your plan? (Enter = no)" for any other single short word that matches a command.

**5. Medium, ease. Success is announced before the save, so a failure contradicts itself.**
- `mark_done_now` prints "Good. That is one less thing..." and "That is N plans..." first, then saves. On a save failure it rolls back and says "Could not save that on this computer."
- The person has just been congratulated for something that was not recorded.
- Fix: save first, then celebrate. On failure, print only the failure and say the plan is still open.

**6. Medium, retention and ease. After `done` the session dead-ends.**
- It prints the praise, then "Press Enter to close". The plan is cleared and there is no offer of what is next.
- Someone who finishes a task and wants to set the next one cannot do so. They must close and reopen.
- Fix: after `done`, prompt "Type the next plan, or Enter = close". This turns one finished plan into a loop inside the same session.

**7. Medium, ease. An unfinished plan costs two prompts every day.**
- "Did you do it?" then "Keep it for today?". Enter at the second already means keep, so this is the commonest second-session path.
- Fix: make `n` ("not yet") keep it automatically and say "Kept. Type clear to drop it." That is one question, not two.

**8. Medium, ease. The first run front-loads text and asks.**
- Order is: a seven-line privacy and welcome block, then the thought and tip, then a plan question, then "Saved", then the sign-in question, then the last prompt.
- That is roughly 25 lines and three prompts before the first close. It contradicts "readable in under 20 seconds".
- Fix:
  - Show the thought and tip first.
  - Shrink the welcome to two lines: "Saved here, nothing sent. Menu 1 shows exactly what."
  - Drop the sign-in offer from the first run entirely (see 2).

**9. Medium, retention. Retention cannot be measured, and the pilot has no protocol.**
- By design the program reports nothing, and "ask five employees" is the plan.
- A person who quietly stops tells nobody.
- Fix, without telemetry:
  - Add a one-page pilot script.
  - On day 14, each pilot user voluntarily reads out menu option 1 (visit dates, done count) to the owner.
  - Pre-write the questions: "When did you last open it, and why?" and "What would make you open it tomorrow?"
  - Set the pass bar before the pilot, for example "4 of 5 opened on at least 8 of 14 working days".

**10. Medium, retention. Corruption recovery has no path back.**
- A damaged file is moved to `notes.json.bak` and the person starts fresh. They are told the earlier days and plan "could not be read".
- Nothing offers to try restoring from the backup. Their count and `same` are gone.
- Fix: say "IT can often recover this; send them notes.json.bak". Longer term, keep one rolling good copy (`notes.json.prev`) at each successful save.

**11. Medium, ease. "Delete everything" is clear but harsher than the person may realize.**
- The y/n prompt is safe: Enter cancels and `done` is not accepted. It does not say that the done count, `same` and the earlier plan all go.
- A typo such as "yse" is treated as cancel here. That is safe, but it is inconsistent with the "named and asked again" behaviour at every other prompt.
- Fix: add the sentence "This also clears your finished count and the earlier plan." Use `ask_choice` so a typo gets named.

**12. Medium, retention. The next-day prompt offers a plan that was already finished.**
- After `done`, tomorrow the plan prompt shows `type same for: "<up to 120 chars>"`. That is inside the prompt line and can wrap badly.
- For a one-off ("Send the invoice") this is noise.
- Fix: show the earlier plan on its own line, as `set_plan` already does. In `daily()`, tell recurring plans apart, for example by offering `same` only when the plan has been finished twice.

**13. Low, ease. The menu puts the most-used action last.**
- Plan is option 6, after Help (5). `Choose 1 to 6` is correct, but order matters.
- Fix: plan first, saved data last.

**14. Low, retention. The weekday and the real week are ignored.**
- The thought is the same on Monday morning and Friday evening.
- A Friday "what did you finish this week" screen is a natural return moment, and nothing uses it.
- Fix: feed the weekly summary below.

**15. Low, ease. The README is long and some bullets are misplaced.**
- The "Sign-in reminder" bullet opens with plan follow-up text unrelated to sign-in.
- Employee instructions and IT install steps are in one file.
- Fix: put `Employees.md` or a short top section first, and keep it to what an employee needs.

**16. Low, ease. `done` double-counts if the plan is retyped.**
- Typing a plan, `done`, `same`, `done` increments the count each time.
- This is harmless to the person and fine for a private count. Just do not read the count as meaningful.

### What works
- State is saved before the last prompt, so closing the window loses nothing.
- Writes are atomic, and a damaged file is kept as a backup, not overwritten.
- Reopening the same day shows the plan and asks nothing new. A launcher run on a day already seen is silent.
- The "welcome back, no guilt" copy and the lack of scores are consistent with the audience.
- Typos are now named and asked again, with three tries and then no change.
- `same` makes day two faster.

### Highest-leverage changes, most important first
1. **Build "Finished this week" this round** (details below). It is the only thing that gives the person something of their own to come back to.
2. **Make `done` learnable.** Accept yes-words at the last prompt. Teach it once after the first plan. Guard reserved words at the plan prompt (findings 3 and 4).
3. **Keep the loop going after `done`.** Offer the next plan in the same session (finding 6).
4. **Save before praising** (finding 5).
5. **Move the sign-in offer** to the first success, say what the person gets, and allow one re-offer (finding 2).
6. **Shrink the first run** to value first, privacy in two lines, no sign-in offer (finding 8).
7. **Write the pilot protocol with a pre-agreed pass bar** (finding 9).
8. Remove the second question when a plan is "not yet" done (finding 7).

### Retention feature to build this round: "Finished this week"
**What.**
- On `done`, store the date and the plan text in a small local list: the last 7 finished plans, with their dates (at most 7 entries).
- The daily screen shows one line when there is something to show: `Finished this week: Send the invoice, Call the bank, Book travel.`
- After the third finished plan in a week, add a single warm line: `Three this week. That is a good week.`
- Option 1 shows the same list. Delete everything removes it, like the other saved items.

**Why the person would come back.**
- Today a finished plan vanishes. After this, opening the program is how you see what you got done, and it is the only place that list exists.
- The new `done` moment then pays off twice, once when you finish and again the next time you open it.
- It makes Friday afternoon a natural return, because that is when someone wants to remember the week's work. It also gives a reason to open on a Monday after a week away ("Last week you finished...") without any guilt wording.
- It turns the plan feature from a prompt into a small record that only the person owns.

**Privacy and honest cost.**
- This reverses part of the "no history of plans" stance. It is a larger change than the single previous plan and the count.
- Mitigate it: cap at 7, keep dates and texts only, keep it local, show it only to the person, and say so in README, PLAN.md and the first-run text.
- Show that the privacy copy matches: "Menu option 1 shows exactly what is saved, including these."
- The developer declined the weekly recap and the last-five plans as product decisions. For a retention release gate I would reopen that decision for the pilot, because without this there is no accumulating value. If it is still declined, then the plan loop (findings 3, 6 and 7) is the minimum to ship.

**Cheap companion for the second session.** Make a numbered "recent plans (1-3)" pick at the plan prompt, so a repeating plan is one keystroke, not typing `same`. It uses the same stored list.

---

## Accessibility

ACCESSIBILITY REVIEW, hello-world 1.13.0 (WCAG 2.2 AA applied to a console program, its plain-text output, CLI help, installer output and docs)

I read the whole packet (dev notes, hello.py, tests, installer, uninstaller, README, PLAN and the WHY doc). I ran nothing.

Verdict: no Critical findings. There are 2 High findings, and fixing both is cheap. The round-38 work is real progress. The new `not_a_choice` helper names the typed word and lists the choices. The output is linear plain text, ASCII only, with no color dependence and no redrawing, and Enter alone always works. The gaps are the ones below.

-----------------------------------------------------------------
SHIP THIS ROUND (all small code changes in hello.py)
1. Fix the dead-end prompts after `done` and `plan` (H1).
2. Say what happened after three misunderstood answers, and after an undecodable input (M1, M2).
3. Remove "done" as a yes at "Keep it for today?" (M3).
4. Soften the README and PLAN accessibility claims until a screen-reader pass has happened (H2).
-----------------------------------------------------------------

HIGH

H1. After `done` or `plan`, the program says one thing and does another, and any typed text closes the window.
- Where: `daily()`, final loop. The `done` and `plan` branches call `ask("Press Enter to close > ")` and throw the answer away.
- WCAG: 3.2.2 On Input, 3.3.1 Error Identification, 3.3.2 Labels or Instructions, 3.2.4 Consistent Identification (best fit).
- Problems:
  - `mark_done_now` with no plan prints "There is no plan to mark as done. Type plan to set one." The very next prompt only says "Press Enter to close", and typing `plan` there closes the window with no message.
  - Typing `menu`, `q` or a typo at "Press Enter to close" also closes the window silently. The main last prompt names typos and asks again, so the same program treats the same input two different ways.
  - A keyboard or screen-reader user who follows the instruction on screen loses the window and any message they have not finished reading.
- Fix: do not close on text. Run the same loop as the main last prompt, with its not-a-choice handling. Show "Press Enter to close, or type plan, menu or q >" after `done` and `plan`. Only an empty answer, `q` and EOF should end it. Add a test: `done` with no plan, then `plan`, then a plan text, should end with the plan saved.

H2. Screen-reader behavior is unverified, yet the docs claim it.
- Where: README ("designed so a screen reader reads it in order"), PLAN ("Designed for, not yet verified"), BACKLOG (the screen-reader pass was declined). The dev notes also say the console reading of the new prompts is untested.
- WCAG: 4.1.2 Name, Role, Value and 1.3.2 Meaningful Sequence cannot be evidenced. This is a release-gate evidence gap, not a defect I found in the code.
- Risk areas:
  - The two-line `input()` prompt: the question, then "(Press Enter to skip) >".
  - A trailing ">" glyph that is read as "greater than" or dropped.
  - Typed echo in conhost versus Windows Terminal.
  - A window that opens at sign-in and takes focus.
  - Quote marks in the not-a-choice message.
- Fix, before the release is called accessible:
  - Run one NVDA pass and one Narrator pass, in conhost and in Windows Terminal. Cover first run, the follow-up, the plan, `done`, a typo, the menu, delete and `--help`. Record the results in `reviews/`.
  - Until then, drop or soften "Everything works... designed so a screen reader reads it in order" in README to "has not been tried with a screen reader yet", which it already says elsewhere.
  - Put the screen-reader pass back in BACKLOG as scheduled rather than declined.

MEDIUM

M1. Three wrong answers end in silence.
- Where: `ask_choice` returns None after 3 tries, and the callers print nothing. The test `test_a_mistyped_yes_or_no_is_named_and_asked_again` asserts that "Left as it was." is absent.
- WCAG: 3.3.1, 4.1.3 Status Messages.
- Result: a screen-reader user hears three errors, then the screen moves on with no statement of the outcome. The same happens at the sign-in offer: nothing is saved and nothing is said.
- Fix: print a one-line outcome at each caller.
  - Follow-up: "Not understood three times. Your plan is left as it was."
  - Sign-in offer: "Not understood. It will ask again later. Menu option 2 turns it on."
  - Update the test.

M2. An input decoding error silently skips the prompt.
- Where: `ask()` catches `UnicodeError` and returns None. In `daily`, that means the plan prompt is skipped as if nothing was typed.
- WCAG: 3.3.1.
- Result: someone typing in a non-Latin script on a console code page that cannot decode it gets no feedback. The plan is dropped and "Saved" is not shown.
- Fix: in `ask`, say "That text could not be read by this window. Try again with plain letters, or press Enter to skip." and re-ask once. Treat only EOF as no answer.

M3. `done` counts as a yes at "Keep it for today?"
- Where: `YES + ("not yet",)` in the keep prompt. `YES` contains "done".
- WCAG: 3.3.4 (error prevention in spirit) and 3.3.1.
- Result: a person who types `done` at "Keep it for today?" (meaning "I finished it") gets "Kept for today." and the plan stays open.
- Fix: at the keep prompt use `STRICT_YES + ("not yet",)`, so `done` is named as not a choice. Better: treat `done` there as a real done, reusing `finish_plan`.

M4. A success message is shown before the save, so a failed save contradicts it.
- Where: `finish_plan` prints "Good. That is one less thing..." and the count before `save`. If the save fails, `mark_done_now` prints "Could not save that on this computer." afterwards. The follow-up path in `daily` does the same.
- WCAG: 3.3.1, 4.1.3.
- Result: the screen reader announces success, then failure, and the person must work out which is true.
- Fix: save first. Print the done line and the count only after the save succeeds. If it fails, print only the failure and say the plan was left unchanged.

M5. Hard-wrapped lines at 72 columns do not reflow in a narrow window.
- Where: `wrapped()`, `indent()`, the first-run welcome and the other `say()` blocks with manual line breaks.
- WCAG: 1.4.10 Reflow, 1.4.4 Resize Text (in the console sense).
- Result: low-vision users enlarge the console font, so the window is often 40 to 60 columns wide. A 72-column hard wrap then wraps again into ragged half-lines. Prompts and file paths are not wrapped at all.
- Fix: compute the width from `shutil.get_terminal_size(fallback=(80, 24)).columns - 1`, capped at 72. Use `textwrap.fill` for the welcome, expiry, "Saved on this computer" and help paragraphs instead of fixed line breaks.

M6. The daily plan prompt embeds the previous plan in the prompt string.
- Where: `skip = f'(Press Enter to skip, or type same for: "{state["previous"]}")'`. The plan can be up to 120 characters.
- WCAG: 1.4.10, 3.3.2.
- Result: it is unwrapped, and it is read as part of the prompt label. The dev notes say the earlier plan is "printed wrapped on its own line", which is true only in `set_plan`, not here. `test_output_is_plain_ascii_and_short` also exempts every line containing "> " from the 72-column check, so this is not caught.
- Fix: print `wrapped("Earlier plan: ", previous)` on its own line, as `set_plan` does. Keep the prompt short: "Type your plan, same to reuse it, or Enter = skip >". Remove the "> " exemption in the length tests, or measure prompts separately.

LOW

L1. Help text has drifted from the program.
- `HELP` mentions only `plan` and `menu`. It omits `done`, `same`, `q` and `?`. `MENU_HELP` omits `h` and the `help` and `?` words.
- WCAG 3.3.2.
- Fix: one short "At the end of the screen" list that matches the real prompt.

L2. Confusing wording.
- "Cleared. It stays as same until you delete everything." is hard to parse ("stays as same"). WCAG 3.3.2.
- Suggested: "Cleared. Type same at the plan prompt to bring it back."
- The expiry message already uses clearer wording.
- Also "Enter = keep" appears at the plan prompt even when there is nothing to keep.

L3. Inconsistent escape words.
- `q` works at the last prompt and the menu, but not at "Did you do it?", "Keep it for today?", the sign-in offer or the delete confirmation. The prompts say Enter, so it is operable. Consider accepting `q` as "skip" at the yes/no questions too.
- The delete confirmation (`reset`) treats a typo as no without naming it. That is a safe default and it says "Nothing was deleted.", but it could add 'I read "yse" as no.'

L4. Non-ASCII plan text prints as "?" on consoles that cannot show it.
- The plan is saved correctly but read back as "????". README says so. WCAG 3.1.1/3.1.2 are N/A to a console. This is a known limit.
- Optional: warn once when a replacement happened.

L5. Color and progress in the installer.
- `Write-Host -ForegroundColor` Cyan, Red and Green are all paired with text ("FAILED:", "Installed...", "Uninstall failed:"), so 1.4.1 passes. Contrast depends on the user's console palette, which is outside the program's control. Red on the legacy PowerShell blue is about 3.9:1.
- `Write-Progress` in `Assert-AdminOnlyTree` is announced inconsistently by screen readers. The text line before it ("this can take several minutes") is the real mitigation. Consider a periodic text line, such as every 1000 items, in non-Quiet mode.

L6. Focus steal at sign-in.
- The launcher opens a new window at sign-in. It is opt-in and documented. Note the behavior in the README for screen-reader users, since it interrupts the login announcement.

L7. Generic errors and an unmarked cut.
- "something went wrong (ValueError). Contact IT." is acceptable, but it goes to stderr only, and the shortcut's `pause` is the only thing keeping it readable.
- "Unknown option: ...[:60]" cuts without "...". The new helper adds "..." elsewhere.

L8. README density.
- The "What is saved" paragraph has a very long parenthetical and a 150-word "Coming back" bullet. The "Sign-in reminder" bullet starts with a sentence about plan follow-up, so the label does not match its content. Headings, lists and the code block are otherwise fine. WCAG 1.3.1 passes. The point is plain-language clarity for the stated audience. Split into short bullets.

L9. Test quality.
- `test_done_at_the_last_prompt_counts_the_plan_the_same_day` has `... or "done" in first.stdout`, which is always true (the prompt contains "done"). Remove that clause or assert on a DONE_LINES string.
- No test covers the H1 dead end or M1 to M4.

PASSES worth keeping
- Operability and flow:
  - All operation is by keyboard, with no timing and no motion.
  - There is a single top-to-bottom flow with blank-line separators.
  - The window title is "hello-world", the shortcut has a description, and the last line of installer failures starts "FAILED:".
- Wording and cues:
  - Prompts state what Enter does.
  - Errors name the typed word, are cut with "...", and list the valid choices.
  - Outcomes are echoed for most actions.
  - No meaning is carried by color or position.
  - The in-a-row line is optional and gentle.
- Safety:
  - A clear yes is required for deletion.
  - Typed control characters are stripped from the output, which protects a screen reader from escape sequences.

Files reviewed: the review packet only.
