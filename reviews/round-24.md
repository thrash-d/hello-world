# Round 24

- Date: 2026-10-01
- Commit reviewed: 9585b36 (version 1.5.7)
- Files reviewed: hello.py, install.ps1, test_hello.py, VERSION, plus the newest changelog entry as developer's notes

---

Review of 1.5.7. I found no Critical, High or Medium issues, and I did not run or parse anything. This is a read-through of the pasted text only.

Scope: `uninstall.ps1` was not included, so it is not covered here. The commit pin and the permission checks make its content part of what you trust, so it needs its own review pass.

**Critical / High / Medium:** none. Only comment-based help changed since 1.5.6. I re-read the logic as it stands and found no new defects in the following areas:
- the ACL checks, including the operator precedence in the `$others` pipeline, the `InheritOnly` skip, and the owner check;
- the commit and `hash-object` pin;
- the build-beside-and-swap flow with its rollback;
- the transcript and `finally` ordering;
- the `hello.py` exit-code handling and its tests.

**Low**
1. **Slow-check warning is not where the operator will see it.**
   - `.NOTES` now says the Git permission checks can take several minutes. The only message printed during the wait says "(this can take a minute)".
   - An operator who never runs `Get-Help` will see a silent window and may kill the run.
   - Fix, on the next code change: make that `Write-Host` line say "this can take several minutes on Git for Windows". Code and help then agree.
2. **Reinstall help sentence is hard to follow and risky to copy.**
   - The sentence is one long parenthetical with the command embedded: `Remove-Item -Recurse -Force $d, because git leaves read-only files in .git; $d is set by the example's first line...`.
   - A comma directly after `$d` is easy to paste into the shell. `$d,` would be parsed as an array.
   - Fix: put the removal on its own example line, e.g. `cd \` then `Remove-Item -Recurse -Force $d`, and explain afterward.
3. **Help parsing is unverified.**
   - There is no line starting with a `.KEYWORD` inside the text, and I see no stray `#>`, so it should parse.
   - I could not confirm it. Run `Get-Help .\install.ps1 -Full` once on Windows. This is your existing pilot item, so it is not a new finding.

**Info**
- The pinned Python URL and SHA-256 (3.14.8 embed-amd64) cannot be checked offline. A wrong hash fails closed. The pilot install will confirm both.
- Your declined items (BACKLOG, ProgramData\Git, the `HOME`/`.gitconfig` assumption, the pin reminder, design size) are reasonable. I am not reopening them.

**Verdict:** ready for the pilot workstation. Make the two help and message fixes on the next change, and run `Get-Help` plus a real install on one machine before rolling out to the other four.
