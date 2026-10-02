# Round 32

- Date: 2026-10-02
- Commit reviewed: 508349e (version 1.9.4)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1, plus the newest changelog entry as developer's notes
- Redactions: none

---

# Review of hello-world 1.9.4

I read both files in full. I also extracted `hello.py` and `test_hello.py` from the bundle into the scratchpad and ran them on Linux with Python 3.11, since the pinned runtime is 3.14. All tests pass. I probed a few behaviours directly, and the confirmed ones are marked below. I checked that there are 100 tips and 100 thoughts, with no duplicates, no non-ASCII characters and no `!`, and that both PowerShell scripts are pure ASCII.

I found no Critical issues. The security design is sound: the commit is pinned, the Python download is hash-pinned, the install tree is checked for admin-only ACLs, reparse points are rejected, and the program runs as the user from an admin-only folder. The previous round's regressions (`--streak` exit code, `--remind` exit code, partial launcher) are fixed and tested.

I could not verify four things:
- The Python 3.14.8 URL.
- The SHA-256 of the Python download.
- The `thrash-d/hello-world` clone URL.
- Anything on Windows.

## Part 1: Findings

### High

**H1. CI never runs the test suite on a normal push or PR, and auto-tag tags ungated.**
- `devkit-quality.yml` runs ruff, gitleaks, osv, vale and jscpd, but no pytest.
- `test_hello.py` runs only in `dependabot-automerge.yml`, and only for Dependabot PRs.
- `auto-tag.yml` tags any push to `main` whose `VERSION` has no tag, regardless of test or quality results.
- README tells IT to install "the release tag", so a tag does not mean tested.
- Fix:
  - Add a `test` job on `push` and `pull_request` that runs `python -m pytest -q`.
  - Make `auto-tag` depend on it, or move tagging into a workflow that runs after the tests pass.
  - Add `windows-latest` to the matrix (see H2).

**H2. The Windows-only code paths have not been run since 1.7.1.**
- PLAN.md and WHY-DAILY-ACTIONS.md both admit this.
- Never run on Windows:
  - the real install, reinstall, interrupted install and uninstall
  - the `interactive()` ctypes console check
  - the shortcut's `cmd /d /c "title ... & ... & if errorlevel 1 pause"` quoting
  - the Startup launcher
  - per-profile launcher removal
  - `Expand-Archive` of the embedded Python and `-I` isolation
- By my reading, the shortcut quoting should work: cmd's old rule strips the first and last quote when the line contains `&`.
- Do not ship to anyone beyond a pilot until PLAN.md's checklist (new install, reinstall, interrupted install, uninstall) has been run on a clean PC.
- Fix:
  - Run `test_hello.py` on `windows-latest` in CI.
  - Add a smoke test that runs `hello.cmd --plain` and one `--stats` run against the real embedded Python.
  - Run the pilot on one real machine first.

### Medium

**M1. Files that the repo references are not in the bundle.**
- Missing: `CHANGELOG.md`, `BACKLOG.md`, `reviews/`, `.devkit/kit/{ruff.toml, vale.ini, gitleaks.toml, check_duplicates.py, commit_lint.py}`, `.devkit/*.json`.
- If they really are absent from the repo (not just gitignored or untracked), then:
  - README's Files section and your notes (`reviews/round-31.md`, `BACKLOG.md`) point at nothing.
  - The ruff step (`--config .devkit/kit/ruff.toml`) and the Vale step (`--config .devkit/kit/vale.ini`) fail on every run.
- Fix: commit those files, or have the workflow install them. Remove the links to anything that stays unpublished.

**M2. `--reset` exits 0 even when deletion fails (confirmed).**
- `run()` calls `reset(state); return 0`.
- When `os.remove` fails, `reset()` prints "Could not delete the file..." and returns False, but the exit code is still 0.
- This is the same class of bug you just fixed for `--streak` and `--remind`, and it matters because the flag is meant for scripted use.
- Fix: return the result of `reset()` as 0 or 1. You can keep 0 when the person answers no.

**M3. Read-only commands change files (confirmed).**
- `run()` calls `load()` for `--stats`, `--reset`, `--remind` and every unknown option.
- If `notes.json` is damaged, `load()` renames it to `notes.json.bak`.
- With a damaged file, `--stats` prints "Days you opened: 0" and an empty file, and `notes.json` no longer exists.
- Fix: pass `load(repair=False)` from `--stats` and unknown options. Have `--stats` say the file is damaged instead of showing an empty state. Only `daily`, `menu` and the writing commands should move files aside.

**M4. CI and automerge supply-chain gaps.**
- `devkit-quality.yml` downloads osv-scanner, gitleaks and vale with `curl` and never checks a checksum.
- Actions are pinned to mutable tags (`@v5`, `@v6`).
- `dependabot-automerge.yml` merges major updates automatically, with only `pytest` as the gate.
  - For this repo that gate says nothing about whether an Actions bump is safe.
  - No `dependabot.yml` is in the bundle, so it is unclear what would ever trigger it.
- The merge step uses `GITHUB_TOKEN`, so merges it makes do not trigger `push` workflows. That means no `devkit-quality` run on `main` after an automerge.
- Fix:
  - Verify download checksums, or use a pinned action for each tool.
  - Pin actions by commit SHA.
  - Drop automerge, or limit it to minor and patch updates plus an explicit allowlist.

**M5. The embedded Python has no patch path.**
- Python 3.14.8 is pinned by URL and hash, and the installer re-downloads it from python.org.
- Nothing watches for new 3.14.x security releases: osv-scanner finds no lockfile, and Dependabot does not see `install.ps1`.
- Every workstation therefore runs an aging interpreter until someone remembers.
- Fix: add a scheduled CI job that compares `$pyUrl` against the latest 3.14.x on python.org and opens an issue. Also say in the README who owns that bump.

**M6. The "Commit messages" step is described as report-only but can fail the job.**
- The comment says "Report only", but the step has no `continue-on-error`.
- If `commit_lint.py` exits non-zero, the job fails even with `DEVKIT_BLOCKING` off.
- The script is not in the bundle, so I cannot confirm what it returns.
- Fix: add `continue-on-error: true`, and add the step to the warning list in Summary.

### Low

- **L1. Content claims more than it delivers.**
  - PLAN.md and WHY-DAILY-ACTIONS.md say the tips assume no "level of ability".
  - Many tips assume sight, hearing, legs or hands: "Look at something far away", "Name three things you can see, hear, and feel", "Listen to one favorite song", "Plant both feet flat", "Wave or smile".
  - Fix: reword or tag those tips, or soften the claim.
- **L2. Lost input if stdout dies mid-run.** `OutputClosed` is raised before `save()`, so a plan typed in that run is lost. This is minor and self-inflicted.
- **L3. Startup launcher has no pause on failure.** The shortcut pauses on errors, but `hello-world-daily.cmd` does not, so a failure at sign-in flashes shut. Add `|| pause` after the call.
- **L4. `save()` does not fsync.** A power loss can leave a zero-length `notes.json`. The next run treats it as damaged and starts fresh, so history is lost. Two instances running at once (the sign-in launcher plus the Start menu) are last-writer-wins.
- **L5. `uninstall.ps1 -Quiet` from a non-admin shell returns before the elevated copy finishes.** `Start-Process -Verb RunAs` is not waited on, and the process then exits 0. A management tool cannot tell whether the uninstall succeeded. Add `-Wait` and propagate the exit code.
- **L6. Profile cleanup deletes a fixed file name inside user-controlled paths as admin.**
  - `uninstall.ps1` removes `...\Startup\hello-world-daily.cmd` under each profile.
  - A user could point the `Startup` folder at another directory with a junction.
  - The damage is limited to a file with that exact name, so this is a hardening point only.
- **L7. README clone step runs before the installer's environment scrub.** `git clone` in the README runs in the admin's raw environment, with their git config and `GIT_*` variables. Only the install is scrubbed. The commit-hash check covers the content, so this is low risk.
- **L8. README "Update" steps rely on `$d` from the install window.** In a new window `$d` is empty and `Remove-Item` errors safely, but the README does not say so. `install.ps1` does.
- **L9. `Assert-AdminOnly` rejects trusted principals other than the four it lists.** For example, an ACE for Domain Admins is flagged as a non-admin. This is a false positive that fails closed.
- **L10. Truncation can split a character sequence.** `clean()` cuts at 120 code points, which can split a combining or ZWJ emoji sequence. This is cosmetic.
- **L11. Minor mismatches.**
  - Menu option 1 says "the file holds only this", but `ensure_ascii=False` means non-ASCII text is shown differently from how it is stored.
  - `Publisher` is hard-coded to "IT Department".

## Part 2: Improvements, most important first

1. **Decide who this is for, and prove it with one measurement.**
   - Right now it is a fortune-cookie console window wrapped in a very hardened deployment.
   - The docs say plainly that the value was mostly in the installer.
   - The program reports nothing, so you cannot learn whether anyone opens it twice.
   - Run the five-person pilot and ask each person after two weeks. If fewer than three still open it, stop adding features.
2. **Make the daily plan the product.**
   - It is the only feature with personal use. Make it more useful without adding surveillance:
     - Carry a plan forward with one key press.
     - Let people keep a short list of two or three items.
     - Add a one-line "what I did yesterday" view that stays local.
3. **Add content people will not tire of.**
   - 100 tips and 100 thoughts repeat in about three months.
   - Allow an optional local `content.txt` (an extra tips and thoughts file) that IT or a team can add to.
   - Alternatively, have the maintainer publish a new content release each quarter.
4. **Close the testing gap (H1, H2).** This is the largest risk to the people installing it.
5. **Give IT a safe rollout path.**
   - Support a single signed-or-hashed zip installer, and a documented Intune/SCCM command.
   - Add a read-only `hello.cmd --version` so IT can check what is installed.
   - Add a `-WhatIf` to the installer.
6. **Handle roaming and non-persistent profiles.** Notes live in `AppData\Local`, so they vanish on VDI and non-persistent machines. Either document it or support `%USERPROFILE%` as an option.
7. **Accessibility.**
   - Offer an "any ability" content set, per L1.
   - Test with Narrator and with high-DPI console scaling.
   - Respect the console's code page when printing.
8. **Cross-platform.** There is a `data_dir()` for Linux, but the launcher is Windows-only. If macOS or Linux users are in scope, say so in README. If not, remove the dead branches.
9. **Keep the privacy promises checkable.**
   - Add a CI test that greps `hello.py` for `socket`, `urllib` and `http` imports, which backs the "no network access" claim.
   - Publish the installed `hello.py` SHA-256 in each release note, which the installer already prints.

## Summary

The code in `hello.py` is correct and careful, and the previous round's fixes hold. Fix M2 and M3 (small, confirmed). Fix H1 before tagging a release. Do not roll out beyond a pilot until H2 has been run on a clean Windows PC.
