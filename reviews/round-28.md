# Round 28

- Date: 2026-10-02
- Commit reviewed: 8b81336 (version 1.9.0)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1, plus the newest changelog entry as developer's notes
- Redactions: none

---

# Review of hello-world 1.9.0

I read the 14 files you listed and the developer's notes, and nothing else. I did not run the tests or any PowerShell, and I could not see `BACKLOG.md`. Some items below may match something you already declined there.

**Verdict:** I found no Critical issues and no exploitable hole in `hello.py`. The code is careful. Its main risk is the way it ships: the admin-privileged installer and the Windows-only program have not been tested together on Windows since 1.7.1.

**Fixes from the last round that I confirmed in the code:**
- `p` at the last prompt works.
- The notes file is read as `utf-8-sig`.
- `isatty()` raising `ValueError` is handled.
- A failed save removes its temp file.
- Both streak-off tests now use a visit that would be the 3rd in a row.
- The README, installer help and `VERSION` all say 1.9.0.
- The test count of 43 matches the file.

---

## Part 1: Findings

### High

**H1. The shipping configuration has never been tested, and no CI gate exists.**
- **Where:** `devkit-quality.yml`, `dependabot-automerge.yml`, `PLAN.md` "Not tested", and the developer's notes ("Not tested: anything on Windows").
- **What is untested:**
  - `test_hello.py` is run only by the Dependabot workflow, on Ubuntu with Python 3.12. No push or PR workflow runs it.
  - The product ships on embedded Python 3.14.8 on Windows. The developer tested on Linux with Python 3.11.
  - `FORCE_INTERACTIVE` bypasses `interactive()` in every prompt test, so the real console check is never run. That check calls `msvcrt` and `ctypes.windll`.
  - There is no parse check, lint or Pester test for `install.ps1` or `uninstall.ps1`.
- **Why it matters:** every employee runs the Windows path, and the installer runs as administrator. The `devkit-quality` checks are non-blocking unless `DEVKIT_BLOCKING=true`.
- **Fix:**
  - Add a `windows-latest` job on every push and PR. Run `python test_hello.py` on 3.14 (and 3.12) and a PowerShell parse plus PSScriptAnalyzer pass over both `.ps1` files.
  - Add a `pty`-based test for the real tty path on Linux.
  - Run the PLAN checklist on a clean Windows VM before rollout. It covers one install, a reinstall, an interrupted install, an uninstall, the icon and title, Enter closing the window, and the sign-in launcher.
  - Make the CI job a required status check.

### Medium

**M1. The README bootstrap runs `git.exe` as administrator before anything is verified.**
- **Where:** README install block, lines 59-66, and the same block in the `install.ps1` help.
- **What happens:** the steps resolve `$git` from the registry and run `git clone`. They do this before `install.ps1` checks that Git and `C:\ProgramData\Git` are admin-only (steps [1/6] and [2/6]). They also clone before clearing `GIT_*`, `HOME` and `XDG_CONFIG_HOME`. A writable Git folder or system config is therefore trusted for the clone, which is the one step the commit pin cannot cover. The snippet also skips the "is under Program Files" check the installer makes.
- **Fix:** ship a tiny bootstrap script that does what [1/6] does, then clones with a cleaned environment. At minimum, put the Git ACL check and the env clearing in the README before the clone line.

**M2. The installer smoke test is too shallow, and the crash handler hides the cause.**
- **Where:** `install.ps1` line 331, `hello.py` lines 408-415, and the `main()` handler.
- **Smoke test:** it only runs `--plain`, which returns before `load()`. It never imports `ctypes` or `msvcrt`, so a broken embedded runtime or a bug in `interactive()` passes install and fails for every employee.
- **Handler:** any exception becomes "something went wrong (TypeName). Contact IT." with no traceback, no log and no contact details.
- **`ctypes` call:** `GetConsoleMode` is called without `argtypes` or `restype`. The call sits outside any try block, so an `ArgumentError` or `OverflowError` would hit that generic handler on every run.
- **Fix:**
  - Declare the call with `wintypes.HANDLE` and `BOOL`, and wrap it in try/except.
  - Add a `--selftest` option that runs `interactive()` and a dry `daily()` against a temp folder. Call it from the installer.
  - Write the traceback to a small `error.log` in the user's data folder, and show a configurable support contact.

**M3. Dependabot auto-merge can merge a major GitHub Actions bump on a test that cannot see it.**
- **Where:** `dependabot-automerge.yml`.
- **What happens:**
  - With no `requirements.txt` or `package.json`, the check job just runs `test_hello.py`, which exercises no workflow.
  - A major bump of `actions/checkout`, `setup-python` or similar therefore merges squash-immediately.
  - `auto-tag.yml` holds `contents: write` and runs on every push to main, so a compromised action gets a write token.
  - `gh pr merge --squash` does not wait for `devkit-quality`, including the secrets scan.
  - Actions are pinned to major tags, not SHAs.
- **Fix:** auto-merge only patch and minor bumps, or exclude the `github-actions` ecosystem. Pin actions to commit SHAs. Make the merge wait on the full quality workflow. Also check `github.actor` as well as the PR author.

**M4. Release integrity depends on one personal GitHub account and an unsafe auto-tag.**
- **Where:** `auto-tag.yml` and the README install block.
- **What happens:**
  - A tag is pushed for any commit on main whose `VERSION` has no tag, whether or not the tests or secret scan passed.
  - The tag is lightweight and unsigned.
  - The root of trust is `github.com/thrash-d/hello-world`.
  - The README never says where IT gets the "reviewed commit" hash, so it can end up copied from the same repo it protects.
  - Two near-simultaneous pushes can race on the tag.
- **Fix:**
  - Protect main: required checks, required review, signed commits.
  - Tag from a `workflow_run` that follows a successful CI run, and add `concurrency`.
  - Publish a GitHub Release that lists the commit SHA and the SHA-256 of `install.ps1` and `hello.py`. IT can then verify against a second channel.
  - Consider moving the repo to an organisation account.

**M5. The embedded Python has no patch path.**
- **Where:** `install.ps1` lines 110-111.
- **What happens:**
  - The pinned URL and hash are edited by hand.
  - Dependabot and `osv-scanner` cannot see them, and the repo has no lockfile for `osv-scanner` to read.
  - Every workstation will run 3.14.8 until someone remembers to rebuild.
  - Nothing shows the bundled Python version, because the Apps entry shows only the hello-world version.
- **Fix:**
  - Add a weekly workflow that checks python.org for a newer 3.14.x and opens an issue or PR with the new URL and hash.
  - Add `--version`, which prints the program and Python versions.
  - Record the Python version in the Apps entry and in the installer's result line.

### Low

**L1. Option 1 and `--stats` say more than they know.**
- **Where:** `show_saved`, line 497.
- It prints "The file holds only this:" followed by the sanitised, in-memory state, not the file's actual contents.
- The README's "you can see exactly what is saved" has the same overstatement. The same README sentence does say "tidied", but the screen does not.
- If `load()` could not read the file (`can_save` is False), the screen shows zero visits and an empty plan, which looks like "nothing saved".
- Non-ASCII plan text appears as `\uXXXX`.
- **Fix:** reword to "After tidying, the file holds:". Say "could not read" when `can_save` is False. Use `ensure_ascii=False` for display. The privacy promise is the product's main trust claim, so it should be literal.

**L2. Future-dated visits and the single backup.**
- **Where:** `load()` and `daily()`.
- A one-time wrong clock (for example 2030) leaves a future date in `visits`. It then sorts last, so `visits[-1]` is that date.
- "Welcome back" can then never fire.
- The 400-visit trim drops real history first.
- The new visit is appended unsorted for the rest of that run.
- A second damaged file overwrites the earlier `notes.json.bak` through `os.replace`.
- **Fix:** drop or clamp visits later than today on load. Use a timestamped `.bak` name, or refuse to replace an existing backup.

**L3. Exit codes do not match the contract or the docs.**
- **Where:** the module docstring, `run()`.
- The docstring promises 0, 1 or 2.
- `--reset` declined or failed, `--streak` that could not save, and `--remind` failures all return 0.
- `--reset` with no person returns 1.
- IT scripting these options cannot detect failure.
- **Fix:** return non-zero on failure and document it.

**L4. `clean()` damages some non-English text and truncates silently.**
- `isprintable()` removes ZWJ and ZWNJ (category Cf).
- These characters are required in Persian and several Indic scripts, and they join emoji sequences.
- This conflicts with the PLAN's "typed letters other than ASCII are kept".
- Plans over 120 characters are cut with no notice, and the cut can land inside a combining sequence.
- **Fix:** allow U+200C and U+200D (the bidi controls U+202A-202E and U+2066-2069 stay blocked), or strip only the dangerous Cf characters. Tell the user when a plan is shortened.

**L5. Uninstall deletes through user-controlled paths as administrator.**
- **Where:** `uninstall.ps1`, lines 65-70.
- It builds `...\Startup\hello-world-daily.cmd` under every profile and removes it with an elevated `Remove-Item`.
- A user can place a junction on that path. The impact is limited to deleting a file with that fixed name, so this is low.
- It also misses launchers in redirected Startup folders.
- **Fix:** skip reparse points in the path, and use the real Startup path where it is known.

**L6. Installer edge cases.**
- There is no Windows version check. Python 3.14 needs Windows 10 or later, and an older system fails with an unclear test-run error.
- `Get-ChildItem -Recurse` follows junctions in Windows PowerShell 5.1 while it collects the list, before the reparse-point check runs. A junction loop could hang the check.
- `Publisher = 'IT Department'` is hard-coded.
- **Fix:** add the OS check. Enumerate without following links. Make `Publisher` a parameter.

**L7. Test gaps.**
- The only pairing test checks the phrase "glass of water", so other near-duplicates between a thought and a tip can pass.
- No test asserts the `.ps1` files are ASCII. Windows PowerShell 5.1 reads BOM-less non-ASCII as ANSI, and a single em dash would silently corrupt `install.ps1`.
- No test checks that the README and installer tag match `VERSION`. That is a repeat of the stale-tag bug.
- `run()` leaves temp folders behind.
- **Fix:** add these guards: an ASCII check on both `.ps1` files, the tag-versus-`VERSION` check, and a broader duplicate-theme check.

**L8. Documentation drift and contradictions.**
- `HELP` omits `p`.
- The WHY table (section 4) omits option 6 and `p`.
- PLAN and WHY say visit counts are "kept out", but option 1 prints "Days you opened hello-world: N (last 7 days: k)".
- WHY says the actions "don't assume a desk", but many tips do:
  - "under your desk"
  - "Wipe your keyboard or screen"
  - "Tidy one small corner of your desk"
  - "recycling at your desk"
  - "Adjust your screen"
- Wording is a UK and US mix: biscuits, kettle, corridor, "1 October 2026", and "nine o'clock" and "lunch" assume an office day.
- **Fix:** align the claims with the behaviour. Pick one regional style, or make it a setting.

**L9. Repo hygiene.**
- `.gitignore` lacks `install.log` and `*.zip`. The installer writes `install.log` into the clone and fetches `python-embed.zip`.
- `.gitignore` also lacks `.ruff_cache/`.
- `.editorconfig` has no `[*.ps1]` rule to keep the encoding safe.
- `devkit-quality` runs twice on same-repo PRs because it triggers on both `push` and `pull_request`.
- `devkit-quality` downloads its tools by version only, with no checksum.

---

## Part 2: Making it more valuable

The purpose is unclear. The WHY doc says it began as a test of the deployment machinery, and PLAN.md talks about five pilot employees. Nothing says who asked for it, what outcome it serves, or what counts as success. Honestly, a console window that shows a generic thought and a stretch is unlikely to hold attention past the first week. The sign-in launcher is off by default and the program cannot see whether anyone is using it. The employer is carrying the cost of an admin-grade installer for content any wellness app already provides.

In order of importance:

1. **Decide the purpose and the success test before widening the rollout.**
   - Write one sentence: who it is for, what it is meant to change, and what number or answer means "keep" or "stop".
   - Run the five-person pilot for two to three weeks with a short, anonymous, direct question set. Ask whether they opened it unprompted, and which line they remember.
   - The program reports nothing by design, so this is the only measure. It matters because otherwise the cost of keeping the installer and review process is never justified.

2. **Give it content only your organisation can supply.**
   - Today the 200 generic lines are hard-coded in `hello.py`, and changing one means a new release and a reinstall on every PC.
   - Move the content into a reviewed data file, `content.json`, shipped with the release.
   - Let IT, security and HR add short, dated items: a phishing-report reminder, a "reboot for patches" nudge, a policy change, the real support contact, a company holiday.
   - This is the one thing that turns it from a generic wellness line into something the employer wants deployed.

3. **Make it findable and look like a real application.**
   - The name "hello-world" and Python's icon make it look like test software, and the WHY doc already says it looked like a system tool.
   - Rename it (for example "Daily Pause"), add a proper `.ico`, and show a real publisher.
   - Keep the optional once-a-day launcher and the "never on by default" rule.
   - Add a one-line "How to open me again" to the first screen.

4. **Fix deployment so it scales past five PCs.**
   - The current path is six manual admin steps that need Git for Windows on every PC and live internet.
   - Add an Intune or SCCM package: a self-contained, hash-checked payload with an install and uninstall command, with the Python pinned and bundled once.
   - Keep the commit-pin check for the hand install.
   - Add `-Quiet` result codes that a management tool can read.

5. **Add support information and a way to give feedback.**
   - "Contact IT" appears in error messages with no name, address or ticket link.
   - Add a configurable support line, and print it on error screens and in the Help text.
   - An optional one-keystroke "Was this useful? y/n", saved locally and shown through `--stats` for the user to share if they choose, would respect the no-reporting rule and still give you evidence.

6. **Test the experience for the people it is meant to serve.**
   - Run it with Narrator and with high-contrast mode.
   - Try a non-English keyboard and non-ASCII names in the profile path.
   - Add a locale setting for date format and vocabulary, and a few non-desk variants of the tips. PLAN already lists a second language as "if employees ask", so first ask them.

7. **Plan the lifecycle.**
   - Decide who owns patching the bundled Python (see M5).
   - Decide who reviews content changes.
   - Add a `--version` option and a visible version in the Apps entry, so a support call can say which release is installed.
   - Add a one-line sunset rule in PLAN.md: if the pilot answers are weak, remove it.
