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
