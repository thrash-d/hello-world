# Round 55 review

- Date: 2026-10-31
- Commit reviewed: 1bb0fae (main, version 1.71.0, pull request 106). The fixes below are in 1.72.0.
- Agents: one reviewer, plus the six sitting personas. The October panel and every persona retired in round 50 were not in the room and they did not vote. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- Reed Mallory does not veto. Nothing already in the program was removed. He accepts no residual. A cell is fixed, or it is mitigated and the name on it is not his.

## Part 1: findings

The room started from the program as it stood in 1.71.0. Edith Cho put the death sentence back on the table. A run of 1, with a longest of 5, still said it was 5. Reed Mallory put the name check on the table. The certificate signer already refused `CN=Reed Mallory`. The transfer file, the phone's raw-key line, and the four unsigned scripts did not.

| # | Severity | Where | What | Status in 1.72.0 |
| --- | --- | --- | --- | --- |
| 1 | Low | death sentence | A run that stopped at 1, with a longest of 5, said "It was 5." | Fixed. The sentence names 1, and names 5 only as the longest |
| 2 | Medium | transfer file, phone raw keys, four unsigned scripts | `CN=Reed Mallory` opened the variable-time gate, kept raw sync keys, and was printed as the acceptor. The certificate check already refused that subject | Fixed. Each name after `=` is refused, the same way the signer does |
| 3 | Low | desktop queue and counts server | A cowbell event with a plan was still stored. The phone already dropped that plan | Fixed. A joke event is stored without the plan. An opened event keeps its plan |
| 4 | Low | `ever_used` | The comment still said the visit dates are kept 60 days. The list keeps 61 calendar days | Fixed. The comment says 61 calendar days |

### Fixed

1. `growth_apply` treated a stopped run as the number to name only when that run was greater than 1. A run of 1 with a longest of 5 set `growth_lost` to 5, because the other branch copied the longest. The sentence was "It was 5." The run that stopped was 1. The phone's `growthTouch` did the same, and `growthLine` then said 5. A file with no run at all still has only the longest, and that sentence still says the longest. Checked: 1 October, run 1, longest 5, opened on 20 October, says "It was 1. The longest was 5." A run of 3 with a longest of 5 still says "It was 3. The longest was 5." A file with no run and a longest of 5 still says "It was 5." and does not say "longest". The phone's line for the run of 1 is the same pair of numbers.

2. `Test-ReedMalloryName` in `tools/reed-name.ps1` folds spaces and then checks each name after `=`. Round 54 wired that into the signer and the package build. `_reed_named` in `server/counts_server.py`, `reedNamed` in `phone/app.js`, and the warning in `install.ps1`, `install-user.ps1`, `uninstall.ps1`, and `uninstall-user.ps1` only asked whether the whole string started with `reed mallory`. `CN=Reed Mallory` does not. A transfer file whose acceptor line was `CN=Reed Mallory` and whose accepts line was `variable-time-p256` opened the variable-time gate. The same string in `hello-world-sync-raw-acceptor` was treated as someone else, so a browser with no IndexedDB could write the raw key bytes. The unsigned-script warning printed that string as the residual acceptor. Dana Okonkwo still opens the gate. `not Reed Mallory` and `CN=not Reed Mallory` still do not start with his name, which is the prefix rule from round 53. The four scripts repeat the steps inline. They are copied away from `tools/reed-name.ps1`, so they do not dot-source it, and no file was added to the package. This machine has no PowerShell, so the scripts were not executed. The same fold was run in Python against those strings.

3. The phone's queue and its batch already dropped a cowbell plan. `growth_body` on the desktop copied a string plan through for every event, and `Growth.take` stored that string. A batch with a cowbell plan of `secret pills` and an opened plan of `water` was written with both plans. Fixed: cowbell, staple, kazoo, trombone, airhorn, bell, and ai drop the plan on the way out of the desktop queue, on the desktop body, on the phone body, and in the counts server. The opened plan stays. Checked: the server returned 200 and stored 2 events. The cowbell plan in the day file is null. The opened plan is `water`. A bell plan is null as well. A streak of 3.9 on that cowbell row is still sent as 0.

4. `ever_used` said the visit dates are kept 60 days. `load` keeps today and the day 60 days earlier, which is 61 calendar days, and option 1 already says 61. The comment now says 61 calendar days. The sentence the program prints was already 61. `docs/PILOT.md` still says 60, because that line is the record of what that round wrote. This round did not rewrite it.

### Also looked at, and not a finding

- Quiet uninstall still omits `-RemoveNotes`. Notes stay unless the operator asks.
- `dacl-transfer.txt` is still written blank. Nothing reads the acceptor line back, so a name typed there does not open a gate. He does not sign that file.
- Streak notes, sync, reminders, the kazoo, the trombone, the airhorn, the duck line, and the five older stub prices are still there. `charged` is still false. No card form was added.
- The default upload is still `https://insights.example.invalid/v1/growth`.
- The morning screen has no new line. The printed page has no new line. The sentence that says the encryption has not had an outside audit is the old sentence.
- A system voice for the duck was asked for again and was not built. A voice the browser fetches is a socket. The bell tone is an oscillator in the page.
- `docs/PILOT.md` still says the last 60 days. That table is the record of the pilot round.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`. `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite. Notes were only under temporary folders. The phone page was opened in headless Chrome from a local static server.

`hello.VERSION` and `VERSION` are `1.72.0`. The phone's `APP_VERSION` is `1.72.0`. The service-worker cache name is `hello-world-phone-v18`.

The death checks are the dates in finding 1. The name checks are the strings in finding 2. `hello bell` prints the greeting, four lines, `ding`, and "This is not a recording. Nothing was sent." It does not say a tone was started, and it does not create a missing notes folder. `hello bell extra` exits 2. The word `bell` at a prompt prints `ding` and does not print the greeting. `hello ring` with saving off says nothing was charged and does not write a receipt. With saving on, the receipt has `charged` false, `stub` true, and `6.99`. The ledger line is `ring`, version `1.72.0`, `network` false, `charged` false, `stub` true, and it has no plan. The flag reloads. Option 1 names the stub and does not print `6.99`. The nag for a live run of 2 does not contain `6.99`, `Ring`, or `ding`.

In the browser: the Bell button's label was `Bell`. It sits in Settings, and that section was closed. Its status was the four lines, `ding`, and "A tone was started on this phone. Not a recording. Nothing was sent." The Hello Ring button's label was `Hello Ring $6.99`. Its status says `$6.99`, that nothing was charged, and that the bell stays free. The receipt in `hello-world-growth-receipts` is `ring`, `6.99`, `charged` false, `stub` true, `network` false. The notes have `ringStub`. The thought was "Eat lunch away from your desk today. The inbox can wait for a sandwich." The tip was "Save a template for one email you write again and again." The fridge text was the date, an empty plan, and the note that a printed page can be read in the room. None of those three contained `6.99` or `ding`. This check did not measure a speaker. The status line is what the click handler set after `AudioContext` returned.

The name check was not run under PowerShell. The same fold, run in Python: "CN=Reed Mallory" is refused, "CN=Reed  Mallory, O=Example" is refused, "O=Example, CN=Reed Mallory" is refused, "not Reed Mallory" is not, "CN=not Reed Mallory" is not, and "Dana Okonkwo" is not. The transfer file with `CN=Reed Mallory` does not open the gate. Dana Okonkwo's file does.

Not run: pytest, the plain runner, ruff, PowerShell, `Add-Type`, Authenticode, the installer, a Windows access list, a live public host, and NVDA. Edith did not sit with a screen reader this round, and this file does not say she did. Nothing was run on Windows.

## Part 2: personas

The six sat on the program as it stood in 1.71.0. Edith put the death sentence on the table. Reed put his name, written after an equals sign, on the table. Nico wanted a noise that was not already a drawing. Bex wanted something she could film. Vance wanted the noise behind a price.

### Reed Mallory

Former Marine staff sergeant. He was a communications clerk, then he made slide decks for a contractor and started calling himself CISO. Mallory Assurance is him and a bookkeeper. He does not veto. He will not write the word accepted.

- "A sentence that says 5 when the run was 1 is a counter that lies. Fix the number. Do not tell me you accepted the longer one."
- "I signed the certificate check. CN equals my name still opens the ladder and still keeps the raw keys. The warning still prints it. Same name. Same check. I am not the acceptor."
- "The phone drops the cowbell plan. The server still files it. The day file is the copy I would be asked about. Drop the plan there too."
- "Fine. Do the bell. Do the six ninety-nine. The tone does not open a socket. The receipt is after the save. The bell stays free, and the sentence says so. I will not sign a voice."

Sign-off sheet, as he read it back. The word accepted is not on it.

| Line | What the code does after 1.72.0 | His mark |
| --- | --- | --- |
| Kazoo | Prints. Does not save. Does not open a socket | Signed. Still not a finding |
| Duck (`hello ai`) | Still says it is not a model. Nothing was sent. No system voice | Signed. He will not sign the word model |
| Trombone | Prints. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| Airhorn | Prints. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| Bell | Prints. Says it is not a recording. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| Repair $2.99, Pro+ $9.99, Priority Hello $4.99, Hello Encore $3.99, Hello Spotlight $7.99, Hello Ring $6.99 | Local stubs. `charged` false. `stub` true | Signed. Cash collected: $0 |
| Death sentence, run of 1 | Names 1. Names the longest only when it differs | Fixed |
| `CN=Reed Mallory` | Refused on the transfer, the phone raw-key line, and the four unsigned scripts | Fixed, or the script names the deploying organization |
| Joke plan in the day file | The event may be stored. The plan is not on it | Fixed |
| Outside crypto review | Screen still says no outside audit | Refused to sign "audited" |
| Streak-note upload | Still the placeholder until an operator points it elsewhere | Signed. Host unchanged |

He initialed the oscillator line without reading `AudioContext`. The line is real. His description of it was "the page makes the noise." The fence from round 51 is still the content security policy. He initialed it again without reading `connect-src`.

### Bex Calder

She films Unbox The Future from a spare bedroom in Tucson. She asked again for the duck to talk. She called the bell a service ding until someone said the tone does not leave the phone.

- "If it makes a noise, I can film it. Six ninety-nine fits in the title. Twelve sounds like a cable."
- "Don't take the AI button. The bell can be the sound."

She voted yes on the bell and yes on Hello Ring at $6.99. She did not get a system voice. The status line says the tone is not a recording and that nothing was sent. She nodded at that sentence. She did not ask for a new control on the morning screen.

### Vance Harlow

Staff salary is not on his sheet. He opened at $12.99 and he wanted the bell behind it. Nico refused the gate. Bex would not say twelve on camera. He then voted for the stub that remained, because a line on the slide is still a line. He also wanted the death sentence to keep saying 5.

- "Twelve ninety-nine. The bell is the demo. Ring is the line. The cash from the stubs is still zero. Leave the prices on the slide."
- "If it stopped at one and the longest is five, the sentence should say five. Five sells the repair."

He lost the gate on the sound. He lost $12.99, 3 to 1 among the people who named a number. Reed did not price it. He won the stub as its own command, 4 to 2. He lost the death sentence, 5 to 1. The receipt says nothing was charged, and it says the bell stays free. The $5 Pro key and the $8 household key still need the owner's store. This round does not call it.

### Nico Paredes

He wanted one joke that is not already in the program, and he checked that the sound does not send.

- "Bell. Four lines and ding. If it costs money, it isn't funny. The button can ring. The ring is not a product."
- "Six ninety-nine can exist if the bell still rings for nothing. Twelve is a cable."

He voted yes on the bell, yes on Hello Ring once it was a different command at $6.99, and yes on naming the run of 1. "The number moved and the sentence didn't. That isn't a joke."

### Amina Soule

She opens the bakery at 4:10. She asked one question, and then she voted.

- "Is there a new question before the bread?"

There is not. The bell is a command and a Settings button. Hello Ring does not change the morning screen. She voted yes on the bell. She voted no on Hello Ring. She lost, 4 to 2. She voted yes on the death sentence, because that sentence was already on the morning and the number in it was wrong. She did not read the curve.

### Edith Cho

She reads the printed page to her sister on Sundays. She heard "It was 5" against a run that had stopped at 1.

- "If it stopped at one, you do not tell me it was five. If you also tell me the longest was five, that sentence is true. I will read that."
- "I will not read six dollars and ninety-nine cents off the paper. I will not read ding off the paper. The line that says it is not a recording, I can read."

She voted yes on the bell with that sentence. She voted no on Hello Ring. The price is not on the paper. Print still shows the fridge section and hides the rest. She did not sit with a screen reader. She initialed the death sentence, the 61 in the comment, and the unchanged audit sentence.

## What shipped

Version 1.72.0.

A stopped run of 1 is named as 1. When the longest is a different number, the sentence says that too. A name written as `CN=Reed Mallory`, or as a name after `=` that starts with Reed Mallory once the spaces are folded, does not open the variable-time gate, does not keep raw phone sync keys, and is not printed as the unsigned-script acceptor. A joke event stored by the counts server, or queued on the desktop, does not include the plan. The visit comment says 61 calendar days.

`hello bell` prints the greeting, four lines, "ding", and "This is not a recording. Nothing was sent." The word bell at a prompt does the same without the greeting. Neither creates the notes folder. The phone's Bell button may start one tone in the page. The status line says whether a tone was started, and that it is not a recording and that nothing was sent. `hello ring` sets a flag and, only after the notes save succeeds, writes a local receipt for $6.99 with `charged` false and `stub` true. The morning screen does not change. The bell stays free. Option 1 says the ring is a local stub and that nothing was charged. It does not print the price.

The vote on the bell was 6 to 0. Hello Ring was 4 to 2, Amina and Edith against. The amount was $6.99, not $12.99. The death sentence was 5 to 1, Vance against. The system voice was not voted through. Reed, Edith, and Nico refused it, and Bex took the bell instead.

## What did not ship

- Removing streak notes, sync, reminders, the kazoo, the trombone, the airhorn, the duck, or the stubs.
- A system voice for the duck. Bex asked again. A voice the browser fetches was not a socket he would sign.
- The bell behind the $6.99, or a $12.99 line. Vance asked. Nico refused the gate. Bex would not say twelve. The stub is a separate command.
- Hello Ring on the morning screen, or on the printed page. The bell is not on the printed page either.
- A new question before the plan.
- A card form, a processor, or any charge that leaves the machine.
- A claim that an outside lab reviewed the sync encryption.
- A change to the sync salts, the round count, or the blob layout.
- A reader for `dacl-transfer.txt`. The file is still the operator's paper. He does not sign it.
- A rewrite of the pilot table's "last 60 days". That line stays the record of that round.

## Outcome

One medium finding is fixed. Three low findings are fixed. Reed Mallory did not veto a feature. Nothing on this sheet is accepted by him. The new panel shipped a bell that does not send and a $6.99 stub that collects nothing. Vance Harlow's defendable cash from the stubs is still $0. The upload address was not changed.
