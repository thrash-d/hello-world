# Round 52 review

- Date: 2026-10-27
- Commit reviewed: 5b9d316 (main, version 1.68.0, pull request 102). The fixes below are in 1.69.0.
- Agents: one reviewer, plus the six sitting personas. The October panel and every persona retired in round 50 were not in the room and they did not vote. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- Reed Mallory led this round. He does not veto. Nothing already in the program was removed. He accepts no residual. A cell is fixed, or it is mitigated and the name on it is not his.

## Part 1: findings

Round 51 left three cells marked accepted, and the sign-off named more residuals beside them. Those cells are the findings of this round. None of them is accepted.

| # | Severity | Where | What round 51 left | Status in 1.69.0 |
| --- | --- | --- | --- | --- |
| 1 | Low | `server/counts_server.py` P-256 | Scalar multiply in ordinary Python. Signed "accepted, not rewritten" | Fixed on the shipping path. The ladder is off, and the gate is not his |
| 2 | Low | `uninstall.ps1` | Recheck, then delete by path. A junction swapped in after the check can be followed | Fixed. If the handle code will not load, the folder is left and the operator holds it |
| 3 | Info | install scripts | Unsigned. Signed as the owner's step | Mitigated. The signing process is in the tree. An unsigned run names the deploying organization |
| 4 | Info | sync encryption and push signing | `TODO.md` still asked for an outside review. He refused to sign "audited" and the cell was still marked accepted | Internal review written. The outside signature is transferred. He still does not sign "audited" |
| 5 | Low | phone sync keys | `localStorage` on the origin that served `app.js`. Signed as residual | Fixed for the stored form. A raw fallback needs someone else's name. A script already on the origin is that host's |
| 6 | Medium | Windows open of handoff, notes, counts secrets | `O_NOFOLLOW` is 0 on Windows, so a swap between the check and the open could be followed | Fixed. The open itself refuses a reparse point |
| 7 | Low | portable notes folder | No Windows access list. Unix mode `0600` is ignored there | Mitigated. Owner and SYSTEM when the volume allows it. A refusal writes a transfer file for the operator |
| 8 | Low | test launcher `.cmd` | `"` and `%` were refused. `!` was not, and delayed expansion would expand it | Fixed. `!` is refused with the other two. The shipping launcher is still the registry value |

### Fixed on the path that ships

1. `es256_sign`, `es256_verify`, and `p256_public` call libcrypto (NID 415, prime256v1) when it loads: `EC_POINT_mul`, `ECDSA_do_sign`, `ECDSA_do_verify`. The low `s` is chosen with `BN_cmp` against the order shifted once, then `BN_sub`, and the choice does not depend on a Python branch over the secret. `p256_backend()` returns `openssl`. Checked here: the NIST scalar `C9AFA9…6721` produces the public point whose X starts `60fed4ba` and whose Y starts `7903fe10`. Five signatures of one message all have `s` at most `N/2`, and `es256_verify` accepts each.

The pure-Python ladder is still in the file. It is a fixed 256-step complete addition (Renes–Costello–Batina, add-2015-rcb, `a = -3`). CPython's integers are not constant-time, so the ladder is not the shipping path. It runs only when `HELLO_P256_VARIABLE_TIME` is `1` and `HELLO_P256_TRANSFER` names a regular file, not a symlink, of at most 4000 bytes, with `accepts: variable-time-p256` and an acceptor who is not Reed Mallory. A name that is his, or that starts with his, does not open the gate. With the gate open and libcrypto present, the backend stays `openssl`. With libcrypto missing and the gate shut, sign raises `P256Unavailable` and verify returns false. A server started with `--remind` in that state fails at startup rather than sign with the ladder. A server without `--remind` still starts. The paper is `docs/transfers/p256-variable-time.md`. He does not accept the ladder.

2. `uninstall.ps1`, `uninstall-user.ps1`, and `install.ps1` delete through `HelloNoFollow` (`tools/nofollow.ps1`, embedded, because an installed copy has no `tools` folder). The directory is opened with `CreateFileW` and `FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS`, without `FILE_SHARE_DELETE`, so the opened object cannot be swapped out from under the handle. Children are opened with `NtCreateFile` relative to that directory and `FILE_OPEN_REPARSE_POINT`. A reparse point is deleted as the node, not followed. `Remove-Tree` throws if `Add-Type` fails, and the path is not then deleted with `rmdir`. `Remove-UserNotes` deletes only `notes.json`, `notes.lock`, `errors.log`, `errors.log.old`, and `notes.json.*` through that chain, and leaves the rest. `uninstall-user.ps1 -RemoveNotes` still removes the notes folder, through the same handle. This VM is Linux. The C# was not compiled here. The failure path is the operator's: the folder stays, and the warning says Reed Mallory has not accepted a path delete.

6. `hello.open_nofollow` sets `O_NOFOLLOW` on POSIX. On Windows it opens with `CreateFileW` and `FILE_FLAG_OPEN_REPARSE_POINT` and refuses `FILE_ATTRIBUTE_REPARSE_POINT`, then keeps the descriptor. The same two functions are in `server/counts_server.py`. They are used for the notes file, `errors.log`, the local streak-note files, the growth queue, the handoff read and the handoff temp write, the test launcher temp, the notes lock, the counts server's private files, the VAPID key, push registration reads, sync reads, the sync temp write, the growth day file, and `security-audit.jsonl`. Checked: a symlink named `notes.json` raised errno 40 and the target still said `keep me`. A lock that was a symlink to a file saying `secret` was replaced by a real lock file, and the target still said `secret`. The handoff file stays mode `0666`. Other people on that PC have to be able to read it. The flag on the final component does not walk intermediate junctions; `OpenChain` refuses those at open time, which is the same conservative result as the old folder check.

8. `launcher_command` returns `None` when the script path or `window_python()` contains `"`, `%`, or `!`. The shipping launcher is the `HKCU` Run value. The `.cmd` is the test stand-in, and delayed expansion would have expanded `!` there. `write_launcher_file` creates that file with `O_EXCL` through `open_nofollow`.

### Mitigated, and the name is not his

3. The git blobs are not Authenticode-signed. This machine has no `signtool` and no Windows PowerShell, so they were not signed here. `tools/sign-scripts.ps1` signs `install.ps1`, `uninstall.ps1`, `install-user.ps1`, and `uninstall-user.ps1` with SHA-256, timestamps when asked, and throws unless `Get-AuthenticodeSignature` returns `Valid`. `tools/build-package.ps1 -CertificateThumbprint` signs the same four before hashing. A certificate subject that names Reed Mallory is refused. He is not the signer.

An unsigned run does not refuse to install. Refusing it would remove the documented clone install, and an extra file in the package would change the hash the installer already checks. The script warns and names the acceptor: `-UnsignedAcceptor`, or `HELLO_UNSIGNED_ACCEPTOR`, or the words `deploying organization`. A name that is Reed Mallory, or that starts with Reed Mallory, is replaced with `deploying organization`. The package build throws if that parameter is his name. The paper is `docs/transfers/code-signing.md`. `docs/ENTERPRISE.md` points at both commands. CI's throwaway-certificate package is unchanged in shape: the file list in `SHA256SUMS` was not extended.

4. `docs/SYNC-CRYPTO-REVIEW.md` records the scheme that already ships. PBKDF2-SHA256, 200,000 rounds, salt `hello-world sync v1` (household salt unchanged), 96 bytes split into label, encryption key, and MAC key. HMAC-SHA256 counter mode, then HMAC-SHA256 over `v1 || nonce || ciphertext`, compared with `hmac.compare_digest`. The derivation, the salts, the round count, and the layout were not changed, so an old blob and a cached phone still open. What was added, and does not change a valid blob: a blob over 64,000 bytes is rejected, a key that is not 32 bytes is rejected, and a plaintext that is not UTF-8 JSON object is rejected.

Checked against that file, code `aaaaa-aaaaa-aaaaa-aaaaa-aaaaa`, nonce 16 zero bytes: label `0063908f…f3dc`, and the blob opens to `{"v": 1, "text": "bread"}`. A tag one byte short does not open. A blob over 64,000 bytes does not open. A short key raises `ValueError` on seal.

The counts server prints `sync review: internal-only` unless `HELLO_SYNC_EXTERNAL_REVIEW` points at a regular file with `accepts: sync-external-review` and an acceptor who is not Reed Mallory. A symlink is not that file. Checked: his name does not flip P-256; Dana Okonkwo's file does, and the backend stayed `openssl`; the sync file flipped the review to `external`; a symlink to that file stayed `internal-only`. The screen still says this encryption has not had an outside audit. He would not let that sentence be rewritten into a claim. The outside signature is `docs/transfers/sync-external-review.md`. Wide promotion stays on the deploying organization's list in `TODO.md`.

5. The phone keeps sync keys in IndexedDB `hello-world-sync-keys`, store `secrets`, as non-extractable HMAC `CryptoKey`s. Personal id `personal`. Household id `house:<label>`. After that write, `localStorage` key `hello-world-sync` is removed. `save()` does not write household key bytes into the notes. It writes `{label, locked:"idb"}` or `locked:"memory"`. The cache name is `hello-world-phone-v15`.

If IndexedDB cannot be opened, the keys stay in memory for the visit and the raw copy is removed, unless `hello-world-sync-raw-acceptor` is a name that is not Reed Mallory. That name is the acceptor of the raw arrays. His name does not keep them. A script that already runs on the origin can still use a non-extractable key. The content security policy from 1.68.0 is the fence on pages the counts server sends. The residual is the host of `app.js`, written in `docs/transfers/phone-sync-keys.md`. It is not his.

7. `seal_owner_dir` and `seal_owner_fd` set a protected access list for the current user and SYSTEM on the notes folder, the error log, the local streak-note files, and, when the counts server is on Windows, on the private files it writes. Off Windows the call is a no-op and returns true; Unix mode remains the control. The handoff folder is not passed in. A volume that refuses the list still gets the notes, and `dacl-transfer.txt` is written once, with a blank `acceptor:` line and the sentence that Reed Mallory does not accept the residual. The operator who keeps the folder writes their name. The paper is `docs/transfers/portable-dacl.md`. This VM is Linux. The access-list calls were not executed.

### Also looked at, and not a finding

- Quiet uninstall still omits `-RemoveNotes`. That is the product. Notes stay unless the operator asks. He did not flip it.
- Streak notes, sync, reminders, the kazoo, the duck line, and the three stub prices are still there. `charged` is still false. No card form was added.
- The default upload is still `https://insights.example.invalid/v1/growth`.
- The morning screen has no new line. The printed page has no new line. The sentence that says the encryption has not had an outside audit is the old sentence.
- The handoff lock stays group-writable on purpose. The notes lock is the one that asks for the owner list.

### Not changed, and why

- The sync construction was not replaced with a standard AEAD, and the round count was not raised. Either change would stop an existing copy from opening. The internal review says what that leaves, and it does not call the result audited.
- Install from a clone was not refused for lack of a signature. The warning names someone else.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`. `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite. Notes were only under temporary folders.

`p256_backend()` is `openssl`. `sync_review_status()` is `internal-only` with no transfer file. The sync vector in `docs/SYNC-CRYPTO-REVIEW.md` opens to `{v: 1, text: bread}`. A short tag and an oversized blob return `None`. `seal_sync` on a short key raises `ValueError`. Five `es256_sign` results verify, and each `s` is at most `N/2`. The NIST public point matches the bytes recorded above. A symlink read raises errno 40 and leaves the target. A symlink lock is replaced and leaves the target. Reed Mallory's transfer file does not enable the ladder. Dana Okonkwo's does, and the backend stays `openssl` while libcrypto is loaded. Her sync-review file returns `external`. A symlink to that file returns `internal-only`.

Not run: pytest, the plain runner, ruff, PowerShell, `Add-Type`, Authenticode, the installer, a Windows access list, a live public host, and NVDA. Edith did not sit with a screen reader this round, and this file does not say she did. Nothing was run on Windows. The C# in `tools/nofollow.ps1` was not compiled.

## Part 2: personas

The six sat on the program as it stood in 1.68.0, and on the sheet from round 51. Reed put that sheet back on the table and crossed out every cell that said accepted. He does not veto. He wanted the new sheet so that, later, nobody can say he agreed to carry a risk.

### Reed Mallory

Former Marine staff sergeant. He was a communications clerk, then he made slide decks for a contractor and started calling himself CISO. Mallory Assurance is him and a bookkeeper. He is loud about not being the one who gets named later. He is not a cryptographer. Round 51 taught him that "accepted" is still his name on a thing that can blame him. He will not write that word again.

- "Accepted means I signed it. I don't sign a hole. Fix it, or put someone else's name on it. Mine stays off."
- "The curve is OpenSSL's or it does not run. The ladder is a file. The file needs a name, and the name is not Reed Mallory."
- "I will not sign audited. The screen still says there was no outside audit. Leave that sentence alone. If I change it, I just signed it."
- "If the handle will not load, the folder stays. The operator moves it. I don't follow a junction so the log can say I tried."

Sign-off sheet, as he read it back. The word accepted is not on it.

| Line | What the code does after 1.69.0 | His mark |
| --- | --- | --- |
| Kazoo | Prints. Does not save. Does not open a socket | Signed. Still not a finding |
| Duck (`hello ai`) | Still says it is not a model. Nothing was sent | Signed. He will not sign the word model |
| Repair $2.99, Pro+ $9.99, Priority Hello $4.99 | Local stub. `charged` false. `stub` true | Signed. Cash collected: $0 |
| P-256 | libcrypto. Ladder off unless a transfer file names someone else | Fixed. He does not accept the ladder |
| Uninstall junction | Delete through the open directory. No path delete if that code will not load | Fixed. The leftover folder is the operator's |
| Unsigned scripts | `tools/sign-scripts.ps1` and the package thumbprint. Unsigned run names the deploying organization | Transferred. He is not the signer |
| Outside crypto review | Internal review on file. Screen still says no outside audit. `external` only with someone else's file | Transferred. Refused to sign "audited" |
| Phone sync keys | Non-extractable keys in IndexedDB. Raw copy only with someone else's name | Fixed. The same-origin script is the host's |
| Windows reparse point | The open refuses it, on notes, handoff, and the counts secrets | Fixed |
| Portable access list | Owner and SYSTEM, or `dacl-transfer.txt` for the operator | Transferred when the volume refuses |
| `!` in the test launcher | Refused, with `"` and `%` | Fixed |
| Quiet uninstall leaves notes | Still omits `-RemoveNotes` | Not a risk. He did not flip the product |
| Streak-note upload | Still the placeholder until an operator points it elsewhere | Signed. Host unchanged |

He initialed the OpenSSL line without reading `BN_cmp`. The line is real. His description of it was "the library does the math." The fence from round 51 is still the content security policy. He initialed it again without reading `connect-src`.

### Bex Calder

She films Unbox The Future from a spare bedroom in Tucson. She calls libcrypto "the cloud's lock" until someone reads her the word OpenSSL.

- "You put the lock in the real library. I can say we hardened the cloud."
- "Don't take the AI button. Don't take the kazoo. A transfer form is not a button."

She initialed the kazoo and the duck because both still exist. She asked whether the transfer file phones a model. It does not. She nodded anyway. She did not ask for a new control on the morning screen.

### Vance Harlow

Staff salary is not on his sheet. He read the transfer papers and looked for a price.

- "A form that names the deploying organization is a form a buyer can ask me to explain. The cash from the stubs is still zero. Leave the prices on the slide."
- "Do not put four ninety-nine on the transfer. Edith already won that."

He initialed the stubs as `charged` false. He initialed the unsigned-script line because the acceptor is the organization that deploys, which is a name he can point at, and because Reed would not leave the cell blank. The $5 Pro key and the $8 household key still need the owner's store. This round does not call it.

### Nico Paredes

He checked the joke, because a hardening round is where a joke quietly starts sending.

- "Kazoo still doesn't send. The bang in the launcher is not a joke. Good that it refuses it."
- "bwap bwap is not a finding, and a transfer file is not a sound."

He initialed the kazoo and the duck. He did not ask for a new joke.

### Amina Soule

She opens the bakery at 4:10. She asked one question.

- "Is there a new question before the bread?"

There is not. The morning screen is the same screen. She initialed that and went back to the ovens. She did not read the curve.

### Edith Cho

She reads the printed page to her sister on Sundays. She asked to see the page and the audit sentence.

- "Nothing new on the paper. I will not read a price, and I will not read a host name."
- "The sentence still says it has not had an outside audit. You did not change it into a claim. Good."

The fridge section is unchanged. Print still hides the rest. She did not sit with a screen reader. She initialed "no new line" and she initialed the unchanged audit sentence. She did not initial the curve.

## What shipped

Hardening only. Version 1.69.0.

P-256 goes through libcrypto. The ladder does not run unless an operator who is not Reed Mallory turns it on in writing. Uninstall deletes through an open directory handle and does not fall back to a path delete. The four install scripts have a signing command, and an unsigned run names the deploying organization. The sync scheme has an internal review, and the outside signature is a file he cannot sign. Phone sync keys are non-extractable browser keys. Windows opens of the notes, the handoff file, and the counts secrets refuse a reparse point. A notes folder on Windows asks for an owner-only access list, and a refusal writes the operator's transfer file. The test launcher refuses `!`.

`hello kazoo`, `hello ai`, and `hello priority` behave as they did in 1.68.0. The morning screen does not gain a line. The printed page does not gain a line. The default upload is still the placeholder. The screen still says the encryption has not had an outside audit.

## What did not ship

- Removing streak notes, sync, reminders, the kazoo, the duck, or the stubs.
- A new morning question, or a new line on the printed page.
- A card form, a processor, or any charge that leaves the machine.
- A claim that an outside lab reviewed the sync encryption.
- An Authenticode signature on the git blobs. This machine cannot make one.
- A compiled run of the uninstall C#, or a Windows access list. This machine is Linux.
- A change to the sync salts, the round count, or the blob layout.

## Outcome

Nothing on this sheet is accepted by Reed Mallory. Eight residuals from round 51 and from the scan of that sign-off are fixed, or mitigated and transferred onto the deploying organization, the operator who keeps the folder, or the host of the phone page. He did not veto a feature. He signed the sheet, including the cells he does not understand, and he refused to sign the word audited. Vance Harlow's defendable cash from the stubs is still $0. The upload address was not changed.
