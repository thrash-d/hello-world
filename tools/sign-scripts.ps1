<#
.SYNOPSIS
Signs the hello-world PowerShell scripts with the deploying organization's certificate.

.DESCRIPTION
Signs install.ps1, uninstall.ps1, install-user.ps1 and uninstall-user.ps1
with Authenticode SHA-256, then checks each signature with
Get-AuthenticodeSignature. Status must be Valid.

With -OutDir, the four scripts are copied there and the copies are signed.
Without -OutDir, the scripts in this repository are signed in place. The
git copies are unsigned until an operator who holds the organization's
certificate runs this. Reed Mallory does not hold that certificate, and a
subject that names him is refused.

docs/transfers/code-signing.md is the transfer for a copy that is still unsigned.

.PARAMETER CertificateThumbprint
40 hex digits. The certificate is in Cert:\CurrentUser\My or
Cert:\LocalMachine\My and has a private key.

.PARAMETER TimestampServer
An RFC 3161 timestamp server, so the signature stays valid after the
certificate expires. Leave it out only for a test certificate.

.PARAMETER OutDir
An empty or missing folder for the signed copies.
#>
param(
    [Parameter(Mandatory)][ValidatePattern('^[0-9A-Fa-f]{40}$')][string]$CertificateThumbprint,
    [string]$TimestampServer,
    [string]$OutDir
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'reed-name.ps1')
$root = Split-Path $PSScriptRoot -Parent
$names = @('install.ps1', 'uninstall.ps1', 'install-user.ps1', 'uninstall-user.ps1')
$cert = @(Get-ChildItem -Path "Cert:\CurrentUser\My\$CertificateThumbprint", "Cert:\LocalMachine\My\$CertificateThumbprint" -CodeSigningCert -ErrorAction SilentlyContinue)[0]
if (-not $cert) { throw "No code-signing certificate with thumbprint $CertificateThumbprint and a private key in CurrentUser\My or LocalMachine\My." }
# Fold spaces, then each name in the subject. "CN=Reed  Mallory" is still his.
if (Test-ReedMalloryName $cert.Subject) { throw 'Reed Mallory is not the signer. Use the deploying organization''s certificate.' }

$dest = $root
if ($OutDir) {
    if ((Test-Path -LiteralPath $OutDir) -and (Get-ChildItem -LiteralPath $OutDir -Force)) { throw "$OutDir is not empty." }
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
    $dest = $OutDir
    foreach ($name in $names) {
        Copy-Item -LiteralPath (Join-Path $root $name) -Destination (Join-Path $dest $name)
    }
}
foreach ($name in $names) {
    $path = Join-Path $dest $name
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing $path" }
    $sign = @{ FilePath = $path; Certificate = $cert; HashAlgorithm = 'SHA256' }
    if ($TimestampServer) { $sign.TimestampServer = $TimestampServer }
    $result = Set-AuthenticodeSignature @sign
    if ($result.Status -ne 'Valid') { throw "Signing $name gave status $($result.Status): $($result.StatusMessage)" }
    $check = Get-AuthenticodeSignature -LiteralPath $path
    if ($check.Status -ne 'Valid') { throw "Verify of $name gave status $($check.Status)." }
    Write-Host "Signed $name. Status Valid."
}
Write-Host 'Signed by the deploying organization. An unsigned copy still names that organization. Reed Mallory accepted nothing.'
