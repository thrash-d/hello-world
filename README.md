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
Search. Read the screen, type a plan for the day if you want one, and press
Enter to skip anything you don't want to answer. At the last prompt:

- Press Enter, or type `q`, `quit` or `exit`, to close.
- Type `done` to mark today's plan finished, right when you finish it. It is
  offered only while a plan is on screen. It lists the last seven plans you
  finished, then asks for your next plan, so finishing one thing leads
  straight to the next. There, one Enter or `q` closes, and `no` or `skip`
  goes back to the last prompt.
- Type `plan` to set or change today's plan, and `same` there to reuse the
  earlier one.
- Type `menu` (or `help`, or `?`) for the options.

Typing a command word such as `menu` or `done` where a plan is asked does not
save it as the plan; it says so. `no`, `none` and `skip` just mean no plan.
Enter at the menu goes back to the last prompt, and the menu says so; Enter
there closes. If two windows are open, each change reads the saved file again
just before it saves and keeps only what that window changed. Finished plans
and the dates you opened it are merged, so one window does not undo the other. Lines wrap to
the width of the window, down to 30 columns. A word the prompt doesn't list gets a message that names it and lists the
choices, and the prompt comes back. The same goes for the yes/no questions and
the menu: a mistyped answer is named and asked again, never taken as a choice.
After `plan` or `done` the last prompt comes back below the result, so you can read it before the window closes. Everything works from the keyboard with plain text,
in a single top-to-bottom flow, designed so a screen reader reads it in order.

- To see the options, type `menu` at the last prompt (`m` also works). You can see a summary of what
  is saved (and the whole file with `full`), open hello-world once a day when you sign in, hide the "in a row"
  line, set or change today's plan (option 6), forget one finished plan
  (option 7), or delete everything saved (including any backup copy of a
  damaged file).
- The "in a row" line shows only on your 3rd, 7th and 14th visit in a row, and
  then every 30th. It counts a visit within three days of the last one, so
  weekends and days off don't break it. Turn it off in the options if you
  don't like it.
- To remove the program, use Settings > Apps > Installed apps > hello-world >
  Uninstall. Windows asks for an administrator password, and the prompt says
  "Windows PowerShell". That is expected. If you don't have the password, ask
  IT.

### What is saved, and who can see it

hello-world saves one small file, `notes.json`, in the `hello-world` folder
under `AppData\Local` in your own user folder. It holds the dates you opened
the program (the last 400), your current plan, the plan before it, how many
plans you marked done, and your last seven finished plans (words and date). It
also holds your in-a-row setting and your answer to the sign-in question. Menu
option 1 shows all of it, option 7 forgets one finished plan, and option 4
deletes everything. Uninstalling leaves the file in place. It saves nothing
else: no name, no computer name, no times.
It makes no network connections and sends nothing to anyone. It does not report
use to IT or to managers. Other people who can read the files on your computer,
such as IT staff, could read that file, so don't type passwords or private
details. Choose option 1 in the menu to see what is saved: a short summary first, and the whole file if you type `full` (the same facts, tidied; a damaged file is kept as `notes.json.bak` (or `.bak2` and so on) until you delete everything), or option 4 to
delete it. When the program is uninstalled, the file stays so you can keep it;
delete the folder if you don't want it.

- Coming back: the last seven finished plans, with their dates, are kept only in `notes.json`, listed after you finish a plan, on "Welcome back" after a week away, and in option 1. Menu option 7 forgets one, and option 4 removes them all. When you finish a plan, or it is replaced or cleared, hello-world remembers it privately. Next time the plan prompt shows it as "Earlier plan", and typing `same` reuses it, so a plan you repeat is one word, not a retype. It also counts the plans you marked done (shown only in menu option 1 and after you finish one). Clearing a plan does not erase these words: they stay as `same` until you delete everything (menu option 4). A plan you left open stays visible if you reopen the program the same day, and one older than two weeks is cleared with a message and kept as `same`.
- Finishing is counted the moment you say so: type `done` at the last prompt.
  If you do not, the next day asks "Did you do it?". A plan already marked
  done is not asked about again.
- Sign-in reminder: if you type a plan, the next day it asks how it went.
  Right after you save your first plan, and on later visits if you have not
  answered yet, it asks whether to open at sign-in (y/n). Only a clear no is
  final. Enter means "ask me later", and it stops asking after three Enters.
  A mistyped answer is named and asked again, and does not count. Option 2 in
  the menu turns it on later.
- Without a mouse or sight: every prompt is plain text and Enter alone always
  works. Ctrl+C at a prompt skips that prompt. Prompts say what Enter does where it matters, such as "Enter = keep" and "Enter = cancel". `--stats` still prints the whole saved file. Menu option 5 explains each
  option, and `hello.cmd --help` prints the folder `hello.cmd` is in. It has
  not been tried with a real screen reader yet.
- English only. A plan in another script is saved, but a console that cannot
  show it prints `?`.

## For IT: install

Run these in one PowerShell window opened as administrator, each line on its own. Change the
first two lines to the release tag and the full 40-character commit hash that
was reviewed, and keep the quotes.

```powershell
$tag = 'v1.16.0'
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
Everything is also written to `install.log` in the setup folder.

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
`install.log` in the setup folder. A failed run before the final
step leaves any working install as it was. If it fails at step 6 (the Apps entry
or the shortcut), the new files are already in place, so run the installer again.
If it fails when replacing the folder, close every open hello-world window
(they hold files open) and run it again.

## Files

- `hello.py`: the program. `hello.cmd --help` lists its options, such as `--plain`, which prints only the greeting and saves nothing.
- `install.ps1`, `uninstall.ps1`: deploy and remove it.
- `test_hello.py`: run with `python test_hello.py` (Python 3.11 or later).
- `VERSION`: the release version; a new version on `main` gets a tag.
- `CHANGELOG.md`, `BACKLOG.md`, `reviews/`: change history, declined changes
  with reasons, and the saved review of each round.
- `PLAN.md`: the value and rollout plan.
- `docs/WHY-DAILY-ACTIONS.md`: why it changed from a greeting to a daily program.
