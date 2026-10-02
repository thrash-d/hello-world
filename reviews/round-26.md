# Round 26

- Date: 2026-10-02
- Commit reviewed: c6bb25a (version 1.7.1)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1, plus the newest changelog entry as developer's notes
- Redactions: none

---

# Review of hello-world 1.7.1

I read both files in full and nothing else. I could not run anything, so every finding comes from reading the code and the notes.

## Part 1: Review

There are no Critical or High findings. The 1.7.1 fixes in the notes (NUL detection, environment restore, stdout error handling) read as correct. What remains is a handful of Medium issues, mostly where the code or docs promise something they don't do, plus Low items.

### Medium

**M1. Pressing Enter at "Keep it for today? (y/n)" silently deletes the plan.** In `hello.py` (`daily`, around line 1287), anything other than a yes sets `intent = None`. That includes Enter, Ctrl-C and end of input. The program already fixed this bug class at "Did you do it?" (Enter now keeps the plan), but the second prompt was missed. The person has just said "not yet", so dropping the plan is the worst default.
- Fix: treat only an explicit no (`is_no`) as drop. Keep the plan on everything else, and add a test for Enter and for `None`.

**M2. Menu option 3 can overwrite a notes file the program decided it must not touch.** `load()` returns `can_save=False` for a locked or unreadable file, with the promise that it is never overwritten. `daily` honours that when it saves. `menu()` option 3 calls `save(state)` directly and ignores `can_save`. On an ACL-denied or transiently locked file in a writable folder, `os.replace` can replace the real file with a near-empty state. `run()` with `--streak` does check `can_save`, so the two paths disagree.
- Fix: pass `can_save` into `menu()` and gate the save, as `--streak` does.

**M3. "Delete everything saved" leaves plan text behind.** Menu option 4 and `--reset` remove only `notes.json`.
- `notes.json.bak` (a copy of a damaged file) and `notes.json.tmp` stay in the folder.
- A `.bak` can hold an old plan. This contradicts the README ("option 4 to delete it") and the privacy promise.
- A second corruption silently overwrites the first `.bak`.
- Fix: delete the `.bak` and `.tmp` files in `reset()`, and either mention them in `--stats` or date-stamp the backups.

**M4. An open hello-world window blocks upgrade and uninstall, and the failure is not explained.** The window waits at "Press Enter" with `python.exe` running from `Program Files\hello-world`.
- `Rename-Retry` gives up after 5 seconds, and `Remove-Item` in `uninstall.ps1` has the same limit.
- An employee who leaves the window open all day makes an unattended `-Quiet` upgrade fail.
- Fix: on a rename failure, name the cause ("close hello-world windows, or retry after sign-out"). Optionally list the processes running from `$dir`, or offer a retry window. Mention it in the README's "If something fails".

**M5. The "a failed run leaves any working install as it was" claim is false for step 6.** The swap completes before `[6/6]`. If the registry write, the shortcut or `Assert-AdminOnly $lnk` fails afterwards, the new version is live, `.old` is already deleted, and the script exits 1.
- On an upgrade, Settings > Apps keeps showing the old version.
- The shortcut may be removed.
- There is no rollback.
- Fix: either defer `Remove-Tree $old` until step 6 succeeds and roll back on failure, or change the README and `FAILED:` text to say the new files are live but registration is incomplete, and rerun.

**M6. The shipping path of the installer was not exercised this round.**
- The notes say the install tests ran from "a test copy pointed at test folders, the current user's registry and a test Start menu folder", non-elevated.
- So `#Requires -RunAsAdministrator`, the HKLM key, `CommonPrograms`, the real `Assert-AdminOnlyTree` on Git and the shipped file's own code paths did not run.
- The notes say untested on Windows: real console typing, all-users Start menu, HKLM, the administrator prompt, more than one profile, and the launcher at sign-in. PLAN.md lists first install, reinstall, interrupted install and uninstall on a clean PC as unrun.
- The CI is Ubuntu-only, yet every 1.7.0 bug was Windows-specific.
- Fix: run PLAN.md's clean-PC checklist as an elevated admin on a real machine before shipping. Add a `windows-latest` job running the tests.

### Low

**L1. Docs are stale and contradict each other.**
- The README and the `install.ps1` example use `$tag = 'v1.6.0'`, but `VERSION` is 1.7.1.
- PLAN.md ("Not tested: Nothing here has run on Windows") and docs/WHY-DAILY-ACTIONS.md §8 ("Nothing has run on Windows") contradict the notes, which report 35 tests passing on Windows.
- The README lists `CHANGELOG.md`, `BACKLOG.md` and `reviews/`, and the workflows use `.devkit/kit/*` (ruff.toml, vale.ini, commit_lint.py, check_duplicates.py). None of these was in the bundle. If they are missing, the links are dead and the Vale and ruff steps misbehave. Vale is configured with `--config .devkit/kit/vale.ini`; ruff falls back to `.devkit/kit/ruff.toml` when the repo has no ruff config of its own. I could not tell which case applies.
- Fix: derive the tag from `VERSION` in the docs, or use an obvious placeholder. Update the "not tested" statements to match what was actually tested.

**L2. `uninstall.ps1` deletes, as administrator, a path inside user-controlled profiles.**
- A standard user can make their Startup folder a junction. The elevated `Remove-Item` then follows it and deletes any file named `hello-world-daily.cmd` in the target.
- The impact is tiny, because the name is fixed and the attacker cannot plant it in privileged folders.
- Fix: skip the launcher if any parent is a reparse point.

**L3. CI supply chain.**
- The workflows `curl` osv-scanner, gitleaks and vale binaries with only version pinning and no checksum.
- Actions are pinned by tag (`@v5`), not SHA.
- Fix: verify SHA-256 and pin to commit SHAs.

**L4. Dependabot auto-merge has weak gating.**
- It squash-merges major updates once only the `check` job passes. It does not wait for the secrets check, and the repo's tests cover only `hello.py`, not the installer or workflows.
- No `dependabot.yml` was in the bundle, and none manages the Python pin in `install.ps1`.

**L5. The pinned embedded Python 3.14.8 is never patched on workstations.** It updates only when someone edits both the URL and the hash and reinstalls everywhere. Add a periodic check or a note in the README.

**L6. `--stats` and the menu can mislead.**
- "The file holds only this" prints the in-memory state, not the file. If the file is unreadable (`can_save` false), it prints an empty state as if nothing were saved. If the file has extra fields, it shows a different file from the one on disk.
- The "Days you opened" count silently caps at 400.

**L7. Plans are silently truncated to 120 characters.** Tell the person, or raise the limit.

**L8. Ctrl-C outside `input()` gives "something went wrong (KeyboardInterrupt)".** Catch it and exit quietly. Visit dates in the future (a clock set back) also stop "Welcome back" from ever showing until the real date catches up.

**L9. Concurrent runs can race on `notes.json.tmp`.** For example, the sign-in launcher and a Start-menu launch at the same moment. Use a unique temp name.

## Part 2: Improvements, most important first

1. **Find out whether anyone wants it before more engineering.** The purpose is clear: a 20-second daily thought, a small action and a one-line plan for general employees. But the installer got about 25 rounds of review and the payload prints one of 100 strings. Ask the five employees after two weeks whether they still open it. If they don't, stop. If they do, ask what they use. Without this, the work is on the machinery rather than on value to the people who use it.

2. **Let people use the plan any time.** Today the plan is asked only on the first visit of the day (`elif not seen_today`). Someone who skips it and decides at 2pm can't add it until tomorrow. Add a menu entry to set, edit or finish today's plan, with Enter keeping what is there. The plan is the only feature with real personal use, and this makes it usable.

3. **Make the content fit the day and the workplace.**
   - The tips are chosen by date only, so Saturday can say "take the long way to your next meeting".
   - Add weekday awareness.
   - Let IT drop an admin-only `content.txt` of company tips or reminders (security hygiene, where to find help) next to `hello.py`. That gives IT a reason to deploy it and employees a reason to read it, with no tracking or network added.

4. **Simplify deployment.**
   - Today each PC needs a git clone of a private repo, which means GitHub credentials on every workstation and Git for Windows installed for all users.
   - Publish a release zip with a published hash, or an Intune, winget or MSI package, and keep the commit-pin verification as an option.
   - The hardening is real, but it depends on credentials and manual steps that will not scale beyond a handful of PCs.

5. **Add Windows CI.** Run `test_hello.py` and a PowerShell parse and lint check on `windows-latest`. Add a scripted smoke test of the installer's pure functions, such as `Assert-AdminOnly` against a temp folder.

6. **Keep one source of truth for facts that drift.** Take the version, the tag and the "what is untested" list from one place. The README, PLAN, WHY doc and installer help currently disagree.

7. **Give employees a way to tell IT it isn't wanted.** Uninstall needs an admin password. A "how to ask IT to remove or pause this" line in the README fits the trust the design builds.
