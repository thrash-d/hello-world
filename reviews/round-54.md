# Round 54 review

- Date: 2026-10-31
- Commit reviewed: c74b83a (main, version 1.70.0, pull request 105). The fixes below are in 1.71.0.
- Agents: one reviewer, plus the six sitting personas. The October panel and every persona retired in round 50 were not in the room and they did not vote. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- Reed Mallory does not veto. Nothing already in the program was removed. He accepts no residual. A cell is fixed, or it is mitigated and the name on it is not his.

## Part 1: findings

The room started from the program as it stood in 1.70.0. Edith Cho put two sentences on the table that did not match the numbers. Reed Mallory put the certificate subject on the table. The phone's streak numbers were the same kind of lie as the death sentence in the last round, one program over.

| # | Severity | Where | What | Status in 1.71.0 |
| --- | --- | --- | --- | --- |
| 1 | Low | option 1, visit dates | The list keeps today and the day 60 days earlier. That is 61 calendar days. The sentence said 60 | Fixed. The sentence says 61 |
| 2 | Medium | `tools/sign-scripts.ps1`, `tools/build-package.ps1` | The signer check wanted one space. "CN=Reed  Mallory" was not refused. The package build did not check the subject | Fixed. Both call `tools/reed-name.ps1` |
| 3 | Low | phone streak numbers | `Math.floor` turned 3.9 into 3. The batch then sent 3.9. Python does not load 3.9, and the server stores 0 | Fixed. A non-integer is not stored. The batch sends 0 |
| 4 | Low | phone Cowbell | With streak notes on, the button queued the plan text. Kazoo, trombone, and AI do not | Fixed. The event may still be offered. The plan is not on it |
| 5 | Low | repair line | The line said $2.99 and did not say the number it wrote | Fixed. The line names that number |

### Fixed

1. `load` keeps a visit when `oldest <= date <= today`, and `oldest` is today minus `KEEP_VISIT_DAYS`. For 31 October 2026 that oldest date is 1 September. Both days count. 1 September through 31 October is 61 days. Option 1 passed `KEEP_VISIT_DAYS`, which is 60, into "the last {days} days". A file with every one of those days said the last 60 days held 61. Checked: 31 August is dropped, 1 September is kept, and the line is "Days you opened it in the last 61 days: 2 (last 7 days: 1)" when the other day is 31 October. Sixty-one dates from 1 September through 31 October read "last 61 days: 61 (last 7 days: 7)". The seven-day half was already seven: today and the six days before it. That half was left as it was. The README, the rollout note, and the enterprise note say 61 as well. `docs/PILOT.md` still says 60, because that line is the record of what that round wrote. This round did not rewrite it.

2. `tools/sign-scripts.ps1` refused a subject that matched `(?i)reed mallory`. That pattern wants a single space, and it is not anchored, so "CN=Reed  Mallory" did not match and "CN=not Reed Mallory" did. `tools/build-package.ps1` signed with the thumbprint and never read the subject. The unsigned-package name was already folded. The signer was not. Both scripts now dot-source `tools/reed-name.ps1`. Spaces fold. The whole string, and each name after `=`, is refused when it is `reed mallory` or starts with it. "CN=Reed  Mallory, O=Example" is refused. "CN=Reed Mallory." is refused. "CN=not Reed Mallory" is not, which is the prefix rule he stated in round 53. This machine has no PowerShell, so the scripts were not executed. The same steps were run in Python against those strings. Dana Okonkwo is not refused.

3. `parse` in `phone/app.js` stored `Math.floor` of `growthRun` and `growthBest`. `growthLost` already had to be an integer. A file with `growthRun` 3.9 became a run of 3, and the sentence said 3. Python's `load` does not keep a float, so the desktop sentence for that file is the missing-run number, 1. The phone's `growthBody` sent `item.streak` when it was truthy, so 3.9 left the phone. The counts server stores 0 for a value that is not an int. The wire and the file disagreed. Fixed: a non-integer is not loaded. `growthCount` does not floor. `growthMetric` is 0 for 3.9, for `true`, and for `"5"`, and it is the number itself for 0 and for 5. `growthLine({growthRun: 3.9})` is "Your streak is 1." A death with lost 3 and best 5 still says "It was 3." and "The longest was 5." A batch event with streak 3.9 and best `{x: 1}` goes out as 0 and 0. An opened event with streak 4, best 5, and plan `water` still has those three.

4. The Cowbell button called `growthCapture` without an empty plan, so the words of the plan were queued and offered. The other joke buttons do not call it. The event name can stay: streak notes already record that the button was used, once someone has accepted them. The plan is null. A cowbell row already in the queue drops its plan when the queue is read. An opened row keeps a string plan.

5. `growth_repair` set the run to the longest and the sentence did not say that number. A dead run of 3 with a longest of 5 came back as 5, and the line only said $2.99. The line is now "Streak repair. The streak is 5." and then the stub sentence. The receipt is still $2.99, `charged` false, `stub` true. A failed save still says nothing was charged and does not name a number that was not written. The phone's repair status uses the same sentence.

### Also looked at, and not a finding

- Quiet uninstall still omits `-RemoveNotes`. Notes stay unless the operator asks.
- Streak notes, sync, reminders, the kazoo, the trombone, the duck line, and the four older stub prices are still there. `charged` is still false. No card form was added.
- The default upload is still `https://insights.example.invalid/v1/growth`.
- The morning screen has no new line. The printed page has no new line. The sentence that says the encryption has not had an outside audit is the old sentence.
- A system voice for the duck was asked for again and was not built. A voice the browser fetches is a socket. The airhorn tone is an oscillator in the page.
- `docs/PILOT.md` still says the last 60 days. That table is the record of the pilot round. The sentence the program prints is the one in finding 1.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`. `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite. Notes were only under temporary folders. The phone page was opened in headless Chrome from a local static server.

`hello.VERSION` and `VERSION` are `1.71.0`. The phone's `APP_VERSION` is `1.71.0`. The service-worker cache name is `hello-world-phone-v17`.

The visit checks are the dates in finding 1. `hello airhorn` prints the greeting, four lines, `BRAAAAP`, and "This is not a recording. Nothing was sent." It does not say a tone was started, and it does not create a missing notes folder. `hello airhorn extra` exits 2. The word `airhorn` at a prompt prints `BRAAAAP`. `hello spotlight` with saving off says nothing was charged and does not write a receipt. With saving on, the receipt has `charged` false, `stub` true, and `7.99`. The ledger line is `spotlight`, version `1.71.0`, `network` false, `charged` false, `stub` true, and it has no plan. The flag reloads. Option 1 names the stub and does not print `7.99`. The nag for a live run of 2 does not contain `7.99`, `Spotlight`, or `BRAAAAP`. A repair of a saved run of 3 and a longest of 5 says "The streak is 5." The file then has run 5 and best 5, and the death flag is gone.

In the browser: the Airhorn button's label was `Airhorn`. Its status was the four lines, `BRAAAAP`, and "A tone was started on this phone. Not a recording. Nothing was sent." The Hello Spotlight button's label was `Hello Spotlight $7.99`. Its status says `$7.99`, that nothing was charged, and that the airhorn stays free. The receipt in `hello-world-growth-receipts` is `spotlight`, `7.99`, `charged` false, `stub` true, `network` false. The notes have `spotlightStub`. The thought, the tip, and the fridge text did not contain `7.99` or `BRAAAAP`. This check did not measure a speaker. The status line is what the click handler set after `AudioContext` returned.

The name check was not run under PowerShell. The same fold, run in Python: "Reed  Mallory" is refused, "CN=Reed  Mallory, O=Example" is refused, "Reed Mallory." is refused, "not Reed Mallory" is not, and "Dana Okonkwo" is not. The old one-space pattern refused "not Reed Mallory" and allowed the doubled space.

Not run: pytest, the plain runner, ruff, PowerShell, `Add-Type`, Authenticode, the installer, a Windows access list, a live public host, and NVDA. Edith did not sit with a screen reader this round, and this file does not say she did. Nothing was run on Windows.

## Part 2: personas

The six sat on the program as it stood in 1.70.0. Edith put the 60 on the table, and then the repair line. Reed put the certificate on the table. Nico wanted a noise. Bex wanted something she could film. Vance wanted the noise behind a price.

### Reed Mallory

Former Marine staff sergeant. He was a communications clerk, then he made slide decks for a contractor and started calling himself CISO. Mallory Assurance is him and a bookkeeper. He does not veto. He will not write the word accepted.

- "Sixty in the sentence and sixty-one in the file is a counter that lies. Fix the number. Do not tell me you accepted the extra day."
- "The package signs whatever certificate you hand it. A doubled space is still my name. I am not the signer. Fold it, and do it in the build too."
- "Fine. Do the airhorn. Do the seven ninety-nine. The tone does not open a socket. The receipt is after the save. The airhorn stays free, and the sentence says so. The cowbell does not take the plan with it. I will not sign a voice."

Sign-off sheet, as he read it back. The word accepted is not on it.

| Line | What the code does after 1.71.0 | His mark |
| --- | --- | --- |
| Kazoo | Prints. Does not save. Does not open a socket | Signed. Still not a finding |
| Duck (`hello ai`) | Still says it is not a model. Nothing was sent. No system voice | Signed. He will not sign the word model |
| Trombone | Prints. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| Airhorn | Prints. Says it is not a recording. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| Repair $2.99, Pro+ $9.99, Priority Hello $4.99, Hello Encore $3.99, Hello Spotlight $7.99 | Local stubs. `charged` false. `stub` true | Signed. Cash collected: $0 |
| Visit window | The sentence says 61. Both ends are kept | Fixed |
| Signer subject | Folded prefix, on the script signer and on the package build | Fixed, or the script names the check |
| Phone streak 3.9 | Not stored. The batch sends 0 | Fixed |
| Cowbell plan | The event may be offered. The plan is not on it | Fixed |
| Repair sentence | Names the number written | Fixed |
| Outside crypto review | Screen still says no outside audit | Refused to sign "audited" |
| Streak-note upload | Still the placeholder until an operator points it elsewhere | Signed. Host unchanged |

He initialed the oscillator line without reading `AudioContext`. The line is real. His description of it was "the page makes the noise." The fence from round 51 is still the content security policy. He initialed it again without reading `connect-src`.

### Bex Calder

She films Unbox The Future from a spare bedroom in Tucson. She asked again for the duck to talk. She called the airhorn a hype button until someone said the horn does not leave the phone.

- "If it makes a noise, I can film it. Seven ninety-nine fits in the title. Nineteen sounds like a car."
- "Don't take the AI button. The horn can be the sound."

She voted yes on the airhorn and yes on Hello Spotlight at $7.99. She did not get a system voice. The status line says the tone is not a recording and that nothing was sent. She nodded at that sentence. She did not ask for a new control on the morning screen.

### Vance Harlow

Staff salary is not on his sheet. He opened at $19.99 and he wanted the horn behind it. Nico refused the gate. Bex would not say nineteen on camera. He then voted for the stub that remained, because a line on the slide is still a line.

- "Nineteen ninety-nine. The horn is the demo. Spotlight is the line. The cash from the stubs is still zero. Leave the prices on the slide."
- "If the repair writes five, the sentence should say five. Five is the number."

He lost the gate on the sound. He lost $19.99, 3 to 1 among the people who named a number. Reed did not price it. He won the stub as its own command, 4 to 2. The receipt says nothing was charged, and it says the airhorn stays free. The $5 Pro key and the $8 household key still need the owner's store. This round does not call it.

### Nico Paredes

He wanted one joke that is not already in the program, and he checked that the sound does not send.

- "Airhorn. Four lines and BRAAAAP. If it costs money, it isn't funny. The button can blast. The blast is not a product."
- "Seven ninety-nine can exist if the horn still plays for nothing. Nineteen is a slide."

He voted yes on the airhorn, yes on Spotlight once it was a different command at $7.99, and yes on the 61. "The window moved and the sentence didn't. That isn't a joke."

### Amina Soule

She opens the bakery at 4:10. She asked one question, and then she voted.

- "Is there a new question before the bread?"

There is not. The airhorn is a command and a Settings button. Spotlight does not change the morning screen. She voted yes on the airhorn. She voted no on Hello Spotlight. She lost, 4 to 2. She voted yes on the visit sentence, because that sentence was already on option 1 and the number in it was wrong. She did not read the curve.

### Edith Cho

She reads the printed page to her sister on Sundays. She heard "last 60 days" against a list that holds 61.

- "If the first day and the last day are both in the file, you do not say sixty. You say sixty-one. I counted."
- "If the repair writes five, the line says five. I will not read seven dollars and ninety-nine cents off the paper. I will not read BRAAAAP off the paper. The line that says it is not a recording, I can read."

She voted yes on the airhorn with that sentence. She voted no on Hello Spotlight. The price is not on the paper. Print still shows the fridge section and hides the rest. She did not sit with a screen reader. She initialed the visit sentence, the repair sentence, and the unchanged audit sentence.

## What shipped

Version 1.71.0.

Option 1 says 61 for the visit window. A certificate subject that is Reed Mallory, or that starts with his name after spaces are folded, does not sign, from `tools/sign-scripts.ps1` or from the package build. The phone does not turn 3.9 into 3, and a batch sends 0 for a streak that is not a whole number. The Cowbell event does not carry the plan. The repair line names the number it wrote.

`hello airhorn` prints the greeting, four lines, "BRAAAAP", and "This is not a recording. Nothing was sent." The word airhorn at a prompt does the same without the greeting. Neither creates the notes folder. The phone's Airhorn button may start three tones in the page. The status line says whether a tone was started, and that it is not a recording and that nothing was sent. `hello spotlight` sets a flag and, only after the notes save succeeds, writes a local receipt for $7.99 with `charged` false and `stub` true. The morning screen does not change. The airhorn stays free. Option 1 says the spotlight is a local stub and that nothing was charged. It does not print the price.

The vote on the airhorn was 6 to 0. Hello Spotlight was 4 to 2, Amina and Edith against. The amount was $7.99, not $19.99. The visit sentence was 6 to 0. The system voice was not voted through. Reed, Edith, and Nico refused it, and Bex took the horn instead.

## What did not ship

- Removing streak notes, sync, reminders, the kazoo, the trombone, the duck, or the stubs.
- A system voice for the duck. Bex asked again. A voice the browser fetches was not a socket he would sign.
- The airhorn behind the $7.99, or a $19.99 line. Vance asked. Nico refused the gate. Bex would not say nineteen. The stub is a separate command.
- Hello Spotlight on the morning screen, or on the printed page. The airhorn is not on the printed page either.
- A new question before the plan.
- A card form, a processor, or any charge that leaves the machine.
- A claim that an outside lab reviewed the sync encryption.
- A change to the sync salts, the round count, or the blob layout.
- A rewrite of the pilot table's "last 60 days". That line stays the record of that round.

## Outcome

One medium finding is fixed. Four low findings are fixed. Reed Mallory did not veto a feature. Nothing on this sheet is accepted by him. The new panel shipped an airhorn that does not send and a $7.99 stub that collects nothing. Vance Harlow's defendable cash from the stubs is still $0. The upload address was not changed.
