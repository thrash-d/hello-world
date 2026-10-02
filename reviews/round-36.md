# Round 36

- Date: 2026-10-02
- Commit reviewed: a5872cb (version 1.10.0)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1 (all given to every reviewer, plus the newest changelog entry)
- Agents run: lead, security, usability and retention, accessibility
- Redactions: none needed

## Lead reviewer

# Review of hello-world 1.10.0 (round 36)

I read all 2720 lines of the packet and nothing else. I ran nothing. Every finding comes from reading the code, so none of it was run on Windows or on Python 3.14.

The packet says "every file in full", but it omits `CHANGELOG.md`, `BACKLOG.md`, `reviews/`, `.devkit/kit/*` (including `commit_lint.py`) and `hello.cmd`. I could not check the developer's claims about the backlog or the round-35 findings. I could not check the "report only" behaviour of the commit lint step either.

Verdict: no Critical findings. The core `hello.py` is solid, and the damaged-file, hostile-input and dead-stdout handling is good. The headline retention change largely misses the people already using the program. The "tested" story has a Windows hole. A few of the accessibility fixes are only half applied.

## Part 1: Findings, most severe first

### 1. High, retention: the sign-in offer never reaches existing users
- `offer_reminder` only fires when `len(state["visits"]) == 2`.
- Anyone already on 1.7 to 1.9 has three or more visits, so they never see it.
- Those people are the deployed base (the "five employees" in PLAN.md).
- The release's main retention lever therefore does nothing for them. A user who skips or misses the second visit never sees it either.
- Fix: offer when `not state.get("offered") and len(visits) >= 2 and no launcher exists`, on the first interactive visit. Add a test with a notes file holding 5 visits and no `offered` key.

### 2. Medium, retention: the offer is shown only to people who already came back
- The only person who sees the offer is one who returned on day 2.
- The moment of highest intent is the end of day 1, right after "Saved. Tomorrow it will ask how this went."
- A person who never returns never sees the lever.
- Fix: ask once at the end of the first run, after a plan is saved. If you want it softer, ask at the end of the first run and then again on the second visit, if the first answer was Enter or an unrecognised reply and not an explicit "n".

### 3. Medium, retention and ease of use: the second visit has too many questions
- Day 2 with a plan can ask, in order: "Did you do it?", "Keep it for today?", "What is one thing...?", the sign-in offer, then the closing prompt.
- That is up to five prompts before the program ends.
- This contradicts the "useful in under 20 seconds" promise and the "Enter alone works" claim, because each Enter is a decision.
- Fix: skip the plan prompt after a "keep" or a "done". Fold the offer into the closing line, for example "Type signin to open this each day". Or move it to the first run (finding 2).

### 4. Medium, bug and data loss: "Left as it was." can be false
- If the answer to "Did you do it?" is Enter or an unrecognised word, the old plan stays dated yesterday.
- The next block (`elif not seen_today`) then asks for a new plan.
- Whatever is typed silently replaces the "left" plan.
- Fix: after "Left as it was.", skip the plan prompt. Alternatively, say "This replaces yesterday's plan" before the prompt. Add a test.

### 5. Medium, bug in the tests: Windows runs are not isolated from the real Startup folder
- `run()` passes `startup=None`.
- On Windows, `startup_file()` then resolves to the real `%APPDATA%\...\Startup`.
- Every second-visit test therefore sees the sign-in offer on Windows and gets one extra prompt that eats typed input.
- `test_menu_shows_saved_data_and_toggles_the_in_a_row_line` types `m` into the offer and will fail.
- Any test that ends up typing `y` at the offer would write a real launcher into the developer's Startup folder.
- The packet admits Windows is untested, and this is exactly the kind of failure that hides there.
- Fix: default `startup` to a fresh `tempfile.mkdtemp()` in `run()`. Add a Windows CI job; it would have caught this.

### 6. Medium, accessibility and ease of use: Ctrl+C and Ctrl+Z do not quit
- `ask()` turns `KeyboardInterrupt` and `EOFError` into "no answer".
- A keyboard or screen-reader user who presses Ctrl+C to get out is walked through every remaining prompt.
- The day is then recorded as a visit.
- The developer declined this as a product decision. I disagree. This is a standard keyboard escape, and ignoring it is a trap-like behaviour.
- Fix: on `KeyboardInterrupt`, finish the current save and exit, or at least print "Stopped. Nothing else was changed." Also accept `q`, `quit` and `exit` at every prompt.

### 7. Medium, accessibility: the menu toggles hide which way they go
- "2  Open once a day at sign-in: off (change it)" and the same for option 3.
- A screen reader reads state plus "(change it)". The direction of the change is never stated.
- Fix: write the action: "2  Turn on: open once a day at sign-in" and "2  Turn off: ...". Echo the result, as option 3 already does. Option 2 also never says "Done" beyond what `remind` prints, but that is fine.

### 8. Medium, ease of use: the command-line options are unreachable for the people they are written for
- HELP and the README say "run hello.cmd with one of these".
- `hello.cmd` lives in `Program Files\hello-world` and is not on PATH.
- Nowhere does the program or the README give that path.
- Employees get the Start-menu shortcut, which takes no arguments.
- Fix: print the real path in HELP, built from `__file__`. Or have the installer add the folder to the machine PATH, or add a `hello-world.cmd` shim.

### 9. Medium, trust and documentation: the privacy statement is now wrong
- The program saves a new `offered` field.
- The README says it "saves nothing else (apart from your in-a-row setting)". PLAN.md and docs/WHY-DAILY-ACTIONS.md say the same.
- The README is the promise made to employees, so correct it.
- Fix: update the three documents. Also make `show_saved` label each field in plain words.

### 10. Medium, ease of use: the sign-in offer treats any non-yes as a permanent no
- Enter, "yse" and "maybe" all set `offered=True`, print "No problem", and never ask again.
- This is inconsistent with the closing prompt, which you fixed to say "not one of the choices" and ask again.
- A typo permanently removes the lever.
- Fix: accept only y or n. Re-ask once on anything else. Treat Enter as "ask me next time", not "no".

### 11. Medium, ease of use: a typed plan on any day after the first is never confirmed
- "Saved. Tomorrow it will ask how this went." prints only when `first and intent`.
- On later days the user types a plan and sees nothing until the next open.
- Plan text that was tidied is never shown back.
- If saving fails, the user only gets the generic message at the end.
- Fix: always print "Saved your plan for today: ..." after a typed plan.

### 12. Medium, security (supply chain), declined by the developer, still stands: `dependabot-automerge.yml`
- It merges major updates automatically. A repo with no `package.json`, no `requirements.txt` and no `test_*.py` merges nothing; this repo has `test_hello.py`.
- For this repo, Dependabot can only be updating GitHub Actions. The only gate is this program's own tests, which never exercise a workflow.
- `auto-tag.yml` has `contents: write`, so a bad Action update can run with that.
- Other defects in the same workflow: `--squash` is used with no `--match-head-commit`, so there is a rebase race. The `devkit-quality` secret and OSV checks are not required before the merge.
- Fix: do not auto-merge major updates. Pin Actions by SHA. Require the quality workflow before merge.

### 13. Low to Medium, ease of use: save failures give neither cause nor action
- "Could not save that on this computer." and "Your notes could not be saved on this computer. This screen still works."
- Neither names the folder or says what to try.
- When `load()` returns `can_save=False` for a locked or unreadable file, the user is shown the first-run Welcome text. They are treated as new, though they are not.
- If the move of a damaged file fails (`os.replace`), nothing is said at all.
- Fix: print the folder path and the OS reason once ("File is in use" or "No permission"). Do not show the first-run text when the file exists but cannot be read.

### 14. Low to Medium, upgrade risk: a window left open blocks the installer
- The sign-in launcher opens a console that waits for Enter.
- A user who leaves it open keeps `python.exe` running from `Program Files\hello-world`.
- `Rename-Retry` fails after five tries on that machine.
- The installer says only "close every window" in the README.
- Fix: name the holding processes in the error. Optionally offer `-CloseOpen` to stop `python.exe` whose path is under `$dir`.

### 15. Low, bug: a plan older than 14 days disappears without a word
- `daily` sets `intent=None` and then saves it.
- Fix: say "Your plan from 3 October was cleared." or keep it. Document the 14-day rule in the README.

### 16. Low, bug: the date can change while the window is open
- `daily()` computes the date once. `set_plan` calls `today()` again.
- A window left open overnight, such as the sign-in window, dates a typed plan to the next day.
- The "left open" window case is realistic.
- Fix: pass `iso` into `set_plan`.

### 17. Low, content bug: a wrong weekday
- The thought "An ordinary Tuesday done well is something quietly to be proud of." shows on any weekday.
- It shows on Thursday 1 October, which is the date used in the tests.
- Time-of-day mismatches are similar: "Leave on time tonight", "Before you log off", "Let the evening belong to you", and "Eat lunch away from your desk today" appear at sign-in.
- The developer declined time tags. Removing the weekday name is free: change it to "An ordinary day done well...".

### 18. Low, accessibility and consistency: hyphens still split in thoughts and tips
- L10 fixed `wrapped()`, but `indent()` still uses default `textwrap.wrap`.
- Hyphenated words in the content ("ten-minute", "twenty-five", "thank-you") can split across lines.
- Fix: pass `break_on_hyphens=False, break_long_words=False` to `indent()`.
- Related: a 120-character unbroken string or CJK text will not wrap at 72. That is acceptable.
- Related: the CJK plan width is counted in characters, not columns.

### 19. Low, accessibility: the closing flow ends without saying so
- After a second wrong answer at the closing prompt, the program prints "That was not one of the choices." and then closes silently.
- Fix: print "Closing." The developer's note claims that the first-run line now says "type plan or menu". It does not: it says only "Type menu at the end of this screen". The test passes anyway, because the closing prompt contains that text.
- Fix: say "type plan or menu" in the first-run line as well, and assert on the first-run text.

### 20. Low, security: the launcher and the uninstaller
- `uninstall.ps1` runs elevated and deletes `<profile>\...\Startup\hello-world-daily.cmd` for every profile in `ProfileList`.
- A user can replace their own `Startup` folder with a junction. The delete then follows it, but only for a file with that fixed name, so the impact is tiny.
- Folder-redirected profiles keep their launcher.
- The `.cmd` written into Startup by `python.exe` is a persistence pattern (T1547.001). EDR products may alert on it.
- Fix: check for reparse points before deleting. Tell IT in the README to expect that alert.

### 21. Low, installer: three smaller problems
- Cyan step text, written with `Write-Host -ForegroundColor Cyan`, has poor contrast on a light console. Errors carry the "FAILED:" prefix, so they are not colour-only.
- ARM64 is rejected. An x64 build runs under emulation on Windows 11 ARM, but not natively.
- The Python 3.14.8 pin is untested here, as the developer says.

### 22. Low, CI and tests
- The "Commit messages" step has no `continue-on-error`, though it is labelled "report only". I cannot see `commit_lint.py`.
- `auto-tag` tags a commit before CI has passed on it.
- The `${{ }}` interpolations of step outcomes are safe.
- Tests never check all 100 tips and 100 thoughts for ASCII, length or `!`.
- There are no tests for the "Cleared." and "Kept for today." echoes the developer says were added.

### 23. Low, ease of use and support: unexpected errors are undiagnosable
- An unexpected error prints only `something went wrong (ValueError). Contact IT.`
- There is no log and no traceback.
- Fix: write the traceback to `<data dir>\error.log`, and name that file in the message.

### 24. Low, minor
- The window can flash on every later sign-in on the same day, when `--startup` exits at once.
- "Unknown option" goes to stdout, not stderr.
- "(Enter keeps it as it is)" appears when there is no plan.
- Only English yes and no are understood.
- A gap of 4 days, such as a long weekend, breaks the in-a-row count although the docs say weekends do not.
- "Days you opened hello-world: N" contradicts the stated rule of showing no visit counts.

## Part 2: Improvements, most important first

1. **Retention: move the sign-in question to the end of the first run and cover existing users.** Ask once, after the plan is saved. Roll out to every user who has not been asked (findings 1 and 2). This is the cheapest change with the biggest effect.

2. **Retention: make the next day shorter, not longer.**
   - Offer "Enter = same plan as yesterday" and "d = done, no new plan today".
   - Drop to two prompts maximum.
   - Why it matters: every extra prompt is a reason to stop opening it.

3. **Accessibility: a real exit and plain toggle labels.**
   - Accept `q`, Ctrl+C and Ctrl+Z at any prompt, with a one-line "Stopped" message.
   - Label toggles with the action they perform (findings 6 and 7).
   - Add a `--once` or "reader" mode that prints the screen and exits with no prompts and no pause, for people using a screen reader who want to read it once.

4. **Accessibility and ease of use: print where `hello.cmd` is.** HELP and the menu should show the full path, or the installer should put a `hello-world` command on PATH (finding 8).

5. **Retention: give the plan some weight, privately.**
   - Allow two or three items. Let "done" mark one at a time.
   - Add an opt-in "things I finished" list the user can see and delete. It is opt-in so it stays consistent with the "no record of done" trust rule.
   - Why it matters: the plan follow-up is the only feature with personal value, and it holds one line.

6. **Retention: a reason to open it on day 100.**
   - The content repeats exactly every 100 days, with the same pairings.
   - Grow it toward 365, or rotate pairings each cycle.
   - Let the owner drop an `extra.txt` of their own lines for the team. The developer declined it; it is cheap and gives IT or a manager a way to keep it fresh.

7. **Product direction.**
   - The purpose is clear enough in README and PLAN.md: a daily moment for employees.
   - Honestly, the installer has had about 25 rounds and the program is about 500 lines. The deployment is more engineered than the product.
   - The strongest hook is the plan and its follow-up. Spend the next effort there. Consider a native Windows notification at a time the user picks, instead of a console window at sign-in.

8. **Trust: show the saved data in plain words.** Option 1 prints raw JSON. Print "Plan: ..., Days opened: ..., In-a-row line: on, Asked about sign-in: yes", then offer the JSON on request.

9. **Quality: make the test suite honest.** Add a Windows job, isolate `STARTUP_DIR` and `HOME` in every test, and add tests for the existing-user offer, a bad answer at the offer, and all content strings.

## What was fine
- Atomic save with a temporary file and `os.replace`.
- Numbered backups that never overwrite the first one.
- Hostile notes files: control characters, deep JSON, future dates and a byte-order mark.
- Dead-stdout handling and exit codes.
- No colour or art in the program output.
- The installer's pinned hash, admin-only trees, rollback, and cleanup of the process environment.

## Security reviewer

# Security review: hello-world 1.10.0

Scope: I read the whole packet (2,720 lines), including hello.py, install.ps1, uninstall.ps1, test_hello.py, the three workflows, and the docs. I read no other files and ran nothing. The packet does not include CHANGELOG.md, BACKLOG.md, reviews/, the `.devkit/` kit, or the generated `hello.cmd`. The README links to the first three, and the workflows use `.devkit/`, so I could not review them.

## Verdict

- There are no Critical or High findings.
- There are 2 Medium and 5 Low findings, plus 3 informational items.
- The application code (`hello.py`) is clean. The risk is in the deployment path and the CI.

## Findings

### M1. Dependabot auto-merge gate is weak and can be steered (Medium)

Where: `.github/workflows/dependabot-automerge.yml`. This is CWE-1357, CWE-829 and CWE-367, and relates to NIST SA-12, CM-3 and SI-7, and ATT&CK T1195.001/.002.

1. **The test gate does not test the update.**
   - This repo has `test_hello.py`, so the `check` job sets `ran=1` whenever any Dependabot PR arrives, including a GitHub Actions version bump.
   - Those tests exercise only `hello.py`, which has no dependencies.
   - The workflow comment says nothing merges "because nothing showed the update works." For this repo the opposite is true: everything merges.
   - A Dependabot bump of a workflow action, which can include a major version, therefore lands on `main` with no human review.
   - The `auto-tag` workflow on `main` holds `contents: write`, and all actions are pinned by tag only.
2. **Install scripts run during the check.**
   - If a `package.json` or `requirements.txt` ever appears, `npm ci`, `npm install` and `pip install` run the bumped package's install scripts on the runner. This is arbitrary code execution from the dependency.
   - The token is read-only, which limits the impact, but a malicious package that passes trivial tests still gets merged.
   - Checkout also leaves the token in `.git/config` because `persist-credentials` is not turned off.
3. **The authorization test is the PR author, not the pusher.**
   - The check is `pull_request.user.login == 'dependabot[bot]'`.
   - Anyone with write access can push extra commits to a `dependabot/*` branch. The author stays the bot, the tests pass trivially, and the merge job merges the whole branch.
   - This sidesteps any "needs a human reviewer" expectation. It matters if branch protection requires reviews, because the workflow merges as `GITHUB_TOKEN`.
4. **Time-of-check to time-of-use gap.** `gh pr merge "$PR" --squash` merges whatever the head is at merge time, not the commit that was tested. A push between `check` and `merge` goes in untested.
5. **The merge job relies on a skipped dependency.** It has no `if` of its own and depends on `check` being skipped for non-bot PRs. That works today but is fragile.

Fix:
- Add `if: github.event.pull_request.user.login == 'dependabot[bot]' && github.actor == 'dependabot[bot]'` to both jobs.
- Use `dependabot/fetch-metadata`. Auto-merge only patch and minor updates of a known ecosystem, and never `github-actions` or major bumps.
- Pass `--match-head-commit "${{ github.event.pull_request.head.sha }}"` to `gh pr merge`.
- Use `npm ci --ignore-scripts` and `persist-credentials: false`.
- Require a branch-protection status check and a human review.
- If the repo has no dependencies, remove this workflow.

### M2. The README bootstrap runs git.exe as admin before the installer's Git permission check (Medium)

Where: README "For IT: install" and the `.EXAMPLE` in `install.ps1`. This is CWE-426, CWE-367 and CWE-693, and relates to NIST CM-5, CM-14 and SI-7, and ATT&CK T1574.

- The installer's step [1/6] exists to prove that only administrators can modify Git for Windows. That check runs only after the pasted lines have already run `git.exe clone` as administrator.
- The pasted lines use the raw admin environment. They do not clear `GIT_*`, `HOME` or `XDG_CONFIG_HOME` the way the installer does. They also do not check that `$git` is under Program Files.
- The scenario the check guards against is Git installed to a user-writable path such as `C:\Git` and registered under HKLM. In that case, a planted `git.exe` or a sibling executable has already run as admin by the time the check could object.
- The commit pin only protects what gets installed. It does not protect the clone step.

Fix:
- Ship a small bootstrap that does the checks before any `git` call: path under Program Files, admin-only ACL tree, cleared environment, `GIT_CONFIG_NOSYSTEM`.
- Or use `git -c` and environment hardening in the README lines.
- Or document that Git must be verified first.
- Give the commit hash out of band (a ticket or a signed message), not from the repo being installed.

### L1. CI tooling is pulled without integrity checks (Low)

Where: `devkit-quality.yml`. This is CWE-494 and CWE-829, and relates to NIST SA-12 and SI-7.

- osv-scanner, gitleaks and vale binaries are downloaded with `curl` from release URLs. The versions are pinned but there is no SHA-256 check, and gitleaks and vale are piped straight into `tar`.
- `pipx install ruff==…` and `npx --yes jscpd@5.3.2` have no hash pinning, and jscpd's transitive dependencies float.
- Actions are pinned to tags (`@v5`, `@v6`), not commit SHAs.
- The impact is capped by `contents: read` and no secrets, so this is Low.
- The developer declined SHA pinning, and I agree the risk is small, but it is still a standing supply-chain exposure.

Fix: verify published checksums (or use `sha256sum -c`), pin actions to SHAs, and use `npm ci` with a lockfile for jscpd.

### L2. The secrets and quality gates can be disabled by the PR they scan, and are non-blocking by default (Low)

Where: `devkit-quality.yml`. This is CWE-693, and relates to NIST SA-11 and SI-7.

- On `pull_request`, the checked-out tree includes the PR's own `.gitleaksignore`, `.devkit/gitleaks.toml` and `.devkit/kit/*`. The PR can allow-list its own leak or change the scripts that judge it.
- `DEVKIT_BLOCKING` is unset by default, so osv, ruff, lint and the other checks only report.
- Nothing here shows that any check is a required status.
- `osv-scanner` exiting with code 128 (no lockfiles) is reported as clean.

Fix:
- Read gate configuration from the base branch (a trusted checkout of `base.sha`).
- Make the checks required in branch protection.
- Default `DEVKIT_BLOCKING` to true.

### L3. Bundled Python is pinned, has no update path, and is invisible to the scanner (Low)

Where: `install.ps1`, `$pyUrl` and `$pySha256`. This is CWE-1104 and CWE-1395, and relates to NIST SI-2 and RA-5.

- The embedded 3.14.8 interpreter ships its own libraries (OpenSSL, sqlite, expat, libffi, zlib).
- Fixing a CVE means bumping two constants, cutting a release, and reinstalling on every PC.
- osv-scanner has no lockfile to read, so this never alerts.
- The program makes no network connections and parses only its own small JSON file, so exposure is low.
- The hash and URL are pinned, which is good. I cannot verify the hash value.
- There is no Authenticode check of `python.exe` after extraction.

Fix: add a scheduled check (CI job or Dependabot-style) that compares the pinned version to the latest 3.14.x. Add `Get-AuthenticodeSignature` on `python.exe` and the DLLs.

### L4. A general-purpose interpreter, with ctypes, is readable and runnable by every user (Low; Medium where AppLocker or WDAC is enforced)

Where: `install.ps1` grants `Users` read and execute on `python\python.exe`. This is CWE-1188, with CIS 2.5 and 2.7 (allowlisting), NIST CM-7 and CM-10, and ATT&CK T1059.006 and T1218.

- Any standard user can run `C:\Program Files\hello-world\python\python.exe` with arbitrary code, including `ctypes` and native calls.
- On a PC that blocks scripting, this is a signed, path-allowed interpreter that could be used to evade the block.
- `hello.cmd` uses `-I`, but that protects only `hello.cmd`.

Fix:
- Add an application-control rule so that `python.exe` in that path may only run `hello.py`.
- Or delete unused extension modules from the embed. Only `ctypes` is needed for the console check, and it could be replaced.
- Or freeze the program into a single launcher.

### L5. Data-file permissions and temp-file handling on POSIX (Low)

Where: `hello.py`, `save()` and `load()`. This is CWE-276, CWE-377 and CWE-59, and relates to NIST AC-6 and MP-4.

- On Linux or macOS the folder is created with `makedirs(exist_ok=True)` and the file with `open(..., "w")`, both under the default umask. That typically gives 0755 and 0644, so `notes.json` (the plan text, which the README warns may be sensitive) is readable by other local users.
- The temp name is predictable (`notes.json.<pid>.tmp`) and is opened without `O_EXCL` or `O_NOFOLLOW`.
- On Windows, `%LOCALAPPDATA%` inherits a per-user ACL, so this does not apply there. The code's own POSIX branch is only used in tests and development.

Fix: `os.makedirs(..., mode=0o700)` and create the temp file with `os.open(tmp, O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW, 0o600)`. Alternatively, drop the POSIX path.

### L6. Elevated uninstall deletes through user-controlled paths, and misses redirected profiles (Low)

Where: `uninstall.ps1`, the per-profile loop. This is CWE-59 and CWE-73, and relates to NIST AC-6 and CM-5.

- As admin it runs `Remove-Item -LiteralPath <profile>\AppData\Roaming\...\Startup\hello-world-daily.cmd -Force` for every profile.
- A user owns that path and can turn `Startup` into a junction, so the admin delete follows it.
- Impact is limited to deleting a file named exactly `hello-world-daily.cmd` in a directory of the user's choosing. That is a minor tampering primitive rather than an arbitrary delete.
- Roaming or redirected profiles and unloaded hives are not covered, so a stale launcher can remain. It points at a path that standard users cannot write to, so it is a nuisance, not an exposure.

Fix: resolve and refuse reparse points in the path before deleting (reuse the existing `Assert-NotLink` pattern), and report profiles that were skipped.

### L7. Sign-in reminder is Startup-folder persistence (Low, mostly detection and consent)

Where: `hello.py`, `remind()` and `offer_reminder()`. This is ATT&CK T1547.001.

- The program writes a `.cmd` into the user's Startup folder. This is consent-gated and documented, and nothing starts without a yes. EDR will flag it, and the SOC should be told.
- `is_yes` accepts "done" as a yes (`YES` includes it). At the new sign-in prompt, a stray "done" turns persistence on. The word is meant for the follow-up question, not this one.
- A no (or any other text, including garbage) is recorded as `offered`, which fails safe.
- The path check blocks `"` and `%`, which is enough for the fixed Program Files path.

Fix: use a separate strict set (`y`, `yes`) for the sign-in offer. Tell the SOC to expect `hello-world-daily.cmd` in the Startup folder.

## Informational

- **I1. Trust anchor and SHA-1.**
  - The reviewed commit hash comes from the same repo that is being installed. The pin is a SHA-1 git object ID, and nothing verifies a signed tag or commit.
  - A SHA-1 collision attack on a git object is impractical today, and git detects the known attack patterns. A signed tag verified out of band would be stronger.
- **I2. Training admins to click through UAC.** The README tells staff that a UAC prompt reading "Windows PowerShell" is expected. This is accurate, but it teaches users to approve exactly the prompt an attacker would imitate. The installer's `Publisher = 'IT Department'` is a self-asserted label, not a verified one.
- **I3. Central workflow source.** The workflow headers say a separate `dev-kit` repo overwrites these files. Whoever controls it controls CI in every repo that uses it. I cannot see that repo.

## Checked and clean

- **Injection (CWE-78, 89, 94).**
  - `hello.py` has no `subprocess`, `eval`, `exec`, `os.system` or SQL.
  - `hello.cmd` quotes both paths. The only pass-through is `%*`, which receives whatever the caller passes, and nothing untrusted registers a handler for it.
  - The Startup launcher rejects `"` and `%` in the target.
  - Workflow expressions in `run:` steps are only step outcomes (fixed values), `vars.*`, and SHAs passed through `env`. The PR URL goes in via `env`, not interpolation. I found no script injection.
- **Terminal escape and output injection.**
  - Plan text, unknown-option text and file content pass through `tidy`, which keeps only printable characters (and ZWJ and ZWNJ). That removes ESC, CR, bidi overrides and other Cf or Cc characters.
  - `--stats` and menu option 1 re-serialize cleaned state rather than echoing the raw file.
  - Tests cover this.
- **Deserialization (CWE-502).**
  - Only `json.loads` is used, and only on a file capped at 1 MB.
  - Deep nesting, huge integers and bad types are all caught, and the file is moved aside as a backup.
  - There is no pickle, yaml or eval.
- **Path traversal and file handling.**
  - All paths are built from fixed names. `reset()` deletes names found by `os.listdir` filtered to `notes.json.*`, with no user-supplied paths.
  - Writes are atomic through `os.replace`, and a file that can't be read is never overwritten.
- **Environment and test hooks.**
  - `TODAY`, `HOME`, `STARTUP_DIR` and `FORCE_INTERACTIVE` are module globals, not environment variables. A test checks that `HELLO_*` variables are ignored.
  - The installed launcher runs `python -I`.
- **Resource exhaustion.** Visits are capped at 400, the plan at 120 characters, and the file at 1 MB. The backup-number loop only grows when the file is damaged repeatedly.
- **Installer integrity.**
  - It enforces an admin-only ACL tree on the setup folder, Git, `ProgramData\Git` and the new install.
  - It rejects reparse points and checks parent folders.
  - It requires a 40-character commit and verifies the four installed files against that commit.
  - It checks the Python SHA-256 before use and builds beside the old install, with rollback.
  - It sets a fixed, admin-only shortcut ACL.
  - I found no gap in the design apart from M2.
- **Secrets (CWE-798).** The packet has none. The commit hash in the README is an obvious placeholder, and a wrong one fails closed. `.gitignore` covers `.env`, keys, `*.bak` and `install.log`. Gitleaks scans full history. No credentials are written to the install log.
- **SSRF, XSS, CSRF, authn and authz.** Not applicable. The app has no network, no web surface and no accounts. The installer's only downloads are fixed URLs (python.org and the GitHub clone), and the Python download is hash-pinned.
- **Data exposure.**
  - The README honestly states that the plan is stored in plaintext, that IT can read it, and that backups persist.
  - `reset()` removes the backups and temp copies.
  - Uninstall deliberately leaves notes behind and says so.

## Not verifiable from the packet

- The Python hash and URL.
- Windows ACL behavior.
- Repo branch protection and settings.
- Whether Dependabot is configured at all (no `dependabot.yml` is in the packet).
- The contents of `.devkit/`.

## Usability and retention reviewer

# Product review: hello-world 1.10.0 (ease of use and retention)

I read the whole packet (2,720 lines). I ran and edited nothing, and I read nothing else on disk. `CHANGELOG.md`, `BACKLOG.md` and `reviews/round-35.md` are not in the packet. I took the declined items from your notes and did not re-check the reasons.

## Verdict

The release gate is not met. The first screen is clear and honest, and the plan and follow-up loop is a real idea. But nothing in the product makes a person come back on day 2, and the one return mechanism you added is offered too late. The people most likely to churn are the ones who press Enter at every prompt. This release treats their Enter as a permanent "no".

## Who this is for

This is unclear, and it matters for retention.

- The README and PLAN say "the most generic possible person". The installer, though, is an IT-pushed deployment to five employees who did not ask for it.
- Nobody here chose it. There is no announcement text, no "what is this" email, and no stated job to be done.
- The README mixes the employee page and the IT install steps in one file. Employees will never read it.
- The product mixes three jobs: a wellness tip, a motivational thought, and a one-item to-do. Only the to-do has personal value, and it is the weakest to-do tool a person could pick. It holds one item of 120 characters, has no same-day completion, and expires after 14 days.
- Decide who the first-week user is and what they do on day 2. Everything below is written for "an employee who tried it once because IT installed it".

## Findings

### Critical

**1. The return mechanism is offered after the moment it is needed. (Retention)**
- The first-run screen now promises "Tomorrow it will ask how this went." Nothing makes tomorrow happen.
- The sign-in offer appears only on the second visit (`len(state["visits"]) != 2` returns early). A person has to have already come back on their own to be offered a way to come back.
- Day 1 to day 2 is where one-time users are lost, and the offer is aimed at the people who already survived it.
- Fix: make the offer at the end of visit 1, right after "Saved. Tomorrow it will ask how this went."
  - Wording: "Want it to open tomorrow when you sign in, so it can ask? (y/n)".
  - Keep it opt-in with nothing on by default. Only the moment changes.
  - The person has just made a one-line commitment, and this is the best time to ask.

### High

**2. A reflexive Enter at the sign-in offer is recorded as a permanent no. (Retention, ease of use)**
- In `offer_reminder`, any answer that is not yes sets `offered=True`. That includes Enter, "maybe", and a typo.
- The design assumes a user who presses Enter through everything, and that user never sees the offer again.
- Fix: only an explicit `n` is final. Enter or an unclear answer means "not now", and it asks again at most two more times on later visits. Change the prompt to `(y = yes, n = no thanks, Enter = ask me later)`.

**3. Users who already have the app never get the offer. (Retention)**
- The condition is exactly two visits. Anyone upgrading from 1.9 or earlier with three or more visits is never asked.
- A person who skipped visit 2 and comes back on visit 3 is never asked either.
- Fix: offer when `not offered`, there are at least 2 visits, and the launcher is not already on. This covers the five current employees.

**4. "Once a day when you sign in" may rarely fire. (Retention)**
- The launcher sits in the Startup folder, which runs at Windows logon. It does not run on unlock or resume from sleep.
- Many office laptops sleep for days. The promised daily nudge could fire weekly or less, and the person would conclude the product "forgot" them.
- I cannot verify this on Windows. It needs testing, and the copy should be honest either way.
- Fix: say "each time you restart or sign in to Windows (not when you unlock)". Consider a per-user logon or daily scheduled task, which also needs no admin rights.

**5. Day 2 is longer than day 1, and the sign-in screen needs two Enters. (Ease of use, retention)**
- On a normal second visit the prompts come in this order: "Did you do it?", possibly "Keep it?", then "What is one thing…", then the sign-in offer, then "Press Enter to close".
- A person who only wants to read needs two Enters (skip the plan, then close). At sign-in that is a chore every morning.
- Fix:
  - Merge the plan prompt and the close prompt into one: "Type today's plan, or press Enter to close (menu for options)".
  - Show the sign-in offer only once.
  - Skip the offer and welcome text on repeat visits.
  - One Enter should be the fast path.

**6. The sign-in launch uses up the day's only plan question. (Retention, ease of use)**
- In `--startup` mode the plan question appears while the person is logging in and busy. They press Enter.
- `seen_today` is then true, so the plan question is never asked again that day. The visit is also recorded just because the window appeared.
- This inflates the "in a row" line. A person who never reads the screen still gets "3 times in a row".
- Fix: in startup mode, show the content and a single prompt. Do not count a visit, and do not spend the plan question, unless the person typed something. Ask the plan question on the first manual open, or let `plan` stay available.

**7. The privacy text discourages the feature it sits next to. (Ease of use, retention)**
- First run prints seven lines of welcome and privacy before any value. "Do not type passwords or private details" comes just before the plan prompt, and the prompt has no example.
- A cautious employee reads this as "don't type anything real", so the plan feature feels unsafe.
- Fix: put the thought and the tip first. Give the plan prompt an example: `(for example: Send the invoice) > `. Cut the privacy block to two lines ("Saved only on this PC. Type menu to see exactly what.") and link the full text from the menu. Keep the "IT could read the file" statement, since it is honest, but place it after the plan prompt.

### Medium

**8. Typing a plan on any day after the first gives no confirmation. (Ease of use)**
- The "Saved. Tomorrow it will ask…" line prints only when `first and intent`.
- Later plans, and plans set through `plan` or menu option 6 on the first-run path, give no feedback in the main flow.
- Fix: always print "Saved. Tomorrow it will ask how this went." (or a shorter form) after any new plan.

**9. A plan can only be closed tomorrow. (Retention)**
- If the person finishes the task at 3pm, reopening shows the plan and asks nothing. The reward line ("Good. You can put that one down now.") arrives the next morning, if at all.
- Fix: on a same-day reopen with an open plan, ask "Is this done yet? (y/n, Enter = not yet)". Yes gives the done line immediately and clears the plan.

**10. A damaged file gives a fresh start with no way back, and the newcomer text reappears. (Ease of use)**
- After repair, `first` is true again. A three-week user sees "Welcome. Each day this gives you…" on top of the damaged-file notice.
- The notice names the backup but gives no way to recover from it. The only instruction is that option 4 deletes it.
- The in-a-row count restarts silently, and `offered` is lost, so a person who said no is asked again.
- Fix: after a repair, skip the first-run text and say "Your earlier days and plan could not be read" once, in one block. Add a "recover from backup" option in the menu, or at least say that IT can help open the `.bak` file. Carry `streak` and `offered` over from the backup when they can be read.

**11. "Could not be saved" has no next step. (Ease of use)**
- The message "Your notes could not be saved on this computer. This screen still works." gives no path and no cause.
- The person cannot act, and tomorrow's promise is quietly false.
- Fix: name the folder, say what to try (restart, ask IT), and do not print the "Tomorrow it will ask" promise in that case. (The current `elif` chain already avoids it; keep that guarantee under test.)

**12. No quick pick for yesterday's unfinished plan. (Ease of use)**
- "Same as last time" is declined as a product decision, so I flag it as a retention cost.
- Answering "n" then "y" works, but a plan that rolls over two days in a row means retyping or re-answering.
- Fix: on "Did you do it? n", offer "Keep it for today? (Enter = yes)". Today Enter already keeps it, but the prompt says `(y/n)`, so the default is invisible. Say `(Enter = yes)`.

**13. The milestone design leaves long dead spans. (Retention)**
- The "in a row" line appears at 3, 7, 14, then 30, 60, and so on. Between 14 and 30 visits there is nothing, and the 3-day tolerance blurs what "in a row" means.
- The line also counts launcher windows (finding 6).
- Fix: after fixing the counting, add one low-key line at 21 (or replace the 30-gap with 21 and 30). Keep it optional as it is now.

**14. Content is the same for everyone and repeats every 100 days. (Retention)**
- The thought and tip pair is fixed by date, so the same pair recurs every 100 days.
- Neither is time-aware. Tips such as "Choose one word for how you want the afternoon to feel" show at 8am. Tag the tips by time of day (declined for now; I would revisit it).
- There is nothing to collect, skip, or react to, and no way to see yesterday's thought.
- Fix: add a menu item "Show yesterday's thought". Later, add "I liked this one" saved locally. Neither needs anything new in the file format beyond a small list.

**15. The name and the first line look like test software. (Retention)**
- A Start entry named "hello-world" and a headline "Hello, world!" read as a developer sample. People do not search for that, and they do not rediscover it a month later.
- The rename is declined as a product decision. I would revisit it: the description, "A daily thought and one small thing to try", is good and is buried.
- Fix: name the Start entry after the description, for example "Daily Moment", and keep the `hello-world` folder name internal.

**16. Option 1 shows raw JSON. (Ease of use)**
- The "Show what is saved" screen ends with a JSON dump with ISO dates (`"visits": [...]`). This is IT-facing, not employee-facing.
- It also shows a day count and last-7-days count, which contradicts "A count is not value".
- Fix: print "Days you opened it: 12. Your plan: …". Put the raw view behind a separate option or `--stats`.

### Low

**17. Sign-in windows give no way to turn the launcher off from the screen. (Ease of use)**
- The first window that annoys someone is the sign-in window. The way out is menu option 2, but nothing on that screen says so.
- Fix: on `--startup` runs, add one line: "To stop this opening at sign-in, type menu, then 2."

**18. "Did you do it?" with an unclear answer says "Left as it was." and moves on. (Ease of use)**
- Your note says M2 is fixed by asking again at the closing prompt only. The follow-up question itself accepts "maybe" and quietly keeps the plan.
- Fix: ask once more here too: "Please type y or n, or press Enter to skip."

**19. A plan older than 14 days is dropped without telling the person. (Ease of use)**
- A plan from 10 days ago is asked about ("Did you do it?") right after "Welcome back", which can read as a check-up. At 15 days it vanishes silently.
- Fix: after a gap over 7 days, skip the old plan and say "Welcome back. Starting fresh today."

**20. Ctrl+C is swallowed by `ask`. (Ease of use)**
- It is treated like Enter and walks the person through the remaining prompts. Outside `ask` it exits with 1, which makes the shortcut show "Press any key to continue".
- Your notes list "Ctrl+C quits" as a declined product decision. At minimum, make both paths end quietly.

**21. The menu orders the most useful action last. (Ease of use)**
- Option 6 (set today's plan) is the only action most people would use, and it sits after Help. Destructive "Delete everything" sits at 4, next to Help.
- Fix: put the plan first and delete last, separated by a blank line.

**22. The delete prompt gives no preview. (Ease of use)**
- "Delete all saved notes and dates on this computer? (y/n)" does not say how many days or what plan will go. Single-key y is accepted.
- It is a reasonable guard. A preview ("12 days and your plan 'Send the invoice'") would make it safer.

**23. The README mixes audiences and has no employee-facing announcement. (Ease of use)**
- Fix: add a short plain-text "What this is" note IT can paste into an email or intranet post, and move the install steps to their own file.

## Highest-leverage changes, most important first

1. Move the sign-in offer to the end of visit 1, right after the plan is saved (finding 1).
2. Make Enter mean "ask me later" and extend the offer to existing users (findings 2 and 3).
3. Make the sign-in window cheap and not consume the plan question or count as a visit (findings 5 and 6).
4. Verify and fix the "once a day" promise (finding 4).
5. Rewrite the first-run screen: value first, an example plan, a short privacy line (finding 7).
6. Add same-day completion (finding 9).
7. Make the damaged-file path recoverable and quiet for existing users (finding 10).
8. Rename the Start entry and present a clear audience (findings 15 and 23).

## Retention features to build this round

**Primary: the "open tomorrow so it can ask" offer at the moment of commitment (findings 1 to 3).**
- Why the person comes back: they have just typed a plan and been told it will be asked about. The offer makes tomorrow's question appear in front of them without effort.
- It removes the need to remember. A person who forgets the app tomorrow loses the follow-up, which is the only personal payoff the product has.
- It stays opt-in, so it respects the "never on by default" rule.

**Secondary: same-day "Is this done yet?" (finding 9).**
- Why the person comes back: finishing a task gives a reason to reopen the window that same afternoon. They get an immediate acknowledgement instead of waiting a day.
- It turns the plan from a note into a loop with a reward. That is what a one-item to-do needs to feel worth opening.

## Not verified

I did not run anything. Findings 4 and 20 depend on Windows behaviour I could not check from the packet. Everything else is read from `hello.py`, the tests, the README and PLAN.

## Accessibility reviewer

# Accessibility review: hello-world 1.10.0 (round 36 against WCAG 2.2 AA)

Scope: the packet, read in full (developer notes, all 2,720 lines). Nothing was run. The interfaces are a console program (`hello.py`), its CLI help, the PowerShell installer and uninstaller output, the README and docs, and the CI summary. I judged the console and plain-text flow by the WCAG intent, since WCAG is written for web content.

Not applicable:
- Target size (2.5.8) and pointer gestures: there are no pointer controls.
- Motion and flashing: there is none.
- Timeouts (2.2.1): there are none, and `ask()` never times out.
- Color: the program uses none. The installer's use of color is covered below.

## Verdict

One High finding, so I would not call it release-ready until that is fixed. There are no Critical findings. The one fix to ship this round is the first item under "Ship this round".

## What passes

- One linear top-to-bottom screen, with no redraw, art or progress bars.
- ASCII-only output, and no information carried by color alone.
- Lines of 72 columns or fewer, short sentences, an unambiguous date, and a window title set by the shortcut (2.4.2).
- The only destructive action that needs confirming asks first (`Delete ... (y/n)`). Enter and unrecognised answers there mean "Nothing was deleted".
- Outcomes are now echoed ("Kept for today.", "Cleared.", "Left as it was.").
- Unknown options are named, and `--remind` or `--streak` alone says it needs on or off.
- Terminal control codes in a hostile notes file are stripped.
- The damaged-file notice now names the real backup, the folder and what was lost.

## Findings

### H1. High. Confirmations and errors vanish because the window closes right after them (4.1.3 Status Messages, 3.3.1 Error Identification)

In `daily()`, the closing loop does `set_plan(...)` and then falls through to `break`. After you type `plan`, `set_plan` prints "Done. Your plan for today is saved." or "Could not save that on this computer." and the program exits at once. The Start shortcut is `cmd /c ... hello.cmd & if errorlevel 1 pause`, and the exit code is 0, so the window closes without a pause.

The same happens when the second closing answer is unrecognised. The loop prints "That was not one of the choices." and then ends, so the window closes. The message never says it is closing.

A screen-reader user, or anyone slow to read, never perceives the result. The worst case is the failure message, because the typed plan is lost and the message is gone before it can be read.

Fix:
- After any action at the closing prompt (plan, or a second bad answer), show a final plain prompt, "Press Enter to close >". The program should exit only after that Enter.
- Make the second bad answer say "Closing now. Nothing was changed." and then wait for Enter.
- Add tests that the last stdout line before exit is the Enter prompt.

### M1. Medium. A plan typed on day 2 or later, or via `plan`, is never confirmed as saved (4.1.3)

Only `first and intent` prints "Saved. Tomorrow it will ask how this went." Every later save of a plan typed at "What is one thing..." is silent unless it fails. M2 from the last round ("silently does something") is therefore only partly closed.

Fix: after a successful save with a new or changed plan, always say "Saved. Tomorrow it will ask how this went." (shorter on repeat visits).

### M2. Medium. Unrecognised y/n answers are silently read as a decision (3.3.1, 3.3.4)

- **"Did you do it?"**: Anything that is not in the yes or no word lists (a typo like "yse", or "ok", "sure", "maybe") gets "Left as it was." The program never says it did not understand, and it does not ask again.
- **Sign-in offer**: The same kind of answer ("sure", "ok", "please") is stored as `offered: true` and answered with "No problem. Menu option 2 turns it on later." A habitual Enter press, which this design expects, does the same. The result is a permanent no that the person may not have meant.
- **"Keep it for today?"**: Any non-no answer, including garbage, keeps the plan. That is safe, but the prompt does not say Enter means yes, while the delete prompt treats Enter as no.

Fix:
- Re-ask once with "Please type y or n (or Enter to skip)."
- Widen the word lists (ok, okay, sure, please, no thanks).
- State the Enter default in every prompt, for example "(y/n, Enter = no)".

### M3. Medium. Installer color and long silent waits (1.4.3 Contrast, 4.1.3)

- **Contrast**: `FAILED:` is written in Red, steps in Cyan and success in Green. In the default Windows PowerShell console (dark blue background), pure red is about 3.9:1, below 4.5:1. It is the most important line in the output. The text is not color-only, so 1.4.1 is met.
- **Waits**: The permission checks "can take several minutes". The only feedback is `Write-Progress`, which many screen readers announce poorly or not at all, and `-Quiet` hides it. This is the "installer progress" item you declined. For an admin using assistive technology it is still a silent multi-minute wait.

Fix:
- Drop the color on `FAILED:` or use a high-contrast variant, and honor `NO_COLOR`.
- Print a plain line every N items or every 30 seconds ("Checked 4,000 items so far").

### M4. Medium. Menu option 5 and `--help` give instructions employees cannot follow (3.3.5 Help)

`HELP` says "run hello.cmd with one of these: --plain, --reset ...". Employees open the program from the Start menu, and `hello.cmd` is not on their PATH. When they choose menu option 5, they get commands they cannot run. The same text is used for `--help` and for the unknown-option reply.

Fix: use a separate in-menu help that says "Type 1 to 6 in this menu to do these things", and keep the `hello.cmd` options for IT and `--help`.

### M5. Medium. The headline accessibility claims were never tested with assistive technology

PLAN.md and the README state that a screen reader reads the program in order. The packet says no real screen reader was used, and the Windows console and Unicode paths are untested. Where the prompt text is spoken in `conhost` or Windows Terminal is unverified.

Gate: run one NVDA pass and one Narrator pass in both hosts before release. Cover first run, the follow-up, the menu, and a forced error. Or reword the claims to say "designed for", with the test status stated.

### M6. Medium. The sign-in launcher opens a window on its own, and an error there is invisible (3.2.1, 2.2.2)

The launcher runs `start "hello-world" hello.cmd --startup`. The window appears over whatever the person is doing, while a screen reader may still be loading, and it asks a question. It is opt-in, which is good. If `hello.cmd` fails, the `start` window closes at once because the `if errorlevel 1 pause` guard is only in the Start shortcut. The focus-at-sign-in item you declined is the real risk here.

Fix: add the same pause-on-error guard to the launcher line, so an error stays readable. Test the window at sign-in with a screen reader.

### M7. Medium, unverified. Non-ASCII plans may display as `?` (1.3.1, 3.1)

The program sets `errors="replace"` on stdout. A plan typed in another script is saved correctly. Where the console can't show it, the person may see `?????` for their own plan the next day and "Last time you planned: ?????". The notes call this "prints ? instead of failing", which is a graceful crash fix but not a readable screen. Behavior in the real Windows console is untested.

Fix: test with Persian, Chinese and accented text on the Windows console. If it fails, set UTF-8 output, or say "Your plan was saved but this window can't display it".

### L1. Low. Fixed 72-column hard wrap, and `say()` splits the welcome into separate lines (1.4.10 Reflow, by analogy)

At large console font sizes the text wraps twice and reads as ragged fragments. Emit paragraphs as single lines where the console wraps for itself, or at least test at a narrow width.

### L2. Low. Ctrl+C or EOF at a prompt is treated as Enter

`ask()` returns None on `KeyboardInterrupt` or `EOFError`, so Ctrl+C skips a prompt and the next one appears on the same line (no newline is printed). It is not a keyboard trap, because the prompts are finite (2.1.2 is met). It is surprising, though. Print a newline, and say "Cancelled." Whether Ctrl+C should quit is a product decision, as you noted.

### L3. Low. Failure messages give no cause or remedy (3.3.3)

"Could not save that on this computer." and "Your notes could not be saved..." do not show the folder, as `--stats` does, or say what to do. Add the folder path and "Ask IT if this keeps happening". "The saved file can't be read right now, or it is damaged" gives two causes with no next step. `--remind maybe` prints "Unknown option: --remind maybe" when the problem is the value.

### L4. Low. The developer notes do not match the code on the first-run line

The notes say the first-run line now says "type plan or menu". The first-run text says only "Type menu at the end of this screen". The test passes because the closing prompt contains the phrase. Say "plan" in the welcome text too.

### L5. Low. Menu labels and docs

- "on (change it)" mixes the current state with an action. Use "Open once a day at sign-in: on. Choose 2 to turn it off".
- The README still says the backup is `notes.json.bak`, and it is now numbered (`.bak2`).
- The README has no accessibility section (what works with Enter alone, the screen-reader status, what is untested).

### L6. Low. Start entry name, icon and language

- The Start entry is named like a dev artifact ("hello-world") and uses the Python icon. It does have a description. Renaming is a product decision, as you noted.
- The program is English only, with English month names. That is acceptable for 3.1.1 here, but record it as a known limit in the README.

## Ship this round

1. **H1 fix**: Always end the session with "Press Enter to close >" after any action and after the second bad answer, so no confirmation or error is lost.
2. **M1 fix**: Always say "Saved." after a plan is stored.
3. **Tests**: Cover both with tests.

Together these are about 10 lines in `daily()` plus the tests. Do M2 and M4 in the same pass if there is room. Schedule M3, M5 and M6 for the Windows verification run.
