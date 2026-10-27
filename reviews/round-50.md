# Round 50 review

- Date: 2026-10-27
- Commit reviewed: 3273dec (main, version 1.66.0). The fixes below are in 1.67.0.
- Agents: one reviewer, plus six simulated persona agents. The October panel and every persona in `docs/PERSONAS-2026-10.md` are retired. They were not in the room and they did not vote. The six new people were not shown `reviews/`, the old votes, or the old compromises. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.
- The test suite was not run. The owner asked for that. What was run is at the end of Part 1.
- The owner said to wipe the panel's memory and let the new room pick its own work. Nothing already in the program was removed. Whatever won the vote shipped.

## Part 1: findings

### Low

1. `VERSION` was still `1.65.0` after 1.66.0 shipped. `hello.py`, the installer tag, the README example, and the phone already said 1.66.0. The auto-tag workflow reads `VERSION` and tags `v<that>`, so a push of 1.66.0 would not create `v1.66.0` once `v1.65.0` existed. Fixed: `VERSION`, `hello.py`, `install.ps1`, the README example, and `phone/app.js` are 1.67.0.

2. The counts server's `growth` folder did not get the treatment the push folder already had. `Growth.__init__` called `makedirs` and followed a symlink of that name, and the mode was whatever the process umask produced, often `0755`, so another account on the machine could list the day files. Fixed: a symlink named `growth` is removed (the link itself; the directory it pointed at is left in place). If the link is still there, the folder is not used and `POST /v1/growth` answers 500 `not stored`. Otherwise the folder is created and tightened to `0700`. The check is repeated under the lock. A day-file symlink was already refused.

3. A queued event whose `attempts` was not a number crashed the text visit. `growth_flush` called `int()` on it, and `daily` calls `growth_flush` with no wrapper. A bool is an int in Python, so `True` would have been counted as one try and then kept forever in the retry path. Fixed: a missing count is zero. A bool, a string, or any other type is treated as already exhausted, so that one record is dropped and the visit continues. The other events in the file stay. The phone uses the same rule. After one flush against the placeholder, a good event with `attempts` 0 is still in the queue and its plan text is still `bins`. A sibling event with `attempts` `"nope"` is gone. The good event's count is 2, because the flush tries once and then once more immediately.

4. The death flag never cleared. A run of 2, then a gap of more than 4 days, set `growth_died` and put the run back to 1. The next day, still within 4 days, the run became 2 again and the flag stayed, so the sentence still said the streak had died. The same is true on the phone. Fixed: the day the gap breaks the run still sets the flag. The next opening that continues the new run clears it, and the sentence uses the new number. A second opening on the death day itself still shows the death sentence. Opening the same day does not count twice. A clock moved backwards does not clear the flag and does not kill the run. Checked: 1 October is run 1, 3 October is run 2, 11 October dies with best 2, 12 October is run 2 with the flag gone. The phone's `growthTouch` agrees.

5. A failed save could still write a receipt or queue an event. `hello repair`, `hello plus`, turning streak notes off, the window's Yes on the consent box, `hello growth` with notes already on, and the text visit's opened and skipped events wrote the queue or the receipt before `commit`. If the save failed, `undo` put the notes back and the receipt or the queue stayed. Fixed: the notes save runs first. The receipt, the ledger line, and the queued event run only after that save returns success. A call with saving turned off leaves no `growth-receipts.jsonl`, no `feature-audit.jsonl`, and no priority flag. The phone's repair, Pro+, Priority Hello, accept, and decline follow the same order: if the browser storage write fails, the flag is put back and no receipt is added.

## Round 49, checked again

Reviewed against 3273dec, then against this tree.

1. Yes on `a; b` on the phone still returns the several-things line, and the finished rows are `a` and then `b`.
2. The default upload is still `https://insights.example.invalid/v1/growth`. `HELLO_GROWTH_SERVER=http://evil.com` still falls back to that placeholder. `http://127.0.0.1:9` still becomes `http://127.0.0.1:9/v1/growth`.
3. q at the picture still raises `Quit`. The visit is still recorded. This round did not change that path.
4. `hello shift` still prints the greeting and one line and does not save. This round did not change it.
5. There is still no on/off policy named `TurnOffGrowth`. This room did not ask for one.

## Not changed, and why

- The server still accepts a sync PUT that sends no `If-Match`. Not changed.
- The phone keeps sync keys in `localStorage` on the origin that served `app.js`. Same as rounds 44 to 49.
- `uninstall.ps1` rechecks the notes folder and then deletes by path. A junction swapped in after the check can still be followed. This VM is Linux. Not changed.
- A portable notes folder still has no Windows DACL. Unix mode `0o600` is ignored there. The new ledger uses the same private write as the receipt, and it has the same Windows limit.
- The scripts are unsigned. Quiet uninstall still omits `-RemoveNotes` on purpose.
- A plan date on the phone is still only the shape. 31 February as a plan date is a string compare. Not changed.
- The sponsored line still shows when streak notes are on, gentle mode is off, and Pro+ is not set. Priority Hello does not remove it.
- Streak notes still exist. This room did not vote on taking them out. The upload address is still the placeholder until an operator points it at their own counts server.
- No card form and no processor. The new price is a stub.

## Checked here

`python3 -m py_compile` on `hello.py` and `server/counts_server.py`, and `node --check` on `phone/app.js` and `phone/sw.js`. Small snippets, not the suite. Notes were only under a temporary folder.

`VERSION` and `hello.VERSION` are both `1.67.0`. The phone's `APP_VERSION` is `1.67.0`. The service-worker cache name is `hello-world-phone-v13`.

`growth_server()` with no override is `https://insights.example.invalid/v1/growth`. `http://evil.com` falls back to the placeholder. `http://127.0.0.1:9` becomes `http://127.0.0.1:9/v1/growth`.

A streak on 1 October is 1. On 3 October it is 2. On 11 October it dies, the run is 1, and the best is 2. On 12 October the run is 2 and the death flag is gone. A second call on 11 October still has the flag. The phone's `growthTouch` agrees. The duck line for 27 October 2026 is the same sentence on the PC and on the phone: "The rubber duck says: the bug is in the sentence you were sure was fine."

`hello kazoo` prints the greeting, four lines, and `bwap bwap`, and exits 0. `hello kazoo extra` exits 2. `hello ai` prints the greeting, "This is not a model. Nothing was sent.", and one duck line, and exits 0. With the notes folder absent, neither command creates it.

`hello priority` with saving turned off says the choice could not be saved and that nothing was charged. It does not write a receipt or a ledger line, and it does not set the flag. With saving on, the receipt has `charged` false, `stub` true, and `4.99`. The ledger line is `priority`, version `1.67.0`, `network` false, `charged` false, `stub` true. The plan text `pills` is not in that line.

A `growth` symlink is replaced by a real directory at mode `0700`. The directory it pointed at is left empty. A symlink put back in that name is not written through. `POST` answers 500 `not stored`.

Not run: pytest, the plain runner, ruff, PowerShell, the installer, a live counts server, and NVDA. Edith did not sit with a screen reader this round, and this file does not say she did. Nothing was run on Windows.

## Part 2: personas

The six sat once, then again with each other's notes. Nobody was scored in advance. They had the program, the price sheet in `docs/PRO.md`, and the screens. They did not have the old rounds.

Four motions were on the table.

- Nico wanted a kazoo: a command, the word at a prompt, and a button. No price. Not the morning.
- Bex wanted an AI button. She could not say what it would call. She wanted it to feel like a product.
- Vance wanted a $4.99 Priority Hello on the slide, and he wanted the death sentence to stay until somebody paid the $2.99 repair.
- Edith wanted the death sentence to match the number, and she would not read a price off the printed page. Amina would not add a question before the plan.

Reed's line, on every motion, was the same. Fine, do it. Then he barked the conditions.

### Bex Calder

She films Unbox The Future from a spare bedroom in Tucson. She owns more gadgets than she can name. She calls the placeholder "the cloud" until someone reads her the host.

- "Put AI on a button. If it has a button, it's tech."
- "Priority sounds expensive, so it must be the good one."

She voted yes on the kazoo, yes on the button labeled AI, and yes on Priority Hello. She did not understand "this is not a model." Edith made the room keep that sentence. Bex still wanted the button. She got the button and the sentence. She did not get a network call, because she could not say where it would go, and Reed would not sign a socket he could not point at.

### Vance Harlow

Staff salary is not on his sheet. He read `docs/PRO.md` and the receipt code. He talked over Amina twice. She waited him out.

- "The sheet has five dollars once, eight dollars for a household, two ninety-nine, and nine ninety-nine a month. I am adding four ninety-nine. The program does not collect it. I am not calling a stub a deposit."
- "Leave the death line up until they take the repair. A number that recovered is a number I cannot bill."

He voted yes on Priority Hello. He voted yes on the kazoo only after Nico refused to put a price on it and the stub stayed a separate command. He voted yes on the duck once the $9.99 AI price lost. He voted to keep the stuck death sentence. He lost that one, 5 to 1. Pro and the household key still need the owner's store. The new line writes a JSON receipt and charges nothing. He put $4.99 on the slide anyway. The cash that line can collect is $0 until a processor exists, and this round does not add one.

### Nico Paredes

He wanted one joke that is not already in the program.

- "Kazoo. Four lines and bwap bwap. If it costs money, it isn't funny."
- "The duck can stay if it admits it's a duck."

He voted yes on the kazoo, yes on the duck, and yes on Priority Hello once it was a different command and the kazoo stayed free. He voted no on a price for the duck. He voted no on leaving the death sentence stuck. "That isn't a joke. The number moved and the sentence didn't."

### Reed Mallory

Former Marine staff sergeant. He was a communications clerk, then he made slide decks for a contractor and started calling himself CISO. Mallory Assurance is him and a bookkeeper. He does not veto. He is loud about not being the one who gets named later.

- "Fine. We do the kazoo. We do the duck. We do the four ninety-nine. Nobody leaves this room with a receipt for a save that did not happen."
- "The folder is 0700. A symlink is not a folder. A bad record does not take down the morning. The ledger does not contain the plan. If you call a duck a model, I will not sign the line, because I am the one they will ask."

He voted yes on all three features, with those conditions. He voted no on the stuck death sentence. "A counter that lies is how I end up in the report." He did not ask to turn streak notes off for the building. He asked for the folder, the order of the writes, and the ledger. Those shipped. The ledger is `feature-audit.jsonl` next to the notes: feature, version, `network` false, `charged` false, `stub` true or false. No plan text and no client id. A joke does not create the notes folder. If the folder is already there, the joke appends one line. A stub writes its line only after the notes save succeeds. Delete everything removes the ledger.

### Amina Soule

She opens the bakery at 4:10. The phone is dusty. She wants the plan, not a speech.

- "Not in the morning. I will not tap through a new question to get to the bread."
- "A button buried in Settings is not my morning. A price in the face is."

She voted yes on the kazoo and the duck because they are commands and Settings buttons, not a new prompt and not the greeting. She voted no on Priority Hello. She lost, 4 to 2. The morning screen does not gain a line for it. The printed page does not gain one either.

### Edith Cho

She reads the printed page to her sister on Sundays. She heard the death sentence against a run that had already started again.

- "If the number is two, you do not tell me it died. I will not read a lie to her."
- "Four lines of a kazoo are not going on that paper. Neither is four dollars and ninety-nine cents."

She voted yes on the kazoo as a command she does not have to read aloud. She voted yes on the duck only with the sentence "This is not a model. Nothing was sent." She voted no on Priority Hello. She voted no on the stuck death sentence. The death sentence is fixed. The price is not on the paper. The kazoo button and the AI button sit with Cowbell, under Settings. Print still shows the fridge section and hides the rest.

## What shipped

`hello kazoo` prints the greeting, four lines, and "bwap bwap". The word kazoo at a prompt prints the lines and does not save a plan. `hello ai` prints the greeting, "This is not a model. Nothing was sent.", and one of five duck lines chosen from the date. The word ai at a prompt does the same without the greeting. Neither command opens the notes file. Neither creates the notes folder. Neither sends anything. Extra words exit 2.

The phone has Kazoo, AI, and Priority Hello in Settings. Kazoo and AI set the status line and do not write storage. They are not on the printed page. The cache name is `hello-world-phone-v13`.

`hello priority` sets a flag and, only after the notes save succeeds, writes a local receipt for $4.99 with `charged` false and `stub` true, and a ledger line. The morning screen does not change. Option 1 says it is a local stub and that nothing was charged. The sponsored line stays. The flag does not unlock Pro. The phone's button does the same into `hello-world-growth-receipts`, and only after the notes write succeeds. Delete everything on the phone removes that list.

Repair and Pro+ use that same order. A failed save does not leave a receipt. The growth folder is not followed when it is a symlink, and it is mode `0700`. A bad try-count does not crash the visit. The death sentence matches the run on the next continued day.

The vote on the three features was yes. Kazoo was 6 to 0. The duck, with Edith's sentence and without a price, was 6 to 0. Priority Hello was 4 to 2, Amina and Edith against. The stuck death sentence lost 5 to 1, Vance against the fix.

## What did not ship

- A price on the kazoo, or a $9.99 line that calls the duck a model. Vance asked. Nico and Edith refused. Reed would not sign the word model.
- A network call for the AI button. Bex could not name a host. The default upload for streak notes is unchanged, and it is still the placeholder.
- Priority Hello on the morning screen, or on the printed page. Amina and Edith. The command still exists. The receipt still exists.
- Removing the sponsored line, or stopping the nag, as a benefit of the $4.99. That would have cut a line that is already there.
- Leaving the death sentence up until repair. Vance. The other five said the sentence had to match the number.
- A card form, a processor, or any charge that leaves the machine.
- A new question before the plan.
- An off switch for streak notes for the whole building. This room did not ask. A person can still run `hello growth off`.

## Outcome

Five findings are fixed in 1.67.0. The new panel shipped a kazoo, a duck line that says it is not a model, and a $4.99 stub that collects nothing. Reed Mallory did not veto. The receipt, the ledger, and the growth folder follow the conditions he barked. Vance Harlow's defendable cash from the new line is $0. The $5 Pro key and the $8 household key still depend on the owner's store, which this program does not call.
