<#
.SYNOPSIS
Removes hello-world: the install folder, the Start menu shortcut, and the
entry in Settings > Apps.

.DESCRIPTION
install.ps1 copies this into the install folder and registers it as the
Uninstall command in Settings > Apps. It asks for administrator rights when
it starts without them. -Quiet skips the Press Enter prompts, and a failed
uninstall exits with 1.
#>
param([switch]$Quiet)
$ErrorActionPreference = 'Stop'
function Wait-Close { if (-not $Quiet) { Read-Host 'Press Enter to close' } }
# A 32-bit PowerShell sees Program Files (x86) and the 32-bit registry.
if (-not [Environment]::Is64BitProcess) {
    Write-Host 'Run this from 64-bit PowerShell.' -ForegroundColor Red; Wait-Close; exit 1
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
$ps = Join-Path ([Environment]::SystemDirectory) 'WindowsPowerShell\v1.0\powershell.exe'
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
        Start-Process $ps -Verb RunAs -ArgumentList $argList
    }
    catch { Write-Host "Couldn't get administrator rights: $($_.Exception.Message) Ask IT to uninstall hello-world." -ForegroundColor Red; Wait-Close }
    exit
}

# The elevated window closes when the script ends, so hold it open to show the result.
try {
    # Windows won't delete a folder that is the current directory. Set both:
    # Set-Location may leave the process's own directory where it was.
    Set-Location $winDir
    [Environment]::CurrentDirectory = $winDir
    # The Apps entry runs $dir\uninstall.ps1, so it is the way to try again:
    # it and its folder go late, after the shortcut, which a failure can leave
    # harmlessly, and the Apps entry goes last.
    $lnk = Join-Path ([Environment]::GetFolderPath('CommonPrograms')) 'hello-world.lnk'
    if (Test-Path -LiteralPath $lnk) { Remove-Item -LiteralPath $lnk }
    foreach ($f in "$dir.new", "$dir.old") {
        if (Test-Path -LiteralPath $f) { Remove-Tree $f }
    }
    if (Test-Path -LiteralPath $dir) {
        Get-ChildItem -LiteralPath $dir -Force | Where-Object Name -ne 'uninstall.ps1' |
            Remove-Item -Recurse -Force
        # Antivirus can hold a file for a moment.
        for ($try = 1; ; $try++) {
            try { Remove-Item -LiteralPath $dir -Recurse -Force; break }
            catch { if ($try -ge 5) { throw }; Start-Sleep -Seconds 1 }
        }
    }
    # Any user can turn on a sign-in reminder. Its launcher sits in that user's own
    # Startup folder and would show an error at every sign-in once hello.cmd is gone.
    $profiles = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\*' -ErrorAction SilentlyContinue).ProfileImagePath
    foreach ($p in $profiles) {
        if (-not $p) { continue }
        $launcher = Join-Path ([Environment]::ExpandEnvironmentVariables($p)) 'AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\hello-world-daily.cmd'
        Remove-Item -LiteralPath $launcher -Force -ErrorAction SilentlyContinue
    }
    $key = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world'
    if (Test-Path -LiteralPath $key) { Remove-Item -LiteralPath $key }
    Write-Host 'hello-world is uninstalled.' -ForegroundColor Green
    Write-Host 'Each user keeps their own saved notes in AppData\Local\hello-world. They can delete that folder if they want.'
}
catch {
    Write-Host "Uninstall failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Close any hello-world windows, then try again from Settings > Apps > Installed apps > hello-world > Uninstall. If it fails again, ask IT.'
    $failed = $true
}
finally { Wait-Close }
if ($failed) { exit 1 }
