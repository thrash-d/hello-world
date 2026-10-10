<#
.SYNOPSIS
Installs hello-world for the signed-in user only, without administrator rights.

.DESCRIPTION
For PCs where IT allows it, such as laptops on site days. Unzip the release
package anywhere, then run this from that folder with the package hash from
the release notes:

    powershell -NoProfile -ExecutionPolicy Bypass -File install-user.ps1 -PackageHash <package hash>

It checks SHA256SUMS against the hash and every file against SHA256SUMS.
Then it installs into %LOCALAPPDATA%\Programs\hello-world and adds
hello-world to this user's Start menu. Settings > Apps gets an entry with an
Uninstall button, for this user only.

The install folder is in the user's own profile, so the user, and any program
running as them, can change it. install.ps1 puts hello-world where only
administrators can change it; use that one wherever IT can.

Exit codes: 0 when installed, 1 for any failure. It refuses to run when
hello-world is already installed for all users.

.PARAMETER PackageHash
The package hash from the release notes: the SHA-256 of SHA256SUMS.

.PARAMETER Quiet
Prints only the result line.
#>
param(
    [Parameter(Mandatory)][ValidatePattern('^[0-9a-fA-F]{64}$')][string]$PackageHash,
    [switch]$Quiet
)
$ErrorActionPreference = 'Stop'
function Write-Info([string]$Text) { if (-not $Quiet) { Write-Host $Text } }
trap { Write-Host "FAILED: $($_.Exception.Message)"; exit 1 }

if (Test-Path -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world') {
    throw 'hello-world is already installed for everyone on this PC.'
}
$sys32 = [Environment]::SystemDirectory
$local = [Environment]::GetFolderPath('LocalApplicationData')
$dir = Join-Path $local 'Programs\hello-world'
$key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\hello-world'

# The package hash vouches for SHA256SUMS, and SHA256SUMS for every file.
$sumsFile = Join-Path $PSScriptRoot 'SHA256SUMS'
if (-not (Test-Path -LiteralPath $sumsFile -PathType Leaf)) { throw "$PSScriptRoot has no SHA256SUMS. Unzip the whole release package into this folder." }
if ((Get-FileHash -LiteralPath $sumsFile).Hash -ne $PackageHash) { throw "SHA256SUMS doesn't match -PackageHash." }
$listed = @{}
foreach ($line in Get-Content -LiteralPath $sumsFile) {
    if ($line -match '^([0-9a-f]{64})  ([A-Za-z0-9._-]+)$') { $listed[$Matches[2]] = $Matches[1] }
    elseif ($line) { throw "SHA256SUMS has a line it can't read: $line" }
}
$files = @('hello.py', 'uninstall-user.ps1', 'VERSION') + @($listed.Keys | Where-Object { $_ -like 'content*.json' -or $_ -like 'hello.*.json' })
foreach ($f in $files + 'python-embed.zip') {
    if (-not $listed.ContainsKey($f)) { throw "SHA256SUMS doesn't list $f." }
    $path = Join-Path $PSScriptRoot $f
    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-FileHash -LiteralPath $path).Hash -ne $listed[$f]) {
        throw "$f is missing or doesn't match SHA256SUMS. Use an unchanged copy of the release package."
    }
}
$version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'VERSION')).Trim()

# Built beside the old copy and swapped in, so a failure leaves it working.
$new = "$dir.new"
$old = "$dir.old"
foreach ($leftover in $new, $old) {
    if (Test-Path -LiteralPath $leftover) { & (Join-Path $sys32 'cmd.exe') /d /c rmdir /s /q "`"$leftover`"" }
}
New-Item -ItemType Directory $new -Force | Out-Null
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Archive\Microsoft.PowerShell.Archive.psd1')
Expand-Archive -LiteralPath (Join-Path $PSScriptRoot 'python-embed.zip') -DestinationPath (Join-Path $new 'python')
foreach ($pattern in '_sqlite3.pyd', 'sqlite3.dll') {
    Get-ChildItem -LiteralPath (Join-Path $new 'python') -Filter $pattern -Force | Remove-Item -Force
}
foreach ($f in $files) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $f) -Destination $new }
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
$out = & (Join-Path $new 'python\python.exe') -I (Join-Path $new 'hello.py') --plain
if ($LASTEXITCODE -or "$out" -ne 'Hello, world!') { throw "Test run failed with exit $LASTEXITCODE`: $out" }
if (Test-Path -LiteralPath $dir) { Rename-Item -LiteralPath $dir -NewName (Split-Path $old -Leaf) }
Rename-Item -LiteralPath $new -NewName (Split-Path $dir -Leaf)
if (Test-Path -LiteralPath $old) { & (Join-Path $sys32 'cmd.exe') /d /c rmdir /s /q "`"$old`"" }

$pythonw = Join-Path $dir 'python\pythonw.exe'
$lnk = Join-Path ([Environment]::GetFolderPath('Programs')) 'hello-world.lnk'
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = "-I `"$dir\hello.py`" --window"
$shortcut.Description = 'A daily thought and one small thing to try'
$shortcut.IconLocation = "$(Join-Path $dir 'python\python.exe'),0"
$shortcut.WorkingDirectory = $local
$shortcut.Save()

New-Item $key -Force | Out-Null
$uninstall = "`"$(Join-Path $sys32 'WindowsPowerShell\v1.0\powershell.exe')`" -NoProfile -ExecutionPolicy Bypass -File `"$dir\uninstall-user.ps1`""
$entry = @{
    DisplayName = 'hello-world'; DisplayVersion = $version; Publisher = 'IT Department'
    DisplayIcon = "$(Join-Path $dir 'python\python.exe'),0"; InstallLocation = $dir
    InstallDate = (Get-Date -Format 'yyyyMMdd'); PackageHash = $PackageHash.ToLower()
    UninstallString = $uninstall; QuietUninstallString = "$uninstall -Quiet"
}
foreach ($name in $entry.Keys) { New-ItemProperty $key -Name $name -Value $entry[$name] -Force | Out-Null }
foreach ($name in 'NoModify', 'NoRepair') { New-ItemProperty $key -Name $name -Value 1 -PropertyType DWord -Force | Out-Null }
Write-Host "Installed hello-world $version for $env:USERNAME in $dir."
exit 0
