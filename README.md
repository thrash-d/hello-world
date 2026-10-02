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
Enter to skip anything you don't want to answer. Press Enter again to close, or type `p` to set or change today's plan.

- To see the options, type `m` at the last prompt. You can see exactly what is
  saved, open hello-world once a day when you sign in, hide the "in a row"
  line, set or change today's plan (option 6), or delete everything saved
  (including any backup copy of a damaged file).
- The "in a row" line shows only on your 3rd, 7th and 14th visit in a row, and
  then every 30th. It counts a visit within three days of the last one, so
  weekends and days off don't break it. Turn it off in the options if you
  don't like it.
- To remove the program, use Settings > Apps > Installed apps > hello-world >
  Uninstall. Windows asks for an administrator password, and the prompt says
  "Windows PowerShell". That is expected. If you don't have the password, ask
  IT.

### What is saved, and who can see it

hello-world saves the dates you opened it and your current plan, in one small
file, `notes.json`, in the `hello-world` folder under `AppData\Local` in your
own user folder. It saves nothing else (apart from your in-a-row setting): no name, no computer name, no times.
It makes no network connections and sends nothing to anyone. It does not report
use to IT or to managers. Other people who can read the files on your computer,
such as IT staff, could read that file, so don't type passwords or private
details. Choose option 1 in the menu to see what is saved (the same facts, tidied; a damaged file is kept as `notes.json.bak` until you delete everything), or option 4 to
delete it. When the program is uninstalled, the file stays so you can keep it;
delete the folder if you don't want it.

## For IT: install

Run these in one PowerShell window opened as administrator, each line on its own. Change the
first two lines to the release tag and the full 40-character commit hash that
was reviewed, and keep the quotes.

```powershell
$tag = 'v1.9.0'
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
- `test_hello.py`: run with `python test_hello.py`.
- `VERSION`: the release version; a new version on `main` gets a tag.
- `CHANGELOG.md`, `BACKLOG.md`, `reviews/`: change history, declined changes
  with reasons, and the saved review of each round.
- `PLAN.md`: the value and rollout plan.
- `docs/WHY-DAILY-ACTIONS.md`: why it changed from a greeting to a daily program.
