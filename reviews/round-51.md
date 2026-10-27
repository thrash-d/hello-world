# Round 51 review

- Date: 2026-10-27
- Commit reviewed: 13c83f7 (main, version 1.67.0). The fixes below are in 1.68.0.
- Agents: one reviewer, plus the six sitting personas. The October panel and every persona retired in round 50 were not in the room and they did not vote. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- Reed Mallory led this round. He does not veto. Nothing already in the program was removed. What he asked to harden was hardened. What he signed as residual stays, and the sign-off says so.

## Part 1: findings

| # | Severity | Where | What | Status |
| --- | --- | --- | --- | --- |
| 1 | High | `server/counts_server.py` reminder thread | One push address with a space or a control character raised `InvalidURL` and ended the only thread that sends reminders | Fixed |
| 2 | Medium | `PUT /v1/sync/<label>` | A stored copy could be replaced by a PUT that sent no `If-Match` | Fixed |
| 3 | Medium | counts data folder, sync files, day files | Created at the process umask, often `0755` / `0644`, so another account could list sync labels and read exact tip counts | Fixed |
| 4 | Medium | `hello.py` handoff | A symlink in the shared handoff folder was followed on read and on write. The temp name used the process id | Fixed, with a Windows residual |
| 5 | Low | `notes.json`, `errors.log` | `open()` followed a symlink of that name | Fixed |
| 6 | Low | `phone/sw.js` | A successful GET, including after a redirect, was stored under the address that was asked for | Fixed |
| 7 | Low | phone page from the counts server | No `nosniff`, no referrer policy, no content security policy, no frame denial | Fixed on that server. Sync keys stay in `localStorage` |
| 8 | Low | `feature-audit.jsonl` | A streak-note upload was offered and the ledger still said `network` false | Fixed. The plan is not on the line |
| 9 | Low | VAPID `es256_sign` | About half of the signatures used the high `s`. The low form is the same signature | Fixed |
| 10 | Low | growth POST and push PUT | Nested JSON inside the body cap raised `RecursionError`, which is not `ValueError` | Fixed |
| 11 | Low | P-256 multiply | Not constant-time | Accepted. Not rewritten |
| 12 | Low | `uninstall.ps1` | Rechecks the notes folder, then deletes by path. A junction swapped in after the check can still be followed | Accepted. This VM is Linux. Round 50 already recorded it |
| 13 | Info | sync encryption and push signing | This sheet is not the outside review `TODO.md` still lists | Accepted. Reed's name is not on "we had it audited" |

### High

1. A push registration whose URL contained a space or a control character stopped every phone's reminder. `push_address_ok` looked at the host after `urlsplit`. `https://fcm.googleapis.com/v1/a b` and a carriage return in the path still had the host `fcm.googleapis.com`, so the address was stored. `urllib` then raises `http.client.InvalidURL`. That class extends `HTTPException`, not `OSError` and not `ValueError`. `Push.send` did not catch it. `Push.run` caught only `OSError`. That thread is the only one that sends. Anyone who can `PUT /v1/push/<32 hex they choose>` could plant the address. Fixed: the address check refuses a non-string, an empty string, a string longer than 1000 characters, any character below space, DEL, a backslash, and `#`, and it still refuses a user name, a password, a fragment, and a host that is not on the push allowlist. `Push.send` returns 0 on any other exception. `Push.run` catches `Exception`, so one bad file cannot end the thread. `Push.due` drops a registration that still fails the address check, and only when the file still names that address.

### Medium

2. The PC and the phone already send `If-Match` (or the word `missing` when they have no copy). The server ignored a missing header when a file was already there, and the new body replaced it. A household put already refused a missing tag. Fixed: if a regular file is already stored, a PUT with no `If-Match` answers 428 `{"error": "If-Match required"}` and writes one `security-audit.jsonl` line (`sync_precondition`). A wrong tag is still 412. Creating a copy still allows no header, or `missing`. A symlink at that name is not read. The link is removed and a new file is written in its place. The file it pointed at is left alone.

3. Round 50 tightened the growth folder to `0700` and left the rest of the counts directory at the umask. `os.makedirs` defaults to `0o777`, which umask `022` turns into `0755`. `open()` defaults to `0o666`, which becomes `0644`. Another account on the machine could list the 64-hex sync labels and read the exact tip counts. The public page rounds those counts and says "a few" below 10. The file did not. Fixed: the data directory and the sync directory are `0700`. Sync blobs, day files, and the server's audit line are `0600`. A symlink named `sync` is removed (the link only) and replaced with a real directory. A day file that is a symlink is not read, and a new tip replaces the link. `chmod` is not called on the operator's `--data` directory when that path itself is a symlink, because `chmod` follows links.

4. The shared handoff folder (on Windows, the installer's ProgramData folder, which other users of that PC can modify) followed a symlink named `handoff.json`. The temporary file was `handoff.json.<pid>.tmp`, which another user of that folder could guess. Fixed: the read returns an empty list when the name is a symlink. The write uses `os.urandom` in the temp name, `O_EXCL`, and `O_NOFOLLOW` where the platform has that flag, mode `0o666` so the shared folder's own permissions still decide who can read the notes. A destination that is a symlink is unlinked (the link only) before replace. Checked: a link to a file that said "keep me" was replaced by a real `handoff.json`, and the other file still said "keep me". Residual: Windows has no `O_NOFOLLOW` (the flag is 0 there), so a swap between the check and the open can still be followed. The handoff file is not forced to `0600`. Other people on that PC have to be able to read it. The handoff lock stays `0666` for the same reason. The notes lock stays `0600`.

### Low

5. `load()` followed a symlink named `notes.json`. `log_error` followed one named `errors.log`. The notes directory is already `0700`, so another user cannot plant that link. A process that can write the directory still could. Fixed: a symlink notes file is not read, and saving is off for that run. A symlink `errors.log`, or a notes directory that is itself a symlink, is not written. Rotation to `.old` is skipped when either name is a link. The private write uses `O_NOFOLLOW` and `fchmod` `0600`.

6. The service worker cached any successful GET except `/v1/`, including a redirected response, under the original URL, and served that copy with no signal. Fixed: only GET, only this origin, only `index.html`, `app.js`, `content.js`, `sw.js`, `manifest.webmanifest`, `icon.svg`, or the directory itself, with no query string. The stored response has to be `ok`, type `basic`, not redirected, and the final URL has to be one of those files too. The cache name is `hello-world-phone-v14`.

7. The phone page served by the counts server sent no `X-Content-Type-Options`, no `Referrer-Policy`, no `Content-Security-Policy`, and no `X-Frame-Options`. The sync label is in the URL, so a referrer would carry it. Fixed on answers from that server: `nosniff`, `no-referrer`, and, on `index.html` only, a content security policy and `X-Frame-Options: DENY`. The policy allows `blob:` for the plans export, `'self'` for scripts, and `connect-src` of `'self'`, any `https:` the person typed, and `http` only for `127.0.0.1` and `localhost`. A phone file that is a symlink is not served. The policy is a response header, not a `<meta>` tag, so opening the same files with `file://` does not inherit a `'self'` policy that would break that open. `index.html` also has `<meta name="referrer" content="no-referrer">`. Sync keys remain in `localStorage` on the origin that served `app.js`. The policy reduces what a script on that page can do. It does not move the keys. Round 50 left that storage as it was. Delete everything on the phone still clears it, and it also clears `hello-world-security-audit`.

8. `growth_flush` offered a batch to the upload address and `feature_audit` was only called from the jokes and the stubs, all with `network` false. A reader of the ledger could say nothing had left. Fixed: after the immediate retry pair, one line is appended for that batch: `feature` `growth_upload`, `network` true, `host` (the host only, 200 characters), `result` (20 characters), and `n` when it is an int from 0 to 1000 and not a bool. No plan text and no client id. Against the placeholder the line is `host` `insights.example.invalid`, `result` `retry`. The phone writes a short note in `hello-world-security-audit` (time, event, host, result, count) and removes it with delete everything. Changing the upload box writes a `growth_server` note with the host. The notes folder is not created just to hold a ledger line. If the folder is a symlink, the line is not written.

9. `es256_sign` returned `s` as computed. For this curve, `s` and `N - s` are the same signature. About half of the values sit above `N // 2`. Some verifiers reject that form. This program's own `es256_verify` accepts either. Fixed: when `s > N // 2`, store `N - s`. Twenty signatures from one key all verified, and each `s` was at most `N // 2`. This is the encoding. It is not a claim that a push service was dropping reminders.

10. `json.loads` on a body under the 64KB cap can raise `RecursionError` on nested arrays. The growth POST and the push PUT caught `ValueError` only, so the exception left the handler. Fixed: those loads catch `RecursionError` as well and answer 400. The VAPID file load does the same. A stored scalar outside `1 .. N-1` is replaced with a new key.

### Accepted, and signed

11. The P-256 scalar multiply is ordinary Python integers. It is not constant-time. Rewriting the curve was not this round. The sign-off names it.

12. `uninstall.ps1` rechecks the notes folder and then deletes by path. A junction swapped in after the check can still be followed. Round 50 recorded the same race. This VM is Linux. The script was not changed. The install scripts are unsigned. Signing them is the owner's step in `docs/ENTERPRISE.md`.

13. `TODO.md` still asks for an outside review of the sync encryption and of the push signing before they are promoted widely. This file is Reed Mallory's sheet. It is not that review. PBKDF2-SHA256 (200,000 rounds, the existing salts) and HMAC-SHA256 were left as they are. The low-`s` change is the only change to the signature bytes.

### Also looked at, and not a finding

- `os.open(..., 0o600)` is not world-readable under umask `022`. The bits umask strips are the group and other bits, and `0o600` has none of those. `0o700` stays `0700`. `0o666` becomes `0644`. The bug was the paths that used the default `0666` / `0777`, not the paths that already asked for `0600`. `tools/pro_keys.py` was left as it is for that reason.
- The growth URL check still rejects a user name, a backslash, and whitespace. `http://127.0.0.1:9@evil.com` is a user name of `127.0.0.1` and a host of `evil.com`, and it falls back to the placeholder. `https` to a host an operator typed is still allowed. Redirects on that upload are still not followed.
- The phone builds text with `textContent`. The CSV export still prefixes a formula character. `git` is still an argument list. The repair, Pro+, and Priority Hello amounts are still local stubs: `charged` false, `stub` true. No card form was added.
- A published tip is cached for about an hour. Replacing a day file with a symlink does not make `GET` return the symlink's target. `Counts.read` of that link is tip 0. The cached number can still be the one published before the swap.
- A private write closes the descriptor if `fchmod` fails after `open`. That close was added with the rest of the notes hardening.

### Not changed, and why

- Streak notes still exist. Reed did not ask to turn them off for the building. A person can still run `hello growth off`.
- The default upload is still `https://insights.example.invalid/v1/growth`.
- The kazoo, the duck line, and the $4.99 stub are still there. None of them gained a morning line or a printed line.
- Sync keys stay in `localStorage`. See finding 7.
- The sponsored line still shows when streak notes are on, gentle mode is off, and Pro+ is not set.
- A plan date on the phone is still only the shape. 31 February as a plan date is a string compare.
- A portable notes folder still has no Windows DACL. Unix mode `0600` is ignored there.
- Quiet uninstall still omits `-RemoveNotes` on purpose.
- No card form and no processor.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`, and `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite. Notes and the counts directory were only under temporary folders.

`push_address_ok("https://fcm.googleapis.com/v1/a b")` is false. The same URL with a carriage return in the path is false. `https://fcm.googleapis.com/fcm/send/abc` is true. `https://evil.example/push` is false. `https://updates.push.services.mozilla.com/wpush/v2/abc` is true. `Push.send` on the spaced URL returns 0. `Push.due` with a planted bad endpoint does not call `send`, and the file is removed.

Twenty `es256_sign` results from one key all have `s <= N // 2`, and `es256_verify` returns true for each.

On `127.0.0.1` with an ephemeral port: a `sync` symlink to `/tmp` is replaced by a real directory at `0700`. The file written there is `0600`. `/tmp/<label>` is not created. A first PUT with no `If-Match` is 200. A second PUT with no `If-Match` is 428 and the body is unchanged. A PUT with the current `ETag` is 200. A stale `If-Match` is 412. A day file after `POST` tip is `0600`. The data directory is `0700`. `Counts.read` through a day-file symlink returns tip 0. A `growth` name that is a symlink to `/tmp` becomes a real directory at `0700`. A sync file that is a symlink to a secret returns 404, and the secret is unchanged.

`hello.HOME` save: directory `0700`, `notes.json` `0600`. A `notes.json` symlink is not loaded (`can_save` is false; the target's streak is not taken). `write_handoff` replaces a symlink and leaves the target text in place.

One queued growth event, flushed at the placeholder, appends one line: feature `growth_upload`, version `1.68.0`, `network` true, `charged` false, `stub` false, host `insights.example.invalid`, result `retry`, `n` 1. The plan text `secret pills` stays in `growth-queue.json` and is not in that line. An empty queue writes no ledger line, because the flush returns before it.

Umask `022`: `makedirs(..., 0o700)` is `0700`, `open(..., 0o600)` is `0600`, `open(..., 0o666)` is `0644`.

Not run: pytest, the plain runner, ruff, PowerShell, the installer, a live public host, and NVDA. Edith did not sit with a screen reader this round, and this file does not say she did. Nothing was run on Windows. A raw-socket check that tried to feed a carriage return to `urllib` was abandoned. `http.client` rejects a space or a control in the path with `InvalidURL` before the bytes are written, and `push_address_ok` now rejects those characters first.

## Part 2: personas

The six sat on the program as it stood in 1.67.0. Nobody brought a new feature. Reed put a sheet on the table and asked each of them to initial the lines that touched their part. He does not veto. He wanted the sheet so that, later, the name on the finding is his and the name on the miss is not.

### Reed Mallory

Former Marine staff sergeant. He was a communications clerk, then he made slide decks for a contractor and started calling himself CISO. Mallory Assurance is him and a bookkeeper. He is loud about not being the one who gets named later. He is not a cryptographer. He signed the curve as "not constant-time, accepted" because someone would ask, and he did not want a blank cell.

- "Fine. Nothing comes out. The kazoo stays. The duck stays. The four ninety-nine stays. I am not the guy who killed a button."
- "If the reminder thread dies, they will say I was the security person in the room. So the thread does not die. Log it. Sign it. Next."
- "The ledger is the product. If an upload left and the line says network false, that line is a lie with my name next to it."

Sign-off sheet, as he read it back:

| Line | What the code does after 1.68.0 | His mark |
| --- | --- | --- |
| Kazoo | Prints. Does not save. Does not open a socket. Ledger, if the notes folder already exists, stays `network` false | Signed |
| Duck (`hello ai`) | Still says "This is not a model. Nothing was sent." `network` false | Signed. He will not sign the word model |
| Repair $2.99, Pro+ $9.99, Priority Hello $4.99 | Local stub. `charged` false. `stub` true. Written only after the notes save | Signed. Cash collected: $0 |
| Streak-note upload | One ledger line per batch offered. `network` true. Host and result recorded. No plan. No client id. Default host `insights.example.invalid` | Signed |
| Sync folder and day files | `0700` / `0600`. Symlink not followed | Signed |
| `If-Match` | Required once a copy exists. 428 if it is missing | Signed |
| Push thread | A bad address returns 0 and the thread continues | Signed |
| P-256 timing | Not constant-time | Accepted, signed as residual |
| Outside crypto review | Not this sheet | Refused to sign "audited" |
| Uninstall junction, unsigned scripts | Owner's step. Not changed here | Accepted, signed as residual |
| Phone sync keys in `localStorage` | Still there. The counts server now sends the policy and `nosniff` | Accepted, signed as residual |

He asked for `security-audit.jsonl` on the counts server (mode `0600`, capped, no address, no plan, no push URL) and for the phone's short note beside it. A missing `If-Match` and a sync symlink write a line. A flood of bad push addresses does not. He called the content security policy "the fence" and initialed it without reading `connect-src`. The fence is real. His description of it is not.

### Bex Calder

She films Unbox The Future from a spare bedroom in Tucson. She calls any header "the cloud" until someone reads her the host.

- "You put a firewall in the cloud. That's the content thing. I can say we hardened it."
- "The AI button is still a button. Don't take the button."

She initialed the kazoo and the duck because both still exist. She asked whether the fence talks to a model. It does not. She nodded anyway. She did not ask for a new control on the morning screen.

### Vance Harlow

Staff salary is not on his sheet. He read the new ledger line and did not like `network` true.

- "A line that admits the notes were offered is a line a buyer can wave at me. The cash from the stubs is still zero. Leave the prices on the slide."
- "Do not put four ninety-nine on the paper. Edith already won that, and I am not reopening a vote I lost in order to lose it again."

He initialed the stubs as `charged` false. He initialed the upload line because Reed would not sign a ledger that hid it, and Vance would rather have the host say `insights.example.invalid` than have a blank he cannot explain. The $5 Pro key and the $8 household key still need the owner's store. This round does not call it.

### Nico Paredes

He checked the joke, because a hardening round is where a joke quietly starts sending.

- "Kazoo still doesn't send. If the ledger says network false, good. If you add a beep that phones home, it isn't a kazoo."
- "bwap bwap is not a finding."

He initialed the kazoo and the duck. He did not ask for a new joke. He said the 428 is fine as long as the phone already sends the tag, which it does.

### Amina Soule

She opens the bakery at 4:10. She asked one question.

- "Is there a new question before the bread?"

There is not. The morning screen is the same screen. She initialed that and went back to the ovens. She did not read the push allowlist.

### Edith Cho

She reads the printed page to her sister on Sundays. She asked to see the page and the price.

- "Nothing new on the paper. I will not read a price, and I will not read a host name."
- "If the sentence still says it is not a model, I can still read that one. You did not change it. Good."

The fridge section is unchanged. Print still hides the rest. She did not sit with a screen reader. She initialed "no new line" and did not initial the curve.

## What shipped

Hardening only. Version 1.68.0.

The reminder thread survives a push address that `urllib` will not send. A stored sync copy requires `If-Match`. Counts, sync, and day files are `0700` or `0600`, and a symlink is not followed. Handoff and the notes file are not opened through a link. The service worker caches only this app's files, and not after a redirect. The counts server sends `nosniff`, `no-referrer`, and a content security policy on the phone page. A streak-note upload appends one ledger line with the host and the result, and without the plan. VAPID signatures use the low `s`. Nested JSON that used to raise `RecursionError` is a 400.

`hello kazoo`, `hello ai`, and `hello priority` behave as they did in 1.67.0. The morning screen does not gain a line. The printed page does not gain a line. The default upload is still the placeholder.

## What did not ship

- Removing streak notes, sync, reminders, the kazoo, the duck, or the stubs.
- A new morning question, or a new line on the printed page.
- A card form, a processor, or any charge that leaves the machine.
- A rewrite of the curve into constant-time arithmetic.
- The outside review of the sync encryption and the push signing.
- A fix for the uninstall junction race, or Authenticode on the scripts.
- Moving sync keys out of `localStorage`.

## Outcome

One high finding is fixed. Three medium findings are fixed, one of them with a Windows residual that is on the sign-off. Six low findings are fixed. Three items are accepted and named so they are not a blank. Reed Mallory did not veto a feature. He signed the sheet, including the cells he does not understand, and he refused to sign the words "we had it audited." Vance Harlow's defendable cash from the stubs is still $0. The upload address was not changed.
