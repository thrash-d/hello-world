#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print "Hello, world!" and one small useful thing each day.

On Windows the installer runs it through hello.cmd with its own pinned Python.
It shows a thought and a small thing to try, and can keep one plan for the day.
Everything it saves stays in one small file in the user's own folder, and
nothing is sent anywhere. Exit 0 when the text was written, 1 when stdout
could not be written, 2 for an unknown option.
"""
import datetime
import json
import os
import sys
import textwrap

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        "Sunday")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

# Chosen by date, so everyone sees the same line on the same day and the
# lists repeat every 100 days.
TIPS = (
    'Sip a glass of water slowly while you look out a window.',
    'Roll your shoulders back five times, nice and slow.',
    'Look at something far away for twenty seconds to rest your eyes.',
    'Stretch your arms overhead, seated or standing, and take a deep breath.',
    'Move to the farthest room or window you can reach, and back.',
    'Check your posture and let your shoulders drop away from your ears.',
    'Turn your neck gently side to side, only as far as feels easy.',
    'Open and close your hands ten times to loosen your fingers.',
    'Blink slowly ten times to refresh your eyes.',
    'Take a short walk or roll outside, whatever suits you.',
    'Pour a warm or cool drink and enjoy it away from your screen.',
    'Gaze at something green or calm for a quiet moment.',
    'Circle your wrists a few times in each direction.',
    'Plant both feet flat and sit tall, or stand tall, for ten breaths.',
    'Stretch your sides by leaning gently one way, then the other.',
    'Unclench your jaw and relax your forehead for a moment.',
    'Move around for two minutes in whatever way feels good today.',
    'Press your palms together and gently stretch your wrists.',
    'Adjust your screen so it sits comfortably at eye level.',
    'Take the long way to your next meeting or call, if you can.',
    'Wiggle your toes and ankles under your desk for a minute.',
    'Cup your palms over closed eyes for thirty seconds of calm dark.',
    'Drink a full glass of water before your next coffee or tea.',
    'Shrug your shoulders up to your ears, then let them melt down.',
    'Step outside or to a window for a minute of fresh air and daylight.',
    'Take five slow breaths, making each exhale a little longer.',
    'Pause for one quiet minute before you open your next message.',
    'Note one good thing that has happened so far today.',
    'Close your eyes for three breaths and notice how you feel.',
    'Name three things you can see, hear, and feel right now.',
    'Write down one thing you are looking forward to this week.',
    'Set a timer for two minutes and simply sit with no screen.',
    'Smile at something small, like a plant or a favorite mug.',
    'Think of one thing you did well this week and give yourself a nod.',
    'Listen to one favorite song, start to finish, with nothing else open.',
    'Breathe in for four counts and out for six, three times.',
    'Take one breath before reacting to the next small annoyance.',
    'Jot down one thing that made you laugh recently.',
    'Notice one pleasant sound around you and listen for a full minute.',
    'Recall a place you love and picture it for thirty seconds.',
    'Say "good enough for now" about one small task and move on.',
    'Write one sentence about something you are grateful for.',
    'Savor the next sip of your drink and notice the taste.',
    'Give yourself a mini break between two tasks before jumping in.',
    'Look for one thing today that turns out better than you expected.',
    'Choose one word for how you want the afternoon to feel.',
    'Let your thoughts drift for sixty seconds, then return to what is next.',
    'Notice your feet on the floor and feel steady for a moment.',
    'Remember one kind thing someone did for you and enjoy the memory.',
    'Jot down one idea you want to revisit later and let it rest.',
    'Tidy one small corner of your desk, just one.',
    'Reply to one message that has been waiting a while.',
    "Write tomorrow's top task on a sticky note or in your notes.",
    'Close the browser tabs you no longer need.',
    'Say thanks to a colleague for something they did recently.',
    'Archive five old emails you no longer need.',
    'Rename one messy file so you can find it easily later.',
    'Clear one or two stray files off your desktop.',
    'Delete one old reminder that no longer applies.',
    'Add a clear title to a document you open often.',
    'Cross off one small item on your to-do list.',
    'Unsubscribe from one newsletter you never read.',
    'Wipe your keyboard or screen with a soft cloth.',
    'Put a pen, notebook, and water where you can reach them easily.',
    'Draft a short note to future you about where you left off today.',
    'Pick the one task that matters most this afternoon and do it first.',
    'Empty the recycling or waste bin at your desk.',
    'Update one progress note so others can see where things stand.',
    'Sort your downloads folder by moving one handful of files.',
    'Set a reminder for one thing you tend to forget.',
    'Turn off one notification you do not really need.',
    'Bookmark one page you keep searching for.',
    'Write a two-line summary of a meeting while it is still fresh.',
    'Ask if one recurring meeting could be a little shorter.',
    'Name your single goal for the next hour and write it down.',
    'Ask a colleague how their day is going and really listen.',
    'Share a useful link with someone who might enjoy it.',
    'Say hello to someone you have not spoken with before.',
    'Send a quick thank-you note to someone who helped you lately.',
    'Wave or smile at a coworker on your next video call.',
    'Ask a teammate what they are looking forward to this week.',
    'Congratulate someone on a small win you noticed.',
    'Invite a colleague for a short chat over tea, coffee, or a call.',
    'Compliment a colleague on something specific they did well.',
    'Learn the name of someone you see often but do not know yet.',
    'Share a helpful tip with a teammate who may need it.',
    'Ask someone to recommend a song, show, or book.',
    'Check in with a colleague who has been quiet lately.',
    'Offer to help with one small thing if someone seems busy.',
    'Greet the next person you meet with a warm hello.',
    'Pass along a kind word you heard about a colleague.',
    'Ask a coworker what made their week easier.',
    'Send a friendly message to someone you used to work with.',
    'Thank someone who keeps shared spaces running smoothly.',
    'Introduce two colleagues who might enjoy meeting each other.',
    'Ask a teammate how you can make a handoff easier for them.',
    'Share a small, harmless joke with someone nearby.',
    'Add a little extra warmth to your next please and thank you.',
    'Ask a colleague what they enjoy doing outside of work.',
    'Listen fully to the next person who speaks to you, without multitasking.',
)

THOUGHTS = (
    'Open the one document you have been avoiding and read just the first paragraph.',
    'A ten-minute start is still a start, and it usually makes the next ten easier.',
    'You do not need the whole plan today, only a sensible first step.',
    'Write the ugly first sentence. It gives you something real to improve later.',
    'Clear one small corner of your desk and notice how much calmer the rest feels.',
    'Pick the smallest task on your list and finish it before you look at the others.',
    'Starting badly on a quiet morning beats waiting for a perfect moment that may not come.',
    'Put the first step in your calendar so it has a place to live.',
    'Big projects are mostly small afternoons stacked together, so aim for one afternoon.',
    'Name the very next action out loud, and let the rest of the list wait its turn.',
    'Some days your pace is slower than you would like, and that pace still counts.',
    'Talk to yourself the way you would talk to a new colleague in their first week.',
    'You are allowed to still be learning something you have done for years.',
    'A flat morning does not decide the afternoon. You can start again after lunch.',
    'Being tired is information, not a failing. Adjust the plan and carry on gently.',
    'Give yourself the same grace you so readily hand to others.',
    'Progress often looks like nothing for a while, then suddenly like a finished page.',
    'It is fine to need a second read before things make sense.',
    'You do not have to feel ready. Doing it nervously is still doing it.',
    "Today's version of your best may be smaller than yesterday's, and that is all right.",
    'Close the tabs you are not using. Your attention will thank you within minutes.',
    'One task, one window, twenty-five minutes. See how far a quiet stretch can go.',
    'Write down the stray thought that pops up, then return to what you were doing.',
    'Silence your phone for one hour and let the work have your full attention.',
    'Decide the one thing that would make today a good day, and protect time for it.',
    'Doing things one at a time is usually faster than it feels.',
    'A tidy list of three things beats a scattered list of twenty.',
    'Notice when your mind wanders, and bring it back without any scolding.',
    'Put the hardest task where your energy is best, even if that is not first thing.',
    'Headphones on, kettle filled, door closed. Set the scene and the focus follows.',
    'Step away from the screen for five minutes. You will come back a little clearer.',
    'Eat lunch away from your desk today. The inbox can wait for a sandwich.',
    'A short walk around the building counts as real work for your head.',
    'Looking out of a window for a minute is a fine use of a busy afternoon.',
    'Stretch your shoulders and unclench your jaw. You have held them up all morning.',
    "Leave on time tonight if you can. Tomorrow's you will be glad of the evening.",
    'Rest is part of the job, because tired people tend to make the same slip twice.',
    'Rest your eyes on something far away and let your shoulders drop.',
    'A proper break makes the second half of the day feel like a fresh start.',
    "Let the evening belong to you. Nothing in your inbox needs you at nine o'clock.",
    'Say thank you to someone today for a small thing they did without being asked.',
    'Most people are doing their best with more on their plate than you can see.',
    'Learn how a colleague takes their tea or coffee. It is a tiny gift to remember.',
    'If someone seems short with you, assume a hard day and not a verdict on you.',
    'Hold the door, share the biscuits, and let someone finish their sentence.',
    'A quick hello and a question about the weekend can be the nicest part of a morning.',
    'When a newcomer asks something obvious, remember that you once asked it too.',
    "Give credit out loud when a teammate's idea made your work better.",
    'Reply to a message with a bit of warmth. It costs nothing and lands softly.',
    'Check in with the person who has gone quiet in meetings lately.',
    'Finish the thing that is nearly done before you start something new.',
    'Done and good enough usually serves people better than perfect and still pending.',
    'Close one open loop today and notice the small relief that follows.',
    'The last ten percent is often just a few careful minutes. Give them today.',
    'Send the email that has been sitting in your drafts. It is probably fine as written.',
    'Mark it complete, take a breath, and let it count for something.',
    'A finished small thing is worth more than a half-finished big one.',
    "Before you log off, jot tomorrow's first step on a note so you can leave lighter.",
    'Reread once, fix what you spot, and then let it go out into the world.',
    'Ending the day with one tidy result makes the evening feel lighter.',
    'Asking a question early usually saves an hour of quiet struggling later.',
    'Most people enjoy being asked for their knowledge. Ask without apologizing.',
    'Saying "I am stuck" is a clear, useful sentence that colleagues can work with.',
    'Ask for what you need in plain words, and give people the chance to say yes.',
    'Two people looking at a problem often solve it faster than one person staring alone.',
    'You are not a burden for needing a hand. You are a teammate.',
    'Bring a specific question and the person you ask can give a specific answer.',
    'If the instructions are unclear, asking for clarity is part of doing the job properly.',
    'Offer help when you can and accept it when you need it. Both get easier with practice.',
    'Someone down the corridor has probably solved this before. Go and find them.',
    'Keep a small note of things you figured out this week. It adds up to more than you think.',
    'Being a beginner at something new is a sign your work is still growing.',
    'Watch how a colleague you admire handles a tricky call, and borrow one thing.',
    'Read one useful page on your break and call that a good day for your mind.',
    'Explaining a task to someone else is a surprisingly good way to learn it yourself.',
    'It is fine to say "I do not know that yet" and then go and find out.',
    'Every unfamiliar system looks confusing until you have used it a handful of times.',
    'Ask someone with more experience how they learned it. The answer is often reassuring.',
    'Skills come from repetition, so repeat the small thing and let it become easy.',
    'A little curiosity about an ordinary task can make it more interesting.',
    'A mistake caught early is just a correction, and most of them are caught early.',
    'Fix it, tell the people who need to know, and then let the sting fade.',
    'Nearly every error at work feels smaller in a week than it does in the moment.',
    'One slip does not erase the years of careful work behind you.',
    'When something goes wrong, look at the process first and the person second.',
    'Everyone around you has sent an email to the wrong person at least once.',
    'Take the one lesson a mistake offers and leave the rest of it behind.',
    'Owning an error plainly usually earns more trust than never having made one.',
    'A clumsy day happens to careful people too, and it passes by evening.',
    "You will not remember most of today's small stumbles by next month.",
    'A quiet day with nothing on fire is a good day, even if no one mentions it.',
    'Notice the small pleasures: a warm mug, a clear inbox, a sunny patch on the desk.',
    'Not every day needs a big win. Steady and pleasant is a fine way to work.',
    'Enjoy the meeting that ends five minutes early and spend the time as you like.',
    'An ordinary Tuesday done well is something quietly to be proud of.',
    'Good work often looks unremarkable from the outside, and that is all right.',
    'Let a pleasant afternoon be pleasant without waiting for it to be productive.',
    'The small routines of the day, the first coffee and the familiar faces, are worth noticing.',
    'Today you showed up and did your share, and that is plenty.',
    'Take a moment this evening to remember one thing that went well today.',
)

DONE_LINES = (
    "Good. That is one less thing to hold in your head.",
    "Nice. It is good to finish a thing.",
    "Well done. Take a moment before the next one.",
    "Good. Small finished things add up.",
    "That is done, and that is enough to be pleased about.",
    "Good. You can put that one down now.",
)

HELP = """hello-world prints a greeting, a thought, and a small thing to try.

At the end of the screen, type p for today's plan or m for options. You can also run hello.cmd
with one of these:
  --plain         Print only the greeting
  --stats         Show what is saved on this computer
  --reset         Delete everything saved (asks first)
  --remind on     Open once a day when you sign in (off to stop)
  --streak off    Hide the in-a-row line (on to show it)
  --help          Show this text

Saved notes stay on this computer, in your user folder. Nothing is sent
anywhere. IT staff who can read this computer's files could read them."""

MAX_VISITS = 400
MAX_FILE = 1_000_000
YES = ("y", "yes", "yep", "ya", "yeah", "done")
NO = ("n", "no", "nope", "not yet")

# The tests set these after importing the module, to run against a fixed date,
# a temporary folder, and typed input. Nothing outside the program sets them.
TODAY = None
HOME = None
STARTUP_DIR = None
FORCE_INTERACTIVE = False


class OutputClosed(Exception):
    """Writing to stdout failed, so nothing more can be shown."""


def today():
    return datetime.date.fromisoformat(TODAY) if TODAY else datetime.date.today()


def long_date(d):
    return f"{DAYS[d.weekday()]}, {d.day} {MONTHS[d.month - 1]} {d.year}"


def data_dir():
    if HOME:
        return HOME
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "hello-world")
    return os.path.join(os.path.expanduser("~"), ".local", "share",
                        "hello-world")


def data_file():
    return os.path.join(data_dir(), "notes.json")


def startup_file():
    folder = STARTUP_DIR
    if not folder and os.name == "nt" and os.environ.get("APPDATA"):
        folder = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows",
                              "Start Menu", "Programs", "Startup")
    return os.path.join(folder, "hello-world-daily.cmd") if folder else None


def new_state():
    return {"visits": [], "intent": None, "streak": True}


def clean(text):
    """One printable line: tabs and odd spaces become spaces, controls go."""
    text = "".join(" " if c.isspace() else c for c in text)
    # ZWNJ and ZWJ are Cf, not printable, but Persian, Indic scripts and emoji
    # sequences need them.
    text = "".join(c for c in text if c.isprintable() or c in "\u200c\u200d")
    return " ".join(text.split())[:120]


def day(value):
    """The date as a canonical string, or ValueError."""
    if not isinstance(value, str):
        raise ValueError("not a date")
    return datetime.date.fromisoformat(value).isoformat()


def load():
    """Read the saved file. Returns (state, can_save).

    A missing file or a damaged one gives a fresh start; a damaged file is kept
    as notes.json.bak. A file that exists but can't be read right now is left
    alone, so a locked file is never overwritten with an empty one.
    """
    state = new_state()
    path = data_file()
    try:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read(MAX_FILE + 1)
    except FileNotFoundError:
        return state, True
    except OSError:
        return state, False
    except ValueError:
        text = None
    try:
        if text is None or len(text) > MAX_FILE:
            raise ValueError("too big or not text")
        raw = json.loads(text)
        if not isinstance(raw, dict):
            raise ValueError("not an object")
    except (ValueError, RecursionError, MemoryError):
        try:
            os.replace(path, path + ".bak")
        except OSError:
            return state, False
        return state, True
    if raw.get("streak") is False:
        state["streak"] = False
    visits = []
    for v in raw["visits"] if isinstance(raw.get("visits"), list) else []:
        try:
            visits.append(day(v))
        except ValueError:
            pass
    # A visit dated after today (a wrong clock once) would sort last and hide
    # every real visit from "welcome back" and the trim.
    now = today().isoformat()
    state["visits"] = sorted(v for v in set(visits) if v <= now)[-MAX_VISITS:]
    intent = raw.get("intent")
    try:
        if isinstance(intent, dict) and isinstance(intent.get("text"), str):
            text = clean(intent["text"])
            if text:
                state["intent"] = {"text": text, "date": day(intent.get("date"))}
    except ValueError:
        pass
    return state, True


def save(state):
    try:
        os.makedirs(data_dir(), exist_ok=True)
        tmp = f"{data_file()}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, data_file())
        return True
    except OSError:
        try:
            os.remove(tmp)
        except (OSError, UnboundLocalError):
            pass
        return False


def say(text=""):
    try:
        print(text, flush=True)
    except (OSError, ValueError) as e:
        raise OutputClosed(e) from e


def indent(text):
    return "\n".join(textwrap.wrap(text, 68, initial_indent="  ",
                                   subsequent_indent="  "))


def interactive():
    if FORCE_INTERACTIVE:
        return True
    try:
        if sys.stdin is None or not sys.stdin.isatty():
            return False
    except (OSError, ValueError):
        return False
    if os.name != "nt":
        return True
    # Windows calls the NUL device a terminal too. Only a real console has a
    # console mode, so ask for one.
    import ctypes
    import msvcrt
    try:
        handle = msvcrt.get_osfhandle(sys.stdin.fileno())
    except (OSError, ValueError):
        return False
    from ctypes import wintypes
    try:
        get_mode = ctypes.WinDLL("kernel32", use_last_error=True).GetConsoleMode
        get_mode.argtypes = [wintypes.HANDLE, wintypes.LPDWORD]
        get_mode.restype = wintypes.BOOL
        return bool(get_mode(handle, ctypes.byref(wintypes.DWORD())))
    except (OSError, ctypes.ArgumentError, OverflowError, AttributeError):
        return False


def ask(prompt):
    """Return the typed text, or None when nobody can answer."""
    if not interactive():
        return None
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt, OSError):
        return None


def is_yes(text):
    return (text or "").lower().strip(" .!") in YES


def is_no(text):
    return (text or "").lower().strip(" .!") in NO


def wrapped(prefix, text):
    return textwrap.fill(prefix + text, 72, subsequent_indent="  ")


def in_a_row(visits, d):
    """Count visits back from today where each is within 3 days of the next."""
    days = [datetime.date.fromisoformat(v) for v in visits]
    days = [x for x in days if x <= d] + [d]
    days = sorted(set(days))
    n = 1
    for later, earlier in zip(days[:0:-1], days[-2::-1]):
        if (later - earlier).days > 3:
            break
        n += 1
    return n


def remind(on):
    path = startup_file()
    if not path:
        say("The sign-in reminder works on Windows only.")
        return
    if on:
        target = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "hello.cmd")
        if '"' in target or "%" in target:
            say("The reminder cannot be set up from this folder.")
            return
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="ascii", newline="") as f:
                f.write(f'@echo off\r\nstart "hello-world" "{target}" '
                        "--startup\r\n")
        except (OSError, UnicodeEncodeError):
            say("Could not set up the reminder.")
            return
        say("Done. hello-world will open once a day when you sign in.")
        say("To stop it, choose the reminder option again, or delete this file:")
        say("  " + path)
    else:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError:
            say("Could not remove the reminder. Delete this file:")
            say("  " + path)
            return
        say("Done. The sign-in reminder is off.")


def show_saved(state):
    d = today()
    recent = [v for v in state["visits"]
              if 0 <= (d - datetime.date.fromisoformat(v)).days <= 6]
    say("Saved on this computer in:")
    say("  " + data_file())
    say(f"Days you opened hello-world: {len(state['visits'])}"
        f" (last 7 days: {len(recent)})")
    if state["intent"]:
        say(wrapped("Your current plan: ", state["intent"]["text"]))
    say("After tidying, the file holds only this:")
    say(json.dumps(state, indent=2, ensure_ascii=False))


def reset(state):
    answer = ask("Delete all saved notes and dates on this computer? (y/n) > ")
    if not is_yes(answer):
        say("Nothing was deleted.")
        return False
    leftovers = [data_file(), data_file() + ".bak"]
    try:
        leftovers += [os.path.join(data_dir(), n)
                      for n in os.listdir(data_dir())
                      if n.startswith("notes.json.") and n.endswith(".tmp")]
    except OSError:
        pass
    for path in leftovers:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError:
            say("Could not delete the file. Delete this file yourself:")
            say("  " + path)
            return False
    state.clear()
    state.update(new_state())
    say("Done. Everything saved was deleted.")
    return True


def set_plan(state, can_save):
    old = state["intent"]
    iso = today().isoformat()
    if old and old["date"] == iso:
        say(wrapped("Your plan for today: ", old["text"]))
    text = clean(ask("Type today's plan (Enter keeps it as it is) > ") or "")
    if not text:
        say("Nothing changed.")
        return
    state["intent"] = {"text": text, "date": iso}
    if can_save and save(state):
        say("Done. Your plan for today is saved.")
    else:
        state["intent"] = old
        say("Could not save that on this computer.")


def menu(state, can_save=True):
    while True:
        say()
        say("Options")
        say("  1  Show what is saved on this computer")
        reminding = startup_file() and os.path.exists(startup_file())
        say("  2  Open once a day at sign-in: "
            + ("on" if reminding else "off") + " (change it)")
        say("  3  Show the in-a-row line: "
            + ("on" if state["streak"] else "off") + " (change it)")
        say("  4  Delete everything saved")
        say("  5  Help")
        say("  6  Set or change today's plan")
        say("  Enter  Close")
        choice = ask("Choose 1 to 6 > ")
        if not choice:
            return
        if choice == "1":
            show_saved(state)
        elif choice == "2":
            remind(not reminding)
        elif choice == "3":
            state["streak"] = not state["streak"]
            if can_save and save(state):
                say("Done. The in-a-row line is "
                    + ("on." if state["streak"] else "off."))
            else:
                state["streak"] = not state["streak"]
                say("Could not save that choice on this computer.")
        elif choice == "4":
            reset(state)
        elif choice == "5":
            say(HELP)
        elif choice == "6":
            set_plan(state, can_save)
        else:
            say("Please type a number from 1 to 6, or press Enter.")


def daily(startup):
    d = today()
    iso = d.isoformat()
    state, can_save = load()
    person = interactive()
    seen_today = iso in state["visits"]
    if startup and seen_today:
        return
    first = not state["visits"]
    intent = state["intent"]
    if intent and intent["date"] > iso:
        intent["date"] = iso  # the clock moved back; it is today's plan now
    if intent and (d - datetime.date.fromisoformat(intent["date"])).days > 14:
        intent = None

    say("Hello, world!")
    say(long_date(d))
    say()

    if first:
        say("Welcome. Each day this gives you one thought and one small thing")
        say("to try. It saves a few notes on this computer, in your own user")
        say("folder, and sends nothing anywhere. Do not type passwords or")
        say("private details. Others who can read this computer's files, such")
        say("as IT staff, could read the notes.")
        say("Type m at the end of this screen to see the options.")
        say()
    elif not seen_today:
        last = datetime.date.fromisoformat(state["visits"][-1])
        row = in_a_row(state["visits"], d)
        if (d - last).days > 7:
            say("Welcome back. Glad you are here.")
            say()
        elif state["streak"] and (row in (3, 7, 14) or row % 30 == 0):
            say(f"You have opened this {row} times in a row. Nice to see you.")
            say()

    if not seen_today and intent and intent["date"] < iso:
        say(wrapped("Last time you planned: ", intent["text"]))
        answer = ask("Did you do it? (y = yes, n = not yet, Enter = skip) > ")
        if answer is not None:
            if is_yes(answer):
                say(DONE_LINES[d.toordinal() % len(DONE_LINES)])
                intent = None
            elif is_no(answer):
                keep = ask("That is fine. Keep it for today? (y/n) > ")
                if is_no(keep):
                    intent = None
                else:
                    intent = {"text": intent["text"], "date": iso}
        say()

    say("Thought for today:")
    say(indent(THOUGHTS[(d.toordinal() + 37) % len(THOUGHTS)]))
    say()
    say("Try this today:")
    say(indent(TIPS[d.toordinal() % len(TIPS)]))
    say()

    if intent and intent["date"] == iso:
        say(wrapped("Your plan for today: ", intent["text"]))
        say()
    elif not seen_today:
        text = ask("What is one thing you want to get done today?\n"
                   "(Press Enter to skip) > ")
        if text:
            text = clean(text)
            if text:
                intent = {"text": text, "date": iso}
        say()

    # With nobody at the keyboard, such as a launch with no console, show the
    # screen but keep today's questions for the next real visit.
    if person:
        if not seen_today:
            state["visits"] = (state["visits"] + [iso])[-MAX_VISITS:]
        state["intent"] = intent
        if not can_save or not save(state):
            say("Your notes could not be saved on this computer. This screen "
                "still works.")

    answer = (ask("Press Enter to close, p for today's plan, m for options > ")
              or "").lower()
    if answer in ("p", "plan") and person:
        set_plan(state, can_save)
    elif answer in ("m", "menu"):
        menu(state, can_save)


def run(argv):
    argv = [a.lower() for a in argv]
    if argv in (["/?"], ["-?"], ["/help"], ["-help"], ["help"]):
        argv = ["--help"]
    if argv == ["--plain"]:
        say("Hello, world!")
        return 0
    if argv == ["--help"] or argv == ["-h"]:
        say(HELP)
        return 0
    if argv == ["--startup"]:
        daily(startup=True)
        return 0
    if not argv:
        daily(startup=False)
        return 0
    state, can_save = load()
    if argv == ["--stats"]:
        show_saved(state)
        return 0
    if argv == ["--reset"]:
        if not interactive():
            say("Deleting saved notes needs a person at the keyboard.")
            return 1
        reset(state)
        return 0
    if len(argv) == 2 and argv[0] == "--remind" and argv[1] in ("on", "off"):
        remind(argv[1] == "on")
        return 0
    if len(argv) == 2 and argv[0] == "--streak" and argv[1] in ("on", "off"):
        state["streak"] = argv[1] == "on"
        if can_save and save(state):
            say("Done. The in-a-row line is "
                + ("on." if state["streak"] else "off."))
        else:
            say("Could not save that choice on this computer.")
        return 0
    say("Unknown option. Here are the options.")
    say()
    say(HELP)
    return 2


def main():
    try:
        # print() silently does nothing when stdout is None (fd 1 closed at start).
        # A stdout object that was closed later raises ValueError instead.
        if sys.stdout is None:
            raise OutputClosed("stdout is closed")
        # A console that can't show a typed character prints ? instead of failing.
        for stream in (sys.stdout, sys.stderr):
            if stream is not None and hasattr(stream, "reconfigure"):
                try:
                    stream.reconfigure(errors="replace")
                except (OSError, ValueError) as e:
                    if stream is sys.stdout:
                        raise OutputClosed(e) from e
        return run(sys.argv[1:])
    except OutputClosed as e:
        try:
            print(f"hello.py: cannot write to stdout: {e} "
                  "(contact IT if this keeps happening)", file=sys.stderr,
                  flush=True)
        except Exception:
            pass
        # A failed write stays buffered, and the shutdown flush would fail
        # again and turn exit 1 into 120. _exit skips that flush.
        os._exit(1)
    except KeyboardInterrupt:
        return 1
    except Exception as e:
        try:
            print(f"hello.py: something went wrong ({type(e).__name__}). "
                  "Contact IT.", file=sys.stderr, flush=True)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
