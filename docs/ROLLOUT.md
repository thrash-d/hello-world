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
> It's optional. Press Enter at each question to skip it. Nothing is sent
> anywhere and nothing is reported to managers or IT. Your notes stay in a
> small file in your own user folder, which IT staff could read, so don't type
> passwords or private details. Type `menu` at the last prompt to see
> everything saved, or to delete it.
>
> Questions: <help desk contact>.

## Employee FAQ

- What is it? A small daily screen: a greeting, a thought, a tip, and an
  optional plan for the day.
- Do I have to use it? No. Nobody can see whether you do.
- How do I open it? Start menu, or type "hello-world" in Windows Search.
- How long does it take? About 20 seconds. Press Enter to skip any question.
- Who sees my plans? Nobody is sent anything. The file sits in your own user
  folder, where IT staff could read it, like any file on a work PC.
- Can it open by itself? Only if you say yes when it asks, or turn it on in
  the menu (option 2). Option 2 turns it off again.
- How do I delete what it saved? Menu option 4.
- I don't want the thought and tip. Menu option 8 hides them.
- Is it in my language? It follows the Windows display language: English,
  Spanish, French, Portuguese or German.
- Does it work with a screen reader? Yes. It's plain text, read top to bottom,
  and every prompt says what Enter does.

## For privacy and records reviewers

Everything below can be checked on a test PC with `hello.cmd --stats`, which
prints the whole saved file.

- The program makes no network connections at any time.
- Each user has one file, `%LOCALAPPDATA%\hello-world\notes.json`. It holds
  the dates they opened the program in the last 60 days, one current plan,
  one unfinished earlier plan, a count of plans marked done, the last seven
  finished plans with dates, and three settings. No names, computer names or
  times.
- The `DisablePlans` policy removes all plan text and counts, and
  `HideDaysInARow` keeps only the latest visit date. With both, the file holds
  one date and three settings.
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
