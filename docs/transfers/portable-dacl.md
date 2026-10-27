# Transfer: a notes folder whose volume has no access list

On Windows, saving notes, the error log, and the local streak-note files
sets an access list on the folder and on the open file: the current user
and SYSTEM, protected, with inheritance on the folder. The shared handoff
folder is not given that list. Other people on that PC have to be able to
read the handoff notes. Unix mode is the control on every other system, and
the list is not attempted there.

A volume that refuses the list (a USB stick formatted so Windows cannot
store one, for example) still receives the notes. Reed Mallory does not
accept that residual.

## Who holds it

The operator who keeps the folder. The first refusal writes
`dacl-transfer.txt` once, next to the notes, and does not overwrite it:

```
This folder's volume refused an owner-only access list.
Reed Mallory does not accept that residual.
The operator who keeps this folder accepts it by writing a name
that is not Reed Mallory on the acceptor line.
acceptor:
```

The operator writes their name on the `acceptor:` line. A name that is Reed
Mallory is not the acceptor. The same file is written for a counts-server
secret when that process is running on Windows and the list is refused.
