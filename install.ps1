<#
.SYNOPSIS
Installs hello.py for all users in a folder only administrators can change.

.DESCRIPTION
Creates "Program Files\hello-world", where only Administrators and SYSTEM can
write. Copies hello.py there and writes hello.cmd next to it. Employees run
hello.cmd, which starts hello.py with the all-users Python 3 in isolated mode.

Run it from an elevated PowerShell on each workstation, from a git clone of a
release tag in a folder only administrators can write. It refuses anything
else, such as an employee's Downloads folder, a clone at another commit, or a
file changed since checkout. Run it again after a Python upgrade, because
hello.cmd pins the interpreter's path.

.PARAMETER Commit
The full commit hash that was reviewed. The clone must be at this commit.

.EXAMPLE
$d = 'C:\ProgramData\hello-setup'; New-Item -ItemType Directory $d
$icacls = "$env:SystemRoot\System32\icacls.exe"; $git = "$env:ProgramFiles\Git\cmd\git.exe"
& $icacls $d /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F'
& $git clone -b <release tag> --depth 1 https://github.com/thrash-d/hello-world $d
cd $d; Set-ExecutionPolicy -Scope Process Bypass -Force
.\install.ps1 -Commit <reviewed commit hash>

Run each line on its own, in order, in one elevated window. Long lines wrap
when copied from a terminal and break the paste.

Locks the setup folder before cloning into it, so nobody else can add files
to the clone, then installs the reviewed commit. Pass the full commit hash,
never a tag name. The tools run by full path for the same reason the
installer pins them. Windows clients block scripts by default, so the
example allows them for this PowerShell window only.

.NOTES
The setup folder isn't needed after a successful install. The installer makes
nothing outside these two folders, so this elevated line uninstalls it:

cd C:\; Remove-Item "$env:ProgramFiles\hello-world", C:\ProgramData\hello-setup -Recurse -Force
#>
#Requires -RunAsAdministrator
param([Parameter(Mandatory)][ValidatePattern('^[0-9a-f]{40}$')][string]$Commit)
$ErrorActionPreference = 'Stop'
# A 32-bit PowerShell reads the 32-bit registry and Program Files (x86), so it
# would pin a different Python than the one checked here.
if (-not [Environment]::Is64BitProcess) { throw 'Run this from 64-bit PowerShell.' }
$dir = Join-Path $env:ProgramFiles 'hello-world'

# Rights that let someone swap a file or folder out: Delete, DeleteChild,
# WRITE_DAC, WRITE_OWNER, GENERIC_ALL. Editing a file adds WriteData,
# AppendData, and GENERIC_WRITE.
$swap = 0x10000 -bor 0x40 -bor 0x40000 -bor 0x80000 -bor 0x10000000
$edit = $swap -bor 0x2 -bor 0x4 -bor 0x40000000
# Administrators, SYSTEM, TrustedInstaller, and the admin running this.
$trusted = 'S-1-5-32-544', 'S-1-5-18', 'S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464',
    [Security.Principal.WindowsIdentity]::GetCurrent().User.Value

function Assert-AdminOnly([string]$Path, [int64]$Rights) {
    # Literal, because Git ships a file named "[.exe".
    $acl = Get-Acl -LiteralPath $Path
    $sid = [Security.Principal.SecurityIdentifier]
    # An owner can always rewrite the DACL, so a non-admin owner counts too.
    $others = @($acl.GetOwner($sid).Value) + @($acl.GetAccessRules($true, $true, $sid) |
        Where-Object { $_.AccessControlType -eq 'Allow' -and
            -not $_.PropagationFlags.HasFlag([Security.AccessControl.PropagationFlags]::InheritOnly) -and
            ([int64]$_.FileSystemRights -band $Rights) } |
        ForEach-Object { $_.IdentityReference.Value }) | Where-Object { $_ -notin $trusted }
    if ($others) { throw "Non-administrators can change $Path ($($others -join ', '))." }
}

# Everything this installer runs as admin comes from a folder tree: the clone,
# Git, and Python, whose standard library loads on every start. Nobody but
# administrators may change anything in the tree, and nobody may swap out a
# folder above it.
function Assert-AdminOnlyTree([string]$Root) {
    Write-Host "Checking permissions under $Root"
    foreach ($i in @(Get-Item -LiteralPath $Root -Force) + @(Get-ChildItem -LiteralPath $Root -Recurse -Force)) {
        # A link's own ACL says nothing about its target.
        if ($i.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "$($i.FullName) is a link." }
        Assert-AdminOnly $i.FullName $edit
    }
    # A drive root can't be deleted or renamed, so Delete on it doesn't matter.
    for ($p = (Get-Item -LiteralPath $Root -Force).Parent; $p; $p = $p.Parent) {
        Assert-AdminOnly $p.FullName ($(if ($p.Parent) { $swap } else { $swap -band -bnot 0x10000 }))
    }
}

# PATH can list folders employees can write, and a git or icacls found there
# would run as admin. Call both by full path.
$icacls = "$env:SystemRoot\System32\icacls.exe"
$gitDir = (Get-ItemProperty HKLM:\SOFTWARE\GitForWindows -ErrorAction SilentlyContinue).InstallPath
$git = "$gitDir\cmd\git.exe"
if (-not $git.StartsWith("$env:ProgramFiles\") -or -not (Test-Path $git)) {
    throw "Need Git for Windows installed for all users under $env:ProgramFiles. Found: '$git'"
}
Assert-AdminOnlyTree $gitDir

# Covers .git too, so nobody can plant git objects that fool the commit check.
Assert-AdminOnlyTree $PSScriptRoot

# The ACL checks show nobody else can change the clone. This shows the clone is
# the reviewed commit, so a moved tag or an edited file fails here.
$head = & $git -C $PSScriptRoot rev-parse HEAD
if ($LASTEXITCODE -or $head -ne $Commit) { throw "Source is at '$head', not the reviewed commit $Commit." }
foreach ($f in 'install.ps1', 'hello.py') {
    if ((& $git -C $PSScriptRoot hash-object $f) -ne (& $git -C $PSScriptRoot rev-parse "HEAD:$f")) { throw "$f differs from commit $Commit." }
}

# py -3 also picks per-user installs, which the employee can replace, so pin
# the newest all-users Python 3 from the PEP 514 registry keys instead.
$key = Get-ChildItem HKLM:\SOFTWARE\Python\PythonCore -ErrorAction SilentlyContinue |
    Where-Object PSChildName -match '^3\.\d+$' |
    Sort-Object { [version]$_.PSChildName } |
    Select-Object -Last 1
$python = if ($key) { (Get-ItemProperty "$($key.PSPath)\InstallPath").ExecutablePath }
# Folders under C:\ outside Program Files are often writable by every user.
# The path goes into a cmd line, so the pattern also rules out ", %, and &.
if ($python -notmatch "^$([regex]::Escape($env:ProgramFiles))\\Python3[\w.-]*\\python\.exe$") {
    throw "Need Python 3 installed for all users in $env:ProgramFiles\Python3*. Found: '$python'"
}
# Windows searches PATH for a DLL missing from the exe's folder, and a planted
# copy there would load as admin in the runs below. These four ship with every
# official 64-bit build.
$pyDlls = ('python{0}.dll' -f ($key.PSChildName -replace '\.')), 'python3.dll', 'vcruntime140.dll', 'vcruntime140_1.dll'
foreach ($f in $pyDlls) {
    if (-not (Test-Path (Join-Path (Split-Path $python) $f))) {
        throw "$f is missing next to $python. Repair that Python install first."
    }
}
Assert-AdminOnlyTree (Split-Path $python)
# Start it before touching the install folder, so a broken Python doesn't
# replace a working install with one that can't run.
& $python -I -c pass
if ($LASTEXITCODE) {
    throw ("$python won't start (exit 0x{0:X8}; 0xC0000135 means a missing DLL). Repair that Python install first." -f $LASTEXITCODE)
}

# Start from an empty folder so no access entry from an earlier copy survives.
if (Test-Path $dir) { Remove-Item $dir -Recurse -Force }
New-Item -ItemType Directory $dir | Out-Null
# Drop inherited entries. Administrators and SYSTEM get full control, Users
# get read and run. Files created below inherit this.
& $icacls $dir /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX' | Out-Null
if ($LASTEXITCODE) { throw "icacls failed on $dir" }

Copy-Item (Join-Path $PSScriptRoot 'hello.py') $dir
# -I ignores PYTHON* variables and the user's site-packages, so nothing the
# employee controls loads into the run.
Set-Content (Join-Path $dir 'hello.cmd') "@`"$python`" -I `"%~dp0hello.py`"" -Encoding ascii

$hash = (Get-FileHash (Join-Path $dir 'hello.py')).Hash
if ($hash -ne (Get-FileHash (Join-Path $PSScriptRoot 'hello.py')).Hash) { throw 'Installed hello.py differs from the source' }
$out = & (Join-Path $dir 'hello.cmd')
if ($LASTEXITCODE -or "$out" -ne 'Hello, world!') { throw "Test run failed with exit $LASTEXITCODE`: $out" }

# The test run above ran as admin, so check what employees get from the ACL.
foreach ($f in $dir, (Join-Path $dir 'hello.py'), (Join-Path $dir 'hello.cmd')) {
    Assert-AdminOnly $f $edit
    $usersRX = (Get-Acl $f).GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]) | Where-Object {
        $_.IdentityReference.Value -eq 'S-1-5-32-545' -and $_.FileSystemRights.HasFlag([Security.AccessControl.FileSystemRights]::ReadAndExecute) }
    if (-not $usersRX) { throw "Users can't read and run $f" }
}
"Installed to $dir with $python. hello.py SHA-256: $hash"
