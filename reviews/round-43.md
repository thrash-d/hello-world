# Round 43 review

- Date: 2026-10-02
- Commit reviewed: 5aafefd (main, version 1.16.0)
- Agents that ran: one reviewer, pasted in by hand.
- Redactions: none needed.

## Part 1: findings

### Finding 1.1: high, key type pollution in state merging

In hello.py, load() sanitizes specific keys from notes.json (such as visits, finished, intent, done, streak), but unknown or arbitrary JSON keys present in notes.json are loaded into state via raw dict expansion or maintained during commit().

```python
for key in set(state) | set(base):
    if key in ("visits", "future", "done", "offer_skips", "finished"):
        continue
    if state.get(key) == base.get(key):
        continue
    ...
```

If a hostile or corrupted notes.json file contains unexpected keys or non-standard types (e.g., {"visits": [], "intent": null, "unknown_key": {"nested": "data"}}), commit() will attempt to merge and JSON-serialize arbitrary object trees without type assertions. Furthermore, modifying structural types via raw JSON hand-editing can lead to runtime TypeError exceptions during subsequent iteration or string formatting inside show_saved() or commit(), causing application crash on launch.

Fix: strictly sanitize and whitelist allowable dictionary keys when loading state from storage, discarding any unrecognized key-value pairs during load():

```python
ALLOWED_KEYS = {"visits", "future", "intent", "previous", "done", "finished", "streak", "offered", "offer_skips", "epoch"}
raw = {k: v for k, v in raw.items() if k in ALLOWED_KEYS}
```

### Finding 1.2: high, command injection and escaping risks in the remind() batch file

In hello.py, the remind() function constructs a .cmd batch launcher script written directly into the user's Startup folder:

```python
target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hello.cmd")
if any(c in target for c in '"%&^<>|!'):
    say("The reminder cannot be set up from this folder.")
    return False
```

While characters like %, &, ^, <, >, |, ! are checked on target, Windows batch script parsing (cmd.exe) exhibits edge-case behavior with other characters (such as @, ~, spaces, parenthesis (), commas ,, and equal signs =). If the directory path where hello-world is installed contains characters like ) or , (e.g., C:\Tools (x86)\hello-world), execution of hello-world-daily.cmd inside cmd.exe fails or parses commands incorrectly.

Fix: avoid creating raw .cmd text files inside the Windows Startup folder where command interpreter syntax parsing rules apply. Instead, write a standard .lnk shortcut file or use PowerShell/WScript to instantiate a Windows Shortcut object, or properly wrap paths with double-quotes while escaping all special Windows command-line delimiters.

```python
safe_target = os.path.abspath(target).replace('"', '""')
with open(path, "w", encoding="ascii", newline="") as f:
    f.write(f'@echo off\r\nstart "" "{safe_target}" --startup\r\n')
```

### Finding 1.3: medium, default Unix file permissions on temporary file creation

In hello.py, save():

```python
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
with os.fdopen(os.open(tmp, flags, 0o600), "w", encoding="utf-8") as f:
```

While 0o600 is specified in os.open, system umask settings can interfere if non-standard environments are used. Furthermore, on Windows platforms, os.open() ignores Unix mode octals (e.g., 0o600). On Windows, file permissions are inherited from the parent directory (data_dir()). If data_dir() was previously created by an external process without explicit DACL restrictions, notes.json may inherit permissive ACLs allowing local multi-user access on shared workstations.

Fix: explicitly set local directory access control when creating data_dir() on Windows platforms using DACLs or restrictive creation attributes.

### Finding 1.4: low, stale temporary files after an abrupt stop

In save(), temporary files are created with PID suffixes: tmp = f"{data_file()}.{os.getpid()}.tmp". If the process is terminated forcibly (SIGKILL or power loss) while writing, .tmp files accumulate in data_dir(). While reset() attempts cleanup of .tmp files, standard startup and normal operations do not prune stale .tmp files, resulting in unnecessary disk clutter over time.

Fix: add a lightweight stale temporary file cleanup routinely inside load() or during startup when initializing data_dir().

## Part 2: value and usability

1. Clarify target persona and value proposition. The program operates as a local daily prompt and tracker designed for workstation users. Expand productivity options to export completed tasks into common Markdown daily log formats (e.g., Obsidian or Logseq daily notes format). This integrates hello-world directly into modern knowledge-worker workflows.

2. Console encoding robustness. Terminal output replaces non-ASCII console display characters with ? on legacy codepages. Standardize output encoding auto-detection and fallback to Unicode UTF-8 streams (sys.stdout.reconfigure(encoding='utf-8')) across standard Windows ConHost and Windows Terminal sessions to natively render multi-language characters and emoji.

3. Multi-window conflict resolution notification. Concurrent windows merge states silently or overwrite non-conflicting keys without proactive visual feedback until menu actions. Provide explicit status warnings when active plan state changes are made by another background window, giving users immediate context on state sync events.
