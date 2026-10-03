<#
.SYNOPSIS
Builds the offline install package for a release.

.DESCRIPTION
Copies install.ps1, uninstall.ps1, hello.py and VERSION into -OutDir. Downloads
the Python zip that install.ps1 pins and checks it against the pinned SHA-256.
Writes SHA256SUMS and a CycloneDX bill of materials. Prints the package hash:
the SHA-256 of SHA256SUMS, which install.ps1 -PackageHash checks first.

The CI tests and the release workflow both run this, so the package that is
tested is the package that ships.

.PARAMETER OutDir
An empty or missing folder to build the package in.
#>
param([Parameter(Mandatory)][string]$OutDir)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$src = Get-Content -Raw -LiteralPath (Join-Path $root 'install.ps1')
$url = [regex]::Match($src, "(?m)^\`$pyUrl = '([^']+)'").Groups[1].Value
$sha = [regex]::Match($src, "(?m)^\`$pySha256 = '([0-9A-Fa-f]{64})'").Groups[1].Value
if (-not $url -or -not $sha) { throw 'Could not read $pyUrl and $pySha256 from install.ps1.' }
$version = (Get-Content -LiteralPath (Join-Path $root 'VERSION')).Trim()

if ((Test-Path -LiteralPath $OutDir) -and (Get-ChildItem -LiteralPath $OutDir -Force)) { throw "$OutDir is not empty." }
New-Item -ItemType Directory -Force $OutDir | Out-Null
foreach ($f in 'install.ps1', 'uninstall.ps1', 'hello.py', 'VERSION') {
    Copy-Item -LiteralPath (Join-Path $root $f) -Destination $OutDir
}

[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
$ProgressPreference = 'SilentlyContinue'
$zip = Join-Path $OutDir 'python-embed.zip'
Invoke-WebRequest $url -OutFile $zip -UseBasicParsing -TimeoutSec 300
if ((Get-FileHash -LiteralPath $zip).Hash -ne $sha) { throw "The download from $url doesn't match the pinned SHA-256." }

# One line per file, "<sha256>  <name>", in a fixed order, so the same inputs
# always give the same package hash.
$files = 'hello.py', 'install.ps1', 'python-embed.zip', 'uninstall.ps1', 'VERSION'
$sums = foreach ($f in $files) { '{0}  {1}' -f (Get-FileHash -LiteralPath (Join-Path $OutDir $f)).Hash.ToLower(), $f }
[IO.File]::WriteAllText((Join-Path $OutDir 'SHA256SUMS'), ($sums -join "`n") + "`n", [Text.Encoding]::ASCII)

$pyVersion = [regex]::Match($url, 'python-([0-9.]+)-embed').Groups[1].Value
$bom = [ordered]@{
    bomFormat    = 'CycloneDX'
    specVersion  = '1.5'
    version      = 1
    metadata     = [ordered]@{ component = [ordered]@{ type = 'application'; name = 'hello-world'; version = $version } }
    components   = @(
        [ordered]@{
            type    = 'application'
            name    = 'hello-world'
            version = $version
            hashes  = @([ordered]@{ alg = 'SHA-256'; content = (Get-FileHash -LiteralPath (Join-Path $OutDir 'hello.py')).Hash.ToLower() })
        },
        [ordered]@{
            type     = 'application'
            name     = 'python-embeddable-amd64'
            version  = $pyVersion
            purl     = "pkg:generic/python@$pyVersion"
            hashes   = @([ordered]@{ alg = 'SHA-256'; content = $sha.ToLower() })
            externalReferences = @([ordered]@{ type = 'distribution'; url = $url })
        }
    )
}
$bom | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OutDir 'sbom.cdx.json') -Encoding ascii

(Get-FileHash -LiteralPath (Join-Path $OutDir 'SHA256SUMS')).Hash.ToLower()
