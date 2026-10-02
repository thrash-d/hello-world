# Round 30

- Date: 2026-10-02
- Commit reviewed: 5468bd8 (version 1.9.2)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1, plus the newest changelog entry as developer's notes
- Redactions: none

---

CODE REVIEW: hello-world 1.9.2 (round 30)

Scope: I read all of bundle.txt (2,518 lines) and notes.txt. Nothing was run, so every finding comes from reading the code.

Not in the bundle, so I could not check them: CHANGELOG.md, BACKLOG.md, reviews/, .github/dependabot.yml, and everything under .devkit/ (kit/ruff.toml, kit/vale.ini, kit/check_duplicates.py, kit/commit_lint.py). The README and workflows reference all of them.

Verdict: I found no Critical issues and no known functional defect in hello.py. The round-29 fixes (H1, M1, M2, Low 1, Low 3) are mostly correct. One of them is incomplete: the numbered backups from Low 1 are not deleted by "delete everything" (finding 2). The biggest risk is that 1.9.2 has never been run on its real target (Windows, Python 3.14).

Verified correct in this round:
- interactive(): the imports and the GetConsoleMode call are now inside try. A real "no console" answer still returns False, and an unexpected failure returns True.
- Future-dated visits are kept out of counts but written back by save() through file_form().
- Plans of only joiner characters count as empty. Plans over 120 characters print "Shortened to 120 characters."
- A second damaged file becomes notes.json.bak2, and so on.
- ask() treats UnicodeError as no answer.
- The in_a_row zip slicing is correct, and the 100-item content lists are correctly indexed.

PART 1: BUGS AND SECURITY, MOST SEVERE FIRST

1. HIGH (release risk, not a known defect): never run on the shipped platform or interpreter.
- The only Windows run was 1.7.1. Everything since was tested on Linux with Python 3.11 (notes.txt says so).
- Production runs the Python 3.14.8 embeddable build. CI uses Python 3.12 on Ubuntu, and only on Dependabot PRs (see finding 4).
- The code that has never run on its target:
  - interactive(), which is the function whose failure makes a window flash shut. It is the area the H1 fix touched, and the notes admit the fallback has no test.
  - The shortcut line `cmd /d /c "title hello-world & "...\hello.cmd" & if errorlevel 1 pause"`.
  - The Startup launcher using `start "hello-world" "<path>" --startup`.
  - The per-profile launcher removal in uninstall.ps1.
  - The Start-menu shortcut ACL check (`Assert-AdminOnly $lnk $edit`) on a stock ProgramData Start Menu. If it fails, the install stops at step 6 after the folder swap, leaving a half-installed state.
- The pinned URL and SHA-256 for python-3.14.8-embed-amd64.zip are not something I can confirm. A typo or a non-existent patch release fails at step 4. That is a safe failure, but it blocks the rollout.
- Fix before shipping:
  - Add a `windows-latest` job that runs `python -m pytest`. Add a second job that runs install.ps1 and uninstall.ps1 on the runner. Run the PLAN.md "Not tested" checklist once on a clean PC.
  - Make CI use the shipped Python minor version (3.14).
  - Add a mocked test for the `interactive()` fallback. Only the GetConsoleMode call needs to be mocked. Do the `os.name` check through an overridable variable so it runs on Linux.

2. MEDIUM: "Delete everything" does not delete the numbered backups.
- The problem:
  - reset() removes only `notes.json`, `notes.json.bak` and `notes.json.*.tmp`.
  - The new backup_name() (Low 1 fix) creates `.bak2`, `.bak3`, and so on. These hold the raw old file, including plan text.
  - The README promises that option 4 deletes everything "including any backup copy of a damaged file". After two damage events, that is false.
- It is easy to hit: `--stats`, `--streak` and every normal run call load(), which moves a damaged file aside.
- The test only covers `.bak`.
- Fix: in reset(), delete every name in data_dir() that equals `notes.json` or starts with `notes.json.`. Make the failure message list the files left behind. Add a test with `.bak`, `.bak2` and `.tmp` present.
- Also decide whether backups should be capped, for example keep the last 3. At the moment they grow without limit.

3. MEDIUM: the "no secrets scan" gap in blocking mode.
- In devkit-quality.yml, only the osv step and later steps use `continue-on-error: DEVKIT_BLOCKING != 'true'`. None of them has `if: always()`.
- With DEVKIT_BLOCKING=true, a failing osv-scanner step fails the job. Every later step is skipped, including gitleaks. The comment on the gitleaks step says it "always runs to completion", and the file header says the secrets check always runs.
- Fix: add `if: ${{ !cancelled() }}` (or `always()`) to every check step after osv, or run gitleaks first.
- Related:
  - osv-scanner, gitleaks and vale are downloaded with curl and no checksum check. The versions are pinned, but a swapped release asset would not be caught. Verify the SHA-256 from the release checksum file.
  - Actions are pinned by tag, not SHA. This matters most for auto-tag.yml, which has `contents: write`.
  - The ruff step uses `.devkit/kit/ruff.toml`, and vale uses `.devkit/kit/vale.ini`. If .devkit is not committed, those steps fail with a config error. The gitleaks step guards against a missing config, but ruff and vale do not.

4. MEDIUM: Dependabot auto-merge is gated by tests that cannot see the update.
- The `check` job passes if pytest passes. The repo has no runtime dependencies, so a bumped GitHub Action passes without ever being exercised. Majors are included on purpose.
- Result: a major bump of `actions/checkout`, or any action, can merge itself. That includes workflows holding `contents: write`.
- The squash merge runs immediately, not as `--auto`.
- Related: no workflow runs the tests on ordinary pushes and PRs. The tests run only in this Dependabot workflow. Add a `test` job to devkit-quality (or a separate workflow) that runs on push and PR, on Windows and Linux.
- Fix: restrict auto-merge to semver patch/minor and to ecosystems the tests actually cover. Leave github-actions updates for human review. `npm ci` should use `--ignore-scripts`. Pin the pytest version.

5. LOW: the README install order runs Git as administrator before Git has been checked.
- The documented steps run `git clone` as admin, in the admin's raw environment (GIT_* variables, HOME and so on). The installer's Git ACL check and environment scrub only happen later.
- If Git's folder were writable by a non-admin, a tampered git.exe would already have run elevated by then.
- This is low risk because Git in Program Files is admin-only by default.
- Fix: add one README line before the clone. Run `icacls "$gitDir"` and confirm no write access for Users. Alternatively, ship the reviewed release as a zip with a published SHA-256 so no clone is needed.

6. LOW: exit codes and edge cases in hello.py.
- `--streak on|off` and `--remind on|off` return 0 even when they fail ("Could not save..." / "Could not set up the reminder."). The documented unattended use cannot detect failure. Return 1.
- ask() turns Ctrl-C into "no answer". At "What is one thing…" the program continues and records the visit, so someone trying to abort is counted as having visited. Let KeyboardInterrupt propagate to main() before the save.
- Truncating to 120 characters (`tidy(text)[:MAX_PLAN]`) can split a combining mark or emoji sequence. It can also leave a trailing space or joiner. Strip the end after cutting.
- The `--stats` command is described as read-only, but it can rename a damaged notes file. A caller running it from a script gets a surprise. Say so in HELP, or report "damaged, not changed".
- Two windows open on the same day (sign-in launcher plus manual start) both prompt, and the last writer wins. Rare. A simple lock file or re-load-before-save would fix it.
- The notes file has no schema version. A later version that adds fields would have them silently dropped by an older 1.9.x. Add `"v": 1` now.
- save() does not fsync before os.replace. Power loss can leave an empty notes.json. The result is treated as damaged and backed up, not lost.
- Two instances may both damage-detect. The second os.replace then fails with FileNotFoundError and sets can_save False for that run. Treat FileNotFoundError there as success.
- The sign-in launcher is created even if `hello.cmd` is not next to hello.py (running from a clone). It then fails on every login. Check that the target exists before writing it.

7. LOW: uninstall.ps1 deletes through user-controlled paths as admin.
- It runs `Remove-Item` on `<profile>\AppData\Roaming\...\Startup\hello-world-daily.cmd` for every profile.
- A user can replace a parent folder with a junction. The impact is limited to deleting a file with that exact name elsewhere. It is still better to skip any path with a reparse point in the chain.
- If the Apps entry stays after a partial failure, the installed Python may be half deleted. Documented, but the Apps entry is the only retry path.

8. LOW: documentation drift.
- The README example uses a placeholder commit hash (`0123456789abcdef…`). It is explained, but any paste without editing fails at step 3 by design. That is fine, but consider making the placeholder obviously invalid (`<40-char hash>`) so it cannot look plausible.
- PLAN.md and docs/WHY-DAILY-ACTIONS.md both repeat "Windows tested for 1.7.1 only". When the Windows run happens, update all three places (README, PLAN, WHY, notes).
- Content: some thoughts and tips assume a time of day, for example "Before you log off", "Leave on time tonight", "before your next coffee", "Nothing in your inbox needs you at nine o'clock", "Eat lunch away from your desk today". They show at sign-in at 8am. Some use UK idioms ("biscuits", "tea or coffee"). This is a polish issue, not a defect.

PART 2: WHAT WOULD MAKE IT MORE VALUABLE

Honest framing: as written, this is a daily "tip and thought" card plus a one-line plan, shipped with about 800 lines of hardened installer and 29 review rounds. The docs say this themselves: "the value was in the deployment machinery, not the program". The retention levers in PLAN.md are hypotheses, and nobody has tested them with the five employees. It is not clear who asked for it. If it is a test vehicle for IT deployment, say so in the README and do not describe it as an employee benefit.

1. Validate before building more. Put it on the five PCs for two weeks, then ask three questions: Do you open it without being told? What did you read? What would you cut? Decide continue, change or stop from that. This matters most because every further feature adds cost without evidence of value. Also rename it. "hello-world" in the Start menu tells an employee nothing. Use a name that says what it does.

2. Make the content IT's to change, so it can carry real value. Move TIPS and THOUGHTS to a UTF-8 text file in the install folder (admin-only), one item per line, with the built-in lists as fallback. Allow date-keyed lines ("2026-11-03: Payroll cut-off is Friday"). Why it matters: one daily security micro-tip (spot a phishing mail, use the password manager), the help-desk number, and real notices (office closures, deadlines) are far more useful to employees than generic wellness text. It is also the natural fit for the trust model already built. The same file makes translation and tone changes trivial, which PLAN.md already lists as "if asked".

3. Make the daily card fit the day. Tag items morning, afternoon or any, and filter by the local hour. Add "another one" (a single key) so a disliked tip is not stuck all day. Let people pick categories from the menu (move, focus, people, tidy). Use coprime list lengths (for example 100 tips and 97 thoughts) so the pairing does not repeat every 100 days; right now there are only 100 distinct screens. Why: fresh content is the main reason the PLAN says people return.

4. Make the plan feature quicker to use. Allow `hello.cmd plan Send the invoice` and `hello.cmd plan` (show only the plan) so it can be used without reading the whole screen. A "carry over" shortcut already exists in the follow-up, so keep it. Optionally allow up to three plan items. Why: the plan is the only feature with real personal use, and the daily screen is the slowest way to reach it. Keep the "no record of done or not done" rule.

5. Test and publish it properly: Windows CI (finding 1), a published checksum for each release, and a short `docs/TESTING.md` with the one-PC test checklist. Why: a broken first launch will end the trial in one day, and nobody will return to something that failed once.

6. Cut documentation and deployment weight to match the value. README currently serves employees and IT in one file; split it into README.md (employees) and docs/IT-INSTALL.md. Merge PLAN.md and WHY-DAILY-ACTIONS.md, which repeat each other. If this will only ever run on five PCs, ask whether your existing tool (Intune, GPO, winget or similar) can deploy a per-user copy. That would retire most of the 800-line install.ps1 attack surface. If the hardened install stays, keep it, but accept that further review rounds have diminishing returns (the project already says so).

7. Measure value without telemetry. A calendar reminder to ask the five people at weeks 2 and 6, plus a pre-agreed stop rule ("fewer than 3 of 5 open it weekly means retire it"). Why: the program deliberately reports nothing, so the decision needs a defined way to be made.

Top three to do before shipping: (1) Windows and 3.14 test run, (2) fix reset() to remove all backups, (3) add `if: !cancelled()` to the CI steps and stop Dependabot from auto-merging Actions bumps.
