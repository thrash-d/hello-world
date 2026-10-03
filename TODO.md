# To do

On 2 October 2026 a six-voice panel debated the "Against the design on purpose" part of `BACKLOG.md` and the rest of the backlog: an engineer, an employee who would use it every morning, a salesperson, a profit maximizer, an IT and security admin, and a blind Narrator and NVDA user who also spoke for motor, ADHD and dyslexia needs. Each gave a position, read the other five, and argued back. This file is what survived the second round, and what is still left of it.

The panel confirmed every "against the design" decision but one: they want fewer finished plans read out after `done`. Most of the to-do items are things nobody had written down before.

## Done in 1.19.0

Items 3 to 8 from the panel's list, plus the installer code for item 2:

- The content pass. Tips and thoughts that assumed sight now offer another way in. Six stretches became practical work tips, and the first run says everyone sees the same tip on the same day.
- The prompt pass. Every prompt ends with "Enter to <outcome>", prose is wrapped by paragraph instead of broken by hand, a saved plan has one wording, and the first run opens with "Press Enter at each question to skip it, and once more to close. That's it."
- After `done` and on welcome back, only the last three finished plans are read out. Option 1 lists all seven.
- A plan answered "not yet" twice is put away and kept for `same`.
- An automated test runs two real windows at once, a test freezes the saved keys, and visits dated after today are dropped instead of carried.
- The employee part of the README is shorter, and the README now holds the one list of what is saved.
- The installer keeps the old install until step 6 has worked and puts it back if step 6 fails during an upgrade. A rename that fails says how many hello-world windows are open. The Apps entry records the commit and install date and has a `QuietUninstallString`, and a copy of `install.log` stays in the install folder.
- `PLAN.md` now has the pilot, with an assistive-tech user and a day-30 check whose result steers the next review rounds.

## Still to do, by hand

1. A simulated 30-day pilot ran instead of waiting a month. `docs/PILOT.md` has what it found, and 1.20.0 answers it. A real pilot can still follow.
2. Check with a real NVDA user whether `>` at the end of each prompt is spoken as "greater". The simulated NVDA user said it is.

The spare-PC session passed for 1.19.0: upgrade from 1.18.0, a forced step 6 rollback, and a standard-user smoke run. `PLAN.md` records it.

## Later, when the problem shows up

- Find launchers through the Known Folder API, but only if any of the five use OneDrive Known Folder Move or folder redirection.
- An offline install path that takes a pre-downloaded Python zip and source folder.
- Ctrl+C stays as it is, and the screen never mentions it. The engineer first wanted Ctrl+C to end the visit, then conceded. The accessibility user would accept two presses in a row ending it, so a stray single press only skips one prompt.

## Ways the tool could earn money

A separate profit-minded review assumed all labor is free, so the tool itself has to earn. All figures are its estimates. It ranked these:

1. An org site license, free up to 10 seats and about $3 per seat per year above that, checked offline by a license file the installer reads. It needs a `LICENSE` and signed MSI or Intune packaging. It touches no privacy promise.
2. Paid support and deployment help for IT, about $1,000 to $3,000 per org per year.
3. The hardened installer sold as its own kit to people who ship small Python tools to Windows, about $299 to $999 one-time. It needs the payload split from the installer, which `PLAN.md` "Later" already describes.
4. Content packs that ship inside the installer (more or branded tips, a second language), about $500 to $2,000 per org per year. They need a content-file loader.
5. Audience-funded content: sponsors or a crowdfund pay for the next 100 tips or a translation.
6. Sponsored tips, worth nothing until there's an install base, since a sponsor can't measure anything. They break the "nothing artificial" spirit.
7. An opt-in HR usage dashboard, listed only to price it. It breaks "no network" and "nothing reported", and the review expects 30 to 60 percent of users to opt out.

Its pick is the site license with support alongside. In the first 30 days: write the license and a price sheet, build the signed package, run the admin test, and pitch 30 IT or HR buyers on a free 60-day pilot. It counts as working if at least 3 of 30 sign a letter of intent for 100 or more seats.

Two assumptions it says could make it wrong, each with a cheap test:

- Employees keep opening it. Ask the five pilot users on day 14 and day 30. If fewer than 3 still open it weekly, sell the installer kit instead.
- Buyers will pay per seat with no usage data. Send the price sheet to 15 buyers before building anything. If most say no, price per org instead, and sell "your staff won't feel watched" as the feature.

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
