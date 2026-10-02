# Round 27

- Date: 2026-10-02
- Commit reviewed: a76697c (version 1.8.0)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1, plus the newest changelog entry as developer's notes
- Redactions: none

---

# Review of hello-world 1.8.0

I read the whole bundle. I found no Critical or High issues in the code I could check. The notes' claims about M1, M2, M3, L9 and option 6 hold up against `hello.py`. The Windows side is the weak spot. I can't run PowerShell here, so I read the installer and uninstaller but did not run them.

Four things are missing from the bundle, so I could not review them: `CHANGELOG.md`, `BACKLOG.md`, `reviews/` (including `round-26.md`), and `.devkit/` (which CI calls for `vale.ini`, `ruff.toml`, `gitleaks.toml`, `check_duplicates.py` and `commit_lint.py`). I also cannot verify the pinned Python 3.14.8 URL or its SHA-256.

## Part 1: Findings, most severe first

### Medium

**1. The Windows branch of `interactive()` is never executed by any test.**
- Every test sets `FORCE_INTERACTIVE`, so the `msvcrt` and `GetConsoleMode` path never runs. That path gates every prompt and every save.
- If it wrongly returns False on some host, the program shows the screen, asks nothing and saves nothing, with no message.
- The `ctypes` call has no `argtypes` or `restype` set. An unexpected exception there ends in "something went wrong".
- Fix: set `GetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.LPDWORD]`; catch `AttributeError` and `OSError`; add a `windows-latest` job to `devkit-quality.yml` that runs the tests; when stdin is a tty but not interactive, print one line saying notes won't be saved.

**2. Two regression tests pass whether or not the bug exists.**
- `test_in_a_row_line_appears_at_milestones_only`: visits fall on days 1 to 7, then the check runs on day 14 after `--streak off`. A gap of 7 days breaks the run, so no line shows even if `--streak off` were ignored. Fix: visit days 1 and 2, run `--streak off`, then visit day 3 (the 3rd in a row) and assert there is no line.
- `test_a_bad_plan_date_does_not_turn_the_in_a_row_line_back_on`: visits 10-01 to 10-03, check on 10-04, which is 4 in a row. Four is not a milestone, so the line is absent either way. Fix: use visits 10-01 and 10-02 and a check on 10-03.

**3. Several privacy and trust statements are not quite true.**
- README, PLAN and WHY say it saves "the dates and your plan, nothing else". The file also stores the `streak` setting.
- They say option 1 shows "the file's exact contents". It prints `json.dumps` of the cleaned in-memory state. Unknown keys, text truncated to 120 characters and invalid entries are dropped. A `.bak` copy of a damaged file is never mentioned there.
- PLAN says nothing assumes a desk. About 40 of the 200 lines mention desks, inboxes, meetings, colleagues or "log off".
- The docs say the program and its tests "have run on Windows", citing a changelog the reviewer can't see. The notes say this release was tested only on Linux.
- Fix: reword these claims.

**4. The README's clone step runs git as administrator before the installer checks Git.**
- The README clones with an unchecked `git.exe`, the admin's own environment (`HOME`, `GIT_*`) and the system gitconfig. `install.ps1` clears those variables and verifies the Git folders only afterwards.
- A config writable by non-admins could run commands during the clone. The commit pin catches changed content but not code run by git itself.
- Mitigation: set `$env:GIT_CONFIG_NOSYSTEM=1` and clear `HOME`, `GIT_*` and `XDG_CONFIG_HOME` in the README snippet, or ship a small bootstrap script that does the Git permission check first.

**5. The CI supply chain is looser than the install chain.**
- `osv-scanner`, `gitleaks` and `vale` are downloaded by version with no checksum check. Actions are pinned by tag, not by SHA. The `auto-tag` job has `contents: write`, and the Dependabot merge job has write access too.
- `dependabot-automerge` merges major bumps once `hello.py`'s tests pass, but those tests don't exercise the actions being bumped.
- In blocking mode the first failing check stops the later ones. The "report only" commit-lint step has no `continue-on-error`.

**6. The sign-in launcher opens a console window at every sign-in, even when there is nothing to show.**
- The `.cmd` runs in its own window, then `start` opens a second one, and only then does `hello.py` find that today was already seen and exit.
- The launcher has no `if errorlevel 1 pause`, so an error closes the window before anyone can read it.
- Fixes: use `start /min`; make the launcher skip the launch when today is already recorded; run it hidden; at minimum, document the flash.

**7. Some pairs of "thought" and "try this" lines are duplicates.**
- Thought and tip use the same index minus 37, so the pairing is fixed. Thought index 37 ("Drink a glass of water and look at something far away...") always appears with tip index 0 ("Sip a glass of water slowly while you look out a window"). That is the same advice twice on one screen, every 100 days.
- About 40% of the "thoughts" are instructions rather than thoughts, which blurs the two sections.
- Fix: decouple the indexes, or add a test that flags near-duplicate pairs.

### Low

- **No test covers all 200 content strings.** Only one date is checked for ASCII, no `!` and width.
- **A damaged file with a UTF-8 BOM is treated as corrupt and moved to `.bak`.** Notepad can write one. Open the file as `utf-8-sig`. A second corruption also overwrites the older `.bak`.
- **Failed saves can leave `notes.json.<pid>.tmp` behind.** Clean it up in `save` on failure. A single `os.replace` failure is never retried.
- **Plans are silently cut to 120 characters** with no notice.
- **Ctrl-C at the first prompts still records the visit.** `ask()` swallows `KeyboardInterrupt`, so the L8 fix only applies outside prompts. The note ("Ctrl-C anywhere exits 1") is overstated, and neither L8 nor L9 has a test.
- **`--stats` and unknown options call `load()` first**, which can rename a damaged file. A "show" command should not change anything.
- **`sys.stdin.isatty()` raises `ValueError` if stdin is closed**, which ends in "something went wrong".
- **The in-a-row count stops reaching milestones after about 390 visits.** `MAX_VISITS=400` caps it at 401.
- **Exit code 1 from `--reset` without a terminal is not in the docstring.**
- **Tip and thought wording assumes a time of day.** "Leave on time tonight", "log off" and "the afternoon" appear at any hour.
- **`test_hello_variables_in_the_environment_are_ignored` runs against the real default data folder** and can touch a developer's real notes.
- **README's example tag is `v1.7.1` while `VERSION` is 1.8.0.** Use `<tag>`, or generate the example from `VERSION`.
- **Uninstall deletes a fixed filename inside each user profile as admin.** Low impact, but a junction planted by the user could redirect the delete. Use `-LiteralPath` plus a reparse-point check on the Startup folder.

## Part 2: Improvements, most important first

1. **Decide who this is for and what it does.** Today it is a daily wellbeing tip with a to-do. The thing with real personal use is the plan and follow-up. Make "today's one thing" the core, and let the final prompt accept `p` or just typing a plan, so it works on the second visit too. That is the only feature someone would miss.
2. **Give the deploying organisation a content file.** A read-only file in Program Files with dated, clearly labelled company lines (a phishing reminder, a maintenance window, a benefits deadline). No network, no reporting. It is the one thing that stays fresh and trusted. Keep the generic tips as a fallback.
3. **Test on Windows in CI, and add an installer smoke test.** A `windows-latest` job should run the tests and a Pester or install-and-uninstall check. Every item under "Not tested" is a Windows item.
4. **Add a set-or-change-plan shortcut and mention it on screen.** A hint line on the main screen: "Enter to close, p for plan, m for options". Option 6 is three keystrokes deep and nothing on the main screen says a plan can still be set.
5. **Define success before the pilot.** Write the three questions for the five employees, the date to ask, and a stop rule such as "if fewer than 3 of 5 still open it after 4 weeks, retire it".
6. **Test accessibility with a real screen reader (Narrator).** The claim is made but not verified, and the claim is part of the product.
7. **Keep one source of truth for facts.** Version, tag example, what is saved and test status live in about five files and drift. Generate them from `VERSION`, or have the README be the only copy and link to it.
8. **Offer "another one" and a rotation that avoids repeats.** Allow a typed `n` for a different tip, and use a shuffled sequence per user rather than a fixed 100-day loop.
