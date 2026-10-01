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
if (-not [Environment]::Is64BitProcess) {
    Write-Host 'Run this from 64-bit PowerShell.' -ForegroundColor Red; Read-Host 'Press Enter to close'; exit 1
}
$dir = Join-Path $env:ProgramFiles 'hello-world'

# Settings > Apps starts this without elevation, so ask for it.
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    try {
        Start-Process "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Verb RunAs `
            -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`""
    }
    catch { Write-Host "Couldn't get administrator rights: $_" -ForegroundColor Red; Read-Host 'Press Enter to close' }
    exit
}

# The elevated window closes when the script ends, so hold it open to show the result.
try {
    # Windows won't delete a folder that is the current directory. Set both:
    # Set-Location may leave the process's own directory where it was.
    Set-Location $env:SystemRoot
    [Environment]::CurrentDirectory = $env:SystemRoot
    # The Apps entry runs $dir\uninstall.ps1, so it is the way to try again:
    # it and its folder go late, after the shortcut, which a failure can leave
    # harmlessly, and the Apps entry goes last.
    $lnk = Join-Path ([Environment]::GetFolderPath('CommonPrograms')) 'hello-world.lnk'
    if (Test-Path -LiteralPath $lnk) { Remove-Item -LiteralPath $lnk }
    foreach ($f in "$dir.new", "$dir.old") {
        if (Test-Path -LiteralPath $f) { Remove-Item -LiteralPath $f -Recurse -Force }
    }
    if (Test-Path -LiteralPath $dir) {
        Get-ChildItem -LiteralPath $dir -Force | Where-Object Name -ne 'uninstall.ps1' |
            Remove-Item -Recurse -Force
        Remove-Item -LiteralPath $dir -Recurse -Force
    }
    $key = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world'
    if (Test-Path -LiteralPath $key) { Remove-Item -LiteralPath $key }
    'hello-world is uninstalled.'
}
catch { Write-Host "Uninstall failed: $_" -ForegroundColor Red }
finally { Read-Host 'Press Enter to close' }
