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
Search. Press Enter at each question to skip it, and once more to close.
That's all you need. Everyone sees the same thought and tip on the same day,
so you can compare notes with a coworker.

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
  once; type `m` to hear them again. Enter at the menu goes back.

`q` closes the window from any question, the menu included, and today's visit
still counts. So do `x` and `close`.

If you don't type `done`, the next visit asks "Did you do it?". A yes is
counted on the spot. If the plan is more than a day old, it lists the days
since and you pick one by number. "Not yet" lets you keep the plan for today, as many days as you
need. Press Enter to skip the question; after two skips it stops asking and
shows the plan as still open, and `done` still works. A plan first set more
than two weeks ago is put away, and `same` brings it back.

If a plan sounds like several things joined together, it says once that
finishing the first part still counts.

The days-in-a-row message shows only on your 3rd, 7th and 14th visit in a
row, then every 30th. A visit within four days of the last one counts, so weekends and
a day off don't break it. You can turn it off in the menu.

The first time you open it, it asks once whether to open by itself when you
sign in. Whatever you answer, menu option 2 changes it later.

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
under `AppData\Local` in your own user folder. It holds the dates you opened
the program in the last 60 days, your current plan, an unfinished earlier
plan, how many times you marked a plan done, and your last seven finished
plans (words and date). It also holds your settings for the days-in-a-row
message and the thought and tip, and your answer to the sign-in question.
Nothing else: no name, no computer name, no times. Older dates are dropped, so
the file is never a long record of when you worked. An empty `notes.lock` file
sits next to it and holds nothing.

It makes no network connections and reports nothing to IT or managers. Other
people who can read your computer's files, such as IT staff, could read the
file, so don't type passwords or private details.

Menu option 1 shows all of it, and whether it opens by itself at sign-in.
Option 7 forgets one finished plan, and option 4 deletes everything. After a delete the file holds only a random marker, so
another open window can't write the notes back. A damaged file is kept as
`notes.json.bak` until you delete everything. Uninstalling asks the
administrator whether to delete everyone's notes too; if not, delete the
folder yourself if you don't want it.

## For IT: install

Run these in one PowerShell window opened as administrator, each line on its own. Change the
first two lines to the release tag and the full 40-character commit hash that
was reviewed, and keep the quotes.

```powershell
$tag = 'v1.22.0'
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

Employees can then turn on a once-a-day sign-in reminder themselves. It lives
in their own Startup folder, needs no administrator rights, and the uninstaller
removes it.

The installer needs Git for Windows installed for all users and internet
access. It checks six steps and prints `[1/6]` to `[6/6]` as it goes. The
permission checks on Git can take several minutes, so let them finish. The
result line says whether this was a new install, a reinstall, or an upgrade
from an earlier version.

For an unattended run, add `-Quiet`. It prints only warnings, errors and the
result line, never asks a question, and exits 0 on success and 1 on failure.
Everything is also written to `install.log` in the setup folder, and a copy
is kept in the install folder.

### Update to a new release

An update is a fresh install of the new release. The installer upgrades in
place. Run each line on its own:

```powershell
cd \
Remove-Item -Recurse -Force $d
```

Then repeat the install steps with the new tag and commit. A fresh clone is
deliberate: it keeps the reviewed commit the only source.

### If something fails

The last line starts with `FAILED:` and says what to fix. The full record is in
`install.log` in the setup folder. A failed run leaves any working install as
it was. An upgrade that fails at step 6 (the Apps entry or the shortcut) puts
the previous install back. A first install that fails there keeps its files,
so run the installer again. If it fails when replacing the folder, it says how
many hello-world windows are open. Close them and run it again.

Each PC's Apps entry records the installed version, the commit and the
install date, and has a `QuietUninstallString` for unattended removal. This
shows what is installed:

```powershell
Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world
```

## Files

- `hello.py`: the program. `hello.cmd --help` lists its options, such as `--plain`, which prints only the greeting and saves nothing.
- `install.ps1`, `uninstall.ps1`: deploy and remove it.
- `test_hello.py`: run with `python test_hello.py` (Python 3.11 or later).
- `VERSION`: the release version; a new version on `main` gets a tag.
- `CHANGELOG.md`, `BACKLOG.md`, `reviews/`: change history, declined changes
  with reasons, and the saved review of each round.
- `PLAN.md`: the value and rollout plan.
- `TODO.md`: what a six-voice panel agreed should be done next.
- `docs/WHY-DAILY-ACTIONS.md`: why it changed from a greeting to a daily program.
- `docs/PILOT.md`: the simulated 30-day pilot and what it changed.
