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

## For employees

Open **hello-world** from the Start menu, or type "hello-world" in Windows
Search. A window opens with the day's thought and tip, and a box for one thing
you want to get done today. Type it and press Enter, or click **Not today**.
That's all you need. Everyone sees the same thought and tip on the same day,
so you can compare notes with a coworker.

A few things for one day go in the same box with `;` between them, such as
`Call Ana; send the report`. Saving says "Saved." and leaves the window open;
Enter again closes it.
The next day the window asks "Did you do it?" with three buttons: **Done**,
**Not yet** (keeps the plan for today) and **Skip** (asks again next time).
For a plan of a few things, tick the ones you did before clicking Done, and
the rest are kept for today. The text screen asks the same with numbers:
`1 3` means the first and third are done.
When today's plan is finished, click **I did it**; if you changed the words in
the box first, the new words are what's marked done. To drop a plan, empty
the box and click **Save**. Typing a new plan instead of answering keeps the
old one for `same`.

After your first plan it asks once whether you want a reminder when you sign
in. With it on, a Windows notification appears at your first sign-in of the
day, only when there is a plan to ask about: "Last time you planned: ... Did
you do it?". Click **Done** or **Not yet** on it and that's the answer; nothing
else opens, and Done brings a short thank-you. Skip is there too. Click the notification itself
to open the window. With no plan, it stays quiet, unless you choose
**Options > Reminder settings > Also on days with no plan**. The same menu
moves the reminder to 8:00, 9:00, 10:00 or 13:00 instead of sign-in, opens
the window after you answer, and keeps weekends quiet. Days your organization
lists as holidays are quiet too. **Options > Greet me by name** puts your
first name at the top.

Options also has **This week...** (what you finished since Monday), **My
numbers...** (days opened, your longest run and plans finished, once you turn
on **Keep my numbers**), **Save my plans to a file** (a Markdown file in
Documents), **Keep a longer history** (60 finished plans instead of 7), and
**Tips for floor and shift work**, a second list of 40 tips for warehouses,
factories and shifts in place of the desk ones.

Every on-or-off choice also works from the command line, for example
`hello.cmd --set numbers on`. The names are `nudge`, `open_after`,
`no_weekends`, `name`, `no_startup_visits`, `long_history`, `hide_finished`
(no finished list in the text screen), `expire_same` (`same` forgets an
earlier plan after 30 days), `no_count` (no done count kept), `numbers`,
`close_after_done` (the text screen closes after `done` and the next plan)
`colon_prompts` (prompts end in `:` instead of `>`) and `floor_tips`. `--week`,
`--numbers` and `--export` print or save the same as the window, and
`--plain-local` prints the greeting in your language. **Options** in the window
turns the reminder off, hides the thought and tip, turns on the days-in-a-row
message, picks a language other than the Windows one, shows what is saved,
deletes everything (your settings stay), or switches to the text screen. In
the text screen, menu option 10 picks the language, and pressing Ctrl+C twice
closes it.

### The text screen

hello-world also runs as text in a console window, for anyone who prefers
typing to clicking. Choose **Options > Use the text screen** in the
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
need. Press Enter to skip the question; after two skips it stops asking and
shows the plan as still open, and `done` still works. A plan first set more
than two weeks ago is put away, and `same` brings it back.

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

It makes no network connections and reports nothing to IT or managers. Other
people who can read your computer's files, such as IT staff, could read the
file, so don't type passwords or private details.

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

### From a git clone

Run these in one PowerShell window opened as administrator, each line on its own. Change the
first two lines to the release tag and the full 40-character commit hash that
was reviewed, and keep the quotes.

```powershell
$tag = 'v1.37.0'
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
