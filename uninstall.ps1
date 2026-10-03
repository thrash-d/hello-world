<#
.SYNOPSIS
Removes hello-world: the install folder, the Start menu shortcut, and the
entry in Settings > Apps.

.DESCRIPTION
install.ps1 copies this into the install folder and registers it as the
Uninstall command in Settings > Apps. It asks for administrator rights when
it starts without them. -Quiet skips the Press Enter prompts.

Exit codes: 0 when removed, 1618 when an open hello-world window blocked it
(Intune and MECM retry that code later), and 1 for any other failure. Nothing
is changed when it exits 1618. Everything is written to
%WINDIR%\Logs\hello-world\uninstall.log, and the result goes to the
Application event log under the source hello-world.

Each user's saved notes stay in their own profile. Users can delete theirs
with menu option 4 before the program is removed. This script doesn't delete
inside user profiles, because a user could redirect such a delete elsewhere.
#>
param([switch]$Quiet)
$ErrorActionPreference = 'Stop'
function Wait-Close { if (-not $Quiet) { Read-Host 'Press Enter to close' } }
# A 32-bit PowerShell sees Program Files (x86) and the 32-bit registry.
# Intune runs uninstall commands in one, so start again in the 64-bit one.
if (-not [Environment]::Is64BitProcess) {
    $native = Join-Path ([Environment]::GetFolderPath('Windows')) 'sysnative\WindowsPowerShell\v1.0\powershell.exe'
    if (-not (Test-Path -LiteralPath $native)) {
        Write-Host 'Run this from 64-bit PowerShell.' -ForegroundColor Red; Wait-Close; exit 1
    }
    $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath)
    if ($Quiet) { $argList += '-Quiet' }
    & $native @argList
    exit $LASTEXITCODE
}
# Settings > Apps starts this as a standard user, and the elevated copy can
# inherit that user's environment variables, so ask Windows for the folders.
$winDir = [Environment]::GetFolderPath('Windows')
$sys32 = [Environment]::SystemDirectory

# Assert-NotLink and Remove-Tree duplicated in install.ps1; change both together.
# This script runs alone from the install folder, so it can't load that one.
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

# Write-AppEvent duplicated in install.ps1; change both together.
function Write-AppEvent([int]$Id, [string]$Type, [string]$Message) {
    try {
        if (-not [Diagnostics.EventLog]::SourceExists('hello-world')) { New-EventLog -LogName Application -Source 'hello-world' }
        Write-EventLog -LogName Application -Source 'hello-world' -EventId $Id -EntryType $Type -Message $Message
    }
    catch { Write-Warning "Couldn't write to the event log: $($_.Exception.Message)" }
}

# Versions before 1.23 wrote a launcher into each user's Startup folder. Remove
# only a plain file with that exact name, and only when no folder on the way
# from the profile down is a link: a user controls their own profile and
# could point a link at another folder.
function Remove-LegacyLauncher([string]$ProfileDir) {
    $parts = 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
    $path = $ProfileDir
    foreach ($part in @('') + $parts) {
        if ($part) { $path = Join-Path $path $part }
        $item = Get-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
        if (-not $item -or -not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { return }
    }
    foreach ($file in @(Get-ChildItem -LiteralPath $path -Force -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -eq 'hello-world-daily.cmd' -or $_.Name -like 'hello-world-daily.cmd.*.tmp' })) {
        if (-not ($file.Attributes -band [IO.FileAttributes]::ReparsePoint)) { [IO.File]::Delete($file.FullName) }
    }
}

$ps = Join-Path $sys32 'WindowsPowerShell\v1.0\powershell.exe'
$dir = Join-Path ([Environment]::GetFolderPath('ProgramFiles')) 'hello-world'
if ($PSScriptRoot -ne $dir) {
    Write-Host "Run this from $dir, not $PSScriptRoot." -ForegroundColor Red; Wait-Close; exit 1
}

# Settings > Apps starts this without elevation, so ask for it.
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    try {
        $argList = '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`""
        if ($Quiet) { $argList += '-Quiet' }
        # Waiting passes the elevated copy's exit code back, so -Quiet runs
        # from a management tool see whether the uninstall worked.
        $child = Start-Process $ps -Verb RunAs -ArgumentList $argList -Wait -PassThru
        exit $child.ExitCode
    }
    catch { Write-Host "Couldn't get administrator rights: $($_.Exception.Message) Ask IT to uninstall hello-world." -ForegroundColor Red; Wait-Close; exit 1 }
}

$logDir = Join-Path $winDir 'Logs\hello-world'
try {
    if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory $logDir | Out-Null }
    Assert-NotLink $logDir
    & (Join-Path $sys32 'icacls.exe') $logDir /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' | Out-Null
    Start-Transcript -LiteralPath (Join-Path $logDir 'uninstall.log') -Append | Out-Null
}
catch { Write-Warning "Couldn't start the uninstall log: $($_.Exception.Message)" }

$exitCode = 0
# The elevated window closes when the script ends, so hold it open to show the result.
try {
    # Windows won't delete a folder that is the current directory. Set both:
    # Set-Location may leave the process's own directory where it was.
    Set-Location $winDir
    [Environment]::CurrentDirectory = $winDir

    # Renamed aside first: if a hello-world window holds a file open, the
    # rename fails and nothing has changed yet, so the uninstall can
    # run again later.
    $removing = "$dir.removing"
    if (Test-Path -LiteralPath $dir) {
        Assert-NotLink $dir
        if (Test-Path -LiteralPath $removing) { Remove-Tree $removing }
        try { Rename-Item -LiteralPath $dir -NewName (Split-Path $removing -Leaf) }
        catch {
            # A file held open without delete sharing blocks the rename. That
            # passes, so the exit code asks the deployment tool to retry later.
            $exitCode = 1618
            $open = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path -like "$dir\*" })
            $hint = if ($open) { " $($open.Count) hello-world window(s) are open; closing them may help." } else { '' }
            throw "A file in $dir is in use.$hint Nothing was changed. Try again later."
        }
    }

    # Old launchers in each profile, one profile at a time, so one bad profile
    # can't stop the rest.
    $profiles = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\*' -ErrorAction SilentlyContinue).ProfileImagePath
    foreach ($p in $profiles) {
        if (-not $p) { continue }
        try { Remove-LegacyLauncher ([Environment]::ExpandEnvironmentVariables($p)) }
        catch { Write-Warning "Couldn't check the old launcher in ${p}: $($_.Exception.Message)" }
    }

    $lnk = Join-Path ([Environment]::GetFolderPath('CommonPrograms')) 'hello-world.lnk'
    if (Test-Path -LiteralPath $lnk) { Remove-Item -LiteralPath $lnk }
    foreach ($f in "$dir.new", "$dir.old", "$dir.failed") {
        if (Test-Path -LiteralPath $f) { Remove-Tree $f }
    }
    if (Test-Path -LiteralPath $removing) {
        # Antivirus can hold a file for a moment.
        for ($try = 1; ; $try++) {
            try { Remove-Tree $removing; break }
            catch { if ($try -ge 5) { Write-Warning "Couldn't remove $removing. The next install clears it."; break }; Start-Sleep -Seconds 1 }
        }
    }
    $key = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world'
    if (Test-Path -LiteralPath $key) { Remove-Item -LiteralPath $key -Recurse }
    Write-Host 'hello-world is uninstalled.' -ForegroundColor Green
    Write-Host 'Each user keeps their own saved notes in AppData\Local\hello-world. They can delete that folder if they want.'
    Write-AppEvent 1002 Information 'hello-world was uninstalled.'
}
catch {
    Write-Host "Uninstall failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Close any hello-world windows, then try again from Settings > Apps > Installed apps > hello-world > Uninstall. If it fails again, ask IT.'
    Write-AppEvent 1003 Error "hello-world uninstall failed: $($_.Exception.Message)"
    if (-not $exitCode) { $exitCode = 1 }
}
finally {
    Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    Wait-Close
}
exit $exitCode
