# To do

On 2 October 2026 a six-voice panel debated the "Against the design on purpose" part of `BACKLOG.md` and the rest of the backlog: an engineer, an employee who would use it every morning, a salesperson, a profit maximizer, an IT and security admin, and a blind Narrator and NVDA user who also spoke for motor, ADHD and dyslexia needs. Each gave a position, read the other five, and argued back. This file is what survived the second round.

The panel confirmed every "against the design" decision but one: they want fewer finished plans read out after `done`. Most of the to-do items are things nobody had written down before.

## Agreed by the whole panel

### 1. Stop the review rounds and run the pilot

- Write a stop rule into `PLAN.md`: no review round without a code change or a report from a real user, and turn off the schedule that runs them.
- Set a 30-day kill metric: ask the five employees in person. If fewer than three open it most days, freeze the program as it is.
- At least one of the five uses NVDA, Magnifier or voice control. Ask them whether anything was read twice, out of order, or too long. Without that, the metric says nothing about the people the access work was for.
- Write the success criteria before the clock starts. Quotes for later use are fine, as long as the pilot doesn't feel like an ad shoot.

Why: the profit maximizer estimated 40 to 90 owner-hours of review against about 7 user-hours a year of use. The engineer and IT agreed that features rot fastest in an app with no users.

### 2. Make upgrades safe, on a spare PC

- Defer `Remove-Tree $old` and roll back when step 6 fails, and name the open windows in the rename error.
- Do a smoke run as a standard user after the install.

Why: a PC left with no working install is the one failure that costs a desk visit, and it costs more than every tip will ever save. Everyone put this in their top three except the accessibility user, who had no installer stake.

### 3. A content pass

- Give an "or" option to every tip and thought that assumes sight, the way "Take a short walk or roll" already does. Candidates: "Look at something far away for twenty seconds to rest your eyes", "Blink slowly ten times", "Cup your palms over closed eyes", "Adjust your screen so it sits comfortably at eye level", "Sip a glass of water slowly while you look out a window", "Step outside or to a window", and the thoughts "Looking out of a window for a minute", "Rest your eyes on something far away", "a sunny patch on the desk" and "Watch how a colleague you admire".
- Replace some stretches with practical work tips, such as turning off one notification, or clearing the downloads folder. By week three the stretches read like the posture poster in the break room.
- Say in the README that everyone gets the same tip on the same day. It makes the app a small shared thing, with no tracking.

### 4. A prompt and first-run pass

- End every prompt with "Enter to <outcome>" and drop "=", which a screen reader may speak as "equals". Today Enter is written as "Enter = keep" in some prompts and "press Enter to close" in others.
- One `say()` per sentence, wrapped by `wrapped()`. The expired-plan message ("Type same at the" / "plan prompt to bring it back.") and the first-run welcome are broken by hand, and a screen reader pauses at each break.
- One wording for "plan saved". Today it's "Saved. Your plan for today is in. Finished it later?..." in one place and "Saved. Tomorrow it will ask how this went." in another.
- Add one line at the top of the first run: "Press Enter to close, that's it." Day one is where people decide whether this is a chore.

### 5. Read out fewer finished plans

- After `done`, show the last three finished plans. Keep all seven in option 1.

Why: hearing seven lines after every `done` is the noisiest moment in the app.

### 6. Stop asking about an abandoned plan

- After two "not yet" answers, stop asking about that plan and let it fall back to `same`. The engineer's condition: work it out from fields already saved, so `commit()` gets no new key to merge.

Why: asking every morning about a plan someone gave up on is a guilt engine, which `PLAN.md` says the program avoids.

### 7. Engineer cleanups

- Add an automated two-window test: start process A with `subprocess.Popen`, leave it waiting at a prompt, run process B to the end, then finish A and check the file. Today `commit()` is proven only by a manual sandbox run.
- Add a test that freezes the set of `notes.json` keys. Any new key fails it until someone writes the merge test for that key.
- Drop the handling of visits dated after today. They exist only because a clock was wrong once. The cost is losing that one day. Today the cost is permanent code.

### 8. Shorter docs

- Cut the employee part of the README roughly in half. Long privacy text makes people think something is being hidden.
- Keep the "what is saved" paragraph in one place and link to it. Today the README, `PLAN.md` and the why-doc each have a copy, and a wrong privacy statement is worse than a bug.

## Later, when the problem shows up

- Write the commit hash and `InstallDate` into the Uninstall registry key, add a `QuietUninstallString` with `-Quiet`, and copy `install.log` to `%ProgramData%\hello-world\`, because the README tells admins to delete the setup folder that holds it. IT and the salesperson wanted these now. The profit maximizer and the engineer said to wait until someone needs them.
- Find launchers through the Known Folder API, but only if any of the five use OneDrive Known Folder Move or folder redirection.
- An offline install path that takes a pre-downloaded Python zip and source folder.
- Ctrl+C stays as it is, and the screen never mentions it. The engineer first wanted Ctrl+C to end the visit, then conceded. The accessibility user would accept two presses in a row ending it, so a stray single press only skips one prompt.

## Raised and dropped by the panel

These confirm the backlog's "against the design" section.

- A default sign-in offer set at install, `-OfferSignIn`: the salesperson withdrew it. A window that opens at sign-in steals focus while the screen reader announces the desktop, and IT doesn't want admin scripts writing sign-in behavior into user profiles.
- A "share my week" summary for HR: reporting with extra steps. The employee said the day HR is in the loop, they're out.
- A Friday line, "You finished 3 things this week": the employee who proposed it dropped it, because it's still a count.
- An export of finished plans: option 1 with `full` already shows the file to copy from.
- A schema version key, `"v": 1`: IT withdrew it. `load()` checking each field's type is the schema, so add a version when a migration needs one.
- A `last-error.txt` file: IT withdrew it. The shortcut's pause on error keeps the message on screen, and a crash path is a bad place to write to disk.
- Capping or warning about `.bak` copies: a cap is a delete path for user data, and the warning was withdrawn too.
- A paid, brandable content pack, MSI or Intune packaging, Authenticode signing, and per-site pricing: not at five free seats. That's a second job with no customers, and an update channel reopens the network question. If a return is wanted, the profit maximizer suggests writing up the hardened installer pattern as a post instead.
