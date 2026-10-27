# Round 48 review

- Date: 2026-10-27
- Commit reviewed: 8c6e5a2 (the round 47 branch, version 1.64.0, not merged). The fixes below are in 1.65.0.
- Agents: one reviewer, plus four simulated persona agents, each in its own run. The first pass did not see the others' notes. A second sitting voted. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that, for this round and later ones. What was run is at the end of Part 1.

Ruth Okonkwo, Dave Pell, and Casey left the panel before this round. They were not asked. Their notes stay in the earlier rounds. This round did not write a vote for them.

## Part 1: findings

### Medium

1. Typing q at the picture left the visit open. `show_fireworks` asked for pic, and any other word, including q, returned. The same was true of "Enter to continue" after the picture. The close sat outside `daily`'s `try`, so a `Quit` raised there would also have skipped the visit and the word "Closing." The accessibility note says q closes from any question. Enter still skips. One Ctrl+C still skips one prompt, because `ask` returns None and the picture treats that as a skip. Fixed: q, and the other quit words, raise `Quit`. `daily` catches that, sets the same flag a later question uses, and the visit is still recorded. q at the picture on a 3-day streak said "Closing." and the file then held that day. Enter at the picture did not draw it, and q at the next question still closed. pic, then q, drew the picture and then closed, and the day was still saved.

2. The first Skip on the phone moved the cursor off the question while the question was still there. `say` treated Skipped like Saved and called `hearSoon`. The plan box is hidden for as long as the question is up, so focus went to the status line and stayed there. The status line is live, so the words did not need the cursor, and the second Skip was no longer the button just pressed. Fixed: when the line is Skipped and the question is still being asked, the status text is set and focus stays on the button. A second Skip still hides the question, focuses the status line, and moves to the plan box about 400 ms later if focus is still on the status line. If focus is left inside something hidden, `draw` still makes that move. The cache name is `hello-world-phone-v11`, so an open phone picks up the new page.

### Low

3. `hello haiku` with no date ignored a day that starts at 18:00. The command runs before the day is opened, so the day start stayed at midnight. At 06:40 on 27 October, with the notes saying 18:00, the menu's day is 26 October and the command printed day 27. Fixed: the form with no date calls `load(repair=False)` and then uses that day. A missing file does not create a folder. A damaged file is left where it is, and it is not moved aside. `hello haiku --date` does not read the notes.

4. `hello haiku --date` accepted `20261027` and `2026-W44-2`. On Python 3.12, `date.fromisoformat` reads both of those as 27 October 2026. The help names `YYYY-MM-DD`. A week date is not that day. Fixed: the word has to be four digits, a hyphen, two digits, a hyphen, and two digits, and `fromisoformat` has to accept it. `2026-02-31`, `2026-02-29`, and `2026-1-2` still exit 2. `2026-10-27` still prints day 27.

5. `haiku.` at the plan prompt was saved. `toy_reply` only used `strip().lower()`. The closing prompt already strips the same punctuation `TRIM` holds, so `haiku.` there was a joke and `haiku.` at the plan was a plan. Fixed: the joke strips that punctuation too. `haiku!` is the same joke. `haiku.world` is not. `plan uuddlrlrba` is still the plan command, and it still saves. The word shift at a prompt is not a joke, so a plan of that word still saves.

6. A symlink named `vapid.json`, or a folder named `push` that was a symlink, was still followed. `tighten` leaves a symlink alone, so it does not change the other file, but `open` and `listdir` follow the link. Fixed: a `vapid.json` symlink is not read. A new key replaces the link, and the file it pointed at is left as it was. A `push` symlink is removed, the link itself and not the target. If the link is still there, the folder is not listed, a save does not write through it, and a reminder does not read it. A registration that is a symlink is not opened and is not chmod'd. Saving that token replaces the link with a file at mode 0600. Windows still only toggles the read-only bit, and 0600 includes write, so a key stays writable there. That is the same limit the notes file already has.

## Round 47, checked again

Reviewed against 8c6e5a2.

1. The same push address and the same times still keep the sent marks. A new address still drops them. A file whose times are not all strings is still replaced, and that save does not throw. The file ends as 08:00 with no sent mark.
2. A new private write is still mode 0600. An old key at 0644 is still tightened on load. The push folder is still 0700. A registration left at 0644 is still 0600 on the next load. A symlink is no longer followed (finding 6).
3. `syncTime("2026-02-31T00:00:00")` is still empty. A time that rolls off a clock, such as 02:30 on the morning the clocks jump forward, is still the known disagreement between the phone and the PC. Not changed.
4. A household line is still "Monday, 06:40" on this device's clock. With the clock set to UTC, the window menu label for `2026-10-26T06:40:00Z` is "evening pills — Monday, 06:40". The fridge page still has the lines and still does not have the household code.
5. A later join still does not clear a leave. Sticky leave stays. The merge was not rewritten this round.
6. A push at 00:04 still counts as a 23:50 repeat, in `pushText` and in the service worker. 99:99 and 25:00 are still the check-in line. 18:00 at 17:50 still matches, which is the early half kept from round 47. Sixteen minutes past 08:00 is still the check-in. The service worker's `nearClock` agrees. The cache name is now `hello-world-phone-v11`.
7. The phone's Not sure button is still there, after Not yet and before Skip. On a plan from 2020 the page is a fresh day, so the second button reads "Bring it over" and Not sure is still the one after it. Yes on two things still returns the several-things line.
8. The colon is still the default. Off is still stored as false. Enter still skips. `PROMPT_COLON` in `Visit.toggle` is still set only after `if not saved`. A Chinese cue ending in `）>` becomes a colon. An English prompt ending in ` > ` becomes the colon it already had. The status sentence that mentions Options still contains `>`. With the colon off, the cue is left alone. Chinese still has 15 cues with no space before `>`, and Japanese still has 9.
9. The plan box still waits about 400 ms. Headless Chrome, after a second Skip, had focus on the status line and then on the plan box. The haiku button and the Klingon button set the status line and do not start that wait. After each of them, focus was still on the status line half a second later.
10. Two reminder times are still two jobs. At 22:10, 22:00 and 22:05 were two calls and two sent marks. 18:00 and 22:00 at 22:10 were one call. The stand-in send did not leave the machine.

Klingon is still not in the sync body, on the PC or the phone. `hello --pirate` is still the greeting and one line, and `--pirate on` still exits 2. There is still no sixth policy key.

## Not changed, and why

- The server still accepts a sync PUT that sends no `If-Match`. Not changed.
- The phone keeps sync keys in `localStorage` on the origin that served `app.js`. Same as rounds 44 to 47.
- `uninstall.ps1` rechecks the notes folder and then deletes by path. A junction swapped in after the check can still be followed. This VM is Linux. Not changed.
- A portable notes folder still has no Windows DACL. Unix mode `0o600` is ignored there. The push files have the same Windows limit, and finding 6 says so.
- `!` in the test-only launcher command is still allowed. The installed launcher is the Run key. Not changed.
- No policy forbids the clock reminder task. There is no sixth policy key. A local-network hello was not brought back.
- The scripts are unsigned. Quiet uninstall still omits `-RemoveNotes` on purpose. `COUNTS_SERVER` in this tree is empty.
- A plan date on the phone is still only the shape. 31 February as a plan date is a string compare, not a crash. Not changed.
- High-s on an ES256 signature is not normalized. Nothing here showed a forged signature. Not changed.
- The theme brush is still cached for the life of the window. The menu already says the colours show the next time it opens.
- The phone's question buttons are still two columns, so Not sure sits under Done. Not changed.
- There is no 100-day sentence. The picture still hangs on the days-in-a-row line, which is 3, 7, 14, and every 30th day.
- The early half of the fifteen-minute window stays. The closest pair in the phone's list is still 06:15 and 07:00.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`, and `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite. Notes were only under a temporary folder.

`hello shift` prints "Hello, world!" and "The day starts when you said it does." and creates no folder. `hello shift extra` exits 2 and creates no folder. `hello haiku` with no notes prints day 27, on a calendar day of 27 October, and creates no folder. With notes that say the day starts at 18:00, and the clock at 06:40 on 27 October, it prints day 26 and does not rewrite the file. A damaged file is left in place. `hello haiku --date 2026-10-27` prints day 27. `20261027`, `2026-W44-2`, `2026-02-31`, `2026-02-29`, and `2026-1-2` exit 2. `hello --pirate` prints two lines and exits 0. `hello --pirate on` exits 2.

`haiku.`, `haiku!`, and `uuddlrlrba` are jokes. `haiku.world` is not. `plan uuddlrlrba` is not a joke command. The word shift at a prompt is not a joke. q at the picture raises `Quit`. Enter skips it. pic, then q, raises `Quit` after the picture. A None from `ask`, which is one Ctrl+C, skips. Driving the day: q on a 3-day streak closed, said "Closing.", and the visit list gained that day. Enter skipped the picture, and q at the next question closed and saved the day. pic, then q, drew the picture, closed, and saved the day.

A `vapid.json` left at 0644 becomes 0600. The push folder becomes 0700. A registration left at 0644 becomes 0600. A symlink key is not read, and the new file is 0600. A `push` symlink is replaced by a directory, and the folder it pointed at is unchanged. A `push` symlink that cannot be removed is not listed, not saved through, and not used for a reminder. A registration symlink is not chmod'd and not opened. Saving that token replaces the link, and the outside file is unchanged.

`colon_prompt` turns `）>` into a colon and leaves the Options sentence alone. With the colon off, the cue stays. Chinese has 15 no-space cues and Japanese has 9.

`pushText` at 00:04 returns the 23:50 repeat. `99:99` and `25:00` return the check-in line. 18:00 at 17:50 returns the repeat. Sixteen minutes past 08:00 returns the check-in line. The service worker agrees, and its cache name is `hello-world-phone-v11`. `syncTime("2026-02-31T00:00:00")` is empty. The first Skip still leaves `asks` true. The second Skip makes it false. Yes on "bins; pills" is the several-things line. Klingon is not in the phone's sync body.

Headless Chrome loaded the phone page. The heading stays "Hello, world!". The Klingon line is hidden, and its text is `qo' vIquv.` The settings button shows it, the status line says it was made up and not checked by a linguist, and focus stays on the status line. A haiku shows the three lines, and half a second later focus is still on the status line. On a fresh day the buttons read Done, Bring it over, Not sure, Skip. The first Skip leaves focus on Skip, the question stays up, the plan box stays hidden, and the status line says "Skipped. It asks again next time." The second Skip hides the question and puts focus on the status line. After the wait, focus is on the plan box. The wait was not timed with a screen reader. Nothing was run on Windows. Not run: pytest, the plain runner, ruff, PowerShell, the installer, and NVDA. Helen did not sit with NVDA this round, and this file does not say she did.

## Part 2: personas

The four who are still here sat once, and then again with each other's notes. Nothing was scored in advance. With the security seat, the sysadmin seat, and the enthusiast seat empty, a feature the remaining four agreed on was going to ship.

Jules Navarro brought six jokes and wanted the lot. Morning Morse, saved. A dry greeting, "You again. The screen noticed." A wave that would print "No packet left this machine." and open no socket. A receipt whose amount due is zero dollars and zero cents, and that says nothing was charged. A staple, four lines of characters, and the word staple at a prompt. A cowbell, as a command and as a phone button. And one line, `hello shift`, that prints the greeting and then "The day starts when you said it does." He would take the dots off the morning. He would not put a price on any of them. He pulled the wave himself once Helen heard the word packet. He held the shift line once Idris said it does not say three in the morning and it is not on the phone.

### Helen Park

She has not sat with NVDA this round. She read the phone page and the picture prompt.

- "I have not sat with NVDA this round. I read the phone page. The first Skip says Skipped and puts me on that line while the question is still there."
- "q is supposed to close from any question. On the picture, q only means not pic, so the visit stays open. Enter still skips."

She said the first Skip and the picture were the bugs. She said a dollar sign is a bill, even at zero dollars and zero cents, and she will not pay to hear a joke, and she will not pay for Done. Morning Morse is the one she flinches at. Dots do not get a saved switch. "You again. The screen noticed." is sarcasm, and she heard it. The wave says packet, which is a network sentence, and she refused it. The cowbell is one more button, and she said the command goes with the button. She refused the staple, the four lines and the prompt word. She picked the shift line as the one joke: plain words, the greeting first, it prints and ends, it saves nothing, it does not read the clock, it does not say three, it does not touch a question, and it is not on the phone.

### Idris Khan

The household line is still Monday, 06:40, under the bins, on the window, and on the fridge. The household code is not on that paper. He pays eight dollars once. He will not keep a streak.

- "Three in the morning is when I put the phones down. I don't want a sentence for that hour, and I don't want a command for it either."
- "hello haiku with no date ignores 18:00. At 06:40 the menu has my day and the command does not."

He said the haiku command should use the day start he already saved. He said yes to the shift line, because it does not say 03:00 and it is not on the phone. He said yes to the wave, because nothing would leave the machine, and yes to the staple, because it is not on the phone. He said no to the receipt. "Nothing was charged" forgets the eight dollars he already paid once. He said no to the cowbell. More cowbell on the status line sits where his mother reads the pills, and that button stays off her phone. "You again" is the screen having a tone. He opens this to tick the bins, not to be noticed. Opt-in is still a phone that can speak, and on the ward that phone goes in the drawer, so a local-network hello stays out. Two reminder times are still two pings, so there is no new price.

### Jules Navarro

He heard the votes and held one command.

- "Shift stays. I only pull that one if he flinches."
- "The receipt stays off the sheet. I will miss the zero."

He had wanted the staple under the greeting, and he said the prompt word would go. Helen refused the four lines as well, so the staple is not in the program. He pulled morning Morse, the dry line, the wave, the receipt, the staple, and the cowbell. The shift line stays. One command. Hello, world! first. Then the line. Then it ends.

### Profit Maximizer

Salary does not count against his budget. He did not recompute the year from a new price. The empty seats did not change the count of people.

- "No new line. Thirteen thousand five hundred is the year, and it is the year after you kill a line I did not bring."
- "Thirteen thousand five hundred. The one joke sits inside the five dollars, and the total does not move."

Pro, 1,500 at five dollars and 500 launch keys at four dollars, is $9,500. Household, 500 at eight dollars, is $4,000. That is $13,500. The jokes stay inside the five dollars. A price on a joke needs a payer, and this room does not have one. The receipt, the wave, the morning dots, and the shift line are zero. He is not reopening them. The hundred dollars, the zero-dollar invoice, the Done toll, and the beacon stay closed and priced at zero. The page he liked best still cannot bill. He did not reopen the dissents from rounds 44 and 45.

## What shipped

`hello shift` prints the greeting and one line, "The day starts when you said it does." It saves nothing. It does not read the clock. It does not say 03:00. It is not a switch, not a menu item, and not a phone button. Extra words exit 2. It is not a Pro check. The word shift typed at a prompt is still a plan, not this command.

The picture now closes on q, the first Skip leaves focus on the button, `hello haiku` follows the saved day start, a haiku date has to be `YYYY-MM-DD`, a punctuated haiku at the plan prompt is the joke, and a symlink in the push files is not followed.

## What did not ship

- Morning Morse as a saved switch. Helen flinches at the dots. The `hello morse` command from 1.64.0 remains, and it is not the morning.
- `hello --dry`, and the line "You again. The screen noticed." Helen called it sarcasm. Idris opens this to tick the bins, not to be noticed.
- `hello --wave`, and the line "No packet left this machine." It would have opened no socket. Helen heard a network sentence and refused it. Jules pulled it. Idris had said yes.
- `hello --receipt`. Amount due: $0.00, and nothing was charged. Helen said a dollar sign is a bill. Idris said it forgets the eight dollars. Profit priced it at zero. Jules will miss the zero.
- `hello staple`, the four lines of a stapler, and the word staple at a prompt. Idris had said yes, because it is not on the phone. Helen said a reader spells four lines, and the prompt word would swallow a plan. Jules pulled both.
- `hello cowbell`, and a cowbell button on the phone. The button would write on the status line where the pills are read. Helen said one more button is a reach, and the command goes with it.
- A hello on the local network. Idris still puts that phone in the drawer. The hundred dollars stays zero.
- Anything about three in the morning, including a command that only prints it when asked.
- A sarcastic greeting, a pirate dialect on the questions, ten phone buttons, a new price, a beacon, a Done toll, a sixth policy key, and `insights.example.invalid`.

## Outcome

Six findings are fixed in 1.65.0. One command shipped, it does not send, and it does not save. The receipt, the wave, the morning dots, the dry line, the staple, and the cowbell are not in the program. Profit Maximizer's year, on the numbers he could defend after the room, is $13,500.
