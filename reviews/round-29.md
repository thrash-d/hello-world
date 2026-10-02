# Round 29

- Date: 2026-10-02
- Commit reviewed: bff74e8 (version 1.9.1)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1, plus the newest changelog entry as developer's notes
- Redactions: none

---

# Review of hello-world 1.9.1 (round 29)

I read all 2,455 lines of the bundle and ran nothing. I could not check the pinned download hash, the tool versions, or the Windows behaviour of any code.

The bundle does not contain `CHANGELOG.md`, `BACKLOG.md`, `reviews/`, `.devkit/` or `.github/dependabot.yml`. All of these are referenced elsewhere.

I found nothing Critical. The five round-28 fixes you listed are correctly implemented in the code I can read. The main risks are about shipping, not about new logic bugs.

## Part 1: Findings, most severe first

### High

**H1. The code every Windows launch passes through has never run on Windows.**
- `PLAN.md` and `docs/WHY-DAILY-ACTIONS.md` say Windows was last tested at 1.7.1. Since then `interactive()` has changed (the new `GetConsoleMode` declaration), and the new `clean()` and `load()` code has only run on Linux.
- In `interactive()`, `import ctypes`, `import msvcrt` and `from ctypes import wintypes` sit outside any `try`. If any of them fails, or `GetConsoleMode` raises something outside `(OSError, ArgumentError, OverflowError, AttributeError)`, `main()` prints "something went wrong ... Contact IT." and exits 1. On the installed copy that would hit every employee on every launch.
- The opposite failure is a wrong "no console" answer. `ask()` then returns `None` at once, the screen prints, and the `cmd /c` window closes without waiting for Enter.
- Your own notes say the new declaration is untested.
- Fix:
  - Do the one-install, one-reinstall, one-interrupted-install, one-uninstall run on a clean PC before shipping. `PLAN.md` already lists it.
  - Add a `windows-latest` job that runs `python test_hello.py`.
  - Move the imports inside the `try` and catch `Exception`.
  - Decide which way to fail. When `GetConsoleMode` fails unexpectedly, falling back to the `isatty()` result is arguably better than a screen that flashes shut.
  - Add a test that mocks `ctypes` so the `except` branch actually runs.

### Medium

**M1. Dropping future-dated visits on load destroys real history when the clock is wrong in the other direction.**
- `load()` keeps only visits where `v <= today`, and `daily()` saves right after.
- If the PC's clock is wrong once (for example reset to 2000 after a dead CMOS battery), every real 2026 visit counts as "future" and is dropped. The save then writes the shortened list, so the history is gone for good.
- That is the opposite of "a wrong clock once can't hide real history".
- It is also inconsistent with plans: a future-dated plan is moved to today, not deleted.
- If all visits are dropped, `first` becomes true and the privacy welcome is shown again.
- Fix: keep the raw list in the file. Filter out future dates only when computing `last`, `in_a_row`, `seen_today` and the recent count. Or drop them only if the clock is plausibly right, for example more than a year ahead.

**M2. A plan longer than 120 characters is cut silently, and a plan of only joiners can be saved.**
- `clean()` ends with `[:120]` and never tells the person. The cut can fall mid-emoji-sequence, now that joiners are kept.
- A plan made only of U+200C or U+200D is truthy after cleaning, so it is saved and shown as "Your plan for today: " with nothing after it.
- Fix: say "Shortened to 120 characters" or raise the limit. Treat text with nothing but joiners as empty, for example `if not text.strip("‌‍")`.

**M3. The reviewed-commit pin has no stated trust root.**
- The README tells IT to paste "the full 40-character commit hash that was reviewed", but the hash can't be inside the commit it names.
- Nothing says where IT gets the hash.
- If they copy it from the same GitHub account that serves the code, the pin protects against a moved tag but not against a compromised account.
- Fix: say where the hash is published, for example a signed tag or a ticket outside the repo, and verify the tag signature (`git verify-tag`). Also consider hosting the repo in an organisation IT controls, not a personal account (`thrash-d`).

**M4. CI supply chain.**
- `devkit-quality.yml` downloads osv-scanner, gitleaks and vale binaries with `curl` and runs them with no checksum check.
- It runs `npx --yes jscpd` and `pipx install ruff`, both unpinned by hash. Actions are pinned by tag, not by commit SHA.
- `dependabot-automerge.yml` merges major bumps once `pytest` passes. For a bump to a GitHub Action, `pytest` exercises nothing that changed, so the "tests passed" signal means nothing.
- The job gate is `pull_request.user.login == 'dependabot[bot]'`. If someone pushes a commit onto a Dependabot branch, the PR author is still Dependabot, so the modified code could auto-merge.
- Fix: verify checksums, pin by SHA, auto-merge only patch and minor updates (use `dependabot/fetch-metadata`), and check `github.actor` as well.
- I also cannot confirm that ruff 0.16.9, jscpd 5.3.2, gitleaks 8.30.1, vale 3.22.0 and osv-scanner 2.6.0 exist. A wrong pin fails the job through `curl -f` or the install step.

**M5. CI and docs depend on files I could not see.**
- The ruff step falls back to `.devkit/kit/ruff.toml`, and the vale step uses `.devkit/kit/vale.ini`. The repo has no `ruff.toml` or `pyproject.toml`. If those files are not committed, both steps fail.
- The README's Files section lists `CHANGELOG.md`, `BACKLOG.md` and `reviews/`.
- Please confirm they exist and are committed.

### Low

1. **`--stats` changes things.** `run()` calls `load()` first, and `load()` moves a damaged `notes.json` to `.bak`. `--stats` then prints "Saved on this computer in: <path>" for a file that no longer exists. A second damaged file overwrites the earlier `.bak`, so the first backup is lost. Fix: make the read-only commands not rename, and use a timestamped `.bak`.
2. **Save durability.** `save()` does not `fsync` before `os.replace`. After a power cut the file can come back empty and be treated as damaged. Also, a concurrent `--startup` run and a manual run can overwrite each other's visit.
3. **Uncaught decode error.** `ask()` catches `EOFError`, `KeyboardInterrupt` and `OSError`. A `UnicodeDecodeError` from `input()` is not caught and becomes "something went wrong".
4. **Ctrl+C acts as Enter.** `ask()` returns `None`, so the visit is recorded and the program carries on instead of stopping.
5. **Follow-up nags.** Pressing Enter at "Did you do it?" leaves the old plan in place, so the question comes back every day for 14 days. Consider asking at most twice.
6. **Sign-in launcher flashes a window.** After the first launch each day, every sign-in still opens a console window that closes at once. `start /min` reduces it.
7. **`clean()` strips the direction marks U+200E and U+200F.** That is correct for the dangerous overrides (U+202A–U+202E, U+2066–U+2069), but the marks are legitimate in mixed Hebrew or Arabic and Latin text.
8. **Wrapping uses character counts, not display width.** A 120-character plan in CJK text with no spaces is about 240 columns wide.
9. **The docs overclaim.** They say nothing assumes a desk, a job or a level of ability, but many tips do ("under your desk", "video call", "archive five emails"). Either soften the claim or add neutral tips.
10. **The "environment variables are ignored" test proves little.** It runs `--stats`, which writes nothing, so the `not os.listdir(home)` assertion cannot fail. `HELLO_TODAY` is never shown to be ignored.
11. **Merges made with `GITHUB_TOKEN` don't trigger other workflows.** Auto-tag and the quality checks won't run after an auto-merged PR. This is harmless unless Dependabot ever changes `VERSION`.
12. **`auto-tag` doesn't validate `VERSION`.** `tr -d '[:space:]'` turns "1.9.1 junk" into the tag `v1.9.1junk`.
13. **Uninstall deletes a launcher by a fixed path under each profile's default Startup folder.** A redirected Startup folder is missed. A user-made junction could only make it delete a file with that exact name, which is negligible.
14. **No `LICENSE`, `SECURITY.md` or `CODEOWNERS`.** Branch protection on `main` isn't visible either.

## Part 2: Improvements, most important first

**What the program is.** It is a daily thought, one small thing to try, and an optional plan with a next-day follow-up. IT deploys it to about five Windows employees. That purpose is clear and sensible. The engineering effort (28 review rounds on the installer) is far larger than the product.

1. **Prove it on Windows and keep proving it.** Add a Windows CI job, run the manual install pass, and fix the `interactive()` fail mode from H1. Nothing else matters if the first launch breaks.
2. **Let the employer put content in.** A 100-item generic list repeats every 100 days. The biggest value for a workplace deployment is a small admin-only content file shipped beside `hello.py`: the team's own tips, the phishing-report address, the holiday calendar, a link to the help desk. Keep the generic lists as the fallback. This is a small code change.
3. **Fix the plan feature's rough edges (M2).** The plan is the only feature with real personal use. Silent cutting, invisible plans and nagging follow-ups hurt exactly the part that earns retention. Also let people see yesterday's plan from the menu.
4. **Define success and an end date.** The program reports nothing, so measurement is by asking. Write down the questions and when you ask (for example at 30 days: "Did you open it last week? Would you miss it?"). Decide in advance what result means "keep it" and what means "uninstall".
5. **Make updates less manual.** Delete-and-reclone on each PC is fine for five machines. Past that, package the installer for the management tool (Intune or similar) with the `DisplayVersion` registry value as the detection rule. `-Quiet` and the exit codes already support this. Set a date to review the pinned Python version, because nothing updates it.
6. **Check accessibility with a real screen reader** (Narrator or NVDA). Plain text is a good start. Allow longer plans, and consider a larger-text or high-contrast note in the README.
7. **Offer another language or tone when someone asks.** The plan already says this. Joiners now being kept makes it more feasible.
8. **Make the first-run privacy text easier to find later.** It is shown once. A "What is saved" line at the end of the screen, or the same text under option 1, would cover people who skipped it.
