# Round 35

- Date: 2026-10-02
- Commit reviewed: 1b83ee1 (version 1.9.7)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1 (all given to every reviewer, plus the newest changelog entry)
- Agents run: lead, security, usability and retention, accessibility
- Redactions: none needed

## Lead reviewer

# Review of hello-world 1.9.7 (hello.py, installer, CI, tests, docs)

Scope: I read only the packet, which was 2621 lines. I ran nothing and did not look at the repository. BACKLOG.md, CHANGELOG.md, `reviews/`, `.devkit/` and the generated `hello.cmd` are not in the packet, so I could not check them. I also could not verify the pinned Python 3.14.8 URL or its SHA-256. The installer fails safely at step 4 if the hash is wrong, but check it once before shipping.

**Verdict:** There are no Critical findings and no data-destroying bugs. The hardening in `hello.py` and the installer is real. The weak spots are retention, a few accessibility gaps that the program's own screen rules should have caught, and a release process that never runs the tests. The one finding in the code changed this round is a small bug (finding 8): the damaged-file notice can name the wrong file.

## Part 1: Findings, most severe first

### 1. High, retention: nothing tells employees the program exists, and nothing brings them back
- **Employee page:** The "For employees" page is in a README inside a repo employees will never open. The installer only adds a Start menu entry named "hello-world", which is meaningless to someone who has not been told about it.
- **Return mechanism:** The only way back is the person remembering to open it. The one mechanism that helps, the sign-in launcher, is menu option 2. It is never mentioned on the first-run screen, which only says "Type m ... to see the options".
- **Outcome:** A person who reads the screen once has no prompt to return. This is the "succeed once and never come back" failure. The plan feature is also never introduced, so the next-day follow-up arrives as a surprise.
- **Fix:**
  - Ship an `EMPLOYEES.txt` or an announcement email text for IT to send.
  - Add one line to the first-run screen: "Tomorrow it will ask how today's plan went."
  - On the 2nd or 3rd visit, ask once: "Open this once a day when you sign in? (y/n)". It stays opt-in, so it still honours "never on by default".
  - Remember a "no" so it is not asked again.

### 2. Medium, retention and ease of use: a plan can never be finished or cleared on the same day, and a stale plan nags for up to 14 days
- **No way to finish a plan:** At 3pm, after doing the thing, the person sees "Your plan for today: X" and has no way to mark it done or remove it. Menu option 6 says "Enter keeps it". A typed space becomes empty and gives "Nothing changed". The only exits are tomorrow's question or option 4, which deletes everything.
- **Stale plan keeps asking:** If the person presses Enter at "Did you do it?" and then Enter at the new-plan prompt, the old plan keeps its old date. Every later first visit of the day asks "Last time you planned: X" again, for 14 days. This is the guilt-by-repetition pattern the docs promise to avoid.
- **Silent expiry:** After 14 days the plan is silently dropped and the drop is saved.
- **Fix:**
  - Let `p` or menu 6 accept `d` (done) or `x` (clear).
  - Ask about a given old plan at most twice.
  - Say "I set that plan aside" when it expires.

### 3. Medium, accessibility: the screen rules are broken in HELP, and wrapping ignores the real window width
- **HELP overflows:** The first HELP line, "At the end of the screen, type p for today's plan or m for options. You can also run hello.cmd", is about 94 columns. The 72-column test only checks the daily screen, not HELP (menu option 5, `--help`, unknown option).
- **Fixed wrap width:** Everything is wrapped at a fixed 72 or 68 columns. A low-vision user who enlarges the console font has fewer columns than that, so lines wrap twice and the text breaks mid-sentence.
- **Fix:**
  - Add a helper that uses `min(72, shutil.get_terminal_size().columns - 2)`.
  - Rewrite HELP in short lines.
  - Add a test that checks HELP and the menu at 72 columns.

### 4. Medium, ease of use and accessibility: "Show what is saved" can print about 400 lines
- **Cause:** `show_saved()` prints `json.dumps(..., indent=2)`, which puts one date per line. After months of use that is up to about 400 lines.
- **Effect:** The useful summary scrolls off the top, a screen reader reads every date, and the menu then redraws underneath. This is the trust feature of the product, and it is the worst-behaved screen.
- **Fix:** Print the dates compactly, such as "Last 14 days: ..." with a count of the rest, and the plan in plain words. Offer the full list only on request.

### 5. Medium, bug and process: nothing runs the tests before release
- **No gate on release:** No workflow runs `test_hello.py` on push or pull request. `auto-tag.yml` tags `main` whenever VERSION changes, with no test gate. The product is Windows-only, yet it has never been run on Windows since 1.7.1, and CI runs on `ubuntu-latest` only.
- **Dependabot gate is weak:**
  - It auto-merges major updates, including updates to the Actions that have `contents: write`. The only gate is pytest, which does not exercise workflows or the installer.
  - You said pytest is not installed locally, so the suite has never been run the way the merge gate runs it.
- **Declined findings 1, 2, 3 and 13:** They were declined as "CI and Windows work I can't run here". Adding a test workflow does not require running it locally.
- **Fix:**
  - Add a `windows-latest` and `ubuntu-latest` test job on push and pull request.
  - Make auto-tag depend on it.
  - Exclude the `github-actions` ecosystem and major bumps from auto-merge, or require review for them.

### 6. Medium, test gap: your note that the content count test is "already covered by existing content tests" is not accurate
- **What the tests do cover:** The only content tests are the day-1 ASCII and width check and the "glass of water" overlap check.
- **What nothing enforces:**
  - `len(TIPS) == len(THOUGHTS) == 100`, which the "repeat every 100 days" claim depends on.
  - ASCII for all 200 entries and the 72-column limit.
  - "No exclamation marks" for every entry.
- **Risk:** A contributor who adds entry 101, or a curly quote, breaks a documented promise without a failing test.
- **Fix:** Add a loop over every entry and every day of the cycle, which is cheap and in-process.

### 7. Low, bug (the code changed this round): the damaged-file notice hard-codes `notes.json.bak`
- **Bug:** `backup_name()` returns `.bak2`, `.bak3` and so on when a backup already exists. The notice, and the test, always say `notes.json.bak`. On a second damage the user is pointed at the wrong, older file, which holds old data.
- **Fix:** Use `os.path.basename(name)` from the actual backup name in the message, and add a test for the second case.
- **Related, not fixed:** The notice still prints above "Hello, world!". If the damage is found on a run with no person at the keyboard, such as a launcher with no console, the file is moved and the notice is lost. Nobody ever learns about the backup.

### 8. Low to Medium, ease of use: Ctrl+C and Ctrl+Z mean "skip"
- **Behaviour:** `ask()` turns KeyboardInterrupt and EOF into "no answer". Ctrl+C at the first prompt does not quit. It continues to the next prompt, then records the visit and saves.
- **Impact:** A keyboard user who wants out has to press it up to four times, and the visit is counted anyway.
- **Fix:** Treat Ctrl+C as "stop now". Print "Closed. Nothing more was saved." and exit without recording the visit.
- **Note:** You declined this as weighed in earlier rounds, so it is a judgement call. I would still do it.

### 9. Low, ease of use: an unreadable or unsavable notes file produces a confusing loop
- **Behaviour:** When `load()` returns `can_save=False`, for example a locked file, a read-only profile, or a VDI or roaming profile that does not persist, `visits` is empty. So every run shows the "Welcome" text and the plan question again, then ends with "Your notes could not be saved on this computer. This screen still works."
- **Problem:** The message has no cause, no path and no "ask IT". The plan was already typed, so the work is lost.
- **Fix:** Name the folder and say who to ask. Use a different first-run text when saving is known to be impossible.

### 10. Low, bug: `reset()` and the menu keep stale state
- **Stale `can_save`:** After a successful menu option 4, `can_save` stays whatever it was. If the file had been unreadable and was just deleted, options 3 and 6 still say "Could not save" until restart.
- **Partial failure:** On a partial failure, `state` is not cleared although `notes.json` may already be gone.
- **Listing failure:** In the folder-listing failure branch (finding 8 of the last round), the output says "Could not delete everything" without saying what was deleted. That branch also has no test.
- **Launcher left behind:** "Delete everything" leaves the sign-in launcher. That is arguably correct, but it should say so.
- **Fix:** Re-run `load()` after a successful reset, and add a listing-failure test.

### 11. Low, ease of use: unrecognised answers get no feedback
- **Behaviour:** At "Did you do it?", "yes please", "yup" or "no thanks" is neither yes nor no. It is treated as skip, the plan stays, and nothing is said.
- **Related:** The same happens at "Keep it for today?".
- **Fix:** Reply "I did not catch that, so I kept the plan as it is." Accept `yup` and `nah`.

### 12. Low, retention and bug: the content cycle repeats exactly
- **Behaviour:** Both lists are 100 long and the pairing offset is fixed at 37. The same thought and tip pair recurs on every 100th day, forever. A daily user sees an exact repeat from about day 101. Everyone sees the same line on the same day, which is by design.
- **Time-of-day mismatches:** Some entries clash with when they are shown: "Choose one word for how you want the afternoon to feel" at 8am, "Leave on time tonight", and "Take the long way to your next meeting" on a weekend sign-in.
- **Fix:** See Part 2, item 1.

### 13. Low, bug: option 1 describes a reconstruction, not the file
- **Behaviour:** `show_saved()` prints "After tidying, the file holds only this", built from in-memory state.
- **When it is wrong:** If the save failed, the file is locked, or `--stats` ran without rewriting the file, the screen shows content that is not in the file.
- **Fix:** Say "This is what would be saved." when the file was not just written.

### 14. Low, accessibility and ease of use: the CLI is unreachable by ordinary employees
- **Problem:** `hello.cmd --stats`, `--reset` and `--remind` live in `Program Files\hello-world`, which is not on PATH. The employee page never gives the path.
- **Menu cover:** The menu covers the same functions, so this is minor.
- **Fix:** Make HELP and the README say "use the menu, or ask IT for the command-line options".

### 15. Low, security: supply chain and uninstall
- **Unverified downloads:** `devkit-quality.yml` downloads osv-scanner, gitleaks and vale binaries with no checksum, and the actions are pinned by tag, not SHA. The token is read-only, so the exposure is small. `auto-tag` has `contents: write`.
- **Where the commit hash comes from:** The installer protects against a moved tag by pinning the commit hash, but nothing says where the admin gets that hash. If it comes only from the same repo page, the pin adds less than it looks like.
- **Uninstall deletes through user paths:** `uninstall.ps1` runs elevated and deletes `...\Startup\hello-world-daily.cmd` under each profile with no reparse-point check. A standard user can make `Startup` a junction. Only that one filename can be removed, so the impact is small, and I did not verify the Windows PowerShell 5.1 behaviour. The installer's own rule is "never delete through a link", so apply it here too.
- **Retry path:** The comment says the Apps entry is the way to retry. If a failure happens after the folder (including `uninstall.ps1`) is deleted, the Apps entry points at a missing script.

### 16. Low, documentation
- **README update step:** It uses `$d` without saying that a new window needs the path typed in. `install.ps1`'s help says this, but the README does not.
- **Where the hash comes from:** See item 15.
- **Test count:** The "tested on Linux, Python 3.11" statement is honest, but the shipped Python is 3.14. The 3.14 `datetime` and console behaviour is untested.

## Part 2: Improvements, most important first

1. **Retention: fresher content, with a path for IT to add to it.**
   - Make the two lists coprime lengths, for example 101 thoughts and 100 tips. The pairing then changes for about 10,000 days instead of repeating every 100.
   - Add an optional `extra.txt` in the admin-only install folder, which IT or a team lead can edit to add local lines: a team tip, a holiday, a policy reminder. Keep it ASCII-checked at load.
   - This gives a returning user a reason to look, because the screen can change in ways they did not predict. It needs no network, no tracking and no code change.

2. **Retention: introduce the follow-up and the launcher at the right moments.**
   - Put one line about the next-day question on the first-run screen.
   - On the third visit, ask once about opening at sign-in, and remember "no".
   - Today a person can use the program for a month without discovering either feature.

3. **Plan feature: let it finish.**
   - Add `d` for done and `x` for clear at the end prompt.
   - Cap the repeats of "Did you do it?" at two.
   - Say aloud when a plan is set aside.
   - It is the only feature with personal value, and right now it cannot be completed except by waiting a day.

4. **Accessibility: wrap to the real console width, and shorten the long screens.**
   - Use a width-aware wrap helper.
   - Rewrite HELP.
   - Compact `show_saved`.
   - Add tests at 40 and 72 columns.
   - People with magnified or narrow consoles, and screen reader users, are the ones who hit this.

5. **Accessibility: handle quitting and "stuck" states in plain words.**
   - Ctrl+C should stop the program.
   - A "could not understand" reply should say so.
   - Every error should say what happened, what was kept, and who to ask. A person using only the keyboard or a screen reader cannot see context that a sighted user might infer.

6. **Ease of use: ship the employee-facing announcement.** A short `EMPLOYEES.txt` that IT can paste into an email: what it is, where to find it ("hello-world" in Start, with a screenshot), what is saved, how to remove it. Also add a Start menu entry named for what it does, such as "hello-world: daily thought", so it can be found by searching "daily" or "thought".

7. **Resilience: do not lose history.**
   - Keep a rolling `notes.json.prev` of the last good file.
   - Add `os.fsync` before `os.replace`.
   - Retry the replace once on `PermissionError`. A power cut or an antivirus lock can currently turn a good file into "damaged, started fresh".

8. **Process: a test workflow on Windows and Linux, and a release that waits for it.** See finding 5. A Windows-only product that has been tested on Windows once is the main shipping risk.

9. **Product direction.**
   - **What it is for:** A low-pressure daily moment for employees, installed by IT. That is clear enough. The unresolved question is who it serves. IT installs it for all users, uninstall needs an administrator password, and the publisher is "IT Department". Employees did not ask for it, and "it only works if they choose to open it" is in tension with that.
   - **Cost mismatch:** About 25 review rounds went into the installer, but the part employees touch is a 2-minute console screen with static text.
   - **Decide before wider rollout:** Run the five-employee pilot with a stated success measure, for example "three of five still open it in week four". If it fails, stop rather than polishing. If it succeeds, consider a per-user self-install so people can choose it and remove it without an administrator.
   - **Name:** "hello-world" tells employees nothing, so rename the Start entry.

Nothing in this review is a reason to hold the 1.9.7 release for security. I would fix finding 7 (a one-line change), add the content test (finding 6) and decide on findings 1 to 3 before calling this ready for employees.

## Security agent

# Security review: hello-world 1.9.7

Scope: the packet only (hello.py, install.ps1, uninstall.ps1, the three workflows, README, docs, tests). The packet did not include `.devkit/kit/*`, `hello.cmd` (generated by the installer), CHANGELOG, BACKLOG or `reviews/`. I did not run anything.

**Verdict: no Critical or High findings. Two Medium, six Low.** The 1.9.7 change itself (the wrapped damaged-file notice and the `reset()` listing-failure message) is clean. Both print static text plus `data_dir()`, and nothing from the notes file reaches the screen unsanitised.

## What I checked and why it is clean

- **Injection (CWE-78, 77, 89):** hello.py has no `subprocess`, `eval` or `os.system`, and no SQL. The only file-derived text that reaches the screen is the plan text, which `tidy()` strips. It drops all Cc and Cf characters, including ESC and bidi overrides such as U+202E, and keeps only ZWJ and ZWNJ. The `visits` entries are re-canonicalised through `date.fromisoformat`, and `streak` is a boolean. The tests cover a hostile notes file.
- **Deserialization (CWE-502):** JSON only, no pickle. Read size is capped at 1 MB. Deep nesting raises `RecursionError`, which is caught. Huge integers raise `ValueError` (the 4300-digit limit), which is also caught.
- **Path traversal (CWE-22):** every path is a fixed filename joined to `data_dir()`. `reset()` deletes only names matching `notes.json.*.tmp` or `notes.json.bak*` from `os.listdir`, so no user-supplied path segments are involved.
- **Environment and config override (CWE-15):**
  - The test hooks (`TODAY`, `HOME`, `STARTUP_DIR`, `FORCE_INTERACTIVE`) are module globals, and no `HELLO_*` environment variables are read. A test covers this.
  - The installed launcher runs `python.exe -I`, which ignores PYTHON* variables, the user site directory, and the script directory and cwd on `sys.path`.
- **Network, SSRF, CSRF, XSS, authn and session:** there is no web surface and no listener. hello.py makes no network calls. The only fetches are the installer's fixed python.org URL and the fixed GitHub clone URL.
- **Secrets (CWE-798):** none in the code. The README commit hash is an obvious placeholder, and gitleaks runs in CI over full history.
- **Installer privilege boundary:** this part is carefully done.
  - It runs only from an admin-only tree. It rejects reparse points, checks parent folders, and checks the ACLs on Git and `ProgramData\Git`.
  - It clears the `GIT_*`, `HOME` and `XDG_CONFIG_HOME` variables, and it runs git and icacls by full path.
  - It pins a 40-hex commit and hash-compares the four files it installs. It pins the Python zip by SHA-256, tests a candidate build, and swaps with rollback.
  - The shortcut ACL is verified, and the uninstall string points into an admin-only directory.
  - The one admin-run execution of hello.py is `--plain`, which reads no user data.
  - Employees can only affect their own per-user data, so there is no standard-user-to-admin path that I can see.

## Findings

### 1. Medium: Dependabot auto-merge of major updates gated only by "tests exist and pass" (CWE-1357, 829; T1195.001; NIST SA-12, SI-7)
`dependabot-automerge.yml` squash-merges any Dependabot PR, majors included, with no human review.
- This repo has no `package.json` or requirements file. If Dependabot is configured for `github-actions`, an update to `actions/*` is merged as soon as `pytest` passes. `pytest` exercises none of the workflows.
- A compromised or retagged action release would reach `main`. `auto-tag.yml` then runs it with `contents: write`.
- The check job also runs `npm ci` and `pip install` without `--ignore-scripts`, so install scripts execute in CI. Its token is read-only and the job has no secrets, so this is bounded.
- Merging with `GITHUB_TOKEN` does not trigger later workflows. The tag therefore only appears on the next human push, which is a minor surprise rather than a hazard.

**Fix:**
- Auto-merge only patch and minor updates. Use `dependabot/fetch-metadata` and gate on `update-type`.
- Never auto-merge `github-actions` or build-tooling ecosystems.
- Require branch protection with at least one review.
- Pin every action to a full commit SHA, which also covers finding 2.
- Add `--ignore-scripts` to `npm ci`.

### 2. Medium: Unverified binaries and floating action tags in CI (CWE-494, 829; NIST SI-7, SA-12)
- `devkit-quality.yml` downloads osv-scanner, gitleaks and vale with `curl` from GitHub releases. The versions are pinned, but no checksum or signature is verified. The tarballs are piped straight into `tar`.
- `actions/checkout@v5`, `setup-node@v5` and `setup-python@v6` are tag-pinned only.
- `npx --yes jscpd@5.3.2` pins the top-level package but pulls transitive dependencies unpinned.
- The impact is capped because the workflow runs with `contents: read`. A compromised scanner could still hide findings, for example by passing a secrets scan.

**Fix:** verify SHA-256 against the release `checksums.txt` or a hash committed to the repo. Use SHA-pinned actions. Use a lockfile or a vendored jscpd.

### 3. Low: Python embed runtime has no patch path (CWE-1104; NIST SI-2)
The pinned `python-3.14.8-embed` is the only third-party code on the workstation. Updating it means editing `install.ps1` by hand and cutting a new release. The program parses only the user's own file, so exposure is small.
- **Fix:** add a documented quarterly bump. Verify the pinned SHA against python.org's signed checksum out of band, because I cannot confirm it from here.

### 4. Low: Notes file is world-readable on POSIX (CWE-276, 732)
`os.makedirs(...)` and `open(tmp, "w")` use the default umask, which typically gives 0755 on the folder and 0644 on `notes.json`. On a shared Linux or macOS host, other users can read the plans. Windows `AppData\Local` is per-user, so this does not apply to the stated deployment. The temporary filename is predictable (`notes.json.<pid>.tmp`) and opened without `O_EXCL` or `O_NOFOLLOW`.
- **Fix:** `os.makedirs(..., mode=0o700)` and `os.open(tmp, O_WRONLY|O_CREAT|O_EXCL, 0o600)` when `os.name != "nt"`.

### 5. Low: Cross-profile launcher removal follows junctions (CWE-59; T1547.001)
`uninstall.ps1`, running elevated, runs `Remove-Item -LiteralPath <profile>\...\Startup\hello-world-daily.cmd` for every profile. A standard user can turn their own `Startup` folder into a junction without admin rights. The impact is limited to deleting one file with that exact name elsewhere, such as another user's launcher. That is negligible.
- **Fix:** skip the path if any component is a reparse point.

The Startup-folder launcher is itself the MITRE T1547.001 persistence technique. It is opt-in, user-level, and runs a fixed admin-owned target, but EDR may flag it. The `--remind on` code path is also not guarded against being run from a user-writable folder. In that case `hello.cmd` in that folder would be what runs at every sign-in.
- **Fix:** have `remind()` refuse unless the target sits under Program Files.

### 6. Low: `hello.cmd` passes `%*` through cmd unquoted
Arguments containing `& | >` are interpreted by cmd. Today only the user, the fixed `--startup` launcher and the fixed shortcut supply arguments, so no boundary is crossed. It would become command injection if anything ever passed untrusted arguments, such as a URL or file association.
- **Fix:** document that no handler may be registered, or run Python with `--` and validate arguments in Python.

### 7. Low: Unsanitised `.bak` files and best-effort deletion (CWE-212, 459)
- Damaged files are kept raw as `notes.json.bak*`. The count is unbounded and each copy is up to 1 MB, but they never go to the screen, so there is no escape-code risk.
- Delete is plain `os.remove`, not a secure wipe. The README states that IT can read the files, so this is acceptable. Do not claim stronger privacy than that.

### 8. Low: Install steps outside the installer's hardening
- The README clone step runs in the admin's own session before `install.ps1` clears `GIT_*`, `HOME` and `XDG_CONFIG_HOME`, so a poisoned session environment affects the clone only.
- The commit pin is SHA-1. GitHub applies collision detection, so this is theoretical. Consider `git verify-commit` or signed tags.
- The destructive update line `Remove-Item -Recurse -Force $d` trusts `$d`, which is set in a different earlier window.

## Not applicable
SSRF, CSRF, XSS, authn and authz, and SQL injection have no attack surface here, because the program is local-only with no server.

## Usability and retention agent

# Product review: ease of use and retention, hello-world 1.9.7

Read only the packet. I did not run anything.

## Verdict

The daily screen is a good, restrained product. It opens fast, uses plain words, never shames anyone, and is honest about what it saves. The 1.9.7 changes (a wrapped damaged-file notice, a better `--reset` message, README wording) are correct but touch almost nothing a person sees. After 34 review rounds, the weakest part is not the code. Nobody has tested whether anyone returns. The product still has one real hook, the plan and next-day follow-up, and it hides that hook from the person it is supposed to retain.

**Who is this for?** It is unclear. The docs say "the most generic possible person, any age, any role". The delivery says five employees whose IT team installed it. Those are different products. A generic person has no reason to open a window called "hello-world". A coworker told by IT to try it might open it once out of politeness. Nothing says who asked for it or what job it does for them. Until that is answered, retention can't be judged. My read is that the real user is an employee at a desk who wants a calm start to the day and a place to park one intention.

No Critical findings. The retention risks below are why this should not be called done.

## Findings

### 1. The hook is never explained at first run
**Severity: High. Retention.**
- The first screen is a welcome paragraph that is mostly privacy language: passwords, IT staff, "sends nothing anywhere".
- It then asks for a plan. It never says tomorrow it will ask whether you did it. That follow-up is the only reason to come back.
- After a plan is typed, nothing confirms it was saved. The "Done. Your plan for today is saved." message only appears through `p` or menu option 6.
- The first session ends with a prompt about `p` and `m`, not a promise about tomorrow.

**Fix:**
- Lead the welcome with the benefit. Draft: "Each day: one thought, one small thing to try, and one thing you plan to do. Tomorrow I will ask how it went."
- Move the privacy detail to one short line, or behind `m`.
- After a first plan is saved, print "Saved. See you tomorrow, I will ask about this."

### 2. Nothing the person made accumulates
**Severity: High. Retention.**
- Plans are deleted after a yes. Past plans are not kept, by design.
- The thought and the tip are the same for every employee and repeat every 100 days.
- After a week, nothing in the product belongs to the person. A new session is no more valuable than the first, so there is no compounding value to lose by leaving.
- The "no record of done" rule protects against surveillance feeling. It does not require throwing away the person's own words.

**Fix:** See "The retention feature to build this round" below.

### 3. The sign-in reminder is the retention lever and is buried
**Severity: High. Retention.**
- `--remind` and menu option 2 are the only things that make a person see it on a second day without remembering to.
- Nothing tells a new person it exists. It is option 2 of a menu reached by typing `m` at the last prompt.
- Most people press Enter to close and never see the menu.

**Fix:**
- On the 2nd or 3rd visit, once, ask "Open this once a day when you sign in? (y/n)" and remember the answer.
- Show the answer only in the menu after that.
- It stays opt-in, so the "nothing starts by itself" principle holds.
- Add one test for "asked once, never again".

### 4. The name and the shortcut give nobody a reason to look for it
**Severity: Medium. Retention.**
- "hello-world" is a developer's name. Windows Search needs the person to remember it.
- Employees never get an announcement or a reason to open it from the install steps.
- The README's "For employees" section is the only communication.

**Fix:**
- Name the Start menu entry for what it does, for example "Daily moment". Keep `hello.cmd` for IT.
- Give IT a two-sentence note to send, with the point of the program in the first sentence.

### 5. A second session is not faster than the first
**Severity: Medium. Ease of use and retention.**
- Day 2 and day 30 follow the same path: read, answer "Did you do it?", re-ask for a plan, Enter.
- It is already fast at two Enters, but there is no memory that rewards repeat use.
- A person who repeats a plan every day, such as "inbox to zero", retypes it each time.

**Fix:**
- Offer "same as last time (s)" at the plan prompt.
- Skip the privacy explanation entirely after visit 1.

### 6. The plan cannot be cleared or fixed, only replaced
**Severity: Medium. Ease of use.**
- In `set_plan`, empty input means "Nothing changed". There is no way to remove today's plan except "Delete everything".
- A mistyped or abandoned plan then comes back tomorrow as "Last time you planned...".
- `p` replaces the plan, which is fine, but there is no hint that a different word clears it.

**Fix:** Accept `clear` or `none` at that prompt and say so in the prompt text.

### 7. Silent fall-through on unclear answers
**Severity: Medium. Ease of use.**
- At "Did you do it?", anything other than a yes or no word, such as "maybe", is treated as a skip.
- At "Keep it for today?", any non-"no" answer keeps the plan. Typing "yes please" or a stray key keeps it without saying so.
- The tests cover this deliberately to protect data. That is safe but not communicative.

**Fix:** Echo the outcome in one line: "Kept for today." or "Cleared." or "Left as it was."

### 8. Delete everything does not say what it deletes
**Severity: Medium. Ease of use, destructive-action safety.**
- Menu option 4 asks "Delete all saved notes and dates on this computer? (y/n)" without saying how many days or what plan will go.
- It sits one number from Help, with no undo.
- The prompt doesn't mention backup copies, but the delete removes them.

**Fix:** Name the contents in the question: "Delete 23 days of dates and your current plan (and any backup copy)? (y/n)". Keep it a typed `y`. Require the word `delete` only if you are worried.

### 9. The damaged-file path loses history and says "Welcome." again
**Severity: Medium. Ease of use.**
- A damaged file is moved to `notes.json.bak`, and the person gets a fresh start with the first-run welcome. They lose their dates and the "welcome back" and in-a-row continuity.
- The 1.9.7 notice explains where the backup is and that menu option 4 deletes it. It does not say how to get anything back.
- The notice prints before the greeting, so the first line a person sees after losing data is a file name, ahead of "Hello, world!".

**Fix:**
- Say what was lost in person words, such as "your earlier days and plan could not be read".
- Add a restore line for IT.
- Skip the privacy welcome on a repaired file, since this person is not new.

### 10. Time-of-day mismatch in the content
**Severity: Low. Retention.**
- The sign-in reminder opens the program when people start work.
- Many lines assume a different time. Examples: "Before you log off, jot tomorrow's first step", "Let the evening belong to you", "Leave on time tonight", "Choose one word for how you want the afternoon to feel".
- They are fine in the afternoon and odd at 8:30, which is exactly when the reminder fires.

**Fix:** Tag each line morning, any or afternoon, and choose from the right pool by local hour. If that is too much for now, remove the clearly evening ones from the pool that the reminder draws on.

### 11. Menu option 1 shows raw JSON
**Severity: Low. Ease of use.**
- It is honest, but a non-technical person sees braces and quotes. It is the trust feature and the one most likely to scare.

**Fix:** Lead with two plain lines (the days opened and the plan). Show the raw file only after "Show the exact file? (y/n)".

### 12. In-a-row wording and rule are slightly dishonest
**Severity: Low. Retention.**
- "You have opened this 3 times in a row" counts visits within 3 days of each other, so it can be shown after a four-day span. "This" is also ambiguous.
- It is gentle and optional, which is good.

**Fix:** "You have been back 3 times this week or so. Nice to see you." Or drop the number and say "Nice to see you again."

### 13. Save failure and crash messages are dead ends
**Severity: Low. Ease of use.**
- "Your notes could not be saved on this computer. This screen still works." gives no cause or next step.
- "Something went wrong. Contact IT." goes to employees, who may not know the install is IT's, and gives nothing to quote.
- Both are accepted in the backlog.

**Fix:** Add the folder path and one likely cause, such as a full disk or a locked folder, and a short reference code.

### 14. Retention can't be observed
**Severity: Medium. Retention.**
- By design nothing reports use, and the plan is to ask five people.
- That is a defensible trust choice, but it leaves the release gate with nothing to read.
- A retention gate with no data is a gate that always opens.

**Fix:**
- Schedule the question before shipping: day 3, day 14, and day 30, asked of each of the five people by name.
- Ask "did you open it yesterday, and why or why not?"
- Option 1 already lets a person read their own dates aloud, so no instrumentation is needed.

## The retention feature to build this round: a note to tomorrow

**What it is:**
- After the plan step, or when closing, ask once: "Anything to leave for tomorrow? (Enter to skip)".
- The next visit shows it at the top: "You left yourself this note: ..."
- It is shown once, then cleared.
- It is stored like the plan: one more field in `notes.json`, one line, cleaned by `tidy`, with the same visibility rules and the same "Delete everything" path.

**Why the person would come back because of it:**
- The reason becomes theirs, not the program's. Tomorrow's screen contains words only they could have written, such as "start with the budget email, the file is on the desktop".
- This is the one thing the program can offer that a calendar or a to-do app does not: a nudge from yesterday-you at the moment you sit down.
- It fits the product rules. It is a message to oneself, not a streak or a score. Skipping it costs nothing, there is no guilt, and nothing records whether it was acted on.
- It fixes finding 2, because every day leaves something behind that waits for the next one.
- It reuses existing mechanics: a field, one prompt, one display line. Add a test for show-once and clear, and a test that Delete everything removes it.

**Pair it with findings 1 and 3.** Say at first run that tomorrow's note and follow-up will be waiting, and offer the sign-in reminder on the 2nd or 3rd visit, so the person is there to read it.

## Highest-leverage changes, most important first

1. **Tell the person the hook up front** (finding 1): benefit-first welcome, "I will ask tomorrow", and a saved confirmation after the first plan.
2. **Build the note to tomorrow** (above), so each visit leaves something that is waiting for the next.
3. **Offer the sign-in reminder once, on the 2nd or 3rd visit** (finding 3).
4. **Answer "who is this for"**, and name the shortcut for what it does (finding 4). Decide whether the audience is the five employees or the generic person, and write the one-sentence promise.
5. **Plan comfort**: "same as last time", a way to clear a plan, and a one-line echo of what each answer did (findings 5, 6, 7).
6. **Safer delete and a friendlier damaged-file path** (findings 8, 9): say what will go, say what was lost, and don't re-welcome a returning person.
7. **Run the day-3, day-14 and day-30 check-ins with the five people** (finding 14). Without that, the retention gate has nothing to measure.

The rest (findings 10 to 13) is polish. Time-tagged content (finding 10) is the cheapest of them with a visible effect.

On process: the declined list in the notes is reasonable for the installer. The next round's effort should move from the installer and rare-error paths to the first and second sessions, where a person decides whether to return.

## Accessibility agent

# Accessibility review: hello-world 1.9.7 (WCAG 2.2 AA)

**Interface reviewed.** The interface is a console program, a PowerShell installer and uninstaller, CLI help, and the README and docs. WCAG is written for web content. I applied each criterion by analogy: names and roles become prompt and option labels, focus order becomes prompt order, and so on.

**Method.** This is a read-through of the packet only. Nothing was run. No screen reader (NVDA, JAWS, Narrator) and no Windows console was tried. The packet does not include `CHANGELOG.md`, `BACKLOG.md` or `reviews/`.

**Result.** No Critical or High findings. Every function is reachable and nameable by keyboard alone, and there are no timeouts. The Mediums are about accuracy and feedback in the text, not about reaching controls. I recommend a fix-then-ship on the first two Mediums.

## What already meets the bar

- **Linear plain-text output.** It is ASCII, uses no color, and has no redrawing, so it reads top to bottom for a screen reader (1.3.1, 1.4.1).
- **Dates.** The date is unambiguous ("Thursday, 1 October 2026").
- **Time limits.** There are none, so 2.2.1 is met.
- **Prompts.** Most prompts state their valid answers: "(y/n)", "Enter = skip", and "Choose 1 to 6".
- **Menu errors.** The menu error ("Please type a number from 1 to 6, or press Enter.") says what was wrong and what to do (3.3.1, 3.3.3).
- **Redundant entry.** The plan is never retyped (3.3.7).
- **Terminal-control input.** The program strips terminal-control characters from saved text.
- **Installer failures.** They begin with the words `FAILED:`, so meaning does not depend on color.
- **Shortcut name and title.** The shortcut has a description and sets the window title, so the window can be named.
- **CI summary.** It uses text outcomes, not color.

## Findings

### Medium

**M1. The damaged-file notice names the wrong file and runs into the greeting.**
Criteria: 3.3.1, 1.3.1, 3.3.3. This is the change under review.

- **Wrong name.** `backup_name()` produces `notes.json.bak2`, `.bak3` and so on when an earlier backup exists. The notice always says "notes.json.bak". On the second damage event it sends the person to the older, wrong file. The test `test_a_second_damaged_file_does_not_overwrite_the_first_backup` does not check the message.
- **No separator.** `load()` prints the notice before the greeting, and no blank line follows it. For a screen reader or a low-vision reader, the notice and "Hello, world!" read as one block.
- **No location.** "In the same folder" gives no path. The person has to go to option 1 to find it.
- **Fix:**
  - Pass the actual backup name through: `os.path.basename(name)` from `backup_name`.
  - Add `say()` after the notice.
  - Include `data_dir()` on its own indented line, like the other path outputs.
  - Extend `test_a_repaired_file_is_announced` to cover a second backup, a blank line after the notice, and the path.

**M2. Unrecognized input at the closing prompt, and at the follow-up prompts, silently does something.**
Criteria: 3.3.1, 3.3.3.

- **Closing prompt.** Anything other than Enter, `p`, `plan`, `m` or `menu` closes the window with no message. `help`, `options`, `2`, `q` or a typo end the program unexplained.
- **"Did you do it?"** An unrecognized answer such as "maybe" is treated as skip. The plan stays. The test `test_follow_up_keeps_the_plan_unless_the_answer_is_clear` locks in the keep behaviour, but nothing tells the person.
- **"Keep it for today? (y/n)"** Any answer except n or no keeps the plan, including Enter. The prompt advertises only y and n.
- **Fix:**
  - At the closing prompt, answer unknown input with "I did not understand that. Press Enter to close, or type plan or menu." and ask again once. Keep Enter as close.
  - Echo the outcome after each follow-up, for example "Kept for today." or "Left as it is."
  - Add Enter to the keep prompt text.

**M3. The installer's long permission check gives no reliable progress for screen-reader users.**
Criteria: 4.1.3, 2.2.2 (analogy).

- The check "can take several minutes". It prints one line, then relies on `Write-Progress`. Progress bars in PowerShell consoles are spoken inconsistently, or not at all.
- A person using a screen reader cannot tell a working window from a hung one for minutes.
- `$ProgressPreference = 'SilentlyContinue'` is set at step 4, so later checks give no progress at all.
- **Fix:** Replace the progress bar with plain periodic lines. Use `Write-Info "Checked $checked items so far"` every 500 items or 30 seconds. Keep it silent under `-Quiet`.

**M4. The opt-in sign-in launcher opens a window that takes focus, and typing at that moment goes into the program.**
Criteria: 3.2.1 and 2.4.3, by analogy.

- `start "hello-world" ... --startup` opens a new console at sign-in and moves focus to it.
- A person who is typing, such as a password, a PIN or a first sentence, can have those keystrokes land in "What is one thing you want to get done today?". That text is then saved in `notes.json`.
- The README tells people not to type passwords into this program.
- **Fix:**
  - Tell people in the README, and in the confirmation that option 2 prints, that a window opens at sign-in and takes focus.
  - Consider a short delay before the first prompt.
  - Consider ignoring input that arrives within the first moment of a `--startup` run. Both are behaviour changes, so the owner decides.

**M5. Menu and main-prompt commands are single letters, which is poor for speech input.**
Criteria: 2.5.3 and 3.3.2, by analogy.

- The prompt says "p for today's plan, m for options". Dictation and voice control handle whole words far better than "p" or "m".
- The program already accepts `plan` and `menu`, but the prompt never shows them.
- **Fix:** Reword to "Press Enter to close, or type plan or menu." Keep `p` and `m` working. Update the first-run line ("Type m ...") and the README to match.

### Low

**L1. `HELP` breaks the program's own 72-column rule.**
Criterion: 1.4.8 (analogy; the program's own line-width rule).
- The line "At the end of the screen, type p for today's plan or m for options. You can also run hello.cmd" is about 95 characters. It reflows unpredictably in a narrow or magnified window.
- The line-width tests exclude help.
- **Fix:** Rewrap `HELP` and add a width test for `--help`.

**L2. An unknown option is not named.**
Criteria: 3.3.1, 3.3.3.
- `--nope` gets "Unknown option. Here are the options." and not "Unknown option: --nope".
- `--remind` or `--streak` with no value gets the same generic message, even though the real problem is a missing `on` or `off`.
- **Fix:** Echo the offending argument, and say "needs on or off" for those two.

**L3. Several error messages state the failure but give no cause or next step.**
Criterion: 3.3.3.
- "Could not save that on this computer."
- "Could not set up the reminder."
- "The saved file can't be read right now, or it is damaged."
- "Your notes could not be saved on this computer."
- **Fix:** Add one short suggestion each, such as "Close other programs using the file, or ask IT". For `--stats`, offer "Run hello-world normally to set a damaged file aside."

**L4. The `--reset` listing-failure message (this change) is correct but not actionable.**
Criterion: 3.3.3.
- "Could not list the folder, so backup copies may remain:" followed by a path does not say what to do.
- **Fix:** Use "Look in this folder for files that start with notes.json. and delete them yourself:".

**L5. Menu wording for options 2 and 3 is ambiguous when read aloud.**
Criterion: 3.3.2.
- "Open once a day at sign-in: off (change it)" is heard as a state followed by a vague action.
- **Fix:** Make the action explicit, for example "2  Turn on opening at sign-in (now off)" and "3  Turn off the in-a-row line (now on)".

**L6. The full menu reprints after every action.**
Criterion: 3.2.3 (analogy).
- A screen-reader user rehears eight lines each time.
- **Fix:** Print the long list once. Afterward, show a short prompt such as "Choose 1 to 6, or Enter to close. Type menu for the list."

**L7. Option 1 ends with a raw JSON dump.**
Criterion: 1.3.1.
- Braces and quotes are spoken as punctuation.
- The first line, "Days you opened hello-world: N (last 7 days: M)", already carries the facts.
- **Fix:** Keep the JSON only for the person who wants it. Introduce it as optional, or put it behind a second choice.

**L8. Some tips and thoughts assume sight or hearing, against the stated design rule.**
Criterion: 3.1.5, plain-language and inclusion; not a strict WCAG item.
- `docs/WHY-DAILY-ACTIONS.md` says content must not assume an ability.
- Examples: "Look at something far away", "Gaze at something green", "Blink slowly", "Listen to one favorite song", and "Notice one pleasant sound".
- **Fix:** Rewrite these, or offer an alternative in the same sentence, such as "or notice what you can hear".

**L9. Ctrl+C is absorbed as "no answer".**
Criterion: 2.1.2 (analogy).
- `ask()` treats Ctrl+C as an empty answer, so the program continues. This is declined in `BACKLOG.md`.
- The person is never trapped, because Enter always works.
- Mention it in the README so keyboard users know Enter, not Ctrl+C, is the exit.

**L10. `textwrap` can split words and paths.**
Criterion: 1.3.1.
- By default it breaks at hyphens and inside long words. That splits "hello-world" across two lines and cuts long URLs in plans.
- **Fix:** Pass `break_on_hyphens=False, break_long_words=False` in `wrapped()`, `indent()` and the notice.

**L11. Installer colors are forced.**
Criteria: 1.4.3, 1.4.1.
- Red, Cyan and Green are set with `-ForegroundColor`. On a blue PowerShell background, Red can fall below 4.5:1, depending on the user's color scheme. I could not verify the actual contrast.
- Meaning is not carried by color alone, because "FAILED:" and "Installed" are in the text.
- **Fix:** Use the default foreground for the `FAILED:` and `Installed ...` lines, or leave color to the terminal theme.

**L12. README and docs details.**
Criteria: 1.3.1, 3.1.5.
- ">" is used as a path separator ("Settings > Apps > Installed apps > hello-world > Uninstall"). Screen readers say "greater than". Use "then" or spell out the steps.
- The IT steps ask for about nine separate paste-and-run lines. This is heavy for motor or cognitive load. Offer one script block, or a wrapper.
- There is no short statement that the program works with a screen reader, or that Enter always closes the window. Add two lines to the employee section.

**L13. The English-only text, and some Windows behaviour, are untested.**
Criterion: 3.1.1.
- The day names, month names and all prompts are hard-coded English. This is a known gap and is listed in PLAN.
- Non-English plan text is kept but untested on a real Windows console, where a font may not show some characters.

**L14. There are no tests for accessibility properties.**
- Add tests for: the help line width, the notice's blank line and actual backup name, the unknown-input message at the closing prompt, and the unknown-option echo.
- Add a manual check with Narrator or NVDA to the "Not tested" list in `PLAN.md`.

## Ship this round

1. **Fix the damaged-file notice (M1).** It is the change under review and has a real accuracy bug.
   - Name the actual backup file.
   - Add a blank line after the notice.
   - Add the folder path.
   - Extend the test to cover a second backup.
2. **Give feedback for unrecognized input (M2).** This is a small, contained change. Echo the outcome at the follow-up prompts, and re-ask once at the closing prompt.
3. **Show `plan` and `menu` in the closing prompt (M5).** It is free, because the program already accepts the words.
4. **Rewrap `HELP` (L1) and echo the unknown option (L2).** Both are quick wins, with a test each.

M3 (installer progress) and M4 (sign-in focus) are real but touch Windows behaviour that cannot be tested here. Schedule them for a round where a Windows run is available.
