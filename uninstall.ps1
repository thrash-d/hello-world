<#
.SYNOPSIS
Removes hello-world: the install folder, the Start menu shortcut, and the
entry in Settings > Apps.

.DESCRIPTION
install.ps1 copies this into the install folder and registers it as the
Uninstall command in Settings > Apps. It asks for administrator rights when
it starts without them. -Quiet skips the Press Enter prompts.

Exit codes: 0 when removed, 1618 when an open hello-world window blocked it
(Intune and MECM retry that code later), and 1 for any other failure. Nothing
is changed when it exits 1618. Everything is written to
%WINDIR%\Logs\hello-world\uninstall.log, and the result goes to the
Application event log under the source hello-world.

Each user's sign-in reminder is turned off: the Run value of every signed-in
user, and every user's reminder task. Each user's saved notes stay in their
own profile, unless -RemoveNotes is given. Users can delete theirs with
Delete everything before the program is removed.

-RemoveNotes also deletes each profile's AppData\Local\hello-world files:
notes.json, its backups and temp copies, notes.lock and errors.log. Each
delete is through a directory handle opened without following a junction, so
a folder swapped for a link after the open is not the folder that is deleted.
An unsigned copy names the deploying organization as the residual acceptor.
Reed Mallory has not accepted that residual.
#>
param([switch]$Quiet, [switch]$RemoveNotes, [ValidateLength(0, 80)][string]$UnsignedAcceptor)
$ErrorActionPreference = 'Stop'
function Note-ScriptSignature {
    $sig = $null
    try { $sig = Get-AuthenticodeSignature -LiteralPath $PSCommandPath } catch { $sig = $null }
    if ($sig -and $sig.Status -eq 'Valid') { return 'signed' }
    $name = if ($UnsignedAcceptor) { $UnsignedAcceptor } else { $env:HELLO_UNSIGNED_ACCEPTOR }
    if (-not $name) { $name = 'deploying organization' }
    if ($name -match '^(?i)\s*reed mallory(\s|$)') { $name = 'deploying organization' }
    Write-Warning "This script is not signed. Residual acceptor: $name. Reed Mallory has not accepted it. See docs/transfers/code-signing.md."
    return $name
}
$script:ScriptAcceptor = Note-ScriptSignature
function Wait-Close { if (-not $Quiet) { Read-Host 'Press Enter to close' } }
# A 32-bit PowerShell sees Program Files (x86) and the 32-bit registry.
# Intune runs uninstall commands in one, so start again in the 64-bit one.
if (-not [Environment]::Is64BitProcess) {
    $native = Join-Path ([Environment]::GetFolderPath('Windows')) 'sysnative\WindowsPowerShell\v1.0\powershell.exe'
    if (-not (Test-Path -LiteralPath $native)) {
        Write-Host 'Run this from 64-bit PowerShell.' -ForegroundColor Red; Wait-Close; exit 1
    }
    $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath)
    if ($Quiet) { $argList += '-Quiet' }
    if ($RemoveNotes) { $argList += '-RemoveNotes' }
    & $native @argList
    exit $LASTEXITCODE
}
# Settings > Apps starts this as a standard user, and the elevated copy can
# inherit that user's environment variables, so ask Windows for the folders.
$winDir = [Environment]::GetFolderPath('Windows')
$sys32 = [Environment]::SystemDirectory

# Assert-NotLink stays. Remove-Tree, Remove-UserNotes and
# Remove-LegacyLauncher are the handle-based delete in tools/nofollow.ps1,
# copied here because this script runs alone from the install folder.
function Assert-NotLink([string]$Path) {
    if ((Get-Item -LiteralPath $Path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "$Path is a link." }
}

# Handle-based delete that does not follow a junction or a symlink.
# Embedded in install.ps1, uninstall.ps1 and uninstall-user.ps1. Those copies
# run from a folder that does not have tools\ next to them, so this file is
# the readable source and the scripts carry the same functions.
# A path delete after a check is the race Reed Mallory will not accept.

function Initialize-NoFollow {
    if ('HelloNoFollow' -as [type]) { return $true }
    $src = @'
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;

public static class HelloNoFollow {
    const uint FILE_READ_ATTRIBUTES = 0x80;
    const uint DELETE = 0x10000;
    const uint SYNCHRONIZE = 0x100000;
    const uint FILE_SHARE_READ = 1;
    const uint FILE_SHARE_WRITE = 2;
    const uint FILE_SHARE_DELETE = 4;
    const uint OPEN_EXISTING = 3;
    const uint FILE_FLAG_BACKUP_SEMANTICS = 0x02000000;
    const uint FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000;
    const uint FILE_ATTRIBUTE_REPARSE_POINT = 0x400;
    const uint FILE_ATTRIBUTE_DIRECTORY = 0x10;
    const uint FILE_ATTRIBUTE_NORMAL = 0x80;
    const uint FILE_OPEN = 1;
    const uint FILE_OPEN_REPARSE_POINT_OPT = 0x00200000;
    const uint FILE_SYNCHRONOUS_IO_NONALERT = 0x00000020;
    const uint FILE_DELETE_ON_CLOSE = 0x00001000;
    const uint OBJ_CASE_INSENSITIVE = 0x40;

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    static extern SafeFileHandle CreateFileW(string name, uint access, uint share, IntPtr sec, uint disp, uint flags, IntPtr template);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern bool GetFileInformationByHandle(SafeFileHandle h, out BY_HANDLE_FILE_INFORMATION info);

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    static extern int GetFinalPathNameByHandleW(SafeFileHandle h, System.Text.StringBuilder buf, int cch, uint flags);

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    static extern bool SetFileAttributesW(string name, uint attrs);

    [DllImport("ntdll.dll")]
    static extern int NtCreateFile(out IntPtr handle, uint access, ref OBJECT_ATTRIBUTES oa, ref IO_STATUS_BLOCK io,
        IntPtr alloc, uint attrs, uint share, uint disp, uint options, IntPtr ea, uint eaLen);

    [DllImport("ntdll.dll")]
    static extern int NtSetInformationFile(IntPtr handle, out IO_STATUS_BLOCK io, byte[] info, int len, int cls);

    [StructLayout(LayoutKind.Sequential)]
    struct IO_STATUS_BLOCK {
        public IntPtr Status;
        public IntPtr Information;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct UNICODE_STRING {
        public ushort Length;
        public ushort MaximumLength;
        public IntPtr Buffer;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct OBJECT_ATTRIBUTES {
        public int Length;
        public IntPtr RootDirectory;
        public IntPtr ObjectName;
        public uint Attributes;
        public IntPtr SecurityDescriptor;
        public IntPtr SecurityQualityOfService;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct BY_HANDLE_FILE_INFORMATION {
        public uint FileAttributes;
        public long CreationTime;
        public long LastAccessTime;
        public long LastWriteTime;
        public uint VolumeSerialNumber;
        public uint FileSizeHigh;
        public uint FileSizeLow;
        public uint NumberOfLinks;
        public uint FileIndexHigh;
        public uint FileIndexLow;
    }

    static BY_HANDLE_FILE_INFORMATION Info(SafeFileHandle h) {
        BY_HANDLE_FILE_INFORMATION info;
        if (!GetFileInformationByHandle(h, out info)) throw new IOException("could not read the open file");
        return info;
    }

    static bool IsReparse(SafeFileHandle h) {
        return (Info(h).FileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0;
    }

    static bool IsDir(SafeFileHandle h) {
        return (Info(h).FileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0;
    }

    public static SafeFileHandle OpenRoot(string path) {
        SafeFileHandle h = CreateFileW(path,
            FILE_READ_ATTRIBUTES | DELETE | SYNCHRONIZE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            IntPtr.Zero, OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT,
            IntPtr.Zero);
        if (h.IsInvalid) throw new IOException("could not open " + path);
        if (IsReparse(h)) { h.Dispose(); throw new IOException(path + " is a link."); }
        return h;
    }

    static SafeFileHandle OpenRelative(SafeFileHandle parent, string name, bool deleteOnClose) {
        IntPtr buf = Marshal.StringToHGlobalUni(name);
        IntPtr usPtr = IntPtr.Zero;
        bool held = false;
        parent.DangerousAddRef(ref held);
        try {
            UNICODE_STRING us = new UNICODE_STRING();
            us.Length = (ushort)(name.Length * 2);
            us.MaximumLength = (ushort)((name.Length + 1) * 2);
            us.Buffer = buf;
            usPtr = Marshal.AllocHGlobal(Marshal.SizeOf(typeof(UNICODE_STRING)));
            Marshal.StructureToPtr(us, usPtr, false);
            OBJECT_ATTRIBUTES oa = new OBJECT_ATTRIBUTES();
            oa.Length = Marshal.SizeOf(typeof(OBJECT_ATTRIBUTES));
            oa.RootDirectory = parent.DangerousGetHandle();
            oa.ObjectName = usPtr;
            oa.Attributes = OBJ_CASE_INSENSITIVE;
            IO_STATUS_BLOCK io = new IO_STATUS_BLOCK();
            IntPtr raw;
            uint options = FILE_OPEN_REPARSE_POINT_OPT | FILE_SYNCHRONOUS_IO_NONALERT;
            if (deleteOnClose) options |= FILE_DELETE_ON_CLOSE;
            int status = NtCreateFile(out raw,
                DELETE | FILE_READ_ATTRIBUTES | SYNCHRONIZE,
                ref oa, ref io, IntPtr.Zero, 0,
                FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                FILE_OPEN, options, IntPtr.Zero, 0);
            if (status < 0) throw new IOException("could not open " + name);
            return new SafeFileHandle(raw, true);
        } finally {
            if (usPtr != IntPtr.Zero) Marshal.FreeHGlobal(usPtr);
            Marshal.FreeHGlobal(buf);
            if (held) parent.DangerousRelease();
        }
    }

    public static void DeleteChild(SafeFileHandle parent, string name) {
        try {
            using (SafeFileHandle h = OpenRelative(parent, name, true)) { }
            return;
        } catch (IOException) { }
        SafeFileHandle held = null;
        try {
            held = OpenRelative(parent, name, false);
            if (!IsReparse(held)) {
                try { SetFileAttributesW(FinalPath(held), FILE_ATTRIBUTE_NORMAL); } catch (IOException) { }
            }
        } catch (IOException) {
            return;
        } finally {
            if (held != null) held.Dispose();
        }
        using (SafeFileHandle h = OpenRelative(parent, name, true)) { }
    }

    public static SafeFileHandle OpenChain(string root, string[] parts) {
        SafeFileHandle h = OpenRoot(root);
        foreach (string part in parts) {
            SafeFileHandle next;
            try { next = OpenRelative(h, part, false); }
            catch { h.Dispose(); throw; }
            if (IsReparse(next) || !IsDir(next)) {
                next.Dispose();
                h.Dispose();
                throw new IOException(part + " is a link.");
            }
            h.Dispose();
            h = next;
        }
        return h;
    }

    public static string FinalPath(SafeFileHandle h) {
        System.Text.StringBuilder sb = new System.Text.StringBuilder(1024);
        int n = GetFinalPathNameByHandleW(h, sb, sb.Capacity, 0);
        if (n <= 0 || n >= sb.Capacity) throw new IOException("could not name the open directory");
        return sb.ToString();
    }

    public static string[] Names(SafeFileHandle dir) {
        List<string> list = new List<string>();
        foreach (string full in Directory.GetFileSystemEntries(FinalPath(dir)))
            list.Add(Path.GetFileName(full));
        return list.ToArray();
    }

    public static bool IsEmpty(SafeFileHandle dir) {
        return Names(dir).Length == 0;
    }

    public static void DeleteOpen(SafeFileHandle h) {
        IO_STATUS_BLOCK io = new IO_STATUS_BLOCK();
        int status = NtSetInformationFile(h.DangerousGetHandle(), out io, new byte[] { 1 }, 1, 13);
        if (status < 0) throw new IOException("could not delete the open directory");
    }

    public static void DeleteTree(SafeFileHandle dir) {
        for (int pass = 0; pass < 8; pass++) {
            string[] names = Names(dir);
            if (names.Length == 0) return;
            foreach (string name in names) {
                using (SafeFileHandle child = OpenRelative(dir, name, false)) {
                    if (!IsReparse(child) && IsDir(child)) DeleteTree(child);
                }
                DeleteChild(dir, name);
            }
        }
        if (Names(dir).Length != 0) throw new IOException("the directory was not emptied");
    }
}
'@
    try {
        Add-Type -TypeDefinition $src -Language CSharp -ErrorAction Stop
        return $true
    }
    catch {
        Write-Warning "No-follow delete could not be loaded ($($_.Exception.Message)). Reed Mallory has not accepted a path delete."
        return $false
    }
}

function Remove-Tree([string]$Path) {
    # The open handle is the directory. A junction swapped in at this path
    # after the open is a different object and is not what gets deleted.
    if (-not (Initialize-NoFollow)) {
        throw "No-follow delete is unavailable, so $Path was left in place. The operator removes it. Reed Mallory has not accepted following a junction."
    }
    $root = $null
    try {
        $root = [HelloNoFollow]::OpenRoot($Path)
        [HelloNoFollow]::DeleteTree($root)
        [HelloNoFollow]::DeleteOpen($root)
    }
    finally {
        if ($root) { $root.Dispose() }
    }
    if (Test-Path -LiteralPath $Path) { throw "Couldn't remove $Path" }
}

function Remove-UserNotes([string]$ProfileDir) {
    if (-not (Initialize-NoFollow)) {
        Write-Warning "Notes under $ProfileDir were left in place. No-follow delete did not load. Reed Mallory has not accepted a path delete."
        return
    }
    $dir = $null
    try { $dir = [HelloNoFollow]::OpenChain($ProfileDir, [string[]]@('AppData', 'Local', 'hello-world')) }
    catch { return }
    try {
        foreach ($name in @([HelloNoFollow]::Names($dir))) {
            if ($name -in 'notes.json', 'notes.lock', 'errors.log', 'errors.log.old' -or $name -like 'notes.json.*') {
                [HelloNoFollow]::DeleteChild($dir, $name)
            }
        }
        if ([HelloNoFollow]::IsEmpty($dir)) { [HelloNoFollow]::DeleteOpen($dir) }
    }
    finally { $dir.Dispose() }
}

function Remove-LegacyLauncher([string]$ProfileDir) {
    if (-not (Initialize-NoFollow)) { return }
    $dir = $null
    try {
        $dir = [HelloNoFollow]::OpenChain($ProfileDir, [string[]]@('AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'))
    }
    catch { return }
    try {
        foreach ($name in @([HelloNoFollow]::Names($dir))) {
            if ($name -eq 'hello-world-daily.cmd' -or $name -like 'hello-world-daily.cmd.*.tmp') {
                [HelloNoFollow]::DeleteChild($dir, $name)
            }
        }
    }
    finally { $dir.Dispose() }
}

# Write-AppEvent duplicated in install.ps1; change both together.
function Write-AppEvent([int]$Id, [string]$Type, [string]$Message) {
    try {
        if (-not [Diagnostics.EventLog]::SourceExists('hello-world')) { New-EventLog -LogName Application -Source 'hello-world' }
        Write-EventLog -LogName Application -Source 'hello-world' -EventId $Id -EntryType $Type -Message $Message
    }
    catch { Write-Warning "Couldn't write to the event log: $($_.Exception.Message)" }
}

# Only values this program wrote: their data runs hello.py or hello.cmd with
# --startup. A value of that name pointing anywhere else is left alone.
function Remove-UserReminders {
    foreach ($sid in @(Get-ChildItem 'Registry::HKEY_USERS' -ErrorAction SilentlyContinue |
            Where-Object { $_.PSChildName -match '^S-1-(5-21|12-1)-[\d-]+$' } | ForEach-Object PSChildName)) {
        $run = "Registry::HKEY_USERS\$sid\Software\Microsoft\Windows\CurrentVersion\Run"
        $value = (Get-ItemProperty -LiteralPath $run -Name 'hello-world' -ErrorAction SilentlyContinue).'hello-world'
        # Only this install's: a per-user install keeps its own.
        if ($value -and $value -match 'hello\.(py|cmd)"? --startup$' -and $value -like "*$dir\*") {
            Remove-ItemProperty -LiteralPath $run -Name 'hello-world' -ErrorAction SilentlyContinue
        }
        # The notification's answer links and name, when they point here.
        $classes = "Registry::HKEY_USERS\$sid\Software\Classes"
        $link = (Get-ItemProperty -LiteralPath "$classes\hello-world\shell\open\command" -ErrorAction SilentlyContinue).'(default)'
        if ($link -and $link -like "*$dir\*") {
            foreach ($k in "$classes\hello-world", "$classes\AppUserModelId\hello-world") {
                Remove-Item -LiteralPath $k -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }
    $schtasks = Join-Path $sys32 'schtasks.exe'
    # Through cmd: Windows PowerShell 5.1 stops on any stderr from a native
    # command, and one bad task must not leave the rest.
    $cmd = Join-Path $sys32 'cmd.exe'
    $names = @(& $cmd /d /c "`"$schtasks`" /Query /FO CSV /NH /V 2>nul" | ConvertFrom-Csv -Header @(1..30) |
        Where-Object { $_.'2' -like '\hello-world reminder*' -and $_.'9' -like "*$dir\*" } | ForEach-Object { $_.'2' } | Sort-Object -Unique)
    foreach ($name in $names) { & $cmd /d /c "`"$schtasks`" /Delete /F /TN `"$name`" >nul 2>&1" }
}

$ps = Join-Path $sys32 'WindowsPowerShell\v1.0\powershell.exe'
$dir = Join-Path ([Environment]::GetFolderPath('ProgramFiles')) 'hello-world'
if ($PSScriptRoot -ne $dir) {
    Write-Host "Run this from $dir, not $PSScriptRoot." -ForegroundColor Red; Wait-Close; exit 1
}

# Settings > Apps starts this without elevation, so ask for it.
$me = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    try {
        $argList = '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`""
        if ($Quiet) { $argList += '-Quiet' }
        if ($RemoveNotes) { $argList += '-RemoveNotes' }
        # Waiting passes the elevated copy's exit code back, so -Quiet runs
        # from a management tool see whether the uninstall worked.
        $child = Start-Process $ps -Verb RunAs -ArgumentList $argList -Wait -PassThru
        exit $child.ExitCode
    }
    catch { Write-Host "Couldn't get administrator rights: $($_.Exception.Message) Ask IT to uninstall hello-world." -ForegroundColor Red; Wait-Close; exit 1 }
}

$logDir = Join-Path $winDir 'Logs\hello-world'
try {
    if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory $logDir | Out-Null }
    Assert-NotLink $logDir
    & (Join-Path $sys32 'icacls.exe') $logDir /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' | Out-Null
    Start-Transcript -LiteralPath (Join-Path $logDir 'uninstall.log') -Append | Out-Null
}
catch { Write-Warning "Couldn't start the uninstall log: $($_.Exception.Message)" }

$exitCode = 0
# The elevated window closes when the script ends, so hold it open to show the result.
try {
    # Windows won't delete a folder that is the current directory. Set both:
    # Set-Location may leave the process's own directory where it was.
    Set-Location $winDir
    [Environment]::CurrentDirectory = $winDir

    # Renamed aside first: if a hello-world window holds a file open, the
    # rename fails and nothing has changed yet, so the uninstall can
    # run again later.
    $removing = "$dir.removing"
    if (Test-Path -LiteralPath $dir) {
        Assert-NotLink $dir
        if (Test-Path -LiteralPath $removing) { Remove-Tree $removing }
        try { Rename-Item -LiteralPath $dir -NewName (Split-Path $removing -Leaf) }
        catch {
            # A file held open without delete sharing blocks the rename. That
            # passes, so the exit code asks the deployment tool to retry later.
            $exitCode = 1618
            $open = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path -like "$dir\*" })
            $names = ($open | ForEach-Object { "$($_.ProcessName) (process $($_.Id))" }) -join ', '
            $hint = if ($open) { " These hello-world programs are open: $names. Closing them may help." } else { '' }
            throw "A file in $dir is in use.$hint Nothing was changed. Try again later."
        }
    }

    # Old launchers in each profile, one profile at a time, so one bad profile
    # can't stop the rest.
    $profiles = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\*' -ErrorAction SilentlyContinue).ProfileImagePath
    foreach ($p in $profiles) {
        if (-not $p) { continue }
        try { Remove-LegacyLauncher ([Environment]::ExpandEnvironmentVariables($p)) }
        catch { Write-Warning "Couldn't check the old launcher in ${p}: $($_.Exception.Message)" }
        if ($RemoveNotes) {
            try { Remove-UserNotes ([Environment]::ExpandEnvironmentVariables($p)) }
            catch { Write-Warning "Couldn't remove the notes in ${p}: $($_.Exception.Message)" }
        }
    }
    $shared = Join-Path ([Environment]::GetFolderPath('CommonApplicationData')) 'hello-world'
    if ($RemoveNotes -and (Test-Path -LiteralPath $shared)) {
        try { Remove-Tree $shared }
        catch { Write-Warning "Couldn't remove the shift handoff notes in ${shared}: $($_.Exception.Message)" }
    }
    try { Remove-UserReminders }
    catch { Write-Warning "Couldn't remove every reminder: $($_.Exception.Message)" }

    $lnk = Join-Path ([Environment]::GetFolderPath('CommonPrograms')) 'hello-world.lnk'
    if (Test-Path -LiteralPath $lnk) { Remove-Item -LiteralPath $lnk }
    foreach ($f in "$dir.new", "$dir.old", "$dir.failed") {
        if (Test-Path -LiteralPath $f) { Remove-Tree $f }
    }
    if (Test-Path -LiteralPath $removing) {
        # Antivirus can hold a file for a moment.
        for ($try = 1; ; $try++) {
            try { Remove-Tree $removing; break }
            catch { if ($try -ge 5) { Write-Warning "Couldn't remove $removing. The next install clears it."; break }; Start-Sleep -Seconds 1 }
        }
    }
    $key = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\hello-world'
    if (Test-Path -LiteralPath $key) { Remove-Item -LiteralPath $key -Recurse }
    Write-Host 'hello-world is uninstalled.' -ForegroundColor Green
    if ($RemoveNotes) { Write-Host "Each user's saved notes were deleted." }
    else { Write-Host 'Each user keeps their own saved notes in AppData\Local\hello-world. They can delete that folder if they want.' }
    Write-AppEvent 1002 Information 'hello-world was uninstalled.'
}
catch {
    Write-Host "Uninstall failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Close any hello-world windows, then try again from Settings > Apps > Installed apps > hello-world > Uninstall. If it fails again, ask IT.'
    Write-AppEvent 1003 Error "hello-world uninstall failed: $($_.Exception.Message)"
    if (-not $exitCode) { $exitCode = 1 }
}
finally {
    Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    Wait-Close
}
exit $exitCode
