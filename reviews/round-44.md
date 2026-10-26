# Round 44 review

- Date: 2026-10-26
- Commit reviewed: 9ca4e38 (main, version 1.62.1). The fixes below are in 1.62.2.
- Agents: one reviewer, plus five simulated persona agents, each in its own run. The first pass did not see the others' notes. A second sitting on this same review answered the profit maximizer. Quotes are simulations, checked against the program before anything was changed.
- Redactions: none.

## Part 1: findings

### High

1. Personal sync replaced the other device when the read failed. `sync_now` in hello.py, and `sync` in phone/app.js, still PUT the local plan when the GET failed, when the body would not decrypt, or when two devices wrote without `If-Match`. The household list already refused that. A phone that finished "Bought milk" could lose that line to a PC whose read had failed. Fixed: a read that is not 200 or 404 stops. A 200 that does not open, or that has no ETag, stops. The PUT names the version just read (`missing` for a new copy) and a 412 merges and tries again, up to three times. The phone uses the same rule (`syncAction`) and sets `redirect: "error"` so a 302 or 307 cannot carry the sealed body to another host.

### Medium

2. A push the service did not accept was marked sent. `Push.due` stored the current minute for any status other than 404 or 410, including 0 and 500. The reminder is due only in that minute, so the day's nudge was dropped. `Push.send` also followed a 302, and a POST that turns into a GET still takes the VAPID `Authorization` header along. Fixed: only a 2xx is marked sent, as the scheduled minute, and a miss is tried again for 15 minutes. `due` checks the push address again before calling out, so a hand-edited file cannot aim the server at some other host. `send` returns the redirect status and does not open the next URL.

3. The local-server check trusted a prefix. `counts_server` allowed any URL that started with `http://127.0.0.1:` or `http://localhost:`. `http://127.0.0.1:9@evil.example` is host `evil.example` with the user name `127.0.0.1`. A user name, a password, or a fragment is now refused, and the host is parsed. `http://127.0.0.1:9` still counts as this computer. `https://` to any host is still allowed, which is the documented way to point at a real counts server.

4. The PC followed redirects on the counts server. `urllib` follows a 302 on GET, and on POST it follows as a GET. The shared-count and sync helpers now stop at the first response, so only the host in policy is called.

5. People who had left filled the household. `house_join` and `house_merge` counted every member toward 20, including departures, and nothing pruned them. After enough leave-and-stay cycles the list could not take a new person. Fixed on the PC and the phone: only people still here take a place (20). Departures are kept for the "who left" line, and the oldest departure is dropped past 20. A merge may hold up to 40 names while it combines both sides, then the same trim runs.

6. An old "gone" stamp deleted a live household thing once history trim dropped the "added" line. The guard looked only for a later "added" or "restored". Six tick and untick lines are enough to trim "added" away (`MAX_HOUSE_HISTORY` is 6). A stamp from 2020 then removed the thing, and the restore list never saw it. Fixed on the PC and the phone: a later history line, of any kind, keeps the thing. The 30-day rule and the "added" or "restored" check stay, so the old Caligula case (a copy from before a real removal) still cannot bring tea back.

### Low

7. Saying yes to a plan of several things said one was finished. The text screen called `done_lines`, which is always singular ("Good. That one is finished."), after `y` marked every part done. The window already used `done_message`. The text screen now does too, so two things say "Good. 2 things are off your list."

## Round 43, checked again

Reviewed against 9ca4e38, and against the 1.16.0 notes in round 43.

1. Unknown keys in notes.json. Fixed. `load` copies only the typed fields `new_state` knows. A stray key in the file is dropped.
2. Startup `.cmd` injection. Fixed for the path that ships. `remind` writes the HKCU Run key. `launcher_command` quotes paths and refuses a quote or a percent sign. A `.cmd` is written only when `STARTUP_DIR` is set, which is the test hook. `!` is still not refused. Delayed expansion is off by default, and that file is not the installed launcher. Left as a residual, low.
3. Unix mode and Windows DACL. The umask claim was wrong: `os.open` with `0o600` cannot end up looser than that, because umask only clears bits. Windows ignores the Unix mode. The installed notes live under the user's LocalAppData and, on Windows, are sealed with DPAPI. A portable folder (`portable.txt` pointing at `notes` beside the app) inherits the directory's ACL. No Windows machine was available here to try a DACL, so that residual is not changed this round.
4. Stale `notes.json.*.tmp` files. Fixed. `save` calls `sweep_tmp`, which removes those files once they are a day old.

## Not changed, and why

- The phone keeps sync keys in `localStorage` on the origin that served `app.js`. With `--phone`, that origin is the counts server. Encryption holds against a server that only stores ciphertext. It does not hold against an operator who replaces the script, because the page and the script are the same site. A subresource hash does not help when the HTML is served from there too. Recorded. Not papered over with a header.
- `uninstall.ps1` rechecks the notes folder before each delete, and a junction swapped in after that check can still be followed. Closing it needs a delete by an open handle. This VM is Linux, so that path was not changed.
- The Windows DACL on a portable notes folder, same reason as round 43 item 3.
- `!` in the test-only launcher command, as above.
- The profit maximizer's prices, his Smart Greeting package, and the enthusiast's colour theme and QR code. The package is rejected in Part 2. He filed a dissent. Nothing from it was built, and nothing in the program sends data for it.
- The trailing `>` on prompts, which a screen reader speaks as "greater". That wants a real NVDA pass (panel item 2). The false "that one" line, which the same reader hit, is fixed.
- Quiet uninstall omits `-RemoveNotes` on purpose: a silent uninstall should not wipe the plan. Unsigned scripts and a counts host in a build whose mail says "nothing is sent" are rollout choices. `COUNTS_SERVER` in this tree is empty. Policy can still name a server, and `TurnOffSharedCounts` turns it off.

## Part 2: personas

Each one ran as its own agent. Nothing they asked for was built, except the bugs in Part 1 that the review already owned. The engineers' line is no accounts, and no network unless the person opts in. The profit maximizer refused that line. The reply, and the rejection, follow his pitch.

### Casey, the enthusiast

Casey installed it, saw a black window, and stayed. Sync stayed off because the code looked like a password. The question mark was a favourite even though it is typed, not tapped. Casey would pay five dollars for a friendlier colour and thought a company might pay eight.

- "I thought the black window meant it had crashed, and then it said hello."
- "The question mark for when I am not sure is my favourite button, even though it is not a button."
- "I would pay five dollars so the window could be a friendlier colour."

### The profit maximizer

He refused the privacy promises as a blocker. He called them a footer: no accounts, and no network unless someone opts in. The button people hit on the first morning is the product, and he wants that click to count as opted in. He told the engineers who wrote the line to get out of the way. Ruth's "no network" review, he said, is how a television company stays in the hardware business while the margin walks out the door. Dave's Group Policy is the cheap tier. Helen can have the notice read aloud. That, he said, is the accommodation.

The package is a Samsung setup screen with the serial numbers filed off. He called it Smart Greeting. If Legal flinches, the name becomes Viewing Information Services, which is what Samsung calls the feature that recognizes what is on screen. He does not want the word telemetry anywhere a person can see it.

What he asked for, and what this review does not build:

- Usage insights in the style of automatic content recognition, on until the person finds a box and turns them off. The day's thought, the plan, and whether it was finished leave the machine as "viewing information."
- A privacy notice long enough that keeping the app means accepting it. First-run setup is the consent. Enter, which today skips a question, should also mean yes.
- A box labeled "Help improve hello-world," already checked when the window opens.
- Sponsored lines in the daily thought, sold to data partners. The counts server is where those partners collect.
- Staff with no ceiling, because salaries are not his budget. He named twelve lawyers to rewrite the privacy policy, a growth team of twenty, and an Insights team of fifteen, and he said he could add more before lunch.

The old prices stay, and then they stop mattering. Five dollars is the cover. The household set is thirty-nine. The feed is the business. He will not take a leaderboard if the feed pays better, and he will not take a no from this panel.

- "The promise is a footer. The button is the product, and the button will say I agree."
- "Call it Smart Greeting. If Legal twitches, call it Viewing Information Services. Nobody ever sued a television for having a greeting."
- "Vizio did not get rich selling glass. The glass was the coupon. I will hire the lawyers who can make our coupon look like a thought for the day."
- "Opt in is what we call it after they press Enter to reach the hello. A pre-checked Help improve box is a courtesy, not a question."
- "Ruth can keep her threat model. Dave can lock the cheap image. The image I sell phones home before the coffee is poured, and I am hiring the Insights team that receives it."

### What the room told him

Casey was delighted, which is the problem with the button. He would leave Smart Greeting checked because it sounds like the window finally got a personality, and he asked if the sponsored thought could be about gadgets. He did not know the plan would leave the PC.

- "Smart Greeting sounds like the black window learned my name. I would leave that box checked."

Helen Park answered him by name. A notice you must accept to keep the hello is a locked door. She will not sit through it. NVDA would speak every word, including the part that calls her plan viewing information. A box that arrives checked is not a choice she can find. Enter already means skip. He does not get to reuse it as yes. Her first note stands: no account, and no new network.

- "I will not accept a novel to keep a hello. If the box is already checked, I have not agreed to anything."
- "Enter skips. He wants Enter to mean send. Those are different words, and the screen reader will say the wrong one if he blurs them."

Ruth Okonkwo answered him by name, with the cases he was waving around.

Vizio, 6 February 2017. The FTC and the New Jersey Attorney General. Vizio and its data firm, Inscape, paid $2.2 million. The software sat on 11 million smart TVs and collected what was on the screen. The feature was named Smart Interactivity. After an update the set said the privacy policy had changed, that Smart Interactivity was enabled, and that you could turn it off in a menu. The message timed out after a minute. It did not say the viewing history was passed on. The order tells them to state what is collected, who receives it, and why, in a disclosure separate from any privacy policy or terms of use, to get affirmative express consent, and to say how to take that consent back.

Samsung's name for the same idea is Viewing Information Services. The Texas Attorney General's petition against Samsung, written for Christmas 2025, says the setup screen offers one obvious control, "I Agree to all," and that reading the notices behind it takes more than 200 clicks across four or more menus. The petition's charge is that the friendly name hides automatic content recognition.

A footer, a pre-checked "Help improve hello-world" box, and a first-run Enter are that pattern on a smaller screen. A new name does not change what leaves the machine. A policy rewritten so it disagrees with the screen is the misrepresentation the Vizio order forbids. She will not sign off on an Insights team whose job is to receive plans. The dissent can be filed. The proposal is rejected.

- "Smart Interactivity was the alias. The FTC still called it a viewing history and sent a bill for $2.2 million."
- "He can hire twelve lawyers. They cannot make a checked box into the consent that order describes."

Dave Pell answered him by name. Computer policy is on the machine before the app is assigned. He already sets TurnOffSharedCounts and TurnOffSync. A first-run beacon ignores both, and then the rollout mail, which says nothing is sent, is false. He pulls that assignment. Group Policy does not read a EULA. A kiosk and a night-shift PC never see the checkbox. A sponsored line in the thought lands on a shared screen. His privacy officer already has to clear a room number in the handoff notes. An ad in the thought does not get that far. An Insights vendor is a processor he did not put on the ticket, and he does not want that headcount on the image.

- "The mail says nothing is sent. His Smart Greeting sends the plan before anyone reads the mail. That image does not ship."
- "Group Policy does not click I agree. If the binary phones home anyway, I take the assignment back."

### Outcome

Rejected. The profit maximizer filed a dissent. Smart Greeting, the partnerships, the ads in the thought, and the bundled notice are not in the program. The engineers' line stands: no accounts, and no network unless the person turns a share on. His prices, and Casey's colour theme and QR code, stay in this review only.

### Ruth on security

Ruth Okonkwo read 9ca4e38. She rated the phone keys on the counts-server origin as high (not fixed, above). She rated the push redirect, the sync put without `If-Match`, and the gone-stamp deletion as medium, and those are fixed. She also named the uninstall junction, which is the residual above. On round 43 she agreed that unknown keys, the shipping launcher, and stale temp files are fixed, and that a portable Windows folder still has no DACL in this tree.

- "The phone seals the plan with a key that sits in localStorage on the origin that just served the script."
- "Push.send will leave the allowlist on a 302 and take the VAPID header with it."
- "Once the added line has been trimmed, an old gone stamp deletes a live household item and the restore list never sees it."

### Helen on access

Helen Park uses NVDA and also spoke for motor, ADHD, and dyslexia needs. She heard "greater" at the end of every prompt. She marked both items done and heard that one was finished. That second one is the low finding above, and the text screen now says the count. She asked the window to speak Saved or Kept before focus returns to the plan box. That is not in this round. No account and no new network.

- "NVDA says greater at the end of every prompt, and that word is wasted time."
- "I marked both items done, and the program told me one was finished."
- "Speak the result in the window and on the text screen, in the same short words."

### Dave on rollout

Dave Pell, before any assignment, would set computer policy: sign-in launcher off, plans off, streak off, shared counts off, sync off. He would leave the notes lock unset so DPAPI still seals them. He will not ship an unsigned package, a build with `COUNTS_SERVER` set, or a rollout mail that says nothing is sent while policy still names a server. He also noted that the scripts are unsigned, so an AllSigned policy fails because install uses `-ExecutionPolicy Bypass`, and that no policy forbids the clock reminder task (`DisableSignInLauncher` is the sign-in launcher only). Those stay as rollout notes.

- "Computer policy is in before the app is assigned: sign-in launcher off, plans off, streak off, shared counts off, sync off."
- "I install the system package only, under our signature, with that signed hash in the ticket and QuietUninstallString as the removal line."
- "The rollout mail says nothing is sent anywhere, and this build still knows a counts server, so that mail waits."
