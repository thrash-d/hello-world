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
$dir = Join-Path $env:ProgramFiles 'hello-world'

# Settings > Apps starts this without elevation, so ask for it.
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Verb RunAs `
        -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`""
    exit
}

# Windows won't delete a folder that is the current directory.
Set-Location $env:SystemRoot
Remove-Item (Join-Path ([Environment]::GetFolderPath('CommonPrograms')) 'hello-world.lnk') -ErrorAction SilentlyContinue
Remove-Item 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world' -ErrorAction SilentlyContinue
# The .new and .old folders exist only after an interrupted install.
foreach ($f in $dir, "$dir.new", "$dir.old") {
    if (Test-Path -LiteralPath $f) { Remove-Item -LiteralPath $f -Recurse -Force }
}
'hello-world is uninstalled.'
