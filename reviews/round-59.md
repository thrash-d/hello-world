# Round 59 review

- Date: 2026-11-01
- Commit reviewed: 0b4b2e1 (main, version 1.75.0, pull request 110). The fixes below are in 1.76.0.
- Agents: one reviewer, plus the six sitting personas. The October panel and every persona retired in round 50 were not in the room and they did not vote. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- Reed Mallory does not veto. Nothing already in the program was removed. He accepts no residual. A cell is fixed, or it is mitigated and the name on it is not his.

## Part 1: findings

The room started from the program as it stood in 1.75.0. Edith Cho opened This week on Sunday, 1 November 2026. Monday of that week is 26 October. She counted 7 days. The page counted a finish dated 15 November as this week, and This year's November line counted it too. The file kept a finish up to 365 days ahead. `hello kept` already said that day was not inside the 15 days. Nico Paredes put 31 November on the sideways list and the smaller-plan question came up. Reed Mallory put a device date of year 9999 on the sync list, and he read the server's "a year" against a sweep of 366 days. Bex Calder wanted the 7 on a line she could point at.

| # | Severity | Where | What | Status in 1.76.0 |
| --- | --- | --- | --- | --- |
| 1 | Medium | This week, This year, the notes file | A finish after today was counted as this week and kept for up to 365 days ahead. The 15-day sentence already said it was outside | Fixed. It is not counted, and it is not kept |
| 2 | Medium | sideways days, letters | `2026-11-31` counted toward the smaller-plan question. `2026-02-31` was kept as a letter's date. On the phone a later day counted, because a negative gap is less than 7 | Fixed. A date that is not a day is dropped. A later day is not one of the 7 |
| 3 | Low | sync and push sweep | The sentence said a year. The code removes a copy only after more than 366 days. A copy last touched exactly 366 days ago stays | Fixed. The sentences say more than 366 days |
| 4 | Low | devices on a sync copy | A seen date of 9999-12-31 sorted first and stayed newest. A sync clock already refuses a time more than a day ahead | Fixed. The same limit applies to the seen date |
| 5 | Low | household comment, phone comment | The household memory comment said a year. The subtraction is 366 days, and that day's stamp is kept. The phone comment said the history is the day, not the minute. The stamp and the README include the time | Fixed. The comments match the code |

### Fixed

1. `week_text` kept every finish dated on or after Monday, with no far end. On 1 November 2026 that Monday is 26 October, which is 7 calendar days through Sunday. A finish on 15 November, or on 1 December, was one of "this week." `year_page` did the same for a later day in the current month. `load` kept a finished row through today plus 365 days. `merge_sync` dropped a finish from 2019 and kept one that was already in the file and dated after today. The two-window save wrote that row back. The window's far end is today. `finish_in_window` is that test. Load, the sync merge, and the two-window save all use it, and they use it before the cap, so a later day cannot push a real line out of the list. This week now starts with the span. On Sunday, 1 November 2026 the line is "This week is 7 days, Monday, 26 October 2026 through Sunday, 1 November 2026." On Monday, 26 October 2026 the line is "This week is 1 day, Monday, 26 October 2026." The finish count is the next sentence, and it counts only those days. Last week, when it has a finish, says "Last week is 7 days," Monday through Sunday. This year says "Through {date}." A later day in November is not in November's count. `keep_days` is unchanged. 18 October is still kept on 1 November. 17 October is still dropped.

2. Sideways days were kept when the text matched `YYYY-MM-DD` and sorted on or before today. `2026-11-31` matches that shape and is not a day. Three such strings in the last 7 days made `smaller_due` true. Letters used the same shape, so `2026-02-31` was stored. The phone already refused that shape for a letter. Its sideways check used `daysBetween(day, today) < 7`, and a later day has a negative gap, so it counted. A stored day is now a real calendar day, and it is not after today. The recent window is today and the day 6 days earlier, both ends, which is 7 calendar days. A later day is not one of them. The smaller-plan question does not come up from a date that is not a day.

3. `SYNC_DAYS` is 366. The sweep, the push forget, and the sync read all use `mtime` older than `366 * 86400` seconds. A copy last touched exactly 366 days ago stays. From 1 November 2026 back to 1 November 2025 is 365 days. The module text, the README, and the sweep's own note said a year. They now say more than 366 days, and they say the equal day stays. The growth files were already "older than 30 days," which keeps the file from exactly 30 days ago. That note now says the equal day stays too. The number of days was not changed.

4. `merge_devices` accepted any real date. `9999-12-31` sorted ahead of a device seen today and stayed the newest entry for that id. A sync clock already stops at one day ahead. The seen date now stops there too, on the desktop and on the phone. A date of tomorrow is still kept. A date of the year 9999 is not.

5. `house_tidy` subtracts `HOUSE_GONE_DAYS`, which is 366, and keeps a stamp on that day (`>=`). The comment said a year. It now says 366 days, and that the stamp on that day is still kept. The phone comment said each household line keeps the day, not the minute. The stamp is the weekday and the time, which is what the README already says. The comment now says that. No retention number moved.

### Also looked at, and not a finding

- What I did still lists 15 days and says 15. A longer history still says 366 for the file and 15 for that page. This round did not change `keep_days`.
- The phone still keeps the last 100 finished lines that remain after a later day is dropped. It does not switch that list to 15. The sentence says 100, and it says a later day is not kept.
- `PRO_KEEP_DAYS` is still unused. Pro does not change the day window. The README still says history stays free. This round did not put the year behind Pro.
- A hex-encoded subject is still not decoded. A symbol that only looks like a space, and is not a format character and not a space, is still not stripped. Both stay the deploying organization's. He does not accept either one.
- `docs/PILOT.md` still says the last 60 days. That table is the record of the pilot round. This round did not rewrite it.
- Quiet uninstall still omits `-RemoveNotes`. Notes stay unless the operator asks.
- `dacl-transfer.txt` is still written blank. Nothing reads the acceptor line back.
- Streak notes, sync, reminders, the kazoo, the trombone, the airhorn, the bell, the duck line, and the six stub prices are still there. `charged` is still false. No card form was added. No seventh price was added.
- The default upload is still `https://insights.example.invalid/v1/growth`.
- The printed page has no new line. The week sentence is not on it. The fridge title is still the day.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`. `node --check` on `phone/app.js` and `phone/sw.js`. The translation files parse as JSON, and every language file loads, including the two regional ones. Small snippets, not the suite. Notes were only under a temporary folder. The phone page was opened in Chrome from a local static server.

`hello.VERSION` and `VERSION` are `1.76.0`. The phone's `APP_VERSION` is `1.76.0`. The service-worker cache name is `hello-world-phone-v22`.

On 1 November 2026, `week_span_days` is 7. The sentence is "This week is 7 days, Monday, 26 October 2026 through Sunday, 1 November 2026." On 26 October 2026 it is 1, and the sentence is "This week is 1 day, Monday, 26 October 2026." Last week is "Last week is 7 days, Monday, 19 October 2026 through Sunday, 25 October 2026." A list that held bread on 26 October, bins on 1 November, a finish on 15 November, a finish on 1 October, and `2026-02-31` produced two lines under this week: bread and bins. November on This year counted bins and did not count 15 November. The through line named Sunday, 1 November 2026. `2026-10-18` is inside the 15 days. `2026-10-17` is not. `2026-11-15` is not. `real_day("2026-02-31")` and `real_day("2026-11-31")` are empty.

A notes file that held those finishes, a letter on 31 February, a letter on 1 December, sideways days of 31 November and 1 December, an unsure note on 15 November, a plan put aside on 1 January 2027, and a device seen in the year 9999 was read and not rewritten. The file that came back held bread, bins, the 1 November letter, sideways days of 1 November and 26 October, the unsure note on 1 November, the plan put aside on 20 October, and the kitchen device. The year-9999 device was not in the list. Three strings that are not days did not make the smaller-plan question due. Three real days in the 7 did. A merge that was handed a finish from 2019 and a finish from 2027, and that already held 15 November and 1 November, kept 1 November.

`hello week secret pills`, with that folder already there, printed the greeting, the 7-day line, the two finishes, and "That is not a day. It was not saved." It did not print secret, and it did not print pills. The notes bytes were the same after. The ledger line was `week`, version `1.76.0`, `network` false, `charged` false, `stub` false. It did not contain bread, bins, secret, or pills, and it did not contain a field for the date that was asked about. The Spanish sentence names 7, lunes, 26 de octubre, and domingo, 1 de noviembre. The French sentence names 7. The other languages were given the same placeholders. On the text screen, Chinese, Japanese, Korean, Arabic, and Hebrew stay in English, which is the old rule. With the window flag on, those files supply the week sentence.

On the phone, the span for 1 November 2026 is 7 and the span for 26 October is 1. `2026-02-31` is 0. A list that held a later day still said "You finished 2." One hundred real days plus a day in December parsed to 100 lines, the first of them 1 January, and the December day was not one of them. A merge kept a finish from 2019, which is a real day, and dropped 31 February and a day in 2027. A device seen in the year 9999 was not kept. A later day is not one of the recent 7. Today is.

In the browser, the page date was Sunday, November 1, 2026. Settings started closed. The week button was not on the main screen until Settings was opened. The status after the click was "This week is 7 days, Monday, October 26, 2026 through Sunday, November 1, 2026. Nothing finished yet this week. That is fine." The kept button said "This phone keeps the last 100 finished lines. A date that is not a real day is not kept. A date after today is not kept." Neither status named a price or a plan. The fridge section was not showing the week sentence. The first-open streak-notes box was on the page because the phone had no saved consent. This round did not add that box. This check did not measure a speaker.

Not run: pytest, the plain runner, ruff, PowerShell, `Add-Type`, Authenticode, the installer, a Windows access list, a live public host, and NVDA. Edith did not sit with a screen reader this round, and this file does not say she did. Nothing was run on Windows.

## Part 2: personas

The six sat on the program as it stood in 1.75.0. Edith put the week count and the word "year" on the table. Bex wanted the 7 where a camera can hold it. Nico tried 31 November and did not want a fifth noise once he had counted the four he already had. Reed wanted the file to match the sentence before it was saved. Amina asked whether the morning gained a question.

### Reed Mallory

Former Marine staff sergeant. He was a communications clerk, then he made slide decks for a contractor and started calling himself CISO. Mallory Assurance is him and a bookkeeper. He does not veto. He will not write the word accepted.

- "Monday through Sunday is seven days. I counted 26 October through 1 November. A finish on the 15th is not one of them. Drop it before the save. Do not let it take a slot from a real line. Do not push it."
- "The page has to say seven on Sunday and one on Monday. Last week is seven. Say seven. Do not tell me a year when the clock is three hundred sixty-six and the equal day stays."
- "Thirty-one November is not a day. Do not count it. Do not keep it as a letter. A date in the year 9999 does not get to be the newest device. One day ahead is the limit you already use for the sync clock. Use it."
- "Fine. A command can say the numbers. It reads the file. It reads the hour, then the clock, the way the morning does. It does not write the file. The extra words are not a plan. If they are not one date, they are not on the screen and they are not in the ledger. The phone button stays inside Settings. The note is the word week. I will not sign an eight ninety-nine receipt. I am not the acceptor on a hex name, and I am not the acceptor on a mark that only looks like a space."

Sign-off sheet, as he read it back. The word accepted is not on it.

| Line | What the code does after 1.76.0 | His mark |
| --- | --- | --- |
| Kazoo | Prints. Does not save. Does not open a socket | Signed. Still not a finding |
| Duck (`hello ai`) | Says it is not a model. Extra words are not read, not saved, and not sent. The line is the date's line. The next sentence names that date | Signed. He will not sign the word model |
| Trombone, airhorn, bell | Print. The phone may start a tone and says whether it did. No fetch | Signed. The tone is not a voice |
| `hello shift` | Reads the notes. Names the menu's hour. Does not write. Does not read the clock | Signed |
| `hello kept` | Reads the notes. Names today after the saved hour. Says 15 for the page and 15 or 366 for the file. Does not write the notes | Signed |
| `hello week` | Reads the notes. Says 1 through 7 for Monday through today. Says 7 for last week when that week has a finish. Does not write the notes. A word that is not one date is not printed. The ledger has no plan and no asked date | Signed |
| Repair $2.99, Pro+ $9.99, Priority Hello $4.99, Hello Encore $3.99, Hello Spotlight $7.99, Hello Ring $6.99 | Local stubs. `charged` false. `stub` true. No seventh receipt | Signed. Cash collected: $0 |
| This week | Monday through today. Sunday is 7. Monday is 1. A later finish is not in the count | Fixed |
| The file's far end | A finish after today is not saved back | Fixed |
| Sideways days and letters | A date that is not a day is not kept. A later day is not one of the 7 | Fixed |
| Sync and push sweep | More than 366 days. The equal day stays | Fixed |
| Device seen date | Not more than a day ahead | Fixed |
| Phone finished lines | The last 100 that remain after a later day is dropped. The sentence says 100, and it says a later day is not kept | Signed |
| Phone week button | Inside Settings, which starts closed. The status has the day count and the finish count. It does not have the plan | Signed |
| Hex subject, and a symbol that only looks like a space | Not decoded, and not stripped. The name on it is the deploying organization | He does not accept it. It is not his |
| Outside crypto review | Screen still says no outside audit | Refused to sign "audited" |
| Streak-note upload | Still the placeholder until an operator points it elsewhere | Signed. Host unchanged |

He initialed the 7, the 1, the 366, and the not-a-day line. He initialed the hex limit and the lookalike-space limit again without reading the certificate encoding. The fence from round 51 is still the content security policy. He initialed it again without reading `connect-src`.

### Bex Calder

She films Unbox The Future from a spare bedroom in Tucson. She had This week open and she could not point at a number of days. She wanted that number on a command, and on the phone, in a place the camera can hold.

- "Seven is a number I can tap. One, on a Monday, is a number I can tap. Do not put a price on the week. A week is a week."
- "The phone button can live in Settings. I will open Settings. Don't take the AI button, and don't put the sentence on the morning."

She voted yes on the sentences, yes on `hello week`, yes on the phone button, yes on dropping a later day, and yes on saying 366. She voted no on Hello Weekly. She did not ask for a new noise.

### Vance Harlow

Staff salary is not on his sheet. He opened at $8.99. He wanted the seven days behind Hello Weekly, and he wanted the server to keep saying a year because a year sounds longer than 366 on a slide. He also wanted a finish dated next month to stay in the count, because a pipeline number looks like growth.

- "Eight ninety-nine. Weekly is the seven days. The cash from the stubs is still zero. A year sells. Three hundred sixty-six sells a correction. Next month in this week's count is a forecast."

He lost the gate on the seven days. He lost $8.99. He lost the word year, and he lost the later finish, 5 to 1. He voted for `hello week` itself, because a command is still a line on the slide, and for the phone button. The six receipts still say nothing was charged. The $5 Pro key and the $8 household key still need the owner's store. This round does not call it.

### Nico Paredes

He counted the noises again and stopped at four. He typed 31 November into the sideways list and watched three fake days ask for a smaller plan. He did not think that was the joke. He started a whoopee cushion, looked at the help line, and put it down.

- "Kazoo, trombone, airhorn, bell. A fifth one is a catalog. I am not adding a cushion. Thirty-one November becoming a smaller plan is the bug. Say it is not a day. If it costs money, it isn't funny."
- "Seven days and a finish from next month isn't a joke. A year and three hundred sixty-six isn't either."

He voted yes on the sentences, yes on `hello week`, yes on refusing the date, and yes on saying 366. He voted no on Hello Weekly. He withdrew the fifth noise before it was put to a vote. Nobody else picked it up.

### Amina Soule

She opens the bakery at 4:10. She asked one question, and then she voted.

- "Is there a new question before the bread?"

There is not. The smaller-plan question was coming up from dates that are not days. That path stops. `hello week` is a command. This week is the page she already opens when she wants it. The phone's button is inside Settings, and Settings starts closed. The morning plan is the same box as yesterday. The printed page does not gain a line. She voted yes on the sentences, yes on the command, and no on Hello Weekly. She did not read the curve.

### Edith Cho

She reads the printed page to her sister on Sundays. She heard a finish from 15 November inside a week that ends on 1 November. She heard "a year" against a sweep of 366 days. She heard 31 November counted as a day.

- "If Monday through Sunday is the week, you say 7. I counted 26 October through 1 November. On Monday you say 1. You do not tell me I finished the 15th this week."
- "Last week is Monday through Sunday. That is 7. Say 7 when you show it."
- "31 November is not a day. 31 February is not a day. You do not count them, and you do not keep them."
- "If the sweep removes a copy after more than 366 days, and the copy from exactly 366 days ago stays, you say more than 366 days. You do not tell me a year."
- "If the phone keeps 100 lines, you say 100. You also say a date after today is not kept, if that is what the phone does."
- "I will not read eight dollars and ninety-nine cents off the paper."

She voted yes on the sentences, yes on `hello week`, yes on the phone's hundred and the later-day line, and yes on 366. She voted no on Hello Weekly. The price is not on the paper. The week sentence is not on the paper. Print still shows the fridge section and hides the rest. She did not sit with a screen reader. She initialed the 7, the 1, the 366, the not-a-day sentence, the command, and the unchanged audit sentence.

## What shipped

Version 1.76.0.

This week, `--week`, the window's This week page, and `hello week` say how many days the week holds, Monday through today. Monday is 1 day. Sunday is 7. The finish count uses only those days. Last week says 7 when it has a finish. This year names today as the last day in the count. A finish after today is not kept. Load, the sync merge, and the two-window save drop it before the cap. `hello week` reads the notes, names today after the saved day start, prints that page, and does not write the notes. One date after the command says whether that day is inside this week. `2026-02-31` is named as not a day. Any other extra words are not printed, not saved, and not sent.

A sideways day that is not a day is not kept, and a later day is not one of the 7, so it does not make the smaller-plan question due. A letter dated on a day that is not a day, or on a day after today, is not kept. A device seen date more than one day ahead is not kept. The server's sentences say more than 366 days. A copy last touched exactly 366 days ago stays.

On the phone, a date after today is dropped before the last 100 lines are kept, and the sentence says so. Settings, which starts closed, has a button that says what this week holds. The status names the day count and the finish count. It does not name the plan. The morning screen does not change. The printed page does not change.

The vote on saying 1 and 7, and on not counting a later finish, was 5 to 1, Vance against. `hello week` was 6 to 0. Refusing a date that is not a day was 6 to 0. Saying more than 366 days was 5 to 1, Vance against. The phone button and the phone's later-day sentence were 6 to 0. Hello Weekly was 1 to 5, Vance for. The amount he asked was $8.99. No fifth noise was put to a vote. Nico withdrew it.

## What did not ship

- Removing streak notes, sync, reminders, the kazoo, the trombone, the airhorn, the bell, the duck, the shift command, the kept command, or the stubs.
- A fifth noise. Nico started one and withdrew it. Nobody else asked.
- Hello Weekly, an $8.99 line, or the seven days behind a price. Vance asked. The vote was 1 to 5.
- Leaving the server on the word year. Vance asked. The vote was 5 to 1.
- Keeping a finish dated after today so the week count would look larger. Vance asked. The vote was 5 to 1.
- The week sentence on the morning screen, or on the printed page.
- A new question before the plan.
- A card form, a processor, or any charge that leaves the machine.
- A claim that an outside lab reviewed the sync encryption.
- A change to the sync salts, the round count, the blob layout, or the 366-day sweep itself.
- A reader for `dacl-transfer.txt`. The file is still the operator's paper. He does not sign it.
- A rewrite of the pilot table's "last 60 days". That line stays the record of that round.
- A decoder for a hex certificate subject. A symbol that only looks like a space is not stripped. A name the fold cannot read stays the deploying organization's.

## Outcome

Two medium findings are fixed. Three low findings are fixed. Reed Mallory did not veto a feature. Nothing on this sheet is accepted by him. The hex subject and the lookalike space stay off his name. The new panel did not ship a noise and did not ship a stub. The week says 7 on Sunday and 1 on Monday, a later finish is not kept, and the server says more than 366 days. Vance Harlow's defendable cash from the stubs is still $0. The upload address was not changed.
