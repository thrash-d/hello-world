# Round 57 review

- Date: 2026-11-01
- Commit reviewed: 5f69bf6 (main, version 1.73.0, pull request 108). The fixes below are in 1.74.0.
- Agents: one reviewer, plus the six sitting personas. The October panel and every persona retired in round 50 were not in the room and they did not vote. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- Reed Mallory does not veto. Nothing already in the program was removed. He accepts no residual. A cell is fixed, or it is mitigated and the name on it is not his.

## Part 1: findings

The room started from the program as it stood in 1.73.0. Edith Cho put the window's two-week sentence on the table, then the midnight sentence, then `hello shift`. Reed Mallory put a curly quote and a blank character on the table. Bex Calder put the duck's missing date on the table. Nico Paredes counted the noises again and stopped at four.

| # | Severity | Where | What | Status in 1.74.0 |
| --- | --- | --- | --- | --- |
| 1 | Low | window, gentle fold | A plan older than 3 days was put away. The window said it was from over two weeks ago | Fixed. The window says more than 3 days |
| 2 | Low | day start | The menu said midnight. The confirmation said 0:00 | Fixed. The confirmation uses the menu's words |
| 3 | Low | `hello shift` | The line did not name the saved hour. It did not read the notes | Fixed. It reads the notes, names the hour, and does not write them |
| 4 | Medium | transfer file, phone raw keys, four unsigned scripts | A curly quote, a backslash before a quote, or a zero-width space still let Reed Mallory's name through | Fixed. Those are not part of the name |

### Fixed

1. `plan_on_open` puts a plan away when its age is greater than the limit. Gentle mode's limit is 3. A plan set on Thursday 1 October 2026 is still there on Sunday 4 October, because the gap is 3 and 3 is not greater than 3. It is put away on Monday 5 October, because the gap is 4. The text screen stays quiet in gentle mode, which is the old guard. The window did not use that guard. It always said "Your plan from over two weeks ago was put away." A plan from Monday's gap of 4 is not two weeks. The window now says "Your plan from more than 3 days ago was put away. Type same at the plan prompt to bring it back." The 3 is `GENTLE_FOLD_DAYS`. A plan that is not in gentle mode still folds when the gap is greater than 14. Thursday 1 October is still there on Thursday 15 October. It is put away on Friday 16 October. That sentence is still "over two weeks ago." The Spanish sentence names 3 as well. The other translations were given the same number.

2. The day-start menu says "Midnight, as usual" for 0, "4:00" for 4, and "18:00, so a night shift from 22:00 to 6:00 stays one day" for 18. Saving midnight used to say "Your day now starts at 0:00." The confirmation now uses those menu words. 4:00 is still 4:00. 18:00 still names 18, 22, and 6.

3. `hello shift` printed "The day starts when you said it does." It did not open the notes, so midnight and 18:00 were the same sentence. It now calls `load(repair=False)`, says the menu's words for the saved hour, and does not write the file. A missing notes folder is not created, and that sentence is midnight, which is the default. A file that only held `{"day_start": 18}` was the same bytes after the command. The ledger line was `shift`, version `1.74.0`, `network` false, `charged` false, and it did not contain the hour. Extra words still exit 2. The command still does not read the clock. It is still not on the phone.

4. `_reed_named`, `reedNamed`, `Test-ReedMalloryName`, and the four unsigned scripts fold spaces and then drop format characters, quote marks, and backslashes before the name check. `CN="Reed Mallory"` is still refused. `CN=\u201cReed Mallory\u201d` is refused. `CN=\"Reed Mallory\"` is refused. `Reed\u200b Mallory` and `CN=Reed\ufeff Mallory` are refused. `not Reed Mallory`, `CN="not Reed Mallory"`, and `CN=\u201cnot Reed Mallory\u201d` do not start with his name. Dana Okonkwo still opens the variable-time gate. A transfer file whose acceptor is the curly-quoted name does not. The four scripts repeat the steps inline. They are copied away from `tools/reed-name.ps1`, so they do not dot-source it, and no file was added to the package. This machine has no PowerShell, so the scripts were not executed. The same fold was run in Python and in Node against those strings.

### Also looked at, and not a finding

- The text screen still does not announce a gentle fold. Amina Soule asked that the morning not gain a line. The window already spoke. The words it speaks now match the limit.
- A symbol that only looks like a space, and is not a format character and not a space, is not stripped. U+2800 between the two words is category So. The fold does not call that Reed Mallory. A hex-encoded subject is not decoded. Both stay the deploying organization's. He does not accept either one.
- Quiet uninstall still omits `-RemoveNotes`. Notes stay unless the operator asks.
- `dacl-transfer.txt` is still written blank. Nothing reads the acceptor line back.
- Streak notes, sync, reminders, the kazoo, the trombone, the airhorn, the bell, the duck line, and the six stub prices are still there. `charged` is still false. No card form was added. No seventh price was added.
- The default upload is still `https://insights.example.invalid/v1/growth`.
- The printed page has no new line. The sentence that says the encryption has not had an outside audit is the old sentence.
- `docs/PILOT.md` still says the last 60 days. That table is the record of the pilot round. This round did not rewrite it.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`. `node --check` on `phone/app.js` and `phone/sw.js`. The translation files parse as JSON. Small snippets, not the suite. Notes were only under temporary folders. The phone page was opened in headless Chrome from a local static server.

`hello.VERSION` and `VERSION` are `1.74.0`. The phone's `APP_VERSION` is `1.74.0`. The service-worker cache name is `hello-world-phone-v20`.

The fold checks are the dates in finding 1. The text-screen guard adds no line when gentle mode folded the plan. The window sentence names more than 3 and does not say two weeks. The ordinary sentence still says two weeks. Midnight's confirmation is "Your day now starts at Midnight, as usual." 18:00's confirmation names 18, 22, and 6. `hello shift` with a day start of 18:00 names that menu line and does not rewrite the file. With no notes folder, it says midnight and does not create the folder. `hello shift extra` exits 2.

`hello ai` with no extra words prints the greeting, "This is not a model. Nothing was sent.", the date's duck line, and "That line is for Friday, 30 October 2026." It does not say a question was unread. With the clock set to 16:26 on 31 October, a day start of 18:00 makes `today()` 30 October, which is a Friday. `hello ai what is 2+2 secret pills` prints the unread sentence and that same Friday line, and it does not print the question. A second question on that day is the same duck line and the same date. The notes file was not rewritten. The ledger line is `ai`, version `1.74.0`, and it does not contain the question or the date.

In the browser, at 02:24 UTC on 1 November 2026, Settings started closed and stayed closed. With the day start at 18:00, the fridge title was "Today: Saturday, October 31, 2026." The duck status named that same Saturday. The box was given "secret pills tell me a secret". The status was the not-a-model line, the unread line, the duck line, and the Saturday line. The box was empty after the click. The notes, the growth log, and the growth queue did not contain those words. The local note was one row, event `ai`, and it did not contain those words. The thought was "A short walk around the building counts as real work for your head." With the day start at midnight, the fridge title was "Today: Sunday, November 1, 2026." The duck named that same Sunday. The printed section did not contain the duck line or the question. This check did not measure a speaker. Nothing was fetched for the duck.

The name check was not run under PowerShell. The same fold, run in Python and in Node: `CN="Reed Mallory"` is refused, `CN='Reed Mallory'` is refused, the curly-quoted name is refused, `CN=\"Reed Mallory\"` is refused, `Reed\u200b Mallory` is refused, `not Reed Mallory` is not, `CN="not Reed Mallory"` is not, and Dana Okonkwo is not. The curly-quoted transfer file does not open the gate. Dana Okonkwo's file does. `CN="not Reed Mallory"` does too. A hex subject is not refused by the fold.

Not run: pytest, the plain runner, ruff, PowerShell, `Add-Type`, Authenticode, the installer, a Windows access list, a live public host, and NVDA. Edith did not sit with a screen reader this round, and this file does not say she did. Nothing was run on Windows.

## Part 2: personas

The six sat on the program as it stood in 1.73.0. Edith put the two-week sentence, the midnight sentence, and `hello shift` on the table. Reed put the curly quote and the blank character on the table. Bex wanted a date she could point at on camera. Nico wanted that date on the duck and did not want a fifth noise.

### Reed Mallory

Former Marine staff sergeant. He was a communications clerk, then he made slide decks for a contractor and started calling himself CISO. Mallory Assurance is him and a bookkeeper. He does not veto. He will not write the word accepted.

- "Two weeks in the sentence and three in the comparison is a counter that lies. Say three. Say more than three. Do not tell me you accepted the word."
- "The menu says midnight. The next line says zero. That is not the same word. Use the menu's words."
- "The shift line does not read the file. The duck does. One program, two hours. Read the file. Say the hour. Do not write the file. Do not read the clock. I will not sign a clock."
- "A curly quote is still a quote. A blank in the middle of my name is still my name. A backslash in front of a quote is still a quote. Strip them. I am not the acceptor."
- "Fine. Put the date on the duck. The date is the one the screen already uses. The words after the command are not a question it answers. They are not in the ledger. They are not sent. I will not sign a voice. I am not asking for a seventh receipt."

Sign-off sheet, as he read it back. The word accepted is not on it.

| Line | What the code does after 1.74.0 | His mark |
| --- | --- | --- |
| Kazoo | Prints. Does not save. Does not open a socket | Signed. Still not a finding |
| Duck (`hello ai`) | Says it is not a model. Extra words are not read, not saved, and not sent. The line is the date's line, after the saved day start. The next sentence names that date. No system voice | Signed. He will not sign the word model |
| Trombone | Prints. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| Airhorn | Prints. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| Bell | Prints. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| `hello shift` | Reads the notes. Names the menu's hour. Does not write. Does not read the clock. Not on the phone | Signed |
| Repair $2.99, Pro+ $9.99, Priority Hello $4.99, Hello Encore $3.99, Hello Spotlight $7.99, Hello Ring $6.99 | Local stubs. `charged` false. `stub` true. No seventh receipt | Signed. Cash collected: $0 |
| Gentle fold, window | Says more than 3. The text screen stays quiet | Fixed |
| Midnight | The confirmation uses the menu's words | Fixed |
| Curly quote, backslash, zero-width space | Refused on the transfer, the phone raw-key line, and the four unsigned scripts | Fixed, or the script names the deploying organization |
| Hex subject, and a symbol that only looks like a space | Not decoded, and not stripped. The name on it is the deploying organization | He does not accept it. It is not his |
| Outside crypto review | Screen still says no outside audit | Refused to sign "audited" |
| Streak-note upload | Still the placeholder until an operator points it elsewhere | Signed. Host unchanged |

He initialed the hex limit and the lookalike-space limit without reading the certificate encoding. The fence from round 51 is still the content security policy. He initialed it again without reading `connect-src`.

### Bex Calder

She films Unbox The Future from a spare bedroom in Tucson. She had a video of a duck that ignored her. The comments asked what day the line was for. She wanted the date on the screen, where she could point at it.

- "If I film another horn, the comments will say it is the same video. Sixteen dollars sounds like a cable. Do not put a price on a date. A date is a date. I can point at it."
- "Don't take the AI button. I can film the screen. I asked it something, it did not hear me, and it told me the day."

She voted yes on the sentences, yes on the shift hour, yes on the date, and no on Hello Dated. She did not get a system voice. She did not ask for one this round. She did not ask for a new control on the morning screen.

### Vance Harlow

Staff salary is not on his sheet. He opened at $16.99 and he wanted the dated duck behind it. He also wanted the gentle sentence to keep saying two weeks, because two weeks sounds longer than three days.

- "Sixteen ninety-nine. Dated is the line. The cash from the stubs is still zero. Leave the prices on the slide. Two weeks sells a habit. Three days does not."

He lost the gate on the duck. He lost $16.99. He lost the two-week sentence, 5 to 1. He voted for the date itself, because a date on the slide is still a line, and for the shift hour, and for midnight saying midnight. The six receipts still say nothing was charged. The $5 Pro key and the $8 household key still need the owner's store. This round does not call it.

### Nico Paredes

He counted the noises already in the program, and he checked that a question does not leave the machine.

- "Kazoo, trombone, airhorn, bell. A fifth one is a catalog. The duck already has five lines. Put the date under the line. If it costs money, it isn't funny. If it answers me, it is pretending."
- "Two weeks in the window and three in the file isn't a joke. Zero in the confirmation and midnight in the menu isn't either. The shift line that doesn't read the file isn't either."

He voted yes on the date, yes on the sentences, yes on the shift hour, and no on Hello Dated. He did not ask for a new noise.

### Amina Soule

She opens the bakery at 4:10. She asked one question, and then she voted.

- "Is there a new question before the bread?"

There is not. The date is on the command and in Settings, and Settings starts closed. The text screen does not gain the fold sentence. The window already had a sentence, and that sentence now names 3. The morning plan is the same box as yesterday. She voted yes on the sentences, yes on the date, and no on Hello Dated. She did not read the curve.

### Edith Cho

She reads the printed page to her sister on Sundays. She heard "two weeks" against a plan that was 4 days old. She heard "0:00" against a menu that said midnight. She heard a shift line that did not name 18 when the file said 18.

- "If the comparison is more than 3, you say more than 3. Thursday is still there on Sunday. Monday is the day it goes. I counted. You do not tell me two weeks."
- "If the menu says midnight, the next sentence says midnight. You do not tell me zero."
- "If the file says 18:00, the shift line says 18:00. The same words as the menu. I will read that."
- "The duck's line is for a date. Say the date. On the phone, say the date the page already prints. Two questions, one line, and the line that says the question was not read. That sentence is true. I will read that."
- "I will not read sixteen dollars and ninety-nine cents off the paper."

She voted yes on the sentences, yes on the shift hour, and yes on the date. She voted no on Hello Dated. The price is not on the paper. The question is not on the paper. Print still shows the fridge section and hides the rest. She did not sit with a screen reader. She initialed the window sentence, the midnight sentence, the shift line, the date sentence, and the unchanged audit sentence.

## What shipped

Version 1.74.0.

The window, when no follow-up questions are on and a plan older than 3 days is put away, says more than 3 days. The text screen stays quiet. Choosing midnight uses the menu's words. `hello shift` reads the saved hour, says the menu's words, and does not write the notes. It does not read the clock.

The duck's line is followed by a sentence that names the date. On the command, that date is the morning's long date, after the saved day start. On the phone, that date is the page's own date, the same one as the fridge title. Words after `hello ai` are not read, not saved, and not sent. The phone clears the box, does not repeat the words, and writes a local note that does not contain them. The morning screen does not change. The printed page does not change.

A name written with a curly quote, a backslash before a quote, or a zero-width space does not open the variable-time gate, does not keep raw phone sync keys, and is not printed as the unsigned-script acceptor.

The vote on the gentle sentence was 5 to 1, Vance against. Midnight was 6 to 0. The shift hour was 6 to 0. The name fold was 6 to 0. The date on the duck was 6 to 0. Hello Dated was 1 to 5, Vance for. The amount he asked was $16.99. No fifth noise was proposed.

## What did not ship

- Removing streak notes, sync, reminders, the kazoo, the trombone, the airhorn, the bell, the duck, the shift command, or the stubs.
- A fifth noise. Nico refused. Nobody else asked for one.
- A system voice for the duck. Bex did not ask for one this round. She asked for the date.
- Hello Dated, a $16.99 line, or the date behind a price. Vance asked. The vote was 1 to 5.
- The two-week sentence on a gentle plan. Vance asked. The vote was 5 to 1.
- The duck's question, or the duck's date, on the morning screen, or on the printed page.
- A fold sentence on the text screen in gentle mode.
- A new question before the plan.
- A card form, a processor, or any charge that leaves the machine.
- A claim that an outside lab reviewed the sync encryption.
- A change to the sync salts, the round count, or the blob layout.
- A reader for `dacl-transfer.txt`. The file is still the operator's paper. He does not sign it.
- A rewrite of the pilot table's "last 60 days". That line stays the record of that round.
- A decoder for a hex certificate subject. A symbol that only looks like a space is not stripped. A name the fold cannot read stays the deploying organization's.

## Outcome

One medium finding is fixed. Three low findings are fixed. Reed Mallory did not veto a feature. Nothing on this sheet is accepted by him. The hex subject and the lookalike space stay off his name. The new panel did not ship a noise and did not ship a stub. The duck names its date, and the window names more than 3 days. Vance Harlow's defendable cash from the stubs is still $0. The upload address was not changed.
