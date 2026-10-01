<#
.SYNOPSIS
Removes hello-world: the install folder, the Start menu shortcut, and the
entry in Settings > Apps.

.DESCRIPTION
install.ps1 copies this into the install folder and registers it as the
Uninstall command in Settings > Apps. It asks for administrator rights when
it starts without them.
#>
$ErrorActionPreference = 'Stop'
# A 32-bit PowerShell sees Program Files (x86) and the 32-bit registry.
if (-not [Environment]::Is64BitProcess) { throw 'Run this from 64-bit PowerShell.' }
$dir = Join-Path $env:ProgramFiles 'hello-world'

# Settings > Apps starts this without elevation, so ask for it.
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Verb RunAs `
        -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`""
    exit
}

# The elevated window closes when the script ends, so hold it open to show the result.
try {
    # Windows won't delete a folder that is the current directory.
    Set-Location $env:SystemRoot
    # Folders first. The Apps entry is the way to try again, so it goes last.
    # The .new and .old folders exist only after an interrupted install.
    foreach ($f in $dir, "$dir.new", "$dir.old") {
        if (Test-Path -LiteralPath $f) { Remove-Item -LiteralPath $f -Recurse -Force }
    }
    Remove-Item -LiteralPath (Join-Path ([Environment]::GetFolderPath('CommonPrograms')) 'hello-world.lnk') -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world' -ErrorAction SilentlyContinue
    'hello-world is uninstalled.'
}
catch { Write-Host "Uninstall failed: $_" -ForegroundColor Red }
finally { Read-Host 'Press Enter to close' }
