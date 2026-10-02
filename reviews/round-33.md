# Round 33

- Date: 2026-10-02
- Commit reviewed: b0661c5 (version 1.9.5)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1
- Redactions: none

# Review of hello-world 1.9.5

I read the whole input file (2,605 lines). I ran nothing, so none of this was executed. I did not check the pinned Python 3.14.8 URL and SHA-256, the pinned tool versions, or the files you say are committed but not shown (`CHANGELOG.md`, `BACKLOG.md`, `reviews/`, `.devkit/kit/*`). I took your word on those.

## Verdict on this change

The two fixes are correct as written.
- **M2 (`--reset`):** `reset()` returns True, False or None. `--reset` exits 1 only on False, and a decline exits 0. The failed-delete test works because `os.remove` on a directory raises `OSError` on Linux and Windows.
- **M3 (read-only commands):** `load(repair=False)` leaves a damaged file in place. `--stats` reports it and exits 1. An unknown option no longer reads the file. `--streak` still repairs the file, which is fine because it writes anyway.

I found no Critical or High defects in the program code or the installers. The 1.9.5 changes introduce no new bugs. The Medium items below are process, robustness and supportability issues. Items 1 and 2 are repeats of things you already declined or accepted.

## Part 1: Findings, most severe first

**Medium 1. The tests never run on push or PR, or on the platform that ships.**
- `devkit-quality.yml` runs no tests.
- `dependabot-automerge.yml` runs pytest only on Dependabot PRs, on Python 3.12 and Linux.
- Production is Windows with embedded Python 3.14.8.
- The suite needs Python 3.11 or later (`fromisoformat("20261001")`), and the Windows-only code is untested: `interactive()`'s ctypes path, the `.cmd` launcher, and `msvcrt`.
- This is the H1/H2 repeat you declined. I still rate it Medium because it is the largest uncovered risk.
- Fix:
  - Add a `test` job on `push` and `pull_request` with a matrix of `ubuntu-latest` and `windows-latest`, on Python 3.12 and 3.14.
  - If you keep declining, put "not tested on Windows or 3.14" in the release notes.

**Medium 2. Dependabot auto-merge is gated by tests that cannot exercise the change.**
- The only manifests are GitHub Actions workflows. A major bump of an action (for example `actions/checkout` in `auto-tag.yml`, which has `contents: write`) merges as soon as `test_hello.py` passes.
- The `check` job only exercises the actions it uses itself.
- All actions are pinned to tags, not commit SHAs.
- I did not see a `dependabot.yml`. If there isn't one, this workflow does nothing.
- Fix:
  - Pin actions to SHAs.
  - Drop auto-merge for major updates, or restrict it to `package-ecosystem` values that tests can cover.
  - Delete the workflow if no manifests exist.

**Medium 3. A zero-length or damaged `notes.json` quietly turns into a first-run screen.**
- `save()` does not flush or `fsync` before `os.replace`. A crash or power loss can leave an empty or truncated file.
- On the next run `load()` moves it to `.bak` and shows "Welcome." and the first-run text. Nothing says the history was set aside.
- The same happens at a slow sign-in, when `load()` returns `can_save=False` for a locked file. That shows the first-run welcome, plus "could not be saved".
- Fix:
  - Call `f.flush()` and `os.fsync(f.fileno())` before replacing.
  - When `load()` moves a file aside, print one line, such as "Your saved file was damaged. A copy is in notes.json.bak."
  - Don't show the first-run welcome when the file exists but could not be read.

**Medium 4. Failures can't be diagnosed.**
- `main()` prints only "something went wrong (ValueError). Contact IT." There is no traceback or log.
- The install log covers the installer only.
- Fix: write the traceback to a small `error.log` in the user's data folder. Print its path, and add it to the `--reset` cleanup list.

**Low 5. `reset()` is incomplete.**
- It stops at the first failed delete and never tries the `.bak` and `.tmp` copies, which may hold plan text.
- It ignores an `os.listdir` error, then prints "Everything saved was deleted."
- `--reset` also calls `load(repair=False)` and never uses the result.
- Fix:
  - Try every file, collect the failures, and list them all.
  - Report False if the listing failed.
  - Drop the unused `load`.

**Low 6. `remind()` and the launcher.**
- A failed rewrite deletes an existing working launcher.
- The launcher path uses `%APPDATA%` rather than the Known Folder, and `uninstall.ps1` hardcodes `AppData\Roaming\...`. Folder redirection would leave a launcher behind.
- `start` opens a console at every sign-in. It flashes shut if you already opened the program that day, for example after a second sign-in.
- Fix:
  - Write the new launcher to a temporary file and then replace the old one.
  - Resolve the Startup folder through the Known Folder API.

**Low 7. Ctrl-C is swallowed at prompts.**
- `ask()` treats `KeyboardInterrupt` as no answer. The run continues and the visit is saved.
- Someone pressing Ctrl-C to quit gets saved data.
- Fix: let it propagate. `main()` already returns 1.

**Low 8. `uninstall.ps1` always exits 0 when it has to elevate.**
- The non-elevated copy calls `Start-Process -Verb RunAs` without `-Wait` and then runs `exit`. Under `-Quiet` the caller never sees the child's result.
- Fix: use `-Wait -PassThru` and exit with the child's exit code.

**Low 9. Content and wording.**
- Thought 960 says "An ordinary Tuesday" and shows on any weekday.
- "nine o'clock" assumes a day job, while PLAN.md says nothing assumes a work pattern.
- "biscuits" sits next to "favorite" and "apologizing" (UK and US spelling mixed).
- Truncating at 120 characters can split a combining sequence.

**Low 10. Docs.**
- The `hello.py` docstring lists exit codes 0, 1 and 2, but 1 now also means a failed reset, an unreadable `--stats`, and a failed `--remind` or `--streak`.
- The README update steps use `$d` without saying it must be the same window as the install. In a new window it is empty and the command errors harmlessly.

**Low 11. `devkit-quality.yml` downloads binaries with no checksum.** The `curl | tar` installs of osv-scanner, gitleaks and vale check nothing. Verify the release checksums, or install from a package manager.

**Low 12. Two instances can overwrite each other.** The startup launcher and a manual open can both read, change and write `notes.json`, and the last writer wins. Impact is small.

## Part 2: What would make it more valuable

1. **Ask the five employees whether they want it before building more.** The design record says this itself. The installer, with its pinned Python, admin-only trees and rollback, took about 25 review rounds. The product is a daily tip. Decide what success is, such as "3 of 5 still open it after a month", and measure it.
2. **Let IT or the company add content.** Right now it is 200 fixed lines that repeat every 100 days. A plain text file, read locally and editable by IT, would let it carry holiday notices, office news, or a "this week" note. That is the one thing that would make it worth opening. Keep it opt-in and local so the no-network promise holds.
3. **Make the deployment much lighter.** It requires Git for Windows installed for all users, an ACL scan that takes minutes, and a bundled interpreter. For one small script, a single signed file, or an MSIX or winget package, with the same pinned hash, would be easier to install and update. Pinned Python never updates itself, so add a calendar reminder to bump it.
4. **Run the tests on Windows on every push** (see Medium 1). It protects the five-person rollout more than any further review round.
5. **Make the plan useful beyond one line.** Allow up to 3 items for the day, with an "all done" shortcut. Keep the rule that nothing records whether plans were done.
6. **Support troubleshooting.** Add `--version` and a `--doctor` check that prints the data path, whether it is writable, and whether the launcher exists. This pairs with Medium 4.
7. **Tell people when something was set aside.** After a damaged-file repair, show a plain line saying so, so they don't think their history vanished (see Medium 3).
8. **Add `--reset --purge` to the uninstaller, plus a per-user cleanup.** Uninstall leaves each user's notes behind. Offer to delete them for the current user when uninstalling.
9. **Test with real assistive technology and a non-English locale.** The accessibility claims are untested, and the dates and content are English only. Do this before expanding past five people.
10. **Say clearly what it is for.** The README's "small daily moment" is clear enough. Put the one-sentence version first and drop the "Hello, world!" framing from the install docs.
