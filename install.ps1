<#
.SYNOPSIS
Installs hello.py for all users in a folder only administrators can change.

.DESCRIPTION
Creates "Program Files\hello-world", where only Administrators and SYSTEM can
write. Unpacks a pinned, hash-checked Python from python.org into it, copies
hello.py and uninstall.ps1 there, and writes hello.cmd next to them. hello.cmd
starts hello.py with that Python in isolated mode and passes its options on. Adds a hello-world shortcut
to every user's Start menu and an entry with an Uninstall button to Settings >
Apps. The workstation needs Git for Windows and internet access, but no Python
of its own. Its guarantees hold only if the employees use standard accounts. A
local administrator can change anything it protects.

Run it from an elevated PowerShell on each workstation, from a git clone of a
release tag in a folder only administrators can write. It refuses anything
else, such as an employee's Downloads folder, a clone at another commit, or a
file changed since checkout.

.PARAMETER Commit
The full commit hash that was reviewed. The clone must be at this commit.

.PARAMETER Quiet
Prints only warnings, errors, and the final result line. Everything is still
written to install.log. The exit code is 0 on success and 1 on failure, so a
management tool can run the installer unattended. It never asks questions.

.EXAMPLE
$tag = 'v1.17.0'
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

The setup folder can be deleted after a successful install. Copy install.log first
if you need a record of the installation steps.
#>
#Requires -RunAsAdministrator
param([Parameter(Mandatory)][ValidatePattern('^[0-9a-f]{40}$')][string]$Commit, [switch]$Quiet)
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
trap { Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red; Restore-Window; exit 1 }
# Progress lines for the person running this. -Quiet hides them; the log keeps them.
function Write-Step([string]$Text) { if (-not $Quiet) { Write-Host $Text -ForegroundColor Cyan } }
function Write-Info([string]$Text) { if (-not $Quiet) { Write-Host $Text } }
# A 32-bit PowerShell sees Program Files (x86) and the 32-bit registry.
if (-not [Environment]::Is64BitProcess) { throw 'Run this from 64-bit PowerShell.' }
# The pinned Python is the amd64 build, which ARM64 Windows 10 can't run.
if ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64') { throw "Need an x64 PC, found $env:PROCESSOR_ARCHITECTURE." }
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

    $others = @($owner) + @($aceRules) | Where-Object { $_ -notin $trusted } | Select-Object -Unique
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
    foreach ($i in @(Get-Item -LiteralPath $Root -Force) + @(Get-ChildItem -LiteralPath $Root -Recurse -Force)) {
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
        catch { if ($try -ge 5) { throw }; Start-Sleep -Seconds 1 }
    }
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
Write-Step '[1/6] Checking Git for Windows and its folders'
# PATH can list folders employees can write, and a git or icacls found there
# would run as admin. Call both by full path.
$icacls = Join-Path $sys32 'icacls.exe'
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
# The admin's own session can carry GIT_DIR and friends that point git elsewhere, and
# HOME/XDG_CONFIG_HOME can point to employee-writable locations. Clear them. Git then
# falls back to the admin's profile for ~/.gitconfig, which is admin-only unless the
# profile is redirected.
Get-ChildItem Env: | Where-Object Name -like 'GIT_*' | ForEach-Object { Remove-Item -LiteralPath "Env:$($_.Name)" }
Remove-Item -LiteralPath 'Env:HOME' -ErrorAction SilentlyContinue
Remove-Item -LiteralPath 'Env:XDG_CONFIG_HOME' -ErrorAction SilentlyContinue
# Set GIT_CONFIG_NOSYSTEM to prevent git from reading /etc/gitconfig (equivalent on Windows)
$env:GIT_CONFIG_NOSYSTEM = '1'

# Covers .git too, so nobody can plant git objects that fool the commit check.
Write-Step '[2/6] Checking the setup folder'
Assert-AdminOnlyTree $PSScriptRoot

# A record of the steps from here on; the checks above print to the console
# only. Opened only now that the setup folder is known to be admin-only, and
# stopped in the last finally below.
try { Start-Transcript -LiteralPath (Join-Path $PSScriptRoot 'install.log') -Append | Out-Null }
catch { throw "Couldn't start the install log (is a transcript already running in this window?): $_" }
Write-Info "Logging to $(Join-Path $PSScriptRoot 'install.log')"
try {

# === COMMIT VERIFICATION: Ensure the clone is at the reviewed commit ===
Write-Step '[3/6] Verifying the reviewed commit'
# The ACL checks show nobody else can change the clone. This shows the clone is
# the reviewed commit, so a moved tag or an edited file fails here.
# git also finds a repository in a parent folder, so require .git here.
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot '.git') -PathType Container)) { throw "$PSScriptRoot is not the top of a git clone (.git must be a folder)." }
$head = & $git -C $PSScriptRoot rev-parse HEAD
if ($LASTEXITCODE) { throw "git rev-parse failed with exit $LASTEXITCODE in $PSScriptRoot. If the message above mentions 'dubious ownership', a different account made this clone." }
if ($head -ne $Commit) { throw "Source is at '$head', not the reviewed commit $Commit." }
foreach ($f in 'install.ps1', 'uninstall.ps1', 'hello.py', 'VERSION') {
    $actual = & $git -C $PSScriptRoot hash-object $f
    $actualOk = $LASTEXITCODE -eq 0
    $expected = & $git -C $PSScriptRoot rev-parse "HEAD:$f"
    # Both commands failing and printing nothing must not read as a match.
    if (-not $actualOk -or $LASTEXITCODE -or "$actual" -notmatch '^[0-9a-f]{40}$' -or "$actual" -ne "$expected") {
        throw "$f differs from commit $Commit. Do not modify files in the clone. Re-clone from the reviewed release tag to reinstall."
    }
}

# === DOWNLOAD AND BUILD: Fetch Python, build, and test in isolation ===
Write-Step '[4/6] Downloading Python and verifying its hash'
# Download into the clone, which only administrators can change, and check the
# hash before the old install is touched. The zip is deleted afterward.
Write-Info "Downloading $pyUrl"
$zip = Join-Path $PSScriptRoot 'python-embed.zip'
# Windows PowerShell 5.1 can default to TLS versions python.org refuses, and its
# progress bar slows downloads to a crawl.
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
$ProgressPreference = 'SilentlyContinue'
try {
    for ($try = 1; ; $try++) {
        try { Invoke-WebRequest $pyUrl -OutFile $zip -UseBasicParsing -TimeoutSec 300; break }
        catch { if ($try -ge 3) { throw }; Write-Warning "Download failed ($_). Trying again."; Start-Sleep -Seconds 5 }
    }
    if ((Get-FileHash -LiteralPath $zip).Hash -ne $pySha256) { throw "The Python download doesn't match the pinned SHA-256." }

    # Build and test the new install beside the old one, so a failure leaves
    # the working install alone. Both sit in Program Files, which only
    # administrators can write to.
    Write-Step '[5/6] Building, testing and installing'
    foreach ($leftover in $new, $old) { if (Test-Path -LiteralPath $leftover) { Remove-Tree $leftover } }
    New-Item -ItemType Directory $new | Out-Null
    # Drop inherited entries. Administrators and SYSTEM get full control, Users
    # get read and run. Files created below inherit this.
    & $icacls $new /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX' | Out-Null
    if ($LASTEXITCODE) { throw "icacls failed on $new" }

    Expand-Archive -LiteralPath $zip -DestinationPath (Join-Path $new 'python')
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'hello.py'), (Join-Path $PSScriptRoot 'uninstall.ps1') -Destination $new
    # -I ignores PYTHON* variables and the user's site-packages, so nothing the
    # employee controls loads into the run.
    Set-Content -LiteralPath (Join-Path $new 'hello.cmd') -Value '@"%~dp0python\python.exe" -I "%~dp0hello.py" %*' -Encoding ascii

    $hash = (Get-FileHash -LiteralPath (Join-Path $new 'hello.py')).Hash
    foreach ($f in 'hello.py', 'uninstall.ps1') {
        if ((Get-FileHash -LiteralPath (Join-Path $new $f)).Hash -ne (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $f)).Hash) { throw "Installed $f differs from the source" }
    }

    # Check the tree before running anything from it as admin.
    Assert-AdminOnlyTree $new
    foreach ($f in $new, (Join-Path $new 'hello.py'), (Join-Path $new 'hello.cmd'), (Join-Path $new 'python\python.exe')) {
        $usersRX = (Get-Acl -LiteralPath $f).GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]) | Where-Object {
            $_.IdentityReference.Value -eq 'S-1-5-32-545' -and $_.FileSystemRights.HasFlag([Security.AccessControl.FileSystemRights]::ReadAndExecute) }
        if (-not $usersRX) { throw "Users can't read and run $f" }
    }
    # --plain prints only the greeting and saves nothing, so the test leaves no notes in the admin's profile.
    $out = & (Join-Path $new 'hello.cmd') --plain
    if ($LASTEXITCODE -or "$out" -ne 'Hello, world!') { throw "Test run failed with exit $LASTEXITCODE`: $out" }

    # Swap in the new folder, and put the old one back if that fails.
    $hadOld = Test-Path -LiteralPath $dir
    $prevVersion = (Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue).DisplayVersion
    # Only administrators can plant a link here, but never delete through one.
    if ($hadOld) { Assert-NotLink $dir }
    if ($hadOld) { Rename-Retry $dir (Split-Path $old -Leaf) }
    try { Rename-Retry $new (Split-Path $dir -Leaf) }
    catch {
        if ($hadOld) { Rename-Retry $old (Split-Path $dir -Leaf) }
        throw
    }
    # The new install is live now, so a leftover .old is only a warning.
    if ($hadOld) {
        try { Remove-Tree $old }
        catch { Write-Warning "Installed, but couldn't remove $old. The next run clears it." }
    }
}
finally {
    Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $new) { try { Remove-Tree $new } catch { Write-Warning "Couldn't remove $new. The next run clears it." } }
}

# === FINALIZATION: Register the installation in Windows settings and Start menu ===
Write-Step '[6/6] Adding the Start menu shortcut and the Settings > Apps entry'
# Added only after the checks pass. The entry in Settings > Apps, whose Uninstall button runs uninstall.ps1.
$version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'VERSION')).Trim()
$pyExe = Join-Path $dir 'python\python.exe'
New-Item $key -Force | Out-Null
$entry = @{
    DisplayName     = 'hello-world'
    DisplayVersion  = $version
    Publisher       = 'IT Department'
    DisplayIcon     = "$pyExe,0"
    InstallLocation = $dir
    UninstallString = "`"$(Join-Path $sys32 'WindowsPowerShell\v1.0\powershell.exe')`" -NoProfile -ExecutionPolicy Bypass -File `"$dir\uninstall.ps1`""
}
foreach ($name in $entry.Keys) { New-ItemProperty $key -Name $name -Value $entry[$name] -Force | Out-Null }
# Settings > Apps shows the size in KB.
$sizeKB = [int]((Get-ChildItem -LiteralPath $dir -Recurse -File -Force | Measure-Object Length -Sum).Sum / 1KB)
$dwords = @{ NoModify = 1; NoRepair = 1; EstimatedSize = $sizeKB }
foreach ($name in $dwords.Keys) { New-ItemProperty $key -Name $name -Value $dwords[$name] -PropertyType DWord -Force | Out-Null }

# Added only after the checks pass, so a failed install never shows up in the
# Start menu, and after the Apps entry, so a half-finished install still has
# an Uninstall button. hello.py waits for Enter before it closes its window; the
# shortcut adds a pause only when hello.cmd fails, so an error message stays readable.
$lnk = Join-Path ([Environment]::GetFolderPath('CommonPrograms')) 'hello-world.lnk'
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$shortcut.TargetPath = Join-Path $sys32 'cmd.exe'
$shortcut.Arguments = "/d /c `"title hello-world & `"$dir\hello.cmd`" & if errorlevel 1 pause`""
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

$how = if ($prevVersion -and $prevVersion -ne $version) { "upgraded from $prevVersion" } elseif ($prevVersion) { 'reinstalled' } else { 'new install' }
Write-Host "Installed hello-world $version to $dir ($how)." -ForegroundColor Green
Write-Host "hello.py SHA-256: $hash"
Write-Info 'Next: open hello-world from the Start menu to check it. The setup folder can be deleted; copy install.log first if you want the record.'
}
# The host prints a script's error only after the finally below, so write it to the log first.
catch { Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red; Write-Host 'The steps above and this message are in install.log in the setup folder.'; exit 1 }
finally { Stop-Transcript -ErrorAction SilentlyContinue | Out-Null; Restore-Window }
