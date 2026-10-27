# Round 47 review

- Date: 2026-10-26
- Commit reviewed: 965bedc (main, version 1.63.0). The fixes below are in 1.64.0.
- Agents: one reviewer, plus seven simulated persona agents, each in its own run. The first pass did not see the others' notes. A second sitting voted on the new panelist's list. Quotes are simulations, checked against the program before anything was changed. No eighth persona.
- Redactions: none.
- The test suite was not run. The owner asked for that, for this round and later ones. What was run is at the end of Part 1.

The seventh seat is Jules Navarro. He writes features because they are funny and because he can. He does not wait to be asked. The room was not told which of his ideas had to win.

## Part 1: findings

### Medium

1. A push key that was already on disk stayed world-readable. `write_private` creates a new file at mode 0600. `Push.__init__` only calls it when `vapid.json` does not parse, so a key left at 0644 by a process with umask 022 was never tightened. The push folder was created with `os.makedirs` and no mode, so a 022 umask left it 0755. The token in a registration's file name is what authorizes a change, and anyone who could list the folder could read those names. Fixed: a key that parses is chmod 0600 on load, the push folder is chmod 0700, and each existing `[0-9a-f]{32}` registration is chmod 0600. `write_private` chmods the destination after replace. A symlink sitting on the temp name is removed once and the write is tried again. A symlink in the folder is not followed. Windows still only toggles the read-only bit, and 0600 includes write, so a key stays writable there. That is the same limit the notes file already has.

2. The plan box and the handoff box did not take a Pro colour. The theme handler answered `WM_CTLCOLORDLG` (0x136), `WM_CTLCOLORSTATIC` (0x138), and `WM_CTLCOLORBTN` (0x135). It did not answer `WM_CTLCOLOREDIT` (0x133), so the edit boxes kept the system colours while the labels around them did not. High contrast already returns no theme colours, and that path still uses the system brushes. Ruth called this low and would have left it. Helen called it medium, because the box a person types into was the one that did not match. Fixed: 0x133 is in the same handler. A theme change still shows the next time the window opens, which is what the colour menu already says.

3. Prompts with no space before the cue still ended on "greater". `ask` rewrote a prompt only when it ended in `" > "`. Fifteen Chinese prompts and nine Japanese prompts end in `>` with no space before it, so the colon never replaced that cue. English, Spanish, French, German, Portuguese, Korean, Arabic, and Hebrew prompts already had the space. Fixed: if the colon is on, a prompt whose trailing whitespace is removed and that then ends in `>` loses that cue and gains `: `. `input` still adds the space before the cursor. The sentence "Prefer no follow-up questions? Options > What the window shows." is a status line, not a prompt. It does not end in `>`, and it was left as it is.

4. A second Skip left focus on a button that was no longer on screen. The question hides once a plan has been skipped twice. Focus stayed on Skip, inside the hidden section, and `say` only moved focus for Saved, Kept, Good, Not sure, and the several-things line. Fixed: those lines, and also Skipped, carried, sideways, set aside, and back, focus the status line, then the plan box about 400 ms later, and only if the plan box is on screen and focus is still on the status line. After `draw`, if focus is inside something hidden, the same move happens. A line that is not one of those cancels the wait, so a later message does not pull the cursor. The haiku button sets the status line and does not start that wait.

### Low

5. Turning the colon off and failing to save still changed the prompts for that visit. The window set `PROMPT_COLON` before `commit`. A failed save undid the notes and left the global flipped, so the rest of the visit asked with the colon the file did not have. Fixed: the global is set only after the save lands.

6. A reminder time that is not a clock time made every push look near. `near` in `phone/app.js` and `phone/sw.js` did `Math.min(diff, 1440 - diff) <= 15`. For `99:99` or `25:00` the gap is larger than a day, `1440 - diff` is negative, and the minimum is always within 15. The server already refuses those times. The phone's own notification and the service worker did not. Fixed: both accept only `HH:MM` from 00:00 to 23:59, the same shape as the server. A real time still uses the fifteen minutes on either side, including across midnight. Ruth said not to drop the early half this round. The closest pair in the phone's list is 06:15 and 07:00, forty-five minutes apart, so that half is not how one reminder steals the other's words. The cache name is `hello-world-phone-v10`.

7. The window's household menu showed the words and not the time. The text screen, the phone, the fridge page, and "Who did what" already say the weekday and the clock time on this device. The popup a person ticks, and the remove and restore lists, showed the words only. Fixed: each of those lines is the words, then an em dash, then the newest line's weekday and time, cut so the time stays. A bad stamp shows the words alone. The list still stores UTC. Nothing new is uploaded.

## Round 46, checked again

Reviewed against 965bedc.

1. The same push address and the same times still keep the sent marks. A new address still drops them. A file whose times are not all strings is still replaced, and that save does not throw.
2. A new private write is still mode 0600. An old key at 0644 is now tightened on load (finding 1).
3. `syncTime("2026-02-31T00:00:00")` is still empty. A time that rolls off a clock, such as 02:30 on the morning the clocks jump forward, is still rejected on the phone and still accepted by the PC's `fromisoformat`. Ruth said not to change that. One morning, and the zones do not agree. Left as it is. The fall-back hour still round-trips.
4. A household line is still "Monday, 06:40" on this device's clock. The fridge page still has the lines and still does not have the household code. The window menu now has the time too (finding 7).
5. A later join still does not clear a leave. Sticky leave stays.
6. A push at 00:04 still counts as a 23:50 repeat, in `pushText` and in the service worker. Fifteen minutes is still the repeat. Sixteen is still the check-in. 18:00 at 17:50 still matches, which is the early half Ruth asked to keep. 99:99 does not match (finding 6).
7. The phone's Not sure button is still there, after Not yet and before Skip. Yes on two things still says "Good. 2 things are off your list."
8. The colon is still the default. Off is still stored as false. Enter still skips. Linen is still not the default colour. High contrast still wins, because a high-contrast flag returns no theme colours.
9. The plan box still waits about 400 ms, on timer id 3. Timer id 1 is still the closer. They are not the same timer.
10. Two reminder times, such as 18:00 and 22:00, are still two jobs.

## Not changed, and why

- The server still accepts a sync PUT that sends no `If-Match`. Ruth left it again. Not changed.
- The phone keeps sync keys in `localStorage` on the origin that served `app.js`. Same as rounds 44 to 46.
- `uninstall.ps1` rechecks the notes folder and then deletes by path. A junction swapped in after the check can still be followed. This VM is Linux. Not changed.
- A portable notes folder still has no Windows DACL. Unix mode `0o600` is ignored there. The push files have the same Windows limit, and finding 1 says so.
- `!` in the test-only launcher command is still allowed. The installed launcher is the Run key. Not changed.
- No policy forbids the clock reminder task. The five switches are unchanged. A sixth switch for a local-network hello was refused, and that hello was not built.
- The scripts are unsigned. Quiet uninstall still omits `-RemoveNotes` on purpose. `COUNTS_SERVER` in this tree is empty.
- A plan date on the phone is still only the shape. 31 February as a plan date is a string compare, not a crash. Not changed.
- High-s on an ES256 signature is not normalized. Nothing here showed a forged signature. Not changed.
- The theme brush is still cached for the life of the window. The menu already says the colours show the next time it opens.
- The phone's question buttons are still two columns, so Not sure sits under Done. Helen noted it and did not ask for a change.
- There is no 100-day sentence. The streak line is 3, 7, 14, and every 30th day. The picture hangs on that line, not on a day the program does not say.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`, and `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite.

The same push address keeps the sent mark. A new address drops it. Mixed-type times do not throw, and the file ends as 08:00 with no sent mark. A `vapid.json` left at 0644 becomes 0600 when `Push` loads it. The push folder becomes 0700. A registration left at 0644 becomes 0600 on the next load. A new private write is 0600. A symlink on the temp name is removed, and the file that replaces it holds the new text.

`colon_prompt` turns a cue ending in `）> ` into a colon. An English prompt ending in ` > ` becomes the same colon it already had. The status sentence that mentions Options still contains `>`. With the colon off, the cue is left alone. Chinese has 15 cues with no space before `>`, Japanese has 9, and Arabic, German, and Spanish have none. The assignment of `PROMPT_COLON` in `Visit.toggle` sits after `if not saved`.

A household menu label for a stamp of `2026-10-26T06:40:00Z`, with the clock set to UTC, is "evening pills — Monday, 06:40". A long line still ends with that time. `hello haiku --date 2026-10-27` prints "Day 27 still fits on one line" and does not create a notes folder. `hello morse` and `hello klingon` print and save nothing. A bad date exits 2. `hello --pirate` prints the plain greeting and one extra line and exits 0. `hello --pirate on` exits 2. `uuddlrlrba` and `haiku` at a prompt are replies, and `plan` is not one of those commands. `klingon` is in the switches, and it is not in the sync body.

`pushText` at 00:04 still returns the 23:50 repeat. `99:99` and `25:00` return the check-in line. 18:00 at 17:50 still returns the repeat. Sixteen minutes past 08:00 returns the check-in line. The service worker's `nearClock` agrees, and its cache name is `hello-world-phone-v10`. `syncTime("2026-02-31T00:00:00")` is empty.

Headless Chrome loaded the phone page. The button reads Not sure. The heading stays "Hello, world!". Klingon hello is hidden until the settings button is pressed, then the line reads `qo' vIquv.` and the status line says it was made up and not checked by a linguist. Focus stays on the status line. A haiku shows the three lines with breaks, and focus stays on the status line. Yes on "bins; pills" says "Good. 2 things are off your list." A second Skip hides the question, the status line is "Skipped. It asks again next time.", and after the wait focus is on the plan box. Chrome was given a timeout. The wait was not timed with a screen reader. Nothing was run on Windows. Not run: pytest, the plain runner, ruff, PowerShell, the installer, and NVDA. Helen did not sit with NVDA this round, and this file does not say she did.

## Part 2: personas

Jules Navarro brought ten ideas and wanted all of them in the tree. A Klingon line under the greeting. Morse. A picture on a long streak. A code you can type. A sarcastic greeting. A hello that looks for other hellos on the local network. A line for opening it at three in the morning. A haiku. A pirate flag. And a page that says the amount due is zero dollars and zero cents, which was his own extra. He would put the plain "Hello, world!" first whenever a joke voice is on. He would take Morse off the morning if the dots were a wall, drop the three-in-the-morning line off the morning if Idris flinched, and drop the network hello if a sysadmin flinched. He would not save a pirate voice. He would not add a pay button to the zero-dollar page.

The room answered one at a time. Nothing was scored in advance.

### Casey

He likes the words he does not know, as long as the hello he already has stays put. He will not pay for a toy. If a price shows up on one, he stops.

- "I don't know Klingon, and the hello can wear those words like a tiny hat, off until I ask."
- "The window says hello to me, and it can leave the other machines alone."

He said yes to Klingon, the picture, sarcasm, the three-in-the-morning line, the haiku, the pirate line, and the invoice at zero dollars. He said no to Morse, because a reader would say the dots. He said no to the code, because it looks like a password, and no to ten buttons that type it. He said no to a hello on the network. That no on the code is his own refusal to type it. It is not a veto of a token on the text screen.

### Ruth Okonkwo

She read 965bedc. She does not sign this round. She does not hold a merge lock, and she will not invent one.

- "Mode 0600 on a file this process just created does not change the key that was already on disk. I read that branch."
- "The first name stays in the greeting. It does not get a port."

She allows a once-key checked on the computer for some toys, and she withholds a price on the picture, the network hello, and the invoice. A local-network hello would have had to use an empty name, a private or link-local address, one datagram, a short listen, and a policy switch, and the first name would still not go on the wire. Three other nos removed it before that shape was built. She said there is no 100-day sentence. The row line is 3, 7, 14, and every 30th day, and she will not hang a picture on a day she did not read. `plan uuddlrlrba` still saves, because that path is the plan command. The token at a prompt does not.

### Helen Park

She has not sat with NVDA this round.

- "Plain words first. Dots are a second morning I did not ask to hear."
- "Enter still means skip, the first time, including a picture on day 100."

She said yes to Klingon if the plain words stay first, yes to a picture if the person types pic and Enter still skips, and yes to a haiku command. She said no to Morse on the morning, even with the plain words above the dots. `hello morse` on its own would have been a yes. She said no to ten buttons, no to sarcasm, no to a network hello, and no to a three-in-the-morning line on the morning. She said no to a pirate voice if it changed "Did you do it?". That reading was wrong: the flag prints two lines and returns, and it does not change a prompt. The misread is recorded here. A pirate dialect on the questions does not ship. The two-line flag does. She said no to the invoice, because a dollar sign is still a bill. There is no 100-day sentence, so the picture she described sits on the days the streak line already prints.

### Dave Pell

1.63.0 is still assignable after the five switches, with the notes lock unset. Quiet uninstall still omits `-RemoveNotes`. `COUNTS_SERVER` in this tree is empty.

- "Fireworks that need the streak never draw here. That one can ride in the signed hash."
- "LAN hello is a UDP send. DisableLanHello is not one of my five, the mail would be false, and that image does not ship."

He would assign the picture, because it never draws when the streak is off or the days-in-a-row line is hidden, and he would assign the haiku, including where plans are turned off. The other toys stay in the public tree and out of his hash. He will not be reorganized into a sixth switch. A till that says zero stays off the image.

### Idris Khan

The household line is right on the phone, the text screen, and the paper, and the code is not on them. The window menu was the gap. He pays eight dollars once for the household, and nothing for a joke.

- "Monday, 06:40 is on the phone under evening pills, and the same words are on the paper, with no household code."
- "At 06:00 the three-in-the-morning line is not there, and at 03:00 it is, and that is when the phones come off the shift."

He said yes to Klingon, to Morse if it stays off the household line, to the picture, to the code, to sarcasm, to the haiku, and to the pirate line. He said no to a network hello, no to the three-in-the-morning line, and no to a bill on a phone his mother opens, including a bill for zero dollars. Jules offered to move that line behind a flag. Idris still said no to the sentence that appears on its own at 03:00. An empty command was not added.

### Jules Navarro

- "greeting() still says the words. I am stapling joy underneath, and I am already grinning at the staple."
- "Amount due is zero dollars and zero cents. I have never been happier about a number."

The second line is the invoice, and the invoice lost. He shipped the ideas the room did not kill, and he left the rest on this page.

### Profit Maximizer

Salary does not count against his budget. He recomputed before the toys, out loud, because the sheet he brought into round 46 needed a Linen-only key and a ten-dollar household key, and neither is for sale.

- "Nineteen thousand five hundred needed a Linen key and a ten-dollar household key, and neither is for sale, so the year I can defend is thirteen thousand five hundred."
- "Thirteen thousand six hundred if the LAN line lives, and thirteen thousand five hundred if the room kills it."

Pro, 1,500 at five dollars and 500 launch keys at four dollars, is $9,500. Household, 500 at eight dollars, is $4,000. That is $13,500. He put Klingon, Morse, sarcasm, the picture, the haiku, and the three-in-the-morning line inside the five dollars already on the table, with no line of their own and no new check in the program. The code and the pirate flag are zero, because there is nothing to check. The invoice is zero. The network hello was fifty people at two dollars, which is $100. The room zeroed it. His year is $13,500. He is annoyed that the page he liked best cannot bill. He did not reopen the beacon, the Done toll, or the dissents from rounds 44 and 45.

## What shipped

Klingon is a switch, off until `--set klingon on` or the settings button or the menu. The plain greeting stays first. If that greeting is a name or a title, "Hello, world!" is said as well. The phone's heading stays the translated hello, and the made-up line sits under it. The note says it was made up and not checked by a linguist. It is not on a household line, it is not in the sync body, and it is not a Pro check. Delete everything keeps it, the same way it keeps the other switches. `hello klingon` prints the greeting, the line, and the note, saves nothing, and exits 0.

`hello morse` prints the greeting, the dots for HELLO, WORLD!, and the greeting again. It is not a morning switch. `hello haiku` prints three English lines, a blank line, and the greeting. `hello haiku --date YYYY-MM-DD` puts that day in the middle line. A bad date says it doesn't look right and exits 2. The same three lines are a menu item and a settings button. They are not the morning thought. The button does not start the 400 ms move to the plan box.

`hello --pirate` prints the greeting and one line under it. `--pirate on` is still an unknown option. It does not change "Did you do it?" and it is not saved.

On the text screen, after the days-in-a-row sentence, and only there, the person can type pic. The picture is eight lines of characters. Enter skips it, and Enter continues after it. The window and the phone keep the sentence only. The same guards as the sentence apply: the streak is on, the policy is not hiding it, and gentle mode is off. The days are 3, 7, 14, and every 30th day.

Typing `uuddlrlrba` or `haiku` at the plan prompt or the closing prompt answers and does not save. `plan uuddlrlrba` still saves. There is no row of ten buttons, and Esc in the window is unchanged.

Plans turned off do not block `hello morse`, `hello klingon`, or `hello haiku`. There is no sixth policy key.

## What did not ship

- Morse as a stored morning line. Helen said a reader would speak the dots every morning. Casey said no. The command remains.
- A sarcastic greeting. Helen said sarcasm about the voice stays off the morning, including as a switch.
- A hello to other machines on the local network. Casey said no. Helen said no new network. Idris said a phone that can speak on the ward network goes in the drawer. Dave said a UDP send would make the rollout mail false, and he will not add `DisableLanHello`. Ruth's narrower socket was not built. The $100 line is zero.
- Anything about three in the morning, including a command that only prints it when asked. Idris said the sentence at 03:00 pulls the phones. An empty command was not added.
- A page whose amount due is zero. Helen said a dollar sign is still a bill. Idris said no bill on a phone his mother opens. Dave said a till that says zero stays off the image.
- Ten phone buttons, or an Esc path in the window, for the code.
- A pirate dialect on the questions, or a pirate voice that is saved.
- A picture that waits for day 100. There is no such sentence. The picture uses the sentence that already exists.
- A new price, a Pro gate on a joke, a beacon, a Done toll, a monthly line, or a sixth policy key. No `insights.example.invalid`.

## Outcome

Seven findings are fixed in 1.64.0. The jokes that survived are local, they do not send, and the ones that print do not save. The network hello, the bill, the morning sarcasm, the morning dots, and the three-in-the-morning line are not in the program. Profit Maximizer's year, on the numbers he could defend after the room, is $13,500.
