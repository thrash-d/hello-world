# Rollout kit

Text to adapt for the day hello-world reaches employees. Change the names in
angle brackets. `docs/ENTERPRISE.md` covers the deployment itself.

## Announcement email

Subject: A 20-second start to the day, if you want one

> Starting <date>, you'll find hello-world in your Start menu. Open it in the
> morning and you get a short thought, one small thing to try, and, if you
> like, one plan for the day. The next time you open it, it asks whether you
> did it. That's all.
>
> It's optional. Click Not today to skip it. Nothing is sent anywhere and
> nothing is reported to managers or IT. Your notes stay in a small file in
> your own user folder, which IT staff could read, so don't type passwords or
> private details. Options > My saved notes shows everything saved, and can
> delete it.
>
> Questions: <help desk contact>.

## Employee FAQ

- What is it? A small daily screen: a greeting, a thought, a tip, and an
  optional plan for the day.
- Do I have to use it? No. Nobody can see whether you do.
- How do I open it? Start menu, or type "hello-world" in Windows Search.
- How long does it take? About 20 seconds. Click Not today to skip it.
- Who sees my plans? Nobody is sent anything. The file sits in your own user
  folder, where IT staff could read it, like any file on a work PC.
- Can it remind me? Only if you say yes when it asks. Then a notification
  comes at your first sign-in of the day, only when there is a plan to ask
  about, and you answer with one click. Options in the window turns it off.
- How do I delete what it saved? Options > My saved notes > Delete everything saved.
- I don't want the thought and tip. Options > Show the thought and tip.
- Is it in my language? It follows the Windows display language: English, Spanish, French (France and Canada), Portuguese (Brazil and Portugal), German, Simplified Chinese, Japanese, Korean, Arabic and Hebrew.
  Options > Language picks another.
- Does it work with a screen reader? Yes. The window uses standard Windows
  buttons and labels, and was checked with Narrator, NVDA, JAWS, Magnifier
  and high contrast. The text screen, plain text read top to bottom, is there
  too: Options > Use the text screen.

## For privacy and records reviewers

Everything below can be checked on a test PC with `hello.cmd --stats`, which
prints the whole saved file.

- The program makes no network connections at any time.
- Each user has one file, `%LOCALAPPDATA%\hello-world\notes.json`. It holds
  the date they last opened the program (the last 60 days of dates only if
  they turned on the days-in-a-row message), one current plan,
  one unfinished earlier plan, a count of plans marked done, the plans
  finished in the last 14 days with dates, four settings, and the date of the last
  sign-in reminder. No names, computer names or times.
- The `DisablePlans` policy removes all plan text and counts, and
  `HideDaysInARow` keeps only the latest visit date. With both, the file holds
  one date and four settings.
- People delete everything themselves with menu option 4. Uninstalling leaves
  the files, since an administrator deleting inside user profiles could be
  redirected; use your own profile cleanup if required.
- Install and uninstall events are logged on the PC under
  `%WINDIR%\Logs\hello-world` and in the Application event log. Nothing about
  use is logged.

## For the help desk

The help desk table in `docs/ENTERPRISE.md` covers the common questions:
where the program and notes are, damaged files, exit code 1618, stopping the
sign-in opening, and removing someone's data.
