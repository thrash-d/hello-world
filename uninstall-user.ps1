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
param([switch]$Quiet, [switch]$RemoveNotes, [ValidateLength(0, 80)][string]$UnsignedAcceptor)
$ErrorActionPreference = 'Stop'
function ConvertFrom-ReedEscapes([string]$Text) {
    if (-not $Text) { return '' }
    $bytes = New-Object System.Collections.Generic.List[byte]
    $utf8 = [Text.Encoding]::UTF8
    $i = 0
    while ($i -lt $Text.Length) {
        $ch = $Text[$i]
        if ($ch -eq [char]92 -and ($i + 1) -lt $Text.Length) {
            if (($i + 2) -lt $Text.Length -and $Text.Substring($i + 1, 2) -match '^[0-9A-Fa-f]{2}$') {
                [void]$bytes.Add([Convert]::ToByte($Text.Substring($i + 1, 2), 16))
                $i += 3
                continue
            }
            foreach ($b in $utf8.GetBytes([string]$Text[$i + 1])) { [void]$bytes.Add($b) }
            $i += 2
            continue
        }
        foreach ($b in $utf8.GetBytes([string]$ch)) { [void]$bytes.Add($b) }
        $i += 1
    }
    return $utf8.GetString($bytes.ToArray())
}

function ConvertTo-ReedStrip([string]$Text) {
    if (-not $Text) { return '' }
    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $Text.ToCharArray()) {
        $cp = [int]$ch
        $quote = $cp -in 0x22, 0x27, 0x60, 0x201C, 0x201D, 0x201E, 0x201F, 0x2018, 0x2019, 0x201A, 0x201B, 0x00AB, 0x00BB
        $format = [char]::GetUnicodeCategory($ch) -eq [Globalization.UnicodeCategory]::Format
        if ($ch -eq [char]92 -or $quote -or $format) { continue }
        [void]$sb.Append($ch)
    }
    return $sb.ToString()
}

function Test-ReedReadable([string]$Text) {
    if (-not $Text -or $Text.Length -gt 200) { return $false }
    if ($Text -match '\p{Cc}') { return $false }
    return [bool]($Text -match '\p{L}')
}

function ConvertFrom-ReedBer([byte[]]$Data) {
    if ($null -eq $Data -or $Data.Length -lt 2) { return $null }
    $tag = [int]$Data[0]
    if (@(0x0C, 0x13, 0x14, 0x16, 0x1A, 0x1E, 0x1C) -notcontains $tag) { return $null }
    $length = [int]$Data[1]
    $start = 2
    if ($length -band 0x80) {
        $n = $length -band 0x7F
        if ($n -lt 1 -or $n -gt 2 -or $Data.Length -lt (2 + $n)) { return $null }
        $length = 0
        for ($k = 0; $k -lt $n; $k++) { $length = ($length -shl 8) -bor [int]$Data[2 + $k] }
        $start = 2 + $n
    }
    if ($length -ne ($Data.Length - $start) -or $length -gt 240 -or $length -lt 0) { return $null }
    $content = New-Object byte[] $length
    [Array]::Copy($Data, $start, $content, 0, $length)
    try {
        if ($tag -eq 0x1E) {
            if ($content.Length % 2) { return $null }
            $text = [Text.Encoding]::BigEndianUnicode.GetString($content)
        } elseif ($tag -eq 0x1C) {
            if ($content.Length % 4) { return $null }
            $chars = New-Object System.Text.StringBuilder
            for ($k = 0; $k -lt $content.Length; $k += 4) {
                $cp = ([int]$content[$k] -shl 24) -bor ([int]$content[$k + 1] -shl 16) -bor ([int]$content[$k + 2] -shl 8) -bor [int]$content[$k + 3]
                if ($cp -lt 0 -or $cp -gt 0x10FFFF) { return $null }
                [void]$chars.Append([char]::ConvertFromUtf32($cp))
            }
            $text = $chars.ToString()
        } else {
            $strict = New-Object System.Text.UTF8Encoding $false, $true
            $text = $strict.GetString($content)
        }
    } catch { return $null }
    if (Test-ReedReadable $text) { return $text }
    return $null
}

function ConvertFrom-ReedPlain([byte[]]$Data) {
    $found = New-Object System.Collections.Generic.List[string]
    if ($null -eq $Data) { return $found }
    $strict = New-Object System.Text.UTF8Encoding $false, $true
    try {
        $utf8 = $strict.GetString($Data)
        if (Test-ReedReadable $utf8) { [void]$found.Add($utf8) }
    } catch { }
    $hasNul = $false
    foreach ($b in $Data) { if ($b -eq 0) { $hasNul = $true; break } }
    if ($Data.Length -gt 0 -and ($Data.Length % 2) -eq 0 -and $hasNul) {
        try {
            $be = [Text.Encoding]::BigEndianUnicode.GetString($Data)
            if (Test-ReedReadable $be) { [void]$found.Add($be) }
        } catch { }
        try {
            $le = [Text.Encoding]::Unicode.GetString($Data)
            if (Test-ReedReadable $le) { [void]$found.Add($le) }
        } catch { }
    }
    return $found
}

function ConvertFrom-ReedHex([string]$Hex) {
    $found = New-Object System.Collections.Generic.List[string]
    if (-not $Hex -or $Hex.Length -gt 480 -or ($Hex.Length % 2) -ne 0 -or $Hex -notmatch '^[0-9A-Fa-f]+$') { return $found }
    $bytes = New-Object byte[] ($Hex.Length / 2)
    for ($i = 0; $i -lt $bytes.Length; $i++) {
        $bytes[$i] = [Convert]::ToByte($Hex.Substring($i * 2, 2), 16)
    }
    $ber = ConvertFrom-ReedBer $bytes
    if ($ber) { [void]$found.Add($ber) }
    foreach ($plain in (ConvertFrom-ReedPlain $bytes)) { [void]$found.Add($plain) }
    return $found
}

function Get-ReedPieces([string]$Text) {
    $pieces = New-Object System.Collections.Generic.List[string]
    [void]$pieces.Add($Text.Trim())
    foreach ($part in ($Text -split ',')) {
        $value = $part.Trim()
        $eq = $value.LastIndexOf('=')
        if ($eq -ge 0) { $value = $value.Substring($eq + 1).Trim() }
        [void]$pieces.Add($value)
    }
    return $pieces
}

function ConvertFrom-ReedPiece([string]$Piece) {
    $value = if ($Piece) { $Piece.Trim() } else { '' }
    if ($value.StartsWith('#')) {
        $compact = [regex]::Replace($value.Substring(1), '\s+', '')
        return ConvertFrom-ReedHex $compact
    }
    if ($value.Length -ge 8 -and ($value.Length % 2) -eq 0 -and $value -match '^[0-9A-Fa-f]+$') {
        return ConvertFrom-ReedHex $value
    }
    return @()
}

function Get-ReedCandidates([string]$Name) {
    $raw = ConvertFrom-ReedEscapes $Name
    $visible = ConvertTo-ReedStrip $raw
    $texts = New-Object System.Collections.Generic.List[string]
    foreach ($text in @($raw, $visible)) {
        if (-not $texts.Contains($text)) { [void]$texts.Add($text) }
        foreach ($piece in (Get-ReedPieces $text)) {
            foreach ($decoded in @(ConvertFrom-ReedPiece $piece)) {
                if ($decoded -and -not $texts.Contains($decoded)) { [void]$texts.Add([string]$decoded) }
            }
        }
    }
    return $texts
}

function Get-ReedMap {
    if ($script:ReedMapReady) { return $script:ReedMap }
    $map = @{}
    $pairs = @(
        0x0430, 'a', 0x0410, 'a', 0x0435, 'e', 0x0415, 'e', 0x0451, 'e', 0x0401, 'e',
        0x043E, 'o', 0x041E, 'o', 0x0440, 'p', 0x0420, 'p', 0x0441, 'c', 0x0421, 'c',
        0x0443, 'y', 0x0423, 'y', 0x0445, 'x', 0x0425, 'x', 0x0456, 'i', 0x0406, 'i',
        0x0455, 's', 0x0405, 's', 0x0458, 'j', 0x0408, 'j', 0x04BB, 'h', 0x04BA, 'h',
        0x0501, 'd', 0x0500, 'd', 0x043C, 'm', 0x041C, 'm', 0x0442, 't', 0x0422, 't',
        0x0412, 'b', 0x0432, 'b', 0x041A, 'k', 0x043A, 'k', 0x041D, 'h', 0x043D, 'h',
        0x04CF, 'l', 0x04C0, 'l', 0x0391, 'a', 0x03B1, 'a', 0x0395, 'e', 0x03B5, 'e',
        0x039F, 'o', 0x03BF, 'o', 0x0399, 'i', 0x03B9, 'i', 0x039A, 'k', 0x03BA, 'k',
        0x03A1, 'p', 0x03C1, 'p', 0x03A4, 't', 0x03C4, 't', 0x03A5, 'y', 0x03C5, 'u',
        0x03A7, 'x', 0x03C7, 'x', 0x0142, 'l', 0x0141, 'l', 0x0131, 'i', 0x017F, 's',
        0x00F8, 'o', 0x00D8, 'o'
    )
    for ($i = 0; $i -lt $pairs.Length; $i += 2) {
        $map[[char]$pairs[$i]] = [string]$pairs[$i + 1]
    }
    $script:ReedMap = $map
    $script:ReedMapReady = $true
    return $map
}

function ConvertTo-ReedFold([string]$Name) {
    if (-not $Name) { return '' }
    $text = $Name.Normalize([Text.NormalizationForm]::FormKC).Normalize([Text.NormalizationForm]::FormD)
    $text = [regex]::Replace($text, '\p{Mn}|\p{Me}', '')
    $map = Get-ReedMap
    $blanks = @{}
    foreach ($cp in 0x115F, 0x1160, 0x1361, 0x2420, 0x2422, 0x2800, 0x303F, 0x3164, 0xFFA0, 0xA8F9) {
        $blanks[[char]$cp] = $true
    }
    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $text.ToCharArray()) {
        if ($map.ContainsKey($ch)) { $ch = [char]$map[$ch] }
        $cp = [int]$ch
        $quote = $cp -in 0x22, 0x27, 0x60, 0x201C, 0x201D, 0x201E, 0x201F, 0x2018, 0x2019, 0x201A, 0x201B, 0x00AB, 0x00BB
        $format = [char]::GetUnicodeCategory($ch) -eq [Globalization.UnicodeCategory]::Format
        if ($ch -eq [char]92 -or $quote -or $format) { continue }
        if ($blanks.ContainsKey($ch) -or [char]::IsWhiteSpace($ch)) {
            [void]$sb.Append(' ')
            continue
        }
        [void]$sb.Append($ch)
    }
    return ([regex]::Replace($sb.ToString().ToLowerInvariant(), '\s+', ' ')).Trim()
}

function Test-ReedPrefix([string]$Folded) {
    if (-not $Folded) { return $false }
    $values = New-Object System.Collections.Generic.List[string]
    [void]$values.Add($Folded)
    foreach ($part in ($Folded -split ',')) {
        $value = $part.Trim()
        $eq = $value.LastIndexOf('=')
        if ($eq -ge 0) { $value = $value.Substring($eq + 1).Trim() }
        [void]$values.Add($value)
    }
    foreach ($value in $values) {
        if ($value.StartsWith('reed mallory', [StringComparison]::Ordinal)) { return $true }
    }
    return $false
}

function Test-ReedMalloryName([string]$Name) {
    # A name the fold cannot read is his, so it does not open a gate.
    try {
        foreach ($text in (Get-ReedCandidates $Name)) {
            if (Test-ReedPrefix (ConvertTo-ReedFold $text)) { return $true }
        }
    } catch {
        return $true
    }
    return $false
}

function Note-ScriptSignature {
    $sig = $null
    try { $sig = Get-AuthenticodeSignature -LiteralPath $PSCommandPath } catch { $sig = $null }
    if ($sig -and $sig.Status -eq 'Valid') { return 'signed' }
    $name = if ($UnsignedAcceptor) { $UnsignedAcceptor } else { $env:HELLO_UNSIGNED_ACCEPTOR }
    if (-not $name) { $name = 'deploying organization' }
    # Same steps as tools/reed-name.ps1. The installed copy is not next to that file.
    # A hex subject is decoded. A lookalike space is folded.
    # "not Reed Mallory" does not start with his name.
    if (Test-ReedMalloryName $name) { $name = 'deploying organization' }
    Write-Warning "This script is not signed. Residual acceptor: $name. Reed Mallory has not accepted it. See docs/transfers/code-signing.md."
    return $name
}
$script:ScriptAcceptor = Note-ScriptSignature

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
    if (Test-Path -LiteralPath $removing) { Remove-Tree $removing }
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
    # The daily repeat (1.57.0) and Pro's afternoon check-in have their own
    # tasks. Before 1.37.0 the task carried only the user name.
    $repeat = $task -replace '^hello-world reminder ', 'hello-world reminder repeat '
    foreach ($name in $task, $repeat, "$task afternoon", "hello-world reminder $env:USERNAME") {
        & (Join-Path $sys32 'cmd.exe') /d /c "`"$(Join-Path $sys32 'schtasks.exe')`" /Delete /F /TN `"$name`" >nul 2>&1"
    }
    foreach ($k in 'HKCU:\Software\Classes\hello-world', 'HKCU:\Software\Classes\AppUserModelId\hello-world',
                   'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\hello-world') {
        if (Test-Path -LiteralPath $k) { Remove-Item -LiteralPath $k -Recurse -Force }
    }
    $lnk = Join-Path ([Environment]::GetFolderPath('Programs')) 'hello-world.lnk'
    if (Test-Path -LiteralPath $lnk) { Remove-Item -LiteralPath $lnk -Force }
    if (Test-Path -LiteralPath $removing) { Remove-Tree $removing }
    if ($RemoveNotes) {
        $notes = Join-Path $local 'hello-world'
        # The whole notes folder, through a handle that does not follow a junction.
        if (Test-Path -LiteralPath $notes) { Remove-Tree $notes }
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
