<#
.SYNOPSIS
Reinstalls hello-world from a git release tag in one step.

.DESCRIPTION
Does what the README's "From a git clone" steps do, in one command. It
removes the setup folder and makes it again, so only administrators and
SYSTEM can change it. Then it clones the release tag into it and runs
install.ps1 with the reviewed commit. Run it as administrator:

    powershell -NoProfile -ExecutionPolicy Bypass -File reinstall.ps1 -Tag v1.35.0 -Commit <40-character hash>

Copy this script somewhere only administrators can write, not into the setup
folder it deletes. install.ps1 makes every check it always does; this only
saves typing.

.PARAMETER Tag
The release tag to clone, such as v1.35.0.

.PARAMETER Commit
The full commit hash that was reviewed. install.ps1 refuses any other.

.PARAMETER SetupDir
The setup folder. The default is Program Files\hello-setup.
#>
#Requires -RunAsAdministrator
param(
    [Parameter(Mandatory)][ValidatePattern('^v\d+\.\d+\.\d+$')][string]$Tag,
    [Parameter(Mandatory)][ValidatePattern('^[0-9a-f]{40}$')][string]$Commit,
    [string]$SetupDir = (Join-Path ([Environment]::GetFolderPath('ProgramFiles')) 'hello-setup')
)
$ErrorActionPreference = 'Stop'
$sys32 = [Environment]::SystemDirectory
if ($PSScriptRoot.StartsWith($SetupDir, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Copy reinstall.ps1 out of $SetupDir first; this deletes that folder."
}
$git = (Get-ItemProperty HKLM:\SOFTWARE\GitForWindows).InstallPath + '\cmd\git.exe'
if (Test-Path -LiteralPath $SetupDir) {
    if ((Get-Item -LiteralPath $SetupDir -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "$SetupDir is a link." }
    # Windows won't delete the folder a window is in, and git leaves read-only files.
    Set-Location ([Environment]::GetFolderPath('Windows'))
    & (Join-Path $sys32 'cmd.exe') /d /c rmdir /s /q "`"$SetupDir`""
    if (Test-Path -LiteralPath $SetupDir) { throw "Couldn't remove $SetupDir." }
}
New-Item -ItemType Directory $SetupDir | Out-Null
& (Join-Path $sys32 'icacls.exe') $SetupDir /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' | Out-Null
if ($LASTEXITCODE) { throw "icacls failed on $SetupDir" }
& $git clone -b $Tag --depth 1 https://github.com/thrash-d/hello-world $SetupDir
if ($LASTEXITCODE) { throw "git clone failed with exit $LASTEXITCODE" }
& (Join-Path $sys32 'WindowsPowerShell\v1.0\powershell.exe') -NoProfile -ExecutionPolicy Bypass -File (Join-Path $SetupDir 'install.ps1') -Commit $Commit
exit $LASTEXITCODE
