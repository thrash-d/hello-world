# Round 34

- Date: 2026-10-02
- Commit reviewed: d8473d5 (version 1.9.6)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1
- Redactions: one GitHub account name replaced with `[account]`

REVIEW OF hello-world 1.9.6 (read-only, from input.txt; I ran nothing). I did not see CHANGELOG.md, BACKLOG.md or reviews/, so I can't check the "declined" items or the L9 wording note.

Verdict: no Critical or High issues. The 1.9.6 changes themselves (reset() trying every file, the damaged-file notice, the docstring and tag updates) are correct and match their tests. I traced `--reset` through a failed delete, a failed listdir and a declined prompt, and each gives the right exit code. The one unverified claim is that "all tests pass", which I can't confirm. What remains is mostly release risk on Windows, one rough edge in the new notice, and CI hardening.

PART 1: FINDINGS (most severe first)

1. Medium: the Windows and Python 3.14 install path is untested.
- The notes say nothing was tested on Windows or Python 3.14. PLAN.md and docs/WHY-DAILY-ACTIONS.md say the last Windows run was 1.7.1, and the real all-users install has never been run.
- Everything employees touch depends on that path. That includes the embedded 3.14.8 Python with `-I`, `interactive()` with ctypes and msvcrt, the Startup launcher and the shortcut quoting (`/d /c "title ... & ... & if errorlevel 1 pause"`).
- The installer's smoke test only runs `--plain`. That never exercises `load`, `interactive()`, `input()` or `save()`.
- Python 3.14 gets no test run at all, and the 3.11 runs can't show 3.14 behaviour.
- A failed install is visible and leaves the old install in place. The worse case is a silent one: `interactive()` wrongly returns False on a real console, so the window prints once and closes with nothing recorded.
- Fix: add a `windows-latest` job running `python test_hello.py` on 3.14, plus an install, `--plain` and uninstall run. If CI is out of scope, do the one-install, reinstall, interrupted-install, uninstall pass from PLAN.md on a clean PC before the wide rollout. Also pilot with a few people first.

2. Medium: dependabot-automerge.yml merges unreviewed changes with weak checks.
- The `check` job runs `pytest` on Linux. That says nothing about a bump to an Action, which is what Dependabot will mostly propose here.
- Majors are merged automatically, and the workflows use mutable tags (`actions/checkout@v5`, `setup-node@v5`). A compromised or buggy tag then runs with `contents: write` in the `merge` job.
- The gate is `github.event.pull_request.user.login == 'dependabot[bot]'`. If someone pushes extra commits to Dependabot's branch, the PR author is still the bot, so their code is checked and then merged.
- `gh pr merge --squash` without `--auto` either fails when branch protection has pending required checks, or merges before devkit-quality (including gitleaks) finishes.
- Fix:
  - Pin Actions to commit SHAs. Dependabot can still update them.
  - Restrict automerge to patch and minor updates (`dependabot/fetch-metadata`).
  - Gate on `github.actor` as well.
  - Use `--auto` with branch protection that requires the quality checks.

3. Medium: devkit-quality.yml downloads tool binaries with no checksum check.
- osv-scanner, gitleaks and vale are fetched over HTTPS and run without verification. Only ruff (pipx) and jscpd (npm) are version-pinned and fetched through a package manager.
- The token is read-only, so the exposure is limited. Still, the secrets scanner is the one check that blocks a run.
- Fix: keep a SHA-256 for each pinned release in the workflow and run `sha256sum -c` before `chmod +x`.

4. Low: the new damaged-file notice breaks the program's own screen rules (hello.py, `load()`).
- The message is one 111-character line. The 72-column rule, and the test `test_output_is_plain_ascii_and_short`, don't cover it.
- It prints before "Hello, world!", so the first thing a person sees is a notice and not the greeting.
- It doesn't name the file (`notes.json.bak`) or say how to remove it (menu option 4).
- Fix: print it with `indent()` or `textwrap`, name `notes.json.bak`, and print it after the greeting, or print it plainly and then a blank line.
- Add a test that checks line width for the damaged-file path.

5. Low: `load()` still moves a damaged file aside in runs that can't save and may not be seen.
- Examples are piped runs, a launch with no console, and `--startup` with a NUL stdin. The notice goes to a pipe, nothing is saved, and the next real visit shows the first-run "Welcome." screen with no explanation.
- The old data is still in the .bak, but to the person it looks erased.
- Fix: only repair when `interactive()` is true, or when the command is one that saves (`--streak`). Otherwise treat it as `can_save=False`.

6. Low: `save()` has no retry on Windows.
- Antivirus and the search indexer often hold a file briefly, and `os.replace` then raises PermissionError.
- The person sees "could not be saved" for that visit, and the visit isn't recorded. The installer already has `Rename-Retry` for the same reason.
- Fix: retry `os.replace` 3 to 5 times with a 0.2 second sleep.

7. Low: `ask()` turns Ctrl+C into "no answer".
- Ctrl+C at "Did you do it?" moves on to the next prompt and still records the visit. `main()`'s `KeyboardInterrupt` handler is mostly unreachable.
- Fix: let KeyboardInterrupt propagate out of `ask`, except where a safe "no" is wanted.

8. Low: `reset()` handles a folder-listing failure poorly.
- If `os.listdir` fails, it adds the whole folder to "Delete these yourself:". That is misleading, because the person may delete a folder they didn't mean to.
- Fix: print "Could not list the folder, so backup copies may remain: <folder>".

9. Low: the Startup launcher doesn't pause on failure.
- `start "hello-world" "...hello.cmd" --startup` opens a window that closes at once on an error. The Start menu shortcut has `if errorlevel 1 pause`, but the launcher doesn't.

10. Low: the Python version requirement isn't stated.
- `date.fromisoformat("20261001")` is only accepted from 3.11. `test_odd_date_spellings_are_normalised` fails on 3.9 and 3.10 dev machines.
- Fix: say "Python 3.11 or later" in the README, or skip or guard the test.

11. Low: the generic error handler gives no detail.
- It prints only "something went wrong (ValueError). Contact IT." with no traceback or log, so IT can't diagnose anything.
- Fix: write the traceback to a local `error.txt` in the data folder. It stays local and sends nothing.

12. Low: concurrent runs are last-writer-wins.
- The sign-in launcher and a manual open can race. `os.replace` prevents a corrupt file but not a lost update.
- It is rare. A note in the code is enough.

13. Low: the devkit-quality "Commit messages" step is described as report-only but has no `continue-on-error`.
- If `commit_lint.py` exits non-zero, the job fails. Check that the script always exits 0, or add `continue-on-error: true`.
- The workflow also triggers on both `push` and `pull_request`, so same-repo PRs run twice.

PART 2: WHAT WOULD MAKE IT MORE VALUABLE (most important first)

1. Be honest about the cost-to-value ratio, and have the owner decide.
- The program prints one stretch or kindness tip per day. The code is roughly 500 lines, behind a hardened installer that has had about 25 review rounds. Employees get a trivial benefit.
- The project says retention should be measured "by asking five employees". Do that before building anything more.
- Cheaper delivery of the same value is a weekly Teams or email tip, an intranet page, or a pinned note.
- If the owner keeps it, state who it is for in the README: "Employees who want a 20-second daily pause." The README already leads with this, so keep it.

2. Add a Windows test job (see finding 1).
- This is the most valuable engineering change. It turns "tested on 1.7.1" into a repeatable check on every release.

3. Give IT a way to change the content without a code change.
- Today the 200 lines are baked into hello.py, so any wording change means a new reviewed commit and a reinstall on every PC.
- Read an optional admin-controlled `content.txt` from the install folder. It is admin-only, so it carries no new trust problem.
- Then a company can add its own tips, such as the help desk link, a holiday notice or a safety message. That is the most likely reason a company keeps it installed.

4. Plan an update path for the pinned Python.
- The 3.14.8 URL and hash are manual. Security fixes to the interpreter need someone to bump both values, re-review and reinstall.
- Put a quarterly reminder in BACKLOG.md and add a CI check that fetches the Python release list and warns when the pin is behind. A reinstall script mode that upgrades without a re-clone would help too.

5. Make the first screen show the exit and the options.
- New users learn about `m` and `p` only from a first-run line and the prompt. The last prompt "Press Enter to close, p for today's plan, m for options" is clear, so keep it.
- Consider an accessible "--stats" or "--help" mention on the README "For employees" page. It mostly exists already.

6. Offer a safe export of the history.
- Option 1 shows what is saved, but a person can't keep or move it without hunting for the file. A "show where the file is, and how to copy it" line would help. It is already printed, so this is minor.

7. Add a small count check for the content.
- A test that asserts exactly 100 tips and 100 thoughts, no duplicates and ASCII only, would protect the "repeat every 100 days" claim when someone edits the lists later.

8. Consider ownership of the source.
- The installer clones from a personal GitHub account (`[account]`) onto admin PCs. The pinned commit hash makes that safe. For a company rollout, an organisation-owned repo with signed tags would remove the "bus factor" and the single-account risk.

Files reviewed (all in input.txt): hello.py, test_hello.py, install.ps1, uninstall.ps1, the three workflows, README.md, PLAN.md, docs/WHY-DAILY-ACTIONS.md, .gitattributes, .gitignore, .editorconfig, VERSION.
