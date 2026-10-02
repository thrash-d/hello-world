# Round 37

- Date: 2026-10-02
- Commit reviewed: e164f0f (version 1.11.0)
- Files reviewed: .editorconfig, .gitattributes, .github/workflows/auto-tag.yml, .github/workflows/dependabot-automerge.yml, .github/workflows/devkit-quality.yml, .gitignore, PLAN.md, README.md, VERSION, docs/WHY-DAILY-ACTIONS.md, hello.py, install.ps1, test_hello.py, uninstall.ps1 (all given to every reviewer in one packet file)
- Packet note: the "Developer's notes on this change" section came through empty because of a packet-building mistake, so the reviewers saw no developer's notes. All four said so.
- Agents run: lead, security, usability and retention, accessibility
- Redactions: none needed

## Lead reviewer

# Review of hello-world 1.11.0

I read the whole packet (2,845 lines). I found no Critical defects. The core program is carefully built and its failure handling is better than most shipped tools. The weak points are three things:
- **Product value:** the product itself gives people little reason to come back.
- **Platform:** several Windows behaviours are still untested.
- **Packet gaps:** the packet doesn't back up some of what the repo says.

**Scope limits.**
- "Developer's notes on this change" is empty, so I can't confirm what was fixed since the last review.
- I did not run anything.
- I can't verify that the pinned Python 3.14.8 URL and SHA-256 are correct.
- I can't verify the `0123...` commit placeholder or the `thrash-d/hello-world` GitHub owner.

## Part 1: Findings, most severe first

### 1. High, retention: nothing here pulls a person back after the first week
- **What is wrong:** the content is 100 generic wellness lines and 100 generic tips, fixed in the source. A thought and tip pair is picked by `ordinal` and `ordinal+37`, so the exact same pair returns every 100 days. The only personal feature is a one-line plan. It keeps no history, can't hold more than one item, and has no way to be edited later.
- **Why it hurts:** a second session is no easier or better than the first, and the person can't shape it. Nothing makes it theirs. Adding or changing content needs a code change and an admin redeploy. A person who once opened the Start menu entry and read generic wellness lines has no reason to do it again.
- **Evidence from the repo:** PLAN.md measures retention by "asking the five employees". Nothing in the repo says they asked for this.
- **Fix:** see Part 2, items 1 and 2.

### 2. High, ease of use / product: the audience and purpose are unclear
- The README opens with "A small daily moment for employees". docs/WHY-DAILY-ACTIONS.md admits the program started as a hello-world payload for a hardened installer.
- It is an IT-deployed program that employees did not ask for, and its pitch is that it feels non-pushy.
- That pitch hasn't been tested with any employee.
- **Fix:** run the pilot in Part 2, item 1 before shipping more features.

### 3. Medium, bug / process: the repo points at files that aren't in it, and CI probably fails
- README, PLAN and docs reference `CHANGELOG.md`, `BACKLOG.md` and `reviews/`. None of them is in the repository listing.
- The workflows call `.devkit/kit/ruff.toml`, `.devkit/kit/vale.ini`, `.devkit/kit/commit_lint.py`, `.devkit/kit/check_duplicates.py` and `.devkit/kit/gitleaks.toml`. No `.devkit/` directory is in the packet.
- If `.devkit/` is really absent, two CI steps fail:
  - the ruff step passes `--config .devkit/kit/ruff.toml` for `hello.py`;
  - the Vale step exits above 1 on a missing config.
- These steps are non-blocking unless `DEVKIT_BLOCKING=true`, but the run goes red and the warnings train people to ignore it.
- **Fix:** commit the files, or have each step skip with a clear message when its config is missing. Remove the dangling README and PLAN references if the files are meant to stay out of the repo.

### 4. Medium, bug: the installer's smoke test can't catch a broken interactive path
- Step 5 only runs `hello.cmd --plain`, which prints one line and never touches the code that decides whether a person is at the keyboard (`interactive()`).
- The Windows-only parts of `hello.py` are untested on Windows 1.8 onward: `interactive()` with ctypes and msvcrt, console Unicode, and the shortcut's `& if errorlevel 1 pause` chain.
- README admits the real install has not been run on a clean machine.
- **Fix:**
  - Smoke-test with `cmd /c "hello.cmd < NUL"`. That runs the whole daily screen without prompting and exercises the real Windows code path.
  - Run the clean-PC test list in PLAN.md before rollout. It names the right cases: install, reinstall, interrupted install, uninstall, and checking the icon, title, Enter-closes and launcher.

### 5. Medium, security: the README runs `git.exe` as admin before the installer has checked it
- The README clones using `$git` taken from the registry, before `install.ps1` verifies that Git's folder is admin-only.
- The check protects every later step but not this one. A user-writable Git install would run attacker code with admin rights on the clone line.
- **Fix:** document the prerequisite (Git installed for all users, folder admin-only) as a check to do first. Or ship a small bootstrap that verifies the Git path before it clones.

### 6. Medium, security: the Startup-folder `.cmd` launcher looks like malware persistence
- A `.cmd` script in the Startup folder is the classic persistence pattern, MITRE T1547.001. EDR and AppLocker/WDAC rules may flag or block it.
- If that happens, the sign-in feature silently never runs, and no one knows why.
- **Fix:**
  - Use a `.lnk` shortcut instead.
  - Tell IT in the README to allow-list it.
  - Say in the menu text that option 2 may be blocked by company policy.

### 7. Medium, security: the CI supply chain isn't pinned the way the installer is
- Workflow actions are on mutable tags (`@v5`, `@v6`).
- osv-scanner, gitleaks and vale are downloaded with `curl` and no checksum, even though the installer hash-pins Python.
- `dependabot-automerge.yml` merges major updates, including action bumps, after only `pytest` passes. The tests don't exercise the workflows at all.
- Its `gh pr merge` has no `--auto`, so it will fail when other required checks are still pending.
- **Fix:** pin actions by commit SHA and checksum-verify the downloaded tools. Don't auto-merge `github-actions` major bumps. Add `--auto` to the merge call.

### 8. Medium, accessibility: no real screen-reader pass and no read-only mode
- README admits it "has not been tried with a real screen reader".
- `--plain` prints only "Hello, world!". There is no way to read the day's thought and tip without being asked questions.
- Every prompt ends in " > ", which screen readers read aloud as "greater than".
- The window closes when the program exits, which is hard to follow for anyone who needs time with it.
- **Fix:** see Part 2, item 3.

### 9. Medium, bug: a plan left unanswered becomes invisible for the rest of the day
- If you press Enter at "Did you do it?", the plan keeps its old date.
- Opening the program again the same day (`seen_today` is true) shows neither "Your plan for today" nor the plan prompt.
- The only way back to the plan is to know about `plan` or the menu.
- **Fix:** show the stale plan, labelled with its date, on repeat opens.

### 10. Medium, bug: stale plans disappear silently after 14 days
- The 14-day cutoff in `daily()` sets the plan to `None`, and it then gets saved over.
- README does not mention this, and nothing tells the person.
- **Fix:** say "I dropped a plan from N days ago" once, or never drop silently. Document the rule.

### 11. Low–Medium, bug: "not yet" at the sign-in offer counts as a permanent "no"
- `is_no("not yet")` is true, because "not yet" is in `NO`, so `offered` is set to true.
- README says "Only a clear no is final. Enter means ask me later."
- Someone who answers "not yet" will never be asked again.
- **Fix:** use a separate set for the offer that excludes "not yet".

### 12. Low–Medium, bug: no `fsync` before `os.replace` in `save()`
- A power cut can leave an empty or truncated `notes.json`.
- On the next load that triggers the "damaged file" path and loses all history.
- **Fix:** `f.flush(); os.fsync(f.fileno())` before the replace.

### 13. Low, bug: unknown fields in the notes file are dropped, and two windows can overwrite each other
- `save()` writes only the keys this version knows. A file written by a newer version loses its extra fields when this one saves.
- Two windows opened at once (for example sign-in plus Start menu) both write, and the last one wins.
- **Fix:** carry unknown keys through, and re-read before saving.

### 14. Low, bug: an unreadable-but-valid file shows the first-run welcome to a returning user
- If the file is locked, `first` is true. The person gets the long welcome text, then "could not be saved".
- **Fix:** say the file couldn't be read instead of replaying the welcome.

### 15. Low, ease of use: the final prompts don't accept common exit words
- `q`, `quit`, `exit`, `x`, `help`, `?` and `bye` all count as "not one of the choices". A second wrong word ends with "Closing now".
- The menu answers an unknown word with "Please type a number from 1 to 6, or press Enter."
- **Fix:** accept `q`/`quit`/`exit` and `h`/`help`/`?` at both prompts.

### 16. Low, ease of use: the in-a-row message reads oddly
- It says "You have opened this 3 times in a row". "This" refers to nothing.
- A visit every 3 days also counts as "in a row", so "in a row" overstates it.
- **Fix:** "You have opened hello-world 3 times in close succession." or "3 visits in a row, weekends included."

### 17. Low, ease of use: menu and option naming is inconsistent
- Option 5 (Help) sits between "Delete" (4) and "Plan" (6), and the prompt says "Choose 1 to 6".
- The same feature is called "sign-in reminder", "open at sign-in" and `--remind` in different places. It is not a reminder, it is a launcher.
- **Fix:** put the plan option and delete in a sensible order, with delete last. Use one name everywhere.

### 18. Low, accessibility / inclusion: the content assumes sight, hearing, desks and British idioms
- Tips such as "look at something far away", "blink slowly", "name three things you can see" and "listen to one favorite song" assume sight and hearing.
- "Share the biscuits", the day-month date format and the desk and video-call framing assume a particular workplace. PLAN.md says nothing assumes ability or role.
- **Fix:** rewrite or alternate the sight and hearing prompts ("or whichever senses suit you"). Add a few that fit non-desk work.

### 19. Low, bug: `show_saved` counts only the last 400 days
- `MAX_VISITS` is 400, so "Days you opened hello-world" stops climbing and is wrong after about a year.
- **Fix:** label it "last N days" or drop the lifetime count.

### 20. Low, operations: nothing patches the pinned Python after install
- The pinned embedded Python never updates on its own.
- Updating means manual re-clone and re-run on every PC, with no notification.
- **Fix:** document an owner and a cadence for the update.

### 21. Low, documentation and CI
- README's "Update to a new release" uses `$d` without saying it only works in the same window as the install (the installer's own notes do say it).
- `devkit-quality` runs twice on pushes to PR branches (`push` plus `pull_request`).
- **Fix:** copy the caveat into README. Limit `push` to `main`.

### 22. Low, tests: gaps
- The in-a-row test checks only the 3rd and 7th visit. 14 and 30 aren't covered.
- No test covers the 14-day plan expiry or the stale-plan-invisible case.
- Tests never clean up their temp dirs.

## Part 2: Improvements, most important first

1. **Decide who it is for, then prove it.**
   - What to build or change: run a two-week pilot with the five employees. Ask each one a single question at the end: "would you miss it?"
   - Why it matters: the whole design assumes a retention story nobody has checked. The pilot decides whether the next work is content, the plan, or retiring the tool.
   - A sharper direction: make the one-line plan the product ("one thing today, then the follow-up"). Alternatively give IT a real reason to deploy it, with an org-owned line (a security tip, a real notice) that IT can edit in a text file in the install folder.

2. **Retention change: let the person own part of it.**
   - What to build: add a menu item, "Add a line of your own". It saves a thought, a tip or a reminder to `notes.json`, and the program mixes it in on roughly one day in five.
   - Add weekday awareness: Monday "name the one thing for the week", Friday "name one thing that went well".
   - Why it matters: the person's own words give them a reason to return. Weekday variation makes the 100-day repeat much less visible. A second session now differs from the first.

3. **Accessibility change: a read-only mode and a real assistive-technology pass.**
   - What to build:
     - `hello.cmd --today` prints the greeting, thought and tip with no prompts and exits with 0.
     - Drop the " > " from prompts.
     - Test with Narrator and NVDA and write the results into README.
   - Why it matters: a screen-reader user can read the day's content once and be done. The claim that it works with a screen reader becomes a tested fact.

4. **Ease of use: forgiving input and one consistent vocabulary.**
   - What to build: accept `q`, `quit`, `exit`, `help` and `?`. Rename the sign-in feature everywhere. Reorder the menu with delete last.
   - Why it matters: a person who types the obvious word shouldn't be told it is wrong.

5. **Make the install trustworthy before rollout.**
   - What to build: switch the launcher to a `.lnk`. Smoke-test with `< NUL`. Run the PLAN.md clean-PC checklist on one real machine. Pin and checksum the CI tooling.
   - Why it matters: nothing here is testable on Linux, and the first real install is the highest-risk moment.

6. **Keep the content from running out.**
   - What to build: expand the lists or generate variants, and let IT or the user supply a content file.
   - Why it matters: at one line a day, 100 lines is about 14 weeks before repeats start.

Relevant files, all in the packet at `[packet file]`: `hello.py`, `install.ps1`, `uninstall.ps1`, `test_hello.py`, `README.md`, `PLAN.md`, `docs/WHY-DAILY-ACTIONS.md` and the three workflows under `.github/workflows/`.

## Security

**Security review: hello-world 1.11.0**

**Summary.** I found no Critical or High issues. The program is small, makes no network calls and has no server surface. The Windows installer is carefully built. Most of the risk is in the supply chain and process around it: unpinned CI actions, unverified CI tool downloads, auto-merge of dependency updates, and a commit-hash trust anchor that is only as strong as the channel it arrives on.

**Scope limits.**
- The "Developer's notes on this change" section is empty, so there was no stated intent to check the code against.
- `.devkit/` (the kit scripts, `gitleaks.toml`, `duplicates.json`), `CHANGELOG.md`, `BACKLOG.md` and `reviews/` were not in the packet, so I did not review them. CI executes the `.devkit/kit` scripts.
- I could not see branch protection, rulesets, repo variables or secrets. Several findings depend on them.

---

### Findings

**1. Medium: GitHub Actions pinned to mutable tags, including a job with `contents: write` (CWE-829, NIST SA-12/SR-3, CIS Software Supply Chain)**
- `actions/checkout@v5`, `setup-node@v5` and `setup-python@v6` are referenced by tag in all three workflows.
- The riskiest case is `auto-tag.yml`, which runs on every push to `main` with `contents: write`. A retagged or compromised action there can push tags or code.
- **Fix:**
  - Pin every action to a full commit SHA, with the version in a comment.
  - Keep `contents: read` on every job that doesn't push.
  - Add `persist-credentials: false` to checkouts that don't need to push. `devkit-quality` and the Dependabot `check` job both run PR-influenced code with the token left in `.git/config`.

**2. Medium: Dependabot auto-merge includes major updates and its gate proves little (CWE-1357, OWASP A06/A08, ATT&CK T1195.001)**
- `dependabot-automerge.yml` squash-merges any PR whose `pull_request.user.login` is `dependabot[bot]`, after `npm run build/test` or pytest passes.
- The check job runs the updated dependencies' install and build scripts. `npm ci` runs lifecycle scripts, and `pip install .` runs build backends.
- A dependency that passes a thin test suite merges unreviewed. In this repo `test_hello.py` never touches dependencies, so any bump passes.
- The condition keys on the PR author, not `github.actor`. A collaborator who pushes to a Dependabot branch still gets auto-merged.
- **Fix:**
  - Gate on `dependabot/fetch-metadata` and merge only patch and minor updates.
  - Exclude the `github-actions` ecosystem from auto-merge, or require human review for it.
  - Use `--auto` so that required reviews and checks are still enforced.
  - Check `github.actor` as well.
  - Run `npm ci --ignore-scripts` where the build allows.
  - Protect `.github/**` and the installer files with CODEOWNERS.

**3. Medium: The installer's "reviewed commit" trust anchor depends on an unspecified channel, and tagging is unreviewed (CWE-494, NIST SI-7, SA-10)**
- The installer validates that the clone is at the commit hash the admin supplies. That is strong only if the hash reaches the admin out of band.
- The README ships a placeholder hash and lives in the same repo. An attacker who controls the repo controls the README, the tag and any "reviewed" claim.
- `auto-tag.yml` tags whatever lands on `main`, so a tag does not mean "reviewed".
- Nothing in the packet shows signed tags, tag immutability, branch protection or CODEOWNERS.
- **Fix:**
  - Publish the expected hash through a separate channel, such as a change ticket or a signed release note.
  - Sign release tags and verify them in the install steps, for example with `git verify-tag` and a pinned key.
  - Enable tag rulesets that block update and delete.
  - Require PR review on `main`, with CODEOWNERS on `install.ps1`, `uninstall.ps1`, `hello.py`, `VERSION` and `.github/`.

**4. Medium/Low: CI downloads and runs tool binaries without integrity checks (CWE-494)**
- `devkit-quality.yml` fetches `osv-scanner`, `gitleaks` and `vale` with `curl` and runs them with no checksum or attestation check.
- `ruff` is installed with `pipx` without hashes. `npx --yes jscpd@5.3.2` pins the top-level version but not its transitive dependencies.
- The token is read-only, so the damage is bounded, but the secrets scanner itself is among the unverified binaries. A tampered gitleaks could hide leaks.
- **Fix:** verify a pinned SHA-256 (`sha256sum -c`) or `gh attestation verify` for each download. Use `pipx install --pip-args="--require-hashes"` or a hashed requirements file. Commit a lockfile for jscpd.

**5. Medium/Low: The bundled Python is outside every dependency scanner (OWASP A06, NIST SI-2, RA-5)**
- The runtime Python 3.14.8 is pinned only by a URL and SHA-256 inside `install.ps1`.
- `osv-scanner` scans lockfiles, and this repo has none, so it scans nothing. The runtime and its bundled DLLs (OpenSSL in `_ssl`, sqlite, expat, libffi) will accumulate CVEs with no alert.
- `hello.py` needs only a small slice of the stdlib. Shipping the whole embeddable distribution adds attack surface, because every user can run it.
- **Fix:**
  - Add a scheduled job that compares `$pySha256` and `$pyUrl` against the latest python.org security release and opens an issue.
  - Verify the sigstore bundle for the zip, not just a hash copied from it.
  - Optionally delete unused extension modules (`_ssl`, `_hashlib`, `_sqlite3` and similar) from `$new` after extraction. Re-run the `--plain` test afterward.

**6. Low: Quality gates are non-blocking by default, and suppression files are editable by PR (CWE-1188, NIST SA-11, CM-3)**
- Vulnerable-dependency, lint and other findings do not fail the run until `DEVKIT_BLOCKING=true`.
- Only gitleaks always fails the run, and that matters only if branch protection requires the check.
- A PR can edit `.gitleaksignore`, `.devkit/gitleaks.toml` and `.devkit/jscpd.json`. That lets a PR author hide a finding in the same PR.
- **Fix:** make `devkit-quality` a required status check and default blocking on. Put suppression files under CODEOWNERS. Run gitleaks with the kit's config when the repo's copy exists, not as an either/or.

**7. Low: Notes file permissions and temp-file handling on POSIX (CWE-276, CWE-377, CWE-59)**
- `save()` calls `os.makedirs(mode=0o700)`, which applies only to the leaf directory.
- It then creates `notes.json.<pid>.tmp` with `open(..., "w")`, which is mode 0644 under a typical umask. The plan text would be world-readable on a shared Linux host.
- The temp name is predictable and the open follows symlinks.
- On Windows it relies on the inherited `AppData\Local` ACL, which is fine.
- **Fix:** use `tempfile.mkstemp(dir=data_dir())` or `os.open(..., O_CREAT|O_EXCL|O_NOFOLLOW, 0o600)`, then `os.replace`. Call `fsync` before the replace.

**8. Low: Elevated uninstall deletes through user-controlled paths (CWE-59, ATT&CK T1574)**
- `uninstall.ps1` runs elevated. For every profile in `ProfileList` it calls `Remove-Item -LiteralPath <profile>\AppData\...\Startup\hello-world-daily.cmd`.
- A standard user can swap `Start Menu\Programs` or `Startup` for a junction, so the admin deletes a file of that exact name anywhere.
- The impact is near zero because the name is fixed, but it is a privileged action on user-controlled paths.
- **Fix:** resolve each path component and refuse to proceed if any is a reparse point. Or drop the sweep: have the launcher `.cmd` test for `hello.cmd` and delete itself if it is missing.

**9. Low/Info: Startup-folder persistence and an unquoted `%*` (ATT&CK T1547.001, CWE-78/88)**
- The opt-in sign-in feature writes a user-writable `.cmd` into the user's Startup folder. It is a deliberate, documented feature and is user-scoped, so there is no privilege gain. EDR products will flag it. Tell the SOC about `hello-world-daily.cmd`.
- `hello.cmd` forwards `%*` unquoted. Nothing currently calls it with untrusted arguments. If a protocol handler or another tool ever does, `&` or `|` in an argument becomes command injection.
- `remind()` rejects `"` and `%` in the target path but not `^`, `&` or `!`. These are safe inside the quotes it uses, but worth a comment.
- **Fix:** document the launcher for detection engineers. Keep `run()`'s strict argument allowlist as the real control rather than trusting the shell layer.

**10. Low: Data retention and exposure, mostly disclosed (CWE-312, CWE-532)**
- Plans are stored in plaintext. `.bak` copies of damaged files keep old plan text until the user deletes everything. Uninstall deliberately leaves notes behind. The README discloses all of this honestly.
- `install.log` is a PowerShell transcript. It records the admin's username and machine name, and the README suggests copying it elsewhere.
- **Fix:** nothing is required for the notes. Tell IT to treat `install.log` as sensitive-ish when they copy it.

**11. Low: `.gitignore` secret patterns are incomplete (CWE-540)**
- Missing: `*.pfx`, `*.p12`, `*.jks`, `id_rsa*`, `*.kdbx`, `.npmrc`, `.pypirc`, `*.tfstate`, `*.p8`.
- Gitleaks over full history partly compensates.
- **Fix:** add the missing patterns.

---

### Checked and clean

- **Injection.**
  - No `eval`, `exec`, `subprocess`, `os.system` or `pickle`/`yaml` anywhere in `hello.py`. The only deserialization is `json.loads`, with a size cap (`MAX_FILE`) and `RecursionError`/`MemoryError` handling.
  - Every date goes through `date.fromisoformat`. Unknown keys in `notes.json` are dropped, never echoed.
  - CI expressions interpolated into shell (`steps.*.outcome`, `vars.*`) are fixed enums. Attacker-controllable event fields (`base.sha`, `head.sha`) go through `env:`, not inline `${{ }}`. No `head_ref` or title interpolation, and no `pull_request_target`.
  - `auto-tag.yml` expands `$v` only as a quoted shell variable behind a `v` prefix, so there is no option injection and no `eval`.
- **Terminal escape and bidi injection (CWE-150).** `tidy()` strips ESC, C1, bidi overrides and other Cf characters, keeping only ZWJ and ZWNJ. It is applied to loaded and typed text, and tested. Output paths print only static text, cleaned text or filesystem paths.
- **SSRF, CSRF, XSS, SQLi, authn/authz.** Not applicable: there is no server, web page, database, account or network client in the program. The installer's only network fetches are a fixed python.org URL and the git clone.
- **Secrets.** No credentials or tokens in the repo. The workflows use only `GITHUB_TOKEN`, with least-privilege `permissions:` blocks.
- **Environment variable hijack.** `hello.py` reads no `HELLO_*` or `PYTHON*` variables. Test hooks are module globals, and a test proves environment values are ignored. `hello.cmd` runs Python with `-I`.
- **Installer privilege boundary.**
  - It refuses anything but an admin-only clone, verifies the commit and the four executed files, and rejects reparse points.
  - It checks Git's install tree and `ProgramData\Git`, and calls `git` and `icacls` by full path.
  - It scrubs `GIT_*`, `HOME` and `XDG_CONFIG_HOME`, and pins and hash-checks the Python download.
  - It builds and tests the new install beside the old one and swaps with rollback.
  - The installed tree and the shortcut get ACL-verified.
  - The shortcut runs `cmd.exe /d`, which skips AutoRun.
  - I found no TOCTOU between check and use, because everything involved is admin-only. The checks are conservative and ignore Deny ACEs.
- **Uninstall elevation.** `uninstall.ps1` runs from an admin-only path and re-checks that `$PSScriptRoot` equals the install folder. It uses the full path to `powershell.exe`.
- **Cross-account access to user data.** The data directory is per-user under `AppData\Local`. Nothing in the program writes outside it, apart from the opt-in Startup launcher.

## Usability and retention

# Product review: hello-world 1.11.0 (ease of use and retention)

I read the whole packet. The "Developer's notes on this change" section is empty. CHANGELOG.md, BACKLOG.md and reviews/ are listed in the README but not in the packet. I reviewed the product as it ships in README.md, PLAN.md and hello.py.

## Verdict

Retention is a release gate, and as built this does not pass it. The one-time experience is polished and kind, and the safety and privacy handling is above average. But the product removes the three things that make a person come back to a daily tool:

- It stores no history of what they did.
- It has no personal asset that grows.
- It has no cost to leaving.

What remains is 100 generic tips that repeat every 100 days, plus one single-slot plan field. Day 30 looks the same as day 2. A person who tries it for a week, finds it pleasant and then stops has no reason to return, and nothing in the product tells you that happened.

**Who is this for?** It is unclear. The README says "employees", "the most generic possible person", "any age, any role". The content is wellness and tidiness advice mixed with a task-planning feature. Nobody chose to install it, because IT deploys it with "IT Department" as the publisher. There is no stated job-to-be-done and no announcement text that gives an employee a reason to try it. The docs speak about the audience in the third person and never to them. A tool for "everyone" with no stated job is the usual cause of one-time use. Pick a primary job (I recommend "start my workday with my own short list") and let the wellness content support it.

## Findings

### Critical

**1. Retention: no personal asset accrues, and the design deliberately blocks one.** *Retention.*
- The program saves only visit dates and one plan. It keeps "no record of whether a plan was done". Answering "y" deletes the plan.
- The "Days you opened hello-world: N" count appears only as a raw JSON dump in menu option 1. That is a debug view, not a progress view.
- Nothing builds on days 3, 10 or 30. The streak line is a single sentence at visit 3, 7, 14 and every 30th. It carries no information and is deliberately off by default for any person who isn't there on those days.
- The design record's reasoning ("a count is not value", "feels like being checked on") is right about employer-visible data. It does not follow that the person's own private history must go. Data that only the person sees is the usual reason people return.
- **Fix:** keep a private, local, person-owned history and show it back to them (see the retention feature below). Keep the no-network, no-reporting rule. That rule is what makes the history safe to keep.

**2. Retention: the daily content gives no reason to return after the first two weeks.** *Retention.*
- It is the same text for every person, chosen by date, and it repeats every 100 days.
- It is not responsive to anything the person did, and it gives no hint of tomorrow. The screen ends with "Press Enter to close".
- By visit 7, an observant person has seen the pattern: a thought, a tip, a question. Nothing is withheld, so nothing pulls them back.
- **Fix:** tie content to the person's own plan, so the tip or thought follows from what they said. The simplest version is carrying forward their own words. Add one line at the end such as "Tomorrow: your plan comes back, and a new thought."

### High

**3. Ease of use: unclear value before the first effort, and the first screen is longer than claimed.** *Ease of use.*
- PLAN.md says "about 14 lines". The first run prints the greeting, a date, an 8-line welcome paragraph (privacy-heavy), the thought, the tip, then the plan prompt, then possibly the sign-in prompt, then the close prompt. That is roughly 25 lines and 3 or 4 prompts in the first minute.
- The most important sentence, "type a plan, and it asks tomorrow how it went", is buried in the middle of the privacy paragraph.
- **Fix:** on first run, lead with one sentence of value and one prompt. Move the privacy statement to a single line ("Saved only on this PC. Menu shows exactly what.") and keep the detail in the menu or README. Show the thought and tip first. They are the immediate value.

**4. Ease of use: the sign-in offer comes too early.** *Ease of use, retention.*
- Right after the person types their first plan, before they have seen the product work once, it asks them to open at every sign-in. Plans are the only thing that reminder is for.
- Enter means "ask me later" and it asks up to three times. Three more unrequested questions is a tax on exactly the people who weren't sure.
- **Fix:** ask only after the person has answered a follow-up ("Did you do it?") once. That is the first moment the reminder has proven its value. Then it is a one-time ask with a clear yes or no.

**5. Ease of use and retention: the second session is not faster than the first, and it is the moment you will lose people.** *Both.*
- Day 2 is: follow-up question, then "keep it for today? (y/n)", then the thought, then the tip, then the plan prompt (usually typed from scratch), then the close prompt. That is 3 to 4 prompts, all typed.
- Nothing is learned about the person. Retyping a recurring plan ("Send the invoice") every day is the exact friction that kills habit.
- **Fix:**
  - Offer "same as yesterday" as a one-key choice.
  - After the person has used it three times, shorten the screen, for example by collapsing the thought and tip into one line unless they ask.
  - Show typed commands once, then trust the person.

**6. Ease of use and retention: the product has never run in its real environment.** *Both.*
- PLAN.md and WHY-DAILY-ACTIONS.md both say the real install was not tested. Untested items include the Start menu shortcut, the icon, the window title, console Unicode input, and whether Enter closes the window.
- Those are the first-run experience for every employee. If the window flashes closed or shows garbled text on the first launch, nobody opens it a second time.
- **Fix:** treat a real-PC first-run on a clean machine as a release blocker. The checklist already exists in PLAN.md "Not tested". Run it before shipping.

**7. Retention: you cannot tell whether anyone returned.** *Retention.*
- Rollout success is defined as "installs that finish without error, out of five". That measures installs, not use. Retention is "asking the five employees".
- With five people and no reminder, silence from two of them looks like success.
- **Fix:** keep the no-reporting rule, but give the person a way to opt in to a signal. For example, after day 7 the program can offer to print a short summary the person can copy and send themselves ("Days opened: 4. Plans done: 3."). Schedule a check-in at day 14 whose question is "did you open it this week?" and record the answer by hand.

### Medium

**8. Ease of use: hidden commands and a dead-end on a wrong word.** *Ease of use.*
- The final prompt is "Press Enter to close, or type plan or menu >". Typing `help`, `?`, `q`, `quit` or `exit` gives "That was not one of the choices." The message does not list the choices.
- A second wrong word prints "Closing now. Nothing was changed.", and the window closes.
- **Fix:** have the error line repeat the choices ("Type plan, menu, or press Enter."). Accept `q`, `quit` and `exit` as close. Accept `help` and `?` as the menu.

**9. Destructive-action safety: silent overwrite and silent expiry of the plan.** *Ease of use.*
- If the person presses Enter at "Did you do it?", the old plan remains, then the program asks for a new plan, and typing one replaces the old one. The prompt does warn: "a plan typed here replaces the old one".
- A plan older than 14 days disappears with no message.
- The follow-up question never says what Enter does. In code, Enter at "Keep it for today? (y/n)" keeps the plan, but the prompt reads like a forced binary.
- **Fix:** keep a short "recently cleared" list (see the retention feature) so any replacement or expiry can be undone from the menu. Say what Enter does in every prompt. Say "Your old plan from 3 weeks ago was cleared" when expiry happens.

**10. Destructive-action safety and error recovery: the delete and damaged-file handling lose history with no way back.** *Ease of use.*
- Option 4 asks y/n but does not say what will be lost (plan, dates, backups). Delete sits next to Help in the menu and is numbered 4, with plan at 6 after Help at 5, so the numbering is out of order.
- A damaged file is set aside as a `.bak`, which is good and clearly announced. But the only recovery is hand-editing JSON, and "Your earlier days and plan could not be read" is a dead end for a non-technical person.
- **Fix:** have the delete prompt list what it will remove ("your plan and 14 days of dates"). Reorder the menu so Delete is last. Offer to restore from the backup automatically when it parses partially.

**11. Empty states and progressive disclosure: menu option 1 is a raw JSON dump.** *Ease of use, retention.*
- This is the only place a person can see their own data. It prints the path, a count and then raw JSON.
- It is accurate and honest, but it reads as a developer tool, which undercuts the "friendly daily moment" tone.
- **Fix:** show a friendly summary first ("You have opened hello-world on 12 days. Your plan today: ..."), then offer "Show the raw file" as a second step.

**12. Retention: the tip has no loop.** *Retention.*
- "Try this today" has no follow-up. The plan gets a next-day question and the tip never does, so the tip is read once and gone.
- **Fix:** let the person press one key to mark the tip as tried. Store it locally, show it back as "tips you tried this month", and let the next day's tip lean on it only if they want.

**13. Ease of use for IT, who are also users.** *Ease of use.*
- The install is eight separate pasted lines, needs Git for Windows installed for all users, and every update is delete, re-clone, reinstall by hand on each workstation. Failures are explained well.
- For one IT admin with five PCs this is acceptable. Past that, it is an adoption cap, and a stale install on an employee PC is invisible.
- **Fix:** provide one copy-paste block for the common case and a short employee announcement template in the README ("What this is, why it is on your PC, how to remove it").

### Low

**14. "Hello, world!" as the title is a developer joke.** *Ease of use.* The employee sees it as the headline of a wellness tool. Keep it only if it is a deliberate brand, otherwise use the date or the person's plan as the first line.

**15. Streak wording.** *Retention.* "You have opened this 7 times in a row" is ambiguous when a 3-day gap counts as continuous. A person who skipped a weekend and two days may feel it is wrong. Say "You have been back 7 times this month" or drop the number.

**16. Typed plan limit.** *Ease of use.* A 120-character plan is cut with a message, which is good. But a person who wants three tasks must squeeze them into one line, which is a sign the single-slot model is too small.

**17. English only.** *Ease of use.* This is honestly disclosed. Note it as a known limit for "any role, any age" if the workforce is mixed.

## What is already good (keep it)

- Honest privacy statement, and a clear way to see and delete what is saved.
- No shaming language, and a welcome back after a gap.
- Safe handling of damaged files, hostile input and a dead terminal.
- Plain linear text that works with a screen reader and with Enter alone.

## Highest-leverage product changes, most important first

1. **Build a private "My list" with history and carry-forward** (the retention feature below). This is the only change that gives a person something worth coming back to.
2. **Cut the first run to one value sentence and one prompt**, and move the privacy detail to one line. Do not show the sign-in offer until after the first answered follow-up.
3. **Make the second session faster.** Offer "same as yesterday" on one key, and shorten the screen after the third visit.
4. **Run the real-PC first-run checklist** on a clean machine before shipping. This is a release blocker, because nothing else matters if the first launch fails.
5. **Add a friendly "your last 7 days" summary** in place of the raw JSON, so the person sees their own progress.
6. **Fix the dead ends:** list the choices in the error line, accept `q`, `quit`, `exit`, `help` and `?`, and say what Enter does in every prompt.
7. **Add an undo for the plan** (a short "recently cleared" list in the menu), and announce plan expiry.
8. **Define who it is for and write the employee announcement.** Choose "start my workday" as the job and say it in one sentence in the README and the first screen.
9. **Add a voluntary, person-controlled signal** (a copyable day-7 summary) and a scheduled day-14 check-in, so you can measure retention without telemetry.

## Retention feature to build this round: a private "My list" with carry-forward and a quiet weekly look-back

**What it is.**
- Replace the single plan with a short list of up to 3 items.
- Anything not finished carries forward to tomorrow in one keypress ("Keep these 2? Enter = yes").
- Once a week, on the first visit of the week, show a private, plain-text look-back: "Last 7 days: you opened it on 5 days and finished 6 things. Biggest one: Send the invoice."
- Keep it all local, visible to the person only, and deletable with one menu choice. It stays outside any report to IT or managers. The no-network rule stays unchanged.

**Why the person would come back because of it.**
- Their unfinished work lives here, so opening it becomes the quickest way to answer "what was I doing?" That is a daily reason that no generic tip can give.
- It costs less each day, because carrying forward is one key, and it speeds up as the list gets used. That is the faster second session.
- The weekly look-back is a reward that only exists if they used it, so skipping a week means missing something specific that is theirs. It is warm, not guilt: no missed-day wording, and it works with any pattern of use.
- Their history gives them a personal switching cost. After a month, leaving means losing a record of what they did.

**How it fits your principles.** The design record rejected "any record of whether plans were done" because it felt like being checked on at work. That risk comes from who can see the data, not from the data existing. Keep it private and local, make it visible in menu option 1, keep the delete option, and say so on the screen in one line ("Only you can see this. It never leaves this PC.").

## Accessibility

# Accessibility review: hello-world 1.11.0 (WCAG 2.2 AA)

**Scope and limits.** The "Developer's notes on this change" section in the packet is empty, so I can't tell what this change was meant to do. I reviewed the whole repository as it stands. CHANGELOG.md, BACKLOG.md and reviews/ are named in the README but were not in the packet, so I did not review them. I did not run anything. Findings come from reading the code, tests and docs.

The interfaces are a Windows console program (hello.py), PowerShell installer and uninstaller output, CLI help, and Markdown docs. There is no GUI, no HTML, no motion and no timeouts. Several decisions are good and should stay:
- Linear plain text with no redrawing (2.3.3).
- Enter alone always works (2.1.1).
- No time limits (2.2.1).
- State is written in words, such as "(now on)" and "(now off)" (1.4.1).
- An unambiguous date format.
- Messages state their outcomes: "Kept for today.", "Left as it was.".
- The window title is set to "hello-world" (2.4.2).
- No retyping when a plan is kept (3.3.7).
- `--plain` and `--help` give a non-interactive path.
- The session never closes before the person presses Enter, except after a second wrong answer (see Medium 1).

There is no Critical finding. No control is unreachable by keyboard.

## High

**H1. The screen-reader claim is unverified, and it is the headline accessibility claim. (4.1.2, 1.3.1, 4.1.3, release gate)**
- README.md says "It has not been tried with a real screen reader yet."
- PLAN.md and README.md still assert "a screen reader reads it in order" and list it as Done.
- Docs and tests only prove things that are easy to check: ASCII output, 72-column lines, and no color.
- The following have never been checked with NVDA, JAWS or Narrator, in either conhost or Windows Terminal:
  - How `input()` prompts are announced. Every prompt ends in ` > `, which many screen readers read as "greater than".
  - Whether multi-line prompts are read in full. The plan prompt embeds a newline: `"What is one thing...?\n(Press Enter to skip) > "`.
  - Whether the output that appears before a prompt is announced.
  - Whether the window closing on Enter loses context.
- Fix:
  - Run a scripted pass of a first run, a follow-up day, the menu, `--help`, `--stats` and the installer with at least NVDA and Narrator.
  - Record the result in PLAN.md "Not tested".
  - Until that is done, change the Done wording to "designed for, not yet verified".
  - Consider ending prompts with ": " instead of " > ".

## Medium

**M1. Error identification and recovery at the final prompt. (3.3.1, 3.3.3)**
- `"That was not one of the choices."` does not say what the choices are or echo what was typed.
- The second wrong entry prints "Closing now. Nothing was changed." and then ends the session.
- Screen-reader and switch users make typos more often. Two typos ending the session is harsh, and it differs from the menu, which loops until Enter.
- Fix:
  - Say `That was not one of the choices. Type plan, menu, or press Enter to close.`
  - Echo the typed word, shortened.
  - Loop until Enter, as the menu does.

**M2. Hard-wrapped text at a fixed 72 columns breaks for low-vision users. (1.4.10 Reflow, applied by analogy)**
- `wrapped()`, `indent()`, the first-run welcome and the damaged-file notice all wrap at 72 or hard-code line breaks.
- The welcome is seven separate `say()` lines. A user who enlarges the console font has fewer than 72 columns. Each line then wraps again and leaves ragged half-lines that are tiring to read.
- Fix:
  - Use `shutil.get_terminal_size().columns - 1`, capped at 72, for every wrap.
  - Wrap the welcome through `textwrap.fill`.
  - Keep the 72-column test, but run it with the width forced to 72.

**M3. Menu option 1 and `--stats` dump raw JSON of up to 400 dates. (1.3.1, 2.4.6, screen-reader flow)**
- `show_saved` prints `json.dumps(..., indent=2)` after the plain summary.
- `visits` can hold up to 400 dates, one per line. That adds brackets and quotes and up to about 400 lines to listen to.
- Fix:
  - Keep the summary lines.
  - Show the last 7 dates and the settings in sentences. Example: `In-a-row line: shown.`
  - Offer the full file only on request, for example `--stats --full`.

**M4. Installer progress depends on a progress bar and on long silences. (4.1.3 Status Messages)**
- Permission checks "can take several minutes". The only mid-check feedback is `Write-Progress`, which screen readers announce inconsistently.
- `$ProgressPreference = 'SilentlyContinue'` is set at step 4 and never restored. That hides the bar for the second `Assert-AdminOnlyTree` call at step 5, and it persists in the admin's window.
- Fix:
  - Print a plain `Write-Info` line every N items, for example every 2000. Example: `Checked 2000 items so far`.
  - Save and restore `$ProgressPreference` in `Restore-Window`.

**M5. The installer's status lines rely on ANSI/console colors that may not have enough contrast. (1.4.3, 1.4.1)**
- Cyan step lines and green success lines are unreadable on light console themes, at roughly 1.5:1 and under 3:1.
- Red on the legacy blue PowerShell background is about 3.9:1, which is below 4.5:1.
- Meaning is also carried by text such as "FAILED:" and "[n/6]", so this is not color-only. The "Installed hello-world ..." result line has no prefix, so a user who cannot see the green may miss that it is the result.
- Fix:
  - Drop `-ForegroundColor` for steps and results, or use it only as an addition.
  - Prefix the result line, for example `SUCCESS:` or `RESULT:`.
  - Honor `NO_COLOR`.

## Low

**L1. Prompts that accept unlisted answers. (3.3.2, 3.3.1)**
- "Keep it for today? (y/n)" keeps the plan on Enter and on any answer that is not a recognized "no". Typing `nn` meaning no keeps it. The prompt does not say Enter means yes.
- The delete confirmation `(y/n)` does not say Enter cancels.
- `is_yes` accepts "done" for the destructive `reset`. Use `STRICT_YES` there.
- Fix: label the defaults, for example `(y/n, Enter = keep)` and `(y/n, Enter = cancel)`.

**L2. Non-English plan text can become `?`. (1.1.1/3.1.2 intent, perceivable language)**
- Output is reconfigured with `errors="replace"`, so characters the console cannot show turn into `?`, which loses information.
- README admits this.
- Fix: on Windows set the console output code page to UTF-8 where possible, and say so in the README.

**L3. The sign-in launcher opens a window at sign-in. (3.2.1 On Focus)**
- It is opt-in and off by default, which is good.
- The window takes focus while a screen reader may still be starting.
- The launcher .cmd briefly flashes its own console.
- Fix: keep the opt-in. Add one line to the offer text, such as "It opens a window when you sign in". Consider `start /min` for the launcher shell.

**L4. Bare failure messages. (3.3.3)**
- `hello.py: something went wrong (ValueError). Contact IT.` goes to stderr with no action the person can take, and no log is written.
- Fix: add one line saying what was affected and what is safe, such as "Nothing was changed."

**L5. The shortcut and Apps icon is python.exe's icon, and the program name is the unexplained "hello-world". (1.1.1, 2.4.6)**
- Not wrong, since the name is text and the Description is set, but non-technical users may read it as a system tool.
- Fix: set a friendlier DisplayName or shortcut label, for example "hello-world (daily thought)".

**L6. `--help` gaps. (3.3.2)**
- There is no `--version`.
- Help is reachable in the program only through the menu.
- Add a one-line `--version`. Print "Type menu, then 5, for help" on the first screen. The first-run text already covers "plan or menu".

## Ship this round (minimum)

Ship these three changes together. They are small and testable:
1. Fix M1: list the valid choices in the error message, echo the typed word, and stop closing the session after two wrong entries.
2. Fix M2: wrap to the terminal width, capped at 72, including the first-run welcome.
3. Fix M3: replace the raw JSON dump with a short plain-language summary.

Also change the README, PLAN and docs wording from "screen reader reads it in order" to "designed for, not yet tested" until the H1 screen-reader pass is done.

Files reviewed: [packet file] (all 2845 lines).
