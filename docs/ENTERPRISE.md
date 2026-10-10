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

A package you build with your own content also holds `content.json`, listed
in `SHA256SUMS` like the rest. See "Your own thoughts and tips" below.

The package hash is the SHA-256 of `SHA256SUMS`. `install.ps1 -PackageHash`
checks it first, then checks every file against `SHA256SUMS`, then checks the
Python zip against the pin inside the verified `install.ps1`. Nothing changes
on the PC until all of that passes.

The build is reproducible. To confirm a release, check out its commit on
Windows and run `tools\build-package.ps1 -OutDir <empty folder>`. It prints
the package hash, which must match the release notes. Record the hash in your
change ticket once the commit is reviewed, and deploy only with that hash.

## Your own thoughts and tips

An organization can replace the built-in thoughts and tips with its own, for
example lines about its values, safety habits or how teams work together.
Write a JSON file in the format of `examples\content.json`: an object with a
`"thoughts"` list and a `"tips"` list, each 7 to 200 lines of 10 to 120
characters. Then build the package with it:

    tools\build-package.ps1 -OutDir <empty folder> -ContentFile <your file>

The lines are meant to be timeless, so the rules keep the file from becoming
an announcement channel: no links or email addresses, no dates or month
names, no control characters. The build stops on a file that breaks a rule
and lists each problem. To check a file first, run
`hello.cmd --check-content <file>`, or add `--local` for the answer in the
Windows display language.

Each file keeps its name in the package, covered by `SHA256SUMS` and
the package hash, so the content is reviewed and signed off with the rest of
the release. The installer checks the file again on the PC and stops if it
breaks a rule. Your lines replace the built-in ones in every language, so
write them in the language your people read. The program shows them by date,
like the built-in lists, so everyone sees the same line on the same day.

An organization that installs from a git clone with `-Commit` commits
`content.json` at the top of its own fork instead. A `content.json` that
isn't in the commit is ignored.

You can also ship a file per language, named `content.<language>.json`,
such as `content.es.json` or `content.fr-CA.json`. A person whose language
has one sees it; a regional language falls back to its base language's file,
then to `content.json`. Pass every file to `-ContentFile`, separated by
commas.

Two more keys are optional:
- `"holidays"`: up to 100 dates such as `"2026-12-25"`. The reminder doesn't
  come on those days.
- `"title"`: 1 to 40 characters that replace "Hello, world!" at the top of
  the window and the text screen, such as your team's name. `--plain` still
  prints "Hello, world!", since scripts read it. A person who chose "Greet me
  by name" sees their own first name instead.

A package with content has its own package hash, so record that one.

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

## Installer behaviour worth knowing

- It runs on Windows 10 version 1809 or later and Windows 11, on x64, and on
  ARM64 with Windows 11. The architecture comes from the operating system,
  not from an environment variable the caller can set.
- Domain Admins and Enterprise Admins count as administrators in its
  permission checks, along with the local Administrators group and SYSTEM.
- It walks each folder it checks without going into a junction or a linked
  folder, and stops at the first link it finds.
- The all-users Start menu folder must be changeable only by administrators,
  since anyone who could change it could swap the shortcut.
- Behind an authenticating proxy, the Python download uses the
  administrator's own Windows credentials. The release package needs no
  download at all.
- `NO_COLOR` set to anything turns its colours off.
- When a file in use blocks an upgrade, the message names the hello-world
  programs that are open.
- The bundled Python leaves out the modules hello.py never loads, and SQLite,
  so fewer files are on every PC for scanners to flag. Since 1.45.0 it keeps
  OpenSSL, for the shared counts server's https.
- `install-user.ps1` installs for one person with no administrator, into
  their own profile; the README has the trade-off. Settings > Apps lists it
  for that person, and Uninstall removes it.
- `tools\reinstall.ps1 -Tag <tag> -Commit <hash>` does the git clone steps in
  one command.

CI checks the pinned Python's sigstore signature from python.org on every
change, and a weekly workflow checks that its hash still matches and fails
when a newer patch release of the same Python is out. CI also runs the
installed program as a standard user, and checks that user can't change the
install.

## Logs and events

`uninstall.ps1` turns off every user's reminder: the `hello-world` Run value
of each signed-in user, when its data runs `hello.py` or `hello.cmd` with
`--startup`, and every `hello-world reminder` scheduled task. With
`-RemoveNotes` it also deletes each profile's `AppData\Local\hello-world`
files (`notes.json` and its backups, `notes.lock`, `errors.log`), checking
that no folder on the way is a link just before each delete. The script's
help says what that check can't rule out.


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
store or locally. The `es-ES`, `fr-FR`, `fr-CA`, `pt-BR`, `pt-PT`, `de-DE`,
`zh-CN`, `ja-JP`, `ko-KR`, `ar-SA` and `he-IL` folders hold
the same templates for administrators who edit policy in those languages; copy
each to the folder of the same name. Intune can import the same ADMX as a
custom template. The
settings are under Computer or User Configuration > Administrative Templates
> hello-world, and the computer setting wins.

| Setting | Registry value (DWORD 1) | Effect |
|---|---|---|
| Turn off opening hello-world at sign-in | `DisableSignInLauncher` | Never offers it, refuses to turn it on, and removes an existing one at the next run |
| Hide the daily thought and tip | `HideThoughtAndTip` | Shows only the plan question |
| Hide the days-in-a-row message | `HideDaysInARow` | Never shows the count, and keeps only the latest visit date |
| Turn off plans | `DisablePlans` | Never asks for a plan, and keeps no plan text, finished plans or done count; text already saved is dropped at each person's next visit |
| Always show hello-world in English | `ForceEnglish` | Shows English whatever the Windows display language, and hides the language choice |
| Write usage events to the event log | `ReportUsage` | One Application event, source `hello-world`, ID 2000, for each open, plan set and plan finished. No plan text; nothing goes over a network |
| Keep an error log | `LogErrors` | `errors.log` in each person's data folder: time, version, error type and `hello.py` line numbers, under 100 KB. No plan text |
| Name backups of a damaged file by date and time | `TimestampBackups` | `notes.json.<date-time>.bak` instead of numbered backups |
| Keep at most this many backups of a damaged file | `MaxBackups` (DWORD 1 to 100) | Deletes the oldest backups beyond that number before making a new one |
| Leave a damaged file alone when nobody is at the screen | `LeaveDamagedFile` | A run with nobody at the keyboard leaves a damaged file in place for the next visit |
| Address for feedback | `FeedbackAddress` (string) | Adds Options > Send feedback..., which opens a new mail to that address in the person's own mail program |
| Show the tips for floor and shift work | `FloorTips` | The second tip list, for warehouses, factories and shifts, for everyone |
| Shared counts server | `SharedCountsServer` (string) | An https address. Each person is asked once whether to see how many people did the day's tip; a count sends only the date. Run `server/counts_server.py` behind any https front end |
| Turn off shared counts | `TurnOffSharedCounts` | Never contacts a counts server and never asks about it |
| Shift handoff on this PC | `ShiftHandoff` | Computer only. Notes for the next shift at the top of the screen, readable by everyone who signs in to the PC, locked to it in `ProgramData\hello-world`. For floor and unit PCs; check room numbers and similar with your privacy officer first |
| Handoff folder | `HandoffFolder` (string) | Computer only. A folder, such as one share per hospital unit, so every PC pointing to it shows the same notes. Notes there are plain text; the folder's permissions decide who reads them |
| Handoff hours | `HandoffHours` (DWORD 1 to 336) | Computer only. How long handoff notes show, 72 by default; 24 suits 12-hour shifts, 168 a long weekend. Notes kept until cleared stay regardless |
| Support line | `SupportLine` (string) | Up to 200 characters, such as an employee assistance number, under "If things feel heavy, someone to talk to" in the text menu and the window's Options. Never shown by itself or in reply to anything typed; nothing records that anyone looked |
| Keep notes unlocked | `UnlockedNotes` | Computer only. Saves notes as plain text as before 1.44.0, for records rules that need them readable. Otherwise notes are locked to each person's Windows account with DPAPI |
| Turn on the sign-in reminder for everyone | `TurnOnReminder` | Turns the reminder on at each person's next open unless they already answered the question; each person can still turn it off |
| Open hello-world as a text screen | `UseTextScreen` | The Start menu opens the text screen in a console, as before 1.28.0, and the sign-in launcher opens it instead of showing a notification |

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
- Running the program: `hello.cmd`, `python.exe` and `pythonw.exe` sit under Program
  Files, which the default AppLocker rules allow. For WDAC, allow
  `%ProgramFiles%\hello-world\*` by file path or the release's files by hash.
  Don't allow the Python Software Foundation publisher, because that would
  allow any Python a user brings.
- Nothing runs from user-writable folders: The sign-in launcher is a
  registry value that points at the admin-only install.
- The sign-in notification is shown by Windows PowerShell 5.1 with
  `-NoProfile -NonInteractive -EncodedCommand`, started by `pythonw.exe`. In
  Constrained Language Mode it can't load the Windows notification types, so
  the window opens at sign-in instead. Use the `UseTextScreen` policy where
  that should never happen either.

## What endpoint detection will see

- During install: PowerShell running `icacls.exe` and `cmd.exe /d /c rmdir`,
  folder renames under Program Files, a new Apps key, an all-users shortcut,
  and an Application event log source.
- When an employee turns on the sign-in reminder, a value named `hello-world`
  under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`:

  ```
  "C:\Program Files\hello-world\python\pythonw.exe" -I "C:\Program Files\hello-world\hello.py" --startup
  ```

  Allow that exact value in persistence detections. It starts the
  admin-only install, and Windows skips it once the program is removed.
- When an employee picks a reminder time instead of sign-in, a scheduled task
  named `hello-world reminder <DOMAIN>-<user>` in the task folder every user
  shares, one per person, running the same
  `pythonw.exe -I hello.py --startup` daily at 8:00, 9:00, 10:00 or 13:00,
  or at the next sign-in when the PC was off then. It needs no
  administrator, and picking sign-in or turning the reminder off removes it.
  Versions 1.23.0 to 1.27.0 wrote a `cmd.exe /d /c if exist ... hello.cmd
  --startup` value instead, which keeps working; turning the reminder off and
  on again writes the new one.
- With the reminder on, two more keys under `HKCU\Software\Classes`:
  `AppUserModelId\hello-world`, the name the notification shows, and the
  `hello-world` link handler, which runs the same `pythonw.exe` with
  `--answer "%1"` when a notification button is clicked. It accepts only
  `hello-world:done`, `hello-world:notyet` and `hello-world:open`, and the
  most a link from a web page could do is mark that person's plan done after
  the browser asks them. Turning the reminder off removes both keys; the
  uninstaller leaves them, like the Run value, and they do nothing once the
  program is gone.
- At sign-in, when there is a plan to ask about, `pythonw.exe` starts
  `powershell.exe` once to show the notification.
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

Each user's `notes.json` holds the date they last opened the program, their
current plan, one unfinished earlier plan, a count of plans marked done, the
plans they finished in the last 14 days with dates (90 with a longer
history), four settings, and the date of the last
sign-in reminder. Only someone who turns on the days-in-a-row message keeps
the dates of the last 60 days, which the message counts.
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
  - Python runs with `-I`. SQLite is removed from the bundled Python, which
    never uses it. OpenSSL stays for https to the shared counts server; with
    no server set, or with `TurnOffSharedCounts`, nothing connects.
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
| Stop the sign-in reminder | Options in the window, menu option 2 in the text screen, or the Group Policy setting. |
| Someone wants the old text screen | Options > Use the text screen in the window, or the `UseTextScreen` policy. Menu option 9 switches back. |
| The window doesn't open | `hello.cmd` still runs the text screen. A PC where the window can't be drawn gets the text screen in a console instead. |
| Remove someone's data | They choose menu option 4, or delete `%LOCALAPPDATA%\hello-world`. |
| Install logs | `%WINDIR%\Logs\hello-world`, and the Application event log, source `hello-world`. |

## Accessibility and language

The Start menu opens a window built from standard Windows controls: labels,
one text box and buttons, in the system font at 12 points, with the system's
colours so high contrast themes apply. Every button has an Alt key, Enter
saves, and Esc closes. The owner checked the window and the notification
with Narrator, NVDA, JAWS, Magnifier at 200 percent and high contrast for
1.28.0, and the translations had a native speaker review.

The text screen is for anyone who prefers typing. All its output is plain
text in one top-to-bottom flow, prompts say what Enter does, and long prompts
wrap to the window. It was checked with Narrator, NVDA and JAWS, and in
simulated pilots with screen reader, Magnifier and second-language users.
Each person can switch to it under Options, and the `UseTextScreen` policy
sets it for everyone. `docs/ACCESSIBILITY.md` has the details.

The program speaks English, Spanish, French (France and Canada), Portuguese (Brazil and Portugal), German, Simplified Chinese, Japanese, Korean, Arabic and Hebrew. It follows
the Windows display language, and shows English for any other language. Each
person can pick another one under Options. The text screen shows English for
Chinese, Japanese, Korean, Arabic and Hebrew, which older consoles can't draw;
the window shows them, Arabic and Hebrew mirrored right to left. The Canadian
French and European Portuguese follow the whole Windows language, such as
fr-CA, while other French and Portuguese PCs get the France and Brazil
texts. The `ForceEnglish` policy keeps everyone in English. The words
people type work in every language: `done`, `hecho`, `fait`, `feito` and
`erledigt` all mark a plan done, and `salir`, `quitter`, `sair` and `beenden`
all close. A PC whose language changes needs no retraining, and a help desk
can talk anyone through it with the English words. `--check-content`, which is for administrators,
answers in English, and `--plain` always prints `Hello, world!` so scripts can
rely on it.
