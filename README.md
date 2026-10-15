# hello-world

A small daily moment for employees, written in Python, and the PowerShell
installer that deploys it to Windows workstations. It starts every day with
"Hello, world!".

## What it is for

hello-world is a small daily moment for the people who use it. Each time you
open it, you get a greeting, one short thought, and one small thing to try
that takes under five minutes. You can also write down one thing you want to
get done today. The next day it asks, gently, whether you did it, and offers to
keep it for today if you didn't.

It is meant to be useful in under twenty seconds, which is why people keep
opening it. It has no accounts, no network access, no scores and no reminders
unless you ask for one.

## For anyone, at home or at work

hello-world isn't only for companies. Anyone on Windows can install it for
themselves, with no administrator and no account: see "For one person,
without an administrator" below. A package built for people outside an
organization sets `COUNTS_SERVER` in `hello.py` to a public counts server, so
the shared count works for them too once they say yes to it. To run that
public server, put `server/counts_server.py` on any host with Python 3.11 and
an https front end (a reverse proxy or a platform that terminates TLS), start
it with `--trust-proxy` behind that proxy, and set `COUNTS_SERVER` to its
address before building the package. It keeps one small file of numbers a day.

## For employees

Open **hello-world** from the Start menu, or type "hello-world" in Windows
Search. A window opens with the day's thought and tip, and a box for one thing
you want to get done today. Type it and press Enter, or click **Not today**.
That's all you need. Everyone sees the same thought and tip on the same day,
so you can compare notes with a coworker.

A few things for one day go in the same box with `;` between them, such as
`Call Ana; send the report`. Saving says "Saved." and leaves the window open;
Enter again closes it.
The next day the window names the day, "Yesterday you planned: ..." or "On
Friday, 2 October 2026 you planned: ...", and asks "Did you do it?" with
four buttons: **Done**, **Not yet** (keeps the plan for today), **I'm not
sure** (keeps it for today with no mark either way; `?` on the text screen)
and **Skip** (asks again next time).
For a plan of a few things, up to ten, tick the ones you did before clicking
Done, and the rest are kept for today. The text screen asks the same with
numbers: `1 3` means the first and third are done, and `1-3` the first
three.
When today's plan is finished, click **Done** under the plan box. A plan of
a few things has a tick box for each: tick what you finished, then click
**Done**. If you changed the words in the box first, the new words are what's
marked done, and today's unfinished things stay. While the window asks about
an earlier plan, only that plan's **Done** shows. To drop a plan, empty the
box and click **Save**. A new plan typed over unfinished things, or instead of
answering about an earlier plan, keeps them after it and says so: "Still on
your list from before: ...". A plan can be up to 400 characters. A plan
typed while the window asks about an earlier one is saved along with the
answer.
A date written in a plan becomes its due date: `30/10` (or `10/30` where
Windows writes the month first), `2026-10-30`, a weekday's name, or "by"
and a weekday, today or tomorrow, as in "send the report by Fri".
**My plans > Due date for my plan...** sets or removes one from the next ten
workdays. The plan, the next day's question and the notification then
say "Due today.", "Due tomorrow." or the date, and the date stays with the
plan while it is carried over. After a missed workday the window says
"Welcome back." and nothing else about the gap.

After your first plan it asks once whether you want a reminder when you sign
in. With it on, a Windows notification appears at your first sign-in of the
day, only when there is a plan to ask about: "Did you do it?". It leaves the
plan's words out, so a shared screen doesn't show them, unless you choose
**Options > Reminder... > Show my plan in the reminder**. Click **Done** or **Not yet** on it and that's the answer; nothing
else opens, and Done brings a short thank-you. Skip is there too. For a plan
of a few things the notification has **Open** instead of Done, so you tick
the ones you did. In the text screen, `done` on a plan of a few things asks
which ones, by number. Click the notification itself
to open the window. With no plan, it stays quiet, unless you choose
**Options > Reminder... > Also on days with no plan**. The same menu
moves the reminder to 8:00, 9:00, 10:00, 13:00, 15:00, 18:00 or 22:00
instead of sign-in, opens
the window after you answer, and comes on weekends only if you choose **Also
on weekends**. The same menu also has **My day starts at**: midnight, 4:00,
12:00 or 18:00, when "today" turns into tomorrow; 18:00 keeps a night shift
from 22:00 to 6:00 on one day. **Every day at...** adds a daily repeat, such
as taking pills, with its own reminder at one of those times (type the words
in the plan box first; in the text screen it's **Every day...**). It's a
reminder only, not a medical device, and its notification leaves the words
out unless **Show my plan in the reminder** is on. **My plans > Print a big
page for the fridge** opens today's plan and the daily repeat in big print in
the browser, to print; it says anyone in the room can read it, and never has
the sync code. Days your organization
lists as holidays are quiet too. **Options > Greet me by name** puts your
first name at the top. Turning off **What the window shows > Also show the
thought** hides the thought and keeps the tip.

Options also has **This week...** (what you finished since Monday, and last
week), **My
numbers...** (days opened, your longest run and plans finished, once you turn
on **Keep my numbers**), **Save my plans to a file** (a Markdown file in
Documents, with a `.csv` copy that opens in a spreadsheet; **Delete the plans
file I saved** removes both), **Keep a longer history** (finished plans kept for a year instead of 14 days), and
**Tips for floor and shift work**, a second list of 40 tips for warehouses,
factories and shifts in place of the desk ones.

Every on-or-off choice also works from the command line, for example
`hello.cmd --set numbers on`. The names are `nudge`, `open_after`,
`weekends`, `name`, `no_startup_visits`, `long_history`, `hide_finished`
(no finished list in the text screen), `expire_same` (`same` forgets an
earlier plan after 30 days), `no_count` (no done count kept), `numbers`,
`close_after_done` (the text screen closes after `done` and the next plan)
`colon_prompts` (prompts end in `:` instead of `>`), `floor_tips`,
`private_reminder` and `hide_thought`. `--week`,
`--numbers` and `--export` print or save the same as the window, and
`--plain-local` prints the greeting in your language. **Options** in the window
turns the reminder off, hides the thought and tip, turns on the days-in-a-row
message, picks a language other than the Windows one, shows what is saved,
deletes everything (your settings stay), or switches to the text screen. In
the text screen, menu option 10 picks the language, option 12 has the
reminder times and the window's other settings, and pressing Ctrl+C twice
closes it.

### The text screen

hello-world also runs as text in a console window, for anyone who prefers
typing to clicking. Choose **Options > Text screen... > Use the text screen** in the
window, or ask IT, who can set it for everyone. In the text screen, menu
option 9 switches back to the window. Press Enter at each question to skip it,
and once more to close.

hello-world speaks the Windows display language when it has a translation:
English, Spanish, French (France and Canada), Portuguese (Brazil and Portugal), German, Simplified Chinese, Japanese, Korean, Arabic and Hebrew. Chinese, Japanese, Korean, Arabic and Hebrew show in the
window; the text screen shows English for them, since older consoles can't
draw those scripts. Options > Language picks another one. The words you type work in every language, so `done`,
`hecho`, `fait`, `feito` and `erledigt` all mark a plan done. One-letter
answers are the exception: `s` means yes only in Spanish and Portuguese, `o`
only in French and `j` only in German, so a stray key in English never
finishes a plan.

At the last prompt:

- Press Enter to close. `q`, `quit`, `exit`, `x` and `close` also close.
- Type `done` when you finish today's plan. It shows your last three finished
  plans, then asks for the next one. Enter there closes.
- Type `plan` to set or change today's plan. Changing today's plan simply
  replaces it. At any plan prompt, `same` brings back a plan from an earlier
  day that you didn't finish. A finished plan is never offered back.
- Type `menu` (or `m`) for the options: see what is saved, open once a day at
  sign-in, hide the days-in-a-row message, delete everything, help, set today's plan,
  forget one finished plan, and hide the thought and tip. The options are read
  once; type `m` to hear them again. Enter at the menu goes back. Typing
  `menu` at the plan question opens the menu too.

`q` closes the window from any question, the menu included, and today's visit
still counts. So do `x` and `close`.

If you don't type `done`, the next visit asks "Did you do it?". A yes is
counted on the spot, and `ok`, `sure`, `did it` and `finished` are yes
too; `nah` and `not really` are "not yet". If the plan is more than a day old, it lists the days
since and you pick one by number. "Not yet" lets you keep the plan for today, as many days as you
need. `sideways` (or **The day went sideways** in the window) asks: carry it
over, or set it aside? Carrying it over is the default; either way nothing is
marked. A plan two or more days old asks "Fresh day. Bring it over, or start
clean?", never how many days were missed. A plan carried over again and again
gets asked once whether to make it smaller or set it aside, and after a few
sideways days in a week the plan question offers once to keep today's plan
small. Those sideways days are kept only on the PC and never shown.
**End the day** (`end` at the last prompt, More settings, or **My plans** in
the window) goes through each thing: done, carry to tomorrow, or set aside,
then says plainly what happened ("Done 1, carried 1, set aside 1"). The
window and the phone have a **Large print** button on the first screen. Press Enter to skip the question; after two skips it stops asking and
shows the plan as still open, and `done` still works. A plan first set more
than two weeks ago is put away, and `same` brings it back. With no plan, the
question ("Anything for today? Small is fine.") lists up to three plans put
aside, by number, so one keystroke brings one back.

If a plan sounds like several things joined together, it says once that
finishing the first part still counts.

The days-in-a-row message is off until you turn it on, under Options or with
menu option 3. Then it shows only on your 3rd, 7th and 14th visit in a row,
then every 30th. A visit within four days of the last one counts, so weekends
and a day off don't break it.

The text screen asks once whether to open by itself when you sign in.
Whatever you answer, menu option 2 changes it later.

Everything works from the keyboard with plain text, in one top-to-bottom flow,
so a screen reader reads it in order. Each prompt ends by saying what Enter
does. It was checked with Narrator in a real console for version 1.16.0. If
two windows are open, each one keeps the other's changes.

To stop using it, you don't need IT: turn off the sign-in opening with menu
option 2, delete your notes with option 4, and don't open it again. To remove
the program itself, use Settings > Apps > Installed apps > hello-world >
Uninstall. That needs an administrator password, so ask IT if you don't have
one.

### What I did, large text, and no follow-up questions

**Options > My plans > What I did...** (menu option 12 in the text screen)
lists the last two weeks, one line a day, newest first: what you finished,
what you weren't sure about, and "nothing noted" on days with nothing, so no
gap is left to wonder about. It offers to print the page. **Take back a
Done...** undoes a Done clicked by mistake and puts the thing back on
today's plan.

**Options > Large text** makes the whole window half
as big again, and stays that way.

**No follow-up questions** in the same menu, or `gentle` at the last prompt,
stops "Did you do it?". Your plan stays until you mark it done or change it;
after three days it folds away quietly, and `same` brings it back. Days and
dates you type stay words, not due dates, and the days-in-a-row message
doesn't show. It's offered once, after a first "not yet" or "not sure", and
never again. Nothing records that you turned it on.

If your organization sets a support line, such as an employee assistance
number, it is under "If things feel heavy, someone to talk to" at the end of
the text menu's options and in the window's Options. It never appears by
itself, never reacts to what you type, and nothing records that you looked.

### In the tray

**Options > What the window shows > Keep hello-world in the tray** puts a
small icon in the corner of the taskbar from each sign-in. It shows a dot while
yesterday's plan waits for an answer. Click it to open hello-world, or
right-click for **Done**, **Not yet** and **Open**. It never opens anything by
itself; for one nudge at a time you pick, use **Options > Reminder...**.

### Pro

Pro is $5 once, or $8 once for a household: a second check-in in the
afternoon or evening (15:00 to 21:00) on days your plan is still open, and
window colours; a household key is used on everyone's devices and also opens
the shared household list when it ships. History (a year, with a **This
year** page), pets, reminders and everything else stay free. Keys come only
from the official store, and hello-world never calls, texts or emails to sell
or check one; the screen where you paste a key says so.

### Letters to family, and the devices syncing

**Letters to family** (More settings or `letters` in the text screen, **My
plans** in the window, and the phone) are written in hello-world and kept
only on that device until you choose **Send with my own mail** (or messages
on a phone), which opens your own mail or messages app with the words filled
in; you press send there. hello-world never sends anything itself. A sent
letter isn't kept unless you choose to keep a copy, and **Delete every
letter** clears them all in one step.

With sync on, each device writes a name you choose ("Kitchen tablet"; "A PC"
or "A phone" until you do) and the day it last synced into the encrypted
sync copy, so the server can't read them. The sync screen lists them with a
short ID each, and says when two share a name. A name you don't know means
the code got out: **Change my sync code** gives a new code, deletes the old
copy on the server, and lists only this device until the others type the
new one. The server keeps only the encrypted copy, its size and when it was
last written.

### The household list

With a household key, **My plans > Household list...** in the window (or
`house` at the last prompt, or More settings) starts a shared list: things
anyone in the household can add and tick, each on their own PC or phone. It
gets its own 25-character code; give it to each adult in person, and they
type it on their own device with their own name. Nobody can add someone else,
and nobody can set reminders or send anything in another person's name.
Everyone is told when someone joins or leaves. Each thing shows who added,
ticked or removed it and on which day (not the minute), visible to everyone,
and nothing counts who did what. Removed things can be restored for 30 days.
When someone leaves, every other device asks until answered whether to make
a new code so the old one stops working; the person who left keeps whatever
was already on their device. The list is encrypted with its code before it
leaves a device, padded so its size says little, and kept on the counts
server like sync.

hello-world collects nothing about anyone, adult or child: no account, no
name, no age, and no plan text leaves a device unless you turn on sync,
encrypted with a code only your devices have. That is why a household key
needs nothing from a child to work. Paste the key in **Options > Pro...** (copy it
first; it is read from the clipboard), type `pro` at the end of the text
screen, or run `hello.cmd pro <key>`. The key is checked on your PC: there is
no account and nothing is sent. Window colours step aside when Windows high
contrast is on. `docs/PRO.md` is how the owner makes and sells keys.

### A desk pet, plans put aside, and the weekly boss

Type `pet` at the last prompt, or choose **Options > What the window shows >
Desk pet**, for a small pet that lives under your plan: `(o.o)  Biscuit is
judging the weather.` It sleeps while you're away and is glad when you're back.
It never gets hungry, never gets sad and never dies. Every 5 things you finish
it gets something to keep, and wears the newest one; the screen says how many
more until the next. Turn it off and it keeps its things for next time.

Plans that move aside (one replaced, cleared, or put away after two weeks) are
listed under **Plans put aside**, from the menu, Options > My plans, or by
typing `aside`, and only there. A number puts one back on today's plan. They're
listed plainly. **Funny farewells** ("It went to find itself.") is a switch,
and never shows with no follow-up questions.

With the shared count on, each week has a silly boss, such as The Inbox Hydra
or Gerald. Every tip anyone does that week is one hit: "This week's boss: The
Inbox Hydra. 212 of 500 hit points gone, from everyone's tips." Its hit points
are 70% of last week's tips, so a small company can win too. It's counted
from the same numbers as the tip count, with nothing more sent. When it falls,
every desk pet gets a trophy. There are no names, no per-person scores and no
penalty if it survives.

### From a command line, for engineers

`hello.cmd` in PowerShell or cmd, or `hello` in WSL and Git Bash (it runs
`hello.cmd` on Windows, so it reads the same notes), takes these words. None of
them prompts unless you're at a terminal, they print plain text, and they exit
0 when it worked, 1 when something failed and 2 for a usage mistake.

```
hello plan "fix flaky test; review PR 88 by Friday"
hello plan                  # today's plan, numbered (--json for scripts)
hello add "ship 1.2"
hello done 2                # or done 1-3, or done all
hello import todo.txt --pick 1 3
hello standup --git --repos ~/src/* --author me@work.com me@home.net --remember
hello export | grep PR
```

A bare `hello done` finishes a plan of one thing and refuses a plan of
several, so a standup never says more than you did. `import` reads a todo.txt
file and never writes to it: done (`x`) lines are skipped, priorities and dates
are dropped, `due:` becomes the due date, and running it twice adds nothing
twice. `standup` lists what you finished since the last workday (Friday on a
Monday, skipping weekends unless you work them, and your organization's
holidays), today's plan, and with `--git` the subjects of your own commits in
local repositories. `--remember` keeps `--git`, `--repos` and `--author` for
next time. In WSL, `--git` runs the Windows git. Tickets from Jira and the like
would need network credentials, so they aren't read. `export` prints every
saved plan as tab-separated text, since the file itself is locked.

### What is saved, and who can see it

This is the one place that lists what is saved. `PLAN.md` and the why-doc link
here.

hello-world saves one small file, `notes.json`, in the `hello-world` folder
under `AppData\Local` in your own user folder. It holds the date you last
opened the program (the dates of the last 60 days only if you turned on the
days-in-a-row message, which needs them), your current plan, an unfinished
earlier plan, how many times you marked a plan done, and the plans you
finished in the last 14 days, or 90 with a longer history (words and date). It also holds your settings for the days-in-a-row
message, the thought and tip, and the window or text screen, your answer to
the sign-in question, and the date of the last sign-in reminder, so it comes
once a day at most.
Nothing else: no name, no computer name, no times. Older dates are dropped, so
the file is never a long record of when you worked. An empty `notes.lock` file
sits next to it and holds nothing.

Turning the reminder on adds three entries to your own part of the Windows
registry: the sign-in value under `Run`, the name the notification shows, and
the `hello-world:` links its buttons open. Turning it off removes them.

It reports nothing to IT or managers. The only network connection it can
make is the shared count below, and only after you say yes to it.

### Shift handoff, on shared PCs

Where your organization turns on shift handoff for a PC (a dock office PC, a
nurses' station, a cart on a unit), the top of hello-world shows the notes
the last shift left on it, with how long ago each was left: "1. 8 h ago:
Forklift 2 pulling left; Dave out Thu". Type `handoff` at the last prompt,
or use the box in the window, to leave one. Notes show for 72 hours unless
your organization changes that. A note about safety can be kept until
someone clears it, and anyone can clear a note that is wrong.

Everyone who signs in to that PC reads the notes, and the screen says so.
Press Enter in the note box to leave it; you'll see "Note left for the next
shift, 22:40." Where the organization asks for it, hello-world opens by itself
at sign-in when there's a note you haven't seen (never for your own), and
signs new notes with your first name, which the box says before you type.
Notes written before that was turned on are never signed.

They aren't signed unless you or your organization sign them, and they aren't a safety or defect
record, or a place for patient or customer details. They are locked to the PC
in `ProgramData\hello-world`, or kept in a unit's shared folder that your
organization names, so every cart on a unit shows the same notes. Your own
plan stays private to your account.

### The shared count

When a shared counts server is set up, either by your organization's policy
or in the package you installed, hello-world asks you once: "See how many
people do each day's tip?" Say yes and the count shows under the tip. Type
`tip` at the last prompt, or click **I did this tip** in the window, when you
have done it, and you are counted once for that day.

The thought gets reactions too: love, ha, dead or eyeroll (or the emoji),
typed at the last prompt or clicked under the thought in the window. The
counts stay hidden until you react, so you aren't nudged, and the screen
shows yesterday's top reaction. Each PC has one reaction a day; picking
another moves it. The window opens at once and fills the numbers in when the
server answers.

Each count sends the date and nothing else: never a plan, a name or a
computer name. The server sees your PC's network address, as any website
does. The reference server, `server/counts_server.py`, doesn't write
addresses anywhere. It keeps only a daily, in-memory hash of them, so each
PC counts once a day. Turn the count on or off in the window under
**Options > What the window shows**, or with menu option 12 in the text
screen, or `hello.cmd --set shared off`. Without a server, nothing is asked
and nothing is sent.

So a small office can't tell who did the tip, the reference server never
sends a count below 10: it says "a few" instead, rounds larger counts to 5,
and changes the numbers it sends only once an hour, so checking before and
after someone's click shows nothing. `--min-group` and `--refresh` change
those. Thoughts and tips your organization replaced are labeled "from your
organization".

To keep its disk from being filled, the server keeps at most `--sync-quota`
encrypted sync copies (100,000; one already there can still be updated),
takes at most 20 new copies a day and 60 writes a minute from one address,
and removes copies untouched for a year every hour. Those per-address limits
live in memory and reset when the server restarts, so rate-limit at the https
proxy in front too.

The file also holds the day you last counted yourself for the tip, whether
you answered the shared count question, today's reaction, the newest handoff
note you have seen, the plans you answered "I'm not
sure" about in the last two weeks, and your settings for no follow-up
questions and large text.

Since 1.44.0 the file is locked to your Windows account with the Windows
Data Protection API, so a plan can be anything you want to get done, at work
or not. Other people who use the PC, and anyone who copies the file, see only
scrambled data. Someone with full admin control of the PC could still get to
it while you are signed in, so don't type passwords. A file saved by an older
version is locked the next time you save. If your organization turns on the
`UnlockedNotes` policy, the file stays readable as before, and the first
screen says so and asks you to keep it to everyday tasks.

If IT resets the password of a local (not domain) account, Windows can no
longer unlock that account's notes. hello-world then sets them aside as a
backup and starts fresh. Domain accounts keep their notes through a reset.

Files you save yourself with **Save my plans to a file** are not locked.

Menu option 1 shows all of it, and whether it opens by itself at sign-in.
Option 7 forgets one finished plan, and option 4 deletes everything. After a delete the file holds only a random marker, so
another open window can't write the notes back. A damaged file is kept as
`notes.json.bak` until you delete everything. Uninstalling leaves your notes
in place, so if you don't want them kept, delete them with option 4 first.

## For IT: install

There are two ways to install. Both check every file before anything changes,
install for all users under Program Files, and exit 0 on success, 1618 when a
file in use blocks the upgrade, and 1 on any other failure.

- **From the release package**, for deployment tools and for PCs without Git
  or internet access. `docs/ENTERPRISE.md` covers Intune, MECM and Group
  Policy, detection rules, signing, logging and the security model.
- **From a git clone** at a reviewed commit, below.

### From the release package

Each release on GitHub has a package zip and, in its notes, the package hash.
Unzip the package into a folder only administrators can write, such as
`C:\Program Files\hello-setup`, then run this as administrator or SYSTEM, with
the package hash from the release you reviewed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1 -PackageHash <package hash> -Quiet
```

The package hash is the SHA-256 of the package's `SHA256SUMS`, which lists the
hash of every file. Anyone can rebuild the package from the reviewed commit
with `tools\build-package.ps1` and get the same hash, so the hash doesn't rest
on the release alone.

### For one person, without an administrator

Where IT allows it, such as on a laptop for site days, one person can install
hello-world for themselves from the release package, with no administrator:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File install-user.ps1 -PackageHash <package hash>
```

It checks the package the same way, installs into
`%LOCALAPPDATA%\Programs\hello-world`, and adds hello-world to that person's
Start menu and Settings > Apps, where Uninstall removes it. That folder is
in their own profile, so they, and programs running as them, can change it;
the all-users install is the one to use wherever IT can.

### On a phone

`phone/` is hello-world for a phone: a web page you open once and add to the
home screen. It works with no signal, opens in English, Spanish or Arabic by
the phone's language, and has one screen: "Did you do it?" with big Done, Not
yet and Skip buttons, a box for today's plan, and the same thought and tip as
the PC that day. Plans stay in that phone's browser and leave it only with
sync on. **The day went sideways** sets a plan aside with nothing marked;
plans set aside come back with one tap when there's no plan.

A reminder only comes if you pick a time. Served by a counts server started
with `--remind`, it arrives even with the page closed: the phone sends the
server a random token, its browser's push address and the time in UTC, and
nothing else, and the server sends a push with nothing in it at that time;
the phone shows "Check-in time" from what it keeps itself. The server only
calls the browser makers' push services, and forgets the address when the
reminder is turned off, the push service says it's gone, or a year passes.
On an iPhone, add hello-world to the Home Screen first. Without `--remind`,
phones only let a web page remind you while it's still open in the
background, and the settings say so.

The settings also have **My day starts at** (as on the PC), **Every day**, a
daily repeat such as "Take my pills" at a time you pick, which is a reminder
and not a medical device and whose words stay on the phone, **Family**, a
name and number kept on the phone that adds **Draft text to** and **Call**
buttons, which only open the phone's own text and call screens with "I'm
okay today." filled in, **Print a big page** for the fridge (it says anyone
in the room can read it, and the sync code is never on it), and **Save my
plans to a file**, a plain-text copy of everything.

Host the folder on any https address (GitHub Pages works; reminders then
work only while the page is open), or run the counts server with
`--phone phone --remind` to serve it at `/phone/` with reminders.
`python tools/build_phone.py` refreshes its thoughts and tips from `hello.py`.

### Sync between a PC and a phone

Off unless you turn it on, under **Options > My saved notes > Sync with my
phone**, `sync` in the text menu, or `hello.cmd sync on`. The PC shows a code
such as `k7mqa-2p9xb-tz4wc-8hcdd-r3vne`; type it once on the phone, in the
phone app's settings. From then on the plan and the done list are the same on
both, the newer plan winning and both done lists kept.

With sync on, your plan and done list leave the device, encrypted with that
code before they go, and the counts server keeps only the encrypted copy under
a label made from the same code. The phone app needs to be served by that
counts server (`--phone`). The scheme is PBKDF2-SHA256, then HMAC-SHA256 as a
counter-mode stream with an HMAC tag, built from what both Python's standard
library and a browser have; it has had no outside audit. `hello.cmd sync code`
shows the code again for a new phone, and `hello.cmd sync new` (or **Change
my sync code**) makes a new one, moves the copy and deletes the old one, so a
code someone else saw stops working.

Wherever the code shows, it says: hello-world has no phone line and no
support staff, never calls, emails or texts, and nobody real will ever ask
for your sync code. Before showing it, it asks whether anyone is on the phone
with you or asking for it; a yes keeps it hidden. The text screen also waits
ten seconds, since a scammer's script is to hurry you. The app always makes
the code itself, so a guessable one like `password123` can't be set. Turning sync off, or deleting
everything, deletes the server's copy. The `TurnOffSync` policy keeps it off
on work PCs.

### Portable, with no install

For a personal PC: download `hello-world-portable-<version>.zip` from the
release, unzip it anywhere you can write, such as Documents or a USB stick, and
double-click **Start hello-world.cmd**. Nothing is installed and nothing goes
in the registry. Notes stay in the `notes` folder next to it, locked to your
Windows account, and deleting the folder removes everything.
`tools\build-portable.ps1 -OutFile hello-world-portable.zip` builds the same
zip. The portable zip is not a way around an employer's software rules: on a
work PC, ask IT, who can deploy the package above.

### From a git clone

Run these in one PowerShell window opened as administrator, each line on its own. Change the
first two lines to the release tag and the full 40-character commit hash that
was reviewed, and keep the quotes.

```powershell
$tag = 'v1.62.0'
$commit = '0123456789abcdef0123456789abcdef01234567'
$d = "$([Environment]::GetFolderPath('ProgramFiles'))\hello-setup"
New-Item -ItemType Directory $d
$icacls = "$([Environment]::SystemDirectory)\icacls.exe"
$git = (Get-ItemProperty HKLM:\SOFTWARE\GitForWindows).InstallPath + '\cmd\git.exe'
& $icacls $d /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F'
& $git clone -b $tag --depth 1 https://github.com/thrash-d/hello-world $d
cd $d; Set-ExecutionPolicy -Scope Process Bypass -Force
.\install.ps1 -Commit $commit
```

This way needs Git for Windows installed for all users and internet access to
download Python. The permission checks on Git can take several minutes, so let
them finish.

### What the installer does

It checks six steps and prints `[1/6]` to `[6/6]` as it goes. The result line
says whether this was a new install, a reinstall, or an upgrade. It refuses to
install an older version over a newer one unless you add `-AllowDowngrade`.
`-Publisher` sets the name shown in Settings > Apps.

For an unattended run, add `-Quiet`. It prints only warnings and the result
line, and never asks a question. Everything is written to
`%WINDIR%\Logs\hello-world\install.log`, which only administrators can read,
and the result goes to the Application event log under the source
`hello-world`.

Employees can turn on a once-a-day opening at sign-in themselves. It's a value
under their own `HKCU\...\Run` key that starts the installed program and does
nothing once the program is gone. Group Policy can turn it off; see
`docs/ENTERPRISE.md`.

### Update to a new release

An update is a fresh install of the new release, and the installer upgrades in
place. With the package, unzip the new one and run its `install.ps1` with its
package hash. With a clone, delete the setup folder first, running each line
on its own:

```powershell
cd \
Remove-Item -Recurse -Force $d
```

Then repeat the clone steps with the new tag and commit.

### If something fails

The last line starts with `FAILED:` and says what to fix, and the log has the
full record. A failed run leaves any working install as it was:

- An upgrade that fails at step 6 (the Apps entry or the shortcut) puts the
  previous install back.
- A first install that fails there leaves no Apps entry or shortcut, so a
  deployment tool's detection sees it as not installed and tries again.
- An open hello-world window doesn't stop an upgrade: its copy is renamed
  aside and removed by the next install.
- If a file in the install folder is in use, for example by antivirus, it
  exits 1618 with nothing changed. Run it again later, or let the deployment
  tool retry.

Each PC's Apps entry records the installed version, the package hash or
commit, the bundled Python version and the install date, and has a
`QuietUninstallString` for unattended removal. This shows what is installed:

```powershell
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world
```

## Files

- `hello.py`: the program. `hello.cmd --help` lists its options, such as `--plain`, which prints only the greeting and saves nothing.
- `install.ps1`, `uninstall.ps1`: deploy and remove it.
- `tools/build-package.ps1`: builds the offline release package, optionally with the organization's own thoughts and tips.
- `examples/content.json`: a sample organization content file.
- `policy/`: Group Policy templates (ADMX, and ADML in English, Spanish, French, Portuguese and German).
- `docs/ENTERPRISE.md`: deploying to a large fleet, and the security model.
- `docs/ROLLOUT.md`: an announcement, an employee FAQ, and a page for privacy reviewers.
- `docs/ACCESSIBILITY.md`: how it meets accessibility expectations, and how that was checked.
- `test_hello.py`: run with `python test_hello.py` (Python 3.11 or later).
- `VERSION`: the release version; a new version on `main` gets a tag.
- `hello.<language>.json`: the translations, which `hello.py` reads at
  start. A regional one, such as `hello.fr-CA.json`, holds only what differs
  from its base language.
- `CHANGELOG.md`, `TODO.md`, `reviews/`: change history, the build queue
- `LICENSE`: MIT.
  with reasons, and the saved review of each round.
- `PLAN.md`: the value and rollout plan.
- `TODO.md`: what a six-voice panel agreed should be done next.
- `docs/WHY-DAILY-ACTIONS.md`: why it changed from a greeting to a daily program.
- `docs/PILOT.md`: the simulated 30-day pilot and what it changed.
- `docs/PERSONAS-2026-10.md`: how simulated personas and an advisor agent were used to decide rounds 70 on, what was checked against the code, and the track record. `docs/personas/` has the brief and prompts to run it again.
