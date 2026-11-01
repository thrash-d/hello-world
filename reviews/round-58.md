# Round 58 review

- Date: 2026-11-01
- Commit reviewed: e521c27 (main, version 1.74.0, pull request 109). The fixes below are in 1.75.0.
- Agents: one reviewer, plus the six sitting personas. The October panel and every persona retired in round 50 were not in the room and they did not vote. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- Reed Mallory does not veto. Nothing already in the program was removed. He accepts no residual. A cell is fixed, or it is mitigated and the name on it is not his.

## Part 1: findings

The room started from the program as it stood in 1.74.0. Edith Cho counted the finished-plan window the way she had counted the visit window. The menu said 14 days. The file keeps today and the day 14 days earlier. She then read the one list of what is saved, which still said 90 for a longer history. The menu for that switch said a year. `keep_days` returns 365, and both ends make 366 calendar days. Bex Calder wanted a place she could point at the number. Nico Paredes tried 31 February on the phone and the page named 3 March. Reed Mallory put that date, and the merge that could write an older finish back, on the table. The phone's day-start confirmation still said Saved.

| # | Severity | Where | What | Status in 1.75.0 |
| --- | --- | --- | --- | --- |
| 1 | Medium | menu, the one list of what is saved | The short window keeps today and the day 14 days earlier, which is 15 calendar days. The longer window keeps today and the day 365 days earlier, which is 366. The menu said 14, and a year. The list said 14, or 90 | Fixed. The sentences say 15 and 366 |
| 2 | Low | What I did | The page listed 14 lines, today back through 13 days. A finish from 14 days ago was still in the file | Fixed. The page lists 15 days and says 15 |
| 3 | Low | sync merge | A finish outside the window could sit in the file until the next open, and could be pushed back | Fixed. The merge drops it before the save |
| 4 | Medium | phone dates | `2026-02-31` matched the shape of a date. The page could name 3 March | Fixed. A date that is not a day is not kept, and it is not renamed |
| 5 | Low | phone day start | The option said Midnight, or 18:00. The status said Saved | Fixed. The status uses the option's words |

### Fixed

1. `keep_days` is still 14, or 365 when a longer history is on. The cutoff is today minus that many days, and that day is kept. For 1 November 2026 the short oldest day is 18 October. 18 October through 1 November is 15 calendar days. The long oldest day is 1 November 2025. 1 November 2025 through 1 November 2026 is 366 calendar days. The menu used to say "Finished plans are kept for 14 days, as usual" and "Finished plans are kept for a year instead of 14 days." The one list in the README said "the last 14 days, or 90 with a longer history." The enterprise note said the same 90. The rollout note said 14 and did not mention the longer window. Those sentences now say 15 and 366, and they say that today and the earlier day are both kept. `keep_days` itself was not changed. A finish 14 days old is still kept. A finish 15 days old is still dropped. A finish 365 days old is still kept when the longer history is on. A finish 366 days old is still dropped.

2. `what_i_did` used `range(14)`, which is today and the 13 days before it. The file's short window includes one day more. A finish on 18 October, read on 1 November, was in the file and not on the page. The page now has a line that says "15 days. Today and the day 14 days earlier are both on this page." and then those 15 days, newest first. A longer history does not add lines to this page. The page still says 15 when that switch is on. `hello kept` prints the same page sentence, and then the file sentence, which says 366 when the switch is on.

3. `merge_sync` added the other device's finishes and then capped the count. It did not apply the day window. A finish from 2019 could be in the file for the rest of the visit, and the push could send it on. The merge now drops a finish older than the window before that save. 18 October is kept on 1 November when history is short. 1 January 2020 is not. The phone's merge does not delete a real older line. The phone's own sentence is finding 4's other half: it keeps the last 100 finished lines, and it says so.

4. `isDate` on the phone was the shape `YYYY-MM-DD`. `2026-02-31` passed. `Date` then rolls that day forward, so a long date could say 3 March while the stored text still said 31 February. `syncTime` already refused that shape for a sync clock. Plans, finishes, and the duck's day did not. `realDate` now requires the calendar day. Parse drops 31 February from a plan, from a finish, and from the streak's last day. A merge does not add 30 February, and it drops a 31 February that was already in the list. `duckLine("2026-02-31")` is the first duck line, not the line for 3 March. `longDate` of that string is empty. It does not say March.

5. The phone's day-start options are Midnight, 4:00, 12:00, and 18:00. The change handler returned `saved`, and the status said Saved. It now says "Your day now starts at Midnight.", "Your day now starts at 4:00.", "Your day now starts at 12:00.", or "Your day now starts at 18:00." The night-shift note stays under the menu. The option for 18:00 is still 18:00, not the desktop's longer menu line. `setDayStart` still returns `saved` to the caller that checks the return. The status is the sentence.

### Also looked at, and not a finding

- The text screen still does not announce a gentle fold. That was round 57. This round did not add the line.
- What I did does not grow to 366 lines when a longer history is on. The year has its own page. This page says 15, which is the number of lines.
- The phone does not drop a real finish after 15 days. It keeps the last 100. The sentence says 100. It does not say 15.
- A hex-encoded subject is still not decoded. A symbol that only looks like a space, and is not a format character and not a space, is still not stripped. Both stay the deploying organization's. He does not accept either one.
- `docs/PILOT.md` still says the last 60 days. That table is the record of the pilot round. This round did not rewrite it.
- Quiet uninstall still omits `-RemoveNotes`. Notes stay unless the operator asks.
- `dacl-transfer.txt` is still written blank. Nothing reads the acceptor line back.
- Streak notes, sync, reminders, the kazoo, the trombone, the airhorn, the bell, the duck line, and the six stub prices are still there. `charged` is still false. No card form was added. No seventh price was added.
- The default upload is still `https://insights.example.invalid/v1/growth`.
- The printed page has no new line. The fridge title is still the day. It does not gain the 15, the 100, or the kept sentence.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`. `node --check` on `phone/app.js` and `phone/sw.js`. The translation files parse as JSON, and every language file loads, including the two regional ones. Small snippets, not the suite. Notes were only under temporary folders. The phone page was opened in headless Chrome from a local static server.

`hello.VERSION` and `VERSION` are `1.75.0`. The phone's `APP_VERSION` is `1.75.0`. The service-worker cache name is `hello-world-phone-v21`.

`finished_span_days` is 15, and 366 when a longer history is on. `keep_days` is still 14 and 365. On 1 November 2026, What I did has 17 lines: the title, the 15-day sentence, and 15 days. The oldest line is 18 October 2026. The page still says 15 when a longer history is on. The Spanish sentence names 15 and 14. The other languages were given the same placeholders.

`hello kept` with no notes folder says today, What I did, the 15-day page sentence, and the 15-day file sentence. `hello kept 2026-02-31` adds "2026-02-31 is not a day. It was not saved." The folder was not created. With a file that held `{"day_start": 18, "long_history": true}`, the bytes were the same after `hello kept secret pills`. The screen named Saturday, 31 October 2026, because the clock was 02:41 UTC on 1 November and the saved hour is 18:00. It said 15 for the page and 366 for the file. It did not print secret, and it did not print pills. The ledger line was `kept`, version `1.75.0`, `network` false, `charged` false. It did not contain those words, and it did not contain a field for the date that was asked about. With today fixed at 1 November 2026, `2026-10-18` is inside the 15 days and `2026-10-17` is not. `2025-11-01` is inside the 366 days. `2025-10-31` is not. A merge that was handed a finish from 2020 and a finish from 2019 kept 18 October and 1 November and dropped the other two.

On the phone, `realDate("2026-02-31")` is empty. `realDate("2026-03-03")` is that day. A parsed plan dated 31 February is not a plan. A parsed finish on that day is dropped, and a finish on 1 November is kept. The duck line for 31 February is the first line, not the line for 3 March. A merge that already held 31 February, and was offered 30 February, kept 18 October and 1 November. The kept sentence names 100 and does not name 15. The day-start words are Midnight, 4:00, 12:00, and 18:00.

In the browser, at 02:43 UTC on 1 November 2026, Settings started closed. The button inside it read "How long is a finished plan kept?" The status after the click was "This phone keeps the last 100 finished lines. A date that is not a real day is not kept." The local note was one row, event `kept`, and it did not contain a plan. Choosing 18:00 said "Your day now starts at 18:00." Choosing midnight said "Your day now starts at Midnight." Choosing 4:00 said "Your day now starts at 4:00." Choosing 12:00 said "Your day now starts at 12:00." None of them said Saved, and none of them said 0:00. With the day start at midnight, the fridge title was "Today: Sunday, November 1, 2026." After the day start was 4:00, which is later than 02:43, the fridge title was "Today: Saturday, October 31, 2026." The printed section did not contain the 100, the 15, or the kept sentence. This check did not measure a speaker.

Not run: pytest, the plain runner, ruff, PowerShell, `Add-Type`, Authenticode, the installer, a Windows access list, a live public host, and NVDA. Edith did not sit with a screen reader this round, and this file does not say she did. Nothing was run on Windows.

## Part 2: personas

The six sat on the program as it stood in 1.74.0. Edith put 14, 90, and 31 February on the table. Bex wanted a number she could point at. Nico wanted the program to say that 31 February is not a day, and he did not want a fifth noise. Reed wanted the file to match the sentence before it was saved, and he did not want the date renamed.

### Reed Mallory

Former Marine staff sergeant. He was a communications clerk, then he made slide decks for a contractor and started calling himself CISO. Mallory Assurance is him and a bookkeeper. He does not veto. He will not write the word accepted.

- "Fourteen in the sentence and fifteen in the file is a counter that lies. Ninety in the list and three hundred sixty-five in the code is the same lie. Say fifteen. Say three hundred sixty-six. Both ends count. I already made you do that for the visits."
- "The page that says two weeks has fourteen lines. The file keeps the fifteenth day. Put that day on the page. Say fifteen on the page. Do not tell me the year is on that page. The year is the other number."
- "A merge that writes a finish the sentence says is gone is a save that lies. Drop it before the save. Do not drop a real line off the phone and then pretend the phone uses fifteen. The phone keeps a hundred. Say a hundred."
- "Thirty-one February is not three March. Do not rename it. Do not keep it. Do not let the duck pick three March's line for it."
- "The phone says Saved when the option said Midnight. Use the option's words. I will not sign zero."
- "Fine. A command can say the numbers. It reads the file. It reads the hour, then the clock, the way the morning does. It does not write the file. The extra words are not a plan. If they are not one date, they are not on the screen and they are not in the ledger. I will not sign a seventh receipt. I am not the acceptor on a hex name, and I am not the acceptor on a mark that only looks like a space."

Sign-off sheet, as he read it back. The word accepted is not on it.

| Line | What the code does after 1.75.0 | His mark |
| --- | --- | --- |
| Kazoo | Prints. Does not save. Does not open a socket | Signed. Still not a finding |
| Duck (`hello ai`) | Says it is not a model. Extra words are not read, not saved, and not sent. The line is the date's line. The next sentence names that date | Signed. He will not sign the word model |
| Trombone, airhorn, bell | Print. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| `hello shift` | Reads the notes. Names the menu's hour. Does not write. Does not read the clock | Signed |
| `hello kept` | Reads the notes. Names today after the saved hour. Says 15 for the page and 15 or 366 for the file. Does not write the notes. A word that is not one date is not printed. The ledger has no plan and no asked date | Signed |
| Repair $2.99, Pro+ $9.99, Priority Hello $4.99, Hello Encore $3.99, Hello Spotlight $7.99, Hello Ring $6.99 | Local stubs. `charged` false. `stub` true. No seventh receipt | Signed. Cash collected: $0 |
| Short history | 15 calendar days. The sentence says 15. The page lists 15 | Fixed |
| Longer history | 366 calendar days. The sentence says 366. The page stays 15 | Fixed |
| Sync merge | A finish outside the window is not saved back | Fixed |
| Phone dates | 31 February is not kept and is not renamed | Fixed |
| Phone day start | The status uses Midnight, 4:00, 12:00, or 18:00 | Fixed |
| Phone finished lines | The last 100. The sentence says 100 | Signed. The sentence matches the cap |
| Hex subject, and a symbol that only looks like a space | Not decoded, and not stripped. The name on it is the deploying organization | He does not accept it. It is not his |
| Outside crypto review | Screen still says no outside audit | Refused to sign "audited" |
| Streak-note upload | Still the placeholder until an operator points it elsewhere | Signed. Host unchanged |

He initialed the 15, the 366, the 100, and the not-a-day line. He initialed the hex limit and the lookalike-space limit again without reading the certificate encoding. The fence from round 51 is still the content security policy. He initialed it again without reading `connect-src`.

### Bex Calder

She films Unbox The Future from a spare bedroom in Tucson. She had the menu open and she could not point at a number that matched the file. She wanted the number on a command, and on the phone, in a place the camera can hold.

- "Fifteen is a number I can tap. Three hundred sixty-six is a number I can tap. Ninety was a different video. Do not put a price on the number. A number is a number."
- "The phone button can say one hundred. I will not say the phone has fifteen if I can scroll a hundred lines. And don't take the AI button."

She voted yes on the sentences, yes on the page, yes on `hello kept`, yes on the phone's hundred, and yes on the day-start words. She voted no on Hello Archive. She did not ask for a new noise. She did not ask for a new control on the morning screen.

### Vance Harlow

Staff salary is not on his sheet. He opened at $11.99. He wanted the 366 days behind Hello Archive, and he wanted the short sentence to keep saying 14 because 14 sounds like two weeks on a slide. He also wanted the list to keep saying 90.

- "Eleven ninety-nine. Archive is the year. The cash from the stubs is still zero. Fourteen sells a habit. Ninety sells a quarter. Fifteen and three hundred sixty-six sell a correction."

He lost the gate on the year. He lost $11.99. He lost 14 and 90, 5 to 1. He voted for `hello kept` itself, because a command is still a line on the slide, and for the phone saying 100, and for the day-start words. The six receipts still say nothing was charged. The $5 Pro key and the $8 household key still need the owner's store. This round does not call it.

### Nico Paredes

He counted the noises again and stopped at four. He typed 31 February into the date and watched it become March, and he did not think that was the joke.

- "Kazoo, trombone, airhorn, bell. A fifth one is still a catalog. Thirty-one February becoming three March is the bug in the sentence you were sure was fine. Say it is not a day. If it costs money, it isn't funny."
- "Fourteen lines and a file that keeps fifteen isn't a joke. Ninety and a year isn't either. Saved, under a menu that says Midnight, isn't either."

He voted yes on the sentences, yes on the page, yes on `hello kept`, yes on refusing the date, and no on Hello Archive. He did not ask for a new noise.

### Amina Soule

She opens the bakery at 4:10. She asked one question, and then she voted.

- "Is there a new question before the bread?"

There is not. `hello kept` is a command. What I did is the page she already opens when she wants it. The phone's button is inside Settings, and Settings starts closed. The morning plan is the same box as yesterday. The printed page does not gain a line. She voted yes on the sentences, yes on the page, yes on the command, and no on Hello Archive. She did not read the curve.

### Edith Cho

She reads the printed page to her sister on Sundays. She heard 14 against a file that keeps both ends. She heard 90 against a function that returns 365. She heard 31 February spoken as 3 March. She heard Saved against a menu that said Midnight.

- "If the file keeps today and the day 14 days earlier, you say 15. I counted 18 October through 1 November. You do not tell me 14, and you do not tell me 90. The longer one is 1 November through 1 November. That is 366."
- "The page has to have that day on it. Fifteen lines, and the sentence says 15. If the longer history is on, the page still says 15, and the other sentence says 366. I will read both."
- "If the phone keeps 100 lines, you say 100. You do not say 15 for a list that is not 15."
- "31 February is not a day. You do not tell me it is 3 March. The sentence that says it was not saved is true. I will read that."
- "If the option says Midnight, the next sentence says Midnight. You do not tell me Saved, and you do not tell me zero."
- "I will not read eleven dollars and ninety-nine cents off the paper."

She voted yes on the sentences, yes on the page, yes on `hello kept`, yes on the phone's hundred, and yes on the day-start words. She voted no on Hello Archive. The price is not on the paper. The kept sentence is not on the paper. Print still shows the fridge section and hides the rest. She did not sit with a screen reader. She initialed the 15, the 366, the page line, the command, the not-a-day sentence, the hundred, and the unchanged audit sentence.

## What shipped

Version 1.75.0.

The menu, What I did, `hello kept`, the README, the enterprise note, and the rollout note say 15 for the short window and 366 for the longer one. What I did lists those 15 days. A longer history does not add lines to that page. `hello kept` reads the notes, names today after the saved day start, prints the same page sentence and the file sentence, and does not write the notes. One date after the command says whether that day is inside the file's window. `2026-02-31` is named as not a day. Any other extra words are not printed, not saved, and not sent. A sync merge drops a finish outside the window before the save.

On the phone, a date that is not a real day is not kept and is not renamed. Settings, which starts closed, has a button that says the phone keeps the last 100 finished lines. Choosing a day start says the option's words. The morning screen does not change. The printed page does not change.

The vote on saying 15 and 366, and on listing the 15 days, was 5 to 1, Vance against. `hello kept` was 6 to 0. Refusing a date that is not a day was 6 to 0. The phone saying 100 was 6 to 0. The day-start words were 6 to 0. Hello Archive was 1 to 5, Vance for. The amount he asked was $11.99. No fifth noise was proposed.

## What did not ship

- Removing streak notes, sync, reminders, the kazoo, the trombone, the airhorn, the bell, the duck, the shift command, or the stubs.
- A fifth noise. Nico did not ask. Nobody else asked.
- Hello Archive, an $11.99 line, or the 366 days behind a price. Vance asked. The vote was 1 to 5.
- Leaving the menu on 14, or the list on 90. Vance asked. The vote was 5 to 1.
- A 366-line What I did. The page stays the short window and says 15.
- Dropping real finishes off the phone after 15 days. The phone keeps 100 and says 100.
- The 15, the 100, or the kept sentence on the morning screen, or on the printed page.
- A new question before the plan.
- A card form, a processor, or any charge that leaves the machine.
- A claim that an outside lab reviewed the sync encryption.
- A change to the sync salts, the round count, or the blob layout.
- A reader for `dacl-transfer.txt`. The file is still the operator's paper. He does not sign it.
- A rewrite of the pilot table's "last 60 days". That line stays the record of that round.
- A decoder for a hex certificate subject. A symbol that only looks like a space is not stripped. A name the fold cannot read stays the deploying organization's.

## Outcome

Two medium findings are fixed. Three low findings are fixed. Reed Mallory did not veto a feature. Nothing on this sheet is accepted by him. The hex subject and the lookalike space stay off his name. The new panel did not ship a noise and did not ship a stub. The sentences say 15 and 366, the page lists 15, and 31 February is not a day. Vance Harlow's defendable cash from the stubs is still $0. The upload address was not changed.
