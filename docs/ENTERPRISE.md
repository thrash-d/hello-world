# Deploying hello-world to a large fleet

This guide is for the endpoint and security teams that package, deploy,
configure and approve hello-world across thousands of Windows PCs. The README
covers what employees see and the basic install steps.

## What it is, in one paragraph

A console program that greets employees with a daily thought, a tip and an
optional plan. It installs for all users under `Program Files\hello-world`
with its own pinned Python, adds an all-users Start menu shortcut and an
Apps entry, and nothing else machine-wide. At run time it makes no network
connections, runs no service, needs no admin rights and never needs a
reboot. Each user's data is one small file in their own `%LOCALAPPDATA%`.

## Requirements

- Windows 10 or 11 on x64, or Windows 11 on ARM64, which runs the bundled x64
  Python through emulation. Windows 10 on ARM64 is refused.
- Windows PowerShell 5.1, which every supported Windows version has.
- Administrator or SYSTEM to install and uninstall.
- No Git and no internet access when installing from the release package.

## The release package

Each release on GitHub has `hello-world-<version>.zip`, a CycloneDX bill of
materials (`sbom.cdx.json`), and in its notes the package hash. The zip holds:

| File | What it is |
|---|---|
| `install.ps1`, `uninstall.ps1` | The installer and uninstaller |
| `hello.py`, `VERSION` | The program and its version |
| `python-embed.zip` | The python.org embeddable Python, pinned by SHA-256 in `install.ps1` |
| `SHA256SUMS` | The SHA-256 of each file above |
| `sbom.cdx.json` | The bill of materials |

The package hash is the SHA-256 of `SHA256SUMS`. `install.ps1 -PackageHash`
checks it first, then checks every file against `SHA256SUMS`, then checks the
Python zip against the pin inside the verified `install.ps1`. Nothing changes
on the PC until all of that passes.

The build is reproducible. To confirm a release, check out its commit on
Windows and run `tools\build-package.ps1 -OutDir <empty folder>`. It prints
the package hash, which must match the release notes. Record the hash in your
change ticket once the commit is reviewed, and deploy only with that hash.

## Install, uninstall and detection

These settings work for an Intune Win32 app and for an MECM application. Wrap
the unzipped package folder as the content.

| Setting | Value |
|---|---|
| Install command | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File install.ps1 -PackageHash <package hash> -Quiet` |
| Uninstall command | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ProgramFiles%\hello-world\uninstall.ps1" -Quiet` |
| Install behavior | System |
| Reboot | Never needed |
| Return codes | `0` success, `1618` retry later, `1` failed |
| Detection | Registry `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world`, value `DisplayVersion`, version greater than or equal to the release; and the file `%ProgramFiles%\hello-world\hello.cmd` exists |

Notes:

- Intune runs commands in 32-bit PowerShell. Both scripts start themselves
  again in 64-bit PowerShell, so no `sysnative` path is needed.
- The installer refuses a package folder that non-administrators can change.
  Intune's `IMECache` and MECM's `ccmcache` pass that check.
- An open hello-world window doesn't block an upgrade. Its copy is renamed
  aside to `hello-world.old`, keeps running until it's closed, and the next
  install removes it. Upgrades on multi-session hosts don't need a drain
  window.
- `1618` means a file in the install folder was held open without delete
  sharing, usually by antivirus or a backup agent. Nothing changed, and both
  tools retry that code later by default. The uninstaller works the same
  way.
- A first install that fails leaves no Apps entry, so detection stays false
  and the tool retries.
- The installer refuses to install an older version over a newer one. Add
  `-AllowDowngrade` to the command to roll back on purpose.
- `-Publisher "<team name>"` sets the publisher shown in Settings > Apps.

Use the `QuietUninstallString` from the Apps entry, never the plain
`UninstallString`, for unattended removal.

## Logs and events

- `%WINDIR%\Logs\hello-world\install.log` and `uninstall.log`, readable by
  administrators only. One earlier install log is kept as `install.log.old`.
- Application event log, source `hello-world`:

| Event ID | Meaning |
|---|---|
| 1000 | Installed, with the version and whether it was new, a reinstall or an upgrade |
| 1001 | Install failed, with the reason |
| 1002 | Uninstalled |
| 1003 | Uninstall failed, with the reason |

The Apps entry also records `DisplayVersion`, `PackageHash` (or `Commit` for
a git install), `PythonVersion` and `InstallDate`, which inventory tools can
read.

## Central settings through Group Policy

Copy `policy\hello-world.admx` to `PolicyDefinitions`, and
`policy\en-US\hello-world.adml` to `PolicyDefinitions\en-US`, in the central
store or locally. Intune can import the same ADMX as a custom template. The
settings are under Computer or User Configuration > Administrative Templates
> hello-world, and the computer setting wins.

| Setting | Registry value (DWORD 1) | Effect |
|---|---|---|
| Turn off opening hello-world at sign-in | `DisableSignInLauncher` | Never offers it, refuses to turn it on, and removes an existing one at the next run |
| Hide the daily thought and tip | `HideThoughtAndTip` | Shows only the plan question |
| Hide the days-in-a-row message | `HideDaysInARow` | Never shows the count, and keeps only the latest visit date |
| Turn off plans | `DisablePlans` | Never asks for a plan, and keeps no plan text, finished plans or done count; text already saved is dropped at each person's next visit |

`DisablePlans` and `HideDaysInARow` together leave only the latest visit date
and the settings in each `notes.json`. Use them where typed plan text or a
history of visits would be a records, legal hold or works-council concern.

The values live under `HKLM` or `HKCU\SOFTWARE\Policies\hello-world`, where
only administrators and Group Policy can write.

## Signing, execution policy and application control

The scripts aren't signed in the repository, because signing needs your
organization's certificate.

- Execution policy: a `MachinePolicy` of AllSigned overrides
  `-ExecutionPolicy Bypass`. Build a signed package with your code-signing
  certificate:

  ```powershell
  tools\build-package.ps1 -OutDir <empty folder> -CertificateThumbprint <thumbprint> -TimestampServer <RFC 3161 URL>
  ```

  It signs `install.ps1` and `uninstall.ps1` with SHA-256 before hashing,
  checks both signatures, and prints the signed package's own hash; record
  that one. A signed package isn't reproducible from the commit alone, since
  the signature and timestamp differ each time. CI builds a signed package
  with a throwaway certificate, sets the runner to AllSigned, and checks that
  it installs and uninstalls with no `-ExecutionPolicy Bypass` while an
  unsigned one is refused.
- WDAC and AppLocker script enforcement: unsigned scripts run in
  Constrained Language Mode, where the installer fails. Sign the scripts, or
  allow them by hash.
- Running the program: `hello.cmd` and `python.exe` sit under Program
  Files, which the default AppLocker rules allow. For WDAC, allow
  `%ProgramFiles%\hello-world\*` by file path or the release's files by hash.
  Don't allow the Python Software Foundation publisher, because that would
  allow any Python a user brings.
- Nothing runs from user-writable folders: The sign-in launcher is a
  registry value that points at the admin-only install.

## What endpoint detection will see

- During install: PowerShell running `icacls.exe` and `cmd.exe /d /c rmdir`,
  folder renames under Program Files, a new Apps key, an all-users shortcut,
  and an Application event log source.
- When an employee turns on the sign-in opening, a value named `hello-world`
  under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`:

  ```
  "C:\Windows\System32\cmd.exe" /d /c if exist "C:\Program Files\hello-world\hello.cmd" start "hello-world" /d "C:\Program Files\hello-world" hello.cmd --startup
  ```

  Allow that exact value in persistence detections. It starts the
  admin-only install and does nothing once the program is removed.
- Versions before 1.23.0 used a `hello-world-daily.cmd` in the Startup folder.
  The program replaces it with the Run value the next time each person opens
  it, and the uninstaller removes any that are left.

## VDI, roaming profiles and multi-session hosts

- Notes live in `%LOCALAPPDATA%\hello-world`. FSLogix profile containers keep
  them. Classic roaming profiles don't roam `Local`, so notes stay on each
  PC. On non-persistent desktops without a profile container they're lost at
  sign-out, and the program starts fresh without errors.
- The Run value is in `HKCU`, so it roams with the profile. On a PC without
  the program it does nothing.
- On multi-session hosts every user has their own notes, saves are atomic,
  and a lock file guards each read-then-write. An upgrade works while
  sessions have the program open; their old copy is cleared by the next
  install.

## Data handling

Each user's `notes.json` holds the days they opened the program in the last
60 days, their current plan, one unfinished earlier plan, a count of plans
marked done, their last seven finished plans with dates, and three settings.
The `DisablePlans` and `HideDaysInARow` policies cut that to the latest visit
date and the settings.
It holds no names, computer names or times. It's plain text, protected by the
user's own profile permissions; administrators and backup tools can read it,
and the program tells employees so on the first day.

Employees see all of it with menu option 1 and delete it with option 4.
Uninstalling leaves each user's notes, because deleting inside user profiles
as an administrator could be redirected by a link a user controls. Use your
own profile-cleanup process if notes must go when the program does.

## Security model

- Assets: the integrity of `Program Files\hello-world` and the all-users
  shortcut, the administrator or SYSTEM context of the scripts, and each
  user's notes.
- Trust boundaries: the scripts run elevated but only read
  administrator-controlled files. The one exception is the sweep for pre-1.23
  launchers, which deletes only a plain file with an exact name, after
  checking that no folder on its path is a link.
- Controls:
  - Every installed file is checked against the package hash or the reviewed
    commit, and Python against its pinned SHA-256.
  - The setup folder and the install tree must be admin-only, with no links.
  - The new install is built beside the old one, test-run, and swapped in
    with rollback.
  - Tools run by full path, `cmd` runs with `/d`, and the Archive module loads
    from `$PSHOME`.
  - Git ignores global and system config during a clone install.
  - Python runs with `-I`. OpenSSL and SQLite are removed from the bundled
    Python, since the program uses neither.
  - User input and file contents are cleaned of control and bidi characters
    before display.
- Known limits:
  - The scripts aren't signed until you sign them.
  - The legacy launcher sweep can't rule out a race in a user's own profile;
    the worst case is deleting a file of that exact name elsewhere.
  - The bundled Python changes only with a release.

## Keeping the bundled Python patched

`install.ps1` pins one embeddable Python by URL and SHA-256, and the bill of
materials names it. When python.org publishes a security release of that
version line, update both values in `install.ps1` from the release's
`.sigstore` file. CI then downloads the zip, checks the hash and runs the
program on it, and the next release ships it. Your vulnerability scanner can
match `PythonVersion` in the Apps entry.

## Help desk

| Question | Answer |
|---|---|
| Where is the program? | `%ProgramFiles%\hello-world`. `hello.cmd --version` prints the version. |
| Where are someone's notes? | `%LOCALAPPDATA%\hello-world\notes.json`. `hello.cmd --stats` shows them. |
| It said the file was damaged | The old file is kept as `notes.json.bak` in the same folder and a fresh one started. |
| An upgrade or uninstall failed with 1618 | A file in `%ProgramFiles%\hello-world` was in use, often by antivirus. Retry later; nothing changed. |
| A `hello-world.old` folder is left | A window was open during an upgrade. The next install removes it. |
| Stop it opening at sign-in | Menu option 2, or the Group Policy setting. |
| Remove someone's data | They choose menu option 4, or delete `%LOCALAPPDATA%\hello-world`. |
| Install logs | `%WINDIR%\Logs\hello-world`, and the Application event log, source `hello-world`. |

## Accessibility and language

All output is plain text in one top-to-bottom flow, prompts say what Enter
does, and long prompts wrap to the window. It was checked with Narrator and
in simulated pilots with screen reader, Magnifier and second-language users.
A pass with NVDA or JAWS is still to do. The program is English only.
