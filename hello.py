#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print "Hello, world!" and one small useful thing each day.

On Windows the installer runs it through hello.cmd with its own pinned Python.
It shows a thought and a small thing to try, and can keep one plan for the day.
Everything it saves stays in one small file in the user's own folder, and
nothing is sent anywhere. Exit 0 when the text was written, 1 when stdout
could not be written or a command (--reset, --stats, --remind, --streak)
failed, 2 for an unknown option.
"""
import collections
import copy
import datetime
import json
import os
import shutil
import sys
import textwrap
import time

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        "Sunday")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

# Chosen by date, so everyone sees the same line on the same day and the
# lists repeat every 100 days (the pairing much later).
TIPS = (
    'Sip a glass of water slowly, away from your screen.',
    'Roll your shoulders back five times, nice and slow.',
    'Rest your eyes for twenty seconds: look far away, or close them.',
    'Stretch your arms overhead, seated or standing, and take a deep breath.',
    'Move to the farthest room or window you can reach, and back.',
    'Check your posture and let your shoulders drop away from your ears.',
    'Turn your neck gently side to side, only as far as feels easy.',
    'Open and close your hands ten times to loosen your fingers.',
    'Pin the one document you open most so it is one click away.',
    'Take a short walk or roll outside, whatever suits you.',
    'Pour a warm or cool drink and enjoy it away from your screen.',
    'Rest your attention on something calm, a view, a sound or a texture.',
    'Write the next step on one task you left half done.',
    'Plant both feet flat and sit tall, or stand tall, for ten breaths.',
    'Mute one group chat you only ever skim.',
    'Unclench your jaw and relax your forehead for a moment.',
    'Move around for two minutes in whatever way feels good today.',
    'Block fifteen minutes in your calendar for the task you keep putting off.',
    'Adjust your chair, screen or keyboard so one thing sits more comfortably.',
    'Take the long way to your next meeting or call, if you can.',
    'Save a template for one email you write again and again.',
    'Learn one keyboard shortcut for the program you use most.',
    'Drink a full glass of water before your next coffee or tea.',
    'Shrug your shoulders up to your ears, then let them melt down.',
    'Step outside or open a window for a minute of fresh air.',
    'Take five slow breaths, making each exhale a little longer.',
    'Pause for one quiet minute before you open your next message.',
    'Note one good thing that has happened so far today.',
    'Close your eyes for three breaths and notice how you feel.',
    'Name three things you notice right now, with any sense.',
    'Write down one thing you are looking forward to this week.',
    'Set a timer for two minutes and simply sit with no screen.',
    'Enjoy something small nearby, like a plant or a favorite mug.',
    'Think of one thing you did well this week and give yourself a nod.',
    'Listen to one favorite song, start to finish, with nothing else open.',
    'Breathe in for four counts and out for six, three times.',
    'Take one breath before reacting to the next small annoyance.',
    'Jot down one thing that made you laugh recently.',
    'Notice one pleasant sound, scent or texture around you for a minute.',
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
    'Greet a coworker warmly at the start of your next call.',
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
    'If you can, silence your phone for an hour and give the work your full attention.',
    'Decide the one thing that would make today a good day, and protect time for it.',
    'Doing things one at a time is usually faster than it feels.',
    'A tidy list of three things beats a scattered list of twenty.',
    'Notice when your mind wanders, and bring it back without any scolding.',
    'Put the hardest task where your energy is best, even if that is not first thing.',
    'Headphones on, kettle filled, door closed. Set the scene and the focus follows.',
    'Step away from the screen for five minutes. You will come back a little clearer.',
    'Eat lunch away from your desk today. The inbox can wait for a sandwich.',
    'A short walk around the building counts as real work for your head.',
    'A minute away from the screen is a fine use of a busy afternoon.',
    'Stretch your shoulders and unclench your jaw. You may have held them up for hours.',
    "Leave on time tonight if you can. Tomorrow's you will be glad of the evening.",
    'Rest is part of the job, because tired people tend to make the same slip twice.',
    'Rest your eyes for a moment and let your shoulders drop.',
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
    'Notice how a colleague you admire handles a tricky call, and borrow one thing.',
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
    'Notice the small pleasures: a warm mug, a clear inbox, a quiet minute.',
    'Not every day needs a big win. Steady and pleasant is a fine way to work.',
    'Enjoy the meeting that ends five minutes early and spend the time as you like.',
    'An ordinary day done well is something quietly to be proud of.',
    'Good work often looks unremarkable from the outside, and that is all right.',
    'Let a pleasant afternoon be pleasant without waiting for it to be productive.',
    'The small routines of the day, the first coffee and the familiar faces, are worth noticing.',
    'Today you showed up and did your share, and that is plenty.',
    'Take a moment this evening to remember one thing that went well today.',
    'A quiet minute between two tasks is not wasted; it is how the next one starts well.',
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

At the last prompt, type plan for today's plan, done when you finish
it, or menu (or m) for options. Enter closes, and q, x and close
close it from any question. At a plan prompt, same brings back an
unfinished earlier plan. After done it lists your last 3 finished
plans. Menu option 1 shows all of them, option 7 forgets one, and
option 8 hides the thought and tip. At the menu, Enter goes back.
You can also run hello.cmd with one of these:
  --plain         Print only the greeting
  --stats         Show what is saved on this computer
  --reset         Delete everything saved (asks first)
  --remind on     Open once a day when you sign in (off to stop)
  --streak off    Hide the in-a-row line (on to show it)
  --version       Show the version
  --help          Show this text

Exit codes: 0 when it worked, 1 when a command failed or the screen
could not be written, 2 for an unknown option.

Saved notes stay on this computer, in your user folder. Nothing is sent
anywhere. IT staff who can read this computer's files could read them."""

MENU_HELP = """Words you can type at the last prompt:
  done  marks today's plan finished, then asks for the next one
  plan  sets or changes today's plan
  menu  opens these options
  q     closes the window, and so does Enter
At a plan prompt, same brings back your earlier unfinished plan.
When it asks "Did you do it?", n means not yet, and you can keep the
plan for today. q closes from any question.
In this menu, 1 shows what is saved, 7 forgets one finished plan,
and 8 hides the thought and tip.
Type m to hear the options again. Nothing is sent anywhere."""


# A thought that shares one of these with the day's tip moves on by one, so
# one screen never has two lines about the same body part.
TOPICS = ("shoulder", "jaw", "neck", "eye", "water", "breath", "posture",
          "stretch", "wrist")


def todays_pair(d):
    """The day's thought and tip. Everyone gets the same pair on the same day."""
    tip = TIPS[d.toordinal() % len(TIPS)]
    i = (d.toordinal() + 37) % len(THOUGHTS)
    while any(w in tip.lower() and w in THOUGHTS[i].lower() for w in TOPICS):
        i = (i + 1) % len(THOUGHTS)
    return THOUGHTS[i], tip


def help_text():
    here = os.path.dirname(os.path.abspath(__file__))
    return HELP + "\n\nhello.cmd is in this folder:\n  " + here

VERSION = "1.21.0"
MAX_VISITS = 400
MAX_FILE = 1_000_000
YES = ("y", "yes", "yep", "ya", "yeah", "done")
# The sign-in offer starts something, so a stray "done" must not count.
STRICT_YES = ("y", "yes", "yep", "ya", "yeah")
MAX_OFFER_SKIPS = 1
NO = ("n", "no", "nope", "not yet")

# The tests set these after importing the module, to run against a fixed date,
# a temporary folder, and typed input. Nothing outside the program sets them.
TODAY = None
HOME = None
STARTUP_DIR = None
FORCE_INTERACTIVE = False


class Quit(Exception):
    """The person typed q at a question, so the window closes."""


QUIT_WORDS = ("q", "quit", "exit", "x", "close")


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
    # The tests set "" for no Startup folder, so they never touch the real one.
    folder = STARTUP_DIR
    if folder is None and os.name == "nt" and os.environ.get("APPDATA"):
        folder = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows",
                              "Start Menu", "Programs", "Startup")
    return os.path.join(folder, "hello-world-daily.cmd") if folder else None


def new_state():
    return {"visits": [], "intent": None, "streak": True}


MAX_PLAN = 120
SAVED_PLAN = "Saved. Type done when you finish it, or it asks next time you open this."
MAX_FINISHED = 7
SHOWN_AFTER_DONE = 3


def tidy(text):
    """One printable line: tabs and odd spaces become spaces, controls go."""
    text = "".join(" " if c.isspace() else c for c in text)
    # ZWNJ and ZWJ are Cf, not printable, but Persian, Indic scripts and emoji
    # sequences need them.
    text = "".join(c for c in text if c.isprintable() or c in "\u200c\u200d")
    text = " ".join(text.split())
    # Nothing but joiners would show as an empty plan.
    return text if text.strip("\u200c\u200d ") else ""


def clean(text):
    return tidy(tidy(text)[:MAX_PLAN].rstrip(" \u200c\u200d"))


def typed_plan(raw):
    """Clean a typed plan, and say so when it is cut."""
    if len(tidy(raw)) > MAX_PLAN:
        say(f"Shortened to {MAX_PLAN} characters.")
    return clean(raw)


def day(value):
    """The date as a canonical string, or ValueError."""
    if not isinstance(value, str):
        raise ValueError("not a date")
    return datetime.date.fromisoformat(value).isoformat()


def backup_name(path):
    """notes.json.bak, or a numbered name when an earlier backup exists."""
    name, n = path + ".bak", 1
    while os.path.exists(name):
        n += 1
        name = f"{path}.bak{n}"
    return name


def load(repair=True):
    """Read the saved file. Returns (state, can_save).

    A missing file or a damaged one gives a fresh start; a damaged file is kept
    as notes.json.bak. A file that exists but can't be read right now is left
    alone, so a locked file is never overwritten with an empty one. With
    repair=False a damaged file is left where it is and can_save is False.
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
        if not repair:
            return state, False
        backup = backup_name(path)
        try:
            os.replace(path, backup)
        except OSError:
            return state, False
        say(textwrap.fill("Your saved file was damaged, so hello-world set it "
                          "aside as a backup copy and started fresh. Your "
                          "earlier days and plan could not be read. Menu "
                          "option 4 deletes the backup.", 72,
                          break_on_hyphens=False, break_long_words=False))
        say("Backup copy: " + os.path.basename(backup))
        say("In the folder: " + data_dir())
        say()
        return state, True
    if raw.get("streak") is False:
        state["streak"] = False
    if raw.get("tips") is False:
        state["tips"] = False
    if raw.get("offered") is True:
        state["offered"] = True
    # Changes only when everything is deleted. commit() compares it, so a
    # window opened before a delete can't write its old notes back.
    epoch = raw.get("epoch")
    state["epoch"] = epoch if isinstance(epoch, str) and len(epoch) <= 64 else ""
    skips = raw.get("offer_skips")
    if isinstance(skips, int) and not isinstance(skips, bool) and skips > 0:
        state["offer_skips"] = min(skips, MAX_OFFER_SKIPS)
    prev = raw.get("previous")
    if isinstance(prev, str) and clean(prev):
        state["previous"] = clean(prev)
    n = raw.get("done")
    if isinstance(n, int) and not isinstance(n, bool) and n > 0:
        state["done"] = min(n, 99999)
    visits = []
    for v in raw["visits"] if isinstance(raw.get("visits"), list) else []:
        try:
            visits.append(day(v))
        except ValueError:
            pass
    # A visit dated after today comes from a clock that was wrong once. It
    # would sort last and hide every real visit, so it is dropped.
    now = today().isoformat()
    state["visits"] = sorted(v for v in set(visits) if v <= now)[-MAX_VISITS:]
    intent = raw.get("intent")
    try:
        if isinstance(intent, dict) and isinstance(intent.get("text"), str):
            text = clean(intent["text"])
            if text:
                state["intent"] = {"text": text, "date": day(intent.get("date"))}
                # The day it was first set, kept while it is carried over.
                try:
                    since = day(intent.get("since"))
                    if since < state["intent"]["date"]:
                        state["intent"]["since"] = since
                except ValueError:
                    pass
                skips = intent.get("skips")
                if isinstance(skips, int) and not isinstance(skips, bool) and 0 < skips < 10:
                    state["intent"]["skips"] = skips
    except ValueError:
        pass
    finished = []
    # A hostile file could fill the screen with far-off dates.
    latest = (today() + datetime.timedelta(days=365)).isoformat()
    for item in (raw.get("finished") if isinstance(raw.get("finished"), list)
                 else []):
        try:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                text = clean(item["text"])
                when = day(item.get("date"))
                if text and "2000-01-01" <= when <= latest:
                    finished.append({"text": text, "date": when})
        except ValueError:
            pass
    if finished:
        state["finished"] = finished[-MAX_FINISHED:]
    return state, True


def file_form(state):
    """What goes in the file: the state, holding at most MAX_VISITS dates."""
    out = {k: v for k, v in state.items() if not (k == "epoch" and not v)}
    out["visits"] = sorted(set(state["visits"]))[-MAX_VISITS:]
    return out


def sweep_tmp():
    """Remove temp copies left by a save that was killed partway.

    Only copies a day old go, so another window's save in progress is never
    touched.
    """
    try:
        names = os.listdir(data_dir())
    except OSError:
        return
    for name in names:
        if name.startswith("notes.json.") and name.endswith(".tmp"):
            path = os.path.join(data_dir(), name)
            try:
                if time.time() - os.path.getmtime(path) > 86400:
                    os.remove(path)
            except OSError:
                pass


def save(state):
    sweep_tmp()
    try:
        os.makedirs(data_dir(), mode=0o700, exist_ok=True)
        tmp = f"{data_file()}.{os.getpid()}.tmp"
        try:
            os.remove(tmp)
        except FileNotFoundError:
            pass
        # Created private, never through a link, and flushed to disk before it
        # replaces the real file, so a power cut can't leave a half-written one.
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(tmp, flags, 0o600), "w", encoding="utf-8") as f:
            json.dump(file_form(state), f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        # Antivirus or another window reading the file can hold it for a
        # moment, and Windows then refuses the replace.
        for attempt in range(5):
            try:
                os.replace(tmp, data_file())
                break
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.1)
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


def width():
    """Wrap to the window, so a large font doesn't re-wrap lines raggedly."""
    try:
        cols = shutil.get_terminal_size((80, 24)).columns
    except (OSError, ValueError):
        cols = 80
    return max(30, min(72, cols - 2))


def indent(text):
    return "\n".join(textwrap.wrap(text, width() - 4, initial_indent="  ",
                                   subsequent_indent="  ",
                                   break_on_hyphens=False,
                                   break_long_words=False))


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
    try:
        import ctypes
        import msvcrt
        from ctypes import wintypes
        handle = msvcrt.get_osfhandle(sys.stdin.fileno())
    except (OSError, ValueError):
        return False
    except Exception:
        return True  # the check itself broke; trust isatty() rather than flash shut
    try:
        get_mode = ctypes.WinDLL("kernel32", use_last_error=True).GetConsoleMode
        get_mode.argtypes = [wintypes.HANDLE, wintypes.LPDWORD]
        get_mode.restype = wintypes.BOOL
        return bool(get_mode(handle, ctypes.byref(wintypes.DWORD())))
    except Exception:
        return True


def ask(prompt):
    """Return the typed text, or None when nobody can answer."""
    if not interactive():
        return None
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        say()  # the prompt is still on this line; start the next one cleanly
        return None
    except (EOFError, OSError, UnicodeError):
        return None


def is_yes(text):
    return (text or "").lower().strip(" .!") in YES


def is_no(text):
    return (text or "").lower().strip(" .!") in NO


def not_a_choice(word, choices):
    """Name what was typed, and say what would have worked."""
    shown = tidy(word)
    if len(shown) > 30:
        shown = shown[:30] + "..."
    say(f'That was not one of the choices: "{shown}". {choices}')


def ask_choice(prompt, yes, no, hint, tries=3):
    """Ask until the answer is recognised. Returns "yes", "no", "" or None.

    "" means Enter, None means nobody could answer or the answers were not
    understood three times, so the caller treats it as no answer.
    """
    for _ in range(tries):
        answer = ask(prompt)
        if answer is None:
            return None
        text = answer.lower().strip(" .!")
        if not text:
            return ""
        if text in QUIT_WORDS:
            raise Quit
        if text in yes:
            return "yes"
        if text in no:
            return "no"
        not_a_choice(answer, hint)
    return None


def para(text):
    """Say a paragraph wrapped to the window, never broken by hand."""
    say(textwrap.fill(text, width(), break_on_hyphens=False,
                      break_long_words=False))


def wrapped(prefix, text):
    return textwrap.fill(prefix + text, width(), subsequent_indent="  ",
                         break_on_hyphens=False, break_long_words=False)


def in_a_row(visits, d):
    """Count visits back from today where each is within 4 days of the next.

    Four days lets a Friday off and a weekend pass without breaking it.
    """
    days = [datetime.date.fromisoformat(v) for v in visits]
    days = [x for x in days if x <= d] + [d]
    days = sorted(set(days))
    n = 1
    for later, earlier in zip(days[:0:-1], days[-2::-1], strict=True):
        if (later - earlier).days > 4:
            break
        n += 1
    return n


def remind(on):
    path = startup_file()
    if not path:
        say("The sign-in reminder works on Windows only.")
        return False
    if on:
        target = os.path.dirname(os.path.abspath(__file__))
        if any(c in target for c in '"%&^<>|!'):
            say("The reminder cannot be set up from this folder.")
            return False
        # Written whole and then moved into place, so a sign-in never runs a
        # half-written launcher.
        tmp = path + ".tmp"
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(tmp, "w", encoding="ascii", newline="") as f:
                # start runs a .cmd through cmd /k, which strips the quotes
                # from a path with ( or @ in it. /d keeps the folder out of
                # that command line.
                f.write(f'@echo off\r\nstart "hello-world" /d "{target}" '
                        "hello.cmd --startup\r\n")
            os.replace(tmp, path)
        except (OSError, UnicodeEncodeError):
            try:
                os.remove(tmp)
            except OSError:
                pass
            say("Could not set up the reminder.")
            return False
        say("Done. hello-world will open once a day when you sign in.")
        say("To stop it, choose option 2 in the menu.")
        return True
    else:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError:
            say("Could not remove the reminder. Delete this file:")
            say("  " + path)
            return False
        say("Done. The sign-in reminder is off.")
    return True


def show_saved(state, full=True):
    d = today()
    recent = [v for v in state["visits"]
              if 0 <= (d - datetime.date.fromisoformat(v)).days <= 6]
    if full:
        say("Saved on this computer in:")
        say("  " + data_file())
    else:
        say("Saved in your own user folder on this computer.")
    say(f"Days you opened hello-world: {len(state['visits'])}"
        f" (last 7 days: {len(recent)})")
    if state.get("done"):
        say(f"Times you marked a plan done: {state['done']}")
    if state["intent"]:
        say(wrapped("Your current plan: ", state["intent"]["text"]))
    if state.get("previous"):
        say(wrapped("Earlier plan (for same): ", state["previous"]))
    show_finished(state)
    say("In-a-row line: " + ("shown." if state["streak"] else "hidden."))
    say("It never leaves this computer. Others who can read this computer's")
    say("files, such as IT staff, could read it.")
    if full:
        say("After tidying, the file holds only this:")
        say(json.dumps(file_form(state), indent=2, ensure_ascii=False))


def reset(state):
    """True when deleted, False when a delete failed, None when declined."""
    answer = ask("Delete all saved notes, dates and plans on this computer? "
                 "(y or n, Enter to cancel) > ")
    word = (answer or "").lower().strip(" .!")
    if word not in STRICT_YES:
        say("Nothing was deleted.")
        if word in QUIT_WORDS:
            raise Quit
        return None
    leftovers = [data_file()]
    failed = []
    listing_failed = False
    try:
        leftovers += [os.path.join(data_dir(), n)
                      for n in os.listdir(data_dir())
                      if n.startswith("notes.json.")
                      and (n.endswith(".tmp") or n.startswith("notes.json.bak"))]
    except FileNotFoundError:
        pass
    except OSError:
        listing_failed = True
    for path in leftovers:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError:
            failed.append(path)
    if failed or listing_failed:
        say("Could not delete everything.")
        if failed:
            say("Delete these yourself:")
            for path in failed:
                say("  " + path)
        if listing_failed:
            say("Could not list the folder, so backup copies may remain:")
            say("  " + data_dir())
        return False
    state.clear()
    state.update(new_state())
    # A marker with a new epoch instead of no file, so another open window
    # can tell the notes were deleted.
    state["epoch"] = os.urandom(8).hex()
    say("Done. Everything saved was deleted.")
    if save(state):
        say("Another open hello-world window cannot put it back.")
    else:
        say("Close any other open hello-world window, or it may save its")
        say("notes again.")
    return True


def refresh(state, can_save):
    """Re-read the file before a change, so a second open window can't
    overwrite what the first one saved. Returns False when it could not."""
    if not can_save:
        return False
    fresh, ok = load(repair=False)
    if ok:
        state.clear()
        state.update(fresh)
    return ok


def commit(state, base, can_save, soft=()):
    """Apply what this window changed since `base` to the file as it is now.

    A second open window's newer save is kept. Every save of a change goes
    through here. The file is re-read just before the write, with no prompt
    in between. Visits and finished plans are merged. Counts add only what
    this window added. Any other key is taken from this window only when it
    changed it. A key in `soft` was changed by tidying, not by the person, so
    the other window's change to it wins. Returns True when saved, and the
    state is then the merged copy.

    When everything was deleted since `base` was read, nothing is saved, and
    both the state and `base` become the file as it is now. A caller's undo()
    then leaves the window empty too.
    """
    if not can_save:
        return False
    fresh, ok = load(repair=False)
    if not ok:
        return False
    if "epoch" in base and fresh.get("epoch") != base["epoch"]:
        say("Everything saved was deleted in another window, so this was not")
        say("saved.")
        state.clear()
        state.update(fresh)
        base.clear()
        base.update(copy.deepcopy(fresh))
        return False
    if (fresh.get("done", 0) > base.get("done", 0)
            and state.get("done", 0) > base.get("done", 0)):
        say("The other open window had also finished a plan.")
    for key in set(state) | set(base):
        if key in ("visits", "done", "offer_skips", "finished"):
            continue
        if state.get(key) == base.get(key):
            continue
        if key in soft and fresh.get(key) != base.get(key):
            if key == "intent":
                say("The other open window changed the plan, so its plan is "
                    "kept.")
            continue
        if key in state:
            fresh[key] = copy.deepcopy(state[key])
        else:
            fresh.pop(key, None)
    fresh["visits"] = sorted(set(fresh["visits"]) | set(state["visits"]))[-MAX_VISITS:]
    mine, before = state.get("finished", []), base.get("finished", [])
    theirs = fresh.get("finished", [])
    added = row_counts(mine) - row_counts(before)
    removed = row_counts(before) - row_counts(mine)
    # Each finished row came with one done. A row the other window also added
    # with the same words and date is one finish, not two.
    repeats = added & (row_counts(theirs) - row_counts(before))
    for key, cap in (("done", 99999), ("offer_skips", MAX_OFFER_SKIPS)):
        gained = state.get(key, 0) - base.get(key, 0)
        if key == "done":
            gained -= sum(repeats.values())
        if gained > 0:
            fresh[key] = min(fresh.get(key, 0) + gained, cap)
    rows = {json.dumps(r, sort_keys=True): r for r in theirs + mine}
    kept = (row_counts(theirs) - removed) + (added - repeats)
    finished = sorted((rows[k] for k in kept.elements()), key=lambda r: r["date"])
    if finished:
        fresh["finished"] = finished[-MAX_FINISHED:]
    else:
        fresh.pop("finished", None)
    if not save(fresh):
        return False
    state.clear()
    state.update(fresh)
    return True


def row_counts(rows):
    """Finished rows counted as a multiset, since dicts can't go in a Counter."""
    return collections.Counter(json.dumps(r, sort_keys=True) for r in rows)


def undo(state, base):
    """Put the state back as it was when a save failed."""
    state.clear()
    state.update(base)


COMMAND_WORDS = ("menu", "help", "?", "q", "quit", "exit", "done", "plan",
                 "m", "p")
# Someone declining to plan is not making an error, so these get no lecture.
DECLINE_WORDS = ("none", "no", "nope", "nothing", "skip", "n")


def is_command(text, again="Type plan at the last prompt to set one."):
    """A command word typed where a plan is asked is not a plan."""
    word = (text or "").lower().strip(" .!")
    if word in DECLINE_WORDS:
        return True
    if word in COMMAND_WORDS:
        say("That looks like a command, not a plan, so nothing was saved. "
            + again)
        return True
    return False


def show_finished(state, limit=MAX_FINISHED):
    """The last few finished plans, so finishing has a visible payoff.

    After done and on welcome back only the last few are read out; option 1
    lists every one kept.
    """
    items = state.get("finished") or []
    if not items:
        return
    say()
    say("Finished lately:")
    for item in list(reversed(items))[:limit]:
        say(wrapped("  " + long_date(datetime.date.fromisoformat(
            item["date"])) + ": ", item["text"]))


def reuse(state, raw):
    """Typing `same` brings back the plan before this one, if there is one."""
    if (raw or "").strip().lower() == "same" and state.get("previous"):
        return state["previous"]
    return raw


def set_plan(state, can_save, iso=None, after_done=False):
    """Returns True when the person chose to close (after a done only)."""
    refresh(state, can_save)
    old = state["intent"]
    # daily() passes its own date, so a window left open past midnight
    # doesn't date a plan to the next day.
    iso = iso or today().isoformat()
    if old:
        when = ("today" if old["date"] == iso else "from " + long_date(
            datetime.date.fromisoformat(old["date"])))
        say(wrapped(f"Your plan {when}: ", old["text"]))
    if state.get("previous"):
        say(wrapped("Earlier plan: ", state["previous"]))
    hint = ", same to reuse the earlier plan" if state.get("previous") else ""
    typed = ask("Type the next plan" + hint + ", or Enter to close > "
                if after_done else
                "Type today's plan" + hint
                + (", or Enter to keep it > " if old else ", or Enter to go back > "))
    word = (typed or "").lower().strip(" .!")
    if after_done and not word:
        say("Closing.")
        return True
    if word in QUIT_WORDS:
        raise Quit
    # Another window may have saved while this prompt waited.
    refresh(state, can_save)
    old = state["intent"]
    if (typed or "").lower() == "same" and not state.get("previous"):
        say("There is no earlier plan to reuse yet. Nothing changed.")
        return False
    if is_command(typed, "Type your plan, or press Enter to go back."):
        return False
    text = typed_plan(reuse(state, typed) or "")
    if not text:
        say("Nothing changed.")
        return False
    base = copy.deepcopy(state)
    # Changing today's plan is a correction, so only a plan carried over from
    # an earlier day is kept for same.
    if old and old["text"] != text and old["date"] != iso:
        state["previous"] = old["text"]
    state["intent"] = {"text": text, "date": iso}
    if commit(state, base, can_save):
        say(SAVED_PLAN)
        nudge_if_several(text)
    else:
        undo(state, base)
        say("Could not save that on this computer. Your plan is unchanged.")
    return False


def forget_finished(state, can_save):
    """Remove one finished plan from the file, and leave everything else."""
    refresh(state, can_save)
    shown = list(reversed(state.get("finished") or []))
    if not shown:
        say("No finished plans are saved.")
        return
    for n, item in enumerate(shown, 1):
        say(wrapped(f"  {n}  {long_date(datetime.date.fromisoformat(item['date']))}: ",
                    item["text"]))
    numbers = [str(n) for n in range(1, len(shown) + 1)]
    for _ in range(3):
        choice = ask(f"Type the number to forget (1 to {len(shown)}), "
                     "or Enter to keep them all > ")
        if (choice or "").lower().strip(" .!") in QUIT_WORDS:
            raise Quit
        if not choice or choice in numbers:
            break
        say(f'There is no number "{tidy(choice)[:30]}" on the list. Type a '
            f"number from 1 to {len(shown)}, or press Enter to keep them all.")
    if not choice or choice not in numbers:
        say("Nothing changed.")
        return
    item = shown[int(choice) - 1]
    also_same = state.get("previous") == item["text"] and ask_choice(
        "Also forget it as the earlier plan for same? "
        "(y or n, Enter to keep it for same) > ",
        STRICT_YES, ("n", "no", "nope"),
        "Type y or n, or press Enter to keep it for same.") == "yes"
    refresh(state, can_save)
    if item not in state.get("finished", []):
        say("That plan was already forgotten. Nothing changed.")
        return
    base = copy.deepcopy(state)
    state["finished"] = [i for i in state["finished"] if i != item]
    if also_same and state.get("previous") == item["text"]:
        state.pop("previous")
    kept = state.get("previous") == item["text"]
    if commit(state, base, can_save):
        say(wrapped("Forgotten: ", item["text"]))
        if kept:
            say("Same still has it.")
    else:
        undo(state, base)
        say("Could not save that on this computer. Nothing changed.")


def menu(state, can_save=True, iso=None):
    # The options are read out once. After that only the prompt comes back,
    # and m lists them again.
    listed = False
    while True:
        say()
        reminding = startup_file() and os.path.exists(startup_file())
        if not listed:
            say("Options")
            say("  1  Show what is saved on this computer")
            say("  2  " + ("Turn off: open once a day at sign-in (now on)"
                           if reminding else
                           "Turn on: open once a day at sign-in (now off)"))
            say("  3  " + ("Hide the in-a-row line (now shown)"
                           if state["streak"] else
                           "Show the in-a-row line (now hidden)"))
            say("  4  Delete everything saved")
            say("  5  Help")
            say("  6  Set or change today's plan")
            say("  7  Forget one finished plan")
            say("  8  " + ("Hide the thought and tip (now shown)"
                           if state.get("tips", True) else
                           "Show the thought and tip (now hidden)"))
            say("  Enter  Back to the last prompt")
            listed = True
            choice = ask("Choose 1 to 8, or Enter to go back > ")
        else:
            choice = ask("Choose 1 to 8, m to list the options, or Enter to "
                         "go back > ")
        if not choice:
            return
        if choice.lower().strip(" .!") in QUIT_WORDS:
            raise Quit
        if choice.lower() in ("m", "menu", "list"):
            listed = False
            continue
        if choice.lower() in ("help", "?", "h"):
            choice = "5"
        if choice == "1":
            if not refresh(state, can_save):
                say("The saved file could not be read just now, so this may "
                    "be out of date.")
            show_saved(state, full=False)
            if (ask("Type full to see the whole file, or Enter to go on > ")
                    or "").lower() == "full":
                refresh(state, can_save)
                say(json.dumps(file_form(state), indent=2, ensure_ascii=False))
        elif choice == "2":
            if remind(not reminding):
                # A choice made here is final; the offer must not come back.
                refresh(state, can_save)
                base = copy.deepcopy(state)
                state["offered"] = True
                if not commit(state, base, can_save):
                    undo(state, base)
                    say("Could not save that choice on this computer.")
        elif choice == "3":
            refresh(state, can_save)
            base = copy.deepcopy(state)
            state["streak"] = not state["streak"]
            if commit(state, base, can_save):
                say("Done. The in-a-row line is "
                    + ("on." if state["streak"] else "off."))
            else:
                undo(state, base)
                say("Could not save that choice on this computer.")
        elif choice == "4":
            reset(state)
        elif choice == "5":
            say(MENU_HELP)
        elif choice == "6":
            set_plan(state, can_save, iso)
        elif choice == "7":
            forget_finished(state, can_save)
        elif choice == "8":
            refresh(state, can_save)
            base = copy.deepcopy(state)
            if state.get("tips", True):
                state["tips"] = False
            else:
                state.pop("tips", None)
            if commit(state, base, can_save):
                say("Done. The thought and tip are "
                    + ("on." if state.get("tips", True) else "off."))
            else:
                undo(state, base)
                say("Could not save that choice on this computer.")
        else:
            not_a_choice(choice, "Type 1 to 8, or press Enter to go back.")


def offer_reminder(state, can_save, planned=False):
    """Ask whether to open at sign-in, right after a plan or from visit two on.

    It is asked once. Enter is final too, and an unclear answer asks again on
    a later visit.
    """
    path = startup_file()
    if (not path or state.get("offered") or os.path.exists(path)
            or not (planned or len(state["visits"]) >= 2)):
        return
    answer = ask_choice(
        "Want it to open once a day when you sign in so it can ask about "
        "your plan? (y or n, Enter for not now) > ",
        STRICT_YES, ("n", "no", "nope", "no thanks", "never", "stop"),
        "Type y or n, or press Enter for not now.")
    if answer is None:
        say("That was not understood. It will ask again on a later visit.")
        return
    refresh(state, can_save)
    base = copy.deepcopy(state)
    if answer == "yes":
        if not remind(True):
            say("It will ask again on a later visit. Menu option 2 also turns "
                "it on.")
            say()
            return
        state["offered"] = True
    elif answer == "no":
        state["offered"] = True
        say("No problem. Menu option 2 turns it on later.")
    else:
        skips = state.get("offer_skips", 0) + 1
        state["offer_skips"] = skips
        if skips >= MAX_OFFER_SKIPS:
            state["offered"] = True
            say("Okay. It won't ask again. Menu option 2 turns it on.")
        else:
            say("Okay. It will ask again on a later visit. Type n to stop it.")
    if not commit(state, base, can_save):
        say("Could not save that choice on this computer.")
    say()


def finish_plan(state, text, d):
    """Count a finished plan, dated d. `same` only ever holds unfinished plans."""
    if state.get("previous") == text:
        state.pop("previous")
    state["done"] = min(state.get("done", 0) + 1, 99999)
    state["finished"] = (state.get("finished", [])
                         + [{"text": text, "date": d.isoformat()}])[-MAX_FINISHED:]


def done_lines(state, d):
    """Shown only once the save has worked, and with the merged count, so
    nobody is congratulated for something that was not recorded."""
    lines = [DONE_LINES[d.toordinal() % len(DONE_LINES)]]
    if state.get("done", 0) > 1:
        lines.append(f"That is {state['done']} done so far.")
    return lines


def finish_day(plan_day, d):
    """The day a plan was finished. Asked only when it was set over a day ago,
    since the next morning almost always means the plan's own day."""
    if (d - plan_day).days <= 1:
        return plan_day
    yesterday = d - datetime.timedelta(days=1)
    for _ in range(3):
        answer = ask(f"When did you finish it? (Enter for {long_date(plan_day)}, "
                     "y for yesterday, t for today) > ")
        word = (answer or "").lower().strip(" .!")
        if not word:
            return plan_day
        if word in QUIT_WORDS:
            raise Quit
        if word in ("y", "yes", "yesterday"):
            return yesterday
        if word in ("t", "today"):
            return d
        not_a_choice(answer, "Press Enter, or type y or t.")
    return plan_day


def nudge_if_several(text):
    """A plan of several things joined together is hard to finish."""
    padded = f" {text.lower()} "
    if any(joint in padded for joint in (" and ", " & ")) or "+" in text:
        para("That looks like more than one thing. Finishing the first part "
             "still counts.")


def mark_done_now(state, can_save, d):
    """Same-day done: the plan on screen is finished, so say so at once."""
    refresh(state, can_save)
    plan = state["intent"]
    if not plan:
        say("There is no plan to mark as done. Type plan to set one.")
        return False
    base = copy.deepcopy(state)
    finish_plan(state, plan["text"], d)
    state["intent"] = None
    if not commit(state, base, can_save):
        undo(state, base)
        say("Could not save that on this computer. The plan is still open.")
        return False
    for line in done_lines(state, d):
        say(line)
    show_finished(state, SHOWN_AFTER_DONE)
    return True


def daily(startup):
    d = today()
    iso = d.isoformat()
    state, can_save = load()
    base = copy.deepcopy(state)
    person = interactive()
    seen_today = iso in state["visits"]
    typed_new = False
    answered = False
    if startup and seen_today:
        return
    first = not state["visits"]
    intent = state["intent"]
    if intent and intent["date"] > iso:
        intent["date"] = iso  # the clock moved back; it is today's plan now
    expired = False
    # A plan kept day after day still counts from the day it was first set.
    since = intent.get("since", intent["date"]) if intent else None
    if intent and (d - datetime.date.fromisoformat(since)).days > 14:
        state["previous"] = intent["text"]
        intent, expired = None, True

    say("Hello, world!")
    say(long_date(d))
    say()

    if expired:
        para("Your plan from over two weeks ago was put away. Type same at "
             "the plan prompt to bring it back.")
        say()

    if first:
        para("Press Enter at each question to skip it, and once more to "
             "close. That's it.")
        say()
        para("Welcome. Each day you get one thought and one small thing to "
             "try, the same for everyone. If you type a plan, it asks next "
             "time how it went. Notes stay in your user folder and it sends "
             "nothing anywhere, but IT staff could read them, so skip private "
             "details. Type menu for the options.")
        say()
    elif not seen_today:
        last = datetime.date.fromisoformat(state["visits"][-1])
        row = in_a_row(state["visits"], d)
        if (d - last).days > 7:
            say("Welcome back. Glad you are here.")
            show_finished(state, SHOWN_AFTER_DONE)
            say()
        elif state["streak"] and (row in (3, 7, 14) or row % 30 == 0):
            say(f"You have opened this {row} times in a row. Nice to see you.")
            say()

    quitting = False
    try:
        # Asked until it is answered, also on a second open the same day,
        # but two skips mean "stop asking"; the plan then shows as still open.
        if intent and intent["date"] < iso and intent.get("skips", 0) < 2:
            say(wrapped("Last time you planned: ", intent["text"]))
            answer = ask_choice(
                "Did you do it? (y for yes, n for not yet, Enter to skip) > ",
                YES, NO, "Type y or n, or press Enter to skip.")
            if answer == "yes":
                answered = True
                when = finish_day(datetime.date.fromisoformat(intent["date"]), d)
                # Saved now, so the answer is heard now.
                finish_plan(state, intent["text"], when)
                state["intent"] = None
                if commit(state, base, can_save):
                    base = copy.deepcopy(state)
                    intent = None
                    for line in done_lines(state, d):
                        say(line)
                else:
                    # A delete in another window also lands here, so take
                    # the plan from the state, never the copy held above.
                    undo(state, base)
                    intent = state["intent"]
                    say("Could not save that on this computer. Your answer was "
                        "not counted.")
            elif answer == "no":
                answered = True
                keep = ask_choice(
                    "That is fine. Keep it for today? (y or n, Enter to keep it) > ",
                    STRICT_YES + ("not yet",), ("n", "no", "nope"),
                    "Type y to keep it, n to clear it, or press Enter to keep it.")
                if keep == "no":
                    state["previous"] = intent["text"]
                    intent = None
                    say("Cleared. Type same at a plan prompt if you want it back.")
                else:
                    intent = {"text": intent["text"], "date": iso,
                              "since": intent.get("since", intent["date"])}
                    say("Kept for today.")
            elif answer is None and person:
                say("That was not understood. Your plan is left as it was.")
            elif answer is not None:
                intent = dict(intent, skips=intent.get("skips", 0) + 1)
                say("Left as it was.")
            say()

        if state.get("tips", True):
            thought, tip = todays_pair(d)
            say("Thought for today:")
            say(indent(thought))
            say()
            say("Try this today:")
            say(indent(tip))
            say()

        if intent and intent["date"] == iso:
            say(wrapped("Your plan for today: ", intent["text"]))
            say()
        elif intent:
            # Not answered, or skipped twice; it must not vanish.
            when = long_date(datetime.date.fromisoformat(intent["date"]))
            say(wrapped(f"Still open from {when}: ", intent["text"]))
            say()
        if not seen_today and not (intent and intent["date"] == iso):
            skip = ("(Enter to skip)" if not intent else
                    "(A plan typed here replaces the old one. Enter to skip)")
            if state.get("previous") and not intent:
                say(wrapped("Earlier plan: ", state["previous"]))
                skip = "(Type same to reuse it, or Enter to skip)"
            text = ask("What is one thing you want to get done today?\n"
                       + skip + " > ")
            if (text or "").lower().strip(" .!") in QUIT_WORDS:
                raise Quit
            if (text or "").lower() == "same" and not state.get("previous"):
                say("There is no earlier plan to reuse yet. Nothing was saved.")
                text = ""
            elif is_command(text):
                text = ""
            if text:
                text = typed_plan(reuse(state, text))
                if text:
                    if intent and intent["text"] != text:
                        state["previous"] = intent["text"]
                    intent = {"text": text, "date": iso}
                    typed_new = True
            say()
    except Quit:
        quitting = True

    # With nobody at the keyboard, such as a launch with no console, show the
    # screen but keep today's questions for the next real visit.
    if person:
        if not seen_today:
            state["visits"] = (state["visits"] + [iso])[-MAX_VISITS:]
        state["intent"] = intent
        # A plan only tidied here (a future date made today, an old plan
        # cleared) must not overwrite one the other window saved meanwhile.
        soft = () if answered or typed_new else ("intent", "previous")
        if not commit(state, base, can_save, soft):
            undo(state, base)
            intent = state["intent"]
            say("Your notes could not be saved on this computer. This screen "
                "still works.")
        else:
            intent = state["intent"]
            if typed_new:
                say(SAVED_PLAN)
                nudge_if_several(intent["text"])
                say()
            if not seen_today and not quitting:
                try:
                    offer_reminder(state, can_save, planned=typed_new)
                except Quit:
                    quitting = True
                # The offer re-reads the file, so pick up the plan it read.
                intent = state["intent"]
    if quitting:
        say("Closing.")
        return

    # A message at the very end must stay on screen until the person has read
    # it, because the window closes as soon as the program exits.
    try:
        last_prompt(state, can_save, intent, person, d, iso)
    except Quit:
        say("Closing.")


def last_prompt(state, can_save, intent, person, d, iso):
    """Loop at the last prompt until the person closes the window."""
    while True:
        planned = bool(intent and person and state["intent"] is intent)
        prompt = ("Type done, plan, menu or q, or Enter to close > "
                  if planned else
                  "Type plan, menu or q, or Enter to close > ")
        answer = (ask(prompt) or "").lower().strip()
        if answer == "done" and person:
            closing = False
            if mark_done_now(state, can_save, d):
                say()
                closing = set_plan(state, can_save, iso, after_done=True)
            intent = state["intent"]
            if closing:
                break
            continue
        elif answer in ("p", "plan") and person:
            set_plan(state, can_save, iso)
            intent = state["intent"]
            continue
        elif answer in ("m", "menu", "h", "help", "?"):
            menu(state, can_save, iso)
            intent = state["intent"]
            continue
        elif answer in ("q", "quit", "exit", "x", "close"):
            pass
        elif answer:
            not_a_choice(answer, "Type " + ("done, " if planned else "")
                         + "plan, menu or q, or press Enter to close.")
            continue
        break


def run(argv):
    argv = [a.lower() for a in argv]
    if argv in (["/?"], ["-?"], ["/help"], ["-help"], ["help"]):
        argv = ["--help"]
    if argv == ["--plain"]:
        say("Hello, world!")
        return 0
    if argv in (["--version"], ["-v"]):
        say("hello-world " + VERSION)
        return 0
    if argv == ["--help"] or argv == ["-h"]:
        say(help_text())
        return 0
    if argv == ["--startup"]:
        daily(startup=True)
        return 0
    if not argv:
        daily(startup=False)
        return 0
    if argv == ["--stats"]:
        state, readable = load(repair=False)
        if not readable:
            say("The saved file can't be read right now, or it is damaged.")
            say("Nothing was changed. Saved in: " + data_dir())
            return 1
        show_saved(state)
        return 0
    if argv == ["--reset"]:
        if not interactive():
            say("Deleting saved notes needs a person at the keyboard.")
            return 1
        state, _ = load(repair=False)
        # Answering no is the person's choice; only a failed delete is an error.
        try:
            return 1 if reset(state) is False else 0
        except Quit:
            return 0
    if len(argv) == 2 and argv[0] == "--remind" and argv[1] in ("on", "off"):
        return 0 if remind(argv[1] == "on") else 1
    if len(argv) == 2 and argv[0] == "--streak" and argv[1] in ("on", "off"):
        state, can_save = load()
        base = copy.deepcopy(state)
        state["streak"] = argv[1] == "on"
        if commit(state, base, can_save):
            say("Done. The in-a-row line is "
                + ("on." if state["streak"] else "off."))
            return 0
        say("Could not save that choice on this computer.")
        return 1
    if len(argv) == 1 and argv[0] in ("--remind", "--streak"):
        say(f"{argv[0]} needs on or off. Here are the options.")
    else:
        say("Unknown option: " + tidy(" ".join(argv))[:60] + ". Here are the options.")
    say()
    say(help_text())
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
