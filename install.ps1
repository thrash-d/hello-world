<#
.SYNOPSIS
Installs hello.py for all users in a folder only administrators can change.

.DESCRIPTION
Creates "Program Files\hello-world", where only Administrators and SYSTEM can
write. Unpacks a pinned, hash-checked Python from python.org into it, copies
hello.py and uninstall.ps1 there, and writes hello.cmd next to them. hello.cmd
starts hello.py with that Python in isolated mode. Adds a hello-world shortcut
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

.EXAMPLE
$d = "$env:ProgramFiles\hello-setup"; New-Item -ItemType Directory $d
$icacls = "$env:SystemRoot\System32\icacls.exe"; $git = (Get-ItemProperty HKLM:\SOFTWARE\GitForWindows).InstallPath + '\cmd\git.exe'
& $icacls $d /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F'
& $git clone -b <release tag> --depth 1 https://github.com/thrash-d/hello-world $d
cd $d; Set-ExecutionPolicy -Scope Process Bypass -Force
.\install.ps1 -Commit <reviewed commit hash>

Run each line on its own, in order, in one elevated window. Long lines wrap
when copied from a terminal and break the paste.

Locks the setup folder before cloning into it, so nobody else can add files
to the clone, then installs the reviewed commit. Pass the full commit hash,
never a tag name. The tools run by full path for the same reason the
installer pins them. Windows clients block scripts by default, so the
example allows them for this PowerShell window only. If a Group Policy sets
the execution policy, that line errors and the policy decides.
To install again, delete the setup folder first, so the example's New-Item and
clone work a second time. The installer upgrades an existing install in place.

.NOTES
Employees open hello-world from the Start menu. To uninstall, use Settings >
Apps > Installed apps > hello-world > Uninstall. That also removes the .new and
.old folders an interrupted run can leave. The setup folder isn't needed after
a successful install and can be deleted.
#>
#Requires -RunAsAdministrator
param([Parameter(Mandatory)][ValidatePattern('^[0-9a-f]{40}$')][string]$Commit)
$ErrorActionPreference = 'Stop'
# A 32-bit PowerShell sees Program Files (x86) and the 32-bit registry.
if (-not [Environment]::Is64BitProcess) { throw 'Run this from 64-bit PowerShell.' }
# The pinned Python is the amd64 build, which ARM64 Windows 10 can't run.
if ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64') { throw "Need an x64 PC, found $env:PROCESSOR_ARCHITECTURE." }
# Ask Windows for the folders; the admin's own session can carry other values.
$pf = [Environment]::GetFolderPath('ProgramFiles')
$winDir = [Environment]::GetFolderPath('Windows')
$sys32 = [Environment]::SystemDirectory
$dir = Join-Path $pf 'hello-world'
# A record of what this run checked and did, in the admin-only setup folder.
Start-Transcript -LiteralPath (Join-Path $PSScriptRoot 'install.log') -Force | Out-Null

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

function Assert-AdminOnly([string]$Path, [int64]$Rights) {
    # Literal, because Git ships a file named "[.exe".
    $acl = Get-Acl -LiteralPath $Path
    $sid = [Security.Principal.SecurityIdentifier]
    # An owner can always rewrite the DACL, so a non-admin owner counts too.
    $others = @($acl.GetOwner($sid).Value) + @($acl.GetAccessRules($true, $true, $sid) |
        Where-Object { $_.AccessControlType -eq 'Allow' -and
            -not $_.PropagationFlags.HasFlag([Security.AccessControl.PropagationFlags]::InheritOnly) -and
            ([int64]$_.FileSystemRights -band $Rights) } |
        ForEach-Object { $_.IdentityReference.Value }) | Where-Object { $_ -notin $trusted }
    if ($others) { throw "Non-administrators can change $Path ($($others -join ', '))." }
}

# Everything this installer runs as admin comes from a folder tree: Git, the
# clone, and the installed Python. Nobody but administrators may change
# anything in the tree, and nobody may swap out a folder above it.
function Assert-AdminOnlyTree([string]$Root) {
    Write-Host "Checking permissions under $Root (this can take a minute)"
    foreach ($i in @(Get-Item -LiteralPath $Root -Force) + @(Get-ChildItem -LiteralPath $Root -Recurse -Force)) {
        # A link's own ACL says nothing about its target.
        if ($i.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "$($i.FullName) is a link." }
        Assert-AdminOnly $i.FullName $edit
    }
    # A drive root can't be deleted or renamed, so Delete on it doesn't matter.
    for ($p = (Get-Item -LiteralPath $Root -Force).Parent; $p; $p = $p.Parent) {
        Assert-AdminOnly $p.FullName ($(if ($p.Parent) { $swap } else { $swap -band -bnot 0x10000 }))
    }
}

# Antivirus scans and a running hello.cmd can hold a file open for a moment,
# and Windows won't rename a folder with an open file in it.
function Rename-Retry([string]$Path, [string]$NewName) {
    for ($try = 1; ; $try++) {
        try { Rename-Item -LiteralPath $Path -NewName $NewName; return }
        catch { if ($try -ge 5) { throw }; Start-Sleep -Seconds 1 }
    }
}

# An interrupted swap leaves the old install as the only good copy. Restore it
# before any check or download that could fail and leave the PC without one.
$new = "$dir.new"
$old = "$dir.old"
if (-not (Test-Path -LiteralPath $dir) -and (Test-Path -LiteralPath $old)) {
    if (Test-Path -LiteralPath (Join-Path $old 'hello.cmd')) {
        Rename-Retry $old (Split-Path $dir -Leaf)
        if (-not (Test-Path -LiteralPath (Join-Path $dir 'hello.cmd'))) { Write-Warning "$dir has no hello.cmd after the restore." }
    }
    else { Write-Warning "$old has no hello.cmd, so it isn't restored. This run installs fresh." }
}

# PATH can list folders employees can write, and a git or icacls found there
# would run as admin. Call both by full path.
$icacls = Join-Path $sys32 'icacls.exe'
$gitDir = (Get-ItemProperty HKLM:\SOFTWARE\GitForWindows -ErrorAction SilentlyContinue).InstallPath
$git = "$gitDir\cmd\git.exe"
if (-not $git.StartsWith("$pf\", [StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $git)) {
    throw "Need Git for Windows installed for all users under $pf. Found: '$git'"
}
Assert-AdminOnlyTree $gitDir
# Git for Windows also reads its system config from here.
$gitData = Join-Path ([Environment]::GetFolderPath('CommonApplicationData')) 'Git'
if (Test-Path -LiteralPath $gitData) { Assert-AdminOnlyTree $gitData }
# The admin's own session can carry GIT_DIR and friends that point git elsewhere.
Get-ChildItem Env: | Where-Object Name -like 'GIT_*' | ForEach-Object { Remove-Item -LiteralPath "Env:$($_.Name)" }

# Covers .git too, so nobody can plant git objects that fool the commit check.
Assert-AdminOnlyTree $PSScriptRoot

# The ACL checks show nobody else can change the clone. This shows the clone is
# the reviewed commit, so a moved tag or an edited file fails here.
# git also finds a repository in a parent folder, so require .git here.
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot '.git'))) { throw "$PSScriptRoot is not the top of a git clone." }
$head = & $git -C $PSScriptRoot rev-parse HEAD
if ($LASTEXITCODE -or $head -ne $Commit) { throw "Source is at '$head', not the reviewed commit $Commit." }
foreach ($f in 'install.ps1', 'uninstall.ps1', 'hello.py', 'VERSION') {
    $actual = & $git -C $PSScriptRoot hash-object $f
    $actualOk = $LASTEXITCODE -eq 0
    $expected = & $git -C $PSScriptRoot rev-parse "HEAD:$f"
    # Both commands failing and printing nothing must not read as a match.
    if (-not $actualOk -or $LASTEXITCODE -or "$actual" -notmatch '^[0-9a-f]{40}$' -or "$actual" -ne "$expected") {
        throw "$f differs from commit $Commit."
    }
}

# Download into the clone, which only administrators can change, and check the
# hash before the old install is touched. The zip is deleted afterward.
Write-Host "Downloading $pyUrl"
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
    foreach ($leftover in $new, $old) { if (Test-Path -LiteralPath $leftover) { Remove-Item -LiteralPath $leftover -Recurse -Force } }
    New-Item -ItemType Directory $new | Out-Null
    # Drop inherited entries. Administrators and SYSTEM get full control, Users
    # get read and run. Files created below inherit this.
    & $icacls $new /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX' | Out-Null
    if ($LASTEXITCODE) { throw "icacls failed on $new" }

    Expand-Archive -LiteralPath $zip -DestinationPath (Join-Path $new 'python')
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'hello.py'), (Join-Path $PSScriptRoot 'uninstall.ps1') -Destination $new
    # -I ignores PYTHON* variables and the user's site-packages, so nothing the
    # employee controls loads into the run.
    Set-Content -LiteralPath (Join-Path $new 'hello.cmd') -Value '@"%~dp0python\python.exe" -I "%~dp0hello.py"' -Encoding ascii

    $hash = (Get-FileHash -LiteralPath (Join-Path $new 'hello.py')).Hash
    if ($hash -ne (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot 'hello.py')).Hash) { throw 'Installed hello.py differs from the source' }

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
    $out = & (Join-Path $new 'hello.cmd')
    if ($LASTEXITCODE -or "$out" -ne 'Hello, world!') { throw "Test run failed with exit $LASTEXITCODE`: $out" }

    # Swap in the new folder, and put the old one back if that fails.
    $hadOld = Test-Path -LiteralPath $dir
    # Only administrators can plant a link here, but never delete through one.
    if ($hadOld -and ((Get-Item -LiteralPath $dir -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "$dir is a link." }
    if ($hadOld) { Rename-Retry $dir (Split-Path $old -Leaf) }
    try { Rename-Retry $new (Split-Path $dir -Leaf) }
    catch {
        if ($hadOld) { Rename-Retry $old (Split-Path $dir -Leaf) }
        throw
    }
    # The new install is live now, so a leftover .old is only a warning.
    if ($hadOld) {
        try { Remove-Item -LiteralPath $old -Recurse -Force }
        catch { Write-Warning "Installed, but couldn't remove $old. The next run clears it." }
    }
}
finally {
    Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath "$dir.new" -Recurse -Force -ErrorAction SilentlyContinue
}

# Added only after the checks pass. The entry in Settings > Apps, whose Uninstall button runs uninstall.ps1.
$key = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world'
New-Item $key -Force | Out-Null
$entry = @{
    DisplayName     = 'hello-world'
    DisplayVersion  = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'VERSION')).Trim()
    InstallLocation = $dir
    UninstallString = "`"$(Join-Path $sys32 'WindowsPowerShell\v1.0\powershell.exe')`" -NoProfile -ExecutionPolicy Bypass -File `"$dir\uninstall.ps1`""
}
foreach ($name in $entry.Keys) { New-ItemProperty $key -Name $name -Value $entry[$name] -Force | Out-Null }
foreach ($name in 'NoModify', 'NoRepair') { New-ItemProperty $key -Name $name -Value 1 -PropertyType DWord -Force | Out-Null }

# Added only after the checks pass, so a failed install never shows up in the
# Start menu, and after the Apps entry, so a half-finished install still has
# an Uninstall button. Run straight from Explorer, hello.cmd's window closes before
# anyone can read it; the shortcut keeps it open until a key is pressed.
$lnk = Join-Path ([Environment]::GetFolderPath('CommonPrograms')) 'hello-world.lnk'
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$shortcut.TargetPath = Join-Path $sys32 'cmd.exe'
$shortcut.Arguments = "/c `"`"$dir\hello.cmd`" & pause`""
# Not $dir: a window left open there is a current directory, and Windows won't
# rename or delete a folder that one is in.
$shortcut.WorkingDirectory = $winDir
$shortcut.Save()

# Every employee opens this shortcut, so only administrators may change it.
# A shortcut that fails the check is removed, not left in every Start menu.
try { Assert-AdminOnly $lnk $edit }
catch { Remove-Item -LiteralPath $lnk -Force -ErrorAction SilentlyContinue; throw }

"Installed to $dir. hello.py SHA-256: $hash (it differs between LF and CRLF checkouts; the -Commit check is what pins the source)"
