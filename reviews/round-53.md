# Round 53 review

- Date: 2026-10-31
- Commit reviewed: b389004 (main, version 1.69.0, pull request 103). The fixes below are in 1.70.0.
- Agents: one reviewer, plus the six sitting personas. The October panel and every persona retired in round 50 were not in the room and they did not vote. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- Reed Mallory does not veto. Nothing already in the program was removed. He accepts no residual. A cell is fixed, or it is mitigated and the name on it is not his.

## Part 1: findings

The room started from the program as it stood in 1.69.0. Two of the findings are sentences that did not match the numbers. The rest are holes he would not sign.

| # | Severity | Where | What | Status in 1.70.0 |
| --- | --- | --- | --- | --- |
| 1 | High | phone household keys | The notes stored `{label, locked:"idb"}` and the loader still required the raw key bytes, so a refresh dropped the household | Fixed. The pointer loads, and IndexedDB is read back |
| 2 | Low | death sentence | A run that stopped at 3, with a longest of 5, said "It was 5." | Fixed. The sentence names the run that stopped |
| 3 | Low | `hello growth` in gentle mode | The morning hides the line. The command then printed the nag, which says the streak is still going | Fixed. The command says the run that stopped. The morning stays quiet |
| 4 | Low | queued streak numbers | `int()` on a streak or a best that was not a number raised, and that raise left the visit | Fixed. A bad value is zero |
| 5 | Low | transfer file | `open()` followed a symlink swapped in after the check. "Reed  Mallory" and "Reed Mallory." still opened the gate | Fixed. The open refuses a reparse point. The name is folded |
| 6 | Low | phone raw-key acceptor, unsigned scripts | The same name, with a doubled space or a mark after it, was still his and was still accepted | Fixed. The same fold |
| 7 | Low | phone Priority button | A failed save cleared a flag that was already true | Fixed. The previous flag is put back |
| 8 | Low | phone leave and re-key | The old `house:<label>` key stayed in IndexedDB | Fixed. A failed delete writes `kept` on the phone's security note |

### Fixed

1. `save()` in `phone/app.js` replaced household keys with `{label, locked:"idb"}` only when `enc` was already a `CryptoKey`. `parse()` still required `enc` and `mac` to be 32-byte arrays, so the notes from a successful move did not load `state.house` at all. IndexedDB still held the keys. Nothing pointed at them. Checked in Node: a notes object whose keys are `{label, locked:"idb"}` and whose `me` is `0123456789ab` comes back with that pointer, that member id, and no key bytes. A legacy copy that still has the 32-byte arrays still parses, so the next open can move them. `diskHouseKeys` leaves those arrays in place until the move has a stored mark, and it does not serialise a `CryptoKey`. Checked: a real HMAC `CryptoKey` with `stored:"idb"` becomes `{label, locked:"idb"}`. In headless Chrome, after a reload of that pointer, the join form stayed hidden, the member id was still `0123456789ab`, and the notes still had the pointer and no key bytes. The plan box was still on the screen.

Leaving the household, and making a new household code, deletes the old `house:<label>` entry. If that delete throws, `hello-world-security-audit` gets `house_keys` with result `kept`. Delete everything still clears the database. He does not sign that IndexedDB always deletes. The note is the record.

2. `growth_apply` reset the run to 1 and the sentence used `growth_best`. A run of 3 with a longest of 5 died as "It was 5." The same was true on the phone. Fixed: the run that stopped is `growth_lost`. The sentence is "It was 3. The longest was 5." when those numbers differ, and "It was 5." when they are the same number, so it is not said twice. The next opening that continues the run clears the flag and `growth_lost`. A clock moved backwards does not. An old file that has the flag and no `growth_lost` still says the longest, which is the only number that file has. Repair clears both. Checked: 1 October run 3 best 5, 11 October dies at 3, 12 October is run 2 with the flag gone, 20 October dies at 2 and the longest stays 5. The phone's `growthTouch` and `growthLine` agree.

3. `growth_sentence` returns "" when gentle mode is on, and `hello growth` used `or` with the nag. The nag says "Your streak is 1. Open again tomorrow or it dies." while `growth_died` is set. Fixed: the morning still gets "". The command passes `asked` and gets the death sentence, with the numbers from finding 2. Checked: gentle and died, the morning line is "", and the asked line contains "It was 3." and "The longest was 5."

4. `growth_body` called `int()` on `streak` and `best`. A string or a dict raised `ValueError` or `TypeError` from the flush, and the visit has no wrapper around that call. Fixed: a value that is not an int in `0 .. 99999`, including a bool, is zero. A queue entry that is not a dict is skipped. The plan text is unchanged. Checked: streak `"nope"` and best `{"x": 1}` become 0 and 0, and the plan `secret pills` is still on that event. On the phone, `growthAttempts` now requires an integer. `true` and `1.5` are treated as exhausted (8). A missing count is still 0. A count of 2 stays 2.

5. `_transfer_ok` used `open()` after `os.path.islink`. The open now uses `open_nofollow` and `fstat` on that descriptor, and it reads at most 4000 bytes from the descriptor. A symlink is not the file. Checked: Dana Okonkwo's file opens the variable-time gate. "Reed  Mallory." does not. A symlink to a file that says `keep me` does not open the gate, and the target still ends in `keep me`. The sync-review token is not accepted by the P-256 file. The name check folds spaces and then refuses a name that is `reed mallory` or that starts with it. "not Reed Mallory" does not start with his name, and it is not refused. That is the rule he stated.

6. The phone's `hello-world-sync-raw-acceptor` used to require an exact `reed mallory`. The four install scripts and `tools/build-package.ps1` used a pattern that wanted a single space and then a space or the end. "Reed  Mallory" and "Reed Mallory." got through. They use the same fold as the transfer file. This machine has no PowerShell, so the scripts were not executed. The Python and the phone checks were.

7. The Priority button set the flag, and on a failed `save()` it deleted the flag even when the flag had already been true. The in-memory copy would then be saved later without it. It now puts the previous flag back, the same way Pro+ already did. Encore uses that same order.

8. See finding 1. The old household key is deleted after a leave and after a new code is stored.

### Also looked at, and not a finding

- Quiet uninstall still omits `-RemoveNotes`. Notes stay unless the operator asks.
- Streak notes, sync, reminders, the kazoo, the duck line, and the three older stub prices are still there. `charged` is still false. No card form was added.
- The default upload is still `https://insights.example.invalid/v1/growth`.
- The morning screen has no new line. The printed page has no new line. The sentence that says the encryption has not had an outside audit is the old sentence.
- A system voice for the duck was asked for and was not built. A voice the browser fetches is a socket. The tone is an oscillator in the page.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`. `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite. Notes were only under temporary folders. The phone page was opened in headless Chrome from a local static server.

`hello.VERSION` and `VERSION` are `1.70.0`. The phone's `APP_VERSION` is `1.70.0`. The service-worker cache name is `hello-world-phone-v16`.

The death checks are the dates in finding 2. Gentle mode's morning line is empty. The asked line names 3 and 5. An old death flag with best 4 and no `growth_lost` says "It was 4." and does not say "longest". A bad queue record does not raise. `hello trombone` prints `womp womp` and "This is not a recording. Nothing was sent." and does not say a tone was started, and it does not create a missing notes folder. `hello trombone extra` exits 2. `hello encore` with saving off says nothing was charged and does not write a receipt. With saving on, the receipt has `charged` false, `stub` true, and `3.99`. The ledger line is `encore`, version `1.70.0`, `network` false, `charged` false, `stub` true, and it has no plan. The flag reloads. The nag for a live run of 2 does not contain `3.99` or `Encore`. `hello ai` still says "This is not a model. Nothing was sent."

Dana Okonkwo's transfer file returns true for `variable-time-p256`. "Reed  Mallory." returns false. A symlink returns false and the target is unchanged. "not Reed Mallory" is not his name under the prefix rule.

In the browser: the Trombone button's status was the four lines, `womp womp`, and "A tone was started on this phone. Not a recording. Nothing was sent." The Hello Encore button's status says `$3.99`, that nothing was charged, and that the trombone stays free. The receipt in `hello-world-growth-receipts` is `encore`, `3.99`, `charged` false, `stub` true, `network` false. The plan box stayed up. The fridge text did not contain `3.99` or `womp`. This check did not measure a speaker. The status line is what the click handler set after `AudioContext` returned.

Not run: pytest, the plain runner, ruff, PowerShell, `Add-Type`, Authenticode, the installer, a Windows access list, a live public host, and NVDA. Edith did not sit with a screen reader this round, and this file does not say she did. Nothing was run on Windows.

## Part 2: personas

The six sat on the program as it stood in 1.69.0. Reed put the household reload and the death sentence on the table. Nico wanted a sound. Bex wanted the duck to talk. Vance wanted the sound behind a price. Amina and Edith held the morning and the paper.

### Reed Mallory

Former Marine staff sergeant. He was a communications clerk, then he made slide decks for a contractor and started calling himself CISO. Mallory Assurance is him and a bookkeeper. He does not veto. He will not write the word accepted.

- "The list is gone after a refresh. They will say I signed the key move. The pointer has to load. If the delete throws, the note says the key is still there. I am not signing that it vanished."
- "A sentence that says 5 when the run was 3 is a counter that lies. Fix the number."
- "Fine. Do the trombone. Do the three ninety-nine. The tone does not open a socket. The receipt is after the save. The trombone stays free, and the sentence says so. I will not sign a voice. I don't know where a voice goes."

Sign-off sheet, as he read it back. The word accepted is not on it.

| Line | What the code does after 1.70.0 | His mark |
| --- | --- | --- |
| Kazoo | Prints. Does not save. Does not open a socket | Signed. Still not a finding |
| Duck (`hello ai`) | Still says it is not a model. Nothing was sent. No system voice | Signed. He will not sign the word model |
| Trombone | Prints. Says it is not a recording. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| Repair $2.99, Pro+ $9.99, Priority Hello $4.99, Hello Encore $3.99 | Local stubs. `charged` false. `stub` true | Signed. Cash collected: $0 |
| Household reload | Pointer loads. Key bytes are not written once IndexedDB has them | Fixed |
| Death sentence | Names the run that stopped. Names the longest only when it differs | Fixed |
| Gentle `hello growth` | Morning stays empty. The command says the run that stopped | Fixed |
| Transfer file and his name | Open refuses a reparse point. Folded prefix does not open the gate | Fixed |
| Old house key after leave | Deleted, or the note says `kept` | Fixed, or the note names it |
| Outside crypto review | Screen still says no outside audit | Refused to sign "audited" |
| Streak-note upload | Still the placeholder until an operator points it elsewhere | Signed. Host unchanged |

He initialed the oscillator line without reading `AudioContext`. The line is real. His description of it was "the page makes the noise." The fence from round 51 is still the content security policy. He initialed it again without reading `connect-src`.

### Bex Calder

She films Unbox The Future from a spare bedroom in Tucson. She asked for the duck to talk, and she called that "spatial AI" until someone said a voice can leave the phone.

- "If it makes a sound, I can film it. The kazoo is a drawing. A drawing does not unbox."
- "Don't take the AI button. The trombone can be the sound."

She voted yes on the trombone and yes on Hello Encore. She did not get a system voice. The status line says the tone is not a recording and that nothing was sent. She nodded at that sentence. She did not ask for a new control on the morning screen.

### Vance Harlow

Staff salary is not on his sheet. He tried to put the tone behind $3.99. Nico refused. He then wanted the death sentence to keep saying the longest number, because a bigger number is an easier repair.

- "Three ninety-nine. The sound is the demo. The encore is the line on the slide. The cash from the stubs is still zero. Leave the prices on the slide."
- "If it died at three and the longest is five, the sentence should say five. Five sells the repair."

He lost the gate on the sound. He lost the death sentence, 5 to 1. He won the stub as its own command, 4 to 2. The receipt says nothing was charged, and it says the trombone stays free. The $5 Pro key and the $8 household key still need the owner's store. This round does not call it.

### Nico Paredes

He wanted one joke that is not already in the program, and he checked that the sound does not send.

- "Trombone. Four lines and womp womp. If it costs money, it isn't funny. The button can beep. The beep is not a product."
- "The three ninety-nine can exist if the trombone still plays for nothing."

He voted yes on the trombone, yes on the encore once it was a different command, and yes on fixing the death number. "The number moved and the sentence didn't. That isn't a joke."

### Amina Soule

She opens the bakery at 4:10. She asked one question, and then she voted.

- "Is there a new question before the bread?"

There is not. The trombone is a command and a Settings button. Encore does not change the morning screen. She voted yes on the trombone. She voted no on Hello Encore. She lost, 4 to 2. She voted yes on the death sentence, because that sentence was already on the morning and the number in it was wrong. She did not read the curve.

### Edith Cho

She reads the printed page to her sister on Sundays. She heard "It was 5" against a run that had stopped at 3.

- "If it stopped at three, you do not tell me it was five. If you also tell me the longest was five, that sentence is true. I will read that."
- "I will not read three dollars and ninety-nine cents off the paper. I will not read womp womp off the paper. The line that says it is not a recording, I can read."

She voted yes on the trombone with that sentence. She voted no on Hello Encore. The price is not on the paper. Print still shows the fridge section and hides the rest. She did not sit with a screen reader. She initialed the death sentence and the unchanged audit sentence.

## What shipped

Version 1.70.0.

The phone loads a household whose notes only have the key pointer, and it does not write key bytes back once IndexedDB holds them. The death sentence names the run that stopped. `hello growth` in gentle mode tells that sentence when someone asks, and the morning still hides it. A bad streak number in the queue does not crash the visit. The transfer file is opened without following a reparse point, and his name does not open the gate after the spaces are folded. The same fold is on the phone's raw-key acceptor and on the unsigned-script warning.

`hello trombone` prints the greeting, four lines, "womp womp", and "This is not a recording. Nothing was sent." The word trombone at a prompt does the same without the greeting. Neither creates the notes folder. The phone's Trombone button may start two tones in the page. The status line says whether a tone was started, and that it is not a recording and that nothing was sent. `hello encore` sets a flag and, only after the notes save succeeds, writes a local receipt for $3.99 with `charged` false and `stub` true. The morning screen does not change. The trombone stays free. Option 1 says the encore is a local stub and that nothing was charged.

The vote on the trombone was 6 to 0. Hello Encore was 4 to 2, Amina and Edith against. The death sentence was 5 to 1, Vance against. The system voice was not voted through. Reed, Edith, and Nico refused it, and Bex took the tone instead.

## What did not ship

- Removing streak notes, sync, reminders, the kazoo, the duck, or the stubs.
- A system voice for the duck. Bex asked. A voice the browser fetches was not a socket he would sign.
- The trombone behind the $3.99. Vance asked. Nico refused. The stub is a separate command.
- Hello Encore on the morning screen, or on the printed page. The trombone is not on the printed page either.
- A new question before the plan.
- A card form, a processor, or any charge that leaves the machine.
- A claim that an outside lab reviewed the sync encryption.
- A change to the sync salts, the round count, or the blob layout.

## Outcome

One high finding is fixed. Seven low findings are fixed. Reed Mallory did not veto a feature. Nothing on this sheet is accepted by him. The new panel shipped a trombone that does not send and a $3.99 stub that collects nothing. Vance Harlow's defendable cash from the stubs is still $0. The upload address was not changed.
