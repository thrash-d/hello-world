<#
.SYNOPSIS
Removes a hello-world that install-user.ps1 installed for this user.

.DESCRIPTION
install-user.ps1 copies this into the install folder and registers it as the
Uninstall command in Settings > Apps for this user. It removes the folder, the
Start menu entry, the Apps entry, the sign-in reminder and its scheduled
task. The saved notes stay, unless -RemoveNotes is given. -Quiet skips the
Press Enter prompt.
#>
param([switch]$Quiet, [switch]$RemoveNotes)
$ErrorActionPreference = 'Stop'
$sys32 = [Environment]::SystemDirectory
$local = [Environment]::GetFolderPath('LocalApplicationData')
$dir = Join-Path $local 'Programs\hello-world'
$exitCode = 0
try {
    # Windows won't delete the folder this script's window is in.
    Set-Location $local
    [Environment]::CurrentDirectory = $local
    $run = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    $value = (Get-ItemProperty -LiteralPath $run -Name 'hello-world' -ErrorAction SilentlyContinue).'hello-world'
    if ($value -and $value -like "*$dir*") { Remove-ItemProperty -LiteralPath $run -Name 'hello-world' }
    & (Join-Path $sys32 'schtasks.exe') /Delete /F /TN "hello-world reminder $env:USERNAME" 2>$null | Out-Null
    foreach ($k in 'HKCU:\Software\Classes\hello-world', 'HKCU:\Software\Classes\AppUserModelId\hello-world',
                   'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\hello-world') {
        if (Test-Path -LiteralPath $k) { Remove-Item -LiteralPath $k -Recurse -Force }
    }
    $lnk = Join-Path ([Environment]::GetFolderPath('Programs')) 'hello-world.lnk'
    if (Test-Path -LiteralPath $lnk) { Remove-Item -LiteralPath $lnk -Force }
    if (Test-Path -LiteralPath $dir) {
        # rmdir removes a link inside the folder without following it.
        & (Join-Path $sys32 'cmd.exe') /d /c rmdir /s /q "`"$dir`""
        if (Test-Path -LiteralPath $dir) { throw "A file in $dir is in use. Close hello-world and try again." }
    }
    if ($RemoveNotes) {
        $notes = Join-Path $local 'hello-world'
        if (Test-Path -LiteralPath $notes) { & (Join-Path $sys32 'cmd.exe') /d /c rmdir /s /q "`"$notes`"" }
    }
    Write-Host 'hello-world is uninstalled for this user.'
}
catch {
    Write-Host "Uninstall failed: $($_.Exception.Message)"
    $exitCode = 1
}
finally {
    if (-not $Quiet) { Read-Host 'Press Enter to close' | Out-Null }
}
exit $exitCode
