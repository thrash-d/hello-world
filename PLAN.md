# Plan: value, usability and rollout

This plan answers two read-throughs of the program: a usability review and a
business value review. Each item shows its status. "Done" means it is in this
release. "Owner" means a person has to do it, because it needs a decision, a
Windows PC, or real employees. "Gated" means it waits on something named.

## Findings and what was done

### Employees

| Finding | Status |
|---|---|
| Shortcut has no icon or description | Done. It uses the Python icon and says what it does. |
| Name `hello-world` doesn't match the "hello" instruction | Done. The docs now say "hello-world". |
| Plain console window with no title | Done. The shortcut sets the title. |
| Error text reads like developer output | Done. The message ends with "contact IT if this keeps happening". |
| Double-clicking `hello.cmd` closes at once | Documented. See `BACKLOG.md` for why the file itself doesn't pause. |

### The person deploying it

| Finding | Status |
|---|---|
| No README | Done. `README.md`. |
| Placeholder text breaks when pasted | Done. The steps use `$tag` and `$commit` variables. |
| Permission checks are silent for minutes | Done. Numbered steps and a progress bar. |
| Failures print a raw error block | Done. One `FAILED:` line, details in `install.log`. |
| Success line is cluttered and out of date | Done. Version, new/reinstall/upgrade, a next step. |
| No unattended mode | Done. `-Quiet`, exit code 0 or 1. |
| Colors differ between installer and uninstaller | Done. Green for success, red for failure in both. |
| Apps entry is thin | Done. Publisher, icon and size added. |
| Reinstalling is awkward | Documented in the README. A helper is declined, see `BACKLOG.md`. |

### Uninstalling

| Finding | Status |
|---|---|
| Elevation prompt says "Windows PowerShell" | Documented in the README. Windows controls the name. |
| Failure message has no next step | Done. It says to close windows and retry, then ask IT. |

### Value and retention

| Recommendation | Status |
|---|---|
| Decide what the program is for | Done in `README.md`: it is a pilot of the deployment pipeline. |
| Define success measures | Below. |
| Pilot with two or three users and interview them | Owner. Phase 2. |
| Choose a real job for employees | Owner. Phase 2. |
| Place it where the work happens, make first run fast, make output change | Gated on the real job. |
| Separate the payload from the installer | Gated on a second payload. See `BACKLOG.md`. |
| Update path | Done as far as it is safe: the installer reports upgrades. |
| One-page rollout note | Done. `README.md`. |
| Stop further review rounds until a real payload exists | Owner. The schedule that runs them is outside this repo. |
| Don't engineer artificial retention | Done. Nothing was added that nags, autostarts or tracks use. |

## Phases

### Phase 1: this release (done)

README, plan, installer and uninstaller messages, shortcut and Apps entry
polish, `-Quiet`. Not tested on Windows. Before the five-PC rollout, run one
install, a reinstall, an interrupted install and an uninstall on a clean
Windows 10 or 11 PC with standard Git for Windows. Check the shortcut icon,
the progress bar, the `-Quiet` exit codes and the Apps entry by eye.

### Phase 2: choose a real job (owner)

1. Ask the five employees what they repeat daily or weekly that is slow or
   error-prone. Pick one task, such as a status submit, an incident
   quick-capture, a connectivity self-check or a device compliance lookup.
2. Replace `hello.py` with that tool, keeping the installer. Give it output
   that changes from day to day, so there is a reason to run it again.
3. Pin it to the taskbar by Group Policy if it is used daily.
4. Pilot with two or three willing users. Ask what they did, what confused
   them, and whether they would miss it.

### Phase 3: make it reusable (gated on a second payload)

When a second tool exists, split the payload from the installer so a new tool
needs no change to the security checks. Do this with two real payloads in
hand, so the split fits real needs, and test it on Windows.

## Success measures

- Rollout: installs that finish without error, out of five. Time to deploy per
  PC. Both come from `install.log` and the exit code.
- Adoption, once there is a real tool: employees who use it each week, out of
  five. Count it from the management tool's inventory or ask in the pilot
  interviews. Don't add tracking to the program.
- Value: minutes saved per use, as the pilot users estimate.

## Cost

About 25 review rounds went into the installer. Until a real payload exists,
more rounds buy little. Pause the schedule that runs them, or let it run only
when the code changes.
