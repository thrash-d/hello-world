<#
.SYNOPSIS
Installs hello.py for all users in a folder only administrators can change.

.DESCRIPTION
Creates "Program Files\hello-world", where only Administrators and SYSTEM can
write. Unpacks a pinned, hash-checked Python from python.org into it, copies
hello.py, uninstall.ps1 and the translations (hello.<language>.json) there,
with the organization's content.json and content.<language>.json files when
the package or commit has one, and writes hello.cmd next to them. hello.cmd
starts hello.py with that Python in isolated mode and passes its options on. Adds a hello-world shortcut,
which opens the window through pythonw.exe, to every user's Start menu, and an
entry with an Uninstall button to Settings > Apps. The workstation needs Git for Windows and internet access, but no Python
of its own. Its guarantees hold only if the employees use standard accounts. A
local administrator can change anything it protects.

Run it from an elevated PowerShell on each workstation, from a git clone of a
release tag in a folder only administrators can write. It refuses anything
else, such as an employee's Downloads folder, a clone at another commit, or a
file changed since checkout.

.PARAMETER Commit
The full commit hash that was reviewed. The clone must be at this commit.
Use this to install from a git clone.

.PARAMETER PackageHash
The package hash from the release notes: the SHA-256 of the package's
SHA256SUMS file. Use this to install from the offline release package, which
needs no Git and no internet access, for example from Intune or MECM. Every
file in the package is checked against SHA256SUMS before anything changes.
Anyone can rebuild the package from the reviewed commit with
tools\build-package.ps1 and get the same hash.

.PARAMETER AllowDowngrade
Installs a version older than the one installed. Without it, that's refused.

.PARAMETER Publisher
The name shown as the publisher in Settings > Apps. The default is
"IT Department".

.PARAMETER Quiet
Prints only warnings, the final result line, and on failure a FAILED line
with where the log is. It never asks questions, so a management tool can run
it unattended.

Exit codes: 0 when installed, 1618 when an open hello-world window blocked
the upgrade (Intune and MECM retry that code later), and 1 for any other
failure. Everything is written to %WINDIR%\Logs\hello-world\install.log, which
only administrators can read, and success and failure go to the Application
event log under the source hello-world.

.EXAMPLE
$tag = 'v1.49.0'
$commit = '0123456789abcdef0123456789abcdef01234567'
$d = "$([Environment]::GetFolderPath('ProgramFiles'))\hello-setup"
New-Item -ItemType Directory $d
$icacls = "$([Environment]::SystemDirectory)\icacls.exe"
$git = (Get-ItemProperty HKLM:\SOFTWARE\GitForWindows).InstallPath + '\cmd\git.exe'
& $icacls $d /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F'
& $git clone -b $tag --depth 1 https://github.com/thrash-d/hello-world $d
cd $d; Set-ExecutionPolicy -Scope Process Bypass -Force
.\install.ps1 -Commit $commit

Run each line on its own, in order, in one elevated window. Long lines wrap
when copied from a terminal and break the paste. Change the first two lines to
the release tag and the full 40-character commit hash that was reviewed, and
keep the quotes. The README has the same steps.

Locks the setup folder before cloning into it, so nobody else can add files
to the clone, then installs the reviewed commit. Pass the full commit hash,
never a tag name. The tools run by full path for the same reason the
installer pins them. Windows clients block scripts by default, so the
example allows them for this PowerShell window only. If a Group Policy sets
the execution policy, that line errors and the policy decides.
To install again, delete the setup folder first, so the example's New-Item and
clone work a second time. Run each line on its own, in the same window as the
example (in a new window, type the folder's path in place of $d):
cd \
Remove-Item -Recurse -Force $d
The cd is needed because Windows won't delete a window's current folder, and
-Force because git leaves read-only files in .git.
The installer upgrades an existing install in place.

.NOTES
Permission checks on Git for Windows can take several minutes - let them finish even
if the window appears idle. The installer verifies that only administrators can modify
Git's installation and config folders in C:\Program Files and C:\ProgramData\Git.

Employees open hello-world from the Start menu or by typing "hello-world" in Windows Search.
To uninstall, use Settings > Apps > Installed apps > hello-world > Uninstall.
That also removes folders named .new and .old left by an interrupted run.

The setup folder can be deleted after a successful install. The log is in
%WINDIR%\Logs\hello-world.
#>
#Requires -RunAsAdministrator
[CmdletBinding(DefaultParameterSetName = 'Clone')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Clone')][ValidatePattern('^[0-9a-f]{40}$')][string]$Commit,
    [Parameter(Mandatory, ParameterSetName = 'Package')][ValidatePattern('^[0-9a-fA-F]{64}$')][string]$PackageHash,
    [switch]$Quiet,
    [switch]$AllowDowngrade,
    [ValidateLength(1, 100)][string]$Publisher = 'IT Department'
)
$packageMode = $PSCmdlet.ParameterSetName -eq 'Package'
$ErrorActionPreference = 'Stop'
# The admin runs this in their own window and keeps using it afterward, for a
# reinstall's git clone among other things. Save what this script changes in
# the window's process, and put it back on every way out: the trap below and
# the last finally.
$savedEnv = @{}
foreach ($name in @('HOME', 'XDG_CONFIG_HOME', 'GIT_CONFIG_NOSYSTEM') + @(Get-ChildItem Env: | Where-Object Name -like 'GIT_*' | ForEach-Object Name)) {
    $savedEnv[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}
$savedTls = [Net.ServicePointManager]::SecurityProtocol
function Restore-Window {
    # A $null value removes the variable, so one that didn't exist stays gone.
    foreach ($name in @(Get-ChildItem Env: | Where-Object Name -like 'GIT_*' | ForEach-Object Name) + @($savedEnv.Keys)) {
        [Environment]::SetEnvironmentVariable($name, $savedEnv[$name], 'Process')
    }
    [Net.ServicePointManager]::SecurityProtocol = $savedTls
}
# A failure before the log starts prints one plain line, not PowerShell's error
# block with its line numbers. A failure after that is reported by the catch below.
trap { if ($env:NO_COLOR) { Write-Host "FAILED: $($_.Exception.Message)" } else { Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red }; Restore-Window; exit 1 }
# Progress lines for the person running this. -Quiet hides them; the log keeps them.
function Write-Color([string]$Text, [string]$Color) {
    # https://no-color.org: any value of NO_COLOR turns colour off.
    if ($env:NO_COLOR) { Write-Host $Text } else { Write-Host $Text -ForegroundColor $Color }
}
function Write-Step([string]$Text) { if (-not $Quiet) { Write-Color $Text Cyan } }
function Write-Info([string]$Text) { if (-not $Quiet) { Write-Host $Text } }
# A 32-bit PowerShell sees Program Files (x86) and the 32-bit registry.
# Intune runs install commands in one, so start again in the 64-bit one.
if (-not [Environment]::Is64BitProcess) {
    $native = Join-Path ([Environment]::GetFolderPath('Windows')) 'sysnative\WindowsPowerShell\v1.0\powershell.exe'
    if (-not (Test-Path -LiteralPath $native)) { throw 'Run this from 64-bit PowerShell.' }
    $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath)
    foreach ($name in $PSBoundParameters.Keys) {
        $value = $PSBoundParameters[$name]
        if ($value -is [switch]) { if ($value) { $argList += "-$name" } }
        else { $argList += "-$name"; $argList += "$value" }
    }
    & $native @argList
    exit $LASTEXITCODE
}
# The pinned Python is the amd64 build. Windows 11 on ARM64 runs it through
# x64 emulation; Windows 10 on ARM64 can't.
# The operating system's own answer; PROCESSOR_ARCHITECTURE is an environment
# variable the caller can set. .NET before 4.7.1 lacks it, so fall back.
try { $arch = "$([Runtime.InteropServices.RuntimeInformation]::OSArchitecture)".ToUpper() } catch { $arch = '' }
if (-not $arch) { $arch = $env:PROCESSOR_ARCHITECTURE }
if ($arch -eq 'X64') { $arch = 'AMD64' }
$build = [Environment]::OSVersion.Version.Build
# The window needs Windows 10 1809 or later for per-monitor scaling and
# notifications with buttons.
if ($build -lt 17763) { throw "This needs Windows 10 version 1809 or later, or Windows 11. This PC is build $build." }
if ($arch -eq 'ARM64') {
    if ($build -lt 22000) { throw 'This needs Windows 11 on an ARM64 PC, to run the x64 Python it ships.' }
}
elseif ($arch -ne 'AMD64') { throw "Need an x64 or ARM64 PC, found $arch." }
# Ask Windows for the folders; the admin's own session can carry other values.
$pf = [Environment]::GetFolderPath('ProgramFiles')
$winDir = [Environment]::GetFolderPath('Windows')
$sys32 = [Environment]::SystemDirectory
$dir = Join-Path $pf 'hello-world'
$key = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world'

# The Python hello.py runs on. To update it, change both values. The hash is
# the SHA-256 recorded in the .sigstore file python.org publishes next to the zip.
$pyUrl = 'https://www.python.org/ftp/python/3.14.8/python-3.14.8-embed-amd64.zip'
$pySha256 = 'A93ABE456AB01BD96D7A085B3CDB6566B3063F4241360D114142FBDB07F0A310'

# Rights that let someone swap a file or folder out: Delete, DeleteChild,
# WRITE_DAC, WRITE_OWNER, GENERIC_ALL. Editing a file adds WriteData,
# AppendData, and GENERIC_WRITE.
$swap = 0x10000 -bor 0x40 -bor 0x40000 -bor 0x80000 -bor 0x10000000
$edit = $swap -bor 0x2 -bor 0x4 -bor 0x40000000
# Administrators, SYSTEM, TrustedInstaller, and the admin running this.
$trusted = 'S-1-5-32-544', 'S-1-5-18', 'S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464',
    [Security.Principal.WindowsIdentity]::GetCurrent().User.Value

function SID-ToName([string]$SID) {
    $names = @{
        'S-1-5-32-544' = 'Administrators'
        'S-1-5-18' = 'SYSTEM'
        'S-1-5-32-545' = 'Users'
        'S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464' = 'TrustedInstaller'
    }
    if ($names.ContainsKey($SID)) { return $names[$SID] }
    try {
        $ntAccount = [Security.Principal.SecurityIdentifier]::new($SID).Translate([Security.Principal.NTAccount])
        return $ntAccount.Value
    } catch {
        return $SID
    }
}

function Assert-AdminOnly([string]$Path, [int64]$Rights) {
    # Verify that only administrators can modify this file/folder.
    # Use -LiteralPath because Git ships files with unusual names like "[.exe".
    $acl = Get-Acl -LiteralPath $Path
    $sid = [Security.Principal.SecurityIdentifier]

    # Collect non-admin principals with dangerous rights:
    # - The owner (owner can always rewrite the DACL, so non-admin owner is a problem)
    # - Any Allow ACE (not InheritOnly) that grants the specified Rights to non-admins
    # InheritOnly entries don't apply directly; they only affect children
    $owner = $acl.GetOwner($sid).Value
    $aceRules = $acl.GetAccessRules($true, $true, $sid) |
        Where-Object { $_.AccessControlType -eq 'Allow' -and
            -not $_.PropagationFlags.HasFlag([Security.AccessControl.PropagationFlags]::InheritOnly) -and
            ([int64]$_.FileSystemRights -band $Rights) } |
        ForEach-Object { $_.IdentityReference.Value }

    # Domain Admins (-512) and Enterprise Admins (-519) of any domain are
    # administrators too.
    $others = @($owner) + @($aceRules) | Where-Object { $_ -notin $trusted -and $_ -notmatch '^S-1-5-21-[\d-]+-(512|519)$' } | Select-Object -Unique
    if ($others) {
        $names = @($others | ForEach-Object { SID-ToName $_ })
        throw "Non-administrators can change $Path ($($names -join ', ')). Restrict write access to administrators only."
    }
}

# Everything this installer runs as admin comes from a folder tree: Git, the
# clone, and the installed Python. Nobody but administrators may change
# anything in the tree, and nobody may swap out a folder above it.
function Assert-AdminOnlyTree([string]$Root) {
    Write-Info "Checking permissions under $Root (this can take several minutes on Git for Windows)"
    $checked = 0
    # A stack, not Get-ChildItem -Recurse, so a link is reported before
    # anything behind it is listed.
    $pending = [Collections.Generic.Stack[object]]::new()
    $pending.Push((Get-Item -LiteralPath $Root -Force))
    while ($pending.Count) {
        $i = $pending.Pop()
        if (($i.Attributes -band [IO.FileAttributes]::Directory) -and -not ($i.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            foreach ($child in @(Get-ChildItem -LiteralPath $i.FullName -Force)) { $pending.Push($child) }
        }
        $checked++
        if (-not $Quiet -and $checked % 200 -eq 0) { Write-Progress -Activity "Checking permissions under $Root" -Status "$checked items checked so far" }
        # A link's own ACL says nothing about its target. Reject both symlinks and junctions.
        if ($i.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            $type = if ($i.Attributes -band [IO.FileAttributes]::Directory) { 'junction' } else { 'symlink' }
            throw "$($i.FullName) is a $type (reparse point). Only administrators can create these, but they could allow bypass of permission checks."
        }
        Assert-AdminOnly $i.FullName $edit
    }
    Write-Progress -Activity "Checking permissions under $Root" -Completed
    Write-Info "Checked $checked items in $Root - all admin-only"
    # Check that parent folders can only be modified by admins. If a parent is writable by
    # non-admins, they could move or delete the entire $Root tree. At the drive root,
    # Delete permission doesn't matter (can't delete a drive root), so we exclude it.
    for ($p = (Get-Item -LiteralPath $Root -Force).Parent; $p; $p = $p.Parent) {
        $checkRights = if ($p.Parent) { $swap } else { $swap -band -bnot 0x10000 }
        Assert-AdminOnly $p.FullName $checkRights
    }
    Write-Info "Checked parent folders of $Root up to drive root - all parent directories are admin-only"
}

# Assert-NotLink and Remove-Tree duplicated in uninstall.ps1; change both together.
function Assert-NotLink([string]$Path) {
    if ((Get-Item -LiteralPath $Path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "$Path is a link." }
}

# cmd's rmdir removes a link inside the tree without following it.
function Remove-Tree([string]$Path) {
    Assert-NotLink $Path
    & (Join-Path $sys32 'cmd.exe') /d /c rmdir /s /q "`"$Path`""
    # rmdir can report success after failing on a locked file, so check the folder is gone.
    if ($LASTEXITCODE -or (Test-Path -LiteralPath $Path)) { throw "Couldn't remove $Path" }
}

# Antivirus scans and a running hello.cmd can hold a file open for a moment,
# and Windows won't rename a folder with an open file in it.
function Rename-Retry([string]$Path, [string]$NewName) {
    for ($try = 1; ; $try++) {
        try { Rename-Item -LiteralPath $Path -NewName $NewName; return }
        catch {
            if ($try -lt 5) { Start-Sleep -Seconds 1; continue }
            # A running hello-world window doesn't block a rename, but a file
            # held open without delete sharing does: antivirus, a backup
            # agent, or another program. That passes, so the exit code asks
            # the deployment tool to retry later.
            $script:busy = $true
            $open = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path -like "$dir\*" })
            $names = ($open | ForEach-Object { "$($_.ProcessName) (process $($_.Id))" }) -join ', '
            $hint = if ($open) { " These hello-world programs are open: $names. Closing them may help." } else { '' }
            throw "Couldn't rename $Path because a file in it is in use.$hint Try again later."
        }
    }
}

# Install results go to the Application event log, so a SIEM or a fleet
# report sees them without collecting log files.
function Write-AppEvent([int]$Id, [string]$Type, [string]$Message) {
    try {
        if (-not [Diagnostics.EventLog]::SourceExists('hello-world')) { New-EventLog -LogName Application -Source 'hello-world' }
        Write-EventLog -LogName Application -Source 'hello-world' -EventId $Id -EntryType $Type -Message $Message
    }
    catch { Write-Warning "Couldn't write to the event log: $($_.Exception.Message)" }
}

# === RECOVERY: Handle interrupted installations ===
# An interrupted swap leaves the old install as the only good copy. Restore it
# before any check or download that could fail and leave the PC without one.
$new = "$dir.new"
$old = "$dir.old"
if (-not (Test-Path -LiteralPath $dir) -and (Test-Path -LiteralPath $old)) {
    if (Test-Path -LiteralPath (Join-Path $old 'hello.cmd')) {
        Assert-NotLink $old
        Rename-Retry $old (Split-Path $dir -Leaf)
        if (-not (Test-Path -LiteralPath (Join-Path $dir 'hello.cmd'))) { Write-Warning "$dir has no hello.cmd after the restore." }
    }
    else { Write-Warning "$old has no hello.cmd, so it isn't restored. This run installs fresh." }
}

# === VERIFICATION: Validate the setup environment ===
# PATH can list folders employees can write, and a git or icacls found there
# would run as admin. Call both by full path.
$icacls = Join-Path $sys32 'icacls.exe'
if ($packageMode) { Write-Step '[1/6] Installing from the release package, so Git is not needed' }
else {
Write-Step '[1/6] Checking Git for Windows and its folders'
$gitDir = (Get-ItemProperty HKLM:\SOFTWARE\GitForWindows -ErrorAction SilentlyContinue).InstallPath
$git = "$gitDir\cmd\git.exe"
if (-not $git.StartsWith("$pf\", [StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $git)) {
    throw "Git for Windows is not installed in $pf. Install 'Git for Windows' for all users (not just current user) from https://git-scm.com/download/win. Found: '$git'"
}
try { Assert-AdminOnlyTree $gitDir }
catch { throw "Non-admin write access in Git for Windows ($gitDir). Reinstall Git for Windows for all users (not just current user). Error: $_" }
# Git for Windows also reads its system config from here.
$gitData = Join-Path ([Environment]::GetFolderPath('CommonApplicationData')) 'Git'
if (Test-Path -LiteralPath $gitData) {
    try { Assert-AdminOnlyTree $gitData }
    catch { throw "Non-admin write access in $gitData (shared Git for Windows config). Ensure only administrators can modify this folder, for example: icacls `"$gitData`" /inheritance:r /grant:r *S-1-5-32-544:(OI)(CI)F *S-1-5-18:(OI)(CI)F *S-1-5-32-545:(OI)(CI)RX" }
}
}
# Covers .git too, so nobody can plant git objects that fool the commit check.
Write-Step '[2/6] Checking the setup folder'
Assert-AdminOnlyTree $PSScriptRoot

# A record of the steps from here on; the checks above print to the console
# only. It goes to a fixed folder only administrators can read, so deleting
# the setup folder or a deployment tool's cache doesn't lose it. Stopped in
# the last finally below.
$logDir = Join-Path $winDir 'Logs\hello-world'
if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory $logDir | Out-Null }
Assert-NotLink $logDir
& $icacls $logDir /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' | Out-Null
if ($LASTEXITCODE) { throw "icacls failed on $logDir" }
$log = Join-Path $logDir 'install.log'
# One earlier log is kept, so the file can't grow without limit.
if ((Test-Path -LiteralPath $log) -and (Get-Item -LiteralPath $log).Length -gt 1MB) { Move-Item -LiteralPath $log -Destination "$log.old" -Force }
try { Start-Transcript -LiteralPath $log -Append | Out-Null }
catch { throw "Couldn't start the install log (is a transcript already running in this window?): $_" }
Write-Info "Logging to $log"
try {

# The admin's own session can carry GIT_DIR and friends that point git elsewhere, and
# HOME/XDG_CONFIG_HOME can point to employee-writable locations. Clear them. Git then
# falls back to the admin's profile for ~/.gitconfig, which is admin-only unless the
# profile is redirected. Done inside this try, so the finally puts them back even
# after Ctrl+C, which the trap above doesn't catch.
Get-ChildItem Env: | Where-Object Name -like 'GIT_*' | ForEach-Object { Remove-Item -LiteralPath "Env:$($_.Name)" }
Remove-Item -LiteralPath 'Env:HOME' -ErrorAction SilentlyContinue
Remove-Item -LiteralPath 'Env:XDG_CONFIG_HOME' -ErrorAction SilentlyContinue
# Set GIT_CONFIG_NOSYSTEM to prevent git from reading /etc/gitconfig (equivalent on Windows)
$env:GIT_CONFIG_NOSYSTEM = '1'
# The admin's home can be a redirected share. A global config or attributes
# file there could make hash-object run a filter program as admin.
$env:GIT_CONFIG_GLOBAL = 'NUL'
$env:GIT_ATTR_NOSYSTEM = '1'

$required = 'install.ps1', 'uninstall.ps1', 'hello.py', 'VERSION'
# The organization's thoughts and tips, installed only when the package or
# the commit carries them, and checked like every other file.
$extra = @()
if ($packageMode) {
Write-Step '[3/6] Verifying the package against its hash'
# The package hash vouches for SHA256SUMS, and SHA256SUMS for every file.
$sumsFile = Join-Path $PSScriptRoot 'SHA256SUMS'
if (-not (Test-Path -LiteralPath $sumsFile -PathType Leaf)) { throw "$PSScriptRoot has no SHA256SUMS. Unzip the whole release package into this folder." }
if ((Get-FileHash -LiteralPath $sumsFile).Hash -ne $PackageHash) { throw "SHA256SUMS doesn't match -PackageHash. Use the package hash from the release you reviewed, and an unchanged package." }
$listed = @{}
foreach ($line in Get-Content -LiteralPath $sumsFile) {
    if ($line -match '^([0-9a-f]{64})  ([A-Za-z0-9._-]+)$') { $listed[$Matches[2]] = $Matches[1] }
    elseif ($line) { throw "SHA256SUMS has a line it can't read: $line" }
}
# The translations and the organization's content files.
$extra = @($listed.Keys | Where-Object { $_ -match '^(content(\.[A-Za-z-]+)?|hello\.[A-Za-z-]+)\.json$' } | Sort-Object)
foreach ($f in $required + 'python-embed.zip' + $extra) {
    if (-not $listed.ContainsKey($f)) { throw "SHA256SUMS doesn't list $f." }
    $path = Join-Path $PSScriptRoot $f
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-FileHash -LiteralPath $path).Hash -ne $listed[$f]) {
        throw "$f is missing or doesn't match SHA256SUMS. Use an unchanged copy of the release package."
    }
}
}
else {
# === COMMIT VERIFICATION: Ensure the clone is at the reviewed commit ===
Write-Step '[3/6] Verifying the reviewed commit'
# The ACL checks show nobody else can change the clone. This shows the clone is
# the reviewed commit, so a moved tag or an edited file fails here.
# git also finds a repository in a parent folder, so require .git here.
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot '.git') -PathType Container)) { throw "$PSScriptRoot is not the top of a git clone (.git must be a folder)." }
$head = & $git -C $PSScriptRoot rev-parse HEAD
if ($LASTEXITCODE) { throw "git rev-parse failed with exit $LASTEXITCODE in $PSScriptRoot. If the message above mentions 'dubious ownership', a different account made this clone." }
if ($head -ne $Commit) { throw "Source is at '$head', not the reviewed commit $Commit." }
# A file that isn't in the commit is ignored, like any other file.
$tracked = & $git -C $PSScriptRoot ls-tree --name-only HEAD
if ($LASTEXITCODE) { throw "git ls-tree failed with exit $LASTEXITCODE in $PSScriptRoot." }
$extra = @($tracked | Where-Object { $_ -match '^(content(\.[A-Za-z-]+)?|hello\.[A-Za-z-]+)\.json$' } | Sort-Object)
foreach ($f in $required + $extra) {
    $actual = & $git -C $PSScriptRoot hash-object --no-filters $f
    $actualOk = $LASTEXITCODE -eq 0
    $expected = & $git -C $PSScriptRoot rev-parse "HEAD:$f"
    # Both commands failing and printing nothing must not read as a match.
    if (-not $actualOk -or $LASTEXITCODE -or "$actual" -notmatch '^[0-9a-f]{40}$' -or "$actual" -ne "$expected") {
        throw "$f differs from commit $Commit. Do not modify files in the clone. Re-clone from the reviewed release tag to reinstall."
    }
}
}

# An older version is refused unless asked for, so a stale package or an old
# deployment assignment can't quietly roll PCs back.
$version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'VERSION')).Trim()
$perUser = @(Get-ChildItem 'Registry::HKEY_USERS' -ErrorAction SilentlyContinue | ForEach-Object {
    Get-ItemProperty -LiteralPath "Registry::$($_.Name)\Software\Microsoft\Windows\CurrentVersion\Uninstall\hello-world" -ErrorAction SilentlyContinue })
if ($perUser) { Write-Warning "$($perUser.Count) signed-in user(s) also have a per-user install. Each can remove theirs in Settings > Apps." }
$installedVersion = (Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue).DisplayVersion
if ($installedVersion -and -not $AllowDowngrade) {
    try { $older = [version]$version -lt [version]$installedVersion } catch { $older = $false }
    if ($older) { throw "$installedVersion is installed, which is newer than $version. Add -AllowDowngrade to install the older version." }
}

# === DOWNLOAD AND BUILD: Fetch Python, build, and test in isolation ===
$zip = Join-Path $PSScriptRoot 'python-embed.zip'
$ProgressPreference = 'SilentlyContinue'
try {
    if ($packageMode) { Write-Step '[4/6] Checking the bundled Python against the pinned hash' }
    else {
        Write-Step '[4/6] Downloading Python and verifying its hash'
        # Download into the clone, which only administrators can change, and
        # check the hash before the old install is touched. Deleted afterward.
        Write-Info "Downloading $pyUrl"
        # Windows PowerShell 5.1 can default to TLS versions python.org refuses,
        # and its progress bar slows downloads to a crawl.
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        # An authenticating proxy gets the admin's own Windows credentials.
        if ([Net.WebRequest]::DefaultWebProxy) { [Net.WebRequest]::DefaultWebProxy.Credentials = [Net.CredentialCache]::DefaultNetworkCredentials }
        for ($try = 1; ; $try++) {
            try { Invoke-WebRequest $pyUrl -OutFile $zip -UseBasicParsing -TimeoutSec 300; break }
            catch { if ($try -ge 3) { throw }; Write-Warning "Download failed ($_). Trying again."; Start-Sleep -Seconds 5 }
        }
    }
    if ((Get-FileHash -LiteralPath $zip).Hash -ne $pySha256) { throw "The Python zip doesn't match the pinned SHA-256." }

    # Build and test the new install beside the old one, so a failure leaves
    # the working install alone. Both sit in Program Files, which only
    # administrators can write to.
    Write-Step '[5/6] Building, testing and installing'
    foreach ($leftover in $new, $old, "$dir.failed") { if (Test-Path -LiteralPath $leftover) { Remove-Tree $leftover } }
    New-Item -ItemType Directory $new | Out-Null
    # Drop inherited entries. Administrators and SYSTEM get full control, Users
    # get read and run. Files created below inherit this.
    & $icacls $new /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX' | Out-Null
    if ($LASTEXITCODE) { throw "icacls failed on $new" }

    # By full path: an autoloaded module could come from a folder the admin's
    # own profile puts first.
    Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Archive\Microsoft.PowerShell.Archive.psd1')
    Expand-Archive -LiteralPath $zip -DestinationPath (Join-Path $new 'python')
    # hello.py doesn't use SQLite, and vulnerability scanners flag every PC
    # that carries a build of it. OpenSSL stays, for the shared counts
    # server's https (1.45.0); Python updates bring its fixes.
    # The rest are modules hello.py never loads; CI runs the trimmed copy.
    foreach ($pattern in '_sqlite3.pyd', 'sqlite3.dll',
            '_lzma.pyd', '_bz2.pyd', '_elementtree.pyd', 'pyexpat.pyd', 'winsound.pyd', '_multiprocessing.pyd',
            '_overlapped.pyd', '_asyncio.pyd', '_zoneinfo.pyd', '_decimal.pyd', '_test*.pyd', 'xxlimited*.pyd') {
        Get-ChildItem -LiteralPath (Join-Path $new 'python') -Filter $pattern -Force | Remove-Item -Force
    }
    foreach ($f in @('hello.py', 'uninstall.ps1') + $extra) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $f) -Destination $new }
    # -I ignores PYTHON* variables and the user's site-packages, so nothing the
    # employee controls loads into the run.
    Set-Content -LiteralPath (Join-Path $new 'hello.cmd') -Value '@"%~dp0python\python.exe" -I "%~dp0hello.py" %*' -Encoding ascii
    # hello for WSL and Git Bash (Priyanka), with Unix line ends.
    $shim = @(
        '#!/usr/bin/env bash',
        '# hello-world from WSL or Git Bash: runs hello.cmd, so it reads the same notes.',
        'd=$(cd "$(dirname "$0")" && pwd)',
        'if command -v wslpath >/dev/null 2>&1; then',
        '  a=()',
        '  for x in "$@"; do if [ -e "$x" ]; then a+=("$(wslpath -w "$x")"); else a+=("$x"); fi; done',
        '  # The folder you are in, for hello standup --git; cmd.exe starts from C:.',
        '  HELLO_CWD=$(wslpath -w "$PWD" 2>/dev/null) && export HELLO_CWD WSLENV="HELLO_CWD${WSLENV:+:$WSLENV}"',
        '  cd /mnt/c 2>/dev/null',
        '  exec cmd.exe /d /c "$(wslpath -w "$d/hello.cmd")" --utf8 "${a[@]}"',
        'fi',
        'exec "$d/hello.cmd" --utf8 "$@"'
    )
    [IO.File]::WriteAllText((Join-Path $new 'hello'), ($shim -join "`n") + "`n")

    $hash = (Get-FileHash -LiteralPath (Join-Path $new 'hello.py')).Hash
    foreach ($f in @('hello.py', 'uninstall.ps1') + $extra) {
        if ((Get-FileHash -LiteralPath (Join-Path $new $f)).Hash -ne (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $f)).Hash) { throw "Installed $f differs from the source" }
    }

    # Check the tree before running anything from it as admin.
    Assert-AdminOnlyTree $new
    foreach ($f in $new, (Join-Path $new 'hello.py'), (Join-Path $new 'hello.cmd'), (Join-Path $new 'python\python.exe'), (Join-Path $new 'python\pythonw.exe')) {
        $usersRX = (Get-Acl -LiteralPath $f).GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]) | Where-Object {
            $_.IdentityReference.Value -eq 'S-1-5-32-545' -and $_.FileSystemRights.HasFlag([Security.AccessControl.FileSystemRights]::ReadAndExecute) }
        if (-not $usersRX) { throw "Users can't read and run $f" }
    }
    # --plain prints only the greeting and saves nothing, so the test leaves no notes in the admin's profile.
    # /d skips cmd AutoRun commands from the registry.
    $out = & (Join-Path $sys32 'cmd.exe') /d /c "`"$(Join-Path $new 'hello.cmd')`" --plain"
    if ($LASTEXITCODE -or "$out" -ne 'Hello, world!') { throw "Test run failed with exit $LASTEXITCODE`: $out" }
    # hello.py would quietly fall back to its own lists, so a bad file stops
    # the install instead.
    foreach ($content in @($extra | Where-Object { $_ -like 'content*.json' })) {
        $out = & (Join-Path $sys32 'cmd.exe') /d /c "`"$(Join-Path $new 'hello.cmd')`" --check-content `"$(Join-Path $new $content)`""
        if ($LASTEXITCODE) { throw "$content breaks these rules:`n$($out -join "`n")" }
        Write-Info "Organization content: $out"
    }

    # Swap in the new folder, and put the old one back if that fails.
    $hadOld = Test-Path -LiteralPath $dir
    # Kept so a failed step 6 can put the old Apps entry back.
    $prevEntry = Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue
    $prevVersion = $prevEntry.DisplayVersion
    # Only administrators can plant a link here, but never delete through one.
    if ($hadOld) { Assert-NotLink $dir }
    if ($hadOld) { Rename-Retry $dir (Split-Path $old -Leaf) }
    try { Rename-Retry $new (Split-Path $dir -Leaf) }
    catch {
        if ($hadOld) { Rename-Retry $old (Split-Path $dir -Leaf) }
        throw
    }
    # The old install stays as .old until step 6 has worked, so a failure
    # there can put it back.
}
finally {
    # A package's zip is part of the package, so only a download is deleted.
    if (-not $packageMode) { Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue }
    if (Test-Path -LiteralPath $new) { try { Remove-Tree $new } catch { Write-Warning "Couldn't remove $new. The next run clears it." } }
}

# === FINALIZATION: Register the installation in Windows settings and Start menu ===
# The shift handoff's notes belong to the PC, not to one person, so every
# user of it can write them. Made even while the policy is off, so turning
# it on needs no reinstall. Nothing is in it until someone leaves a note.
$shared = Join-Path ([Environment]::GetFolderPath('CommonApplicationData')) 'hello-world'
if (-not (Test-Path -LiteralPath $shared)) { New-Item -ItemType Directory -Path $shared | Out-Null }
& $icacls $shared /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)M' | Out-Null
if ($LASTEXITCODE) { throw "icacls failed on $shared" }

Write-Step '[6/6] Adding the Start menu shortcut and the Settings > Apps entry'
# Added only after the checks pass. The entry in Settings > Apps, whose Uninstall button runs uninstall.ps1.
$pyExe = Join-Path $dir 'python\python.exe'
$lnk = Join-Path ([Environment]::GetFolderPath('CommonPrograms')) 'hello-world.lnk'
# Saving the shortcut overwrites the old install's one, so keep a copy for a
# rollback. Set before anything here can fail, and any copy left by an earlier
# run is cleared first. The setup folder is admin-only, like the Start menu folder.
$lnkBackup = Join-Path $PSScriptRoot 'hello-world.lnk.bak'
Remove-Item -LiteralPath $lnkBackup -Force -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath $lnk) { Copy-Item -LiteralPath $lnk -Destination $lnkBackup -Force }
try {
New-Item $key -Force | Out-Null
$uninstall = "`"$(Join-Path $sys32 'WindowsPowerShell\v1.0\powershell.exe')`" -NoProfile -ExecutionPolicy Bypass -File `"$dir\uninstall.ps1`""
# Commit and InstallDate let an admin read what code is on a PC remotely.
$entry = @{
    DisplayName          = 'hello-world'
    DisplayVersion       = $version
    Publisher            = $Publisher
    DisplayIcon          = "$pyExe,0"
    InstallLocation      = $dir
    InstallDate          = (Get-Date -Format 'yyyyMMdd')
    PythonVersion        = [regex]::Match($pyUrl, 'python-([0-9.]+)-embed').Groups[1].Value
    UninstallString      = $uninstall
    QuietUninstallString = "$uninstall -Quiet"
}
if ($packageMode) { $entry.PackageHash = $PackageHash.ToLower() } else { $entry.Commit = $Commit }
foreach ($name in $entry.Keys) { New-ItemProperty $key -Name $name -Value $entry[$name] -Force | Out-Null }
# Settings > Apps shows the size in KB.
$sizeKB = [int]((Get-ChildItem -LiteralPath $dir -Recurse -File -Force | Measure-Object Length -Sum).Sum / 1KB)
$dwords = @{ NoModify = 1; NoRepair = 1; EstimatedSize = $sizeKB }
foreach ($name in $dwords.Keys) { New-ItemProperty $key -Name $name -Value $dwords[$name] -PropertyType DWord -Force | Out-Null }

# Added only after the checks pass, so a failed install never shows up in the
# Start menu, and after the Apps entry, so a half-finished install still has
# an Uninstall button. pythonw.exe opens no console: hello.py shows its window,
# or opens the text screens in a console when the person or a policy chose them.
# Someone who could change the folder could swap the shortcut for their own.
Assert-AdminOnly (Split-Path $lnk) $swap
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$shortcut.TargetPath = Join-Path $dir 'python\pythonw.exe'
$shortcut.Arguments = "-I `"$dir\hello.py`" --window"
$shortcut.Description = 'A daily thought and one small thing to try'
$shortcut.IconLocation = "$pyExe,0"
# Not $dir: a window left open there is a current directory, and Windows won't
# rename or delete a folder that one is in.
$shortcut.WorkingDirectory = $winDir
$shortcut.Save()

# Every employee opens this shortcut, so only administrators may change it.
# A shortcut that fails the check is removed, not left in every Start menu.
try { Assert-AdminOnly $lnk $edit }
catch { Remove-Item -LiteralPath $lnk -Force -ErrorAction SilentlyContinue; throw }
}
catch {
    # An upgrade that fails here puts the old install, its shortcut and its
    # Apps entry back, so the PC keeps a working install. A first install
    # keeps its new files, and running the installer again finishes it.
    $stepError = $_
    if ($hadOld -and (Test-Path -LiteralPath $old)) {
        Write-Warning "Step 6 failed, so the previous install is put back: $($stepError.Exception.Message)"
        try {
            # Renamed aside, not deleted, so a file held open can't leave a
            # half-deleted folder in the way of the old install.
            $failed = "$dir.failed"
            if (Test-Path -LiteralPath $failed) { Remove-Tree $failed }
            Rename-Retry $dir (Split-Path $failed -Leaf)
            try { Rename-Retry $old (Split-Path $dir -Leaf) }
            catch {
                # Never leave nothing at $dir: put the new install back instead.
                Rename-Retry $failed (Split-Path $dir -Leaf)
                throw
            }
            if (Test-Path -LiteralPath $lnkBackup) {
                Copy-Item -LiteralPath $lnkBackup -Destination $lnk -Force
                try { Assert-AdminOnly $lnk $edit }
                catch { Remove-Item -LiteralPath $lnk -Force -ErrorAction SilentlyContinue }
            }
            Remove-Item -LiteralPath $key -Recurse -Force -ErrorAction SilentlyContinue
            if ($prevEntry) {
                New-Item $key -Force | Out-Null
                foreach ($p in $prevEntry.PSObject.Properties | Where-Object Name -notlike 'PS*') {
                    $type = if ($p.Value -is [int]) { 'DWord' } else { 'String' }
                    New-ItemProperty $key -Name $p.Name -Value $p.Value -PropertyType $type -Force | Out-Null
                }
            }
            try { Remove-Tree $failed } catch { Write-Warning "Couldn't remove $failed. The next run clears it." }
        }
        catch { Write-Warning "Couldn't put the previous install back: $($_.Exception.Message)" }
    }
    elseif (-not $hadOld) {
        # A first install that fails here leaves no Apps entry or shortcut, so
        # a deployment tool's detection rule doesn't count it as installed and
        # tries again.
        Remove-Item -LiteralPath $key -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $lnk -Force -ErrorAction SilentlyContinue
    }
    Remove-Item -LiteralPath $lnkBackup -Force -ErrorAction SilentlyContinue
    throw $stepError
}
Remove-Item -LiteralPath $lnkBackup -Force -ErrorAction SilentlyContinue
# Step 6 worked, so the old install can go. A leftover .old is only a warning.
if ($hadOld) {
    try { Remove-Tree $old }
    catch { Write-Warning "Installed, but couldn't remove $old. The next run clears it." }
}

$how = if ($prevVersion -and $prevVersion -ne $version) { "upgraded from $prevVersion" } elseif ($prevVersion) { 'reinstalled' } else { 'new install' }
Write-Color "Installed hello-world $version to $dir ($how)." Green
Write-AppEvent 1000 Information "Installed hello-world $version to $dir ($how)." 
Write-Info "hello.py SHA-256: $hash"
Write-Info "Next: open hello-world from the Start menu to check it. The setup folder can be deleted. The log is $log." 
}
# The host prints a script's error only after the finally below, so write it to the log first.
catch {
    Write-Color "FAILED: $($_.Exception.Message)" Red
    Write-Host "The steps above and this message are in $log."
    Write-AppEvent 1001 Error "hello-world install failed: $($_.Exception.Message)"
    if ($script:busy) { exit 1618 }
    exit 1
}
finally {
    Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    Restore-Window
}
