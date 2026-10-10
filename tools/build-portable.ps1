<#
.SYNOPSIS
Builds hello-world-portable.zip: hello-world with its own Python, no install.

.DESCRIPTION
For a personal PC where you'd rather not install anything: unzip anywhere you
can write, such as Documents or a USB stick, and double-click
"Start hello-world.cmd". No administrator, no registry, no Apps entry. Notes
are kept in the notes folder next to it, still locked to your Windows
account, and deleting the folder removes everything.

It is not a way around an employer's software rules: on a work PC, ask IT,
who can deploy the normal package with install.ps1 and Group Policy.

Uses the same pinned Python as install.ps1, checked against its SHA-256.

.PARAMETER OutFile
The zip to write. It must not exist yet.
#>
param(
    [Parameter(Mandatory)][string]$OutFile
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$src = Get-Content -Raw -LiteralPath (Join-Path $root 'install.ps1')
$url = [regex]::Match($src, "(?m)^\`$pyUrl = '([^']+)'").Groups[1].Value
$sha = [regex]::Match($src, "(?m)^\`$pySha256 = '([0-9A-Fa-f]{64})'").Groups[1].Value
if (-not $url -or -not $sha) { throw 'Could not read $pyUrl and $pySha256 from install.ps1.' }
if (Test-Path -LiteralPath $OutFile) { throw "$OutFile already exists." }

$stage = Join-Path ([IO.Path]::GetTempPath()) ([IO.Path]::GetRandomFileName())
$app = Join-Path $stage 'hello-world'
New-Item -ItemType Directory -Force $app | Out-Null
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $ProgressPreference = 'SilentlyContinue'
    $zip = Join-Path $stage 'python-embed.zip'
    Invoke-WebRequest $url -OutFile $zip -UseBasicParsing -TimeoutSec 300
    if ((Get-FileHash -LiteralPath $zip).Hash -ne $sha) { throw "The download from $url doesn't match the pinned SHA-256." }
    Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Archive\Microsoft.PowerShell.Archive.psd1')
    Expand-Archive -LiteralPath $zip -DestinationPath (Join-Path $app 'python')
    foreach ($f in @('hello.py', 'VERSION') + @(Get-ChildItem -LiteralPath $root -Filter 'hello.*.json' | ForEach-Object Name)) {
        Copy-Item -LiteralPath (Join-Path $root $f) -Destination $app
    }
    # This file tells hello.py to keep its notes in the notes folder beside it.
    [IO.File]::WriteAllText((Join-Path $app 'portable.txt'), "hello-world keeps its notes in the notes folder next to this file.`r`n")
    Set-Content -LiteralPath (Join-Path $app 'hello.cmd') -Value '@"%~dp0python\python.exe" -I "%~dp0hello.py" %*' -Encoding ascii
    Set-Content -LiteralPath (Join-Path $app 'Start hello-world.cmd') -Value '@start "" "%~dp0python\pythonw.exe" -I "%~dp0hello.py" --window' -Encoding ascii
    $out = & (Join-Path $app 'python\python.exe') -I (Join-Path $app 'hello.py') --plain
    if ($LASTEXITCODE -or "$out" -ne 'Hello, world!') { throw "Test run failed with exit $LASTEXITCODE`: $out" }
    Compress-Archive -Path $app -DestinationPath $OutFile
    Write-Output (Get-FileHash -LiteralPath $OutFile).Hash.ToLower()
}
finally { Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue }
