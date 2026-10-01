# hello-world

A small Python program that prints "Hello, world!", and the PowerShell
installer that deploys it to Windows workstations.

## What it is for

Today the program is a pilot. Its job is to prove that IT can ship a program
to employee PCs safely: a pinned source commit, a pinned and hash-checked
Python, folders only administrators can change, a tested swap with rollback,
and a clean uninstall. Employees get no benefit from the greeting itself. See
`PLAN.md` for how it becomes a tool people use.

## For employees

Open **hello-world** from the Start menu, or type "hello-world" in Windows
Search. A window shows the greeting and waits for a key. To remove it, use
Settings > Apps > Installed apps > hello-world > Uninstall. Windows asks for an
administrator password, and the prompt says "Windows PowerShell". That is
expected. If you don't have the password, ask IT.

## For IT: install

Run these in one elevated PowerShell window, each line on its own. Change the
first two lines to the release tag and the full 40-character commit hash that
was reviewed, and keep the quotes.

```powershell
$tag = 'v1.6.0'
$commit = '0123456789abcdef0123456789abcdef01234567'
$d = "$([Environment]::GetFolderPath('ProgramFiles'))\hello-setup"; New-Item -ItemType Directory $d
$icacls = "$([Environment]::SystemDirectory)\icacls.exe"; $git = (Get-ItemProperty HKLM:\SOFTWARE\GitForWindows).InstallPath + '\cmd\git.exe'
& $icacls $d /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F'
& $git clone -b $tag --depth 1 https://github.com/thrash-d/hello-world $d
cd $d; Set-ExecutionPolicy -Scope Process Bypass -Force
.\install.ps1 -Commit $commit
```

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
`install.log` in the setup folder. A failed run leaves any working install as
it was.

## Files

- `hello.py`: the program.
- `install.ps1`, `uninstall.ps1`: deploy and remove it.
- `test_hello.py`: run with `python test_hello.py`.
- `VERSION`: the release version; a new version on `main` gets a tag.
- `CHANGELOG.md`, `BACKLOG.md`, `reviews/`: change history, declined changes
  with reasons, and the saved review of each round.
- `PLAN.md`: the value and rollout plan.
