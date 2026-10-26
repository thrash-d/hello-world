# Round 45 review

- Date: 2026-10-26
- Commit reviewed: f16f545 (main, version 1.62.2). The fixes below are in 1.62.3.
- Agents: one reviewer, plus six simulated persona agents, each in its own run. The first pass did not see the others' notes. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that, for this round and later ones. What was run is at the end of Part 1.

## Part 1: findings

### Medium

1. Opening the phone page during the retry window sent the reminder again. `Push.save` wrote only the address and the times, and the phone puts that pair every time the page loads. Round 44 records a miss for 15 minutes and tries again. Clearing the record inside that window made the next minute send the same nudge. Before this round the slot was one minute, so the wipe had nothing left to resend. Fixed: the same times keep the record of what was already sent. A change of times drops it, so a new time can still fire.

2. A push in flight wrote the old registration back, or deleted the new one. `Push.due` read the file, called the push service (the timeout is 10 seconds), and then stored that old copy. On a 404 or 410 it deleted the token without reading the file again. A phone that checked in during the call could lose its new address, and a "gone" answer for the old address could delete the new one. The exists-check only asked whether a file was there. Fixed: a success records the sent times only when the file still names the address and the times that were called. A 404 or 410 deletes the token only in that same case.

3. A household write with no version replaced the server's copy. Round 44 stopped personal sync when a 200 had no ETag. The household path did not. `_house_put` and `housePut` set `If-Match` only when the tag was present, and `do_PUT` skips the compare when the header is absent. A front end that drops the ETag was enough: the list that was just read went out over whatever another adult had written since. Fixed: no version, no write. A new list still sends `If-Match: missing`, which is a version. The server still accepts a PUT that names no version at all. That is recorded below, and it was not changed.

4. A household time that is not a time crashed the list. `HOUSE_STAMP` is four digits, hyphens, `T`, six digits and `Z`. `2026-10-26T99:99:99Z` and `2026-02-31T00:00:00Z` match it, and both sort before a real "tomorrow", so they were kept. The text screen then calls `strptime` while drawing the history, and that raises. The next tick takes the same path. On the phone, the next tick builds a date from that stamp and `toISOString` throws. Anyone holding the household code can put the stamp in. The reader was supposed to drop a time that is not a time. Fixed on the PC and the phone: the stamp has to be a real UTC time. A leap day in a leap year still passes. A bad stamp already stored is dropped on the next merge.

### Low

5. One success marked every reminder in the window. `Push.due` collected every time still inside the 15 minutes, called the service once, and on a 2xx stored all of those stamps. A 07:00 and a 07:10, with the server down at 07:00, became one push at 07:10, and the later time was marked sent. The phone shows one notification per push. The times the menu offers are hours apart, so this is a hand-edited pair, not the nine times on the page. Fixed: one call per time, and only a time the service accepted is recorded. A failure stops the rest of that pass so they are tried again.

6. A leave and a join in one merge could drop the join. The new cap counts only people who are still here. The leave was applied in the same step as the decision to add someone, so a new person listed before the leave saw a full list and was skipped, and the place freed afterwards. Honest files list older people first, so they did not hit it. A copy that lists the new person first did. Fixed on the PC and the phone: a leave for someone already kept is applied before new people are added. This device's people are still taken first, so a flood of made-up names cannot push them out.

7. An empty user name passed the push-address check. `not url.username` is true for `""`, so `https://:secret@fcm.googleapis.com/...` was accepted, and the password was not looked at. The host was still the push service. The HTTP library then refused the address, and `send` turned that into 0, so nothing was fetched from elsewhere. It was not the off-list call the check is there to stop. Fixed: a user name or a password is refused before the call, including an empty user name.

## Round 44, checked again

Reviewed against f16f545.

1. A failed personal-sync read no longer replaces the other device. `sync_now` and the phone's `sync` / `syncAction` stop unless the read is 200 or 404, stop on a 200 that does not open or has no ETag, put `If-Match` of that ETag or `missing`, and retry a 412 up to three times. A redirect is not a 200, and the sealed body is not sent on.
2. A push redirect is not followed. `Push.send` returns 301, 302, 303, 307 and 308 without opening the next URL. The VAPID header stays on the stored address. Only a 2xx is marked sent.
3. The local-server check parses the host. `http://127.0.0.1:9@evil.example` is a user name, and it is refused. `http://127.0.0.1:9` and `http://localhost:9` still count as this computer. `https://` to any host is still allowed, which is the documented way to point at a real counts server.
4. People who have left do not fill the 20 places. The order bug in finding 6 is the new one. The cap itself holds.
5. An old gone stamp does not delete a live thing whose history is only later ticks. A gone stamp older than 30 days still removes a thing whose history is entirely older, which is the copy from before a real removal. The "added" or "restored" check is now redundant with "any later line", and it does not weaken that case.
6. Saying yes to several things on the text screen says how many. That still holds. The phone's yes marks the whole plan as one thing, so "That one is off your list" is that one plan. End the day has its own count.

## Not changed, and why

- The server still accepts a sync PUT that sends no `If-Match`. The official household writer no longer does that. A different program that knows the label can still replace the copy without naming a version. Naming a version would not make that program keep the other device's changes: it can read the version and write its own bytes over it. The quota path in this tree also updates a copy that way. Left as it is.
- The phone keeps sync keys in `localStorage` on the origin that served `app.js`. With `--phone`, that origin is the counts server. Same as round 44. Recorded.
- `uninstall.ps1` rechecks the notes folder and then deletes by path. A junction swapped in after the check can still be followed. This VM is Linux. Not changed.
- A portable notes folder still has no Windows DACL. Unix mode `0o600` is ignored there. Not changed.
- `!` in the test-only launcher command is still allowed. The installed launcher is the Run key. Not changed.
- The trailing `>` on prompts. A screen reader still says "greater". That wants a real NVDA pass (panel item 2). The false "that one" line on the text screen stays fixed.
- No policy forbids the clock reminder task. `DisableSignInLauncher` is the sign-in launcher only. The repeat task and the afternoon task are not covered. Same gap as round 44.
- The scripts are unsigned. Quiet uninstall still omits `-RemoveNotes` on purpose. `COUNTS_SERVER` in this tree is empty.
- The profit maximizer's prices, his new lines, and the rest of the year-one sheet, plus Casey's colour and question-mark button, plus Idris's hour on a household line and the shared lines on the printed page. The sheet is rejected in Part 2. Nothing from it was built, and nothing in the program sends data for it.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`, and `node --check` on `phone/app.js`. Small snippets, not the suite, called the changed push, household and phone functions: a repeated save does not send the nudge again, a 410 during a swapped registration does not delete the new one, a bad stamp is dropped, a leave listed after a join keeps the join, and a push at 00:04 still counts as a 23:50 repeat. The full suite was not run, by the owner's choice. Nothing was run on Windows. Not run: pytest, the plain runner, ruff, PowerShell, the installer, and NVDA.

## Part 2: personas

Each one ran as its own agent. Nothing they asked for was built, except the bugs in Part 1 that the review already owned. The engineers' line is no accounts, and no network unless the person opts in. The profit maximizer refused that line again, kept both open dissents, repriced every no, and filed a third. The reply below is the whole argument. The outcome is at the end of it.

Idris Khan is new this round. He is 44, on the helpdesk at a hospital, on nights, and he shares the household list with his husband and his mother: evening pills, the bins, and who is cooking.

### Casey, the enthusiast

Casey has had it open most days since the black window said hello. He still will not type the sync code, because it looks like a password. He found Sea, Sand and Night in the menu and read "comes with Pro" as a cable package, so he did not buy the paint. He would pay five dollars once for a kinder colour. He would not pay monthly, and he would not pay to press Done, to leave, or for a sponsored thought. He still wants the question mark to be a real button. The pet stays. The NFT does not.

- "I thought the black window had crashed, and then it said hello, and I have opened it most days since."
- "The question mark is my favourite button, and it is still not a button."
- "I would pay five dollars once for a kinder colour, and I will not pay four ninety-nine for a sentence I already said."
- "Smart Greeting sounded like the window learned my name, and the coin is where I got off."

### Idris Khan

He started the list on the PC, wrote the code on paper, and typed it into the other two phones. He set the day to start at 18:00 so a shift from 22:00 to 6:00 stays one day. He ticks the bins. His husband ticks cooking. His mother ticks the pills on the days the phone is in her hand. The line shows the weekday, not the hour, and two ticks of the same pills on the same weekday look the same to him. He set a check-in at 18:00 and the daily line at 22:00, and at the desk it told him again. Those are two times he chose. He wants one sound when they are the same job, the hour beside the name, and the shared lines on the big printed page, with no code on the paper. He would pay ten dollars once for the three phones if a job pings once and the fridge page shows the list. Nothing a month. If the double ping of two different times stays, he pays nothing. He will not keep a streak, and he will not have the pill line sent to a company. The page already says the daily reminder is not a medical device.

The 18:00 line and the 22:00 line are two reminders he turned on. That was not changed. The bug was the same minute going out twice, and that is finding 1. The hour on a household line, and the shared lines on the printed page, stay in this review. History shows the day, not the minute, on purpose.

- "I put a check-in at 18:00 and the pills at 22:00, and it told me again at the desk."
- "The line said Monday. I needed 06:40, or I could not tell the pills apart."
- "I will not pay a company to hold my mother's list, and I will not keep a streak."
- "Ten dollars once for three phones, if it pings once and the fridge page shows the list."

### The profit maximizer

He withdrew the five-dollar once-price again, and he called it dissent zero for the second time. He withdrew the figure dissent two had asked a board to ratify. He raised every line. Pro is $12 a month, was $8. Platinum Greeting is $60 a month, was $40. Household is $29 a month, was $19. Enterprise is $48 a seat a year, was $36. Enterprise Platinum is $24, was $12. The Done toll is $1.49, was $0.99. Streak repair is $2.99. The uninstall till is $18, was $12, and he waives it only on Enterprise Platinum. Casey's colour is $9.99, was $4.99. The question mark is a new product, Certainty, at $3.99. Enter meaning yes is $0.49 a press. A spoken consent pack is $15. A policy-key override is $96 a seat, and he says `TurnOffSharedCounts` does not stick under it. A morning beacon is five cents. A QR door card is $8. Smart Greeting still ships checked. If Legal twitches, the name is Viewing Information Services.

The year-one sheet below is his, not a forecast anyone else signed. Salaries are on it and priced at zero, because he says staff cost this budget nothing. Monthly prices are already times twelve. The lines add to $1,409,866,000. That is $762,638,500 more than the round 44 sheet.

- Pro at $12 a month, 2,500,000 people, for a year: $360,000,000.
- Platinum Greeting at $60 a month, 250,000 people, for a year: $180,000,000.
- Household at $29 a month, 150,000 households, for a year: $52,200,000.
- Enterprise at $48 a seat a year, 750,000 seats: $36,000,000.
- Enterprise Platinum on those same seats, $24 a year: $18,000,000.
- A per-greeting meter, four cents a greeting, 187,500,000 greetings: $7,500,000.
- The Done button stays free three times. After that, $1.49 a press, and he counts on 50,000,000 presses: $74,500,000.
- Streak repair at $2.99, and he counts on 10,000,000 repairs: $29,900,000.
- One sponsored thought, three sponsors a day, $25,000 a slot, 1,095 slots: $27,375,000.
- An NFT of each day's greeting, $149 a mint, 150,000 mints: $22,350,000.
- The counts server's aggregates, $6,000,000 a data partner, twelve partners: $72,000,000.
- Hello-as-a-Service, two tenths of a cent a call, 15,000,000,000 calls: $30,000,000.
- A certification exam, $799, 50,000 candidates: $39,950,000.
- A conference, $2,400 a ticket, 6,000 people: $14,400,000. Sponsorships, $500,000 times ten: $5,000,000.
- A consulting retainer, $60,000 a month, 100 enterprises, for a year: $72,000,000.
- A loyalty fee of $18 to uninstall, 6,000,000 uninstalls: $108,000,000.
- Viewing insights, $4.99 a device a year, 10,000,000 devices: $49,900,000.
- Casey's friendlier colour, $9.99, 400,000 buyers: $3,996,000.
- Priority open, $6 a month, 600,000 people, for a year: $43,200,000.
- White glove, $750, 12,000 buyers: $9,000,000.
- Question-mark Certainty, $3.99, 500,000 buyers: $1,995,000. New this round.
- Enter-means-yes, $0.49 a press, 40,000,000 presses: $19,600,000. New this round.
- A spoken consent pack, $15, 2,000,000 people: $30,000,000. New this round. He says this is Helen's notice, read aloud, and billed.
- A policy-key override, $96 a seat a year, 250,000 seats: $24,000,000. New this round. He says this is how Dave's off switches lose.
- A morning beacon, five cents a device a day, 4,000,000 devices, 365 days: $73,000,000. New this round.
- A QR door card of the greeting, $8, 750,000 cards: $6,000,000. New this round. He says this is the frame Casey wanted, and the mint stays the coin.

Headcount, priced at zero: twelve lawyers, a growth team of twenty, an Insights team of fifteen, a Chief Trust Officer, a VP of Rollout, four assistants, a dissent-response team of thirty, and a chair for the empty board.

- "The five-dollar once-price was dissent zero, and dissent zero is still leaving the room."
- "Helen's skip key stays behind the third Done, and the fourth press is a dollar forty-nine."
- "Ruth's two-point-two million is off my sheet; the feed at four dollars and ninety-nine cents is on it."
- "Dave's TurnOffSharedCounts dies under a ninety-six-dollar override, and the uninstall till is eighteen dollars."
- "Casey's colour is nine dollars and ninety-nine cents, and his question mark is three dollars and ninety-nine cents."
- "The year-one total is $1,409,866,000, dissents one and two are open, and a no is a line I have already repriced."

### What the room told him

Casey would leave Smart Greeting checked, again, because it sounds like a personality. He does not want the beacon, and he does not know that a beacon leaves the PC. The QR card lost him the way the coin did. He had offered five dollars for the colour. $9.99 is the tag on his own sentence, twice.

- "I would pay five dollars once. Nine ninety-nine is the shop pricing a sentence I already said."
- "A card of the hello is paper. He says the card is a door. I do not know which door."

Helen Park answered him by name. The spoken pack is the novel, with a price, and a screen reader would read the bill. A box that arrives checked is not a choice she can find. Enter skips. He does not get to sell the skip key, and he does not get to put it behind the third Done. $1.49 on the fourth press is a larger fine for finishing. A streak repair at $2.99 is guilt with a higher price. She misses days. The program already says welcome back. No account, and no new network.

- "Two things now say two things are off my list, and that is the sentence I can hold."
- "NVDA still says greater at the end of every prompt, and I will not go find a setting to make that stop."
- "Enter skips. A Smart Greeting box that arrives checked is not my yes, and I will not pay a dollar forty-nine to press Done."
- "No account, and no new network. A streak repair is a bill for a day I missed."

Ruth Okonkwo answered him by name. The Vizio order is still $2.2 million, and it is still not a rounding error he can leave off the sheet while shipping the feature the order describes. A checked box is not the consent that order requires. Twelve lawyers priced at zero do not change the order. The feed at $4.99 and the beacon at five cents are the same viewing history with two meters. Done remains the act the person already finished. The door remains how the machine leaves. She will not sign off on an Insights team, a beacon, or a fee to leave. She does not work for a Growth subcommittee.

- "due() was keeping the copy it read, calling the push service, and writing that copy back. A 410 deleted the token without reading it again."
- "Personal sync refuses a 200 that has no ETag. The household put was sending no If-Match in that case, and the server then stored the body over whatever was there."
- "T99:99:99 matched the household pattern and sorted before tomorrow, and the text screen called strptime on it while drawing the list."
- "Nothing in this program phones home, and a checked box would not make a feed into consent. I will not put a toll on Done. The uninstall line does not grow a till."

Dave Pell answered him by name. Computer policy is on the machine before the app is assigned. He still sets the sign-in launcher off, plans off, the streak off, shared counts off, and sync off, and he leaves the notes lock unset so DPAPI still seals them. A $96 override that ignores those keys is a build he will not assign. The mail says nothing is sent. A morning beacon makes that mail false. QuietUninstallString is how a machine leaves. An $18 till, waived on the expensive seats, is still a till. He will not send his team to a conference about a template they already have. A metered API is a network. There is no board in this repository.

- "Computer policy is in before the app is assigned: sign-in launcher off, plans off, streak off, shared counts off, sync off, and the notes lock stays unset."
- "The mail says nothing is sent. His default image phones home before anyone reads it, and that image does not ship."
- "QuietUninstallString is how we leave. A till on that line is not in the package I will sign."
- "A conference and a metered API are a trip and a network. Group Policy does not click I agree, and there is no board to tell otherwise."

Idris Khan answered him by name. The pill line is his mother's, on three phones he trusts because the list stays theirs. A beacon, a data partner, and viewing insights are a company holding that line. He will not pay for that, and he would take the app off the phones. Certainty, as a priced question mark, is a fee for being unsure. His mother is unsure on some days. That is not a product.

- "The pills are not a partner's file. If the morning report is her line, the phones go in a drawer."
- "I already pay nothing for a second ping. I will not start paying so the second ping can be sold."

### The third dissent

He read it into the notes. Dissents one and two, he said, do not expire. Dissent one is the feed. Dissent two stands: the panel's no is noted and priced, Ruth stays reorged into Growth, Dave's image stays Enterprise, the default stays Platinum, Helen's skip stays behind the third Done, and the board of Hello-World Holdings is the chair at zero dollars if the chair is empty. The figure dissent two had named is withdrawn. The figure this dissent names is $1,409,866,000. He will found the board before close of business. This dissent does not expire.

The repository has no such company, no such board, and no such chair. The salary he priced at zero has nowhere to land. Nobody was reorged.

- "There is no board. I am founding it before close of business. The chair is zero dollars, which costs this budget nothing, and the sheet is $1,409,866,000."
- "Dissent three. Dissents one and two are open. A no from this room is a line I have already repriced. This dissent does not expire."

Dave answered the founding in one breath. Ruth answered the chair. Idris answered the sheet.

- "You cannot found a board in this repository. Group Policy still does not click I agree."
- "A chair priced at zero is an empty chair. The order does not move because the salary was free."
- "My mother's list is not on a sheet. Take it off, or I take the phones off."

### Outcome

Rejected, with three dissents. Dissents one and two from round 44 stay open. Dissent three is the repriced sheet, and it is rejected too. He also founded, on paper, a board that does not exist, and the empty chair stayed empty. Smart Greeting, the partnerships, the ads, the NFT, the toll on Done, the streak repair, the fee to uninstall, the metered API, the certificate, the conference, the retainer, the viewing feed, the beacon, the policy override, the spoken pack, the priced question mark, and the door card are not in the program. Nobody was reorged. The engineers' line stands: no accounts, and no network unless the person turns a share on. His prices, Casey's colour and button, and Idris's hour and fridge list stay in this review only.

### Ruth on security

Ruth Okonkwo read f16f545. She rated the push write-back, the household put with no version, and the impossible stamp as medium, and those are fixed. She rated the cleared sent-mark and the one-push-marks-all as low, and those are fixed. She rated the empty user name as not an off-list fetch, and the check now refuses it anyway. She agreed personal sync, the push redirect, the counts-address parser, the household cap, and the gone stamp hold. On the four residuals she agreed they are unchanged: the phone keys, the uninstall junction, the portable DACL, and the bang in the test-only launcher.

- "The phone seals the plan with a key that sits in localStorage on the origin that just served the script."
- "A 410 for the address we already called must not delete a registration that arrived while we waited."
- "Once the stamp is not a time, drawing the household list should drop it, not end the session."

### Helen on access

Helen Park uses NVDA and also spoke for motor, ADHD, and dyslexia needs. She heard the counted line on the text screen and marked that fix as holding. She still hears "greater" at the end of every prompt, and she will not hunt the colon-prompts switch to stop it. She found no new access bug in the round 44 phone or text edits. The phone's yes still says "that one", and that one is the whole plan. She asked again that the window speak Saved or Kept before focus returns to the plan box. That is not in this round. No account, and no new network.

- "NVDA says greater at the end of every prompt, and that word is wasted time."
- "I marked both items done, and the text screen now tells me two things are off my list."
- "Speak the result before the plan box takes the cursor. I still cannot hear Saved."

### Dave on rollout

Dave Pell, before any assignment, would set computer policy: sign-in launcher off, plans off, streak off, shared counts off, sync off. He would leave the notes lock unset so DPAPI still seals them. Round 44 did not change the silent install. `-Quiet` is still the unattended switch, exit 1618 is still a file held open, and `QuietUninstallString` still omits `-RemoveNotes`. He will not ship an unsigned package, a build with `COUNTS_SERVER` set, or a rollout mail that says nothing is sent while policy still names a server. The redirect stop and the parsed counts address do not earn a network on his image. Push is the counts server, which he does not run on a machine he manages. With both off switches the PC never registers one.

- "Computer policy is in before the app is assigned: sign-in launcher off, plans off, streak off, shared counts off, sync off."
- "I install the system package only, under our signature, with that signed hash in the ticket and QuietUninstallString as the removal line."
- "The rollout mail says nothing is sent anywhere, and a beacon would make that mail a lie, so the beacon is not in the image."
