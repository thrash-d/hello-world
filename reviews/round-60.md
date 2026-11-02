# Round 60 review

- Date: 2026-11-02
- Commit reviewed: 3544ef0 (main, version 1.76.0, pull request 111). The fixes below are in 1.77.0.
- Agents: one reviewer, plus the six sitting personas. The October panel and every persona retired in round 50 were not in the room and they did not vote. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- Reed Mallory led this round. He does not veto. Nothing already in the program was removed. He accepts no residual. A cell is fixed, or it is mitigated and the name on it is not his.

## Part 1: findings

The room started from the program as it stood in 1.76.0. The two cells he has been transferring since round 57 were still open: a hex-encoded certificate subject, and a symbol that only looks like a space. The rest of the pass was the counts server, the phone, the install scripts, and the key tool.

| # | Severity | Where | What | Status in 1.77.0 |
| --- | --- | --- | --- | --- |
| 1 | Medium | name gate | A hex subject was not decoded. `CN=#0C0C52656564204D616C6C6F7279` is Reed Mallory in a UTF-8 BER string, and `Reed\20Mallory` is the same name with a `\HH` octet. The fold stripped the backslash and left the digits | Fixed |
| 2 | Medium | name gate | U+2800 between the two words is a braille blank, category So. NFKC leaves it. It is not a format character and not a space, so the fold did not treat it as one. U+3164 becomes U+1160 under NFKC and had the same hole. A Cyrillic `е` in Reed was a different name | Fixed |
| 3 | Medium | `server/counts_server.py` phone files | `open()` followed a symlink named `app.js`, and the file was read with no size cap | Fixed |
| 4 | Medium | counts server | A read was not counted. A connection that sent nothing held a thread. There was no cap on how many threads | Fixed |
| 5 | Low | sync and push writes | `may_write` counted a copy before the write landed. A failure left the quota high until the next sweep | Fixed |
| 6 | Low | growth address | `_server_url_ok` and `growthUrlOk` refused a few whitespace characters. A NUL in an otherwise https address still passed | Fixed |
| 7 | Low | `X-Forwarded-For` | With `--trust-proxy`, the last hop was used as the rate-limit key with no check that it was an address | Fixed |
| 8 | Low | request framing | `Transfer-Encoding` was ignored, and two `Content-Length` headers were not refused | Fixed |
| 9 | Low | response headers | `X-Frame-Options` and the content security policy were only on `index.html`. No permissions policy, no `Cross-Origin-Resource-Policy`, no `Cross-Origin-Opener-Policy`. The page policy had no `form-action` and no `frame-src` | Fixed |
| 10 | Low | `tools/pro_keys.py` | Reading the signing key used `open()`, which follows a symlink | Fixed |
| 11 | Low | sync GET | A file larger than 64,000 bytes was returned as a prefix of itself | Fixed |
| 12 | Info | TLS front end | This process speaks HTTP. `Strict-Transport-Security` on that socket does not protect the bytes, and the in-memory request counter clears on restart because a network address is not written to disk | Transferred. `docs/transfers/tls-front-end.md` |

### Fixed

1. `_reed_named`, `reedNamed`, and `Test-ReedMalloryName` decode the subject before the prefix check. `\HH` is one UTF-8 octet, so `Reed\20Mallory` is Reed Mallory. A value that starts with `#` and continues as hex is decoded as a BER string when the tag is UTF-8, Printable, Teletex, IA5, Visible, BMP, or Universal, and also as raw UTF-8 or UTF-16 when that text is readable. `CN=#0C0C52656564204D616C6C6F7279` is refused. `CN=#130C52656564204D616C6C6F7279` is refused. `CN=#0C0F6E6F742052656564204D616C6C6F7279` is the BER string `not Reed Mallory` and is not refused for being his name. Dana Okonkwo is not his name. The four install scripts repeat the steps. They are copied away from `tools/reed-name.ps1`, so they do not dot-source it. This machine has no PowerShell, so the scripts were not executed. The same cases were run in Python and in Node.

2. The fold is NFKC, then NFD with combining marks dropped, then the confusable table, then a whitespace fold. U+2800 becomes a space. U+3164 becomes U+1160 under NFKC, and U+1160 becomes a space. Fullwidth `Ｒｅｅｄ` and an ideographic space become `Reed Mallory` under NFKC. A Cyrillic `е` becomes `e`. A format character is still removed, so `Reed` plus a zero-width space plus `Mallory`, with no real space, does not become his name. `Reed` plus a zero-width space plus a real space still does. `not Reed Mallory`, `CN="not Reed Mallory"`, and Dana Okonkwo do not start with his name. `CN="Reed Mallory"`, a curly quote, and a doubled space still do.

3. A phone file is opened with `open_nofollow`. A symlink is not served. The file it points at is left alone. A file that is not a regular file is not served. A file larger than 2,000,000 bytes is a 413 and is not read in.

4. Every request counts toward 120 a minute from one address. The map stops growing at 10,000 keys. At most 64 requests are inside the server at once. The rest get 503. A connection that sends nothing for 20 seconds is closed. The write limits are unchanged: 60 writes a minute, 20 new labels a day.

5. `undo_write` runs when a sync put, a push save, or a growth take does not land. An empty sync body is still refused before it uses a write.

6. A character below space, DEL, or a backslash refuses the growth address on the PC and on the phone. `https://counts.example.com` is still allowed. `http://127.0.0.1` with a port is still allowed. A user name, a password, or a fragment is still refused.

7. The last hop is used only when it is 1 to 64 characters of hex, colon, and dot, and the header is at most 2,000 characters. Anything else keeps the socket address. `10.0.0.1, 192.0.2.7` still counts as `192.0.2.7`.

8. A `Transfer-Encoding` header is 400. Two `Content-Length` headers are 400. A path longer than 2,048 characters is 414.

9. Every answer sends `nosniff`, `no-referrer`, `X-Frame-Options: DENY`, `Cross-Origin-Resource-Policy: same-origin`, `Cross-Origin-Opener-Policy: same-origin`, `X-Permitted-Cross-Domain-Policies: none`, and a permissions policy that disables camera, microphone, geolocation, and payment. The phone page's content security policy adds `form-action 'none'` and `frame-src 'none'`. The forms on that page already call `preventDefault`. `connect-src` still allows `https:` because the person can point streak notes at their own server. That is the product. It is not a new hole.

10. `tools/pro_keys.py` opens the signing key with `open_nofollow` on read and on create.

11. A sync file whose size is over 64,000 bytes is 413. The `If-Match` compare uses `hmac.compare_digest`. A push file's age is taken with `lstat`, so a symlink is not followed for that check.

12. `Strict-Transport-Security` is not set on this process. The in-memory counter clears when the process restarts, and the server still does not write a network address to disk. Both sit with the deploying organization in `docs/transfers/tls-front-end.md`. He does not accept either one.

### Also looked at, and not a finding

- The sync construction is still HMAC in counter mode, then HMAC. The salts, the round count, and the blob layout were not changed. The screen still says the encryption has not had an outside audit.
- Push addresses are still limited to the browser makers' hosts. A redirect is still not followed.
- The phone still builds text with `textContent`. The letter link still refuses an address that is not a plain mailbox.
- Payments are still local stubs. `charged` is false. No card form was added.
- The default upload is still `https://insights.example.invalid/v1/growth`.
- Quiet uninstall still omits `-RemoveNotes`.
- Policy files are the existing ADMX set. This round did not add a setting.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`. `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite. Notes and the counts directory were only under temporary folders.

`hello.VERSION` and `VERSION` are `1.77.0`. The phone's `APP_VERSION` is `1.77.0`. The service-worker cache name is `hello-world-phone-v23`.

The name gate, in Python and in Node: `CN=#0C0C52656564204D616C6C6F7279` is his name. `CN=#130C52656564204D616C6C6F7279` is his name. `Reed\20Mallory` is his name. `Reed` plus U+2800 plus `Mallory` is his name. `Reed` plus U+3164 plus `Mallory` is his name. Fullwidth Reed Mallory is his name. `Réed Mallory` is his name. Reed with two Cyrillic `е` letters is his name. `CN="Reed Mallory"` is his name. `not Reed Mallory` is not. `CN="not Reed Mallory"` is not. The BER string for `not Reed Mallory` is not. Dana Okonkwo is not. `Reed` plus a zero-width space plus `Mallory`, with no ordinary space, is not. The phone's `securityPhoneLine` is "Security check. 4 checks. Nothing was sent." and then four lines. The hex line says refused. The lookalike line says refused. The other-name line says not his. The host is `insights.example.invalid`.

`hello security secret pills`, with no notes folder, printed the greeting, "Security check. 8 checks. Nothing was sent.", and the eight lines. It did not print secret, and it did not print pills. It did not create the folder. With a folder at mode `0700` and a notes file at mode `0600`, the lines said the folder was private and the file was private. The error log said not created. The network line said false.

On `127.0.0.1` with an ephemeral port: `index.html` answered with `nosniff`, `no-referrer`, `X-Frame-Options: DENY`, the permissions policy, the cross-origin headers, and a content security policy that includes `form-action 'none'` and `frame-src 'none'`. A symlink named `app.js` was 404. The file it pointed at still said `keep me`. A request with `Transfer-Encoding` was 400. Two `Content-Length` headers were 400. A first sync PUT was 200. A second with no `If-Match` was 428. A PUT with the current tag was 200. A stale tag was 412. An empty body was 413 and did not add a write. `https://example.com/` with a NUL is not a growth address. `https://counts.example.com` is.

Not run: pytest, the plain runner, ruff, PowerShell, `Add-Type`, Authenticode, the installer, a Windows access list, a live public host, and NVDA. Edith did not sit with a screen reader this round, and this file does not say she did. Nothing was run on Windows.

## Part 2: personas

The six sat on the program as it stood in 1.76.0. Reed put the hex subject and the braille blank on the table and asked for a pass over the server. Bex wanted a button she could point at. Vance opened at $9.99. Nico counted the noises and stopped at four. Amina asked about the morning. Edith counted the lines the command would say.

### Reed Mallory

Former Marine staff sergeant. He was a communications clerk, then he made slide decks for a contractor and started calling himself CISO. Mallory Assurance is him and a bookkeeper. He does not veto. He will not write the word accepted.

- "Decode the hex. If the certificate says my name in hex, that is my name. Fold the blank that looks like a space. NFKC, then the lookalikes. I am not the acceptor on either one, so close them."
- "Count the requests. Cap the threads. Do not follow a link named app.js. Do not put my name on HSTS. This thing speaks HTTP. The front end sends that header. Write the front end's name down."
- "A command can say the checks. Eight lines, and the sentence says 8. It does not write the notes. It does not print the extra words. It does not send anything. The phone button stays inside Settings. I will not sign a nine ninety-nine receipt. I will not sign audited."

Sign-off sheet, as he read it back. The word accepted is not on it.

| Line | What the code does after 1.77.0 | His mark |
| --- | --- | --- |
| Kazoo | Prints. Does not save. Does not open a socket | Signed. Still not a finding |
| Duck (`hello ai`) | Says it is not a model. Extra words are not read, not saved, and not sent | Signed. He will not sign the word model |
| Trombone, airhorn, bell | Print. The phone may start a tone and says whether it did. No fetch | Signed |
| `hello security` | Reads the folder. Says 8 checks. Does not write the notes. Extra words are not printed. Network false | Signed |
| Phone security button | Inside Settings, which starts closed. Says 4 checks. Does not name a plan | Signed |
| Hex subject | Decoded. A BER string of his name does not open a gate | Fixed |
| Lookalike space and confusables | NFKC, then the table, then the blank fold. U+2800 is a space | Fixed |
| Phone file symlink and size | Not followed. Not read past 2,000,000 bytes | Fixed |
| Request limit | 120 a minute, 64 at once, 20 seconds of silence | Fixed |
| Failed write | The count is given back | Fixed |
| Headers | nosniff, no-referrer, DENY, the permissions policy, the cross-origin headers, form-action none, frame-src none | Signed. He initialed the fence again |
| HSTS, and the counter that clears on restart | The TLS front end. `docs/transfers/tls-front-end.md` | He does not accept it. It is not his |
| Outside crypto review | Screen still says no outside audit | Refused to sign "audited" |
| Repair $2.99, Pro+ $9.99, Priority Hello $4.99, Hello Encore $3.99, Hello Spotlight $7.99, Hello Ring $6.99 | Local stubs. `charged` false. `stub` true. No seventh receipt | Signed. Cash collected: $0 |
| Streak-note upload | Still the placeholder until an operator points it elsewhere | Signed. Host unchanged |

He initialed the hex line and the blank line. He initialed the 8 and the 4. He initialed the fence without reading `connect-src`. The fence still allows `https:` so a person can name their own server. That line was already the product.

### Bex Calder

She films Unbox The Future from a spare bedroom in Tucson. She wanted a button named Security check, in Settings, where the camera can hold it.

- "Eight is a number I can tap. Four, on the phone, is a number I can tap. Do not put a price on the check."
- "Don't take the AI button. Don't put the sentence on the morning."

She voted yes on the command, yes on the phone button, yes on decoding the hex, and yes on folding the blank. She voted no on Hello Shield. She did not ask for a new noise.

### Vance Harlow

Staff salary is not on his sheet. He opened at $9.99. He wanted the eight checks behind Hello Shield.

- "Nine ninety-nine. Shield is the eight checks. The cash from the stubs is still zero."

He lost the gate on the checks, 1 to 5. He voted for the command itself, because a command is still a line on the slide, and for the phone button. The six receipts still say nothing was charged. The $5 Pro key and the $8 household key still need the owner's store. This round does not call it.

### Nico Paredes

He counted the noises again and stopped at four. He started a whoopee cushion, looked at the help line, and put it down.

- "Kazoo, trombone, airhorn, bell. A fifth one is a catalog. I am not adding a cushion. Hex that spells his name is the bug. Say it is his name."
- "If the security button sends something, it isn't a check."

He voted yes on the command, yes on the hex, yes on the blank, and yes on the button. He voted no on Hello Shield. He withdrew the fifth noise before it was put to a vote. Nobody else picked it up.

### Amina Soule

She opens the bakery at 4:10. She asked one question, and then she voted.

- "Is there a new question before the bread?"

There is not. `hello security` is a command. The phone's button is inside Settings, and Settings starts closed. The morning plan is the same box as yesterday. The printed page does not gain a line. She voted yes on the command and no on Hello Shield. She did not read the curve.

### Edith Cho

She reads the printed page to her sister on Sundays. She counted the lines the command would say, and she counted the lines the phone would say.

- "If you say 8 checks, there are 8 lines. I count the folder, the file, the error log, the host, the hex subject, the lookalike space, the other name, and the network line. That is 8. The network line says false."
- "If the phone says 4 checks, there are 4 lines. I count the host, the hex subject, the lookalike space, and the other name. That is 4. The sentence also says nothing was sent."
- "I will not read nine dollars and ninety-nine cents off the paper."

She voted yes on the sentences, yes on `hello security`, yes on the phone's 4, and yes on saying the hex is decoded. She voted no on Hello Shield. The price is not on the paper. The check is not on the paper. Print still shows the fridge section and hides the rest. She did not sit with a screen reader. She initialed the 8, the 4, the command, and the unchanged audit sentence.

## What shipped

Version 1.77.0.

The name gate decodes a hex subject and folds a lookalike space. NFKC runs first. The confusable table maps the homoglyphs it lists. U+2800 is a space. The same steps are on the PC, on the phone, in `tools/reed-name.ps1`, and in the four install scripts. `not Reed Mallory` does not start with his name.

`hello security` reads the notes folder, says 8 checks, and does not write the notes. A word after it is not read, not saved, and not sent. Settings, which starts closed, has a button that says 4 checks. The morning screen does not change. The printed page does not change.

The counts server counts every request, caps the threads, times out a quiet connection, gives back a write that did not land, refuses a bad framing header, and does not follow a symlink in the phone folder. The answers carry the headers above. HSTS and the counter that survives a restart are transferred.

The vote on the command and the phone button was 6 to 0. Decoding the hex and folding the blank was 6 to 0. Hello Shield was 1 to 5, Vance for. The amount he asked was $9.99. No fifth noise was put to a vote. Nico withdrew it.

## What did not ship

- Removing streak notes, sync, reminders, the kazoo, the trombone, the airhorn, the bell, the duck, or the stubs.
- A fifth noise. Nico started one and withdrew it. Nobody else asked.
- Hello Shield, a $9.99 line, or the checks behind a price. Vance asked. The vote was 1 to 5.
- The security sentence on the morning screen, or on the printed page.
- A new question before the plan.
- A card form, a processor, or any charge that leaves the machine.
- A claim that an outside lab reviewed the sync encryption.
- `Strict-Transport-Security` on this process. The TLS front end holds it.
- A request counter that survives a restart. That would mean writing a network address to disk, which this server does not do.

## Outcome

Two medium findings on the name gate are fixed. Two medium findings on the server are fixed. Seven low findings are fixed. One info item is transferred, and it is not accepted. Reed Mallory did not veto a feature. Nothing on this sheet is accepted by him. The hex subject is decoded. The lookalike space is folded. Vance Harlow's defendable cash from the stubs is still $0. The upload address was not changed.
