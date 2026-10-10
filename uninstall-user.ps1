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
    # Renamed aside before anything else changes, so a hello-world window
    # still open blocks the uninstall with everything left in place.
    $removing = "$dir.removing"
    if (Test-Path -LiteralPath $removing) { & (Join-Path $sys32 'cmd.exe') /d /c rmdir /s /q "`"$removing`"" }
    if (Test-Path -LiteralPath $dir) {
        try { Rename-Item -LiteralPath $dir -NewName (Split-Path $removing -Leaf) }
        catch { throw "A file in $dir is in use. Close hello-world and try again. Nothing was changed." }
    }
    $run = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    $value = (Get-ItemProperty -LiteralPath $run -Name 'hello-world' -ErrorAction SilentlyContinue).'hello-world'
    if ($value -and $value -like "*$dir*") { Remove-ItemProperty -LiteralPath $run -Name 'hello-world' }
    # Through cmd: Windows PowerShell 5.1 stops on any stderr text from a
    # native command, and schtasks writes some when there is no task.
    # -join binds looser than +, so the join needs its own parentheses.
    $task = 'hello-world reminder ' + ((@($env:USERDOMAIN, $env:USERNAME) | Where-Object { $_ }) -join '-')
    # Before 1.37.0 the task carried only the user name.
    # The daily repeat has its own task (1.57.0).
    $repeat = $task -replace '^hello-world reminder ', 'hello-world reminder repeat '
    foreach ($name in $task, $repeat, "hello-world reminder $env:USERNAME") {
        & (Join-Path $sys32 'cmd.exe') /d /c "`"$(Join-Path $sys32 'schtasks.exe')`" /Delete /F /TN `"$name`" >nul 2>&1"
    }
    foreach ($k in 'HKCU:\Software\Classes\hello-world', 'HKCU:\Software\Classes\AppUserModelId\hello-world',
                   'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\hello-world') {
        if (Test-Path -LiteralPath $k) { Remove-Item -LiteralPath $k -Recurse -Force }
    }
    $lnk = Join-Path ([Environment]::GetFolderPath('Programs')) 'hello-world.lnk'
    if (Test-Path -LiteralPath $lnk) { Remove-Item -LiteralPath $lnk -Force }
    if (Test-Path -LiteralPath $removing) {
        # rmdir removes a link inside the folder without following it.
        & (Join-Path $sys32 'cmd.exe') /d /c rmdir /s /q "`"$removing`""
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
