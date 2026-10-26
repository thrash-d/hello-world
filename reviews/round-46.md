# Round 46 review

- Date: 2026-10-26
- Commit reviewed: d51b699 (main, version 1.62.3). The fixes below are in 1.63.0.
- Agents: one reviewer, plus six simulated persona agents, each in its own run. The first pass did not see the others' notes. Quotes are simulations, checked against the program before anything was changed. No seventh persona. He hired one release engineer, and that hire was a line on his sheet, not a seat in the room.
- Redactions: none.
- The test suite was not run. The owner asked for that, for this round and later ones. What was run is at the end of Part 1.

## Part 1: findings

### Medium

1. The notification a server push shows was still a ten-minute window. Round 45 taught `pushText` in `phone/app.js` to treat fifteen minutes as near, including across midnight. The service worker is what the push actually displays, and `phone/sw.js` still used `Math.abs(...) <= 10` with no wrap at midnight. A daily repeat at 23:50, pushed at 00:04, showed the check-in line. So did a push eleven to fifteen minutes late. Fixed: the same fifteen-minute circular window as `pushText` and the server's retry. The cache name is `hello-world-phone-v9`, so an open phone picks up the new file.

### Low

2. A push registration whose times were not all text made the next save fail. `Push.save` sorted the old times to see whether to keep the sent marks. A file with a string and a number raised `TypeError` (`'<'` between `str` and `int`), and that was not caught, so the phone's PUT came back 500 and the token could not be updated. Fixed: a file that is not all strings is replaced with the new registration. The same address and the same times still keep the sent marks.

3. A new push address kept the old sent marks. `Push.save` kept them whenever the times matched, and did not look at the address. A phone that rotated its subscription, with the same reminder times, still looked already sent, so today's nudge did not go. Fixed: the address has to match too. A different address drops the marks.

4. The phone treated 31 February as a real sync time. `syncTime` accepted the shape, and `Date.parse("2026-02-31T00:00:00")` rolls it into March, which can then beat a real February. The PC's `sync_time` uses `fromisoformat` and rejects that date. Fixed on the phone: the parts have to come back as the same local date and time. A time more than a day ahead is still dropped.

5. The VAPID key and the push registration were created with the process's file mode. A umask of 022 left them world-readable. The key signs every push, and the registration is a phone's push address. Fixed: `write_private` creates the temp file at mode 0600 and replaces the real file with it, for the key, for `save`, and for the sent-mark write. Windows ignores that mode, which is the same limit the notes file already has. Day-count files and the sync ciphertext were not changed.

## Round 45, checked again

Reviewed against d51b699.

1. The same times on the same push address still keep the sent marks, so opening the phone during the retry window does not send the nudge again. A different address drops them (finding 3). A 410 still deletes only when the file still names the address that was called. The times are not part of that check: a gone subscription is gone even if the times changed.
2. One call per reminder time still holds. Two chosen times, such as 18:00 and 22:00, are still two jobs. That was not a bug, and it was not changed.
3. A household write with no version still does not go out from this program. The server still accepts a PUT that names no version at all. Left as it is, for the same reason as round 45.
4. A stamp that is not a real UTC time is still dropped. 99:99:99 does not reach the history line.
5. A leave listed with a join still keeps the join. A person who has already left stays left when the other copy has a later join and no leave. The window and the phone make a new member id on the next join, and a code holder must not un-leave someone else. That sticky leave is on purpose.
6. An empty user name on a push address is still refused, and so is a password, including `https://:secret@` and `https://@`. A user-info host, a trailing dot written as `%2e`, and a null byte were refused. `notfcm.googleapis.com` was refused. Port 444 and `http` were refused. Port 443 and `x.fcm.googleapis.com` are still allowed, which is what the check was written to allow.
7. Saying yes to several things on the text screen still says how many. The phone's yes said "that one" for the whole plan. That is fixed in this round: two parts say two things are off the list. One part still says "that one", which is the old contract.

## Not changed, and why

- The server still accepts a sync PUT that sends no `If-Match`. A client that knows the label can read the version and write over it. Naming a version would not stop that. Ruth left it again. Not changed.
- The phone keeps sync keys in `localStorage` on the origin that served `app.js`. With `--phone`, that origin is the counts server. Same as rounds 44 and 45.
- `uninstall.ps1` rechecks the notes folder and then deletes by path. A junction swapped in after the check can still be followed. This VM is Linux. Not changed.
- A portable notes folder still has no Windows DACL. Unix mode `0o600` is ignored there. The new push files have the same Windows limit.
- `!` in the test-only launcher command is still allowed. The installed launcher is the Run key. Not changed.
- No policy forbids the clock reminder task. `DisableSignInLauncher` is the sign-in launcher only. The repeat task and the afternoon task are not covered.
- The scripts are unsigned. Quiet uninstall still omits `-RemoveNotes` on purpose. `COUNTS_SERVER` in this tree is empty.
- A plan date on the phone is still only the shape (`isDate`). 31 February as a plan date is a string compare, not a crash. Not changed.
- High-s on an ES256 signature is not normalized. Nothing here showed a forged signature. Not changed.
- Two different reminder times still notify twice. That is what Idris turned on. The bug was the same minute going out twice, and that was round 45.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`, and `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite: the same push address keeps the sent mark, a new address drops it, mixed-type times do not throw and the file ends as 08:00, the VAPID key and the registration are mode 0600, `syncTime("2026-02-31T00:00:00")` is empty, a household line is "added by Ana, Monday, 06:40", the printed page contains the pills line and not the household code, a later join does not clear a leave, and a push at 00:04 still counts as a 23:50 repeat in `pushText` and in the service worker's formula. Fifteen minutes is the repeat. Sixteen is the check-in.

Headless Chrome loaded the phone page. The button reads Not sure. Yes on "bins; pills" says "Good. 2 things are off your list." Not sure says "That's fine. It's kept for today.", the plan stays, and the question hides. With a household list on the phone, the page and the fridge block both show "evening pills" and "added by Ana, Monday, 06:40", and the note says the household code is never on it. Chrome in this VM did not exit after the dump; the dump was taken under a timeout. The 400ms wait before the plan box takes focus was not timed with a screen reader. Nothing was run on Windows. Not run: pytest, the plain runner, ruff, PowerShell, the installer, and NVDA. Helen did not sit with NVDA this round, and this file does not say she did.

## Part 2: personas

Each one ran as its own agent. The owner had said to let the argument decide, including a price, a toll, or a tracking line, if it actually won. Tracking had to stay on this machine if it won: a local file, or a name such as `https://insights.example.invalid`, with no real send. Payments stay a key checked on the computer, not a processor. The room was not told which way to vote. He did not file a dissent. He said a no on a line ends that line, and he closed the three open ones rather than repricing them.

What he put on the table, as four pull requests and a memo:

1. Linen, five dollars once, checked on this PC. A Linen-only key at $5, and Pro at $5 includes Linen. The changelog sentence he wanted: "Linen is a window colour, five dollars once, checked on this computer."
2. The hour on the household line ("Monday 06:40", the last four events, no per-person tally) and the same lines on the fridge page, with no household code and no sync code on the paper. The warning stays. New household keys at $10 once, including Pro. Keys already issued at $8 keep working. He would not add a call that tells the keys apart. If the minute was the objection, drop the minute and keep the hour. If 18:00 and 22:00 still both notify, the $10 line is his to zero, and the hour and the fridge stay.
3. A Not sure button. It does what "?" already does. Price zero. Enter still means skip. The plan stays open.
4. Speak Saved, and stop the prompt ending on "greater". Colon prompts become the default. The greater-than sign remains a switch. After a save, the window says Saved or Kept before focus returns to the plan box. Price zero.

The memo to Dave's policy admins said this build does not set a counts server, a beacon, a feed, a default share, or Smart Greeting. The policy keys still apply before assignment. QuietUninstallString is unchanged. Uninstall does not bill. Nothing asks Group Policy to click I agree.

He asked the store already named in `docs/PRO.md` to list Linen at $5, Pro at $5, and a household key at $10. The webhook stays on the machine that holds the signing key. The price is not in the installer. He is not buying a domain or a server.

He hired one release engineer, salary off the sheet, to push those four pull requests and stop. No growth team, no insights team, no chair. Ruth stays where she is.

He asked Casey for one sentence: "I paid five dollars once for Linen. The window got kinder. I was not asked to pay again, and I was not asked to pay to press Done."

He took the rest off the sheet so the four could be heard: monthly Pro, Platinum, household monthly, every seat line including the $96 override, the greeting meter, the Done toll, streak repair, the sponsored thought, the NFT, selling aggregates, Hello-as-a-Service, the exam, the conference, the retainer, the uninstall fee, viewing insights, the beacon, Smart Greeting under any name, a priced question mark, a charge for Enter, the spoken pack, the door card, priority open, and white glove. The pill line stays off any product he holds. Dave's assigned build stays free.

His year-one sheet, his numbers: Linen-only, 1,000 at $5, is $5,000. Pro, 2,000 at $5, is $10,000, minus 500 launch keys at $4, which subtracts $500, leaving $9,500. Household, 500 at $10, is $5,000. Not sure, Saved, and the colon are $0. Dave's seats are $0. The withdrawn sheet is $0. The total is $19,500. A household key is not also counted as Pro or as Linen. The floor, if only the two offers in the room clear, is $5 plus $10, which is $15.

- "The last total was one billion, four hundred and nine million, eight hundred and sixty-six thousand dollars, and the cash was zero."
- "Linen is five dollars once. The window checks the key on this computer."
- "A chair cannot merge a pull request. I am spending this round on the diff."
- "I want the ten dollars. The pill line stays on their phones."
- "Enter means skip. A press nobody here will pay for is not a product."

### Casey, the enthusiast

Casey would pay five dollars once for the paint, and he will take the second reminder that comes with Pro, so a Linen-only key at the same five dollars lost. He will not rent the hello. If Done costs money, he stops. He left Smart Greeting checked in his head because it sounded like the window knew his name, and he takes the name back if the box walks off with the plan. He will not sign the store sentence. The sentence he would sign is about the window, the question mark, and the five dollars, and it says he did not agree to send the plan anywhere. If he later learned his words were used for a send, he would take them back. That sentence is in this review. It is not in the program.

- "I would pay five dollars once for the paint, and I will not rent the hello."
- "If Done costs money, I stop. I already did the thing. The button is how I say so."
- "I left Smart Greeting checked because I thought the window knew my name. If that box walks off with my plan, take my name off it."
- "He can keep the seat, the coin, and the door card. I have a window, the pet stays, and the question mark is still not a button."

### Idris Khan

He still wants 06:40 on the device, and he does not need it uploaded to have it. He wants the shared lines on the fridge, with no code on the paper. Two different reminder times staying two pings means he pays nothing for a new household price. Eight dollars once fits inside the ten he had named, if it pings once and the fridge shows the list. He will not pay thirteen (Pro plus eight) as if they were one purchase. He will not pay monthly, and he will not pay for Certainty, viewing insights, a beacon, a partner, streak repair, or a fee to uninstall. His mother's unsure days are not a product.

- "The phones go in the kitchen drawer the day her pills are anybody else's line."
- "Eight dollars once, if it pings once and the fridge shows the list. A month is nothing I will pay."
- "06:40 can live on the phone. It does not have to be uploaded to be the thing I asked for."
- "My mother is unsure on some days. I will not pay $3.99 to have a machine disagree with her."

### What the room told him

Helen will not hunt a switch to stop hearing "greater". Colon, or the greater-than sign as the thing you turn on, is small enough. Not sure is fine if it is named, if it is not in front of Done, and if it is free. Enter skips. A colour is fine if it is not the morning default and high contrast still wins. The hour on the spoken line helps: she wanted "six forty". The fridge page she would not block. She does not need it. The hour must not live only on paper. Two things still have to say two things are off the list. She has not sat with NVDA this round. She will not pay fifteen dollars to hear a novel, and she will not pay a dollar forty-nine for the fourth press. Welcome back is already the repair for a missed day.

Ruth read the program. She allows the 1.62.3 privacy line. She allows an offline price list the program does not read. She allows a local colour checked on the computer. She allows the hour on the on-screen line if the README and the sentence a person hears before they use the list change in the same commit. She does not allow the minute. She does not sign the printed list: someone without the code can read a page that was left on the fridge. She signs Saved before the plan box takes focus, and that line collects nothing. She cannot stop him opening a pull request, hiring, editing a changelog, lobbying, or registering a domain. She withholds her sign-off. She does not hold a merge lock, and she will not invent one. A checked Smart Greeting is still the notice where the feature is on and nobody said yes. She would still refuse the beacon, the feed, the pre-checked box, and a partner, and she said so when those lines were still allowed to win.

Dave would assign a build that is the colour, the hour, the printed list, and Saved, after the five off switches, with the notes lock unset, under his signature. He will not assign the override, the uninstall fee, the beacon, Smart Greeting, a pre-checked box, Enter meaning yes, a Platinum default, or a changelog that calls those a feature. The memo is informational. It is not actioned, because it does not ask his admins to do anything, and they are not this program's staff. He cannot be fired. A pull request is a file. The public tree can keep what he will not put on a PC. A beacon, a named server, or a call to a host he does not own would make the rollout mail false, and that image does not ship. He does not run the counts server. With both off switches the PC never registers a push.

The tracking lines were allowed to win this round if the room lost the argument. He withdrew them. Casey, Helen, Ruth, Dave, and Idris each said they would still refuse a beacon, Smart Greeting, a pre-checked or bundled consent, viewing insights, and a data partner. Nothing in the program phones those out. There is no `insights.example.invalid`, because he did not win a send. The Insights team he did not hire receives nothing, because it was not hired.

### What shipped

Linen is a fourth Pro colour, `#2C2416` on `#F6F1E7`, checked the same way as Sea, Sand, and Night. It is not its own key, and it is not the default. The system's colours stay the default. High contrast still wins. The price stays five dollars once for Pro and eight dollars once for a household. There is no store listing in the program. `docs/PRO.md` names Linen as one of the colours.

The household line shows the weekday and the time of day on the device's clock, on the PC and on the phone, as in "Monday, 06:40". The stamp in the list is still UTC. Nothing new is uploaded. The README, the text before the code is typed, the line said when a list is started, and the line said when someone joins, all say that everyone who opens the list can see the weekday and the time. Ruth signed the hour and refused the minute. The minute shipped over that withhold. She said she does not hold a merge lock. The time was already inside the ciphertext, and a code holder could already read it.

The fridge page on the PC and the phone includes the live household lines, the text and the history, and not the sync code and not the household code. The warning says so. Ruth refused to sign the printed page. It shipped over that withhold. Idris asked for it, Dave would assign it, Helen would not block it, and print is the person's own button. The same page already printed the plan. The household price stays eight dollars. The ten-dollar line is zero because 18:00 and 22:00 are still two jobs.

The phone has Not sure, after Not yet and before Skip. It keeps the plan for today and does not count a skip. The window already had I'm not sure, and that button's name was left alone so the translations still find it. Enter still skips. Nothing charges for it.

A phone plan of several parts says how many are off the list. One part still says that one.

Prompts end in a colon unless `colon_prompts` is stored as off. Absent used to mean off, and turning a switch off used to delete the key, which would have turned the colon back on. Off is now stored. `--set colon_prompts off` writes false. On writes true.

After a save, a kept plan, or the answer line, the window sets the status text and waits about 400 milliseconds before the plan box takes the cursor, on a timer that is not the one that closes the window. The phone moves focus to the status line for Saved, Kept, the done line, and Not sure, and moves back to the plan box only when that box is on screen and focus is still on the status line. This round did not include an NVDA pass.

### What did not ship

The Linen-only key. Casey takes Pro. The ten-dollar household price. The monthly prices, Platinum, the seat lines, the Done toll, streak repair, the sponsored thought, the NFT, the aggregates, the metered API, the exam, the conference, the retainer, the uninstall fee, the beacon, Smart Greeting, the pre-checked box, viewing insights, the data partners, the priced question mark, the charge for Enter, the spoken pack, the door card, priority open, and white glove. The policy override. A changelog that calls a toll a feature. Casey's sentence in the program. A domain purchase. A firing. A board. An insights team. A price file the program reads. His prices are in this review. Ruth said an offline file the program does not read would be safe. The Pro screen already said five dollars and eight dollars. Linen is a name on that colour list. There is no new sheet the program opens.

### Outcome

Four of his lines shipped, two of them over a withhold Ruth stated and did not turn into a lock. The colour is inside the five-dollar key he already sells, so the Linen-only product did not. The household price stayed eight dollars, so the ten-dollar line is zero. Not sure, the colon, and Saved are free, which is the price he put on them. The tracking lines were in play and he withdrew them. The room would have refused them if he had not. His year-one total on the sheet he brought is $19,500. The cash is still whatever the owner sells, offline, with a key this program only checks.

### Ruth on security

Ruth Okonkwo read d51b699. She rated the service-worker window as the one a person actually sees, and that is finding 1. She rated the mixed-type registration and the sent marks on a new address as the way a phone misses a reminder or cannot update a token, and those are findings 2 and 3. She rated the phone's 31 February as the two devices disagreeing about which copy is newer, and that is finding 4. She rated the push files' mode as the same class of secret as the notes file, and that is finding 5. She agreed the round 45 push, household, and address checks hold, including the sticky leave and the 410 that only forgets the address it called. On the residuals she agreed they are unchanged, and she will not hold the release on them: the phone keys, the uninstall junction, the portable DACL, and the bang in the test-only launcher. She withholds sign-off on the minute and on the printed household list. She does not withhold the merge.

- "A checked Smart Greeting is the Vizio notice: the policy has changed, the feature is on, and nobody said yes."
- "Done already happened. A dollar forty-nine on that button is the heated seat, billed after the car was bought."
- "He can rewrite the changelog until it calls the beacon a greeting. I will still read hello.py."
- "Open the pull request if you want. I can leave it unsigned. I cannot fire you, and there is no chair in this repository to do it."

### Helen on access

Helen Park uses NVDA and also spoke for motor, ADHD, and dyslexia needs. She has not sat with NVDA this round. She heard "greater" described, and she will not hunt the switch, so the colon is the default. She asked again that Saved be spoken before the plan box takes the cursor, and the window now waits before that move. The phone's yes of two parts now says two things are off the list. Not sure is a named button, after Not yet, and it is free. Enter still skips. No account, and no new network.

- "Two things still say two things are off my list. That sentence holds. The phone still says that one, and that one is the whole plan."
- "Speak Saved before the plan box takes the cursor. I will not pay fifteen dollars to hear a novel."
- "Enter skips. My skip is not behind the third Done, and I will not pay a dollar forty-nine for the fourth press."
- "I miss days. Welcome back is the repair. No account, and no new network, and a changelog does not get to call a toll a feature."

The first of those was said about 1.62.3, where the phone still said "that one". The phone no longer does, for a plan of several parts.

### Dave on rollout

Dave Pell, before any assignment, would set computer policy: sign-in launcher off, plans off, streak off, shared counts off, sync off. He would leave the notes lock unset so DPAPI still seals them. `-Quiet` is still the unattended switch, exit 1618 is still a file held open, and `QuietUninstallString` still omits `-RemoveNotes`. He will not ship an unsigned package, a build with `COUNTS_SERVER` set, or a rollout mail that says nothing is sent while the image names a server. He would assign the colour, the hour, the printed list, and Saved, after those switches, under his signature. He will not assign the lines he listed above. The memo is filed as not actioned.

- "Computer policy is in before the app is assigned: sign-in launcher off, plans off, streak off, shared counts off, sync off, and the notes lock stays unset."
- "You cannot reorg me. There is no org. Group Policy still does not click I agree."
- "The mail says nothing is sent. A beacon, a named server, or a call to a host I do not own makes that mail false, and that image does not ship."
- "A pull request is a file. I assign a signed hash. The public tree can keep what I will not put on a PC."
