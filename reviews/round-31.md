# Round 31

- Date: 2026-10-02
- Commit reviewed: c96f7b5 (version 1.9.3)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1, plus the newest changelog entry as developer's notes
- Redactions: none

---

REVIEW OF hello-world 1.9.3

Scope: I read all 2524 lines of bundle.txt and notes.txt. I ran nothing, so every finding comes from reading the code. Line numbers refer to bundle.txt.

Verdict: I found no Critical or High defects in hello.py. The one defect that matters to employees is a regression from this round that the changelog says is fixed but isn't. The main shipping risk is process, not code. The installer runs as admin on every workstation, and Windows and Python 3.14 are untested. Nothing in CI runs the 60-odd tests on a normal push.

================ PART 1: BUGS AND SECURITY, BY SEVERITY ================

CRITICAL: none found.
HIGH: none found as code defects. See M2 and M3, which I would treat as ship-blockers on process grounds.

---- MEDIUM ----

M1. `--streak on|off` always exits 1, even on success (hello.py lines 1454-1461).
- The notes say it "returns 1 when the choice can't be saved". The code does not do that. `return 1` sits after the if/else at function level, so it runs on both branches. A successful `hello.cmd --streak off` prints "Done." and then exits 1.
- Any management script that checks the exit code reads this as a failure. Run from the shortcut's `cmd /c ... if errorlevel 1 pause`, it adds a stray pause.
- No test catches it. `test_in_a_row_line_appears_at_milestones_only` calls `run(["--streak","off"])` and never looks at `returncode`.
- Fix: put `return 0` at the end of the success branch and `return 1` at the end of the else branch. Add a test asserting both exit codes. The failing case can use `home=` pointing at a file, as `test_unsavable_notes_still_greet` does.
- Related, same cause: `--reset` returns 0 when the user declines, and also when a delete fails (line 1449-1450). `reset()` already returns True or False, so use it. `--remind` returns 0 even when it prints "Could not set up the reminder."

M2. The tests never run in CI for ordinary pushes or pull requests.
- `devkit-quality.yml` runs gitleaks, ruff, jscpd, Vale and osv-scanner, but no pytest or `python test_hello.py`.
- The only job that runs the tests is the Dependabot check job.
- `auto-tag.yml` tags any push to main with a new VERSION whether or not anything passed.
- The tests only ran locally, on Linux with Python 3.11. The shipped runtime is the embedded Windows Python 3.14.8.
- M1 is exactly the kind of regression this would catch.
- Fix:
  - Add a test job on `ubuntu-latest` and `windows-latest` with Python 3.14.
  - Make `auto-tag` depend on it (`needs:`, or trigger it on a successful workflow run).
  - Add PSScriptAnalyzer for the two .ps1 files.

M3. The Windows install, upgrade and uninstall paths are untested, and the pinned Python is unverified.
- PLAN.md and the notes admit it: Windows was tested for 1.7.1 only, and Python 3.14 and the real all-users install were never tested.
- I cannot verify that `python-3.14.8-embed-amd64.zip` exists or that SHA-256 `A93ABE45...` is correct. If the hash is wrong, the installer fails closed at step 4. That is safe but is a day-one failure.
- Also unverified: the claim that `Assert-AdminOnly` passes on `CommonPrograms`, `Program Files` and `ProgramData\Git` on real machines. Several of those ACLs commonly contain Authenticated Users or CREATOR OWNER entries.
- Fix: before the fleet rollout, run PLAN.md's own checklist on one clean VM (install, reinstall, interrupted install, uninstall). Record the hash source, for example the python.org .sigstore value. Do not roll out to five machines first.

M4. Upgrade and uninstall fail whenever a hello-world window is open, and the program makes that common.
- The program blocks on `input()` at the last prompt, and the opt-in sign-in launcher opens a console at logon that sits there until Enter.
- An open window holds `python.exe` and the folder open. `Rename-Retry` in the installer gives up after 5 seconds, and the uninstall's `Remove-Item` gives up after 5 tries.
- The README does say to close the windows. Still, on a fleet this will fail often during working hours.
- Fix, any of:
  - Have the installer find processes whose path is under `$dir\python` and name them in the error.
  - Auto-close the program after about 60 seconds of no input.
  - Install into a versioned folder and switch a pointer, so a running window does not block the swap.

M5. Dependabot auto-merge is risky if it is ever turned on, and is currently inert.
- The workflow squash-merges major updates once the checks pass, with a job holding `contents: write` and `pull-requests: write`.
- Here the only tests are test_hello.py. They do not exercise the workflows at all, so a major bump of an action used by `auto-tag` or `devkit-quality` would merge on a green pytest.
- There is no `.github/dependabot.yml` in the bundle, so version updates for Actions are probably never opened. The workflow is dead code, and the actions stay on stale mutable tags.
- Fix: either add the config and restrict auto-merge to minor and patch updates, or delete the workflow. Pin third-party actions by commit SHA. Require review on workflow-file changes.

---- LOW ----

L1. The README clone step runs Git as admin before Git's folder has been checked.
- `& $git clone ...` runs first. `install.ps1` only verifies that Git's tree is admin-only afterward, at step 1.
- If those ACLs are wrong, attacker-controlled code has already run elevated by then, which defeats the check.
- `$git` in the README is not even checked to be under Program Files.
- Fix: move the Git ACL check into a short bootstrap block in the README that runs before the clone, or ship the check as a one-liner.

L2. CI tool downloads are unverified.
- osv-scanner, gitleaks and vale are fetched with `curl` and extracted with no checksum check. `npx --yes jscpd@...` pulls from npm at run time.
- The token is read-only, so the blast radius is small. Add `sha256sum -c` against pinned hashes.
- I could not verify that the pinned versions (ruff 0.16.9, gitleaks 8.30.1 and others) exist.

L3. Files and configuration are referenced but absent from the bundle.
- The bundle is described as every file. It has no `CHANGELOG.md`, `BACKLOG.md`, `reviews/`, `.devkit/kit/*` or `.gitleaksignore`.
- README, PLAN, the notes and the workflows all point at them.
- If they are really absent, the ruff step runs `ruff check --config .devkit/kit/ruff.toml` against a missing file and fails, and the README links are dead.
- If they are untracked or ignored, say so.

L4. Read-only commands can change files.
- `--stats`, `--remind` and `--streak` call `load()`. If notes.json is damaged, `load()` renames it to `.bak`.
- A notes.json saved as UTF-16 by Notepad ("Unicode") counts as damaged. It is silently set aside and the user sees the first-run welcome again. The .bak survives, so nothing is lost, but nothing explains it.
- `--stats` and `--remind` should not mutate the folder. Print one line when a file was set aside.

L5. Two open windows can overwrite each other's data.
- The menu saves the whole in-memory state. A window left open from sign-in, plus a second window the user opens, will overwrite the other's plan or setting with its own stale copy.
- Fix: re-`load()` before each menu save, or merge.

L6. `save()` has no retry on Windows.
- `os.replace` onto notes.json fails with PermissionError when antivirus or a backup agent holds the file for a moment. The user is told "could not be saved" even though a retry would work.
- Add 2 or 3 retries over about 1 second, as the installer already does for renames.

L7. `remind(True)` can leave a partial launcher.
- If the target path has a non-ASCII character, the `ascii` write raises after the file is created, leaving an empty `hello-world-daily.cmd` behind. The `except` message says it could not be set up, but the file stays.
- Remove the file in the except branch.

L8. Uninstall exit code and cleanup are incomplete.
- With `-Quiet` and no elevation, `uninstall.ps1` starts the elevated child and exits 0 immediately, so a management tool sees success before anything has run. Use `-Wait` and propagate the child's exit code.
- Launcher cleanup only covers profiles listed in ProfileList and the default `AppData\Roaming` path. Profiles with redirected AppData, or not listed, keep a launcher that shows an error at every sign-in.

L9. `tidy()` silently drops characters the running Python's Unicode data does not know yet.
- It keeps only `isprintable()` characters. Emoji or scripts newer than the embedded Python's Unicode tables are unassigned there and get stripped from plans without any message.
- Cosmetic, but unexplained.

L10. A unrecognised answer at "Did you do it?" gets no feedback.
- "yes please", "nah" or "N/A" counts as neither yes nor no. The plan is kept and the user is not told.
- On Enter the program gives no hint either. Say "I did not catch that, keeping your plan."
- Plans older than 14 days are dropped silently (line 1348). That is undocumented in the README.

L11. Test and content gaps.
- `test_thought_and_tip_never_repeat_each_other_on_one_screen` only checks the phrase "glass of water". Other same-day overlaps (the same idea in both lists) are not checked.
- Several thoughts and tips assume a time of day ("this afternoon", "this evening", "Eat lunch away from your desk"). They appear at 8 am on the sign-in launcher and for shift workers.
- Nothing tests the installer or the shortcut quoting.

L12. Minor hygiene.
- On non-Windows, notes.json is created with the default umask (0644). Irrelevant for the Windows target, relevant if anyone runs it on Linux or macOS.
- The README's placeholder commit hash is a syntactically valid 40-hex string, so a careless paste fails only at the commit check.
- `Publisher = 'IT Department'` is generic.

Things I checked that are fine:
- No unsafe handling of the notes file: controls and escapes are stripped, deep JSON is caught, and the size is capped.
- The atomic save, the `.bak` handling, and `reset()` removing all backups and temp files.
- The cmd quoting in the shortcut works despite the nested quotes.
- The `hello.cmd` exit-code propagation and the commit and hash checks in the installer.
- `needs: check` correctly skips the merge job for non-Dependabot PRs.
- The TIPS and THOUGHTS lists are 100 each, matching the docs.

================ PART 2: MAKING IT MORE VALUABLE ================

1. Decide who this is for and what it is for, and test that before deploying.
- The docs say it is for "the most generic possible person", and the decision record says the value was "in the deployment machinery, not the program". As written, the payload is a generic wellness quote plus a one-line to-do. Employees already have sticky notes, a task app and a thousand wellness tips.
- Nobody inside the documents asked for it. Right now it is a very hardened way to deliver a thing no one requested.
- What to do:
  - Pilot with the five employees for two weeks.
  - Before starting, write the pass/fail rule (for example "3 of 5 still open it in week 3").
  - Be ready to stop.
- Why it matters: it avoids installing admin-grade software on a fleet for something nobody opens twice.

2. If you want it to earn its place, give it something only IT can give.
- The one thing that fits this deployment is a short IT section in the same screen: a security tip of the day, a known outage, "restart your PC, it has been up 14 days" or "your password expires in 5 days", the day's company holidays.
- That can be done without breaking the no-network, no-reporting promise. IT pushes a small local content file with the install or an update, and the program only reads it. Make it visible in the "what is saved" menu, and label IT messages as from IT.
- Why it matters: this is the only content that would make an employee open it for a reason other than habit, and it gives IT a channel.

3. Make the content editable and extendable.
- Today all 200 items are in hello.py, English only, so changing a line means a new release and a reinstall.
- Move them to a plain text or JSON file next to hello.py, with an optional per-user file so employees can add their own tips and thoughts. This also makes the "second language file" in PLAN.md a data change.
- Why it matters: the main reason people stop opening a daily tip is repetition.

4. Fix the repetition.
- The thought and tip are locked together by a constant offset of 37, so the same pair returns exactly every 100 days.
- Use a longer list, or index the two lists with different strides so the pairs shift. Skip weekends if the reminder is on a workday basis. Let the user press a key for "another one".
- Add morning and afternoon variants, or write the items to be time-neutral.
- Why it matters: after the second cycle people stop reading it.

5. Make the plan feature quicker, since it is the only personal-value feature.
- Support `hello.cmd --plan "text"` and a Start menu shortcut to it for quick capture without the whole screen.
- Accept more answers, in more languages, at "Did you do it?", and confirm what was understood.
- Document the 14-day expiry.
- Why it matters: a plan that takes under 5 seconds to enter is used more often than one that needs a whole screen.

6. Stop it blocking.
- Close the window by itself after about 60 seconds of no input, and never leave a sign-in window sitting open all day. This also fixes M4.
- Why it matters: a window that hangs around and blocks updates becomes a thing employees and IT resent.

7. Define how success is measured.
- PLAN.md says retention is measured by asking five people. Write the questions and the date. For example: ask at week 2 and week 6 whether they still open it and what they would change.
- Add one measurable rollout number, such as installs completed without error out of the machines targeted.
- Why it matters: without this, "better" is only an opinion.

8. Simplify delivery.
- The installer is hundreds of lines of ACL checks, a git clone and a hash-pinned Python for a text screen.
- If you keep the product, consider packaging as an MSI/MSIX or a standard Intune or SCCM Win32 app, signed, with the Python build tested in CI on Windows. That removes the manual clone-and-paste install and the several-minute permission walk.
- Keep the pinned-hash approach, and add a documented path for taking Python security updates, because the embedded 3.14.8 never updates itself.
- Why it matters: IT can maintain it, and employees get updates that do not depend on closing windows.

9. Decide about other platforms.
- The data-path code already handles Linux and macOS, but there is no installer, no README section and no test for them. Either say "Windows only" in the README or support them.
- Why it matters: any mixed-OS user will otherwise conclude it is broken.
