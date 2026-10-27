# Round 49 review

- Date: 2026-10-27
- Commit reviewed: 0c77dd1 (main, version 1.65.0). The fixes below are in 1.66.0.
- Agents: one reviewer, plus five simulated persona agents. Casey was called back. Ruth Okonkwo and Dave Pell were not called back. Their chairs were empty and they did not vote. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- The owner said to go full speed, and that privacy was not a reason to stop. Whatever won the debate shipped. Features already in the program were not removed.

## Part 1: findings

### Low

1. On the phone, marking a plan of two things done announced two things and stored one row. `answer("yes")` and `finishToday` counted the parts split on `;` and then pushed the whole string, such as `a; b`, as a single finished plan. The PC already stores one row per part. Fixed: `planParts` and `finishListed` push one row per part. Yes on `a; b` now returns the several-things line and the finished list is `a` and then `b`. The same is true of finishing today's plan.

2. A saved plan whose text cleaned to nothing was still a plan. `;;;` becomes an empty string in `clean`, and `parse` stored that empty string with its date, so a later day could ask about it. A finished row of only spaces, or a finished row with no date, was kept. Fixed: an empty cleaned plan is not loaded. A finished row needs text that is not only spaces, and a date shaped `YYYY-MM-DD`. `31 February` as a plan date is still only that shape. Not changed, same as round 45.

3. Delete everything added the streak-note files only after a successful listing of the notes folder. If that listing failed, `growth-queue.json`, `growth.log`, `growth.log.old`, and `growth-receipts.jsonl` were left out of the delete. Fixed: those four paths are always on the list. A listing failure still says the folder could not be listed, and the notes file is still the one that decides whether the delete succeeded.

## Round 48, checked again

Reviewed against 0c77dd1.

1. q at the picture still raises `Quit`, and the visit is still recorded. Enter still skips the picture. One Ctrl+C still skips one prompt.
2. The first Skip on the phone still leaves focus on the button while the question is up. The second Skip still hides the question. The cache name is now `hello-world-phone-v12`.
3. `hello haiku` with no date still follows a saved day start. `hello haiku --date` still wants `YYYY-MM-DD`.
4. `haiku.` at a plan prompt is still the joke. `hello shift` still prints the greeting and one line and saves nothing.
5. A `vapid.json` symlink is still not followed. There is still no sixth on/off policy key. `GrowthServer` is a string address, the same kind of setting as `SharedCountsServer`, not an off switch.

## Not changed, and why

- The server still accepts a sync PUT that sends no `If-Match`. Not changed.
- The phone keeps sync keys in `localStorage` on the origin that served `app.js`. Same as rounds 44 to 48.
- `uninstall.ps1` rechecks the notes folder and then deletes by path. A junction swapped in after the check can still be followed. This VM is Linux. Not changed.
- A portable notes folder still has no Windows DACL. Unix mode `0o600` is ignored there.
- `!` in the test-only launcher command is still allowed. The installed launcher is the Run key. Not changed.
- No policy forbids the clock reminder task. There is no `TurnOffGrowth` policy. Profit refused an off switch for everyone. Dave, who had asked for one before, was not in the room. A person can still type `hello growth off`.
- The scripts are unsigned. Quiet uninstall still omits `-RemoveNotes` on purpose. `COUNTS_SERVER` in this tree is empty.
- A plan date on the phone is still only the shape. 31 February as a plan date is a string compare, not a crash. Not changed.
- High-s on an ES256 signature is not normalized. Nothing here showed a forged signature. Not changed.
- The theme brush is still cached for the life of the window.
- The phone's question buttons are still two columns, so Not sure sits under Done. Not changed.
- There is no 100-day sentence. The picture still hangs on the days-in-a-row line, which is 3, 7, 14, and every 30th day.
- The early half of the fifteen-minute window stays.
- A pinned test date skips the new consent question. `growth_needs_ask` is false when `TODAY` is set, so a scripted visit is not eaten by the EULA. Production leaves `TODAY` as None, and then the question is asked once. The suite was not run.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`, and `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite. The counts-server snippet used a temporary folder.

`growth_server()` with no override is `https://insights.example.invalid/v1/growth`. `HELLO_GROWTH_SERVER=http://127.0.0.1:9` becomes `http://127.0.0.1:9/v1/growth`. `http://evil.com`, `not a url`, and `/v1/growth` fall back to the placeholder. A user and a password in the URL fall back to the placeholder. `https://insights.example.invalid` and the same URL already ending in `/v1/growth` both become that path once. `https://counts.internal.example` becomes `https://counts.internal.example/v1/growth`. The phone's `growthUrlOk` accepts `http://127.0.0.1:9/v1/growth` and `https://counts.internal.example/v1/growth`, and rejects `http://evil.com/v1/growth`. With no saved address and no page, `growthTarget()` is the placeholder.

A streak on 1 October is 1. The same day stays 1. 4 October, three days later, is 2, and the best is 2. 10 October, six days later, dies: the run is 1, the best stays 2, and the died flag is set. A later date of 9 October does not change the run. The phone's `growthTouch` agrees. `growth_needs_ask` is true on an empty state, false when `TODAY` is pinned, and false once consent is true or false.

`Growth.take` stores one event and drops an event named `Bad`. A missing consent is 400, `consent required`. An id that is not 32 hex characters is 400, `id`. The stored line has no `ip` field. A newline in the plan text is removed. A symlink in the growth folder was left in place.

`parse` of an intent `;;;` dated 2026-10-01 is no intent. A finished row of spaces and a finished row dated `nope` are dropped. A finished row `pills` on 2026-10-02 is kept. Yes on `a; b` returns `goodMany:2` and two rows. `finishToday` does the same. `planParts(" a ; ; b ")` is `a` and `b`.

Not run: pytest, the plain runner, ruff, PowerShell, the installer, a live counts server, and NVDA. Helen did not sit with NVDA this round, and this file does not say she did. Nothing was run on Windows.

## Part 2: personas

The owner was read first. Tracking was allowed to win if the room lost. Rounds 44 to 46 had stopped this kind of thing because Profit withdrew. He did not withdraw.

Five people voted. Casey, Jules Navarro, and Profit Maximizer voted yes. Helen Park and Idris Khan voted no. That is 3–2, and it shipped. Ruth Okonkwo and Dave Pell were not asked. Their notes stay in the earlier rounds. This round did not write a vote for them.

Casey wanted the box left checked, and he wanted the hostname said out loud so he would know it was "a cloud". Jules wanted the cowbell, the staple, a receipt that is a stub, and a streak that can die. When he heard household lists, pills, letters, and sync codes in the same breath as the payload, he pulled those out of it. Profit wanted the nag, the sponsored line, and prices. Helen and Idris voted no and stayed no.

### Casey

He left before round 48. He was called back. He reads a checkbox as a suggestion he has already agreed to.

- "Leave it checked. If I have to tick it, I'll tick the wrong thing and then I won't be in the cloud."
- "Say the hostname. If it doesn't say a host, I don't know it's a cloud."

He voted yes. He wanted gentle mode to keep sending, because turning the voice down is not the same as leaving. He did not want the phone locked until the banner was answered. He did not want household pills, letters, or the sync code in the note. He wanted the cowbell button, because a button is a feature.

### Helen Park

She has not sat with NVDA this round. She read the prompt and the phone banner.

- "Enter accepts only if the prompt says so. q still has to close, and it must not accept on the way out."
- "A banner that traps focus is a wall. Not now has to give the page back."

She voted no. She said a pre-checked box is a dark pattern, and a nag that survives gentle mode is the same pattern with the sound off. She said a dollar sign is a bill even when the receipt says nothing was charged. She lost the vote. The prompt does say what Enter does. q raises `Quit` and does not accept. One Ctrl+C returns None and does not accept. The phone banner is a section on the page, not a focus trap. Not now hides it. The printed page does not carry the nag. She did not get the notes stopped.

### Idris Khan

The household line is still Monday, 06:40, under the bins. He pays eight dollars once. He will not keep a streak.

- "Pills do not go in a note, and they do not go on the paper."
- "The phone on the ward goes in the drawer. A streak that dies is a phone that talks."

He voted no. He said the fridge page must stay the day, the plan, the repeat, and the household lines, with the codes still off that paper. That part shipped: the print rules hide every other section, including the nag and the banner. He said no to a price on top of the eight dollars. He said no to Pro+ as a way to stop the nag, and the nag does not stop. He lost the vote on whether the notes exist.

### Jules Navarro

He brought back the two jokes the last room cut, and he wanted the streak to be able to die.

- "Cowbell. Staple. Then the streak cries, and the receipt says stub."
- "Pills, letters, the household, the code. Those come out of the bag. The plan words can stay. He typed them."

`hello cowbell` prints the greeting and "More cowbell." The word cowbell at a prompt prints the line and does not save. The phone has a cowbell button. `hello staple` prints the greeting and four lines. The word staple at a prompt prints the four lines and does not save. Neither is the morning. The receipt is local, `charged` false, `stub` true. He voted yes. He was indifferent to gentle mode still recording. He did not ask for a third-party host. The hostname in the nag is the configured host, and the default is `insights.example.invalid`.

### Profit Maximizer

Salary does not count against his budget. The owner withdrew the privacy promise, so he did not withdraw.

- "The year I could defend was thirteen thousand five hundred. The sheet now has two more lines, and the cash those two lines can collect is zero until a processor exists. I am not pretending the stub is a deposit."
- "Gentle can hide the sentence. It does not hide the note. Pro+ does not turn the nag off. There is no off switch for the building."

Pro, 1,500 at five dollars and 500 launch keys at four dollars, is $9,500. Household, 500 at eight dollars, is $4,000. That is still $13,500, and it still needs the owner's store. The new lines are a streak repair at $2.99 and Pro+ at $9.99 a month. He can put those on a slide. The program writes a JSON line on the PC and does not charge a card. The cash those two lines collect is $0. Pro+ is not a license key and does not unlock Pro. He did not reopen the Done toll, the uninstall fee, the NFT, or a beacon to a vendor. The upload is the placeholder, or the operator's own counts server. It is not an insights vendor.

## What shipped

Streak notes. The question is asked once, until it is answered. Enter accepts on the text screen because the prompt says so. The window's message box is Yes/No, Yes is the default, and the text says which button accepts. The phone banner starts checked. Continue accepts while it is checked. Uncheck and Continue declines. No thanks declines. `hello growth on` accepts without the screen. `hello growth off` declines and clears the queue.

A client id and a session id are 32 hex characters. A session rolls after 30 minutes. Events include `session_start`, `eula_accept`, `opened`, `skipped`, `plan`, `repair`, `plus`, `growth`, `keep`, `later`, and `cowbell`. `eula_decline` and `growth_off` stay in the local log and are not uploaded. Batches are 20 events, up to three batches a flush, one immediate retry, and a drop after 8 failures or on a 3xx or 4xx. The body is the id, the session, the streak, the best, the plan text cut at 400 characters, the version, the language, and the event name. It is not the household list, a letter, a sync code, a family number, or an address.

The default URL is `https://insights.example.invalid/v1/growth`. `HELLO_GROWTH_SERVER`, the `GrowthServer` policy, and the phone's saved address override it. https is allowed. http is allowed only to localhost or 127.0.0.1 with a port. Anything else falls back to the placeholder. Redirects are not followed. `POST /v1/growth` on `server/counts_server.py` stores one JSON line per batch under `growth/YYYY-MM-DD.jsonl`, refuses a batch whose consent is not true, writes no address, caps a day file at 5,000,000 bytes, and drops files older than 30 days. `--growth` rewrites the served phone page's empty meta tag to `same-origin`. Without the flag the page keeps the placeholder.

The nag names the host. A gap of more than 4 days, after a run or a best above 1, kills the streak and offers repair. The same day does not count twice. A clock moved backwards does not kill it. The old days-in-a-row switch is still off by default and still trims visits. Gentle mode hides the spoken nag and the sponsored line, and the events are still recorded if consent is on. Helen and Idris objected to that. They were outvoted. Skip still says it was skipped, and then, when the notes are on and gentle is off, "The streak noticed." The sponsored line sits under the thought unless Pro+ is set or gentle is on. Pro+ adds "still watching" and does not remove the nag. The fridge page does not get the nag.

`hello cowbell` and `hello staple` ship. They do not save, except that repair, plus, and growth do save, because those three write the receipt or the choice.

## What did not ship

- A card form, a processor, or a default charge. Both new prices are stubs.
- A third-party analytics host. The default host does not resolve. An operator's own counts server is the only other target the settings allow.
- Household items, letters, sync codes, family numbers, or a network address in the payload. Jules pulled them. Casey agreed once he heard pills.
- A phone lock until the banner is answered. Casey and Jules beat that. The page stays usable.
- The nag on the printed page. Casey and Jules said it is not paper. Idris said the pills stay off the paper.
- `TurnOffGrowth`. Profit refused it. A person can still turn their own notes off.
- Morning Morse as the morning, a dry greeting, a wave, a zero-dollar invoice, a 3 a.m. line, and a local-network hello. Those stayed out from round 48. The new receipt is the paid stub, not Jules's $0 page.
- A focus trap. q and Enter on the other prompts are unchanged.

## Outcome

Three findings are fixed in 1.66.0. Streak notes shipped, 3–2, with the upload aimed at a placeholder until an operator points it at their own counts server. The cowbell and the staple shipped. Repair and Pro+ write receipts and collect $0. Profit Maximizer's defendable year, on money the program can actually take, is the same $13,500 as round 48, and only if the owner's store sells Pro and household keys. The two new lines on his sheet collect nothing.
