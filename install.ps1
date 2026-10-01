<#
.SYNOPSIS
Installs hello.py for all users in a folder only administrators can change.

.DESCRIPTION
Creates "Program Files\hello-world", where only Administrators and SYSTEM can
write. Copies hello.py there and writes hello.cmd next to it. Employees run
hello.cmd, which starts hello.py with the all-users Python 3 in isolated mode.

Run it from an elevated PowerShell on each workstation. Run it again after a
Python upgrade, because hello.cmd pins the interpreter's path.

.EXAMPLE
.\install.ps1
#>
#Requires -RunAsAdministrator
$ErrorActionPreference = 'Stop'
$dir = Join-Path $env:ProgramFiles 'hello-world'

# py -3 also picks per-user installs, which the employee can replace, so pin
# the newest all-users Python 3 from the PEP 514 registry keys instead.
$python = Get-ChildItem HKLM:\SOFTWARE\Python\PythonCore -ErrorAction SilentlyContinue |
    Where-Object PSChildName -match '^3\.\d+$' |
    Sort-Object { [version]$_.PSChildName } |
    Select-Object -Last 1 |
    ForEach-Object { (Get-ItemProperty "$($_.PSPath)\InstallPath").ExecutablePath }
# Folders under C:\ outside Program Files are often writable by every user.
if (-not $python -or -not $python.StartsWith("$env:ProgramFiles\")) {
    throw "Need Python 3 installed for all users under $env:ProgramFiles. Found: '$python'"
}

# Start from an empty folder so no access entry from an earlier copy survives.
if (Test-Path $dir) { Remove-Item $dir -Recurse -Force }
New-Item -ItemType Directory $dir | Out-Null
# Drop inherited entries. Administrators and SYSTEM get full control, Users
# get read and run. Files created below inherit this.
icacls $dir /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX' | Out-Null
if ($LASTEXITCODE) { throw "icacls failed on $dir" }

Copy-Item (Join-Path $PSScriptRoot 'hello.py') $dir
# -I ignores PYTHON* variables and the user's site-packages, so nothing the
# employee controls loads into the run.
Set-Content (Join-Path $dir 'hello.cmd') "@`"$python`" -I `"%~dp0hello.py`"" -Encoding ascii

$hash = (Get-FileHash (Join-Path $dir 'hello.py')).Hash
if ($hash -ne (Get-FileHash (Join-Path $PSScriptRoot 'hello.py')).Hash) { throw 'Installed hello.py differs from the source' }
$out = & (Join-Path $dir 'hello.cmd')
if ($LASTEXITCODE -or $out -ne 'Hello, world!') { throw "Test run failed with exit $LASTEXITCODE`: $out" }
"Installed to $dir with $python. hello.py SHA-256: $hash"
