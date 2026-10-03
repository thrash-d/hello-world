#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print "Hello, world!" and one small useful thing each day.

On Windows the Start menu opens it as a window, through pythonw.exe from its
own pinned Python, and hello.cmd runs the same screens as text in a console.
It shows a thought and a small thing to try, and can keep one plan for the day.
Everything it saves stays in one small file in the user's own folder, and
nothing is sent anywhere. Exit 0 when the text was written, 1 when stdout
could not be written or a command (--reset, --stats, --remind, --streak)
failed, 2 for an unknown option or a reminder link it doesn't know.
"""
import collections
import contextlib
import copy
import datetime
import io
import json
import os
import shutil
import sys
import textwrap
import unicodedata
import time

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        "Sunday")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
GREETING = "Hello, world!"

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
    'For one minute, notice something pleasant: a sound, a smell or something you touch.',
    'Recall a place you love and picture it for thirty seconds.',
    'Say "good enough for now" about one small task and move on.',
    'Write one sentence about something you are grateful for.',
    'Savor the next sip of your drink and notice the taste.',
    'Take a short break between two tasks before you start the next one.',
    'Look for one thing today that turns out better than you expected.',
    'Choose one word for how you want the afternoon to feel.',
    'Let your mind rest for sixty seconds, then go back to your next task.',
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
    'Talk to a colleague who has been quiet in meetings lately and ask how they are.',
    'Finish the thing that is nearly done before you start something new.',
    'Finished and good enough is usually more useful than perfect and not finished.',
    'Close one open loop today and notice the small relief that follows.',
    'The last ten percent is often just a few careful minutes. Give them today.',
    'Send the email that is waiting in your drafts. It is probably fine as it is.',
    'Mark it complete, take a breath, and be pleased that it is done.',
    'A finished small thing is worth more than a half-finished big one.',
    "Before you log off, write tomorrow's first step on a note so you don't have to remember it.",
    'Read it once more, fix what you find, and then send it.',
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
    "Good. That one is finished.",
    "Nice. It is good to finish something.",
    "Well done. Take a short break before the next one.",
    "Good. Small finished tasks add up.",
    "That is done. You can be pleased about it.",
    "Good. That one is off your list.",
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
  --streak off    Hide the days-in-a-row message (on to show it)
  --version       Show the version
  --check-content FILE
                  Check an organization content file
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
          "stretch", "wrist", "hombro", "mandíbula", "cuello", "ojo", "agua",
          "respir", "postura", "estir", "muñeca", "épaule", "mâchoire", "nuque",
          "yeux", "œil", "étir", "poignet", "ombro", "pescoço", "olho", "água",
          "along", "pulso", "schulter", "kiefer", "nacken", "auge", "wasser",
          "atem", "atm", "haltung", "dehn", "handgelenk",
          "肩", "下巴", "颈", "眼", "水", "呼吸", "姿势", "伸展", "手腕",
          "あご", "首", "目", "姿勢", "ストレッチ", "手首",
          "어깨", "턱", "목", "눈", "물", "호흡", "자세", "스트레칭", "손목",
          "كتف", "فك", "رقبة", "عين", "ماء", "تنفس", "وضعية", "تمدد", "معصم",
          "כתפ", "לסת", "צוואר", "עינ", "מים", "נשימ", "יציבה", "מתיחה")


def todays_pair(d):
    """The day's thought and tip. Everyone gets the same pair on the same day."""
    thoughts, tips = content_lists()
    tip = tips[d.toordinal() % len(tips)]
    i = (d.toordinal() + 37) % len(thoughts)
    # At most one pass, so lists where every thought shares a topic with the
    # tip can't loop forever.
    for _ in range(len(thoughts)):
        if not any(w in tip.lower() and w in thoughts[i].lower() for w in TOPICS):
            break
        i = (i + 1) % len(thoughts)
    return thoughts[i], tip


# An organization can ship its own thoughts and tips in content.json next to
# hello.py, inside the signed package. They replace the built-in lists whole.
# The rules keep it a list of short, timeless lines, not a way to send
# announcements: no links, no addresses, no dates, nothing long.
CONTENT = None
MIN_CONTENT, MAX_CONTENT = 7, 200
MAX_HOLIDAYS = 100
CONTENT_LENGTH = (10, 120)


def content_problems(data, t=lambda text: text):
    """What is wrong with organization content, as plain sentences. `t`
    translates them; the default keeps them in English."""
    if (not isinstance(data, dict) or not {"thoughts", "tips"} <= set(data)
            or not set(data) <= {"thoughts", "tips", "holidays", "title"}):
        return [t('The file must hold an object with two lists, "thoughts" and '
                  '"tips", and may add "holidays" and "title".')]
    problems = []
    holidays = data.get("holidays", [])
    if not isinstance(holidays, list) or len(holidays) > MAX_HOLIDAYS:
        problems.append(t('"holidays" must be a list of at most {n} dates.')
                        .format(n=MAX_HOLIDAYS))
    else:
        for n, value in enumerate(holidays, 1):
            try:
                day(value)
            except ValueError:
                problems.append(t("holidays line {line} is not a date like "
                                  "2026-12-25.").format(line=n))
    title = data.get("title", "Hello, world!")
    if (not isinstance(title, str) or not 1 <= len(tidy(title)) <= 40
            or tidy(title) != title.strip()
            or any(mark in title.lower() for mark in ("http", "www.", "://", "@"))):
        problems.append(t('"title" must be 1 to 40 characters of plain text, '
                          'with no link or address.'))
    low_months = [m.lower() for m in MONTHS if m != "May"] + [
        m.lower() for data in LANGUAGES.values() for m in data["months"]]
    for key in ("thoughts", "tips"):
        items = data[key]
        if not isinstance(items, list) or not MIN_CONTENT <= len(items) <= MAX_CONTENT:
            problems.append(t('"{list}" must be a list of {low} to {high} lines.')
                            .format(list=key, low=MIN_CONTENT, high=MAX_CONTENT))
            continue
        for n, item in enumerate(items, 1):
            where = {"list": key, "line": n}
            if not isinstance(item, str):
                problems.append(t("{list} line {line} is not text.").format(**where))
                continue
            text, low = tidy(item), tidy(item).lower()
            if text != item.strip():
                problems.append(t("{list} line {line} has control characters or "
                                  "extra spaces.").format(**where))
            if not CONTENT_LENGTH[0] <= len(text) <= CONTENT_LENGTH[1]:
                problems.append(t("{list} line {line} must be {low} to {high} "
                                  "characters long.").format(
                                      low=CONTENT_LENGTH[0], high=CONTENT_LENGTH[1],
                                      **where))
            if any(mark in low for mark in ("http", "www.", "://", "@")):
                problems.append(t("{list} line {line} has a link or an address.")
                                .format(**where))
            if any(m in low.split() or m + "," in low for m in low_months) or any(
                    c.isdigit() and next_c in "/-." and after.isdigit()
                    for c, next_c, after in zip(text, text[1:], text[2:], strict=False)):
                problems.append(t("{list} line {line} has a date.").format(**where))
    return problems


def org_content():
    """The organization's content.json when it is valid, else None. A file
    that breaks the rules is ignored whole."""
    path = CONTENT or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "content.json")
    try:
        with open(path, encoding="utf-8-sig") as f:
            data = json.loads(f.read(200_000))
    except (OSError, ValueError, RecursionError):
        return None
    return None if content_problems(data) else data


def content_lists():
    """The organization's thoughts and tips if it shipped valid ones, else
    the built-in lists."""
    data = org_content()
    if not data:
        return built_in_lists()
    return (tuple(tidy(x) for x in data["thoughts"]),
            tuple(tidy(x) for x in data["tips"]))


def holiday(d):
    """True on a day the organization's content.json lists as a holiday."""
    data = org_content() or {}
    return d.isoformat() in {day(x) for x in data.get("holidays", [])}


def first_name():
    """The first word of this person's Windows display name, or None."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        size = ctypes.c_ulong(256)
        buffer = ctypes.create_unicode_buffer(256)
        # NameDisplay is 3. It fails on PCs outside a domain.
        if not ctypes.windll.secur32.GetUserNameExW(3, buffer, ctypes.byref(size)):
            return None
    except (AttributeError, OSError):
        return None
    words = tidy(buffer.value).replace(",", " ").split()
    # "Surname, Given" is a common directory order.
    name = words[-1] if "," in buffer.value and len(words) > 1 else (words or [None])[0]
    return name[:30] if name else None


def greeting(state):
    """The heading: the person's name if they asked for it, then the
    organization's title, then "Hello, world!". --plain always says the last."""
    name = first_name() if state.get("name") else None
    if name:
        return tr("Hello, {name}!").format(name=name)
    title = (org_content() or {}).get("title")
    return tidy(title) if title else tr(GREETING)


def built_in_lists():
    data = translation()
    return (data["thoughts"], data["tips"]) if data else (THOUGHTS, TIPS)


def help_text():
    here = os.path.dirname(os.path.abspath(__file__))
    return tr(HELP) + "\n\n" + tr("hello.cmd is in this folder:") + "\n  " + here

VERSION = "1.34.0"
MAX_VISITS = 400
KEEP_VISIT_DAYS = 60
MAX_FILE = 1_000_000
# The words of every language work in every language, so nobody has to
# guess which language the program thinks it speaks, and a PC whose
# language changes needs no retraining.
DONE_WORDS = ("done", "hecho", "listo", "fait", "feito", "erledigt")
# The sign-in offer starts something, so a stray "done" must not count.
STRICT_YES = ("y", "yes", "yep", "ya", "yeah", "yup", "ok", "okay", "sure",
              "si", "sí", "vale", "sim", "claro", "oui", "d'accord", "ja",
              "klar")
# One-letter yes words work only in their own language: in English, s or o
# is a slip or "skip", and must not finish a plan.
LETTER_YES = {"es": ("s",), "pt": ("s",), "fr": ("o",), "de": ("j",)}
# Natural ways to say a plan is finished, for "Did you do it?" only.
DID_WORDS = ("did it", "i did", "i did it", "done it", "finished", "lo hice",
             "terminé", "fiz", "geschafft")
NOT_YET = ("not yet", "todavía no", "aún no", "aun no", "pas encore",
           "ainda não", "ainda nao", "noch nicht")
NO_WORDS = ("n", "no", "nope", "nah", "non", "não", "nao", "nein")
NO = NO_WORDS + NOT_YET + ("not really", "not done")
MAX_OFFER_SKIPS = 1
NO_THANKS = NO_WORDS + ("no thanks", "never", "stop", "no gracias", "nunca",
                  "non merci", "jamais", "não obrigado", "nein danke", "nie")
SAME_WORDS = ("same", "repetir", "retomar", "reprendre", "wieder")
PLAN_WORDS = ("p", "plan", "plano")
MENU_WORDS = ("m", "menu", "menú", "menü")
HELP_WORDS = ("h", "help", "?", "ayuda", "aide", "ajuda", "hilfe")
LIST_WORDS = ("list", "lista", "liste")
FULL_WORDS = ("full", "todo", "tout", "tudo", "alles")

# The tests set these after importing the module, to run against a fixed date,
# a temporary folder, and typed input. Nothing outside the program sets them.
TODAY = None
HOME = None
STARTUP_DIR = None
FORCE_INTERACTIVE = False
# A dict of policy values, so tests never read the real registry.
POLICY = None
# "en" or "es" in tests; None follows the Windows display language.
LANGUAGE = None
# A list in tests: the sign-in reminder's XML goes here instead of to Windows.
SHOWN = None
# Milliseconds after which tests close the window by itself.
CLOSE_WINDOW_AFTER = None
# True while the window runs, so nothing waits for typed input.
WINDOW = False
# When Ctrl+C last skipped a question, for "twice in a row closes".
INTERRUPTED = 0.0
# "colon_prompts": prompts end in ":" instead of " >".
PROMPT_COLON = False
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
# Where the reminder's name and its answer links are registered for the user.
CLASSES_KEY = r"Software\Classes"
RUN_VALUE = "hello-world"
POLICY_KEY = r"SOFTWARE\Policies\hello-world"


class Quit(Exception):
    """The person typed q at a question, so the window closes."""


# Stripped from a typed word: end punctuation, and the quote marks the
# screens put around command words, in case someone types them too.
TRIM = " .!¡\"'«»„“”‚‘’"
QUIT_WORDS = ("q", "quit", "exit", "x", "close", "salir", "cerrar",
              "quitter", "sair", "beenden")


class OutputClosed(Exception):
    """Writing to stdout failed, so nothing more can be shown."""


def today():
    return datetime.date.fromisoformat(TODAY) if TODAY else datetime.date.today()


def long_date(d):
    data = translation() or {"days": DAYS, "months": MONTHS,
                             "date": "{day}, {d} {month} {year}"}
    # French writes the first of the month as 1er, Portuguese as 1º.
    day = data.get("first", 1) if d.day == 1 else d.day
    return data["date"].format(day=data["days"][d.weekday()], d=day,
                               month=data["months"][d.month - 1], year=d.year)


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


def policy(name):
    """True when Group Policy sets this value to 1 for the PC or the user.

    Read from HKLM, then HKCU, under SOFTWARE\\Policies\\hello-world, where
    only administrators and Group Policy can write.
    """
    if POLICY is not None:
        return bool(POLICY.get(name))
    if os.name != "nt":
        return False
    import winreg
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, POLICY_KEY) as key:
                value, kind = winreg.QueryValueEx(key, name)
            if kind == winreg.REG_DWORD and value == 1:
                return True
        except OSError:
            pass
    return False


def policy_value(name, kind):
    """A Group Policy value of `kind` ("text" or "number"), HKLM first, or
    None when it isn't set."""
    if POLICY is not None:
        value = POLICY.get(name)
        return value if isinstance(value, str if kind == "text" else int) else None
    if os.name != "nt":
        return None
    import winreg
    want = (winreg.REG_SZ,) if kind == "text" else (winreg.REG_DWORD,)
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, POLICY_KEY) as key:
                value, found = winreg.QueryValueEx(key, name)
            if found in want:
                return value
        except OSError:
            pass
    return None


def feedback_address():
    """The address the FeedbackAddress policy sets, when it looks like one."""
    value = policy_value("FeedbackAddress", "text") or ""
    local, _, domain = value.strip().partition("@")
    if (local and "." in domain and len(value) <= 254
            and not any(c.isspace() or c in '<>"?&%,;' for c in value)):
        return value.strip()
    return None


# A list in tests: the usage events that would go to the event log.
EVENTS = None


def report_usage(what):
    """Under the ReportUsage policy, write one line to the Application event
    log, source hello-world: "opened", "plan set" or "plan finished". Never
    plan text, and nothing goes over a network."""
    if not policy("ReportUsage"):
        return
    message = f"hello-world: {what}"
    if EVENTS is not None:
        EVENTS.append(message)
        return
    if os.name != "nt":
        return
    try:
        import ctypes
        api = ctypes.windll.advapi32
        api.RegisterEventSourceW.restype = ctypes.c_void_p
        source = api.RegisterEventSourceW(None, "hello-world")
        if source:
            strings = (ctypes.c_wchar_p * 1)(message)
            # EVENTLOG_INFORMATION_TYPE, event 2000
            api.ReportEventW(ctypes.c_void_p(source), 4, 0, 2000, None, 1, 0,
                             strings, None)
            api.DeregisterEventSource(ctypes.c_void_p(source))
    except (AttributeError, OSError):
        pass


def log_error(error):
    """Under the LogErrors policy, add what went wrong to errors.log in the
    data folder, kept under 100 KB. Never plan text: only the error's type
    and where in hello.py it happened."""
    if not policy("LogErrors"):
        return
    import traceback
    where = [f"line {f.lineno} in {f.name}"
             for f in traceback.extract_tb(error.__traceback__)
             if f.filename == os.path.abspath(__file__)]
    line = (f"{datetime.datetime.now().isoformat(timespec='seconds')} "
            f"{VERSION} {type(error).__name__}: {', '.join(where[-3:])}\n")
    path = os.path.join(data_dir(), "errors.log")
    try:
        os.makedirs(data_dir(), mode=0o700, exist_ok=True)
        if os.path.exists(path) and os.path.getsize(path) > 100_000:
            os.replace(path, path + ".old")
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass


def plans_off():
    """Group Policy can turn plans off, for records or works-council rules."""
    return policy("DisablePlans")


def launcher_place():
    """Where the sign-in launcher lives: ("file", path) for a test folder,
    ("run", key) for the HKCU Run value on Windows, or (None, None)."""
    # The tests set "" for no launcher, so they never touch the real one.
    if STARTUP_DIR is not None:
        if not STARTUP_DIR:
            return None, None
        return "file", os.path.join(STARTUP_DIR, "hello-world-daily.cmd")
    if os.name == "nt":
        return "run", RUN_KEY
    return None, None


def legacy_launcher():
    """The Startup .cmd that versions before 1.23 wrote, on Windows only."""
    if STARTUP_DIR is not None or os.name != "nt" or not os.environ.get("APPDATA"):
        return None
    return os.path.join(os.environ["APPDATA"], "Microsoft", "Windows",
                        "Start Menu", "Programs", "Startup",
                        "hello-world-daily.cmd")


def launcher_on():
    kind, where = launcher_place()
    if kind == "file":
        return os.path.exists(where)
    if kind == "run":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, where) as key:
                winreg.QueryValueEx(key, RUN_VALUE)
            return True
        except OSError:
            return False
    return False


# Choices, not notes: Delete everything keeps them.
# On-or-off choices, each false unless turned on. --set NAME on|off changes
# any of them; the window's Options has the ones people look for.
SWITCHES = ("nudge", "open_after", "no_weekends", "name", "no_startup_visits",
            "long_history", "hide_finished", "expire_same", "no_count",
            "numbers", "close_after_done", "colon_prompts")
SETTINGS = ("streak", "tips", "text", "offered", "offer_skips", "lang",
            "remind_at") + SWITCHES


def new_state():
    return {"visits": [], "intent": None, "streak": False}


MAX_PLAN = 200
# A plan can be a few things with ; between them, each finished on its own.
MAX_PARTS = 5
SAVED_PLAN = "Saved. Type done when you finish it, or it asks next time you open this."
MAX_FINISHED = 7
# With "long_history" on, finished plans are kept this long instead.
LONG_FINISHED = 60


def finished_cap(state):
    return LONG_FINISHED if state.get("long_history") else MAX_FINISHED
SHOWN_AFTER_DONE = 3


# Windows primary language IDs, for the translations at the end of this file.
WINDOWS_LANGUAGES = {0x0A: "es", 0x0C: "fr", 0x16: "pt", 0x07: "de",
                     0x11: "ja", 0x12: "ko", 0x01: "ar", 0x0D: "he"}
# Whole language IDs, checked first: regional variants, and Simplified
# Chinese only where Windows shows it (China and Singapore).
WINDOWS_VARIANTS = {0x0C0C: "fr-CA", 0x0816: "pt-PT", 0x0804: "zh", 0x1004: "zh"}
# Older consoles draw these scripts as "?", and right-to-left text runs
# backwards in one, so the text screen stays in English for them.
WINDOW_ONLY = ("zh", "ja", "ko", "ar", "he")
RIGHT_TO_LEFT = ("ar", "he")
LANGUAGES = {}
# Each in its own language, so anyone can find theirs.
LANGUAGE_NAMES = {"en": "English", "es": "Español", "fr": "Français",
                  "fr-CA": "Français (Canada)", "pt": "Português",
                  "pt-PT": "Português (Portugal)", "de": "Deutsch",
                  "zh": "中文 (简体)", "ja": "日本語", "ko": "한국어",
                  "ar": "العربية", "he": "עברית"}
# The language this person chose, read from their file; None follows Windows.
CHOSEN_LANGUAGE = None


def language():
    """The code of the language to show: the person's choice, else the
    Windows display language when there is a translation for it, else "en".
    Policy can force English, and the text screen shows English for the
    scripts in WINDOW_ONLY."""
    code = windows_language() if CHOSEN_LANGUAGE not in LANGUAGE_NAMES else CHOSEN_LANGUAGE
    if policy("ForceEnglish") or code in WINDOW_ONLY and not WINDOW:
        return "en"
    return code


def windows_language():
    if LANGUAGE is not None:
        return LANGUAGE
    if os.name != "nt":
        return "en"
    try:
        import ctypes
        whole = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFFFF
    except (AttributeError, OSError):
        return "en"
    return WINDOWS_VARIANTS.get(whole) or WINDOWS_LANGUAGES.get(whole & 0x3FF, "en")


def translation():
    """The data for the person's language, or None for English."""
    return LANGUAGES.get(language())


def tr(text):
    """The text in the person's language. The English text is the key."""
    data = translation()
    return data["text"].get(text, text) if data else text


# Controls, format marks such as bidi overrides, private-use and surrogate
# code points go. Unassigned ones (Cn) stay, so emoji newer than the bundled
# Python's Unicode tables survive.
DROPPED = {"Cc", "Cf", "Co", "Cs", "Zl", "Zp"}
MAX_MARKS = 4


def tidy(text):
    """One printable line: tabs and odd spaces become spaces, controls go."""
    text = "".join(" " if c.isspace() else c for c in text)
    kept, marks = [], 0
    for c in text:
        kind = unicodedata.category(c)
        # ZWNJ and ZWJ are format marks, but Persian, Indic scripts and emoji
        # sequences need them.
        # LRM and RLM only steer the text next to them, unlike overrides.
        if kind in DROPPED and c not in "\u200c\u200d\u200e\u200f":
            continue
        # A pile of combining marks on one letter draws over the lines above.
        marks = marks + 1 if kind in ("Mn", "Me") else 0
        if marks > MAX_MARKS:
            continue
        kept.append(c)
    text = " ".join("".join(kept).split())
    # Nothing but joiners would show as an empty plan.
    return text if text.strip("\u200c\u200d ") else ""


def clean(text):
    return tidy(tidy(text)[:MAX_PLAN].rstrip(" \u200c\u200d"))


def typed_plan(raw):
    """Clean a typed plan, and say so when it is cut."""
    if len(tidy(raw)) > MAX_PLAN:
        say(tr("Shortened to {n} characters.").format(n=MAX_PLAN))
    return clean(raw)


def day(value):
    """The date as a canonical string, or ValueError."""
    if not isinstance(value, str):
        raise ValueError("not a date")
    return datetime.date.fromisoformat(value).isoformat()


def backup_name(path):
    """notes.json.bak, or a numbered name when an earlier backup exists. Under
    the TimestampBackups policy, notes.json.<date-time>.bak instead. The
    MaxBackups policy deletes the oldest beyond that many first."""
    keep = policy_value("MaxBackups", "number")
    if keep:
        folder, base = os.path.split(path)
        try:
            old = sorted((os.path.getmtime(os.path.join(folder, n)), n)
                         for n in os.listdir(folder)
                         if n.startswith(base + ".") and ".bak" in n)
        except OSError:
            old = []
        for _, n in old[:max(0, len(old) - keep + 1)]:
            try:
                os.remove(os.path.join(folder, n))
            except OSError:
                pass
    if policy("TimestampBackups"):
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        name, n = f"{path}.{stamp}.bak", 1
        while os.path.exists(name):
            n += 1
            name = f"{path}.{stamp}-{n}.bak"
        return name
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
        para(tr("Your saved file was damaged, so hello-world set it aside as a "
                "backup copy and started fresh. Your earlier days and plan "
                "could not be read. Menu option 4 deletes the backup."))
        say(tr("Backup copy: ") + os.path.basename(backup))
        say(tr("In the folder: ") + data_dir())
        say()
        return state, True
    # Off unless turned on. Files from before 1.29.0 saved true for everyone,
    # so those people keep it until they turn it off.
    if raw.get("streak") is True:
        state["streak"] = True
    if raw.get("tips") is False:
        state["tips"] = False
    if raw.get("offered") is True:
        state["offered"] = True
    if raw.get("text") is True:
        state["text"] = True
    for key in SWITCHES:
        if raw.get(key) is True:
            state[key] = True
    global PROMPT_COLON
    PROMPT_COLON = bool(state.get("colon_prompts"))
    for key in ("opens", "run", "best_run"):
        n = raw.get(key)
        if isinstance(n, int) and not isinstance(n, bool) and 0 < n < 100000:
            state[key] = n
    try:
        state["previous_date"] = day(raw.get("previous_date"))
    except ValueError:
        pass
    if raw.get("remind_at") in REMINDER_TIMES:
        state["remind_at"] = raw["remind_at"]
    global CHOSEN_LANGUAGE
    CHOSEN_LANGUAGE = None
    if raw.get("lang") in LANGUAGE_NAMES:
        state["lang"] = CHOSEN_LANGUAGE = raw["lang"]
    try:
        if day(raw.get("notified")) <= today().isoformat():
            state["notified"] = day(raw["notified"])
    except ValueError:
        pass
    # Changes only when everything is deleted. commit() compares it, so a
    # window opened before a delete can't write its old notes back.
    epoch = raw.get("epoch")
    state["epoch"] = (epoch if isinstance(epoch, str) and len(epoch) <= 64
                      and all(c in "0123456789abcdef" for c in epoch) else "")
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
    # Only recent visits are kept: enough for "welcome back" and the
    # days-in-a-row count, and too few to read as an attendance record.
    oldest = (today() - datetime.timedelta(days=KEEP_VISIT_DAYS)).isoformat()
    state["visits"] = sorted(v for v in set(visits) if oldest <= v <= now)[-MAX_VISITS:]
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
        state["finished"] = finished[-finished_cap(state):]
    if (state.get("expire_same") and state.get("previous")
            and state.get("previous_date", "9999")
            < (today() - datetime.timedelta(days=30)).isoformat()):
        state.pop("previous")
        state.pop("previous_date")
    # With plans turned off by policy, plan text is neither shown nor kept: it
    # is dropped here, so the next save leaves it out of the file.
    if plans_off():
        state["intent"] = None
        for key in ("previous", "done", "finished"):
            state.pop(key, None)
    # Without the days-in-a-row count, only the latest visit is needed, so
    # nothing reads like a record of the days someone opened it.
    if policy("HideDaysInARow") or not state["streak"]:
        state["visits"] = state["visits"][-1:]
    return state, True


# The layout of notes.json. load() still checks every field by type.
SCHEMA = 1


def file_form(state):
    """What goes in the file: the state, holding at most MAX_VISITS dates."""
    out = {"schema": SCHEMA}
    out.update({k: v for k, v in state.items() if not (k == "epoch" and not v)})
    out["visits"] = sorted(set(state["visits"]))[-MAX_VISITS:]
    # The same rule as load(): with no days-in-a-row count, one date.
    if policy("HideDaysInARow") or not state.get("streak"):
        out["visits"] = out["visits"][-1:]
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
    if WINDOW:
        return False
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
    """Return the typed text, or None when nobody can answer.

    A prompt longer than the window is wrapped, and only its last line is
    left for the answer, so the choices never run off a magnified screen.
    """
    if not interactive():
        return None
    if PROMPT_COLON and prompt.endswith(" > "):
        prompt = prompt[:-3] + ": "
    lines = []
    for part in prompt.split("\n"):
        lines += textwrap.wrap(part, width(), break_on_hyphens=False,
                               break_long_words=False) or [""]
    for line in lines[:-1]:
        say(line)
    global INTERRUPTED
    try:
        answer = input(lines[-1] + " ").strip()
        INTERRUPTED = 0.0
        return answer
    except KeyboardInterrupt:
        say()  # the prompt is still on this line; start the next one cleanly
        # One press skips the question; a second within two seconds closes.
        if time.monotonic() - INTERRUPTED < 2:
            raise Quit from None
        INTERRUPTED = time.monotonic()
        return None
    except (EOFError, OSError, UnicodeError):
        return None


def strict_yes():
    """Yes words, with the one-letter yes of the person's language."""
    return STRICT_YES + LETTER_YES.get(language(), ())


def is_yes(text):
    return (text or "").lower().strip(TRIM) in strict_yes() + DONE_WORDS + DID_WORDS


def is_no(text):
    return (text or "").lower().strip(TRIM) in NO


def not_a_choice(word, choices):
    """Name what was typed, and say what would have worked."""
    shown = tidy(word)
    if len(shown) > 30:
        shown = shown[:30] + "..."
    say(tr('Sorry, "{shown}" is not one of the choices.').format(shown=shown)
        + " " + choices)


def ask_choice(prompt, yes, no, hint, tries=3):
    """Ask until the answer is recognised. Returns "yes", "no", "" or None.

    "" means Enter, None means nobody could answer or the answers were not
    understood three times, so the caller treats it as no answer.
    """
    for _ in range(tries):
        answer = ask(prompt)
        if answer is None:
            return None
        text = answer.lower().strip(TRIM)
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


def launcher_command():
    """The command the launcher runs, or None for a folder it can't quote.

    It runs pythonw.exe, so no console opens at sign-in. A launcher left
    behind after an uninstall names a program that is gone, and Windows
    skips it.
    """
    script = os.path.abspath(__file__)
    if any(c in script + window_python() for c in '"%'):
        return None
    return f'"{window_python()}" -I "{script}" --startup'


def remove_legacy_launcher():
    """Delete an old Startup .cmd launcher; True when there was one."""
    path = legacy_launcher()
    if not path or not os.path.isfile(path) or os.path.islink(path):
        return False
    clear_launcher_temps(path)
    try:
        os.remove(path)
        return True
    except OSError:
        return False


def clear_launcher_temps(path):
    """Remove temp copies a killed launcher write left in the Startup folder."""
    folder, name = os.path.split(path)
    try:
        names = os.listdir(folder)
    except OSError:
        return
    for n in names:
        if n.startswith(name + ".") and n.endswith(".tmp"):
            try:
                os.remove(os.path.join(folder, n))
            except OSError:
                pass


def remind(on, quiet=False, window=False):
    """Turn the sign-in launcher on or off. True when it worked."""
    kind, where = launcher_place()
    if not kind:
        say(tr("The sign-in reminder works on Windows only."))
        return False
    if on and policy("DisableSignInLauncher"):
        say(tr("Your organization has turned off opening at sign-in."))
        return False
    if on:
        command = launcher_command()
        if not command:
            say(tr("The reminder cannot be set up from this folder."))
            return False
        try:
            if kind == "file":
                write_launcher_file(where, command)
            else:
                import winreg
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, where) as key:
                    winreg.SetValueEx(key, RUN_VALUE, 0, winreg.REG_SZ, command)
                remove_legacy_launcher()
                reminder_keys(True)
        except (OSError, UnicodeEncodeError):
            say(tr("Could not set up the reminder."))
            return False
        if quiet:
            pass
        elif window:
            para(tr("Done. A reminder comes when you sign in, if there is a "
                    "plan to ask about."))
        else:
            say(tr("Done. hello-world will open once a day when you sign in."))
            say(tr("To stop it, choose option 2 in the menu."))
        return True
    try:
        if kind == "file":
            clear_launcher_temps(where)
            try:
                os.remove(where)
            except FileNotFoundError:
                pass
        else:
            import winreg
            remove_legacy_launcher()
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, where, 0,
                                    winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, RUN_VALUE)
            except FileNotFoundError:
                pass
            reminder_keys(False)
    except OSError:
        say(tr("Could not turn off the sign-in reminder."))
        return False
    if not quiet:
        say(tr("Done. The sign-in reminder is off."))
    return True


def write_launcher_file(path, command):
    """Write the test stand-in for the Run value, whole, then move it in."""
    clear_launcher_temps(path)
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(tmp, "w", encoding="ascii", newline="") as f:
            f.write("@echo off\r\n" + command + "\r\n")
        os.replace(tmp, path)
    except (OSError, UnicodeEncodeError):
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def show_saved(state, full=True):
    d = today()
    recent = [v for v in state["visits"]
              if 0 <= (d - datetime.date.fromisoformat(v)).days <= 6]
    if full:
        say(tr("Saved on this computer in:"))
        say("  " + data_file())
    else:
        say(tr("Saved in your own user folder on this computer."))
    para(tr("Days you opened it in the last {days} days: {n} (last 7 days: "
            "{recent})").format(days=KEEP_VISIT_DAYS, n=len(state["visits"]),
                                recent=len(recent)))
    if state.get("done"):
        say(tr("Times you marked a plan done: {n}").format(n=state["done"]))
    if state["intent"]:
        say(wrapped(tr("Your current plan: "), state["intent"]["text"]))
    if state.get("previous"):
        say(wrapped(tr("Earlier plan (for same): "), state["previous"]))
    show_finished(state)
    say(tr("Days-in-a-row message: shown.") if state["streak"] else
        tr("Days-in-a-row message: hidden."))
    if launcher_place()[0] and text_screen(state):
        say(tr("Opens by itself at sign-in: turned off by your organization.")
            if policy("DisableSignInLauncher") else
            tr("Opens by itself at sign-in: on.") if launcher_on() else
            tr("Opens by itself at sign-in: off."))
    elif launcher_place()[0]:
        say(tr("Reminder when you sign in: turned off by your organization.")
            if policy("DisableSignInLauncher") else
            tr("Reminder when you sign in: on.") if launcher_on() else
            tr("Reminder when you sign in: off."))
    para(tr("It never leaves this computer. Others who can read this "
            "computer's files, such as IT staff, could read it."))
    if full:
        say(tr("After tidying, the file holds only this:"))
        say(json.dumps(file_form(state), indent=2, ensure_ascii=False))


def reset(state):
    """True when deleted, False when a delete failed, None when declined."""
    answer = ask(tr("Delete all saved notes, dates and plans on this "
                    "computer? (y or n, Enter to cancel) > "))
    word = (answer or "").lower().strip(TRIM)
    if word not in strict_yes():
        say(tr("Nothing was deleted."))
        if word in QUIT_WORDS:
            raise Quit
        return None
    with file_lock():
        return delete_everything(state)


def delete_everything(state):
    """The body of reset() once confirmed, run while holding the lock."""
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
        say(tr("Could not delete everything."))
        if failed:
            say(tr("Delete these yourself:"))
            for path in failed:
                say("  " + path)
        if listing_failed:
            say(tr("Could not list the folder, so backup copies may remain:"))
            say("  " + data_dir())
        return False
    settings = {k: state[k] for k in SETTINGS if k in state}
    state.clear()
    state.update(new_state())
    state.update(settings)
    # A marker with a new epoch instead of no file, so another open window
    # can tell the notes were deleted.
    state["epoch"] = os.urandom(8).hex()
    say(tr("Done. Everything saved was deleted."))
    if settings:
        say(tr("Your settings were kept."))
    if save(state):
        say(tr("Another open hello-world window cannot put it back."))
    else:
        para(tr("Close any other open hello-world window, or it may save its "
                "notes again."))
    return True


@contextlib.contextmanager
def file_lock():
    """Hold notes.lock while a change reads and writes the file.

    Without it, a delete in one window could land between another window's
    read and write, and that write would bring the deleted notes back.
    """
    try:
        os.makedirs(data_dir(), mode=0o700, exist_ok=True)
        fd = os.open(os.path.join(data_dir(), "notes.lock"),
                     os.O_RDWR | os.O_CREAT, 0o600)
    except OSError:
        yield
        return
    locked = False
    try:
        # ponytail: gives up after about 5 seconds and goes ahead unlocked,
        # so a stuck window can never freeze another one.
        for _ in range(50):
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError:
                time.sleep(0.1)
        yield
    finally:
        if locked:
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
        os.close(fd)


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
    # The day an earlier plan was put aside, so same can let go of it.
    if state.get("previous") != base.get("previous"):
        if state.get("previous"):
            state["previous_date"] = today().isoformat()
        else:
            state.pop("previous_date", None)
    with file_lock():
        return merge_and_save(state, base, soft)


def merge_and_save(state, base, soft):
    """The body of commit(), run while holding the lock."""
    fresh, ok = load(repair=False)
    if not ok:
        return False
    # A missing file has no marker at all: deleted by hand or set aside as
    # damaged, not by Delete everything, which always writes a new marker.
    if "epoch" in base and "epoch" in fresh and fresh["epoch"] != base["epoch"]:
        para(tr("Everything saved was deleted in another window, so this was "
                "not saved."))
        state.clear()
        state.update(fresh)
        base.clear()
        base.update(copy.deepcopy(fresh))
        return False
    if (fresh.get("done", 0) > base.get("done", 0)
            and state.get("done", 0) > base.get("done", 0)):
        say(tr("The other open window had also finished a plan."))
    for key in set(state) | set(base):
        if key in ("visits", "done", "offer_skips", "finished"):
            continue
        if state.get(key) == base.get(key):
            continue
        if key in soft and fresh.get(key) != base.get(key):
            if key == "intent":
                say(tr("The other open window changed the plan, so its plan "
                       "is kept."))
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
        fresh["finished"] = finished[-finished_cap(state):]
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


COMMAND_WORDS = MENU_WORDS + HELP_WORDS + QUIT_WORDS + DONE_WORDS + PLAN_WORDS
# Someone declining to plan is not making an error, so these get no lecture.
DECLINE_WORDS = NO_WORDS + ("none", "nothing", "skip", "nada", "ninguno", "saltar",
                      "rien", "nichts")


def is_command(text, again=None):
    """A command word typed where a plan is asked is not a plan."""
    word = (text or "").lower().strip(TRIM)
    if word in DECLINE_WORDS:
        return True
    if word in COMMAND_WORDS:
        para(tr("That looks like a command, not a plan, so nothing was saved.")
             + " " + (again or tr("Type plan at the last prompt to set one.")))
        return True
    # A menu number typed one question too early, or a stray key.
    if word and not any(c.isalpha() for c in word) and all(
            c.isdigit() or c.isspace() or unicodedata.category(c).startswith("P")
            for c in word):
        para(tr("A plan needs a word or two, so nothing was saved."))
        return True
    return False


def is_same(text):
    return (text or "").lower().strip(TRIM) in SAME_WORDS


def show_finished(state, limit=MAX_FINISHED):
    """The last few finished plans, so finishing has a visible payoff.

    After done and on welcome back only the last few are read out; option 1
    lists every one kept.
    """
    items = state.get("finished") or []
    if not items or state.get("hide_finished"):
        return
    say()
    say(tr("Finished lately:"))
    for item in list(reversed(items))[:limit]:
        say(wrapped("  " + tr("{date}: ").format(date=long_date(
            datetime.date.fromisoformat(item["date"]))), item["text"]))


def reuse(state, raw):
    """Typing `same` brings back the plan before this one, if there is one."""
    if is_same(raw) and state.get("previous"):
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
        label = (tr("Your plan today: ") if old["date"] == iso else
                 tr("Your plan from {date}: ").format(date=long_date(
                     datetime.date.fromisoformat(old["date"]))))
        say(wrapped(label, old["text"]))
    same = bool(state.get("previous"))
    if same:
        say(wrapped(tr("Earlier plan: "), state["previous"]))
    if after_done:
        prompt = (tr("Type the next plan, same to reuse the earlier plan, or "
                     "Enter to close > ") if same else
                  tr("Type the next plan, or Enter to close > "))
    elif old:
        prompt = (tr("Type today's plan, same to reuse the earlier plan, or "
                     "Enter to keep it > ") if same else
                  tr("Type today's plan, or Enter to keep it > "))
    else:
        prompt = (tr("Type today's plan, same to reuse the earlier plan, or "
                     "Enter to go back > ") if same else
                  tr("Type today's plan, or Enter to go back > "))
    typed = ask(prompt)
    word = (typed or "").lower().strip(TRIM)
    if after_done and not word:
        say(tr("Closing."))
        return True
    if word in QUIT_WORDS:
        raise Quit
    # Another window may have saved while this prompt waited.
    refresh(state, can_save)
    old = state["intent"]
    if is_same(typed) and not state.get("previous"):
        say(tr("There is no earlier plan to reuse yet. Nothing changed."))
        return False
    if is_command(typed, tr("Type your plan, or press Enter to go back.")):
        return False
    text = typed_plan(reuse(state, typed) or "")
    if not text:
        say(tr("Nothing changed."))
        return False
    base = copy.deepcopy(state)
    # Changing today's plan is a correction, so only a plan carried over from
    # an earlier day is kept for same.
    if old and old["text"] != text and old["date"] != iso:
        state["previous"] = old["text"]
    state["intent"] = {"text": text, "date": iso}
    if commit(state, base, can_save):
        para(tr(SAVED_PLAN))
        nudge_if_several(text)
    else:
        undo(state, base)
        say(tr("Could not save that on this computer. Your plan is unchanged."))
    return False


def forget_finished(state, can_save):
    """Remove one finished plan from the file, and leave everything else."""
    refresh(state, can_save)
    shown = list(reversed(state.get("finished") or []))
    if not shown:
        say(tr("No finished plans are saved."))
        return
    for n, item in enumerate(shown, 1):
        say(wrapped(f"  {n}  " + tr("{date}: ").format(
            date=long_date(datetime.date.fromisoformat(item["date"]))),
                    item["text"]))
    numbers = [str(n) for n in range(1, len(shown) + 1)]
    for _ in range(3):
        choice = ask(tr("Type the number to forget (1 to {n}), or Enter to "
                        "keep them all > ").format(n=len(shown)))
        if (choice or "").lower().strip(TRIM) in QUIT_WORDS:
            raise Quit
        if not choice or choice in numbers:
            break
        para(tr('There is no number "{typed}" on the list. Type a number from '
                "1 to {n}, or press Enter to keep them all.").format(
                    typed=tidy(choice)[:30], n=len(shown)))
    if not choice or choice not in numbers:
        say(tr("Nothing changed."))
        return
    item = shown[int(choice) - 1]
    also_same = state.get("previous") == item["text"] and ask_choice(
        tr("Also forget it as the earlier plan for same? "
           "(y or n, Enter to keep it for same) > "),
        strict_yes(), NO_WORDS,
        tr("Type y or n, or press Enter to keep it for same.")) == "yes"
    refresh(state, can_save)
    if item not in state.get("finished", []):
        say(tr("That plan was already forgotten. Nothing changed."))
        return
    base = copy.deepcopy(state)
    state["finished"] = [i for i in state["finished"] if i != item]
    if also_same and state.get("previous") == item["text"]:
        state.pop("previous")
    kept = state.get("previous") == item["text"]
    if commit(state, base, can_save):
        say(wrapped(tr("Forgotten: "), item["text"]))
        if kept:
            say(tr("Same still has it."))
    else:
        undo(state, base)
        say(tr("Could not save that on this computer. Nothing changed."))


def menu(state, can_save=True, iso=None, alone=False):
    # The options are read out once. After that only the prompt comes back,
    # and m lists them again.
    listed = False
    while True:
        say()
        reminding = launcher_on()
        if not listed:
            say(tr("Options"))
            say("  1  " + tr("Show what is saved on this computer"))
            # With the window, sign-in brings a notification, not the program.
            say("  2  " + ((
                tr("Open once a day at sign-in (turned off by your "
                   "organization)") if text_screen(state) else
                tr("Reminder when you sign in (turned off by your "
                   "organization)"))
                if policy("DisableSignInLauncher") and not reminding else
                (tr("Turn off: open once a day at sign-in (now on)")
                 if text_screen(state) else
                 tr("Turn off: reminder when you sign in (now on)"))
                if reminding else
                (tr("Turn on: open once a day at sign-in (now off)")
                 if text_screen(state) else
                 tr("Turn on: reminder when you sign in (now off)"))))
            say("  3  " + (tr("Days-in-a-row message (hidden by your "
                              "organization)")
                           if policy("HideDaysInARow") else
                           tr("Hide the days-in-a-row message (now shown)")
                           if state["streak"] else
                           tr("Show the days-in-a-row message (now hidden)")))
            say("  4  " + tr("Delete everything saved"))
            say("  5  " + tr("Help"))
            if plans_off():
                say("  6  " + tr("Set today's plan (turned off by your "
                                 "organization)"))
                say("  7  " + tr("Forget a finished plan (turned off by your "
                                 "organization)"))
            else:
                say("  6  " + tr("Set or change today's plan"))
                say("  7  " + tr("Forget one finished plan"))
            say("  8  " + (tr("Thought and tip (hidden by your organization)")
                           if policy("HideThoughtAndTip") else
                           tr("Hide the thought and tip (now shown)")
                           if state.get("tips", True) else
                           tr("Show the thought and tip (now hidden)")))
            say("  9  " + (tr("Window or text screen (set by your organization)")
                           if policy("UseTextScreen") else
                           tr("Use a window with buttons (now this text screen)")
                           if state.get("text") else
                           tr("Use this text screen (now a window with buttons)")))
            say(" 10  " + (tr("Language (set by your organization)")
                           if policy("ForceEnglish") else
                           tr("Language (now {name})").format(
                               name=LANGUAGE_NAMES.get(state.get("lang"))
                               or tr("following Windows"))))
            say(" 11  " + (tr("Mark today's plan done (plans are turned off)")
                           if plans_off() else tr("Mark today's plan done")))
            say("  " + tr("Enter") + "  " + (tr("Close") if alone else
                                             tr("Back to the last prompt")))
            listed = True
            choice = ask(tr("Choose 1 to 11, or Enter to go back > "))
        else:
            choice = ask(tr("Choose 1 to 11, m to list the options, or Enter to "
                            "go back > "))
        if not choice:
            return
        if choice.lower().strip(TRIM) in QUIT_WORDS:
            raise Quit
        if choice.lower() in MENU_WORDS + LIST_WORDS:
            listed = False
            continue
        if choice.lower() in HELP_WORDS:
            choice = "5"
        if choice == "1":
            if not refresh(state, can_save):
                para(tr("The saved file could not be read just now, so this "
                        "may be out of date."))
            show_saved(state, full=False)
            if (ask(tr("Type full to see the whole file, or Enter to go on > "))
                    or "").lower() in FULL_WORDS:
                refresh(state, can_save)
                say(json.dumps(file_form(state), indent=2, ensure_ascii=False))
        elif choice == "2":
            if remind(not reminding, window=not text_screen(state)):
                # A choice made here is final; the offer must not come back.
                refresh(state, can_save)
                base = copy.deepcopy(state)
                state["offered"] = True
                if not commit(state, base, can_save):
                    undo(state, base)
                    say(tr("Could not save that choice on this computer."))
        elif choice == "3" and policy("HideDaysInARow"):
            say(tr("Your organization has hidden the days-in-a-row message."))
        elif choice == "3":
            refresh(state, can_save)
            base = copy.deepcopy(state)
            state["streak"] = not state["streak"]
            if commit(state, base, can_save):
                say(tr("Done. The days-in-a-row message is on.")
                    if state["streak"] else
                    tr("Done. The days-in-a-row message is off."))
            else:
                undo(state, base)
                say(tr("Could not save that choice on this computer."))
        elif choice == "4":
            reset(state)
        elif choice == "5":
            say(tr(MENU_HELP))
        elif choice in ("6", "7") and plans_off():
            say(tr("Plans are turned off by your organization."))
        elif choice == "6":
            set_plan(state, can_save, iso)
        elif choice == "7":
            forget_finished(state, can_save)
        elif choice == "8" and policy("HideThoughtAndTip"):
            say(tr("Your organization has hidden the thought and tip."))
        elif choice == "8":
            refresh(state, can_save)
            base = copy.deepcopy(state)
            if state.get("tips", True):
                state["tips"] = False
            else:
                state.pop("tips", None)
            if commit(state, base, can_save):
                say(tr("Done. The thought and tip are on.")
                    if state.get("tips", True) else
                    tr("Done. The thought and tip are off."))
            else:
                undo(state, base)
                say(tr("Could not save that choice on this computer."))
        elif choice == "11" and plans_off():
            say(tr("Plans are turned off by your organization."))
        elif choice == "11":
            mark_done_now(state, can_save, today())
        elif choice == "10" and policy("ForceEnglish"):
            say(tr("Your organization shows hello-world in English."))
        elif choice == "10":
            choose_language(state, can_save)
        elif choice == "9" and policy("UseTextScreen"):
            say(tr("Your organization has set hello-world to open as a text "
                   "screen."))
        elif choice == "9":
            refresh(state, can_save)
            base = copy.deepcopy(state)
            if state.pop("text", None) is None:
                state["text"] = True
            if commit(state, base, can_save):
                say(tr("Done. The Start menu opens this text screen.")
                    if state.get("text") else
                    tr("Done. The Start menu opens a window with buttons."))
            else:
                undo(state, base)
                say(tr("Could not save that choice on this computer."))
        else:
            not_a_choice(choice, tr("Type 1 to 11, or press Enter to go back."))


def set_language(state, can_save, code):
    """Save a language for this person, or None to follow Windows. Returns
    True when saved. It shows from the next open."""
    refresh(state, can_save)
    base = copy.deepcopy(state)
    if code:
        state["lang"] = code
    else:
        state.pop("lang", None)
    if commit(state, base, can_save):
        return True
    undo(state, base)
    return False


def choose_language(state, can_save):
    """Menu option 10: pick a language by number."""
    codes = list(LANGUAGE_NAMES) + [None]
    for n, code in enumerate(codes, 1):
        say(f"  {n}  " + (LANGUAGE_NAMES[code] if code else tr("Follow Windows")))
    answer = ask(tr("Type a number from 1 to {n}, or Enter to keep it > ")
                 .format(n=len(codes)))
    word = (answer or "").strip(TRIM)
    if word.lower() in QUIT_WORDS:
        raise Quit
    if word not in [str(n) for n in range(1, len(codes) + 1)]:
        say(tr("Nothing changed."))
        return
    if set_language(state, can_save, codes[int(word) - 1]):
        say(tr("Done. The new language shows next time you open hello-world."))
    else:
        say(tr("Could not save that choice on this computer."))


def offer_reminder(state, can_save, planned=False):
    """Ask whether to open at sign-in, right after a plan or from visit two on.

    It is asked once. Enter is final too, and an unclear answer asks again on
    a later visit.
    """
    if (not launcher_place()[0] or policy("DisableSignInLauncher")
            or state.get("offered") or launcher_on()
            or not (planned or len(state["visits"]) >= 2)):
        return
    answer = ask_choice(
        tr("Want it to open once a day when you sign in? "
           "(y or n, Enter for not now) > ")
        if plans_off() else
        tr("Want it to open once a day when you sign in so it can ask about "
           "your plan? (y or n, Enter for not now) > "),
        strict_yes(), NO_THANKS,
        tr("Type y or n, or press Enter for not now."))
    if answer is None:
        say(tr("That was not understood. It will ask again on a later visit."))
        return
    refresh(state, can_save)
    base = copy.deepcopy(state)
    if answer == "yes":
        if not remind(True):
            para(tr("It will ask again on a later visit. Menu option 2 also "
                    "turns it on."))
            say()
            return
        state["offered"] = True
    elif answer == "no":
        state["offered"] = True
        say(tr("No problem. Menu option 2 turns it on later."))
    else:
        skips = state.get("offer_skips", 0) + 1
        state["offer_skips"] = skips
        if skips >= MAX_OFFER_SKIPS:
            state["offered"] = True
            para(tr("Okay. It won't ask again. Menu option 2 turns it on."))
        else:
            para(tr("Okay. It will ask again on a later visit. Type n to stop it."))
    if not commit(state, base, can_save):
        say(tr("Could not save that choice on this computer."))
    say()


def plan_parts(text):
    """The things in one plan: "Call Ana; send the report" is two. A plan
    of more than MAX_PARTS keeps the extra ones together in the last part."""
    parts = [part.strip() for part in text.split(";") if part.strip()]
    if len(parts) > MAX_PARTS:
        parts = parts[:MAX_PARTS - 1] + ["; ".join(parts[MAX_PARTS - 1:])]
    return parts or [text]


def finish_plan(state, text, d, parts=None):
    report_usage("plan finished")
    return _finish_plan(state, text, d, parts)


def _finish_plan(state, text, d, parts=None):
    """Count a finished plan, dated d, one finished row and one done for each
    thing in it. `parts` finishes only those indexes; returns the rest of the
    plan, or "". `same` only ever holds unfinished plans."""
    if state.get("previous") == text:
        state.pop("previous")
    every = plan_parts(text)
    chosen = [every[i] for i in sorted(set(parts))] if parts else every
    for part in chosen:
        if not state.get("no_count"):
            state["done"] = min(state.get("done", 0) + 1, 99999)
        state["finished"] = (state.get("finished", [])
                             + [{"text": part, "date": d.isoformat()}])[-finished_cap(state):]
    return "; ".join(part for i, part in enumerate(every)
                     if parts and i not in parts)


def done_lines(state, d):
    """Shown only once the save has worked, and with the merged count, so
    nobody is congratulated for something that was not recorded."""
    data = translation()
    lines = data["done"] if data else DONE_LINES
    return [lines[d.toordinal() % len(lines)]]


def ask_parts(parts):
    """"Did you do them?" for a plan of several things. Returns (answer,
    parts done): ("yes", None) for all, ("yes", [0, 2]) for some, or the
    "no", "" or None of ask_choice()."""
    say(tr("Last time you planned:"))
    for n, part in enumerate(parts, 1):
        say(wrapped(f"  {n}  ", part))
    numbers = [str(n) for n in range(1, len(parts) + 1)]
    hint = tr("Type y for all, n for not yet, or the numbers you did, such "
              "as 1 3. Enter skips.")
    for _ in range(3):
        typed = ask(tr("Did you do them? (y for all, n for not yet, numbers "
                       "for the ones you did, Enter to skip) > "))
        if typed is None:
            return None, None
        text = typed.lower().strip(TRIM)
        words = text.replace(",", " ").split()
        if not text:
            return "", None
        if text in QUIT_WORDS:
            raise Quit
        if words and all(w in numbers for w in words):
            done = sorted({int(w) - 1 for w in words})
            return "yes", (None if len(done) == len(parts) else done)
        if text in strict_yes() + DONE_WORDS + DID_WORDS:
            return "yes", None
        if text in NO:
            return "no", None
        not_a_choice(typed, hint)
    return None, None


def finish_day(plan_day, d):
    """The day a plan was finished. Asked only when it was set over a day ago,
    since the next morning almost always means the plan's own day."""
    if (d - plan_day).days <= 1:
        return plan_day
    days = [plan_day + datetime.timedelta(days=n)
            for n in range((d - plan_day).days + 1)]
    if len(days) > 7:
        days = days[:1] + days[-6:]
    # Numbers, like the menu: a letter here would clash with the y just typed.
    say(tr("When did you finish it?"))
    for n, when in enumerate(days, 1):
        say(f"  {n}  " + (tr("Today") if when == d else long_date(when)))
    numbers = [str(n) for n in range(1, len(days) + 1)]
    for _ in range(3):
        answer = ask(tr("Type a number from 1 to {n}, or Enter for 1 > ")
                     .format(n=len(days)))
        word = (answer or "").lower().strip(TRIM)
        if not word:
            return days[0]
        if word in QUIT_WORDS:
            raise Quit
        if word in numbers:
            return days[int(word) - 1]
        not_a_choice(answer, tr("Type a number from 1 to {n}, or press Enter.")
                     .format(n=len(days)))
    return days[0]


def nudge_if_several(text):
    """A plan of several things joined together is hard to finish. A list
    with ; is several on purpose, and each part is finished on its own."""
    if ";" in text:
        return
    padded = f" {text.lower()} "
    if any(joint in padded for joint in (" and ", " & ", " y ")) or "+" in text:
        para(tr("That looks like more than one thing. Finishing the first "
                "part still counts."))


def mark_done_now(state, can_save, d):
    """Same-day done: the plan on screen is finished, so say so at once."""
    refresh(state, can_save)
    plan = state["intent"]
    if not plan:
        para(tr("There is no plan to mark as done. Type plan to set one."))
        return False
    base = copy.deepcopy(state)
    finish_plan(state, plan["text"], d)
    state["intent"] = None
    if not commit(state, base, can_save):
        undo(state, base)
        say(tr("Could not save that on this computer. The plan is still open."))
        return False
    for line in done_lines(state, d):
        say(line)
    show_finished(state, SHOWN_AFTER_DONE)
    return True


def policy_reminder(state):
    """Under the TurnOnReminder policy, the reminder starts on for anyone who
    hasn't made a choice yet. Turning it off afterwards stays off."""
    if (policy("TurnOnReminder") and not state.get("offered")
            and not policy("DisableSignInLauncher") and launcher_place()[0]
            and not reminder_on()):
        if remind(True, quiet=True, window=not text_screen(state)):
            state["offered"] = True


def count_visit(state, d):
    """With "numbers" on, count a new day: the days opened, the current run
    (each visit within four days of the last) and the longest run."""
    if not state.get("numbers") or d.isoformat() in state["visits"]:
        return
    last = state["visits"][-1] if state["visits"] else None
    close = last and (d - datetime.date.fromisoformat(last)).days <= 4
    state["opens"] = min(state.get("opens", 0) + 1, 99999)
    state["run"] = min(state.get("run", 0) + 1, 99999) if close else 1
    state["best_run"] = max(state.get("best_run", 0), state["run"])


def numbers_text(state):
    """"My numbers", for the window and --numbers."""
    if not state.get("numbers"):
        return tr("My numbers are off. Turn them on under Options, or with "
                  "--set numbers on.")
    return "\n".join([
        tr("Days you opened hello-world: {n}").format(n=state.get("opens", 0)),
        tr("Longest run of days: {n}").format(n=state.get("best_run", 0)),
        tr("Plans finished: {n}").format(n=state.get("done", 0))])


def week_text(state, d):
    """What was finished since Monday."""
    monday = (d - datetime.timedelta(days=d.weekday())).isoformat()
    items = [i for i in state.get("finished", []) if i["date"] >= monday]
    if not items:
        return tr("Nothing finished yet this week. That is fine.")
    return "\n".join([tr("This week you finished {n}:").format(n=len(items))] + [
        "  " + tr("{date}: ").format(date=long_date(datetime.date.fromisoformat(
            i["date"]))) + i["text"] for i in items])


# Where --export and Options save the plans; None is the Documents folder.
EXPORT_DIR = None


def export_plans(state):
    """Write the current and finished plans to a Markdown file in the
    person's Documents folder. Returns the path, or None."""
    folder = EXPORT_DIR or os.path.join(os.path.expanduser("~"), "Documents")
    path = os.path.join(folder, "hello-world plans.md")
    lines = ["# hello-world", ""]
    if state["intent"]:
        lines += ["## " + tr("Your current plan: ").strip(), ""]
        lines += [f"- {part}" for part in plan_parts(state["intent"]["text"])] + [""]
    if state.get("finished"):
        lines += ["## " + tr("Finished lately:"), ""]
        lines += [f"- {i['date']}: {i['text']}" for i in reversed(state["finished"])]
    try:
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines).rstrip() + "\n")
        return path
    except OSError:
        return None


def launcher_value():
    """The Run value's text, or the test launcher file's, or ""."""
    kind, where = launcher_place()
    try:
        if kind == "file":
            with open(where, encoding="ascii") as f:
                return f.read()
        if kind == "run":
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, where) as key:
                return winreg.QueryValueEx(key, RUN_VALUE)[0]
    except (OSError, UnicodeDecodeError):
        pass
    return ""


def tidy_launcher():
    """Apply the launcher policy, move a pre-1.23 launcher to the Run value,
    and rewrite a 1.23.0 to 1.27.0 value, which opened a console, to the one
    that starts pythonw.exe."""
    if launcher_on() and "hello.cmd --startup" in launcher_value():
        remind(True, quiet=True)
    if policy("DisableSignInLauncher"):
        if launcher_on() or legacy_launcher() and os.path.isfile(legacy_launcher()):
            remind(False, quiet=True)
    elif remove_legacy_launcher():
        # An old Startup .cmd becomes the Run value, keeping the person's choice.
        remind(True)


def plan_on_open(state, d):
    """The plan as it stands on day d, and whether an old one was put away.

    A plan dated after d becomes d's plan. One set over two weeks ago moves
    to "previous", for same. Nothing is saved here.
    """
    intent = state["intent"]
    if intent and intent["date"] > d.isoformat():
        intent["date"] = d.isoformat()  # the clock moved back; it is today's plan now
    # A plan kept day after day still counts from the day it was first set.
    since = intent.get("since", intent["date"]) if intent else None
    if intent and (d - datetime.date.fromisoformat(since)).days > 14:
        state["previous"] = intent["text"]
        return None, True
    return intent, False


def asks_followup(intent, d):
    """True when "Did you do it?" is due: a plan from an earlier day, skipped
    fewer than two times, with plans allowed."""
    return bool(intent and intent["date"] < d.isoformat()
                and intent.get("skips", 0) < 2 and not plans_off())


def answer_plan(state, can_save, d, choice, text, parts=None):
    """Answer "Did you do it?" for the plan `text` from the window or the
    sign-in reminder: "yes", "no" (not yet, kept for today) or "skip".

    Returns (saved, message). Finishing counts on day d, the day it was
    answered, which is the date people expect to see in the finished list.
    With `parts`, "yes" finishes only those things and keeps the rest for
    today.
    """
    refresh(state, can_save)
    intent = state["intent"]
    if not (intent and intent["text"] == text and asks_followup(intent, d)):
        return False, tr("The other open window changed the plan, so its plan "
                         "is kept.")
    base = copy.deepcopy(state)
    rest = ""
    if choice == "yes":
        rest = finish_plan(state, text, d, parts)
        state["intent"] = rest and {"text": rest, "date": d.isoformat(),
                                    "since": intent.get("since", intent["date"])}
        state["intent"] = state["intent"] or None
    elif choice == "no":
        state["intent"] = {"text": text, "date": d.isoformat(),
                           "since": intent.get("since", intent["date"])}
    else:
        state["intent"] = dict(intent, skips=intent.get("skips", 0) + 1)
    if not commit(state, base, can_save):
        undo(state, base)
        return False, tr("Could not save that on this computer. Your answer "
                         "was not counted.")
    if choice == "yes":
        return True, done_lines(state, d)[0] + (
            " " + tr("The rest is kept for today.") if rest else "")
    return True, tr("Kept for today.") if choice == "no" else tr(
        "Your plan is still open.")


def daily(startup):
    d = today()
    iso = d.isoformat()
    person = interactive()
    # Repairing sets the file aside with a notice nobody might read.
    state, can_save = load(repair=person or not policy("LeaveDamagedFile"))
    base = copy.deepcopy(state)
    seen_today = iso in state["visits"]
    typed_new = False
    answered = False
    if startup and seen_today:
        return
    tidy_launcher()
    policy_reminder(state)
    if not seen_today:
        count_visit(state, d)
    first = not state["visits"]
    intent, expired = plan_on_open(state, d)

    say(greeting(state))
    header = long_date(d)
    say(header[0].upper() + header[1:])
    say()

    if expired:
        para(tr("Your plan from over two weeks ago was put away. Type same "
                "at the plan prompt to bring it back."))
        say()

    if first:
        para(tr("Press Enter at each question to skip it, and once more to "
                "close. That's it."))
        say()
        welcome = [tr("Welcome.")]
        if not policy("HideThoughtAndTip"):
            welcome.append(tr("Each day you get one thought and one small "
                              "thing to try, the same for everyone."))
        if not plans_off():
            welcome.append(tr("If you type a plan, it asks next time how it "
                              "went. Your notes stay on this computer and are "
                              "never sent anywhere. Like any work file they "
                              "are not secret, so keep them to everyday "
                              "tasks."))
        welcome.append(tr("Type menu at the end for the options."))
        para(" ".join(welcome))
        say()
    elif not seen_today:
        last = datetime.date.fromisoformat(state["visits"][-1])
        row = in_a_row(state["visits"], d)
        if (d - last).days > 7:
            say(tr("Welcome back. Glad you are here."))
            show_finished(state, SHOWN_AFTER_DONE)
            say()
        elif (state["streak"] and not policy("HideDaysInARow")
              and (row in (3, 7, 14) or row % 30 == 0)):
            say(tr("You have opened this {row} days in a row. Nice to see "
                   "you.").format(row=row))
            say()

    quitting = False
    wants_menu = False
    try:
        # Asked until it is answered, also on a second open the same day,
        # but two skips mean "stop asking"; the plan then shows as still open.
        if (intent and intent["date"] < iso and intent.get("skips", 0) < 2
                and not plans_off()):
            parts = plan_parts(intent["text"])
            if len(parts) == 1:
                say(wrapped(tr("Last time you planned: "), intent["text"]))
                answer = ask_choice(
                    tr("Did you do it? (y for yes, n for not yet, Enter to skip) > "),
                    strict_yes() + DONE_WORDS + DID_WORDS, NO,
                    tr("Type y or n, or press Enter to skip."))
                some = None
            else:
                answer, some = ask_parts(parts)
            if answer == "yes":
                answered = True
                when = finish_day(datetime.date.fromisoformat(intent["date"]), d)
                # Saved now, so the answer is heard now.
                rest = finish_plan(state, intent["text"], when, some)
                state["intent"] = rest and {
                    "text": rest, "date": iso,
                    "since": intent.get("since", intent["date"])} or None
                if commit(state, base, can_save):
                    base = copy.deepcopy(state)
                    intent = state["intent"]
                    for line in done_lines(state, d):
                        say(line)
                    if rest:
                        say(tr("The rest is kept for today."))
                else:
                    # A delete in another window also lands here, so take
                    # the plan from the state, never the copy held above.
                    undo(state, base)
                    intent = state["intent"]
                    say(tr("Could not save that on this computer. Your answer "
                           "was not counted."))
            elif answer == "no":
                answered = True
                keep = ask_choice(
                    tr("That is fine. Keep it for today? (y or n, Enter to "
                       "keep it) > "),
                    strict_yes() + NOT_YET, NO_WORDS,
                    tr("Type y to keep it, n to clear it, or press Enter to "
                       "keep it."))
                if keep == "no":
                    state["previous"] = intent["text"]
                    intent = None
                    say(tr("Cleared. Type same at a plan prompt if you want it back."))
                else:
                    intent = {"text": intent["text"], "date": iso,
                              "since": intent.get("since", intent["date"])}
                    say(tr("Kept for today."))
            elif answer is None and person:
                say(tr("That was not understood. Your plan is left as it was."))
            elif answer is not None:
                intent = dict(intent, skips=intent.get("skips", 0) + 1)
                say(tr("Your plan is still open."))
            say()

        if state.get("tips", True) and not policy("HideThoughtAndTip"):
            thought, tip = todays_pair(d)
            say(tr("Thought for today:"))
            say(indent(thought))
            say()
            say(tr("Try this today:"))
            say(indent(tip))
            say()

        if intent and intent["date"] == iso:
            say(wrapped(tr("Your plan for today: "), intent["text"]))
            say()
        elif intent:
            # Not answered, or skipped twice; it must not vanish.
            when = long_date(datetime.date.fromisoformat(intent["date"]))
            say(tr("Still open since {date}:").format(date=when))
            say(indent(intent["text"]))
            say()
        if (not seen_today and not plans_off()
                and not (intent and intent["date"] == iso)):
            skip = (tr("(Enter to skip)") if not intent else
                    tr("(A plan typed here replaces the old one. Enter to skip)"))
            if state.get("previous") and not intent:
                say(wrapped(tr("Earlier plan: "), state["previous"]))
                skip = tr("(Type same to reuse it, or Enter to skip)")
            question = (tr("What is one thing you want to get done today?")
                        + "\n" + skip + " > ")
            text = ask(question)
            # The welcome mentions the menu, so someone may type it here
            # first. It opens, rather than being told where it lives.
            if (text or "").lower().strip(TRIM) in MENU_WORDS + HELP_WORDS:
                wants_menu = True
                text = ""
            if (text or "").lower().strip(TRIM) in QUIT_WORDS:
                raise Quit
            if is_same(text) and not state.get("previous"):
                say(tr("There is no earlier plan to reuse yet. Nothing was saved."))
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
        report_usage("opened")
        if typed_new:
            report_usage("plan set")
        if not seen_today and not (startup and state.get("no_startup_visits")):
            state["visits"] = (state["visits"] + [iso])[-MAX_VISITS:]
        state["intent"] = intent
        # A plan only tidied here (a future date made today, an old plan
        # cleared) must not overwrite one the other window saved meanwhile.
        soft = () if answered or typed_new else ("intent", "previous")
        if not commit(state, base, can_save, soft):
            undo(state, base)
            intent = state["intent"]
            para(tr("Your notes could not be saved on this computer. This "
                    "screen still works."))
        else:
            intent = state["intent"]
            if typed_new:
                para(tr(SAVED_PLAN))
                nudge_if_several(intent["text"])
                say()
            if not seen_today and not quitting and not wants_menu:
                try:
                    offer_reminder(state, can_save, planned=typed_new)
                except Quit:
                    quitting = True
                # The offer re-reads the file, so pick up the plan it read.
                intent = state["intent"]
    if quitting:
        say(tr("Closing."))
        return

    # A message at the very end must stay on screen until the person has read
    # it, because the window closes as soon as the program exits.
    try:
        last_prompt(state, can_save, intent, person, d, iso, wants_menu)
    except Quit:
        say(tr("Closing."))


def last_prompt(state, can_save, intent, person, d, iso, open_menu=False):
    """Loop at the last prompt until the person closes the window."""
    if open_menu:
        menu(state, can_save, iso)
        intent = state["intent"]
    while True:
        planned = bool(intent and person and state["intent"] is intent)
        # q, x and the other close words still work; naming them only
        # added a letter nobody could guess the meaning of.
        prompt = (tr("Type menu, or Enter to close > ") if plans_off() else
                  tr("Type done, plan or menu, or Enter to close > ")
                  if planned else
                  tr("Type plan or menu, or Enter to close > "))
        answer = (ask(prompt) or "").lower().strip(TRIM)
        if answer in DONE_WORDS + PLAN_WORDS and plans_off():
            say(tr("Plans are turned off by your organization."))
            continue
        if answer in DONE_WORDS and person:
            closing = False
            if mark_done_now(state, can_save, d):
                say()
                closing = set_plan(state, can_save, iso, after_done=True)
            intent = state["intent"]
            if closing or state.get("close_after_done") and intent:
                break
            continue
        elif answer in PLAN_WORDS and person:
            set_plan(state, can_save, iso)
            intent = state["intent"]
            continue
        elif answer in MENU_WORDS + HELP_WORDS:
            menu(state, can_save, iso)
            intent = state["intent"]
            continue
        elif answer in QUIT_WORDS:
            pass
        elif answer:
            not_a_choice(answer, tr("Type done, plan or menu, or press "
                                    "Enter to close.")
                         if planned else
                         tr("Type plan or menu, or press Enter to close."))
            continue
        break


def run(argv):
    # Before lowercasing, so a path keeps its case.
    if len(argv) == 2 and argv[0].lower() == "--check-content":
        return check_content(argv[1])
    if len(argv) == 3 and argv[0].lower() == "--check-content" and argv[2].lower() == "--local":
        return check_content(argv[1], local=True)
    argv = [a.lower() for a in argv]
    if argv[:1] == ["--console"]:
        # The window opens the text screens with this, in a console of their own.
        if os.name == "nt":
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW("hello-world")
        argv = argv[1:]
    if argv == ["--menu"]:
        state, can_save = load()
        try:
            menu(state, can_save, today().isoformat(), alone=True)
        except Quit:
            pass
        return 0
    if argv in (["/?"], ["-?"], ["/help"], ["-help"], ["help"]):
        argv = ["--help"]
    if argv == ["--plain"]:
        say(GREETING)
        return 0
    if argv == ["--plain-local"]:
        say(tr(GREETING))
        return 0
    if len(argv) == 3 and argv[0] == "--set" and argv[1] in SWITCHES and argv[2] in ("on", "off"):
        state, can_save = load()
        base = copy.deepcopy(state)
        if argv[2] == "on":
            state[argv[1]] = True
        else:
            state.pop(argv[1], None)
        if commit(state, base, can_save):
            say(tr("Saved."))
            return 0
        say(tr("Could not save that choice on this computer."))
        return 1
    if argv in (["--week"], ["--numbers"], ["--export"]):
        state, _ = load(repair=False)
        if argv == ["--week"]:
            say(week_text(state, today()))
        elif argv == ["--numbers"]:
            say(numbers_text(state))
        else:
            path = export_plans(state)
            say(tr("Saved to {path}").format(path=path) if path else
                tr("Could not save that on this computer."))
            return 0 if path else 1
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
            say(tr("The saved file can't be read right now, or it is damaged."))
            say(tr("Nothing was changed. Saved in: ") + data_dir())
            return 1
        show_saved(state)
        return 0
    if argv == ["--reset"]:
        if not interactive():
            say(tr("Deleting saved notes needs a person at the keyboard."))
            return 1
        state, _ = load(repair=False)
        # Answering no is the person's choice; only a failed delete is an error.
        try:
            return 1 if reset(state) is False else 0
        except Quit:
            return 0
    if len(argv) == 2 and argv[0] == "--remind" and argv[1] in ("on", "off"):
        return 0 if remind(argv[1] == "on") else 1
    if len(argv) == 2 and argv[0] == "--count-sign-in" and argv[1] in ("on", "off"):
        state, can_save = load()
        base = copy.deepcopy(state)
        if argv[1] == "on":
            state.pop("no_startup_visits", None)
        else:
            state["no_startup_visits"] = True
        if commit(state, base, can_save):
            say(tr("Saved."))
            return 0
        say(tr("Could not save that choice on this computer."))
        return 1
    if len(argv) == 2 and argv[0] == "--streak" and argv[1] in ("on", "off"):
        state, can_save = load()
        base = copy.deepcopy(state)
        state["streak"] = argv[1] == "on"
        if commit(state, base, can_save):
            say(tr("Done. The days-in-a-row message is on.")
                if state["streak"] else
                tr("Done. The days-in-a-row message is off."))
            return 0
        say(tr("Could not save that choice on this computer."))
        return 1
    if len(argv) == 1 and argv[0] in ("--remind", "--streak"):
        say(tr("{option} needs on or off. Here are the options.")
            .format(option=argv[0]))
    else:
        say(tr("Unknown option: {option}. Here are the options.")
            .format(option=tidy(" ".join(argv))[:60]))
    say()
    say(help_text())
    return 2


def check_content(path, local=False):
    """--check-content: say whether an organization content file is usable.
    In English, for administrators' tickets, unless --local is added."""
    t = tr if local else (lambda text: text)
    try:
        with open(path, encoding="utf-8-sig") as f:
            data = json.loads(f.read(200_001))
    except OSError as e:
        say(t("Can't read {path}: {error}").format(path=tidy(path), error=e.strerror))
        return 1
    except (ValueError, RecursionError):
        say(t("The file isn't valid JSON, or is over 200,000 characters."))
        return 1
    problems = content_problems(data, t)
    for problem in problems:
        say(problem)
    if problems:
        return 1
    say(t("OK: {thoughts} thoughts and {tips} tips.").format(
        thoughts=len(data["thoughts"]), tips=len(data["tips"])))
    return 0


def main():
    if "--utf8" in [a.lower() for a in sys.argv[1:]]:
        sys.argv = [a for a in sys.argv if a.lower() != "--utf8"]
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            pass
    args = [a.lower() for a in sys.argv[1:]]
    # pythonw.exe has no stdout, so the window and the sign-in run start here.
    if (args == ["--window"] or args[:1] == ["--answer"] and len(args) == 2
            or args == ["--startup"] and sys.stdout is None):
        try:
            return gui(args)
        except Exception as e:
            log_error(e)
            return 1
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
        log_error(e)
        try:
            print(f"hello.py: something went wrong ({type(e).__name__}). "
                  "Contact IT.", file=sys.stderr, flush=True)
        except Exception:
            pass
        return 1


# ==== Window ====
# The Start menu runs hello.py --window through pythonw.exe, so there is no
# console. The window is built from standard Windows controls, which screen
# readers and high contrast already know. The text screens above stay for
# anyone who prefers them, behind menu option 9 and the UseTextScreen policy.


def text_screen(state):
    """True when this person or the organization chose the text screen."""
    return policy("UseTextScreen") or state.get("text") is True


def console_python():
    folder, name = os.path.split(sys.executable)
    return (os.path.join(folder, "python.exe") if name.lower() == "pythonw.exe"
            else sys.executable)


def window_python():
    folder, name = os.path.split(sys.executable)
    return (os.path.join(folder, "pythonw.exe")
            if os.name == "nt" and name.lower() == "python.exe" else sys.executable)


def open_console(*args):
    """Show the text screens in a console window of their own."""
    import subprocess
    subprocess.Popen([console_python(), "-I", os.path.abspath(__file__),
                      "--console", *args],
                     creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))


def quietly(fn, *args):
    """Run fn and return (its result, what it said) for the window to show."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        result = fn(*args)
    return result, " ".join(out.getvalue().split())


def gui(args):
    """--window, --answer and a sign-in run under pythonw.exe."""
    global WINDOW
    WINDOW = True
    # pythonw.exe has no stdout, and anything said goes to the window instead.
    with contextlib.redirect_stdout(io.StringIO()):
        if args[0] == "--answer":
            return answer_reminder(args[1])
        if args == ["--startup"]:
            return sign_in()
        return show_window()


# A list in tests: what would have been opened with the default program.
STARTED = None


def send_feedback():
    """Open a new mail to the FeedbackAddress policy's address in the
    person's own mail program. hello-world itself sends nothing."""
    address = feedback_address()
    if not address:
        return False
    from urllib.parse import quote
    link = f"mailto:{address}?subject={quote('hello-world ' + VERSION)}"
    if STARTED is not None:
        STARTED.append(link)
        return True
    try:
        os.startfile(link)
        return True
    except (AttributeError, OSError):
        return False


def show_window():
    state, _ = load(repair=False)
    if os.name != "nt" or text_screen(state):
        open_console()
        return 0
    try:
        Window(Visit()).run()
    except Exception as e:
        log_error(e)
        # A PC where the window can't be drawn still gets the text screens.
        open_console()
    return 0


# Reminders show under this name. Answering one opens hello-world:done,
# hello-world:notyet or hello-world:open, which run hello.py --answer.
APP_ID = "hello-world"


# A list in tests: the reminder tasks that would be created, by time, and
# None for a removed one. Nothing outside the program sets it.
TASKS = None
# The task folder is shared by everyone on the PC, so each person's task
# carries their user name.
TASK_NAME = "hello-world reminder " + (os.environ.get("USERNAME") or "user")
REMINDER_TIMES = ("08:00", "09:00", "10:00", "13:00")


def reminder_task(at):
    """Create the daily reminder task at "HH:MM", or remove it for None.
    It runs as this user, so it needs no administrator. True when it worked."""
    if TASKS is not None:
        TASKS.append(at)
        return True
    if os.name != "nt":
        return False
    import subprocess
    import tempfile
    from xml.sax.saxutils import escape
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    if not at:
        r = subprocess.run(["schtasks", "/Delete", "/F", "/TN", TASK_NAME],
                           capture_output=True, creationflags=flags)
        return r.returncode == 0 or not task_on()
    # StartWhenAvailable runs it at the next sign-in when the PC was off at
    # the time, which schtasks /Create can only set from XML.
    xml = ('<?xml version="1.0" encoding="UTF-16"?>'
           '<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">'
           f'<Triggers><CalendarTrigger><StartBoundary>2026-01-01T{at}:00</StartBoundary>'
           '<ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>'
           '</CalendarTrigger></Triggers><Settings>'
           '<StartWhenAvailable>true</StartWhenAvailable>'
           '<DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>'
           '<StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>'
           '<ExecutionTimeLimit>PT5M</ExecutionTimeLimit>'
           '<MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>'
           '</Settings><Actions><Exec>'
           f'<Command>{escape(window_python())}</Command>'
           f'<Arguments>-I "{escape(os.path.abspath(__file__))}" --startup</Arguments>'
           '</Exec></Actions></Task>')
    fd, path = tempfile.mkstemp(suffix=".xml")
    try:
        with os.fdopen(fd, "w", encoding="utf-16") as f:
            f.write(xml)
        r = subprocess.run(["schtasks", "/Create", "/F", "/TN", TASK_NAME,
                            "/XML", path], capture_output=True, creationflags=flags)
        return r.returncode == 0
    except OSError:
        return False
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def task_on():
    if TASKS is not None:
        return bool(TASKS and TASKS[-1])
    if os.name != "nt":
        return False
    import subprocess
    return subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME],
                          capture_output=True,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                          ).returncode == 0


def reminder_on():
    """True when the reminder comes at sign-in or at a set time."""
    return launcher_on() or task_on()


def reminder_keys(on):
    """Register, or remove, the reminder's name and its answer links for this
    user. Neither needs administrator rights."""
    if launcher_place()[0] != "run":
        return
    import winreg
    classes = CLASSES_KEY
    names = (classes + "\\" + APP_ID + r"\shell\open\command",
             classes + "\\" + APP_ID + r"\shell\open",
             classes + "\\" + APP_ID + r"\shell", classes + "\\" + APP_ID,
             classes + r"\AppUserModelId" + "\\" + APP_ID)
    if not on:
        for name in names:
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, name)
            except OSError:
                pass
        return
    command = (f'"{window_python()}" -I "{os.path.abspath(__file__)}" '
               '--answer "%1"')
    for name, values in ((names[4], {"DisplayName": "hello-world"}),
                         (names[3], {"": "URL:hello-world", "URL Protocol": ""}),
                         (names[0], {"": command})):
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, name) as key:
            for value, data in values.items():
                winreg.SetValueEx(key, value, 0, winreg.REG_SZ, data)


def reminder_due(state, d):
    """What the reminder says today: the plan to ask about, "" for "One thing
    to get done today?" when the person asked for that on days with no plan,
    or None for nothing.

    Once a day, not after hello-world was opened that day, not on weekends
    when the person chose that, and not on the organization's holidays.
    """
    iso = d.isoformat()
    if (iso in state["visits"] or state.get("notified") == iso or holiday(d)
            or state.get("no_weekends") and d.weekday() >= 5):
        return None
    intent, expired = plan_on_open(copy.deepcopy(state), d)
    if asks_followup(intent, d) and not expired:
        return intent["text"]
    if state.get("nudge") and not plans_off() and not (
            intent and intent["date"] == iso):
        return ""
    return None


def sign_in():
    """The launcher's run at sign-in, in pythonw.exe."""
    d = today()
    state, can_save = load()
    if text_screen(state):
        open_console("--startup")
        return 0
    text = reminder_due(state, d)
    if text is None:
        return 0
    base = copy.deepcopy(state)
    state["notified"] = d.isoformat()
    # Unsaved, it would come again at the next sign-in today.
    if commit(state, base, can_save) and not (
            show_reminder(text) if text else show_nudge()):
        show_window()
    return 0


def show_nudge():
    """The reminder on a day with no plan: one line, and Open."""
    return notify(
        '<toast activationType="protocol" launch="hello-world:open">'
        '<visual><binding template="ToastGeneric">'
        f'<text>{xml_text(tr("One thing to get done today? Open hello-world to plan it."))}</text>'
        '</binding></visual><actions>'
        f'<action content="{xml_text(tr("&Open").replace("&", ""))}" '
        'activationType="protocol" arguments="hello-world:open"/>'
        '</actions></toast>')


def xml_text(text):
    from xml.sax.saxutils import escape
    return escape(text, {'"': "&quot;"})


def show_reminder(text):
    """Show a Windows notification with the plan and two answers. False when
    Windows would not show it, such as where PowerShell is locked down."""
    escape = xml_text
    return notify('<toast activationType="protocol" launch="hello-world:open">'
           '<visual><binding template="ToastGeneric">'
           f'<text>{escape(tr("Last time you planned: ") + text)}</text>'
           f'<text>{escape(tr("Did you do it?"))}</text></binding></visual>'
           '<actions>'
           f'<action content="{escape(tr("&Done").replace("&", ""))}" '
           'activationType="protocol" arguments="hello-world:done"/>'
           f'<action content="{escape(tr("&Not yet").replace("&", ""))}" '
           'activationType="protocol" arguments="hello-world:notyet"/>'
           f'<action content="{escape(tr("S&kip").replace("&", ""))}" '
           'activationType="protocol" arguments="hello-world:skip"/>'
           '</actions></toast>')


def notify(xml):
    """Show one Windows notification. False when Windows would not show it."""
    if SHOWN is not None:
        SHOWN.append(xml)
        return True
    if os.name != "nt":
        return False
    import base64
    import subprocess
    # The XML goes in as base64, so no plan text can break out of the script.
    data = base64.b64encode(xml.encode("utf-8")).decode("ascii")
    script = (
        "$ErrorActionPreference='Stop'\n"
        f"$x=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{data}'))\n"
        "$null=[Windows.UI.Notifications.ToastNotificationManager,"
        "Windows.UI.Notifications,ContentType=WindowsRuntime]\n"
        "$null=[Windows.Data.Xml.Dom.XmlDocument,"
        "Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime]\n"
        "$d=New-Object Windows.Data.Xml.Dom.XmlDocument\n$d.LoadXml($x)\n"
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("
        f"'{APP_ID}').Show([Windows.UI.Notifications.ToastNotification]::new($d))")
    exe = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32",
                       "WindowsPowerShell", "v1.0", "powershell.exe")
    try:
        return subprocess.run(
            [exe, "-NoProfile", "-NonInteractive", "-EncodedCommand",
             base64.b64encode(script.encode("utf-16-le")).decode("ascii")],
            capture_output=True, timeout=60,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def answer_reminder(link):
    """hello-world:done or :notyet from the reminder, answered with no window;
    :open opens the window. Anything else is refused."""
    link = link.strip().lower().rstrip("/")
    word = link[len(APP_ID) + 1:] if link.startswith(APP_ID + ":") else ""
    if word == "open":
        return show_window()
    if word not in ("done", "notyet", "skip"):
        return 2
    d = today()
    state, can_save = load()
    intent = state["intent"]
    if asks_followup(intent, d):
        saved, message = answer_plan(
            state, can_save, d,
            {"done": "yes", "notyet": "no"}.get(word, "skip"), intent["text"])
        if saved and word == "done" and not state.get("open_after"):
            # The window says this out loud; the reminder had no way to.
            notify('<toast><visual><binding template="ToastGeneric">'
                   f'<text>{xml_text(message)}</text></binding></visual></toast>')
    if state.get("open_after"):
        return show_window()
    return 0


class Visit:
    """One opening of the window: what it shows, and what its buttons do.
    The window only draws this, so the tests drive it directly."""

    def __init__(self):
        self.d = today()
        self.iso = self.d.isoformat()
        (self.state, self.can_save), said = quietly(load)
        state, d = self.state, self.d
        base = copy.deepcopy(state)
        seen = self.iso in state["visits"]
        first = not state["visits"]
        quietly(tidy_launcher)
        quietly(policy_reminder, state)
        intent, expired = plan_on_open(state, d)
        notes = [said] if said else []
        if expired:
            notes.append(tr("Your plan from over two weeks ago was put away. "
                            "Type same at the plan prompt to bring it back."))
        if first:
            notes.append(tr("Welcome."))
            if not policy("HideThoughtAndTip"):
                notes.append(tr("Each day you get one thought and one small "
                                "thing to try, the same for everyone."))
            if not plans_off():
                notes.append(tr("If you type a plan, it asks next time how it "
                                "went. Your notes stay on this computer and are "
                                "never sent anywhere. Like any work file they "
                                "are not secret, so keep them to everyday "
                                "tasks."))
        elif not seen:
            row = in_a_row(state["visits"], d)
            if (d - datetime.date.fromisoformat(state["visits"][-1])).days > 7:
                notes.append(tr("Welcome back. Glad you are here."))
            elif (state["streak"] and not policy("HideDaysInARow")
                  and (row in (3, 7, 14) or row % 30 == 0)):
                notes.append(tr("You have opened this {row} days in a row. "
                                "Nice to see you.").format(row=row))
        state["intent"] = intent
        report_usage("opened")
        if not seen:
            count_visit(state, d)
            state["visits"] = (state["visits"] + [self.iso])[-MAX_VISITS:]
        saved, said = quietly(commit, state, base, self.can_save,
                              ("intent", "previous"))
        if not saved:
            undo(state, base)
            notes.append(said or tr("Your notes could not be saved on this "
                                    "computer. This screen still works."))
        self.note = " ".join(notes)
        intent = state["intent"]
        self.followup = intent["text"] if asks_followup(intent, d) else None
        self.pair = (todays_pair(d) if state.get("tips", True)
                     and not policy("HideThoughtAndTip") else None)

    def plan(self):
        """Today's plan, or "" when there is none for today."""
        intent = self.state["intent"]
        return intent["text"] if intent and intent["date"] == self.iso else ""

    def answer(self, choice, parts=None):
        """"yes", "no" or "skip" to "Did you do it?", with `parts` for the
        things done when only some were. Returns the message."""
        (saved, message), _ = quietly(answer_plan, self.state, self.can_save,
                                      self.d, choice, self.followup, parts)
        if saved:
            self.followup = None
        return message

    def save(self, typed):
        """The plan typed in the box. Returns (close, message, saved).

        Nothing new to save closes the window. A saved plan keeps it open to
        say so, and Enter again closes it. A refused plan keeps it open to
        say why.
        """
        if plans_off():
            return True, "", False
        quietly(refresh, self.state, self.can_save)
        if not tidy(typed) or clean(typed) == self.plan():
            return True, "", False
        if is_same(typed) and not self.state.get("previous"):
            return False, tr("There is no earlier plan to reuse yet. Nothing "
                             "was saved."), False
        command, said = quietly(is_command, typed, tr("Type your plan in the box."))
        if command:
            # A word like "skip" or "none" is a choice to plan nothing.
            return not said, said, False
        text = clean(reuse(self.state, typed))
        state = self.state
        base = copy.deepcopy(state)
        old = state["intent"]
        if old and old["text"] != text and old["date"] != self.iso:
            state["previous"] = old["text"]
        state["intent"] = {"text": text, "date": self.iso}
        saved, said = quietly(commit, state, base, self.can_save)
        if not saved:
            undo(state, base)
            return False, said or tr("Could not save that on this computer. "
                                     "Your plan is unchanged."), False
        self.followup = None
        _, several = quietly(nudge_if_several, text)
        return False, " ".join([tr("Saved.")] + ([several] if several else [])), True

    def saved_summary(self):
        """What is saved, in words, and where the file is. The raw file stays
        in the text menu, for anyone who wants it."""
        quietly(refresh, self.state, self.can_save)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            show_saved(self.state, full=False)
        return (out.getvalue().strip() + "\n\n" + tr("Saved on this computer in:")
                + "\n" + data_file())

    def clear(self):
        """Drop today's plan; same can bring it back. Returns the message."""
        quietly(refresh, self.state, self.can_save)
        base = copy.deepcopy(self.state)
        if self.state["intent"]:
            self.state["previous"] = self.state["intent"]["text"]
        self.state["intent"] = None
        saved, said = quietly(commit, self.state, base, self.can_save)
        if not saved:
            undo(self.state, base)
            return said or tr("Could not save that on this computer. Your plan "
                              "is unchanged.")
        self.followup = None
        return tr("Cleared. Type same at a plan prompt if you want it back.")

    def delete_all(self):
        """Delete everything saved, as menu option 4 does. Returns the message."""
        def delete():
            with file_lock():
                return delete_everything(self.state)
        _, said = quietly(delete)
        self.followup = None
        return said

    def did_it(self, typed=""):
        """Today's plan, or what was typed over it, is finished. Returns the
        message."""
        if tidy(typed) and clean(typed) != self.plan():
            close, message, saved = self.save(typed)
            if not saved:
                return message
        _, said = quietly(mark_done_now, self.state, self.can_save, self.d)
        # The finished list after it is for the text screen.
        return said.split(tr("Finished lately:"))[0].strip()

    def offer_due(self):
        """True when the window should ask once about the sign-in reminder."""
        return bool(launcher_place()[0] and not policy("DisableSignInLauncher")
                    and not plans_off() and not self.state.get("offered")
                    and not launcher_on())

    def set_reminder(self, on):
        """Turn the reminder on at sign-in, or off. Returns the message."""
        if self.state.get("remind_at") or task_on():
            quietly(reminder_task, None)
            self.setting("remind_at", None)
        worked, said = quietly(remind, on)
        quietly(refresh, self.state, self.can_save)
        base = copy.deepcopy(self.state)
        self.state["offered"] = True
        quietly(commit, self.state, base, self.can_save)
        if not worked:
            return said
        return (tr("Done. A reminder comes when you sign in, if there is a "
                   "plan to ask about.") if on else
                tr("Done. The sign-in reminder is off."))

    def setting(self, key, value):
        """Save one setting; None removes it. Returns False when it could not
        be saved."""
        quietly(refresh, self.state, self.can_save)
        base = copy.deepcopy(self.state)
        if value is None:
            self.state.pop(key, None)
        else:
            self.state[key] = value
        saved, _ = quietly(commit, self.state, base, self.can_save)
        if not saved:
            undo(self.state, base)
        return saved

    def reminder_at(self, at):
        """The reminder at a set time each day instead of at sign-in.
        Returns the message."""
        if not reminder_task(at):
            return tr("Could not set up the reminder.")
        # The links its buttons open are the sign-in reminder's.
        quietly(remind, False, True)
        quietly(reminder_keys, True)
        self.setting("remind_at", at)
        self.setting("offered", True)
        return tr("Done. A reminder comes at {at} each day, if there is a "
                  "plan to ask about.").format(at=at.lstrip("0"))

    def toggle(self, key):
        """Flip "tips" (shown unless False), "streak" or "text" (the text
        screen). Returns False when it could not be saved."""
        quietly(refresh, self.state, self.can_save)
        base = copy.deepcopy(self.state)
        if key == "tips":
            if self.state.get("tips", True):
                self.state["tips"] = False
            else:
                self.state.pop("tips", None)
        elif key == "streak":
            self.state["streak"] = not self.state["streak"]
        elif key in SWITCHES:
            if self.state.pop(key, None) is None:
                self.state[key] = True
        elif self.state.pop("text", None) is None:
            self.state["text"] = True
        saved, _ = quietly(commit, self.state, base, self.can_save)
        if not saved:
            undo(self.state, base)
        return saved


def live_region(hwnd):
    """Mark a label as a polite UI Automation live region, through the
    Dynamic Annotation API, so its changes are announced. Quietly does
    nothing where that isn't available."""
    import ctypes
    import uuid

    class GUID(ctypes.Structure):
        _fields_ = [("data", ctypes.c_byte * 16)]

    class VARIANT(ctypes.Structure):
        _fields_ = [("vt", ctypes.c_ushort), ("r1", ctypes.c_ushort),
                    ("r2", ctypes.c_ushort), ("r3", ctypes.c_ushort),
                    ("value", ctypes.c_longlong), ("pad", ctypes.c_longlong)]

    def guid(text):
        return GUID((ctypes.c_byte * 16).from_buffer_copy(uuid.UUID(text).bytes_le))

    try:
        ole = ctypes.OleDLL("ole32")
        ole.CoInitialize(None)
        services = ctypes.c_void_p()
        clsid = guid("b5f8350b-0548-48b1-a6ee-88bd00b4a5e7")
        iid = guid("6e26e776-04f0-495d-80e4-3330352e3169")
        ole.CoCreateInstance(ctypes.byref(clsid), None, 1, ctypes.byref(iid),
                             ctypes.byref(services))
        vtable = ctypes.cast(ctypes.cast(services, ctypes.POINTER(ctypes.c_void_p))[0],
                             ctypes.POINTER(ctypes.c_void_p))
        # IAccPropServices::SetHwndProp is the seventh method.
        set_prop = ctypes.WINFUNCTYPE(
            ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong,
            ctypes.c_ulong, GUID, VARIANT)(vtable[6])
        # LiveSetting_Property_GUID; 1 is Polite, VT_I4 is 3.
        set_prop(services, hwnd, 0xFFFFFFFC, 0,
                 guid("c12bcd8e-2a8e-4950-8ae7-3625111d58eb"), VARIANT(3, 0, 0, 0, 1, 0))
        release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtable[2])
        release(services)
        return True
    except (AttributeError, OSError, ValueError):
        return False


class Window:
    """The Visit drawn as a standard Windows dialog, through ctypes."""

    # Dialog units: one across is a quarter of an average character, one
    # down an eighth of a line. Windows scales them with the font and DPI.
    WIDTH, MARGIN, LINE = 300, 12, 10
    TITLE, DATE, NOTE, PLANNED, ASK, DONE, NOT_YET, SKIP = range(100, 108)
    THOUGHT_LABEL, THOUGHT, TIP_LABEL, TIP = range(110, 114)
    PLAN_LABEL, PLAN, STATUS, OPTIONS, DID_IT = range(120, 125)
    TICK = 130  # to 134, one tick box for each thing in yesterday's plan
    SAVE, CLOSE = 1, 2  # IDOK and IDCANCEL, so Enter and Esc work

    def __init__(self, visit):
        self.visit = visit
        self.error = None
        self.fonts = []
        self.finished = False  # a plan was finished in this window
        self.asking = bool(visit.followup)

    def lines(self, text):
        per_line = int(self.WIDTH / 4.2)
        # Chinese, Japanese and Korean characters are about two wide.
        units = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)
        return max(1, len(textwrap.wrap(text, per_line)), -(-units // per_line))

    def layout(self):
        """The controls, as (class, id, text, style, x, y, w, h), and the height."""
        v, m, w, line = self.visit, self.MARGIN, self.WIDTH, self.LINE
        static, button, edit = 0x82, 0x80, 0x81
        text_style, tab = 0x80, 0x10000  # SS_NOPREFIX, WS_TABSTOP
        items, y = [], 10

        def add(cls, cid, text, style, x, h, width=w):
            items.append((cls, cid, text, style, x, y, width, h))

        def para(cid, text, gap=6):
            nonlocal y
            h = self.lines(text) * line
            add(static, cid, text, text_style, m, h)
            y += h + gap

        add(static, self.TITLE, greeting(v.state), text_style, m, 20)
        y += 24
        header = long_date(v.d)
        para(self.DATE, header[0].upper() + header[1:], 8)
        if v.note:
            para(self.NOTE, v.note, 8)
        parts = plan_parts(v.followup) if v.followup else []
        if len(parts) > 1:
            para(self.PLANNED, tr("Last time you planned:"), 2)
            para(self.ASK, tr("Tick the ones you did, then click Done. With "
                              "none ticked, Done means all of them."), 2)
            for n, part in enumerate(parts):
                h = self.lines(part) * line
                # A tick box draws & as an underline, so it is doubled.
                add(button, self.TICK + n, part.replace("&", "&&"),
                    tab | 0x3 | 0x2000, m + 6, h,
                    w - 6)  # BS_AUTOCHECKBOX | BS_MULTILINE
                y += h + 2
            y += 4
        elif v.followup:
            para(self.PLANNED, tr("Last time you planned: ") + v.followup, 2)
            para(self.ASK, tr("Did you do it?"), 4)
        if v.followup:
            for n, (cid, label) in enumerate(((self.DONE, tr("&Done")),
                                              (self.NOT_YET, tr("&Not yet")),
                                              (self.SKIP, tr("S&kip")))):
                add(button, cid, label, tab, m + n * 70, 16, 64)
            y += 26
        if v.pair:
            para(self.THOUGHT_LABEL, tr("Thought for today:"), 1)
            para(self.THOUGHT, v.pair[0], 6)
            para(self.TIP_LABEL, tr("Try this today:"), 1)
            para(self.TIP, v.pair[1], 8)
        if not plans_off():
            para(self.PLAN_LABEL, self.plan_label(), 2)
            add(edit, self.PLAN, v.plan(), tab | 0x800000 | 0x80, m, 15)
            y += 19
        add(static, self.STATUS, "" if plans_off() else tr(
            "A few things? Put ; between them."), text_style, m, 2 * line)
        y += 2 * line + 6
        add(button, self.OPTIONS, tr("&Options"), tab, m, 16, 64)
        right = m + w
        # Added left to right, which is the Tab order.
        if not plans_off():
            add(button, self.DID_IT, tr("&I did it"), tab, right - 204, 16, 64)
            add(button, self.SAVE, tr("&Save"), tab | 1, right - 134, 16, 64)
            add(button, self.CLOSE, self.close_label(), tab, right - 64, 16, 64)
        else:
            add(button, self.CLOSE, tr("Close"), tab | 1, right - 64, 16, 64)
        return items, y + 26

    def plan_label(self):
        return (tr("Your plan for today: ").strip() if self.visit.plan() else
                tr("Next plan, if you want one:") if self.finished else
                tr("What is one thing you want to get done today?"))

    def close_label(self):
        return tr("Close") if self.visit.plan() or self.finished else tr("Not today")

    def template(self):
        import struct

        def text(s):
            return (s + "\0").encode("utf-16-le")

        items, height = self.layout()
        self.ids = [item[1] for item in items]
        # WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX, and DS_SETFONT,
        # DS_MODALFRAME and DS_CENTER. WS_EX_APPWINDOW puts it on the taskbar.
        # WS_EX_LAYOUTRTL mirrors the whole dialog for Arabic and Hebrew.
        exstyle = 0x40000 | (0x400000 if language() in RIGHT_TO_LEFT else 0)
        data = struct.pack("<IIH4h", 0x80CA08C0, exstyle, len(items), 0, 0,
                           self.WIDTH + 2 * self.MARGIN, height)
        data += b"\0\0\0\0" + text("hello-world") + struct.pack("<H", 12)
        data += text("Segoe UI")
        for cls, cid, label, style, x, y, w, h in items:
            data += b"\0" * (-len(data) % 4)
            # WS_CHILD | WS_VISIBLE; the box gets WS_EX_CLIENTEDGE.
            data += struct.pack("<IIhhhhH", 0x50000000 | style,
                                0x200 if cls == 0x81 else 0, x, y, w, h, cid)
            data += struct.pack("<HH", 0xFFFF, cls) + text(label) + b"\0\0"
        return data

    def run(self):
        import ctypes
        from ctypes import wintypes as wt
        self.user = user = ctypes.WinDLL("user32", use_last_error=True)
        self.gdi = gdi = ctypes.WinDLL("gdi32")
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        lresult = ctypes.c_ssize_t
        for fn, args, res in (
                ("SendMessageW", [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM], lresult),
                ("GetDlgItem", [wt.HWND, ctypes.c_int], wt.HWND),
                ("SetWindowTextW", [wt.HWND, wt.LPCWSTR], wt.BOOL),
                ("GetWindowTextW", [wt.HWND, wt.LPWSTR, ctypes.c_int], ctypes.c_int),
                ("EndDialog", [wt.HWND, lresult], wt.BOOL),
                ("ShowWindow", [wt.HWND, ctypes.c_int], wt.BOOL),
                ("MessageBoxW", [wt.HWND, wt.LPCWSTR, wt.LPCWSTR, wt.UINT], ctypes.c_int),
                ("CreatePopupMenu", [], wt.HMENU),
                ("AppendMenuW", [wt.HMENU, wt.UINT, ctypes.c_size_t, wt.LPCWSTR], wt.BOOL),
                ("TrackPopupMenu", [wt.HMENU, wt.UINT, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, wt.HWND, ctypes.c_void_p], wt.BOOL),
                ("DestroyMenu", [wt.HMENU], wt.BOOL),
                ("GetWindowRect", [wt.HWND, ctypes.POINTER(wt.RECT)], wt.BOOL),
                ("GetSysColor", [ctypes.c_int], wt.DWORD),
                ("GetSysColorBrush", [ctypes.c_int], wt.HBRUSH),
                ("SetTimer", [wt.HWND, ctypes.c_size_t, wt.UINT, ctypes.c_void_p],
                 ctypes.c_size_t),
                ("DialogBoxIndirectParamW", [wt.HINSTANCE, ctypes.c_void_p, wt.HWND,
                                             ctypes.c_void_p, wt.LPARAM], lresult)):
            getattr(user, fn).argtypes, getattr(user, fn).restype = args, res
        gdi.CreateFontW.argtypes = [ctypes.c_int] * 5 + [wt.DWORD] * 8 + [wt.LPCWSTR]
        gdi.CreateFontW.restype = wt.HFONT
        gdi.SetTextColor.argtypes = gdi.SetBkColor.argtypes = [wt.HDC, wt.DWORD]
        gdi.DeleteObject.argtypes = [wt.HGDIOBJ]
        kernel.GetModuleHandleW.restype = wt.HMODULE
        # Sharp text on scaled displays, and the current look for buttons,
        # which pythonw.exe's own manifest doesn't ask for.
        try:
            user.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except AttributeError:
            pass
        self.visual_styles(ctypes, wt, kernel)
        proc_type = ctypes.WINFUNCTYPE(lresult, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)
        self.proc = proc_type(self.dialog_proc)
        data = self.template()
        buffer = ctypes.create_string_buffer(data, len(data) + 4)
        result = user.DialogBoxIndirectParamW(
            kernel.GetModuleHandleW(None), buffer, None,
            ctypes.cast(self.proc, ctypes.c_void_p), 0)
        for font in self.fonts:
            gdi.DeleteObject(font)
        if self.error:
            raise self.error
        if result == -1:
            raise ctypes.WinError(ctypes.get_last_error())

    @staticmethod
    def visual_styles(ctypes, wt, kernel):
        """Activate common controls 6 from the manifest inside shell32.dll."""
        class ACTCTXW(ctypes.Structure):
            _fields_ = [("cbSize", wt.ULONG), ("dwFlags", wt.DWORD),
                        ("lpSource", wt.LPCWSTR), ("wProcessorArchitecture", wt.USHORT),
                        ("wLangId", wt.USHORT), ("lpAssemblyDirectory", wt.LPCWSTR),
                        ("lpResourceName", ctypes.c_void_p),
                        ("lpApplicationName", wt.LPCWSTR), ("hModule", wt.HMODULE)]
        system = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32")
        # ACTCTX_FLAG_RESOURCE_NAME_VALID | ACTCTX_FLAG_ASSEMBLY_DIRECTORY_VALID
        ctx = ACTCTXW(ctypes.sizeof(ACTCTXW), 0x0C, os.path.join(system, "shell32.dll"),
                      0, 0, system, 124, None, None)
        kernel.CreateActCtxW.restype = wt.HANDLE
        kernel.ActivateActCtx.argtypes = [wt.HANDLE, ctypes.POINTER(ctypes.c_size_t)]
        handle = kernel.CreateActCtxW(ctypes.byref(ctx))
        if handle and handle != wt.HANDLE(-1).value:
            kernel.ActivateActCtx(handle, ctypes.byref(ctypes.c_size_t()))
            ctypes.WinDLL("comctl32").InitCommonControls()

    def dialog_proc(self, hwnd, msg, wparam, lparam):
        try:
            return self.handle(hwnd, msg, wparam, lparam)
        except Exception as e:
            self.error = e
            self.user.EndDialog(hwnd, 2)
            return 1

    def item(self, cid):
        return self.user.GetDlgItem(self.hwnd, cid)

    def set_text(self, cid, text):
        self.user.SetWindowTextW(self.item(cid), text)
        if cid in (self.STATUS, self.PLANNED) and text:
            # UIA_LiveRegionChangedEventId through MSAA: screen readers read
            # the new text without the person moving to it.
            try:
                self.user.NotifyWinEvent(0x8019, self.item(cid), -4, 0)
            except (AttributeError, OSError):
                pass

    def show(self, cid, visible):
        self.user.ShowWindow(self.item(cid), 5 if visible else 0)

    def focus(self, cid):
        self.user.SendMessageW(self.hwnd, 0x28, self.item(cid), 1)  # WM_NEXTDLGCTL

    def handle(self, hwnd, msg, wparam, lparam):
        user = self.user
        if msg == 0x110:  # WM_INITDIALOG
            self.hwnd = hwnd
            self.init_dialog()
            return 0
        if msg in (0x136, 0x138, 0x135):  # WM_CTLCOLORDLG, STATIC, BTN
            # The system's window colours, so high contrast themes still apply.
            self.gdi.SetTextColor(wparam, user.GetSysColor(8))
            self.gdi.SetBkColor(wparam, user.GetSysColor(5))
            return user.GetSysColorBrush(5)
        if msg == 0x113:  # WM_TIMER, from CLOSE_WINDOW_AFTER
            user.EndDialog(hwnd, 2)
            return 1
        if msg == 0x111 and (wparam >> 16) == 0:  # WM_COMMAND, BN_CLICKED
            self.command(wparam & 0xFFFF)
            return 1
        if msg == 0x111 and (wparam >> 16) == 0x501:  # EN_MAXTEXT
            self.set_text(self.STATUS, tr("A plan can be up to {n} characters.")
                          .format(n=MAX_PLAN))
            return 1
        return 0

    def init_dialog(self):
        user, gdi = self.user, self.gdi
        try:
            dpi = user.GetDpiForWindow(self.hwnd) or 96
        except AttributeError:
            dpi = 96
        for cids, points, weight in (((self.TITLE,), 20, 600),
                                     ((self.THOUGHT_LABEL, self.TIP_LABEL,
                                       self.PLAN_LABEL, self.ASK), 12, 600)):
            font = gdi.CreateFontW(-(points * dpi // 72), 0, 0, 0, weight,
                                   0, 0, 0, 1, 0, 0, 5, 0, "Segoe UI")
            self.fonts.append(font)
            for cid in cids:
                if self.item(cid):
                    user.SendMessageW(self.item(cid), 0x30, font, 1)  # WM_SETFONT
        if self.item(self.PLAN):
            user.SendMessageW(self.item(self.PLAN), 0xC5, MAX_PLAN, 0)  # EM_LIMITTEXT
        for cid in (self.STATUS, self.PLANNED):
            if self.item(cid):
                live_region(self.item(cid))
        self.show(self.DID_IT, bool(self.visit.plan()))
        if self.visit.followup:
            self.focus(self.DONE)
        else:
            self.focus_plan()
        if CLOSE_WINDOW_AFTER:
            user.SetTimer(self.hwnd, 1, CLOSE_WINDOW_AFTER, None)

    def command(self, cid):
        v = self.visit
        if cid in (self.DONE, self.NOT_YET, self.SKIP):
            ticks = [n for n in range(MAX_PARTS) if self.item(self.TICK + n)
                     and self.user.SendMessageW(self.item(self.TICK + n), 0xF0, 0, 0)]
            message = v.answer({self.DONE: "yes", self.NOT_YET: "no"}.get(cid, "skip"),
                               ticks if cid == self.DONE and ticks else None)
            if v.followup:
                self.set_text(self.STATUS, message)
                return
            for hidden in (self.ASK, self.DONE, self.NOT_YET, self.SKIP) + tuple(
                    self.TICK + n for n in range(MAX_PARTS)):
                self.show(hidden, False)
            # The question's line stays as space under the answer.
            first = self.TICK if self.item(self.TICK) else self.DONE
            self.collapse(first, self.SKIP)
            self.asking = False
            self.set_text(self.PLANNED, message)
            self.refresh_plan()
            self.focus_plan()
        elif cid == self.DID_IT:
            self.set_text(self.STATUS, v.did_it(self.typed()))
            self.finished = not v.plan()
            self.refresh_plan()
            self.focus_plan()
        elif cid == self.SAVE:
            if not self.typed().strip() and v.plan():
                # An emptied box is a plan to drop, which asks first.
                if self.confirm(tr("Clear today's plan?")):
                    self.set_text(self.STATUS, v.clear())
                    self.refresh_plan()
                self.focus_plan()
            elif self.save_typed() is None:
                self.user.EndDialog(self.hwnd, 1)
        elif cid == self.CLOSE:
            if (self.item(self.PLAN) and self.typed().strip()
                    and clean(self.typed()) != v.plan()
                    and self.confirm(tr("Save your plan before closing?"))
                    and self.save_typed() is False):
                return
            self.user.EndDialog(self.hwnd, 2)
        elif cid == self.OPTIONS:
            self.options()

    def save_typed(self):
        """Save the box. True when saved, False when refused (the window
        says why), None when there was nothing to save."""
        v = self.visit
        close, message, saved = v.save(self.typed())
        if close:
            return None
        self.set_text(self.STATUS, message)
        if saved:
            if self.asking:
                # A new plan replaces the one asked about, which same keeps.
                for hidden in (self.PLANNED, self.ASK, self.DONE, self.NOT_YET,
                               self.SKIP) + tuple(self.TICK + n for n in range(MAX_PARTS)):
                    self.show(hidden, False)
                self.collapse(self.PLANNED, self.SKIP)
                self.asking = False
            elif self.item(self.PLANNED):
                self.set_text(self.PLANNED, "")
            self.refresh_plan()
            if v.offer_due():
                v.set_reminder(self.confirm(tr(
                    "Want a reminder when you sign in? It shows your plan from "
                    "last time, and you answer with one click. You can turn it "
                    "off under Options.")))
        self.focus_plan()
        return saved

    def collapse(self, first, last):
        """Move everything after the hidden controls first..last up into
        their place, and shorten the window to match."""
        import ctypes
        from ctypes import wintypes as wt
        user = self.user
        user.MapWindowPoints.argtypes = [wt.HWND, wt.HWND, ctypes.c_void_p, wt.UINT]
        user.SetWindowPos.argtypes = [wt.HWND, wt.HWND] + [ctypes.c_int] * 4 + [wt.UINT]

        def rect(hwnd, client=True):
            r = wt.RECT()
            user.GetWindowRect(hwnd, ctypes.byref(r))
            if client:
                user.MapWindowPoints(None, self.hwnd, ctypes.byref(r), 2)
            return r

        later = self.ids[self.ids.index(last) + 1:]
        shift = rect(self.item(later[0])).top - rect(self.item(first)).top
        for cid in later:
            r = rect(self.item(cid))
            # SWP_NOSIZE | SWP_NOZORDER
            user.SetWindowPos(self.item(cid), None, r.left, r.top - shift, 0, 0, 0x5)
        r = rect(self.hwnd, client=False)
        # SWP_NOMOVE | SWP_NOZORDER
        user.SetWindowPos(self.hwnd, None, 0, 0, r.right - r.left,
                          r.bottom - r.top - shift, 0x6)

    def focus_plan(self):
        """Focus the plan box with the cursor at the end, so a stray key adds
        to the plan instead of replacing it."""
        if not self.item(self.PLAN):
            self.focus(self.CLOSE)
            return
        self.focus(self.PLAN)
        self.user.SendMessageW(self.item(self.PLAN), 0xB1, 0x7FFFFFFF, 0x7FFFFFFF)  # EM_SETSEL

    def typed(self):
        import ctypes
        if not self.item(self.PLAN):
            return ""
        buffer = ctypes.create_unicode_buffer(MAX_PLAN + 2)
        self.user.GetWindowTextW(self.item(self.PLAN), buffer, MAX_PLAN + 2)
        return buffer.value

    def refresh_plan(self):
        if not self.item(self.PLAN):
            return
        self.set_text(self.PLAN_LABEL, self.plan_label())
        self.set_text(self.PLAN, self.visit.plan())
        self.set_text(self.CLOSE, self.close_label())
        self.show(self.DID_IT, bool(self.visit.plan()))

    def popup(self, entries):
        """Show the Options menu of (flags, id, label) and return the id chosen,
        or 0."""
        import ctypes
        from ctypes import wintypes as wt
        user = self.user
        menu = user.CreatePopupMenu()
        for flags, cid, label in entries:
            user.AppendMenuW(menu, flags, cid, label)
        rect = wt.RECT()
        user.GetWindowRect(self.item(self.OPTIONS), ctypes.byref(rect))
        # TPM_RETURNCMD: the choice comes back here instead of as a message.
        # TPM_LAYOUTRTL for a right-to-left language.
        rtl = 0x8000 if language() in RIGHT_TO_LEFT else 0
        choice = user.TrackPopupMenu(menu, 0x100 | rtl, rect.left, rect.bottom, 0,
                                     self.hwnd, None)
        user.DestroyMenu(menu)
        return choice

    @staticmethod
    def rtl_box():
        """MB_RTLREADING | MB_RIGHT for a right-to-left language."""
        return 0x180000 if language() in RIGHT_TO_LEFT else 0

    def confirm(self, text):
        """A yes or no question in a standard message box."""
        # MB_YESNO | MB_ICONQUESTION; IDYES is 6.
        return self.user.MessageBoxW(self.hwnd, text, "hello-world",
                                     0x24 | self.rtl_box()) == 6

    def inform(self, text):
        """Text to read, in a standard message box with OK."""
        self.user.MessageBoxW(self.hwnd, text, "hello-world",
                              0x40 | self.rtl_box())  # MB_ICONINFORMATION

    def reminder_settings(self):
        v, checked = self.visit, 0x8
        at = v.state.get("remind_at")
        on = reminder_on()
        entries = [(checked if on and not at else 0, 1, tr("At sign-in"))]
        entries += [(checked if on and at == t else 0, 2 + n,
                     tr("At {at}").format(at=t.lstrip("0")))
                    for n, t in enumerate(REMINDER_TIMES)]
        entries.append((0x800, 0, None))
        for cid, key, label in ((20, "nudge", tr("Also on days with no plan")),
                                (21, "open_after", tr("Open hello-world after I answer")),
                                (22, "no_weekends", tr("Not on weekends"))):
            entries.append((checked if v.state.get(key) else 0, cid, label))
        choice = self.popup(entries)
        if choice == 1:
            self.set_text(self.STATUS, v.set_reminder(True))
        elif 2 <= choice < 2 + len(REMINDER_TIMES):
            self.set_text(self.STATUS, v.reminder_at(REMINDER_TIMES[choice - 2]))
        elif choice in (20, 21, 22):
            saved = v.toggle({20: "nudge", 21: "open_after", 22: "no_weekends"}[choice])
            self.set_text(self.STATUS, tr("Saved.") if saved else
                          tr("Could not save that choice on this computer."))

    def options(self):
        user, v = self.user, self.visit
        checked, grayed = 0x8, 0x1
        entries = []
        if launcher_place()[0] and not plans_off():
            on = reminder_on()
            entries.append(((checked if on else 0) | (
                grayed if policy("DisableSignInLauncher") and not on else 0),
                1, tr("Remind me when I sign in")))
            if not policy("DisableSignInLauncher"):
                entries.append((0, 9, tr("Reminder settings...")))
        entries.append((checked if v.state.get("name") else 0, 10,
                        tr("Greet me by name")))
        if not policy("HideThoughtAndTip"):
            entries.append((checked if v.state.get("tips", True) else 0, 2,
                            tr("Show the thought and tip")))
        if not policy("HideDaysInARow"):
            entries.append((checked if v.state["streak"] else 0, 7,
                            tr("Show the days-in-a-row message")))
        if not policy("ForceEnglish"):
            entries.append((0, 8, tr("Language...")))
        entries.append((0, 5, tr("Show what is saved on this computer")))
        entries.append((0, 6, tr("Delete everything saved")))
        entries.append((0, 12, tr("This week...")))
        entries.append((0, 13, tr("My numbers...")))
        entries.append((0, 14, tr("Save my plans to a file")))
        entries.append((checked if v.state.get("long_history") else 0, 15,
                        tr("Keep a longer history")))
        entries.append((checked if v.state.get("numbers") else 0, 16,
                        tr("Keep my numbers")))
        if feedback_address():
            entries.append((0, 11, tr("Send feedback...")))
        entries.append((0x800, 0, None))  # MF_SEPARATOR
        entries.append((grayed if policy("UseTextScreen") else 0, 3,
                        tr("Use the text screen")))
        entries.append((0, 4, tr("More options")))
        choice = self.popup(entries)
        if choice == 1:
            self.set_text(self.STATUS, v.set_reminder(not reminder_on()))
        elif choice == 9:
            self.reminder_settings()
        elif choice == 11:
            send_feedback()
        elif choice == 12:
            self.inform(week_text(v.state, v.d))
        elif choice == 13:
            self.inform(numbers_text(v.state))
        elif choice == 14:
            path = export_plans(v.state)
            self.set_text(self.STATUS, tr("Saved to {path}").format(path=path)
                          if path else tr("Could not save that on this computer."))
        elif choice in (15, 16):
            saved = v.toggle("long_history" if choice == 15 else "numbers")
            self.set_text(self.STATUS, tr("Saved.") if saved else
                          tr("Could not save that choice on this computer."))
        elif choice == 10:
            saved = v.toggle("name")
            self.set_text(self.STATUS, tr("Saved.") if saved else
                          tr("Could not save that choice on this computer."))
            if saved:
                self.set_text(self.TITLE, greeting(v.state))
        elif choice == 2:
            saved = v.toggle("tips")
            shown = v.state.get("tips", True)
            if saved and not shown and self.item(self.THOUGHT_LABEL):
                for cid in (self.THOUGHT_LABEL, self.THOUGHT, self.TIP_LABEL, self.TIP):
                    self.show(cid, False)
                self.collapse(self.THOUGHT_LABEL, self.TIP)
            self.set_text(self.STATUS, (
                tr("Could not save that choice on this computer.") if not saved
                else tr("Done. The thought and tip show next time you open "
                        "hello-world.") if shown else
                tr("Done. The thought and tip are off.")))
        elif choice == 7:
            saved = v.toggle("streak")
            self.set_text(self.STATUS, (
                tr("Could not save that choice on this computer.") if not saved
                else tr("Done. The days-in-a-row message is on.")
                if v.state["streak"] else
                tr("Done. The days-in-a-row message is off.")))
        elif choice == 8:
            codes = list(LANGUAGE_NAMES) + [None]
            current = v.state.get("lang")
            picked = self.popup([(0x8 if code == current else 0, 100 + n,
                                  LANGUAGE_NAMES[code] if code else tr("Follow Windows"))
                                 for n, code in enumerate(codes)])
            if picked:
                saved, _ = quietly(set_language, v.state, v.can_save,
                                   codes[picked - 100])
                self.set_text(self.STATUS, tr(
                    "Done. The new language shows next time you open hello-world.")
                    if saved else tr("Could not save that choice on this computer."))
        elif choice == 5:
            self.inform(v.saved_summary())
        elif choice == 6:
            if self.confirm(tr("Delete all saved notes, dates and plans on this "
                               "computer?")):
                self.set_text(self.STATUS, v.delete_all())
                self.refresh_plan()
            else:
                self.set_text(self.STATUS, tr("Nothing was deleted."))
        elif choice == 3:
            if v.toggle("text"):
                open_console()
                user.EndDialog(self.hwnd, 2)
            else:
                self.set_text(self.STATUS, tr("Could not save that choice on "
                                              "this computer."))
        elif choice == 4:
            open_console("--menu")
            user.EndDialog(self.hwnd, 2)


# ==== Translations ====
# Each one follows the English lists item for item. The keys of "text" are
# the English strings that tr() looks up.

# ---- Spanish ----

LANGUAGES["es"] = {
    "days": ('lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'),
    "months": ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'),
    "date": '{day}, {d} de {month} de {year}',
    "thoughts": (
        'Abre ese documento que llevas tiempo evitando y lee solo el primer párrafo.',
        'Diez minutos de trabajo ya son un comienzo, y suelen hacer más fáciles los diez siguientes.',
        'Hoy no necesitas el plan completo, solo un primer paso razonable.',
        'Escribe una primera frase imperfecta. Te da algo real que mejorar después.',
        'Despeja un rincón de tu mesa y fíjate en cuánto más tranquilo se ve el resto.',
        'Elige la tarea más pequeña de tu lista y termínala antes de mirar las demás.',
        'Un comienzo imperfecto en una mañana tranquila vale más que esperar un momento perfecto que quizá no llegue.',
        'Pon el primer paso en tu calendario para que tenga su propio espacio.',
        'Los grandes proyectos se hacen tarde a tarde. Piensa solo en esta.',
        'Di en voz alta la próxima acción y deja que el resto de la lista espere su turno.',
        'Algunos días vas más despacio de lo que te gustaría, y ese ritmo también cuenta.',
        'Háblate como le hablarías a una persona nueva en su primera semana de trabajo.',
        'Puedes seguir aprendiendo algo que llevas años haciendo.',
        'Una mañana floja no decide la tarde. Puedes empezar de nuevo después de comer.',
        'El cansancio es información, no un fallo. Ajusta el plan y sigue con calma.',
        'Trátate con la misma comprensión que ofreces tan fácilmente a los demás.',
        'A veces el progreso no se nota durante un tiempo, y de pronto tienes una página terminada.',
        'No pasa nada si necesitas leer algo dos veces para entenderlo.',
        'No necesitas sentir que todo está listo. Hacerlo con nervios también es hacerlo.',
        'Lo mejor que puedes dar hoy quizá sea menos que ayer, y no pasa nada.',
        'Cierra las pestañas que no usas. Tu atención lo notará en pocos minutos.',
        'Una tarea, una ventana, veinticinco minutos. Mira hasta dónde llegas con un rato tranquilo.',
        'Anota la idea suelta que te venga a la cabeza y vuelve a lo que estabas haciendo.',
        'Si puedes, silencia el teléfono durante una hora y dale al trabajo toda tu atención.',
        'Decide qué cosa haría de hoy un buen día y reserva tiempo para ella.',
        'Hacer las cosas de una en una suele ser más rápido de lo que parece.',
        'Una lista clara de tres cosas es mejor que una lista desordenada de veinte.',
        'Nota cuándo se distrae tu mente y tráela de vuelta sin regañarte.',
        'Pon la tarea más difícil en el momento en que tienes más energía, aunque no sea a primera hora.',
        'Auriculares puestos, una bebida a mano, puerta cerrada. Prepara el lugar y la concentración llega sola.',
        'Aléjate de la pantalla cinco minutos. Volverás con la mente un poco más clara.',
        'Hoy come lejos de tu mesa. El correo puede esperar mientras comes.',
        'Un paseo corto alrededor del edificio también es trabajo útil para tu cabeza.',
        'Un minuto lejos de la pantalla es un buen uso de una tarde ocupada.',
        'Estira los hombros y relaja la mandíbula. Quizá llevas horas en tensión.',
        'Si puedes, sal a tu hora hoy. Mañana agradecerás haber tenido la tarde libre.',
        'Descansar es parte del trabajo, porque con cansancio es fácil repetir el mismo error.',
        'Descansa la vista un momento y deja caer los hombros.',
        'Un buen descanso hace que la segunda mitad del día se sienta como un nuevo comienzo.',
        'Deja que la noche sea para ti. Nada en tu correo te necesita a las nueve.',
        'Da las gracias hoy a alguien por algo pequeño que hizo sin que se lo pidieran.',
        'La mayoría de la gente hace lo que puede, con más carga de la que tú ves.',
        'Averigua cómo toma el té o el café alguien del trabajo. Recordarlo es un pequeño regalo.',
        'Si alguien te responde de forma seca, piensa que tiene un mal día, no que te está juzgando.',
        'Sujeta la puerta, comparte las galletas y deja que la otra persona termine de hablar.',
        'Un saludo rápido y una pregunta sobre el fin de semana pueden ser lo mejor de la mañana.',
        'Cuando alguien nuevo pregunte algo obvio, recuerda que tú también lo preguntaste una vez.',
        'Reconoce en voz alta cuando la idea de alguien del equipo mejoró tu trabajo.',
        'Responde a un mensaje con un poco de calidez. No cuesta nada y se recibe bien.',
        'Habla con alguien que ha participado poco en las reuniones y pregúntale cómo está.',
        'Termina lo que casi está hecho antes de empezar algo nuevo.',
        'Más vale hecho y bastante bien que perfecto y sin terminar.',
        'Cierra hoy un asunto pendiente y nota el pequeño alivio que llega después.',
        'El último diez por ciento suele ser solo unos minutos de cuidado. Dáselos hoy.',
        'Envía el correo que espera en tus borradores. Probablemente está bien así.',
        'Márcalo como hecho, respira y alégrate de haberlo terminado.',
        'Una cosa pequeña terminada vale más que una grande a medias.',
        'Antes de desconectarte, anota el primer paso de mañana para no tener que recordarlo.',
        'Léelo una vez más, corrige lo que encuentres y envíalo.',
        'Terminar el día con un resultado claro hace que la noche se sienta más ligera.',
        'Preguntar pronto suele ahorrar una hora de esfuerzo en silencio después.',
        'A la mayoría de la gente le gusta compartir lo que sabe. Pregunta sin pedir perdón.',
        '"No sé cómo seguir" es una frase clara y útil con la que tu equipo puede ayudarte.',
        'Pide lo que necesitas con palabras sencillas y da a los demás la oportunidad de decir que sí.',
        'Dos personas mirando un problema suelen resolverlo antes que una sola persona en silencio.',
        'Necesitar ayuda no te convierte en una carga. Eres parte del equipo.',
        'Lleva una pregunta concreta y la persona a quien preguntes podrá darte una respuesta concreta.',
        'Si las instrucciones no están claras, pedir aclaraciones es parte de hacer bien el trabajo.',
        'Ofrece ayuda cuando puedas y acéptala cuando la necesites. Ambas cosas se aprenden con práctica.',
        'Seguramente alguien cerca de ti ya ha resuelto esto antes. Ve a buscar a esa persona.',
        'Anota las cosas que aprendiste a resolver esta semana. Suman más de lo que crees.',
        'Ser principiante en algo nuevo es señal de que tu trabajo sigue creciendo.',
        'Observa cómo alguien a quien admiras maneja una llamada difícil y quédate con una idea.',
        'Lee una página útil en tu descanso y da el día por bien aprovechado.',
        'Explicar una tarea a otra persona es una forma sorprendentemente buena de aprenderla.',
        'Está bien decir "todavía no lo sé" y luego ir a averiguarlo.',
        'Todo sistema nuevo parece confuso hasta que lo has usado unas cuantas veces.',
        'Pregunta a alguien con más experiencia cómo lo aprendió. La respuesta suele tranquilizar.',
        'Las habilidades vienen de la repetición. Repite lo pequeño y deja que se vuelva fácil.',
        'Un poco de curiosidad puede hacer más interesante una tarea normal.',
        'Un error detectado a tiempo es solo una corrección, y la mayoría se detectan a tiempo.',
        'Corrígelo, avisa a quien necesite saberlo y deja que la molestia pase.',
        'Casi cualquier error en el trabajo parece más pequeño una semana después.',
        'Un fallo no borra los años de trabajo cuidadoso que llevas detrás.',
        'Cuando algo sale mal, mira primero el proceso y después a la persona.',
        'Todas las personas a tu alrededor han enviado alguna vez un correo a quien no era.',
        'Quédate con la lección que deja un error y deja atrás el resto.',
        'Reconocer un error con sencillez suele dar más confianza que no haberlo cometido nunca.',
        'Hasta la gente cuidadosa tiene días torpes, y se acaban antes de la noche.',
        'El próximo mes no recordarás la mayoría de los pequeños tropiezos de hoy.',
        'Un día tranquilo y sin urgencias es un buen día, aunque nadie lo diga.',
        'Fíjate en los pequeños placeres: una taza caliente, la bandeja de entrada vacía, un minuto de calma.',
        'No todos los días necesitan un gran logro. Trabajar con calma y a gusto está bien.',
        'Disfruta de la reunión que termina cinco minutos antes y usa ese tiempo como quieras.',
        'Un día normal bien hecho es motivo de un orgullo tranquilo.',
        'El buen trabajo a menudo no se nota desde fuera, y no pasa nada.',
        'Deja que una tarde agradable sea agradable, sin esperar que sea productiva.',
        'Las pequeñas rutinas del día, como el primer café y las caras conocidas, merecen tu atención.',
        'Hoy estuviste presente e hiciste tu parte, y eso es suficiente.',
        'Esta noche, tómate un momento para recordar algo que salió bien hoy.',
        'Un minuto tranquilo entre dos tareas no es tiempo perdido; ayuda a empezar bien la siguiente.',
    ),
    "tips": (
        'Bebe un vaso de agua despacio, lejos de la pantalla.',
        'Gira los hombros hacia atrás cinco veces, muy despacio.',
        'Descansa la vista veinte segundos: mira a lo lejos o cierra los ojos.',
        'Estira los brazos hacia arriba, en la silla o de pie, y respira hondo.',
        'Ve hasta la sala o la ventana más lejana que puedas y vuelve.',
        'Revisa tu postura y deja caer los hombros, lejos de las orejas.',
        'Gira el cuello con suavidad de un lado a otro, solo hasta donde sea cómodo.',
        'Abre y cierra las manos diez veces para soltar los dedos.',
        'Fija el documento que más abres para tenerlo a un clic.',
        'Sal a dar un paseo corto, caminando o en silla de ruedas, como te vaya mejor.',
        'Sírvete una bebida caliente o fría y disfrútala lejos de la pantalla.',
        'Fíjate en algo tranquilo: un paisaje, un sonido o una textura.',
        'Escribe el siguiente paso de una tarea que dejaste a medias.',
        'Apoya los pies en el suelo y estira la espalda, en la silla o de pie, durante diez respiraciones.',
        'Silencia un chat de grupo que solo lees por encima.',
        'Relaja la mandíbula y la frente durante un momento.',
        'Muévete durante dos minutos de la forma que te siente bien hoy.',
        'Reserva quince minutos en tu calendario para la tarea que siempre aplazas.',
        'Ajusta un poco la silla, la pantalla o el teclado para tu comodidad.',
        'Si puedes, toma el camino largo hacia tu próxima reunión o llamada.',
        'Guarda una plantilla para un correo que escribes una y otra vez.',
        'Aprende un atajo de teclado del programa que más usas.',
        'Bebe un vaso entero de agua antes de tu próximo café o té.',
        'Sube los hombros hasta las orejas y luego déjalos caer despacio.',
        'Sal un minuto o abre una ventana para tomar aire fresco.',
        'Respira despacio cinco veces y alarga un poco cada exhalación.',
        'Haz una pausa tranquila de un minuto antes de abrir tu próximo mensaje.',
        'Anota una cosa buena que te haya pasado hoy.',
        'Cierra los ojos durante tres respiraciones y nota cómo te sientes.',
        'Nombra tres cosas que percibes ahora mismo, con cualquier sentido.',
        'Escribe una cosa que esperas con ganas esta semana.',
        'Pon un temporizador de dos minutos y descansa sin ninguna pantalla.',
        'Disfruta de algo pequeño cerca de ti, como una planta o tu taza favorita.',
        'Piensa en algo que hiciste bien esta semana y reconócelo.',
        'Escucha una de tus canciones favoritas de principio a fin, sin nada más abierto.',
        'Inhala contando hasta cuatro y exhala contando hasta seis, tres veces.',
        'Respira una vez antes de reaccionar a la próxima pequeña molestia.',
        'Anota algo que te hizo reír hace poco.',
        'Durante un minuto, fíjate en algo agradable: un sonido, un olor o algo que tocas.',
        'Recuerda un lugar que te encanta e imagínalo durante treinta segundos.',
        'Di "por ahora está bien así" sobre una tarea pequeña y sigue adelante.',
        'Escribe una frase sobre algo que agradeces.',
        'Saborea el próximo sorbo de tu bebida y fíjate en el sabor.',
        'Haz una pausa corta entre dos tareas antes de empezar la siguiente.',
        'Busca hoy una cosa que salga mejor de lo que esperabas.',
        'Resume en una palabra cómo quieres que sea la tarde.',
        'Deja descansar la mente sesenta segundos y luego vuelve a tu siguiente tarea.',
        'Siente los pies en el suelo y nota la estabilidad un momento.',
        'Recuerda algo amable que alguien hizo por ti y disfruta del recuerdo.',
        'Anota una idea que quieras retomar más tarde y déjala reposar.',
        'Ordena un rincón pequeño de tu escritorio, solo uno.',
        'Responde a un mensaje que lleva un tiempo esperando.',
        'Apunta la tarea principal de mañana en una nota adhesiva o en tus notas.',
        'Cierra las pestañas del navegador que ya no necesitas.',
        'Da las gracias a alguien de tu equipo por algo que hizo hace poco.',
        'Archiva cinco correos antiguos que ya no necesitas.',
        'Cambia el nombre de un archivo desordenado para encontrarlo fácilmente después.',
        'Quita uno o dos archivos sueltos del escritorio de Windows.',
        'Borra un recordatorio antiguo que ya no sirve.',
        'Pon un título claro a un documento que abres a menudo.',
        'Tacha una tarea pequeña de tu lista de pendientes.',
        'Date de baja de un boletín que nunca lees.',
        'Limpia el teclado o la pantalla con un paño suave.',
        'Deja un bolígrafo, un cuaderno y agua donde los alcances fácilmente.',
        'Escribe una nota breve para tu yo de mañana sobre dónde lo dejaste hoy.',
        'Elige la tarea más importante de esta tarde y hazla primero.',
        'Vacía la papelera o el contenedor de reciclaje de tu mesa.',
        'Actualiza una nota de progreso para que otros vean cómo van las cosas.',
        'Ordena tu carpeta de descargas moviendo unos cuantos archivos.',
        'Pon un recordatorio para algo que sueles olvidar.',
        'Desactiva una notificación que en realidad no necesitas.',
        'Guarda en favoritos una página que buscas una y otra vez.',
        'Escribe un resumen de dos líneas de una reunión mientras la recuerdas bien.',
        'Pregunta si una reunión periódica podría ser un poco más corta.',
        'Define tu único objetivo para la próxima hora y escríbelo.',
        'Pregunta a alguien del equipo cómo va su día y escucha con atención.',
        'Comparte un enlace útil con alguien a quien le pueda gustar.',
        'Saluda a alguien con quien todavía no has hablado.',
        'Envía una nota breve de agradecimiento a alguien que te ayudó hace poco.',
        'Saluda con calidez a los demás al empezar tu próxima llamada.',
        'Pregunta a alguien de tu equipo qué espera con ganas esta semana.',
        'Felicita a alguien por un pequeño logro que hayas notado.',
        'Invita a alguien del trabajo a una charla corta con un té, un café o por llamada.',
        'Elogia algo concreto que alguien del trabajo hizo bien.',
        'Aprende el nombre de alguien a quien ves a menudo pero aún no conoces.',
        'Comparte un consejo útil con alguien del equipo que pueda necesitarlo.',
        'Pide a alguien que te recomiende una canción, una serie o un libro.',
        'Habla con alguien del trabajo que ha hablado poco últimamente y pregúntale cómo está.',
        'Si alguien parece tener mucho trabajo, ofrécete a ayudar con algo pequeño.',
        'Saluda con calidez a la próxima persona que veas.',
        'Si oíste algo amable sobre alguien del trabajo, cuéntaselo.',
        'Pregunta a alguien del trabajo qué le facilitó la semana.',
        'Envía un mensaje amable a alguien con quien trabajaste antes.',
        'Da las gracias a quien mantiene en orden los espacios compartidos.',
        'Presenta a dos personas del trabajo que podrían llevarse bien.',
        'Pregunta a alguien del equipo cómo puedes facilitarle el traspaso de una tarea.',
        'Comparte una broma pequeña e inofensiva con alguien cerca de ti.',
        'Pon un poco más de calidez en tu próximo "por favor" y "gracias".',
        'Pregunta a alguien del trabajo qué le gusta hacer en su tiempo libre.',
        'Escucha con toda tu atención a la próxima persona que te hable, sin hacer otras cosas.',
    ),
    "done": (
        'Bien. Esa ya está terminada.',
        'Muy bien. Da gusto terminar algo.',
        'Bien hecho. Descansa un poco antes de la siguiente.',
        'Bien. Las tareas pequeñas terminadas suman.',
        'Ya está hecho. Alégrate un momento.',
        'Bien. Una tarea menos en tu lista.',
    ),
    "text": {
        HELP: """hello-world muestra un saludo, una idea y algo sencillo que probar.

En la última pregunta, escribe plan para el plan de hoy, hecho cuando
lo termines, o menú (o m) para ver las opciones. Enter cierra; q, salir
o x cierran desde cualquier pregunta. En la pregunta del plan,
repetir recupera un plan anterior sin terminar. Después de hecho,
muestra tus 3 últimos planes terminados. La opción 1 del menú los
muestra todos, la 7 olvida uno y la 8 oculta la idea y la sugerencia.
En el menú, Enter vuelve atrás.
También puedes ejecutar hello.cmd con una de estas opciones:
  --plain         Muestra solo el saludo, en inglés
  --stats         Muestra lo que hay guardado en este equipo
  --reset         Borra todo lo guardado (pregunta antes)
  --remind on     Se abre al iniciar sesión cada día (off: lo quita)
  --streak off    Oculta el mensaje de días seguidos (on: lo muestra)
  --version       Muestra la versión
  --check-content FILE
                  Comprueba un archivo de contenido de la organización
  --help          Muestra este texto

Códigos de salida: 0 si funcionó, 1 si un comando falló o no se pudo
escribir en la pantalla, 2 para una opción desconocida.

Las notas guardadas se quedan en este equipo, en tu carpeta de
usuario. No se envía nada a ningún sitio. El personal de TI que puede
leer los archivos de este equipo podría leerlas.""",
        MENU_HELP: """Palabras que puedes escribir en la última pregunta:
  hecho  marca como terminado el plan de hoy y pide el siguiente
  plan   escribe o cambia el plan de hoy
  menú   abre estas opciones
  q      cierra la ventana, igual que Enter
En la pregunta del plan, repetir recupera tu plan anterior sin terminar.
Cuando pregunta "¿Lo hiciste?", n significa todavía no, y puedes
mantener el plan para hoy. q cierra desde cualquier pregunta.
En este menú, 1 muestra lo guardado, 7 olvida un plan terminado
y 8 oculta la idea y la sugerencia.
Escribe m para ver de nuevo las opciones. No se envía nada a ningún
sitio.""",
        SAVED_PLAN: 'Guardado. Escribe hecho al terminarlo, o te lo preguntará en la próxima visita.',
        GREETING: '¡Hola, mundo!',
        'hello.cmd is in this folder:':
            'hello.cmd está en esta carpeta:',
        'Shortened to {n} characters.':
            'Se acortó a {n} caracteres.',
        'Your saved file was damaged, so hello-world set it aside as a backup copy and started fresh. Your earlier days and plan could not be read. Menu option 4 deletes the backup.':
            'Tu archivo guardado estaba dañado, así que hello-world lo apartó como copia de seguridad y empezó de nuevo. No se pudieron leer tus días ni tu plan anteriores. La opción 4 del menú borra la copia.',
        'Backup copy: ':
            'Copia de seguridad: ',
        'In the folder: ':
            'En la carpeta: ',
        'Sorry, "{shown}" is not one of the choices.':
            'Perdona, "{shown}" no es una de las opciones.',
        'A plan needs a word or two, so nothing was saved.':
            'Un plan necesita una o dos palabras, así que no se guardó nada.',
        'The sign-in reminder works on Windows only.':
            'El aviso al iniciar sesión solo funciona en Windows.',
        'Your organization has turned off opening at sign-in.':
            'Tu organización ha desactivado la apertura al iniciar sesión.',
        'The reminder cannot be set up from this folder.':
            'El aviso no se puede configurar desde esta carpeta.',
        'Could not set up the reminder.':
            'No se pudo configurar el aviso.',
        'Done. hello-world will open once a day when you sign in.':
            'Listo. hello-world se abrirá una vez al día al iniciar sesión.',
        'To stop it, choose option 2 in the menu.':
            'Para desactivarlo, elige la opción 2 del menú.',
        'Could not turn off the sign-in reminder.':
            'No se pudo desactivar el aviso al iniciar sesión.',
        'Done. The sign-in reminder is off.':
            'Listo. El aviso al iniciar sesión está desactivado.',
        'Saved on this computer in:':
            'Guardado en este equipo, en:',
        'Saved in your own user folder on this computer.':
            'Guardado en tu propia carpeta de usuario de este equipo.',
        'Days you opened it in the last {days} days: {n} (last 7 days: {recent})':
            'Días que lo abriste en los últimos {days} días: {n} (últimos 7 días: {recent})',
        'Times you marked a plan done: {n}':
            'Veces que marcaste un plan como hecho: {n}',
        'Your current plan: ':
            'Tu plan actual: ',
        'Earlier plan (for same): ':
            'Plan anterior (para repetir): ',
        'Days-in-a-row message: shown.':
            'Mensaje de días seguidos: visible.',
        'Days-in-a-row message: hidden.':
            'Mensaje de días seguidos: oculto.',
        'Opens by itself at sign-in: turned off by your organization.':
            'Se abre solo al iniciar sesión: desactivado por tu organización.',
        'Opens by itself at sign-in: on.':
            'Se abre solo al iniciar sesión: sí.',
        'Opens by itself at sign-in: off.':
            'Se abre solo al iniciar sesión: no.',
        "It never leaves this computer. Others who can read this computer's files, such as IT staff, could read it.":
            'Nunca sale de este equipo. Quien pueda leer los archivos de este equipo, como el personal de TI, podría leerlo.',
        'After tidying, the file holds only this:':
            'Después de ordenarlo, el archivo solo contiene esto:',
        'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
            '¿Borrar todas las notas, fechas y planes guardados en este equipo? (s o n, Enter para cancelar) > ',
        'Nothing was deleted.':
            'No se borró nada.',
        'Could not delete everything.':
            'No se pudo borrar todo.',
        'Delete these yourself:':
            'Borra tú estos archivos:',
        'Could not list the folder, so backup copies may remain:':
            'No se pudo leer la carpeta, así que pueden quedar copias:',
        'Done. Everything saved was deleted.':
            'Listo. Se borró todo lo guardado.',
        'Another open hello-world window cannot put it back.':
            'Otra ventana abierta de hello-world no puede recuperarlo.',
        'Close any other open hello-world window, or it may save its notes again.':
            'Cierra cualquier otra ventana abierta de hello-world, o podría volver a guardar sus notas.',
        'Everything saved was deleted in another window, so this was not saved.':
            'Todo lo guardado se borró en otra ventana, así que esto no se guardó.',
        'The other open window had also finished a plan.':
            'La otra ventana abierta también había terminado un plan.',
        'The other open window changed the plan, so its plan is kept.':
            'La otra ventana cambió el plan, así que se mantiene el suyo.',
        'Type plan at the last prompt to set one.':
            'Escribe plan en la última pregunta para crear uno.',
        'That looks like a command, not a plan, so nothing was saved.':
            'Eso parece un comando, no un plan, así que no se guardó nada.',
        'Type your plan, or press Enter to go back.':
            'Escribe tu plan o pulsa Enter para volver.',
        'Finished lately:':
            'Terminados hace poco:',
        'Your plan today: ':
            'Tu plan de hoy: ',
        'Your plan from {date}: ':
            'Tu plan del {date}: ',
        'Earlier plan: ':
            'Plan anterior: ',
        'Type the next plan, or Enter to close > ':
            'Escribe el siguiente plan, o Enter para cerrar > ',
        'Type the next plan, same to reuse the earlier plan, or Enter to close > ':
            'Escribe el siguiente plan, repetir para usar el plan anterior, o Enter para cerrar > ',
        "Type today's plan, or Enter to keep it > ":
            'Escribe el plan de hoy, o Enter para mantenerlo > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
            'Escribe el plan de hoy, repetir para usar el plan anterior, o Enter para mantenerlo > ',
        "Type today's plan, or Enter to go back > ":
            'Escribe el plan de hoy, o Enter para volver > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
            'Escribe el plan de hoy, repetir para usar el plan anterior, o Enter para volver > ',
        'Closing.':
            'Cerrando.',
        'There is no earlier plan to reuse yet. Nothing changed.':
            'Todavía no hay un plan anterior para repetir. No cambió nada.',
        'Nothing changed.':
            'No cambió nada.',
        'Could not save that on this computer. Your plan is unchanged.':
            'No se pudo guardar en este equipo. Tu plan no ha cambiado.',
        'No finished plans are saved.':
            'No hay planes terminados guardados.',
        'Type the number to forget (1 to {n}), or Enter to keep them all > ':
            'Escribe el número que quieres olvidar (del 1 al {n}), o Enter para mantenerlos todos > ',
        'There is no number "{typed}" on the list. Type a number from 1 to {n}, or press Enter to keep them all.':
            'No hay ningún número "{typed}" en la lista. Escribe un número del 1 al {n}, o pulsa Enter para mantenerlos todos.',
        'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
            '¿Olvidarlo también como plan anterior para repetir? (s o n, Enter para mantenerlo) > ',
        'Type y or n, or press Enter to keep it for same.':
            'Escribe s o n, o pulsa Enter para mantenerlo para repetir.',
        'That plan was already forgotten. Nothing changed.':
            'Ese plan ya estaba olvidado. No cambió nada.',
        'Forgotten: ':
            'Olvidado: ',
        'Same still has it.':
            'Aún puedes recuperarlo con repetir.',
        'Could not save that on this computer. Nothing changed.':
            'No se pudo guardar en este equipo. No cambió nada.',
        'Options':
            'Opciones',
        'Show what is saved on this computer':
            'Mostrar lo guardado en este equipo',
        'Open once a day at sign-in (turned off by your organization)':
            'Abrir al iniciar sesión (desactivado por tu organización)',
        'Turn off: open once a day at sign-in (now on)':
            'Desactivar: abrir al iniciar sesión (ahora activado)',
        'Turn on: open once a day at sign-in (now off)':
            'Activar: abrir al iniciar sesión (ahora desactivado)',
        'Days-in-a-row message (hidden by your organization)':
            'Mensaje de días seguidos (oculto por tu organización)',
        'Hide the days-in-a-row message (now shown)':
            'Ocultar el mensaje de días seguidos (ahora visible)',
        'Show the days-in-a-row message (now hidden)':
            'Mostrar el mensaje de días seguidos (ahora oculto)',
        'Delete everything saved':
            'Borrar todo lo guardado',
        'Help':
            'Ayuda',
        "Set today's plan (turned off by your organization)":
            'Escribir el plan de hoy (desactivado por tu organización)',
        'Forget a finished plan (turned off by your organization)':
            'Olvidar un plan terminado (desactivado por tu organización)',
        "Set or change today's plan":
            'Escribir o cambiar el plan de hoy',
        'Forget one finished plan':
            'Olvidar un plan terminado',
        'Thought and tip (hidden by your organization)':
            'Idea y sugerencia (ocultas por tu organización)',
        'Hide the thought and tip (now shown)':
            'Ocultar la idea y la sugerencia (ahora visibles)',
        'Show the thought and tip (now hidden)':
            'Mostrar la idea y la sugerencia (ahora ocultas)',
        '{date}: ':
            '{date}: ',
        'Enter':
            'Enter',
        'Back to the last prompt':
            'Volver a la última pregunta',
        'Choose 1 to 11, or Enter to go back > ':
            'Elige del 1 al 11, o Enter para volver > ',
        'Choose 1 to 11, m to list the options, or Enter to go back > ':
            'Elige del 1 al 11, m para ver las opciones, o Enter para volver > ',
        'The saved file could not be read just now, so this may be out of date.':
            'El archivo guardado no se pudo leer ahora, así que esto puede no estar al día.',
        'Type full to see the whole file, or Enter to go on > ':
            'Escribe todo para ver el archivo entero, o Enter para seguir > ',
        'Could not save that choice on this computer.':
            'No se pudo guardar esa elección en este equipo.',
        'Your organization has hidden the days-in-a-row message.':
            'Tu organización ha ocultado el mensaje de días seguidos.',
        'Done. The days-in-a-row message is on.':
            'Listo. El mensaje de días seguidos está activado.',
        'Done. The days-in-a-row message is off.':
            'Listo. El mensaje de días seguidos está desactivado.',
        'Plans are turned off by your organization.':
            'Tu organización ha desactivado los planes.',
        'Your organization has hidden the thought and tip.':
            'Tu organización ha ocultado la idea y la sugerencia.',
        'Done. The thought and tip are on.':
            'Listo. La idea y la sugerencia están activadas.',
        'Done. The thought and tip are off.':
            'Listo. La idea y la sugerencia están desactivadas.',
        'Type 1 to 11, or press Enter to go back.':
            'Escribe del 1 al 11, o pulsa Enter para volver.',
        'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
            '¿Quieres que se abra una vez al día al iniciar sesión? (s o n, Enter para más tarde) > ',
        'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
            '¿Quieres que se abra una vez al día al iniciar sesión para preguntarte por tu plan? (s o n, Enter para más tarde) > ',
        'Type y or n, or press Enter for not now.':
            'Escribe s o n, o pulsa Enter para más tarde.',
        'That was not understood. It will ask again on a later visit.':
            'No se entendió. Volverá a preguntar en otra visita.',
        'It will ask again on a later visit. Menu option 2 also turns it on.':
            'Volverá a preguntar en otra visita. La opción 2 del menú también lo activa.',
        'No problem. Menu option 2 turns it on later.':
            'Sin problema. La opción 2 del menú lo activa más adelante.',
        "Okay. It won't ask again. Menu option 2 turns it on.":
            'De acuerdo. No volverá a preguntar. La opción 2 del menú lo activa.',
        'Okay. It will ask again on a later visit. Type n to stop it.':
            'De acuerdo. Volverá a preguntar en otra visita. Escribe n para que no pregunte más.',
        'When did you finish it?':
            '¿Cuándo lo terminaste?',
        'Today':
            'Hoy',
        'Type a number from 1 to {n}, or Enter for 1 > ':
            'Escribe un número del 1 al {n}, o Enter para 1 > ',
        'Type a number from 1 to {n}, or press Enter.':
            'Escribe un número del 1 al {n}, o pulsa Enter.',
        'That looks like more than one thing. Finishing the first part still counts.':
            'Eso parece más de una cosa. Terminar la primera parte ya cuenta.',
        'There is no plan to mark as done. Type plan to set one.':
            'No hay ningún plan para marcar como hecho. Escribe plan para crear uno.',
        'Could not save that on this computer. The plan is still open.':
            'No se pudo guardar en este equipo. El plan sigue pendiente.',
        'Your plan from over two weeks ago was put away. Type same at the plan prompt to bring it back.':
            'Tu plan de hace más de dos semanas se guardó aparte. Escribe repetir en la pregunta del plan para recuperarlo.',
        "Press Enter at each question to skip it, and once more to close. That's it.":
            'Pulsa Enter en cada pregunta para saltarla, y una vez más para cerrar. Eso es todo.',
        'Welcome.':
            'Te damos la bienvenida.',
        'Each day you get one thought and one small thing to try, the same for everyone.':
            'Cada día verás una idea y algo sencillo que probar, igual para todo el mundo.',
        'If you type a plan, it asks next time how it went. Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks.':
            'Si escribes un plan, la próxima vez te pregunta cómo fue. Tus notas se quedan en este equipo y nunca se envían a ningún sitio. Como cualquier archivo del trabajo, no son secretas, así que úsalas solo para tareas del día a día.',
        'Type menu at the end for the options.':
            'Escribe menú al final para ver las opciones.',
        'Welcome back. Glad you are here.':
            'Qué bien verte de nuevo.',
        'You have opened this {row} days in a row. Nice to see you.':
            'Lo has abierto {row} días seguidos. Qué bien verte.',
        'Last time you planned: ':
            'Tu último plan: ',
        'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
            '¿Lo hiciste? (s para sí, n para todavía no, Enter para saltar) > ',
        'Type y or n, or press Enter to skip.':
            'Escribe s o n, o pulsa Enter para saltar.',
        'Could not save that on this computer. Your answer was not counted.':
            'No se pudo guardar en este equipo. Tu respuesta no se contó.',
        'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
            'No pasa nada. ¿Lo mantienes para hoy? (s o n, Enter para mantenerlo) > ',
        'Type y to keep it, n to clear it, or press Enter to keep it.':
            'Escribe s para mantenerlo, n para quitarlo, o pulsa Enter para mantenerlo.',
        'Cleared. Type same at a plan prompt if you want it back.':
            'Quitado. Escribe repetir en la pregunta del plan para recuperarlo.',
        'Kept for today.':
            'Se mantiene para hoy.',
        'That was not understood. Your plan is left as it was.':
            'No se entendió. Tu plan se queda como estaba.',
        'Your plan is still open.':
            'Tu plan sigue pendiente.',
        'Thought for today:':
            'Idea para hoy:',
        'Try this today:':
            'Prueba esto hoy:',
        'Your plan for today: ':
            'Tu plan para hoy: ',
        'Still open since {date}:':
            'Pendiente desde el {date}:',
        '(Enter to skip)':
            '(Enter para saltar)',
        '(A plan typed here replaces the old one. Enter to skip)':
            '(Un plan escrito aquí sustituye al anterior. Enter para saltar)',
        '(Type same to reuse it, or Enter to skip)':
            '(Escribe repetir para usarlo, o Enter para saltar)',
        'What is one thing you want to get done today?':
            '¿Qué cosa quieres terminar hoy?',
        'There is no earlier plan to reuse yet. Nothing was saved.':
            'Todavía no hay un plan anterior para repetir. No se guardó nada.',
        'Your notes could not be saved on this computer. This screen still works.':
            'Tus notas no se pudieron guardar en este equipo. Esta pantalla sigue funcionando.',
        'Type menu, or Enter to close > ':
            'Escribe menú, o Enter para cerrar > ',
        'Type done, plan or menu, or Enter to close > ':
            'Escribe hecho, plan o menú, o Enter para cerrar > ',
        'Type plan or menu, or Enter to close > ':
            'Escribe plan o menú, o Enter para cerrar > ',
        'Type done, plan or menu, or press Enter to close.':
            'Escribe hecho, plan o menú, o pulsa Enter para cerrar.',
        'Type plan or menu, or press Enter to close.':
            'Escribe plan o menú, o pulsa Enter para cerrar.',
        "The saved file can't be read right now, or it is damaged.":
            'El archivo guardado no se puede leer ahora, o está dañado.',
        'Nothing was changed. Saved in: ':
            'No se cambió nada. Guardado en: ',
        'Deleting saved notes needs a person at the keyboard.':
            'Para borrar las notas guardadas hace falta una persona al teclado.',
        '{option} needs on or off. Here are the options.':
            '{option} necesita on u off. Estas son las opciones.',
        'Unknown option: {option}. Here are the options.':
            'Opción desconocida: {option}. Estas son las opciones.',
        '&Done':
            '&Hecho',
        '&Not yet':
            '&Todavía no',
        'S&kip':
            '&Saltar',
        '&Save':
            '&Guardar',
        '&I did it':
            '&Ya lo hice',
        '&Options':
            '&Opciones',
        'Close':
            'Cerrar',
        'Not today':
            'Hoy no',
        'Did you do it?':
            '¿Lo hiciste?',
        'Done. A reminder comes when you sign in, if there is a plan to ask about.':
            'Listo. Al iniciar sesión verás un aviso si hay un plan sobre el que preguntar.',
        'Done. The Start menu opens a window with buttons.':
            'Listo. El menú Inicio abre una ventana con botones.',
        'Done. The Start menu opens this text screen.':
            'Listo. El menú Inicio abre esta pantalla de texto.',
        'More options':
            'Más opciones',
        'Remind me when I sign in':
            'Avisarme al iniciar sesión',
        'Show the thought and tip':
            'Mostrar la idea y la sugerencia',
        'Type your plan in the box.':
            'Escribe tu plan en el cuadro.',
        'Use a window with buttons (now this text screen)':
            'Usar una ventana con botones (ahora esta pantalla de texto)',
        'Use the text screen':
            'Usar la pantalla de texto',
        'Use this text screen (now a window with buttons)':
            'Usar esta pantalla de texto (ahora una ventana con botones)',
        'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
            '¿Quieres un aviso al iniciar sesión? Te muestra tu plan de la última vez y respondes con un clic. Puedes desactivarlo en Opciones.',
        'Window or text screen (set by your organization)':
            'Ventana o pantalla de texto (lo decide tu organización)',
        'Your organization has set hello-world to open as a text screen.':
            'Tu organización ha configurado hello-world como pantalla de texto.',
        'Saved.':
            'Guardado.',
        'Save your plan before closing?':
            '¿Guardar tu plan antes de cerrar?',
        'Delete all saved notes, dates and plans on this computer?':
            '¿Borrar todas las notas, fechas y planes guardados en este equipo?',
        'Turn off: reminder when you sign in (now on)':
            'Desactivar: aviso al iniciar sesión (ahora activado)',
        'Turn on: reminder when you sign in (now off)':
            'Activar: aviso al iniciar sesión (ahora desactivado)',
        'Reminder when you sign in (turned off by your organization)':
            'Aviso al iniciar sesión (desactivado por tu organización)',
        'Reminder when you sign in: on.':
            'Aviso al iniciar sesión: activado.',
        'Reminder when you sign in: off.':
            'Aviso al iniciar sesión: desactivado.',
        'Reminder when you sign in: turned off by your organization.':
            'Aviso al iniciar sesión: desactivado por tu organización.',
        'Show the days-in-a-row message':
            'Mostrar el mensaje de días seguidos',
        'Done. The thought and tip show next time you open hello-world.':
            'Listo. La idea y la sugerencia se verán la próxima vez que abras hello-world.',
        "Clear today's plan?":
            '¿Borrar el plan de hoy?',
        'Next plan, if you want one:':
            'Siguiente plan, si quieres:',
        'A few things? Put ; between them.':
            '¿Varias cosas? Sepáralas con ;',
        'A plan can be up to {n} characters.':
            'Un plan puede tener hasta {n} caracteres.',
        'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
            '¿Las hiciste? (s para todas, n para todavía no, los números de las que hiciste, Enter para saltar) > ',
        'Last time you planned:':
            'Tu último plan:',
        'The rest is kept for today.':
            'Lo demás se mantiene para hoy.',
        'Tick the ones you did, then click Done. With none ticked, Done means all of them.':
            'Marca las que hiciste y haz clic en Hecho. Sin ninguna marcada, Hecho vale para todas.',
        'Type y for all, n for not yet, or the numbers you did, such as 1 3. Enter skips.':
            'Escribe s para todas, n para todavía no, o los números de las que hiciste, como 1 3. Enter salta.',
        'Your settings were kept.':
            'Tus ajustes se han mantenido.',
        'Language (set by your organization)':
            'Idioma (lo decide tu organización)',
        'Language (now {name})':
            'Idioma (ahora {name})',
        'following Windows':
            'según Windows',
        'Your organization shows hello-world in English.':
            'Tu organización muestra hello-world en inglés.',
        'Follow Windows':
            'Según Windows',
        'Type a number from 1 to {n}, or Enter to keep it > ':
            'Escribe un número del 1 al {n}, o Enter para mantenerlo > ',
        'Done. The new language shows next time you open hello-world.':
            'Listo. El nuevo idioma se verá la próxima vez que abras hello-world.',
        'Language...':
            'Idioma...',
        'Hello, {name}!':
            '¡Hola, {name}!',
        'One thing to get done today? Open hello-world to plan it.':
            '¿Una cosa que terminar hoy? Abre hello-world para planearla.',
        '&Open':
            '&Abrir',
        'Reminder settings...':
            'Ajustes del aviso...',
        'Greet me by name':
            'Saludarme por mi nombre',
        'At sign-in':
            'Al iniciar sesión',
        'At {at}':
            'A las {at}',
        'Also on days with no plan':
            'También los días sin plan',
        'Open hello-world after I answer':
            'Abrir hello-world después de responder',
        'Not on weekends':
            'No los fines de semana',
        'Done. A reminder comes at {at} each day, if there is a plan to ask about.':
            'Listo. Cada día a las {at} llega un aviso si hay un plan sobre el que preguntar.',
        'Send feedback...':
            'Enviar comentarios...',
        '"holidays" must be a list of at most {n} dates.':
            '"holidays" debe ser una lista de {n} fechas como máximo.',
        '"title" must be 1 to 40 characters of plain text, with no link or address.':
            '"title" debe tener de 1 a 40 caracteres de texto simple, sin enlaces ni direcciones.',
        '"{list}" must be a list of {low} to {high} lines.':
            '"{list}" debe ser una lista de {low} a {high} líneas.',
        "Can't read {path}: {error}":
            'No se puede leer {path}: {error}',
        'Could not save that on this computer.':
            'No se pudo guardar en este equipo.',
        'Days you opened hello-world: {n}':
            'Días que abriste hello-world: {n}',
        'Keep a longer history':
            'Guardar un historial más largo',
        'Keep my numbers':
            'Guardar mis cifras',
        'Longest run of days: {n}':
            'Racha más larga de días: {n}',
        "Mark today's plan done":
            'Marcar como hecho el plan de hoy',
        "Mark today's plan done (plans are turned off)":
            'Marcar como hecho el plan de hoy (planes desactivados)',
        'My numbers are off. Turn them on under Options, or with --set numbers on.':
            'Tus cifras están desactivadas. Actívalas en Opciones o con --set numbers on.',
        'My numbers...':
            'Mis cifras...',
        'Nothing finished yet this week. That is fine.':
            'Esta semana aún no has terminado nada. No pasa nada.',
        'OK: {thoughts} thoughts and {tips} tips.':
            'Correcto: {thoughts} ideas y {tips} sugerencias.',
        'Plans finished: {n}':
            'Planes terminados: {n}',
        'Save my plans to a file':
            'Guardar mis planes en un archivo',
        'Saved to {path}':
            'Guardado en {path}',
        "The file isn't valid JSON, or is over 200,000 characters.":
            'El archivo no es JSON válido o pasa de 200.000 caracteres.',
        'The file must hold an object with two lists, "thoughts" and "tips", and may add "holidays" and "title".':
            'El archivo debe contener un objeto con dos listas, "thoughts" y "tips", y puede añadir "holidays" y "title".',
        'This week you finished {n}:':
            'Esta semana terminaste {n}:',
        'This week...':
            'Esta semana...',
        'holidays line {line} is not a date like 2026-12-25.':
            'La línea {line} de holidays no es una fecha como 2026-12-25.',
        '{list} line {line} has a date.':
            'La línea {line} de {list} tiene una fecha.',
        '{list} line {line} has a link or an address.':
            'La línea {line} de {list} tiene un enlace o una dirección.',
        '{list} line {line} has control characters or extra spaces.':
            'La línea {line} de {list} tiene caracteres de control o espacios de más.',
        '{list} line {line} is not text.':
            'La línea {line} de {list} no es texto.',
        '{list} line {line} must be {low} to {high} characters long.':
            'La línea {line} de {list} debe tener de {low} a {high} caracteres.',
    },
}


# ---- Portuguese ----

LANGUAGES["pt"] = {
    "days": ('segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo'),
    "months": ('janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'),
    "date": '{day}, {d} de {month} de {year}',
    "first": '1º',
    "thoughts": (
        'Abra aquele documento que você vem evitando e leia só o primeiro parágrafo.',
        'Dez minutos de trabalho já são um começo, e costumam tornar os dez seguintes mais fáceis.',
        'Hoje você não precisa do plano inteiro, só de um primeiro passo sensato.',
        'Escreva a primeira frase, mesmo malfeita. Assim você tem algo concreto para melhorar depois.',
        'Arrume um cantinho da sua mesa e repare como o resto parece mais calmo.',
        'Escolha a menor tarefa da sua lista e termine-a antes de olhar as outras.',
        'Começar de forma imperfeita numa manhã tranquila é melhor do que esperar um momento perfeito que talvez não chegue.',
        'Coloque o primeiro passo na sua agenda para que ele tenha um lugar garantido.',
        'Grandes projetos são feitos de muitas tardes comuns. Pense só em uma tarde de cada vez.',
        'Diga em voz alta qual é a próxima ação e deixe o resto da lista esperar a vez.',
        'Em alguns dias o seu ritmo é mais lento do que você gostaria, e esse ritmo também conta.',
        'Fale consigo como falaria com uma pessoa recém-chegada na primeira semana de trabalho.',
        'Você pode continuar aprendendo algo que faz há anos.',
        'Uma manhã fraca não decide a tarde. Você pode recomeçar depois do almoço.',
        'O cansaço é uma informação, não uma falha. Ajuste o plano e siga com calma.',
        'Trate-se com a mesma compreensão que você oferece tão facilmente aos outros.',
        'Às vezes o progresso não aparece por um tempo, e de repente há uma página terminada.',
        'Não tem problema precisar ler algo duas vezes para entender.',
        'Não é preciso esperar pela confiança total. Fazer com nervosismo também é fazer.',
        'O melhor que você pode dar hoje talvez seja menos do que ontem, e está tudo bem.',
        'Feche as abas que você não está usando. A sua atenção vai agradecer em poucos minutos.',
        'Uma tarefa, uma janela, vinte e cinco minutos. Veja até onde um período tranquilo pode levar.',
        'Anote o pensamento solto que aparecer e volte ao que estava fazendo.',
        'Se puder, silencie o celular por uma hora e dê ao trabalho toda a sua atenção.',
        'Decida qual coisa faria de hoje um bom dia e reserve tempo para ela.',
        'Fazer uma coisa de cada vez costuma ser mais rápido do que parece.',
        'Uma lista clara de três coisas é melhor do que uma lista confusa de vinte.',
        'Repare quando a mente se distrai e traga-a de volta sem se repreender.',
        'Coloque a tarefa mais difícil no momento em que você tem mais energia, mesmo que não seja logo cedo.',
        'Fones de ouvido, uma bebida por perto, porta fechada. Prepare o ambiente e a concentração vem.',
        'Afaste-se da tela por cinco minutos. Você vai voltar com a cabeça um pouco mais clara.',
        'Hoje, almoce longe da sua mesa. Os e-mails podem esperar enquanto você come.',
        'Uma caminhada curta em volta do prédio também é trabalho útil para a cabeça.',
        'Um minuto longe da tela é um bom uso de uma tarde cheia.',
        'Alongue os ombros e solte a mandíbula. Talvez eles estejam tensos há horas.',
        'Se puder, saia no horário hoje. Amanhã você vai agradecer pela noite livre.',
        'Descansar faz parte do trabalho, porque o cansaço leva a repetir o mesmo erro.',
        'Descanse os olhos por um momento e deixe os ombros relaxarem.',
        'Uma boa pausa faz a segunda metade do dia parecer um novo começo.',
        'Deixe a noite ser sua. Nada nos seus e-mails precisa de você às nove da noite.',
        'Agradeça hoje a alguém por uma pequena coisa que fez sem ninguém pedir.',
        'A maioria das pessoas está fazendo o melhor que pode, com mais tarefas do que você vê.',
        'Descubra como alguém do trabalho gosta do chá ou do café. Lembrar disso é um pequeno presente.',
        'Se alguém responder de forma seca, pense num dia difícil, e não num julgamento sobre você.',
        'Segure a porta, divida os biscoitos e deixe a outra pessoa terminar de falar.',
        'Um olá rápido e uma pergunta sobre o fim de semana podem ser a melhor parte da manhã.',
        'Quando alguém que acabou de chegar perguntar algo óbvio, lembre que você também já perguntou.',
        'Reconheça em voz alta quando a ideia de alguém da equipe melhorou o seu trabalho.',
        'Responda a uma mensagem com um pouco de simpatia. Não custa nada e é bem recebido.',
        'Procure alguém que tem falado pouco nas reuniões e pergunte como essa pessoa está.',
        'Termine o que está quase terminado antes de começar algo novo.',
        'Feito e bom o bastante costuma ser mais útil do que perfeito e inacabado.',
        'Resolva hoje um assunto pendente e repare no pequeno alívio que vem depois.',
        'Os últimos dez por cento muitas vezes são só alguns minutos de cuidado. Dedique-os hoje.',
        'Envie o e-mail que está esperando nos seus rascunhos. Provavelmente ele está bom assim.',
        'Marque como concluído, respire e aproveite a satisfação de ter terminado.',
        'Uma coisa pequena terminada vale mais do que uma grande pela metade.',
        'Antes de encerrar o dia, anote o primeiro passo de amanhã para não ter que lembrar dele.',
        'Leia mais uma vez, corrija o que encontrar e envie.',
        'Encerrar o dia com um resultado concluído deixa a noite mais leve.',
        'Fazer uma pergunta cedo costuma poupar uma hora de esforço silencioso depois.',
        'A maioria das pessoas gosta de compartilhar o que sabe. Pergunte sem pedir desculpas.',
        '"Não sei como continuar" é uma frase clara e útil, e dá à equipe algo concreto com que ajudar.',
        'Peça o que você precisa com palavras simples e dê às pessoas a chance de dizer sim.',
        'Duas pessoas olhando para um problema costumam resolvê-lo mais rápido do que uma só.',
        'Precisar de ajuda não faz de você um peso. Você faz parte da equipe.',
        'Leve uma pergunta específica, e a pessoa a quem você perguntar poderá dar uma resposta específica.',
        'Se as instruções não estão claras, pedir esclarecimentos faz parte de fazer bem o trabalho.',
        'Ofereça ajuda quando puder e aceite-a quando precisar. As duas coisas ficam mais fáceis com a prática.',
        'Provavelmente alguém perto de você já resolveu isso antes. Vá procurar essa pessoa.',
        'Anote as coisas que você conseguiu resolver esta semana. Elas somam mais do que você imagina.',
        'Ser iniciante em algo novo é sinal de que o seu trabalho continua crescendo.',
        'Observe como alguém que você admira lida com uma ligação difícil e aproveite uma ideia.',
        'Leia uma página útil na sua pausa e conte isso como um bom dia para a sua mente.',
        'Explicar uma tarefa a outra pessoa é uma forma surpreendentemente boa de aprendê-la.',
        'Não tem problema dizer "ainda não sei isso" e depois ir descobrir.',
        'Todo sistema desconhecido parece confuso até você usá-lo algumas vezes.',
        'Pergunte a alguém com mais experiência como aprendeu. A resposta costuma tranquilizar.',
        'As habilidades vêm da repetição. Repita a coisa pequena e deixe que ela fique fácil.',
        'Um pouco de curiosidade pode tornar uma tarefa comum mais interessante.',
        'Um erro percebido cedo é só uma correção, e a maioria é percebida cedo.',
        'Corrija, avise quem precisa saber e depois deixe o incômodo passar.',
        'Quase todo erro no trabalho parece menor uma semana depois do que no momento.',
        'Um deslize não apaga os anos de trabalho cuidadoso que você tem.',
        'Quando algo dá errado, olhe primeiro para o processo e só depois para a pessoa.',
        'Todas as pessoas à sua volta já enviaram um e-mail para a pessoa errada pelo menos uma vez.',
        'Fique com a lição que um erro oferece e deixe o resto para trás.',
        'Assumir um erro com simplicidade costuma gerar mais confiança do que nunca ter errado.',
        'Pessoas cuidadosas também têm dias desajeitados, e eles passam até a noite.',
        'No mês que vem, você não vai lembrar da maioria dos pequenos tropeços de hoje.',
        'Um dia tranquilo e sem emergências é um bom dia, mesmo que ninguém comente.',
        'Repare nos pequenos prazeres: uma caneca quente, a caixa de entrada vazia, um minuto de calma.',
        'Nem todo dia precisa de uma grande conquista. Trabalhar com calma e de forma agradável está ótimo.',
        'Aproveite a reunião que termina cinco minutos mais cedo e use o tempo como quiser.',
        'Um dia comum bem feito é motivo de um orgulho tranquilo.',
        'Um bom trabalho muitas vezes não chama atenção de fora, e está tudo bem.',
        'Deixe uma tarde agradável ser apenas agradável, sem esperar que seja produtiva.',
        'As pequenas rotinas do dia, como o primeiro café e os rostos conhecidos, merecem a sua atenção.',
        'Hoje você esteve presente e fez a sua parte, e isso é bastante.',
        'Esta noite, reserve um momento para lembrar de uma coisa que deu certo hoje.',
        'Um minuto tranquilo entre duas tarefas não é tempo perdido; é assim que a próxima começa bem.',
    ),
    "tips": (
        'Beba um copo de água devagar, longe da tela.',
        'Gire os ombros para trás cinco vezes, bem devagar.',
        'Descanse os olhos por vinte segundos: olhe para longe ou feche-os.',
        'Estique os braços para cima, na cadeira ou em pé, e respire fundo.',
        'Vá até a sala ou a janela mais distante que puder e volte.',
        'Confira a sua postura e deixe os ombros descerem, longe das orelhas.',
        'Gire o pescoço com suavidade de um lado para o outro, só até onde for confortável.',
        'Abra e feche as mãos dez vezes para soltar os dedos.',
        'Fixe o documento que você mais abre para que ele fique a um clique.',
        'Faça um passeio curto lá fora, a pé ou de cadeira de rodas, como for melhor para você.',
        'Prepare uma bebida quente ou fresca e aproveite-a longe da tela.',
        'Concentre a atenção em algo calmo: uma vista, um som ou uma textura.',
        'Escreva o próximo passo de uma tarefa que você deixou pela metade.',
        'Apoie os pés no chão e alongue a coluna, na cadeira ou em pé, durante dez respirações.',
        'Silencie um grupo de conversa que você só lê por cima.',
        'Solte a mandíbula e relaxe a testa por um momento.',
        'Movimente-se por dois minutos da forma que for boa para você hoje.',
        'Reserve quinze minutos na sua agenda para a tarefa que você vive adiando.',
        'Ajuste a cadeira, a tela ou o teclado para que uma coisa fique mais confortável.',
        'Se puder, faça o caminho mais longo até a sua próxima reunião ou chamada.',
        'Salve um modelo para um e-mail que você escreve várias vezes.',
        'Aprenda um atalho de teclado do programa que você mais usa.',
        'Beba um copo inteiro de água antes do próximo café ou chá.',
        'Suba os ombros até as orelhas e depois deixe-os descer devagar.',
        'Saia um pouco ou abra uma janela para um minuto de ar fresco.',
        'Respire devagar cinco vezes, deixando cada expiração um pouco mais longa.',
        'Faça uma pausa tranquila de um minuto antes de abrir a próxima mensagem.',
        'Anote uma coisa boa que já aconteceu hoje.',
        'Feche os olhos durante três respirações e repare em como você se sente.',
        'Diga três coisas que você percebe agora, com qualquer um dos sentidos.',
        'Anote uma coisa boa que você espera desta semana.',
        'Programe um alarme de dois minutos e fique esse tempo longe de qualquer tela.',
        'Aproveite algo pequeno por perto, como uma planta ou a sua caneca favorita.',
        'Pense em algo que você fez bem esta semana e reconheça isso.',
        'Ouça uma música favorita do começo ao fim, sem mais nada aberto.',
        'Inspire contando até quatro e expire contando até seis, três vezes.',
        'Respire uma vez antes de reagir ao próximo pequeno incômodo.',
        'Anote algo que fez você rir recentemente.',
        'Durante um minuto, repare em algo agradável: um som, um cheiro ou algo que você toca.',
        'Lembre de um lugar de que você gosta muito e imagine-o por trinta segundos.',
        'Diga "por enquanto está bom assim" sobre uma tarefa pequena e siga em frente.',
        'Escreva uma frase sobre algo pelo qual você sente gratidão.',
        'Saboreie o próximo gole da sua bebida e repare no sabor.',
        'Faça uma pausa curta entre duas tarefas antes de começar a próxima.',
        'Procure hoje uma coisa que saia melhor do que você esperava.',
        'Escolha uma palavra que descreva como você quer que seja a sua tarde.',
        'Deixe a mente descansar por sessenta segundos e depois volte à próxima tarefa.',
        'Sinta os pés no chão e perceba a estabilidade por um momento.',
        'Lembre de algo gentil que alguém fez por você e aproveite a lembrança.',
        'Anote uma ideia que você quer retomar mais tarde e deixe-a descansar.',
        'Arrume um cantinho da sua mesa, só um.',
        'Responda a uma mensagem que está esperando há algum tempo.',
        'Escreva a principal tarefa de amanhã num post-it ou nas suas notas.',
        'Feche as abas do navegador de que você não precisa mais.',
        'Agradeça a alguém da equipe por algo que essa pessoa fez recentemente.',
        'Arquive cinco e-mails antigos de que você não precisa mais.',
        'Renomeie um arquivo com nome confuso para encontrá-lo facilmente depois.',
        'Tire um ou dois arquivos soltos da área de trabalho.',
        'Apague um lembrete antigo que não vale mais.',
        'Dê um título claro a um documento que você abre com frequência.',
        'Risque um item pequeno da sua lista de tarefas.',
        'Cancele a assinatura de uma newsletter que você nunca lê.',
        'Limpe o teclado ou a tela com um pano macio.',
        'Deixe uma caneta, um caderno e água onde você alcance facilmente.',
        'Escreva uma nota curta para amanhã sobre onde você parou hoje.',
        'Escolha a tarefa mais importante desta tarde e faça-a primeiro.',
        'Esvazie a lixeira ou o cesto de reciclagem da sua mesa.',
        'Atualize uma nota de andamento para que outras pessoas vejam como as coisas estão.',
        'Organize a pasta de downloads movendo um punhado de arquivos.',
        'Crie um lembrete para uma coisa que você costuma esquecer.',
        'Desative uma notificação de que você não precisa de verdade.',
        'Adicione aos favoritos uma página que você vive procurando.',
        'Escreva um resumo de duas linhas de uma reunião enquanto ela está fresca na memória.',
        'Pergunte se uma reunião recorrente poderia ser um pouco mais curta.',
        'Defina o seu único objetivo para a próxima hora e anote-o.',
        'Pergunte a alguém da equipe como está sendo o dia e ouça com atenção.',
        'Compartilhe um link útil com alguém que possa gostar dele.',
        'Cumprimente alguém com quem você nunca falou.',
        'Envie uma nota rápida de agradecimento a alguém que ajudou você recentemente.',
        'Cumprimente as pessoas com simpatia no início da sua próxima chamada.',
        'Pergunte a alguém da equipe o que espera de bom nesta semana.',
        'Dê parabéns a alguém por uma pequena conquista que você notou.',
        'Convide alguém do trabalho para uma conversa curta com chá ou café, ao vivo ou por chamada.',
        'Elogie algo específico que alguém do trabalho fez bem.',
        'Aprenda o nome de alguém que você vê sempre, mas ainda não conhece.',
        'Compartilhe uma dica útil com alguém da equipe que possa precisar dela.',
        'Peça a alguém que recomende uma música, uma série ou um livro.',
        'Procure alguém do trabalho que tem falado pouco ultimamente e pergunte como está.',
        'Ofereça ajuda com uma pequena coisa se alguém parecer ter muito trabalho.',
        'Cumprimente com simpatia a próxima pessoa que encontrar.',
        'Conte a alguém do trabalho uma palavra gentil que você ouviu sobre essa pessoa.',
        'Pergunte a alguém do trabalho o que deixou a semana mais fácil.',
        'Envie uma mensagem simpática a alguém com quem você já trabalhou.',
        'Agradeça a quem mantém os espaços compartilhados funcionando bem.',
        'Apresente duas pessoas do trabalho que podem gostar de se conhecer.',
        'Pergunte a alguém da equipe como você pode facilitar a passagem de uma tarefa.',
        'Compartilhe uma piada pequena e inofensiva com alguém por perto.',
        'Coloque um pouco mais de simpatia no próximo pedido ou agradecimento que fizer.',
        'Pergunte a alguém do trabalho o que gosta de fazer fora do trabalho.',
        'Ouça com toda a atenção a próxima pessoa que falar com você, sem fazer outras coisas.',
    ),
    "done": (
        'Ótimo. Esse já está concluído.',
        'Muito bem. É bom terminar alguma coisa.',
        'Bom trabalho. Faça uma pausa curta antes do próximo.',
        'Bom. Pequenas tarefas concluídas vão se somando.',
        'Está feito. Pode se alegrar com isso.',
        'Ótimo. Um item a menos na sua lista.',
    ),
    "text": {
        HELP: """hello-world mostra uma saudação, um pensamento e algo simples para
experimentar.

Na última pergunta, digite plano para o plano de hoje, feito quando
terminar, ou menu (ou m) para ver as opções. Enter fecha, e q, x e sair
fecham o programa em qualquer pergunta. Na pergunta do plano, repetir
traz de volta um plano anterior não terminado. Depois de feito, aparecem
os seus 3 últimos planos terminados. A opção 1 do menu mostra todos, a
opção 7 esquece um e a opção 8 oculta o pensamento e a dica. No menu,
Enter volta.
Você também pode executar hello.cmd com uma destas opções:
  --plain         Mostra só a saudação, em inglês
  --stats         Mostra o que está salvo neste computador
  --reset         Apaga tudo o que foi salvo (pergunta antes)
  --remind on     Abre todo dia ao iniciar a sessão (off desativa)
  --streak off    Oculta a mensagem de dias seguidos (on mostra)
  --version       Mostra a versão
  --check-content ARQUIVO
                  Verifica um arquivo de conteúdo da organização
  --help          Mostra este texto

Códigos de saída: 0 quando funcionou, 1 quando um comando falhou ou não
foi possível escrever na tela, 2 para uma opção desconhecida.

As notas salvas ficam neste computador, na sua pasta de usuário. Nada é
enviado para lugar nenhum. A equipe de TI que pode ler os arquivos deste
computador poderia lê-las.""",
        MENU_HELP: """Palavras que você pode digitar na última pergunta:
  feito  marca o plano de hoje como terminado e pede o próximo
  plano  define ou muda o plano de hoje
  menu   abre estas opções
  q      fecha a janela, assim como Enter
Na pergunta do plano, repetir traz de volta o seu plano anterior não
terminado. Quando aparece "Você fez?", n quer dizer ainda não, e você
pode manter o plano para hoje. q fecha em qualquer pergunta.
Neste menu, 1 mostra o que está salvo, 7 esquece um plano terminado
e 8 oculta o pensamento e a dica.
Digite m para ver as opções de novo. Nada é enviado para lugar nenhum.""",
        SAVED_PLAN: 'Salvo. Digite feito quando terminar, ou o programa pergunta na próxima vez que você o abrir.',
        GREETING: 'Olá, mundo!',
        'hello.cmd is in this folder:':
            'O hello.cmd está nesta pasta:',
        'Shortened to {n} characters.':
            'Encurtado para {n} caracteres.',
        'Your saved file was damaged, so hello-world set it aside as a backup copy and started fresh. Your earlier days and plan could not be read. Menu option 4 deletes the backup.':
            'O seu arquivo salvo estava danificado, então o hello-world guardou-o como cópia de segurança e começou do zero. Não foi possível ler os seus dias nem o seu plano anteriores. A opção 4 do menu apaga a cópia.',
        'Backup copy: ':
            'Cópia de segurança: ',
        'In the folder: ':
            'Na pasta: ',
        'Sorry, "{shown}" is not one of the choices.':
            'Desculpe, "{shown}" não é uma das opções.',
        'A plan needs a word or two, so nothing was saved.':
            'Um plano precisa de uma ou duas palavras, então nada foi salvo.',
        'The sign-in reminder works on Windows only.':
            'O lembrete ao iniciar a sessão só funciona no Windows.',
        'Your organization has turned off opening at sign-in.':
            'A sua organização desativou a abertura ao iniciar a sessão.',
        'The reminder cannot be set up from this folder.':
            'Não é possível configurar o lembrete a partir desta pasta.',
        'Could not set up the reminder.':
            'Não foi possível configurar o lembrete.',
        'Done. hello-world will open once a day when you sign in.':
            'Concluído. O hello-world vai abrir uma vez por dia ao iniciar a sessão.',
        'To stop it, choose option 2 in the menu.':
            'Para desativar, escolha a opção 2 do menu.',
        'Could not turn off the sign-in reminder.':
            'Não foi possível desativar o lembrete ao iniciar a sessão.',
        'Done. The sign-in reminder is off.':
            'Concluído. O lembrete ao iniciar a sessão está desativado.',
        'Saved on this computer in:':
            'Salvo neste computador, em:',
        'Saved in your own user folder on this computer.':
            'Salvo na sua própria pasta de usuário neste computador.',
        'Days you opened it in the last {days} days: {n} (last 7 days: {recent})':
            'Dias em que você o abriu nos últimos {days} dias: {n} (últimos 7 dias: {recent})',
        'Times you marked a plan done: {n}':
            'Vezes que você marcou um plano como feito: {n}',
        'Your current plan: ':
            'O seu plano atual: ',
        'Earlier plan (for same): ':
            'Plano anterior (para repetir): ',
        'Days-in-a-row message: shown.':
            'Mensagem de dias seguidos: visível.',
        'Days-in-a-row message: hidden.':
            'Mensagem de dias seguidos: oculta.',
        'Opens by itself at sign-in: turned off by your organization.':
            'Abre automaticamente ao iniciar a sessão: desativado pela organização.',
        'Opens by itself at sign-in: on.':
            'Abre automaticamente ao iniciar a sessão: sim.',
        'Opens by itself at sign-in: off.':
            'Abre automaticamente ao iniciar a sessão: não.',
        "It never leaves this computer. Others who can read this computer's files, such as IT staff, could read it.":
            'Estes dados nunca saem deste computador. Outras pessoas que podem ler os arquivos dele, como a equipe de TI, poderiam lê-los.',
        'After tidying, the file holds only this:':
            'Depois da arrumação, o arquivo contém apenas isto:',
        'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
            'Apagar todas as notas, datas e planos salvos neste computador? (s ou n, Enter para cancelar) > ',
        'Nothing was deleted.':
            'Nada foi apagado.',
        'Could not delete everything.':
            'Não foi possível apagar tudo.',
        'Delete these yourself:':
            'Apague estes arquivos manualmente:',
        'Could not list the folder, so backup copies may remain:':
            'Não foi possível ler a pasta, então podem restar cópias de segurança:',
        'Done. Everything saved was deleted.':
            'Concluído. Tudo o que estava salvo foi apagado.',
        'Another open hello-world window cannot put it back.':
            'Outra janela aberta do hello-world não consegue restaurar esses dados.',
        'Close any other open hello-world window, or it may save its notes again.':
            'Feche qualquer outra janela aberta do hello-world, ou ela pode salvar as notas de novo.',
        'Everything saved was deleted in another window, so this was not saved.':
            'Tudo o que estava salvo foi apagado em outra janela, então isto não foi salvo.',
        'The other open window had also finished a plan.':
            'A outra janela aberta também tinha terminado um plano.',
        'The other open window changed the plan, so its plan is kept.':
            'A outra janela aberta mudou o plano, então o plano dela foi mantido.',
        'Type plan at the last prompt to set one.':
            'Digite plano na última pergunta para definir um.',
        'That looks like a command, not a plan, so nothing was saved.':
            'Isso parece um comando, não um plano, então nada foi salvo.',
        'Type your plan, or press Enter to go back.':
            'Digite o seu plano ou pressione Enter para voltar.',
        'Finished lately:':
            'Terminados recentemente:',
        'Your plan today: ':
            'O seu plano de hoje: ',
        'Your plan from {date}: ':
            'O seu plano de {date}: ',
        'Earlier plan: ':
            'Plano anterior: ',
        'Type the next plan, or Enter to close > ':
            'Digite o próximo plano, ou Enter para fechar > ',
        'Type the next plan, same to reuse the earlier plan, or Enter to close > ':
            'Digite o próximo plano, repetir para usar o plano anterior, ou Enter para fechar > ',
        "Type today's plan, or Enter to keep it > ":
            'Digite o plano de hoje, ou Enter para mantê-lo > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
            'Digite o plano de hoje, repetir para usar o plano anterior, ou Enter para mantê-lo > ',
        "Type today's plan, or Enter to go back > ":
            'Digite o plano de hoje, ou Enter para voltar > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
            'Digite o plano de hoje, repetir para usar o plano anterior, ou Enter para voltar > ',
        'Closing.':
            'Fechando.',
        'There is no earlier plan to reuse yet. Nothing changed.':
            'Ainda não há um plano anterior para repetir. Nada mudou.',
        'Nothing changed.':
            'Nada mudou.',
        'Could not save that on this computer. Your plan is unchanged.':
            'Não foi possível salvar isso neste computador. O seu plano não mudou.',
        'No finished plans are saved.':
            'Não há planos terminados salvos.',
        'Type the number to forget (1 to {n}), or Enter to keep them all > ':
            'Digite o número a esquecer (1 a {n}), ou Enter para manter todos > ',
        'There is no number "{typed}" on the list. Type a number from 1 to {n}, or press Enter to keep them all.':
            'Não há nenhum número "{typed}" na lista. Digite um número de 1 a {n}, ou pressione Enter para manter todos.',
        'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
            'Esquecer também como plano anterior, usado por repetir? (s ou n, Enter para mantê-lo) > ',
        'Type y or n, or press Enter to keep it for same.':
            'Digite s ou n, ou pressione Enter para mantê-lo para repetir.',
        'That plan was already forgotten. Nothing changed.':
            'Esse plano já tinha sido esquecido. Nada mudou.',
        'Forgotten: ':
            'Esquecido: ',
        'Same still has it.':
            'Ainda é possível recuperá-lo com repetir.',
        'Could not save that on this computer. Nothing changed.':
            'Não foi possível salvar isso neste computador. Nada mudou.',
        'Options':
            'Opções',
        'Show what is saved on this computer':
            'Mostrar o que está salvo neste computador',
        'Open once a day at sign-in (turned off by your organization)':
            'Abrir todo dia ao iniciar a sessão (desativado pela organização)',
        'Turn off: open once a day at sign-in (now on)':
            'Desativar: abrir todo dia ao iniciar a sessão (agora ativado)',
        'Turn on: open once a day at sign-in (now off)':
            'Ativar: abrir todo dia ao iniciar a sessão (agora desativado)',
        'Days-in-a-row message (hidden by your organization)':
            'Mensagem de dias seguidos (oculta pela sua organização)',
        'Hide the days-in-a-row message (now shown)':
            'Ocultar a mensagem de dias seguidos (agora visível)',
        'Show the days-in-a-row message (now hidden)':
            'Mostrar a mensagem de dias seguidos (agora oculta)',
        'Delete everything saved':
            'Apagar tudo o que está salvo',
        'Help':
            'Ajuda',
        "Set today's plan (turned off by your organization)":
            'Definir o plano de hoje (desativado pela sua organização)',
        'Forget a finished plan (turned off by your organization)':
            'Esquecer um plano terminado (desativado pela sua organização)',
        "Set or change today's plan":
            'Definir ou mudar o plano de hoje',
        'Forget one finished plan':
            'Esquecer um plano terminado',
        'Thought and tip (hidden by your organization)':
            'Pensamento e dica (ocultos pela sua organização)',
        'Hide the thought and tip (now shown)':
            'Ocultar o pensamento e a dica (agora visíveis)',
        'Show the thought and tip (now hidden)':
            'Mostrar o pensamento e a dica (agora ocultos)',
        '{date}: ':
            '{date}: ',
        'Enter':
            'Enter',
        'Back to the last prompt':
            'Voltar à última pergunta',
        'Choose 1 to 11, or Enter to go back > ':
            'Escolha de 1 a 11, ou Enter para voltar > ',
        'Choose 1 to 11, m to list the options, or Enter to go back > ':
            'Escolha de 1 a 11, m para listar as opções, ou Enter para voltar > ',
        'The saved file could not be read just now, so this may be out of date.':
            'Não foi possível ler o arquivo salvo agora, então isto pode estar desatualizado.',
        'Type full to see the whole file, or Enter to go on > ':
            'Digite tudo para ver o arquivo inteiro, ou Enter para continuar > ',
        'Could not save that choice on this computer.':
            'Não foi possível salvar essa escolha neste computador.',
        'Your organization has hidden the days-in-a-row message.':
            'A sua organização ocultou a mensagem de dias seguidos.',
        'Done. The days-in-a-row message is on.':
            'Concluído. A mensagem de dias seguidos está ativada.',
        'Done. The days-in-a-row message is off.':
            'Concluído. A mensagem de dias seguidos está desativada.',
        'Plans are turned off by your organization.':
            'Os planos foram desativados pela sua organização.',
        'Your organization has hidden the thought and tip.':
            'A sua organização ocultou o pensamento e a dica.',
        'Done. The thought and tip are on.':
            'Concluído. O pensamento e a dica estão ativados.',
        'Done. The thought and tip are off.':
            'Concluído. O pensamento e a dica estão desativados.',
        'Type 1 to 11, or press Enter to go back.':
            'Digite de 1 a 11, ou pressione Enter para voltar.',
        'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
            'Quer que o hello-world abra uma vez por dia ao iniciar a sessão? (s ou n, Enter para agora não) > ',
        'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
            'Quer que o hello-world abra uma vez por dia ao iniciar a sessão para perguntar sobre o seu plano? (s ou n, Enter para agora não) > ',
        'Type y or n, or press Enter for not now.':
            'Digite s ou n, ou pressione Enter para agora não.',
        'That was not understood. It will ask again on a later visit.':
            'Resposta não entendida. O programa pergunta de novo em outra visita.',
        'It will ask again on a later visit. Menu option 2 also turns it on.':
            'O programa vai perguntar de novo em outra visita. A opção 2 do menu também ativa isso.',
        'No problem. Menu option 2 turns it on later.':
            'Sem problema. A opção 2 do menu ativa isso mais tarde.',
        "Okay. It won't ask again. Menu option 2 turns it on.":
            'Certo. O programa não vai perguntar de novo. A opção 2 do menu ativa isso.',
        'Okay. It will ask again on a later visit. Type n to stop it.':
            'Certo. O programa vai perguntar de novo em outra visita. Digite n para que ele não pergunte mais.',
        'When did you finish it?':
            'Quando você terminou?',
        'Today':
            'Hoje',
        'Type a number from 1 to {n}, or Enter for 1 > ':
            'Digite um número de 1 a {n}, ou Enter para 1 > ',
        'Type a number from 1 to {n}, or press Enter.':
            'Digite um número de 1 a {n}, ou pressione Enter.',
        'That looks like more than one thing. Finishing the first part still counts.':
            'Isso parece ser mais de uma coisa. Terminar a primeira parte já conta.',
        'There is no plan to mark as done. Type plan to set one.':
            'Não há nenhum plano para marcar como feito. Digite plano para definir um.',
        'Could not save that on this computer. The plan is still open.':
            'Não foi possível salvar neste computador. O plano continua em aberto.',
        'Your plan from over two weeks ago was put away. Type same at the plan prompt to bring it back.':
            'O seu plano de mais de duas semanas atrás foi guardado. Digite repetir na pergunta do plano para trazê-lo de volta.',
        "Press Enter at each question to skip it, and once more to close. That's it.":
            'Pressione Enter em cada pergunta para pulá-la, e mais uma vez para fechar. É só isso.',
        'Welcome.':
            'Boas-vindas.',
        'Each day you get one thought and one small thing to try, the same for everyone.':
            'Todo dia você recebe um pensamento e algo simples para experimentar, iguais para todas as pessoas.',
        'If you type a plan, it asks next time how it went. Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks.':
            'Se você digitar um plano, na próxima vez ele pergunta como foi. Suas notas ficam neste computador e nunca são enviadas para lugar nenhum. Como qualquer arquivo de trabalho, elas não são secretas, então use-as só para tarefas do dia a dia.',
        'Type menu at the end for the options.':
            'Digite menu no final para ver as opções.',
        'Welcome back. Glad you are here.':
            'Olá de novo. Que bom ter você aqui.',
        'You have opened this {row} days in a row. Nice to see you.':
            'Você abriu o hello-world {row} dias seguidos. Que bom ver você.',
        'Last time you planned: ':
            'O seu último plano: ',
        'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
            'Você fez? (s para sim, n para ainda não, Enter para pular) > ',
        'Type y or n, or press Enter to skip.':
            'Digite s ou n, ou pressione Enter para pular.',
        'Could not save that on this computer. Your answer was not counted.':
            'Não foi possível salvar neste computador. A sua resposta não contou.',
        'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
            'Tudo bem. Manter para hoje? (s ou n, Enter para manter) > ',
        'Type y to keep it, n to clear it, or press Enter to keep it.':
            'Digite s para manter, n para apagar, ou pressione Enter para manter.',
        'Cleared. Type same at a plan prompt if you want it back.':
            'Apagado. Digite repetir na pergunta do plano para trazê-lo de volta.',
        'Kept for today.':
            'Mantido para hoje.',
        'That was not understood. Your plan is left as it was.':
            'A resposta não foi entendida. O seu plano ficou como estava.',
        'Your plan is still open.':
            'O seu plano continua em aberto.',
        'Thought for today:':
            'Pensamento do dia:',
        'Try this today:':
            'Experimente hoje:',
        'Your plan for today: ':
            'O seu plano para hoje: ',
        'Still open since {date}:':
            'Em aberto desde {date}:',
        '(Enter to skip)':
            '(Enter para pular)',
        '(A plan typed here replaces the old one. Enter to skip)':
            '(Um plano digitado aqui substitui o anterior. Enter para pular)',
        '(Type same to reuse it, or Enter to skip)':
            '(Digite repetir para usá-lo de novo, ou Enter para pular)',
        'What is one thing you want to get done today?':
            'Que tarefa você quer concluir hoje? Basta uma.',
        'There is no earlier plan to reuse yet. Nothing was saved.':
            'Ainda não há um plano anterior para repetir. Nada foi salvo.',
        'Your notes could not be saved on this computer. This screen still works.':
            'Não foi possível salvar as suas notas neste computador. Esta tela continua funcionando.',
        'Type menu, or Enter to close > ':
            'Digite menu, ou Enter para fechar > ',
        'Type done, plan or menu, or Enter to close > ':
            'Digite feito, plano ou menu, ou Enter para fechar > ',
        'Type plan or menu, or Enter to close > ':
            'Digite plano ou menu, ou Enter para fechar > ',
        'Type done, plan or menu, or press Enter to close.':
            'Digite feito, plano ou menu, ou pressione Enter para fechar.',
        'Type plan or menu, or press Enter to close.':
            'Digite plano ou menu, ou pressione Enter para fechar.',
        "The saved file can't be read right now, or it is damaged.":
            'Não é possível ler o arquivo salvo agora, ou ele está danificado.',
        'Nothing was changed. Saved in: ':
            'Nada foi alterado. Salvo em: ',
        'Deleting saved notes needs a person at the keyboard.':
            'Para apagar as notas salvas é preciso haver uma pessoa ao teclado.',
        '{option} needs on or off. Here are the options.':
            '{option} precisa de on ou off. Estas são as opções.',
        'Unknown option: {option}. Here are the options.':
            'Opção desconhecida: {option}. Estas são as opções.',
        '&Done':
            '&Feito',
        '&Not yet':
            '&Ainda não',
        'S&kip':
            '&Pular',
        '&Save':
            '&Salvar',
        '&I did it':
            '&Eu fiz',
        '&Options':
            '&Opções',
        'Close':
            'Fechar',
        'Not today':
            'Hoje não',
        'Did you do it?':
            'Você fez?',
        'Done. A reminder comes when you sign in, if there is a plan to ask about.':
            'Concluído. Ao entrar, aparece um lembrete se houver um plano para acompanhar.',
        'Done. The Start menu opens a window with buttons.':
            'Concluído. O menu Iniciar abre uma janela com botões.',
        'Done. The Start menu opens this text screen.':
            'Concluído. O menu Iniciar abre esta tela de texto.',
        'More options':
            'Mais opções',
        'Remind me when I sign in':
            'Lembrar-me ao entrar',
        'Show the thought and tip':
            'Mostrar o pensamento e a dica',
        'Type your plan in the box.':
            'Digite seu plano na caixa.',
        'Use a window with buttons (now this text screen)':
            'Usar uma janela com botões (agora esta tela de texto)',
        'Use the text screen':
            'Usar a tela de texto',
        'Use this text screen (now a window with buttons)':
            'Usar esta tela de texto (agora uma janela com botões)',
        'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
            'Quer um lembrete ao entrar? Ele mostra o seu plano da última vez, e você responde com um clique. Você pode desativá-lo em Opções.',
        'Window or text screen (set by your organization)':
            'Janela ou tela de texto (definido pela sua organização)',
        'Your organization has set hello-world to open as a text screen.':
            'Sua organização configurou o hello-world para abrir como tela de texto.',
        'Saved.':
            'Salvo.',
        'Save your plan before closing?':
            'Salvar seu plano antes de fechar?',
        'Delete all saved notes, dates and plans on this computer?':
            'Apagar todas as notas, datas e planos salvos neste computador?',
        'Turn off: reminder when you sign in (now on)':
            'Desativar: lembrete ao entrar (agora ativado)',
        'Turn on: reminder when you sign in (now off)':
            'Ativar: lembrete ao entrar (agora desativado)',
        'Reminder when you sign in (turned off by your organization)':
            'Lembrete ao entrar (desativado pela sua organização)',
        'Reminder when you sign in: on.':
            'Lembrete ao entrar: ativado.',
        'Reminder when you sign in: off.':
            'Lembrete ao entrar: desativado.',
        'Reminder when you sign in: turned off by your organization.':
            'Lembrete ao entrar: desativado pela sua organização.',
        'Show the days-in-a-row message':
            'Mostrar a mensagem de dias seguidos',
        'Done. The thought and tip show next time you open hello-world.':
            'Concluído. O pensamento e a dica aparecem na próxima vez que você abrir o hello-world.',
        "Clear today's plan?":
            'Apagar o plano de hoje?',
        'Next plan, if you want one:':
            'Próximo plano, se quiser:',
        'A few things? Put ; between them.':
            'Várias coisas? Separe com ;',
        'A plan can be up to {n} characters.':
            'Um plano pode ter até {n} caracteres.',
        'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
            'Você fez? (s para todas, n para ainda não, os números das que fez, Enter para pular) > ',
        'Last time you planned:':
            'O seu último plano:',
        'The rest is kept for today.':
            'O resto fica para hoje.',
        'Tick the ones you did, then click Done. With none ticked, Done means all of them.':
            'Marque as que você fez e clique em Feito. Sem nenhuma marcada, Feito vale para todas.',
        'Type y for all, n for not yet, or the numbers you did, such as 1 3. Enter skips.':
            'Digite s para todas, n para ainda não, ou os números das que fez, como 1 3. Enter pula.',
        'Your settings were kept.':
            'Suas configurações foram mantidas.',
        'Language (set by your organization)':
            'Idioma (definido pela sua organização)',
        'Language (now {name})':
            'Idioma (agora {name})',
        'following Windows':
            'segue o Windows',
        'Your organization shows hello-world in English.':
            'Sua organização mostra o hello-world em inglês.',
        'Follow Windows':
            'Seguir o Windows',
        'Type a number from 1 to {n}, or Enter to keep it > ':
            'Digite um número de 1 a {n}, ou Enter para manter > ',
        'Done. The new language shows next time you open hello-world.':
            'Pronto. O novo idioma aparece quando você abrir o hello-world de novo.',
        'Language...':
            'Idioma...',
        'Hello, {name}!':
            'Olá, {name}!',
        'One thing to get done today? Open hello-world to plan it.':
            'Uma coisa para concluir hoje? Abra o hello-world para planejar.',
        '&Open':
            '&Abrir',
        'Reminder settings...':
            'Configurações do lembrete...',
        'Greet me by name':
            'Cumprimentar pelo meu nome',
        'At sign-in':
            'Ao entrar',
        'At {at}':
            'Às {at}',
        'Also on days with no plan':
            'Também nos dias sem plano',
        'Open hello-world after I answer':
            'Abrir o hello-world depois de responder',
        'Not on weekends':
            'Não nos fins de semana',
        'Done. A reminder comes at {at} each day, if there is a plan to ask about.':
            'Pronto. Todo dia às {at} aparece um lembrete se houver um plano para acompanhar.',
        'Send feedback...':
            'Enviar comentários...',
        '"holidays" must be a list of at most {n} dates.':
            '"holidays" deve ser uma lista de no máximo {n} datas.',
        '"title" must be 1 to 40 characters of plain text, with no link or address.':
            '"title" deve ter de 1 a 40 caracteres de texto simples, sem links nem endereços.',
        '"{list}" must be a list of {low} to {high} lines.':
            '"{list}" deve ser uma lista de {low} a {high} linhas.',
        "Can't read {path}: {error}":
            'Não é possível ler {path}: {error}',
        'Could not save that on this computer.':
            'Não foi possível salvar neste computador.',
        'Days you opened hello-world: {n}':
            'Dias em que você abriu o hello-world: {n}',
        'Keep a longer history':
            'Manter um histórico mais longo',
        'Keep my numbers':
            'Manter meus números',
        'Longest run of days: {n}':
            'Maior sequência de dias: {n}',
        "Mark today's plan done":
            'Marcar o plano de hoje como feito',
        "Mark today's plan done (plans are turned off)":
            'Marcar o plano de hoje como feito (planos desativados)',
        'My numbers are off. Turn them on under Options, or with --set numbers on.':
            'Seus números estão desativados. Ative em Opções ou com --set numbers on.',
        'My numbers...':
            'Meus números...',
        'Nothing finished yet this week. That is fine.':
            'Nada concluído ainda esta semana. Tudo bem.',
        'OK: {thoughts} thoughts and {tips} tips.':
            'OK: {thoughts} pensamentos e {tips} dicas.',
        'Plans finished: {n}':
            'Planos concluídos: {n}',
        'Save my plans to a file':
            'Salvar meus planos em um arquivo',
        'Saved to {path}':
            'Salvo em {path}',
        "The file isn't valid JSON, or is over 200,000 characters.":
            'O arquivo não é JSON válido ou tem mais de 200.000 caracteres.',
        'The file must hold an object with two lists, "thoughts" and "tips", and may add "holidays" and "title".':
            'O arquivo deve conter um objeto com duas listas, "thoughts" e "tips", e pode incluir "holidays" e "title".',
        'This week you finished {n}:':
            'Esta semana você concluiu {n}:',
        'This week...':
            'Esta semana...',
        'holidays line {line} is not a date like 2026-12-25.':
            'A linha {line} de holidays não é uma data como 2026-12-25.',
        '{list} line {line} has a date.':
            'A linha {line} de {list} tem uma data.',
        '{list} line {line} has a link or an address.':
            'A linha {line} de {list} tem um link ou um endereço.',
        '{list} line {line} has control characters or extra spaces.':
            'A linha {line} de {list} tem caracteres de controle ou espaços a mais.',
        '{list} line {line} is not text.':
            'A linha {line} de {list} não é texto.',
        '{list} line {line} must be {low} to {high} characters long.':
            'A linha {line} de {list} deve ter de {low} a {high} caracteres.',
    },
}

# ---- French ----

LANGUAGES["fr"] = {
    "days": ('lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'),
    "months": ('janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'),
    "date": '{day} {d} {month} {year}',
    "first": '1er',
    "thoughts": (
        'Ouvrez le document que vous évitez depuis un moment et lisez seulement le premier paragraphe.',
        "Dix minutes de travail, c'est déjà un début, et les dix suivantes en deviennent souvent plus faciles.",
        "Pas besoin d'avoir tout le plan aujourd'hui : une première étape raisonnable suffit.",
        'Écrivez une première phrase maladroite. Elle vous donne quelque chose de concret à améliorer ensuite.',
        'Dégagez un petit coin de votre bureau et remarquez à quel point le reste paraît plus calme.',
        'Choisissez la plus petite tâche de votre liste et terminez-la avant de regarder les autres.',
        "Un début maladroit par un matin calme vaut mieux qu'attendre un moment parfait qui ne viendra peut-être pas.",
        "Inscrivez la première étape dans votre agenda pour qu'elle ait sa place.",
        "Les grands projets se construisent surtout un après-midi après l'autre. Visez-en un seul.",
        'Dites à voix haute la toute prochaine action, et laissez le reste de la liste attendre son tour.',
        'Certains jours, votre rythme est plus lent que vous ne le voudriez, et ce rythme compte quand même.',
        "Parlez-vous comme vous parleriez à une personne arrivée dans l'équipe cette semaine.",
        "Vous avez le droit d'apprendre encore quelque chose que vous faites depuis des années.",
        "Une matinée sans entrain ne décide pas de l'après-midi. Vous pouvez recommencer après la pause de midi.",
        'La fatigue est une information, pas un échec. Ajustez le plan et continuez en douceur.',
        'Accordez-vous la même indulgence que vous offrez si volontiers aux autres.',
        'Souvent, le progrès ne se voit pas pendant un moment, puis soudain une page est terminée.',
        "Il n'y a aucun mal à devoir relire une chose pour la comprendre.",
        "Pas besoin d'attendre de vous sentir à la hauteur. Le faire avec le trac, c'est quand même le faire.",
        "Ce que vous pouvez donner aujourd'hui sera peut-être plus modeste qu'hier, et ce n'est pas grave.",
        'Fermez les onglets dont vous ne vous servez pas. Votre attention vous en remerciera en quelques minutes.',
        "Une tâche, une fenêtre, vingt-cinq minutes. Voyez jusqu'où peut mener un moment de calme.",
        "Notez l'idée parasite qui surgit, puis revenez à ce que vous faisiez.",
        'Si vous le pouvez, coupez le son de votre téléphone pendant une heure et donnez au travail toute votre attention.',
        "Choisissez la chose qui ferait d'aujourd'hui une bonne journée, et réservez-lui du temps.",
        "Faire les choses une par une est souvent plus rapide qu'il n'y paraît.",
        "Une liste claire de trois choses vaut mieux qu'une liste éparpillée de vingt.",
        "Remarquez quand votre esprit s'égare, et ramenez-le sans vous faire de reproches.",
        "Placez la tâche la plus difficile au moment où vous avez le plus d'énergie, même si ce n'est pas le matin.",
        'Casque sur les oreilles, boisson à portée de main, porte fermée. Préparez le cadre et la concentration suivra.',
        "Éloignez-vous de l'écran cinq minutes. Vous reviendrez l'esprit un peu plus clair.",
        "Aujourd'hui, prenez votre repas de midi loin de votre bureau. La messagerie peut attendre.",
        "Un petit tour autour du bâtiment, c'est aussi du vrai travail pour votre tête.",
        "Une minute loin de l'écran est un bon usage d'un après-midi chargé.",
        "Étirez vos épaules et desserrez la mâchoire. La tension s'y loge peut-être depuis des heures.",
        "Si vous le pouvez, partez à l'heure ce soir. Demain, vous apprécierez d'avoir eu votre soirée.",
        'Le repos fait partie du travail, car la fatigue pousse à commettre deux fois la même erreur.',
        'Reposez vos yeux un instant et laissez retomber vos épaules.',
        "Une vraie pause donne à la seconde moitié de la journée l'allure d'un nouveau départ.",
        "Laissez la soirée vous appartenir. Rien dans votre messagerie n'a besoin de vous à vingt et une heures.",
        "Remerciez aujourd'hui quelqu'un pour une petite chose faite sans qu'on le lui demande.",
        'La plupart des gens font de leur mieux, avec plus de choses à gérer que vous ne le voyez.',
        "Retenez comment une personne de l'équipe prend son thé ou son café. S'en souvenir est un petit cadeau.",
        "Si quelqu'un vous répond sèchement, pensez à une journée difficile plutôt qu'à un jugement sur vous.",
        "Tenez la porte, partagez les biscuits et laissez l'autre finir sa phrase.",
        'Un bonjour rapide et une question sur le week-end peuvent être le meilleur moment de la matinée.',
        "Quand une nouvelle personne pose une question évidente, rappelez-vous que vous l'avez posée vous aussi.",
        "Dites-le ouvertement quand l'idée d'une personne de l'équipe a amélioré votre travail.",
        'Répondez à un message avec un peu de chaleur. Cela ne coûte rien et fait du bien.',
        'Allez voir une personne qui parle peu en réunion ces temps-ci, et demandez-lui comment elle va.',
        'Terminez ce qui est presque fini avant de commencer autre chose.',
        'Terminé et assez bien est souvent plus utile que parfait et inachevé.',
        "Réglez aujourd'hui une affaire en suspens et remarquez le petit soulagement qui suit.",
        "Les dix derniers pour cent ne demandent souvent que quelques minutes d'attention. Accordez-les aujourd'hui.",
        'Envoyez le courriel qui attend dans vos brouillons. Il est sans doute très bien comme il est.',
        'Cochez la tâche comme terminée, respirez, et réjouissez-vous que ce soit fait.',
        "Une petite chose terminée vaut plus qu'une grande à moitié faite.",
        'Avant de vous déconnecter, notez la première étape de demain pour ne pas avoir à vous en souvenir.',
        'Relisez votre texte une fois, corrigez ce que vous trouvez, puis envoyez-le.',
        'Finir la journée sur un résultat net rend la soirée plus légère.',
        'Poser une question tôt évite souvent une heure de blocage en silence plus tard.',
        "La plupart des gens aiment partager ce qu'ils savent. Demandez sans vous excuser.",
        "« Je n'arrive pas à avancer » est une phrase claire et utile, avec laquelle l'équipe peut vous aider.",
        'Demandez ce dont vous avez besoin avec des mots simples, et laissez aux autres la possibilité de dire oui.',
        "Deux personnes face à un problème le résolvent souvent plus vite qu'une seule qui le fixe en silence.",
        "Avoir besoin d'un coup de main ne fait pas de vous un fardeau. Vous faites partie de l'équipe.",
        'Venez avec une question précise, et la personne interrogée pourra vous donner une réponse précise.',
        'Si les consignes ne sont pas claires, demander des précisions fait partie du travail bien fait.',
        "Proposez votre aide quand vous le pouvez et acceptez-la quand il le faut. Les deux s'apprennent.",
        "Quelqu'un près de vous a sans doute déjà résolu ce problème. Allez trouver cette personne.",
        'Notez ce que vous avez appris à résoudre cette semaine. Cela fait plus que vous ne le pensez.',
        "Être débutant dans un domaine nouveau, c'est le signe que votre travail continue de grandir.",
        'Observez comment une personne que vous admirez gère un appel délicat, et retenez-en une chose.',
        'Lisez une page utile pendant votre pause, et votre esprit aura fait une bonne journée.',
        "Expliquer une tâche à quelqu'un d'autre est une façon étonnamment efficace de l'apprendre soi-même.",
        'Vous pouvez dire « je ne le sais pas encore », puis aller le découvrir.',
        "Tout système inconnu paraît déroutant jusqu'à ce qu'on l'ait utilisé quelques fois.",
        'Demandez à une personne plus expérimentée comment elle a appris. La réponse est souvent rassurante.',
        'Les compétences viennent de la répétition. Répétez la petite chose et laissez-la devenir facile.',
        'Un peu de curiosité peut rendre plus intéressante une tâche ordinaire.',
        "Une erreur repérée tôt n'est qu'une correction, et la plupart sont repérées tôt.",
        "Corrigez-la, prévenez les personnes concernées, puis laissez la contrariété s'estomper.",
        'Presque toute erreur au travail paraît plus petite une semaine plus tard que sur le moment.',
        "Un faux pas n'efface pas les années de travail soigné derrière vous.",
        "Quand quelque chose tourne mal, regardez d'abord le processus, et la personne ensuite.",
        'Tout le monde autour de vous a déjà envoyé un courriel à la mauvaise personne au moins une fois.',
        "Gardez la leçon qu'offre une erreur et laissez le reste derrière vous.",
        "Reconnaître simplement une erreur inspire souvent plus confiance que de n'en avoir jamais commis.",
        'Les personnes soigneuses ont aussi des journées maladroites, et ces journées sont oubliées le soir venu.',
        "Le mois prochain, vous aurez oublié la plupart des petits faux pas d'aujourd'hui.",
        'Une journée calme, sans urgence, est une bonne journée, même si personne ne le dit.',
        'Remarquez les petits plaisirs : une tasse chaude, une boîte de réception vide, une minute de calme.',
        "Toutes les journées n'ont pas besoin d'une grande réussite. Avancer calmement et agréablement, c'est bien.",
        'Profitez de la réunion qui finit cinq minutes plus tôt, et utilisez ce temps comme vous le voulez.',
        'Une journée ordinaire bien faite mérite une fierté tranquille.',
        "Le bon travail passe souvent inaperçu de l'extérieur, et ce n'est pas grave.",
        "Laissez un après-midi agréable être agréable, sans attendre qu'il soit productif.",
        'Les petites habitudes de la journée, le premier café, les visages familiers, méritent votre attention.',
        "Aujourd'hui, vous étiez là et vous avez fait votre part, et c'est bien assez.",
        "Ce soir, prenez un moment pour repenser à une chose qui s'est bien passée aujourd'hui.",
        "Une minute calme entre deux tâches n'est pas du temps perdu : c'est ainsi que la suivante commence bien.",
    ),
    "tips": (
        "Buvez un verre d'eau lentement, loin de votre écran.",
        "Roulez les épaules vers l'arrière cinq fois, tout doucement.",
        'Reposez vos yeux vingt secondes : regardez au loin ou fermez-les.',
        'Levez les bras au-dessus de la tête, en position assise ou debout, et respirez profondément.',
        "Allez jusqu'à la pièce ou la fenêtre la plus éloignée que vous pouvez atteindre, puis revenez.",
        'Vérifiez votre posture et laissez vos épaules descendre loin de vos oreilles.',
        "Tournez doucement la tête d'un côté à l'autre, seulement tant que c'est confortable.",
        'Ouvrez et fermez les mains dix fois pour délier vos doigts.',
        "Épinglez le document que vous ouvrez le plus pour l'avoir à un clic.",
        'Faites un petit tour dehors, à pied ou en fauteuil roulant, comme il vous convient.',
        'Servez-vous une boisson chaude ou fraîche et savourez-la loin de votre écran.',
        'Portez votre attention sur quelque chose de calme : un paysage, un son ou une texture.',
        "Notez la prochaine étape d'une tâche laissée à moitié faite.",
        'Posez les deux pieds à plat et redressez le dos, en position assise ou debout, pendant dix respirations.',
        'Mettez en sourdine une discussion de groupe que vous ne faites que survoler.',
        'Desserrez la mâchoire et détendez votre front un instant.',
        "Bougez pendant deux minutes, de la manière qui vous fait du bien aujourd'hui.",
        'Réservez quinze minutes dans votre agenda pour la tâche que vous repoussez sans cesse.',
        'Réglez votre chaise, votre écran ou votre clavier pour gagner un peu de confort.',
        "Si vous le pouvez, prenez le chemin le plus long jusqu'à votre prochaine réunion ou votre prochain appel.",
        'Enregistrez un modèle pour un courriel que vous écrivez souvent.',
        'Apprenez un raccourci clavier du programme que vous utilisez le plus.',
        "Buvez un grand verre d'eau avant votre prochain café ou thé.",
        "Haussez les épaules jusqu'aux oreilles, puis laissez-les redescendre doucement.",
        "Sortez ou ouvrez une fenêtre pour prendre une minute d'air frais.",
        'Respirez lentement cinq fois, en allongeant un peu chaque expiration.',
        "Faites une minute de pause tranquille avant d'ouvrir votre prochain message.",
        "Notez une bonne chose qui s'est passée aujourd'hui.",
        'Fermez les yeux le temps de trois respirations et observez comment vous vous sentez.',
        "Nommez trois choses que vous percevez en ce moment, avec n'importe quel sens.",
        'Notez une chose que vous attendez avec plaisir cette semaine.',
        'Réglez une minuterie sur deux minutes et restez simplement sans écran.',
        'Appréciez une petite chose près de vous, comme une plante ou votre tasse préférée.',
        'Pensez à une chose que vous avez bien faite cette semaine et reconnaissez-la.',
        "Écoutez une de vos chansons préférées du début à la fin, sans rien d'autre d'ouvert.",
        "Inspirez en comptant jusqu'à quatre et expirez jusqu'à six, trois fois.",
        'Prenez une respiration avant de réagir au prochain petit agacement.',
        'Notez une chose qui vous a fait rire récemment.',
        "Pendant une minute, remarquez quelque chose d'agréable : un son, une odeur ou ce que vous touchez.",
        'Pensez à un lieu que vous aimez et imaginez-le pendant trente secondes.',
        "Décidez qu'une petite tâche est « assez bien pour l'instant » et passez à la suite.",
        'Écrivez une phrase sur une chose pour laquelle vous éprouvez de la gratitude.',
        'Savourez la prochaine gorgée de votre boisson et remarquez son goût.',
        'Faites une courte pause entre deux tâches avant de commencer la suivante.',
        "Cherchez aujourd'hui une chose qui se passe mieux que prévu.",
        "Choisissez un mot pour décrire l'après-midi que vous souhaitez.",
        'Laissez votre esprit se reposer soixante secondes, puis revenez à votre prochaine tâche.',
        'Sentez vos pieds sur le sol et ressentez votre stabilité un moment.',
        "Souvenez-vous d'un geste gentil que quelqu'un a eu pour vous et savourez ce souvenir.",
        'Notez une idée à revoir plus tard, et laissez-la mûrir.',
        'Rangez un petit coin de votre bureau, un seul.',
        'Répondez à un message qui attend depuis un moment.',
        'Notez la tâche principale de demain sur un pense-bête ou dans vos notes.',
        "Fermez les onglets du navigateur dont vous n'avez plus besoin.",
        "Remerciez une personne de l'équipe pour quelque chose qu'elle a fait récemment.",
        "Archivez cinq anciens courriels dont vous n'avez plus besoin.",
        'Renommez un fichier mal nommé pour le retrouver facilement plus tard.',
        'Retirez un ou deux fichiers qui traînent sur votre bureau Windows.',
        'Supprimez un ancien rappel qui ne sert plus.',
        'Donnez un titre clair à un document que vous ouvrez souvent.',
        'Rayez une petite tâche de votre liste de choses à faire.',
        "Désabonnez-vous d'une lettre d'information que vous ne lisez jamais.",
        'Essuyez votre clavier ou votre écran avec un chiffon doux.',
        "Placez un stylo, un carnet et de l'eau à portée de main.",
        "Laissez-vous une courte note pour demain qui indique où en est votre travail aujourd'hui.",
        'Choisissez la tâche la plus importante de cet après-midi et faites-la en premier.',
        'Videz la corbeille ou le bac de recyclage de votre bureau.',
        "Mettez à jour une note d'avancement pour que les autres voient où en sont les choses.",
        'Rangez votre dossier Téléchargements en déplaçant quelques fichiers.',
        'Programmez un rappel pour une chose que vous avez tendance à oublier.',
        "Désactivez une notification dont vous n'avez pas vraiment besoin.",
        'Ajoutez aux favoris une page que vous cherchez sans arrêt.',
        "Rédigez un résumé de deux lignes d'une réunion pendant qu'elle est encore fraîche.",
        'Demandez si une réunion récurrente pourrait être un peu plus courte.',
        "Fixez-vous un seul objectif pour l'heure qui vient et notez-le.",
        "Demandez à une personne de l'équipe comment se passe sa journée, et écoutez vraiment.",
        "Partagez un lien utile avec quelqu'un qu'il pourrait intéresser.",
        "Dites bonjour à quelqu'un à qui vous n'avez encore jamais parlé.",
        'Envoyez un petit mot de remerciement à une personne qui vous a donné un coup de main récemment.',
        'Saluez chaleureusement les autres au début de votre prochain appel.',
        "Demandez à une personne de l'équipe ce qu'elle attend avec plaisir cette semaine.",
        "Félicitez quelqu'un pour une petite réussite que vous avez remarquée.",
        "Proposez à une personne de l'équipe une courte pause thé ou café, sur place ou par appel.",
        "Complimentez une personne de l'équipe sur une chose précise qu'elle a bien faite.",
        "Apprenez le nom d'une personne que vous croisez souvent sans la connaître encore.",
        "Partagez une astuce utile avec une personne de l'équipe qui pourrait en avoir besoin.",
        "Demandez à quelqu'un de vous recommander une chanson, une série ou un livre.",
        "Prenez des nouvelles d'une personne de l'équipe qui parle peu ces temps-ci.",
        "Si quelqu'un a beaucoup de travail, proposez de l'aider pour une petite chose.",
        'Saluez chaleureusement la prochaine personne que vous croisez.',
        "Transmettez à une personne de l'équipe un compliment entendu à son sujet.",
        "Demandez à une personne de l'équipe ce qui lui a facilité la semaine.",
        "Envoyez un message amical à quelqu'un avec qui vous avez travaillé autrefois.",
        'Remerciez les personnes qui veillent au bon fonctionnement des espaces partagés.',
        "Présentez l'une à l'autre deux personnes du travail qui pourraient bien s'entendre.",
        "Demandez à une personne de l'équipe comment vous pourriez lui faciliter la passation d'une tâche.",
        "Partagez une petite plaisanterie inoffensive avec quelqu'un près de vous.",
        "Mettez un peu plus de chaleur dans votre prochain « s'il vous plaît » et votre prochain « merci ».",
        "Demandez à une personne de l'équipe ce qu'elle aime faire en dehors du travail.",
        'Écoutez pleinement la prochaine personne qui vous parle, sans faire autre chose en même temps.',
    ),
    "done": (
        'Bien. Voilà une chose de terminée.',
        'Très bien. Ça fait du bien de finir quelque chose.',
        'Bien joué. Faites une courte pause avant la suivante.',
        "Bien. Les petites tâches terminées s'additionnent.",
        "C'est fait. Vous pouvez vous en réjouir.",
        'Bien. Une chose de moins sur votre liste.',
    ),
    "text": {
        HELP: """hello-world affiche une salutation, une pensée et une petite chose
à essayer.

À la dernière question, tapez plan pour le plan du jour, fait quand
vous l'avez terminé, ou menu (ou m) pour les options. Entrée ferme le
programme, et q, x et quitter le ferment depuis n'importe quelle
question. À une question de plan, reprendre ramène un plan antérieur
non terminé. Après fait, vos 3 derniers plans terminés s'affichent.
L'option 1 du menu les affiche tous, l'option 7 en oublie un et
l'option 8 masque la pensée et l'astuce.
Au menu, Entrée permet de revenir. Vous pouvez aussi lancer hello.cmd
avec l'une de ces options :
  --plain         Affiche seulement la salutation, en anglais
  --stats         Montre ce qui est enregistré sur cet ordinateur
  --reset         Supprime tout ce qui est enregistré (demande avant)
  --remind on     S'ouvre chaque jour à la connexion (off : arrête)
  --streak off    Masque le message des jours d'affilée (on : affiche)
  --version       Affiche la version
  --check-content FICHIER
                  Vérifie un fichier de contenu de l'organisation
  --help          Affiche ce texte

Codes de sortie : 0 en cas de réussite, 1 si une commande a échoué ou
si l'écran n'a pas pu être écrit, 2 pour une option inconnue.

Les notes enregistrées restent sur cet ordinateur, dans votre dossier
utilisateur. Rien n'est envoyé nulle part. Le personnel informatique
qui peut lire les fichiers de cet ordinateur pourrait les lire.""",
        MENU_HELP: """Mots à taper à la dernière question :
  fait  marque le plan du jour comme terminé, puis demande le suivant
  plan  définit ou modifie le plan du jour
  menu  ouvre ces options
  q     ferme la fenêtre, tout comme Entrée
À une question de plan, reprendre ramène le plan antérieur non terminé.
À la question « L'avez-vous fait ? », n veut dire pas encore, et
vous pouvez garder le plan pour aujourd'hui. q ferme depuis n'importe
quelle question.
Dans ce menu, 1 montre ce qui est enregistré, 7 oublie un plan terminé
et 8 masque la pensée et l'astuce.
Tapez m pour revoir les options. Rien n'est envoyé nulle part.""",
        SAVED_PLAN: "Enregistré. Tapez fait quand vous l'aurez terminé, sinon la question vous sera posée à la prochaine ouverture.",
        GREETING: 'Bonjour, le monde !',
        'hello.cmd is in this folder:':
            'hello.cmd se trouve dans ce dossier :',
        'Shortened to {n} characters.':
            'Texte raccourci à {n} caractères.',
        'Your saved file was damaged, so hello-world set it aside as a backup copy and started fresh. Your earlier days and plan could not be read. Menu option 4 deletes the backup.':
            "Votre fichier enregistré était endommagé : hello-world l'a mis de côté comme copie de sauvegarde et a recommencé à zéro. Vos jours et votre plan précédents n'ont pas pu être lus. L'option 4 du menu supprime la sauvegarde.",
        'Backup copy: ':
            'Copie de sauvegarde : ',
        'In the folder: ':
            'Dans le dossier : ',
        'Sorry, "{shown}" is not one of the choices.':
            'Pardon, « {shown} » ne fait pas partie des choix.',
        'A plan needs a word or two, so nothing was saved.':
            "Un plan a besoin d'un mot ou deux, donc rien n'a été enregistré.",
        'The sign-in reminder works on Windows only.':
            'Le rappel à la connexion fonctionne uniquement sous Windows.',
        'Your organization has turned off opening at sign-in.':
            "Votre organisation a désactivé l'ouverture à la connexion.",
        'The reminder cannot be set up from this folder.':
            'Le rappel ne peut pas être configuré depuis ce dossier.',
        'Could not set up the reminder.':
            'Impossible de configurer le rappel.',
        'Done. hello-world will open once a day when you sign in.':
            "C'est fait. hello-world s'ouvrira une fois par jour à votre connexion.",
        'To stop it, choose option 2 in the menu.':
            "Pour l'arrêter, choisissez l'option 2 du menu.",
        'Could not turn off the sign-in reminder.':
            'Impossible de désactiver le rappel à la connexion.',
        'Done. The sign-in reminder is off.':
            "C'est fait. Le rappel à la connexion est désactivé.",
        'Saved on this computer in:':
            'Enregistré sur cet ordinateur dans :',
        'Saved in your own user folder on this computer.':
            'Enregistré dans votre propre dossier utilisateur sur cet ordinateur.',
        'Days you opened it in the last {days} days: {n} (last 7 days: {recent})':
            "Jours d'ouverture sur les {days} derniers jours : {n} (7 derniers jours : {recent})",
        'Times you marked a plan done: {n}':
            'Plans marqués comme faits : {n}',
        'Your current plan: ':
            'Votre plan actuel : ',
        'Earlier plan (for same): ':
            'Plan antérieur (pour reprendre) : ',
        'Days-in-a-row message: shown.':
            "Message des jours d'affilée : affiché.",
        'Days-in-a-row message: hidden.':
            "Message des jours d'affilée : masqué.",
        'Opens by itself at sign-in: turned off by your organization.':
            'Ouverture à la connexion : désactivée par votre organisation.',
        'Opens by itself at sign-in: on.':
            'Ouverture à la connexion : activée.',
        'Opens by itself at sign-in: off.':
            'Ouverture à la connexion : désactivée.',
        "It never leaves this computer. Others who can read this computer's files, such as IT staff, could read it.":
            'Ces données ne quittent jamais cet ordinateur. Les personnes qui peuvent lire les fichiers de cet ordinateur, comme le personnel informatique, pourraient les lire.',
        'After tidying, the file holds only this:':
            'Après nettoyage, le fichier contient seulement ceci :',
        'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
            'Supprimer toutes les notes, dates et plans enregistrés sur cet ordinateur ? (o ou n, Entrée pour annuler) > ',
        'Nothing was deleted.':
            "Rien n'a été supprimé.",
        'Could not delete everything.':
            'Impossible de tout supprimer.',
        'Delete these yourself:':
            'Supprimez vous-même ces fichiers :',
        'Could not list the folder, so backup copies may remain:':
            'Impossible de lister le dossier. Des sauvegardes peuvent subsister :',
        'Done. Everything saved was deleted.':
            "C'est fait. Tout ce qui était enregistré a été supprimé.",
        'Another open hello-world window cannot put it back.':
            'Une autre fenêtre hello-world ouverte ne peut pas le rétablir.',
        'Close any other open hello-world window, or it may save its notes again.':
            'Fermez toute autre fenêtre hello-world ouverte, sinon elle pourrait enregistrer de nouveau ses notes.',
        'Everything saved was deleted in another window, so this was not saved.':
            "Tout ce qui était enregistré a été supprimé dans une autre fenêtre, donc ceci n'a pas été enregistré.",
        'The other open window had also finished a plan.':
            "L'autre fenêtre ouverte avait aussi terminé un plan.",
        'The other open window changed the plan, so its plan is kept.':
            "L'autre fenêtre a modifié le plan, c'est donc le sien qui est conservé.",
        'Type plan at the last prompt to set one.':
            'Tapez plan à la dernière question pour en définir un.',
        'That looks like a command, not a plan, so nothing was saved.':
            "Cela ressemble à une commande, pas à un plan : rien n'a été enregistré.",
        'Type your plan, or press Enter to go back.':
            'Tapez votre plan, ou appuyez sur Entrée pour revenir.',
        'Finished lately:':
            'Terminés récemment :',
        'Your plan today: ':
            'Votre plan du jour : ',
        'Your plan from {date}: ':
            'Votre plan du {date} : ',
        'Earlier plan: ':
            'Plan antérieur : ',
        'Type the next plan, or Enter to close > ':
            'Tapez le plan suivant, ou Entrée pour fermer > ',
        'Type the next plan, same to reuse the earlier plan, or Enter to close > ':
            'Tapez le plan suivant, reprendre pour réutiliser le plan antérieur, ou Entrée pour fermer > ',
        "Type today's plan, or Enter to keep it > ":
            'Tapez le plan du jour, ou Entrée pour le garder > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
            'Tapez le plan du jour, reprendre pour réutiliser le plan antérieur, ou Entrée pour le garder > ',
        "Type today's plan, or Enter to go back > ":
            'Tapez le plan du jour, ou Entrée pour revenir > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
            'Tapez le plan du jour, reprendre pour réutiliser le plan antérieur, ou Entrée pour revenir > ',
        'Closing.':
            'Fermeture.',
        'There is no earlier plan to reuse yet. Nothing changed.':
            "Pas encore de plan antérieur à reprendre. Rien n'a changé.",
        'Nothing changed.':
            "Rien n'a changé.",
        'Could not save that on this computer. Your plan is unchanged.':
            "Impossible d'enregistrer sur cet ordinateur. Votre plan n'a pas changé.",
        'No finished plans are saved.':
            "Aucun plan terminé n'est enregistré.",
        'Type the number to forget (1 to {n}), or Enter to keep them all > ':
            'Tapez le numéro à oublier (1 à {n}), ou Entrée pour tout garder > ',
        'There is no number "{typed}" on the list. Type a number from 1 to {n}, or press Enter to keep them all.':
            "Le numéro « {typed} » n'est pas dans la liste. Tapez un numéro de 1 à {n}, ou appuyez sur Entrée pour tout garder.",
        'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
            "L'oublier aussi comme plan à reprendre ? (o ou n, Entrée pour le garder) > ",
        'Type y or n, or press Enter to keep it for same.':
            'Tapez o ou n, ou appuyez sur Entrée pour le garder.',
        'That plan was already forgotten. Nothing changed.':
            "Ce plan était déjà oublié. Rien n'a changé.",
        'Forgotten: ':
            'Oublié : ',
        'Same still has it.':
            'Il reste disponible avec reprendre.',
        'Could not save that on this computer. Nothing changed.':
            "Impossible d'enregistrer sur cet ordinateur. Rien n'a changé.",
        'Options':
            'Options',
        'Show what is saved on this computer':
            'Montrer ce qui est enregistré sur cet ordinateur',
        'Open once a day at sign-in (turned off by your organization)':
            'Ouverture à la connexion (désactivée par votre organisation)',
        'Turn off: open once a day at sign-in (now on)':
            "Désactiver l'ouverture quotidienne à la connexion (activée)",
        'Turn on: open once a day at sign-in (now off)':
            "Activer l'ouverture quotidienne à la connexion (désactivée)",
        'Days-in-a-row message (hidden by your organization)':
            "Message des jours d'affilée (masqué par votre organisation)",
        'Hide the days-in-a-row message (now shown)':
            "Masquer le message des jours d'affilée (affiché)",
        'Show the days-in-a-row message (now hidden)':
            "Afficher le message des jours d'affilée (masqué)",
        'Delete everything saved':
            'Supprimer tout ce qui est enregistré',
        'Help':
            'Aide',
        "Set today's plan (turned off by your organization)":
            'Définir le plan du jour (désactivé par votre organisation)',
        'Forget a finished plan (turned off by your organization)':
            'Oublier un plan terminé (désactivé par votre organisation)',
        "Set or change today's plan":
            'Définir ou modifier le plan du jour',
        'Forget one finished plan':
            'Oublier un plan terminé',
        'Thought and tip (hidden by your organization)':
            'Pensée et astuce (masquées par votre organisation)',
        'Hide the thought and tip (now shown)':
            "Masquer la pensée et l'astuce (affichées)",
        'Show the thought and tip (now hidden)':
            "Afficher la pensée et l'astuce (masquées)",
        '{date}: ':
            '{date} : ',
        'Enter':
            'Entrée',
        'Back to the last prompt':
            'Revenir à la dernière question',
        'Choose 1 to 11, or Enter to go back > ':
            'Choisissez de 1 à 11, ou Entrée pour revenir > ',
        'Choose 1 to 11, m to list the options, or Enter to go back > ':
            'Choisissez de 1 à 11, m pour afficher les options, ou Entrée pour revenir > ',
        'The saved file could not be read just now, so this may be out of date.':
            "Le fichier enregistré n'a pas pu être lu pour l'instant, ces informations ne sont donc peut-être pas à jour.",
        'Type full to see the whole file, or Enter to go on > ':
            'Tapez tout pour voir le fichier entier, ou Entrée pour continuer > ',
        'Could not save that choice on this computer.':
            "Impossible d'enregistrer ce choix sur cet ordinateur.",
        'Your organization has hidden the days-in-a-row message.':
            "Votre organisation a masqué le message des jours d'affilée.",
        'Done. The days-in-a-row message is on.':
            "C'est fait. Le message des jours d'affilée est activé.",
        'Done. The days-in-a-row message is off.':
            "C'est fait. Le message des jours d'affilée est désactivé.",
        'Plans are turned off by your organization.':
            'Les plans sont désactivés par votre organisation.',
        'Your organization has hidden the thought and tip.':
            "Votre organisation a masqué la pensée et l'astuce.",
        'Done. The thought and tip are on.':
            "C'est fait. La pensée et l'astuce sont activées.",
        'Done. The thought and tip are off.':
            "C'est fait. La pensée et l'astuce sont désactivées.",
        'Type 1 to 11, or press Enter to go back.':
            'Tapez un chiffre de 1 à 11, ou appuyez sur Entrée pour revenir.',
        'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
            "Voulez-vous que hello-world s'ouvre une fois par jour à votre connexion ? (o ou n, Entrée pour plus tard) > ",
        'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
            "Voulez-vous que hello-world s'ouvre une fois par jour à votre connexion pour vous demander où en est votre plan ? (o ou n, Entrée pour plus tard) > ",
        'Type y or n, or press Enter for not now.':
            'Tapez o ou n, ou appuyez sur Entrée pour plus tard.',
        'That was not understood. It will ask again on a later visit.':
            "Réponse non comprise. La question reviendra lors d'une prochaine visite.",
        'It will ask again on a later visit. Menu option 2 also turns it on.':
            "La question reviendra lors d'une prochaine visite. L'option 2 du menu l'active aussi.",
        'No problem. Menu option 2 turns it on later.':
            "Pas de problème. L'option 2 du menu permet de l'activer plus tard.",
        "Okay. It won't ask again. Menu option 2 turns it on.":
            "D'accord. La question ne sera plus posée. L'option 2 du menu l'active.",
        'Okay. It will ask again on a later visit. Type n to stop it.':
            "D'accord. La question reviendra lors d'une prochaine visite. Tapez n pour qu'elle ne revienne plus.",
        'When did you finish it?':
            "Quand l'avez-vous terminé ?",
        'Today':
            "Aujourd'hui",
        'Type a number from 1 to {n}, or Enter for 1 > ':
            'Tapez un numéro de 1 à {n}, ou Entrée pour 1 > ',
        'Type a number from 1 to {n}, or press Enter.':
            'Tapez un numéro de 1 à {n}, ou appuyez sur Entrée.',
        'That looks like more than one thing. Finishing the first part still counts.':
            'Cela ressemble à plusieurs tâches. Terminer la première compte déjà.',
        'There is no plan to mark as done. Type plan to set one.':
            "Il n'y a aucun plan à marquer comme fait. Tapez plan pour en définir un.",
        'Could not save that on this computer. The plan is still open.':
            "Impossible d'enregistrer sur cet ordinateur. Le plan reste en cours.",
        'Your plan from over two weeks ago was put away. Type same at the plan prompt to bring it back.':
            "Votre plan d'il y a plus de deux semaines a été mis de côté. Tapez reprendre à une question de plan pour le récupérer.",
        "Press Enter at each question to skip it, and once more to close. That's it.":
            "Appuyez sur Entrée à chaque question pour la passer, puis une fois de plus pour fermer. C'est tout.",
        'Welcome.':
            'Bienvenue.',
        'Each day you get one thought and one small thing to try, the same for everyone.':
            'Chaque jour, vous recevez une pensée et une petite chose à essayer, les mêmes pour tout le monde.',
        'If you type a plan, it asks next time how it went. Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks.':
            "Si vous tapez un plan, la prochaine fois on vous demandera comment ça s'est passé. Vos notes restent sur cet ordinateur et ne sont jamais envoyées nulle part. Comme tout fichier de travail, elles ne sont pas secrètes : tenez-vous-en aux tâches courantes.",
        'Type menu at the end for the options.':
            'Tapez menu à la fin pour voir les options.',
        'Welcome back. Glad you are here.':
            'Bon retour parmi nous. Ça fait plaisir de vous revoir.',
        'You have opened this {row} days in a row. Nice to see you.':
            "Vous avez ouvert hello-world {row} jours d'affilée. Merci d'être là.",
        'Last time you planned: ':
            'Votre dernier plan : ',
        'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
            "L'avez-vous fait ? (o pour oui, n pour pas encore, Entrée pour passer) > ",
        'Type y or n, or press Enter to skip.':
            'Tapez o ou n, ou appuyez sur Entrée pour passer.',
        'Could not save that on this computer. Your answer was not counted.':
            "Impossible d'enregistrer : votre réponse n'a pas été prise en compte.",
        'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
            "Ce n'est pas grave. Le garder pour aujourd'hui ? (o ou n, Entrée pour le garder) > ",
        'Type y to keep it, n to clear it, or press Enter to keep it.':
            "Tapez o pour le garder, n pour l'effacer, ou appuyez sur Entrée pour le garder.",
        'Cleared. Type same at a plan prompt if you want it back.':
            'Effacé. Tapez reprendre à une question de plan pour le récupérer.',
        'Kept for today.':
            "Gardé pour aujourd'hui.",
        'That was not understood. Your plan is left as it was.':
            'Réponse non comprise. Votre plan reste tel quel.',
        'Your plan is still open.':
            'Votre plan est toujours en cours.',
        'Thought for today:':
            'Pensée du jour :',
        'Try this today:':
            "À essayer aujourd'hui :",
        'Your plan for today: ':
            "Votre plan pour aujourd'hui : ",
        'Still open since {date}:':
            'En cours depuis le {date} :',
        '(Enter to skip)':
            '(Entrée pour passer)',
        '(A plan typed here replaces the old one. Enter to skip)':
            "(Un plan tapé ici remplace l'ancien. Entrée pour passer)",
        '(Type same to reuse it, or Enter to skip)':
            '(Tapez reprendre pour le réutiliser, ou Entrée pour passer)',
        'What is one thing you want to get done today?':
            "Quelle tâche voulez-vous accomplir aujourd'hui ?",
        'There is no earlier plan to reuse yet. Nothing was saved.':
            "Pas encore de plan antérieur à reprendre. Rien n'a été enregistré.",
        'Your notes could not be saved on this computer. This screen still works.':
            "Vos notes n'ont pas pu être enregistrées sur cet ordinateur. Cet écran fonctionne quand même.",
        'Type menu, or Enter to close > ':
            'Tapez menu, ou Entrée pour fermer > ',
        'Type done, plan or menu, or Enter to close > ':
            'Tapez fait, plan ou menu, ou Entrée pour fermer > ',
        'Type plan or menu, or Enter to close > ':
            'Tapez plan ou menu, ou Entrée pour fermer > ',
        'Type done, plan or menu, or press Enter to close.':
            'Tapez fait, plan ou menu, ou appuyez sur Entrée pour fermer.',
        'Type plan or menu, or press Enter to close.':
            'Tapez plan ou menu, ou appuyez sur Entrée pour fermer.',
        "The saved file can't be read right now, or it is damaged.":
            "Le fichier enregistré est illisible pour l'instant, ou endommagé.",
        'Nothing was changed. Saved in: ':
            "Rien n'a été modifié. Enregistré dans : ",
        'Deleting saved notes needs a person at the keyboard.':
            'La suppression des notes demande une personne au clavier.',
        '{option} needs on or off. Here are the options.':
            '{option} doit être suivi de on ou off. Voici les options.',
        'Unknown option: {option}. Here are the options.':
            'Option inconnue : {option}. Voici les options.',
        '&Done':
            '&Fait',
        '&Not yet':
            '&Pas encore',
        'S&kip':
            'P&asser',
        '&Save':
            '&Enregistrer',
        '&I did it':
            "&C'est fait",
        '&Options':
            '&Options',
        'Close':
            'Fermer',
        'Not today':
            "Pas aujourd'hui",
        'Did you do it?':
            "L'avez-vous fait ?",
        'Done. A reminder comes when you sign in, if there is a plan to ask about.':
            "C'est fait. Un rappel s'affiche à la connexion s'il y a un plan à suivre.",
        'Done. The Start menu opens a window with buttons.':
            "C'est fait. Le menu Démarrer ouvre une fenêtre avec des boutons.",
        'Done. The Start menu opens this text screen.':
            "C'est fait. Le menu Démarrer ouvre cet écran texte.",
        'More options':
            "Plus d'options",
        'Remind me when I sign in':
            'Me le rappeler à la connexion',
        'Show the thought and tip':
            "Afficher la pensée et l'astuce",
        'Type your plan in the box.':
            'Tapez votre plan dans la zone.',
        'Use a window with buttons (now this text screen)':
            'Utiliser une fenêtre avec des boutons (écran texte)',
        'Use the text screen':
            "Utiliser l'écran texte",
        'Use this text screen (now a window with buttons)':
            'Utiliser cet écran texte (fenêtre avec boutons)',
        'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
            "Voulez-vous un rappel à la connexion ? Il affiche votre plan de la dernière fois, et vous répondez d'un clic. Vous pouvez le désactiver dans Options.",
        'Window or text screen (set by your organization)':
            'Fenêtre ou écran texte (défini par votre organisation)',
        'Your organization has set hello-world to open as a text screen.':
            'Votre organisation a configuré hello-world en écran texte.',
        'Saved.':
            'Enregistré.',
        'Save your plan before closing?':
            'Enregistrer votre plan avant de fermer ?',
        'Delete all saved notes, dates and plans on this computer?':
            'Supprimer toutes les notes, dates et plans enregistrés sur cet ordinateur ?',
        'Turn off: reminder when you sign in (now on)':
            'Désactiver le rappel à la connexion (activé)',
        'Turn on: reminder when you sign in (now off)':
            'Activer le rappel à la connexion (désactivé)',
        'Reminder when you sign in (turned off by your organization)':
            'Rappel à la connexion (désactivé par votre organisation)',
        'Reminder when you sign in: on.':
            'Rappel à la connexion : activé.',
        'Reminder when you sign in: off.':
            'Rappel à la connexion : désactivé.',
        'Reminder when you sign in: turned off by your organization.':
            'Rappel à la connexion : désactivé par votre organisation.',
        'Show the days-in-a-row message':
            "Afficher le message des jours d'affilée",
        'Done. The thought and tip show next time you open hello-world.':
            "C'est fait. La pensée et l'astuce s'afficheront à la prochaine ouverture de hello-world.",
        "Clear today's plan?":
            "Effacer le plan d'aujourd'hui ?",
        'Next plan, if you want one:':
            'Plan suivant, si vous voulez :',
        'A few things? Put ; between them.':
            'Plusieurs choses ? Séparez-les par ;',
        'A plan can be up to {n} characters.':
            "Un plan peut compter jusqu'à {n} caractères.",
        'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
            'Les avez-vous faites ? (o pour toutes, n pour pas encore, les numéros de celles faites, Entrée pour passer) > ',
        'Last time you planned:':
            'Votre dernier plan :',
        'The rest is kept for today.':
            "Le reste est gardé pour aujourd'hui.",
        'Tick the ones you did, then click Done. With none ticked, Done means all of them.':
            'Cochez celles que vous avez faites, puis cliquez sur Fait. Sans case cochée, Fait vaut pour toutes.',
        'Type y for all, n for not yet, or the numbers you did, such as 1 3. Enter skips.':
            'Tapez o pour toutes, n pour pas encore, ou les numéros de celles faites, par exemple 1 3. Entrée pour passer.',
        'Your settings were kept.':
            'Vos réglages ont été conservés.',
        'Language (set by your organization)':
            'Langue (définie par votre organisation)',
        'Language (now {name})':
            'Langue (actuellement {name})',
        'following Windows':
            'selon Windows',
        'Your organization shows hello-world in English.':
            'Votre organisation affiche hello-world en anglais.',
        'Follow Windows':
            'Suivre Windows',
        'Type a number from 1 to {n}, or Enter to keep it > ':
            'Tapez un chiffre de 1 à {n}, ou Entrée pour la garder > ',
        'Done. The new language shows next time you open hello-world.':
            "C'est fait. La nouvelle langue s'affichera à la prochaine ouverture.",
        'Language...':
            'Langue...',
        'Hello, {name}!':
            'Bonjour, {name} !',
        'One thing to get done today? Open hello-world to plan it.':
            "Une chose à faire aujourd'hui ? Ouvrez hello-world pour la planifier.",
        '&Open':
            '&Ouvrir',
        'Reminder settings...':
            'Réglages du rappel...',
        'Greet me by name':
            "M'accueillir par mon prénom",
        'At sign-in':
            'À la connexion',
        'At {at}':
            'À {at}',
        'Also on days with no plan':
            'Aussi les jours sans plan',
        'Open hello-world after I answer':
            'Ouvrir hello-world après ma réponse',
        'Not on weekends':
            'Pas le week-end',
        'Done. A reminder comes at {at} each day, if there is a plan to ask about.':
            "C'est fait. Un rappel s'affiche chaque jour à {at} s'il y a un plan à suivre.",
        'Send feedback...':
            'Envoyer un commentaire...',
        '"holidays" must be a list of at most {n} dates.':
            '"holidays" doit être une liste d\'au plus {n} dates.',
        '"title" must be 1 to 40 characters of plain text, with no link or address.':
            '"title" doit compter de 1 à 40 caractères de texte simple, sans lien ni adresse.',
        '"{list}" must be a list of {low} to {high} lines.':
            '"{list}" doit être une liste de {low} à {high} lignes.',
        "Can't read {path}: {error}":
            'Impossible de lire {path} : {error}',
        'Could not save that on this computer.':
            "Impossible d'enregistrer sur cet ordinateur.",
        'Days you opened hello-world: {n}':
            'Jours où vous avez ouvert hello-world : {n}',
        'Keep a longer history':
            'Garder un historique plus long',
        'Keep my numbers':
            'Garder mes chiffres',
        'Longest run of days: {n}':
            'Plus longue suite de jours : {n}',
        "Mark today's plan done":
            "Marquer le plan d'aujourd'hui comme fait",
        "Mark today's plan done (plans are turned off)":
            "Marquer le plan d'aujourd'hui comme fait (plans désactivés)",
        'My numbers are off. Turn them on under Options, or with --set numbers on.':
            'Vos chiffres sont désactivés. Activez-les sous Options ou avec --set numbers on.',
        'My numbers...':
            'Mes chiffres...',
        'Nothing finished yet this week. That is fine.':
            "Rien de terminé cette semaine pour l'instant. Ce n'est pas grave.",
        'OK: {thoughts} thoughts and {tips} tips.':
            'OK : {thoughts} pensées et {tips} astuces.',
        'Plans finished: {n}':
            'Plans terminés : {n}',
        'Save my plans to a file':
            'Enregistrer mes plans dans un fichier',
        'Saved to {path}':
            'Enregistré dans {path}',
        "The file isn't valid JSON, or is over 200,000 characters.":
            "Le fichier n'est pas du JSON valide ou dépasse 200 000 caractères.",
        'The file must hold an object with two lists, "thoughts" and "tips", and may add "holidays" and "title".':
            'Le fichier doit contenir un objet avec deux listes, "thoughts" et "tips", et peut ajouter "holidays" et "title".',
        'This week you finished {n}:':
            'Cette semaine, vous avez terminé {n} :',
        'This week...':
            'Cette semaine...',
        'holidays line {line} is not a date like 2026-12-25.':
            "La ligne {line} de holidays n'est pas une date comme 2026-12-25.",
        '{list} line {line} has a date.':
            'La ligne {line} de {list} contient une date.',
        '{list} line {line} has a link or an address.':
            'La ligne {line} de {list} contient un lien ou une adresse.',
        '{list} line {line} has control characters or extra spaces.':
            'La ligne {line} de {list} contient des caractères de contrôle ou des espaces en trop.',
        '{list} line {line} is not text.':
            "La ligne {line} de {list} n'est pas du texte.",
        '{list} line {line} must be {low} to {high} characters long.':
            'La ligne {line} de {list} doit compter de {low} à {high} caractères.',
    },
}

# ---- German ----

LANGUAGES["de"] = {
    "days": ('Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'),
    "months": ('Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'),
    "date": '{day}, {d}. {month} {year}',
    "thoughts": (
        'Öffnen Sie das eine Dokument, das Sie vor sich herschieben, und lesen Sie nur den ersten Absatz.',
        'Zehn Minuten Anfang sind auch ein Anfang, und meist fallen die nächsten zehn dann leichter.',
        'Sie brauchen heute nicht den ganzen Plan, nur einen sinnvollen ersten Schritt.',
        'Schreiben Sie den holprigen ersten Satz. Dann haben Sie etwas Echtes, das Sie später verbessern können.',
        'Räumen Sie eine kleine Ecke Ihres Schreibtischs frei und merken Sie, wie viel ruhiger der Rest wirkt.',
        'Wählen Sie die kleinste Aufgabe auf Ihrer Liste und erledigen Sie sie, bevor Sie die anderen ansehen.',
        'Lieber an einem ruhigen Morgen holprig anfangen, als auf den perfekten Moment zu warten, der vielleicht nie kommt.',
        'Tragen Sie den ersten Schritt in Ihren Kalender ein, damit er einen festen Platz hat.',
        'Große Projekte bestehen meist aus vielen kleinen Nachmittagen. Nehmen Sie sich einen davon vor.',
        'Sprechen Sie den nächsten Schritt laut aus und lassen Sie den Rest der Liste warten.',
        'Manche Tage sind langsamer, als Ihnen lieb ist, und auch dieses Tempo zählt.',
        'Sprechen Sie mit sich so, wie Sie mit jemandem sprechen würden, der gerade neu im Team ist.',
        'Sie dürfen auch bei etwas, das Sie seit Jahren tun, noch dazulernen.',
        'Ein zäher Vormittag entscheidet nicht über den Nachmittag. Nach dem Mittagessen können Sie neu anfangen.',
        'Müdigkeit ist eine Information, kein Versagen. Passen Sie den Plan an und machen Sie behutsam weiter.',
        'Gehen Sie mit sich so nachsichtig um, wie Sie es mit anderen ganz selbstverständlich tun.',
        'Fortschritt sieht oft lange nach nichts aus und dann plötzlich nach einer fertigen Seite.',
        'Es ist in Ordnung, etwas zweimal lesen zu müssen, bevor es klar wird.',
        'Sie müssen sich nicht bereit fühlen. Auch wer nervös anfängt, fängt an.',
        'Ihr Bestes kann heute kleiner sein als gestern, und das ist in Ordnung.',
        'Schließen Sie die Tabs, die Sie nicht brauchen. Ihre Konzentration merkt es schon nach wenigen Minuten.',
        'Eine Aufgabe, ein Fenster, fünfundzwanzig Minuten. Sehen Sie, wie weit Sie in einer ruhigen Phase kommen.',
        'Notieren Sie den Gedanken, der dazwischenkommt, und kehren Sie dann zu Ihrer Arbeit zurück.',
        'Schalten Sie Ihr Telefon, wenn möglich, eine Stunde stumm und widmen Sie der Arbeit Ihre volle Aufmerksamkeit.',
        'Überlegen Sie, welche Sache heute zu einem guten Tag machen würde, und halten Sie Zeit dafür frei.',
        'Eins nach dem anderen geht meist schneller, als es sich anfühlt.',
        'Eine übersichtliche Liste mit drei Punkten ist besser als eine unübersichtliche mit zwanzig.',
        'Wenn Ihre Gedanken abschweifen, holen Sie sie ohne Selbstvorwürfe zurück.',
        'Legen Sie die schwierigste Aufgabe dorthin, wo Ihre Energie am größten ist, auch wenn das nicht gleich morgens ist.',
        'Kopfhörer auf, Wasserkocher an, Tür zu. Schaffen Sie den Rahmen, die Konzentration folgt.',
        'Gehen Sie fünf Minuten weg vom Bildschirm. Sie kommen mit etwas klarerem Kopf zurück.',
        'Essen Sie heute nicht am Schreibtisch zu Mittag. Das Postfach kann warten, bis Sie gegessen haben.',
        'Ein kurzer Gang ums Gebäude ist echte Arbeit für den Kopf.',
        'Eine Minute weg vom Bildschirm ist an einem vollen Nachmittag gut investiert.',
        'Lockern Sie die Schultern und entspannen Sie den Kiefer. Vielleicht waren sie stundenlang angespannt.',
        'Gehen Sie heute pünktlich, wenn Sie können. Morgen werden Sie über den freien Abend froh sein.',
        'Pausen gehören zur Arbeit, denn wer müde ist, macht denselben Fehler leicht zweimal.',
        'Lassen Sie Ihre Augen einen Moment ruhen und die Schultern sinken.',
        'Eine richtige Pause lässt die zweite Tageshälfte wie einen Neuanfang wirken.',
        'Der Abend gehört Ihnen. Nichts in Ihrem Postfach braucht Sie um neun Uhr abends.',
        'Danken Sie heute jemandem für eine Kleinigkeit, die ungefragt erledigt wurde.',
        'Die meisten Menschen geben ihr Bestes und haben mehr zu tragen, als Sie sehen.',
        'Merken Sie sich, wie jemand aus dem Team Tee oder Kaffee trinkt. Daran zu denken ist ein kleines Geschenk.',
        'Wirkt jemand kurz angebunden, denken Sie an einen schweren Tag und nicht an ein Urteil über Sie.',
        'Halten Sie die Tür auf, teilen Sie die Kekse und lassen Sie andere ausreden.',
        'Ein kurzes Hallo und eine Frage zum Wochenende können der schönste Teil des Morgens sein.',
        'Wenn jemand Neues etwas Offensichtliches fragt, denken Sie daran, dass Sie es auch einmal gefragt haben.',
        'Sagen Sie es offen, wenn eine Idee aus dem Team Ihre Arbeit verbessert hat.',
        'Antworten Sie auf eine Nachricht mit etwas Wärme. Es kostet nichts und kommt freundlich an.',
        'Sprechen Sie jemanden aus dem Team an, der in Besprechungen zuletzt still war, und fragen Sie, wie es geht.',
        'Erledigen Sie das, was fast fertig ist, bevor Sie etwas Neues anfangen.',
        'Fertig und gut genug ist meist nützlicher als perfekt und unfertig.',
        'Schließen Sie heute eine offene Sache ab und spüren Sie die kleine Erleichterung danach.',
        'Die letzten zehn Prozent sind oft nur ein paar sorgfältige Minuten. Nehmen Sie sie sich heute.',
        'Senden Sie die E-Mail, die in Ihren Entwürfen wartet. Sie ist wahrscheinlich gut so, wie sie ist.',
        'Haken Sie es ab, atmen Sie durch und freuen Sie sich, dass es erledigt ist.',
        'Eine kleine erledigte Sache ist mehr wert als eine große halb fertige.',
        'Notieren Sie vor Feierabend den ersten Schritt für morgen, dann müssen Sie ihn sich nicht merken.',
        'Lesen Sie es noch einmal, korrigieren Sie, was Ihnen auffällt, und senden Sie es dann ab.',
        'Ein klares Ergebnis zum Tagesende macht den Abend leichter.',
        'Eine frühe Frage erspart später oft eine Stunde stilles Grübeln.',
        'Die meisten Menschen teilen ihr Wissen gern. Fragen Sie, ohne sich zu entschuldigen.',
        '„Ich komme nicht weiter“ ist ein klarer, nützlicher Satz, mit dem Ihr Team etwas anfangen kann.',
        'Sagen Sie in einfachen Worten, was Sie brauchen, und geben Sie anderen die Chance, Ja zu sagen.',
        'Zwei Leute lösen ein Problem oft schneller als eine Person, die allein darauf starrt.',
        'Sie sind keine Last, wenn Sie Hilfe brauchen. Sie gehören zum Team.',
        'Kommen Sie mit einer konkreten Frage, dann bekommen Sie auch eine konkrete Antwort.',
        'Sind die Anweisungen unklar, gehört Nachfragen dazu, die Arbeit richtig zu machen.',
        'Bieten Sie Hilfe an, wenn Sie können, und nehmen Sie sie an, wenn Sie sie brauchen. Beides wird mit Übung leichter.',
        'Jemand ein paar Türen weiter hat das wahrscheinlich schon einmal gelöst. Fragen Sie nach.',
        'Notieren Sie, was Sie diese Woche herausgefunden haben. Es ist mehr, als Sie denken.',
        'Etwas Neues zu lernen zeigt, dass Sie mit Ihrer Arbeit noch wachsen.',
        'Achten Sie darauf, wie jemand, den Sie schätzen, ein schwieriges Gespräch führt, und übernehmen Sie eine Sache davon.',
        'Lesen Sie in der Pause eine nützliche Seite und verbuchen Sie das als guten Tag für den Kopf.',
        'Wer eine Aufgabe jemand anderem erklärt, lernt sie dabei selbst überraschend gut.',
        'Es ist in Ordnung zu sagen: „Das weiß ich noch nicht“, und es dann herauszufinden.',
        'Jedes neue System wirkt verwirrend, bis Sie es ein paar Mal benutzt haben.',
        'Fragen Sie erfahrene Leute, wie sie es gelernt haben. Die Antwort beruhigt oft.',
        'Können entsteht durch Wiederholung. Wiederholen Sie das Kleine, bis es leicht wird.',
        'Ein wenig Neugier kann eine gewöhnliche Aufgabe interessanter machen.',
        'Ein früh bemerkter Fehler ist nur eine Korrektur, und die meisten werden früh bemerkt.',
        'Beheben Sie den Fehler, informieren Sie die Betroffenen und lassen Sie den Ärger dann verblassen.',
        'Fast jeder Fehler bei der Arbeit wirkt nach einer Woche kleiner als im Moment selbst.',
        'Ein Ausrutscher löscht nicht die Jahre sorgfältiger Arbeit, die hinter Ihnen liegen.',
        'Wenn etwas schiefgeht, schauen Sie zuerst auf den Ablauf und erst danach auf die Person.',
        'Alle um Sie herum haben schon einmal eine E-Mail an die falsche Person geschickt.',
        'Nehmen Sie die eine Lehre aus einem Fehler mit und lassen Sie den Rest hinter sich.',
        'Einen Fehler offen zuzugeben, schafft meist mehr Vertrauen, als nie einen gemacht zu haben.',
        'Auch sorgfältige Menschen haben ungeschickte Tage, und auch die sind am Abend vorbei.',
        'An die meisten kleinen Stolperer von heute werden Sie sich nächsten Monat nicht mehr erinnern.',
        'Ein ruhiger Tag ohne Notfälle ist ein guter Tag, auch wenn es niemand erwähnt.',
        'Achten Sie auf die kleinen Freuden: eine warme Tasse, ein leeres Postfach, eine ruhige Minute.',
        'Nicht jeder Tag braucht einen großen Erfolg. Ruhig und angenehm zu arbeiten reicht völlig.',
        'Freuen Sie sich über die Besprechung, die fünf Minuten früher endet, und nutzen Sie die Zeit, wie Sie möchten.',
        'Ein gewöhnlicher, gut gemachter Tag ist etwas, worauf Sie still stolz sein können.',
        'Gute Arbeit wirkt von außen oft unscheinbar, und das ist in Ordnung.',
        'Lassen Sie einen angenehmen Nachmittag angenehm sein, ohne dass er produktiv sein muss.',
        'Die kleinen Rituale des Tages, der erste Kaffee und die vertrauten Gesichter, verdienen Beachtung.',
        'Sie waren heute da und haben Ihren Teil getan, und das ist genug.',
        'Nehmen Sie sich heute Abend einen Moment, um an etwas zu denken, das gut gelaufen ist.',
        'Eine ruhige Minute zwischen zwei Aufgaben ist keine verlorene Zeit. So beginnt die nächste gut.',
    ),
    "tips": (
        'Trinken Sie langsam ein Glas Wasser, weg vom Bildschirm.',
        'Rollen Sie die Schultern fünfmal langsam nach hinten.',
        'Gönnen Sie Ihren Augen zwanzig Sekunden Ruhe: Schauen Sie in die Ferne oder schließen Sie sie.',
        'Strecken Sie die Arme über den Kopf, im Sitzen oder Stehen, und atmen Sie tief ein.',
        'Machen Sie einen Abstecher zum entferntesten Raum oder Fenster, das Sie erreichen können, und zurück.',
        'Prüfen Sie Ihre Haltung und lassen Sie die Schultern von den Ohren weg sinken.',
        'Drehen Sie den Kopf sanft von einer Seite zur anderen, nur so weit, wie es angenehm ist.',
        'Öffnen und schließen Sie die Hände zehnmal, um die Finger zu lockern.',
        'Heften Sie das Dokument an, das Sie am häufigsten öffnen, damit es nur einen Klick entfernt ist.',
        'Machen Sie draußen eine kurze Runde, zu Fuß oder im Rollstuhl, wie es für Sie passt.',
        'Nehmen Sie sich ein warmes oder kühles Getränk und genießen Sie es weg vom Bildschirm.',
        'Richten Sie Ihre Aufmerksamkeit auf etwas Ruhiges: einen Ausblick, ein Geräusch oder eine Oberfläche.',
        'Notieren Sie den nächsten Schritt einer Aufgabe, die Sie halb erledigt liegen gelassen haben.',
        'Stellen Sie beide Füße flach auf und sitzen oder stehen Sie zehn Atemzüge lang aufrecht.',
        'Schalten Sie einen Gruppenchat stumm, den Sie nur überfliegen.',
        'Lösen Sie kurz den Kiefer und entspannen Sie die Stirn.',
        'Bewegen Sie sich zwei Minuten lang so, wie es Ihnen heute guttut.',
        'Reservieren Sie sich fünfzehn Minuten im Kalender für die Aufgabe, die Sie immer wieder aufschieben.',
        'Stellen Sie Stuhl, Bildschirm oder Tastatur so ein, dass eine Sache bequemer wird.',
        'Nehmen Sie den längeren Weg zu Ihrer nächsten Besprechung oder Ihrem nächsten Anruf, wenn es geht.',
        'Speichern Sie eine Vorlage für eine E-Mail, die Sie immer wieder schreiben.',
        'Lernen Sie ein Tastenkürzel für das Programm, das Sie am meisten nutzen.',
        'Trinken Sie ein ganzes Glas Wasser vor Ihrem nächsten Kaffee oder Tee.',
        'Ziehen Sie die Schultern zu den Ohren hoch und lassen Sie sie dann langsam sinken.',
        'Gönnen Sie sich draußen oder am offenen Fenster eine Minute frische Luft.',
        'Atmen Sie fünfmal langsam durch und lassen Sie jedes Ausatmen etwas länger werden.',
        'Halten Sie eine ruhige Minute inne, bevor Sie die nächste Nachricht öffnen.',
        'Notieren Sie eine gute Sache, die heute schon passiert ist.',
        'Schließen Sie für drei Atemzüge die Augen und spüren Sie, wie es Ihnen geht.',
        'Nennen Sie drei Dinge, die Sie gerade wahrnehmen, egal mit welchem Sinn.',
        'Schreiben Sie eine Sache auf, auf die Sie sich diese Woche freuen.',
        'Stellen Sie einen Timer auf zwei Minuten und sitzen Sie einfach da, ohne Bildschirm.',
        'Freuen Sie sich an etwas Kleinem in Ihrer Nähe, etwa einer Pflanze oder Ihrer Lieblingstasse.',
        'Denken Sie an eine Sache, die Ihnen diese Woche gut gelungen ist, und klopfen Sie sich auf die Schulter.',
        'Hören Sie ein Lieblingslied von Anfang bis Ende, ohne dass etwas anderes offen ist.',
        'Atmen Sie dreimal ein, während Sie bis vier zählen, und aus, während Sie bis sechs zählen.',
        'Atmen Sie einmal durch, bevor Sie auf den nächsten kleinen Ärger reagieren.',
        'Notieren Sie etwas, das Sie kürzlich zum Lachen gebracht hat.',
        'Achten Sie eine Minute lang auf etwas Angenehmes: ein Geräusch, einen Duft oder etwas, das Sie berühren.',
        'Denken Sie an einen Ort, den Sie lieben, und stellen Sie ihn sich dreißig Sekunden lang vor.',
        'Erklären Sie eine kleine Aufgabe für „vorerst gut genug“ und machen Sie weiter.',
        'Schreiben Sie einen Satz über etwas, wofür Sie dankbar sind.',
        'Genießen Sie den nächsten Schluck Ihres Getränks und achten Sie auf den Geschmack.',
        'Machen Sie zwischen zwei Aufgaben eine kurze Pause, bevor Sie die nächste beginnen.',
        'Suchen Sie heute eine Sache, die besser läuft als erwartet.',
        'Wählen Sie ein Wort dafür, wie sich der Nachmittag anfühlen soll.',
        'Lassen Sie den Kopf sechzig Sekunden ruhen und kehren Sie dann zur nächsten Aufgabe zurück.',
        'Spüren Sie Ihre Füße auf dem Boden und einen Moment lang festen Halt.',
        'Erinnern Sie sich an etwas Freundliches, das jemand für Sie getan hat, und genießen Sie die Erinnerung.',
        'Notieren Sie eine Idee, auf die Sie später zurückkommen möchten, und lassen Sie sie ruhen.',
        'Räumen Sie eine kleine Ecke Ihres Schreibtischs auf, nur eine.',
        'Beantworten Sie eine Nachricht, die schon eine Weile wartet.',
        'Schreiben Sie die wichtigste Aufgabe für morgen auf einen Haftzettel oder in Ihre Notizen.',
        'Schließen Sie die Browser-Tabs, die Sie nicht mehr brauchen.',
        'Bedanken Sie sich bei jemandem aus dem Team für etwas, das diese Person kürzlich getan hat.',
        'Archivieren Sie fünf alte E-Mails, die Sie nicht mehr brauchen.',
        'Benennen Sie eine unübersichtlich benannte Datei um, damit Sie sie später leicht finden.',
        'Entfernen Sie ein oder zwei verirrte Dateien von Ihrem Desktop.',
        'Löschen Sie eine alte Erinnerung, die nicht mehr gilt.',
        'Geben Sie einem Dokument, das Sie oft öffnen, einen klaren Titel.',
        'Streichen Sie einen kleinen Punkt auf Ihrer Aufgabenliste durch.',
        'Melden Sie sich von einem Newsletter ab, den Sie nie lesen.',
        'Wischen Sie Tastatur oder Bildschirm mit einem weichen Tuch ab.',
        'Legen Sie Stift, Notizbuch und Wasser in Reichweite.',
        'Schreiben Sie sich selbst eine kurze Notiz, wo Sie heute aufgehört haben.',
        'Wählen Sie die wichtigste Aufgabe für heute Nachmittag und erledigen Sie sie zuerst.',
        'Leeren Sie den Papierkorb oder Recyclingbehälter an Ihrem Platz.',
        'Aktualisieren Sie eine Fortschrittsnotiz, damit andere den aktuellen Stand sehen.',
        'Räumen Sie Ihren Download-Ordner auf, indem Sie eine Handvoll Dateien verschieben.',
        'Stellen Sie eine Erinnerung für etwas ein, das Sie oft vergessen.',
        'Schalten Sie eine Benachrichtigung aus, die Sie nicht wirklich brauchen.',
        'Setzen Sie ein Lesezeichen für eine Seite, nach der Sie immer wieder suchen.',
        'Schreiben Sie eine zweizeilige Zusammenfassung einer Besprechung, solange sie noch frisch ist.',
        'Fragen Sie, ob eine regelmäßige Besprechung etwas kürzer sein könnte.',
        'Legen Sie ein einziges Ziel für die nächste Stunde fest und schreiben Sie es auf.',
        'Fragen Sie jemanden aus dem Team, wie der Tag läuft, und hören Sie wirklich zu.',
        'Teilen Sie einen nützlichen Link mit jemandem, dem er gefallen könnte.',
        'Sagen Sie Hallo zu jemandem, mit dem Sie noch nie gesprochen haben.',
        'Schicken Sie ein kurzes Dankeschön an jemanden, der Ihnen kürzlich geholfen hat.',
        'Begrüßen Sie zu Beginn Ihres nächsten Anrufs die anderen besonders herzlich.',
        'Fragen Sie im Team, worauf sich die anderen diese Woche freuen.',
        'Gratulieren Sie jemandem zu einem kleinen Erfolg, der Ihnen aufgefallen ist.',
        'Laden Sie jemanden aus dem Team zu einem kurzen Gespräch ein, bei Tee, Kaffee oder am Telefon.',
        'Loben Sie jemanden aus dem Team für etwas Bestimmtes, das gut gelungen ist.',
        'Lernen Sie den Namen von jemandem, den Sie oft sehen, aber noch nicht kennen.',
        'Geben Sie einen hilfreichen Tipp an jemanden im Team weiter, der ihn brauchen könnte.',
        'Bitten Sie jemanden um eine Empfehlung für ein Lied, eine Serie oder ein Buch.',
        'Melden Sie sich bei jemandem aus dem Team, der in letzter Zeit still war.',
        'Bieten Sie Hilfe bei einer Kleinigkeit an, wenn jemand viel zu tun hat.',
        'Begrüßen Sie die nächste Person, der Sie begegnen, mit einem herzlichen Hallo.',
        'Geben Sie ein freundliches Wort weiter, das Sie über jemanden aus dem Team gehört haben.',
        'Fragen Sie jemanden aus dem Team, was die Woche leichter gemacht hat.',
        'Schicken Sie eine freundliche Nachricht an jemanden, mit dem Sie früher gearbeitet haben.',
        'Danken Sie jemandem, der dafür sorgt, dass gemeinsame Räume gut funktionieren.',
        'Machen Sie zwei Leute aus dem Team miteinander bekannt, die sich gut verstehen könnten.',
        'Fragen Sie jemanden aus dem Team, wie Sie eine Übergabe leichter machen können.',
        'Teilen Sie einen kleinen, harmlosen Witz mit jemandem in Ihrer Nähe.',
        'Legen Sie etwas mehr Wärme in Ihr nächstes Bitte und Danke.',
        'Fragen Sie jemanden aus dem Team, was der Person in der Freizeit Freude macht.',
        'Hören Sie der nächsten Person, die mit Ihnen spricht, ganz zu, ohne nebenbei etwas anderes zu tun.',
    ),
    "done": (
        'Gut. Das ist erledigt.',
        'Schön. Es tut gut, etwas abzuschließen.',
        'Gut gemacht. Gönnen Sie sich eine kurze Pause vor der nächsten Aufgabe.',
        'Gut. Kleine erledigte Aufgaben summieren sich.',
        'Das ist geschafft. Darüber dürfen Sie sich freuen.',
        'Gut. Das können Sie von der Liste streichen.',
    ),
    "text": {
        HELP: """hello-world zeigt einen Gruß, einen Gedanken und einen kleinen Tipp.

Geben Sie bei der letzten Frage „plan“ für den Plan des Tages ein,
„erledigt“, wenn Sie ihn geschafft haben, oder „menü“ (oder m) für die
Optionen. Die Eingabetaste schließt das Fenster, q, x oder „beenden“
schließen es bei jeder Frage. Bei einer Planfrage holt „wieder“ einen
früheren, unerledigten Plan zurück. Nach „erledigt“ sehen Sie Ihre
letzten 3 erledigten Pläne. Menüoption 1 zeigt alle, Option 7 vergisst
einen, und Option 8 blendet Gedanken und Tipp aus. Im Menü führt die
Eingabetaste zurück.
Sie können hello.cmd auch mit einer dieser Optionen starten:
  --plain         Zeigt nur den Gruß, auf Englisch
  --stats         Zeigt, was auf diesem Computer gespeichert ist
  --reset         Löscht alles Gespeicherte (fragt vorher)
  --remind on     Öffnet sich täglich bei der Anmeldung (off: aus)
  --streak off    Blendet den Hinweis zu Tagen in Folge aus (on: ein)
  --version       Zeigt die Version
  --check-content DATEI
                  Prüft eine Inhaltsdatei der Organisation
  --help          Zeigt diesen Text

Exit-Codes: 0 bei Erfolg, 1 wenn ein Befehl fehlschlug oder die
Anzeige nicht ausgegeben werden konnte, 2 bei unbekannter Option.

Gespeicherte Notizen bleiben auf diesem Computer, in Ihrem
Benutzerordner. Nichts wird irgendwohin gesendet. Wer in der IT Zugriff
auf die Dateien dieses Computers hat, kann sie lesen.""",
        MENU_HELP: """Befehle, die Sie bei der letzten Frage eingeben können:
  erledigt  hakt den heutigen Plan ab und fragt nach dem nächsten
  plan      legt den heutigen Plan fest oder ändert ihn
  menü      öffnet diese Optionen
  q         schließt das Fenster, ebenso die Eingabetaste
Bei einer Planfrage holt „wieder“ Ihren früheren, unerledigten Plan
zurück.
Bei der Frage „Haben Sie es geschafft?“ bedeutet n „noch nicht“, und
Sie können den Plan für heute behalten. q schließt bei jeder Frage.
In diesem Menü zeigt 1 das Gespeicherte, 7 vergisst einen erledigten
Plan, und 8 blendet Gedanken und Tipp aus.
Geben Sie m ein, um die Optionen erneut zu sehen. Nichts wird
irgendwohin gesendet.""",
        SAVED_PLAN: 'Gespeichert. Geben Sie „erledigt“ ein, wenn Sie ihn geschafft haben, sonst fragt hello-world beim nächsten Öffnen nach.',
        GREETING: 'Hallo, Welt!',
        'hello.cmd is in this folder:':
            'hello.cmd liegt in diesem Ordner:',
        'Shortened to {n} characters.':
            'Auf {n} Zeichen gekürzt.',
        'Your saved file was damaged, so hello-world set it aside as a backup copy and started fresh. Your earlier days and plan could not be read. Menu option 4 deletes the backup.':
            'Ihre gespeicherte Datei war beschädigt. hello-world hat sie deshalb als Sicherungskopie beiseitegelegt und neu begonnen. Ihre bisherigen Tage und Ihr Plan konnten nicht gelesen werden. Menüoption 4 löscht die Sicherungskopie.',
        'Backup copy: ':
            'Sicherungskopie: ',
        'In the folder: ':
            'Im Ordner: ',
        'Sorry, "{shown}" is not one of the choices.':
            'Entschuldigung, „{shown}“ ist keine der Möglichkeiten.',
        'A plan needs a word or two, so nothing was saved.':
            'Ein Plan braucht ein oder zwei Wörter, daher wurde nichts gespeichert.',
        'The sign-in reminder works on Windows only.':
            'Die Erinnerung bei der Anmeldung funktioniert nur unter Windows.',
        'Your organization has turned off opening at sign-in.':
            'Ihre Organisation hat das Öffnen bei der Anmeldung deaktiviert.',
        'The reminder cannot be set up from this folder.':
            'Die Erinnerung kann aus diesem Ordner nicht eingerichtet werden.',
        'Could not set up the reminder.':
            'Die Erinnerung konnte nicht eingerichtet werden.',
        'Done. hello-world will open once a day when you sign in.':
            'Fertig. hello-world öffnet sich einmal täglich bei der Anmeldung.',
        'To stop it, choose option 2 in the menu.':
            'Zum Ausschalten wählen Sie Option 2 im Menü.',
        'Could not turn off the sign-in reminder.':
            'Die Erinnerung bei der Anmeldung ließ sich nicht ausschalten.',
        'Done. The sign-in reminder is off.':
            'Fertig. Die Erinnerung bei der Anmeldung ist aus.',
        'Saved on this computer in:':
            'Auf diesem Computer gespeichert in:',
        'Saved in your own user folder on this computer.':
            'In Ihrem eigenen Benutzerordner auf diesem Computer gespeichert.',
        'Days you opened it in the last {days} days: {n} (last 7 days: {recent})':
            'In den letzten {days} Tagen an {n} Tagen geöffnet (letzte 7 Tage: {recent})',
        'Times you marked a plan done: {n}':
            'So oft haben Sie einen Plan als erledigt markiert: {n}',
        'Your current plan: ':
            'Ihr aktueller Plan: ',
        'Earlier plan (for same): ':
            'Früherer Plan (für „wieder“): ',
        'Days-in-a-row message: shown.':
            'Hinweis zu Tagen in Folge: sichtbar.',
        'Days-in-a-row message: hidden.':
            'Hinweis zu Tagen in Folge: ausgeblendet.',
        'Opens by itself at sign-in: turned off by your organization.':
            'Öffnet sich bei der Anmeldung: von Ihrer Organisation deaktiviert.',
        'Opens by itself at sign-in: on.':
            'Öffnet sich bei der Anmeldung: ein.',
        'Opens by itself at sign-in: off.':
            'Öffnet sich bei der Anmeldung: aus.',
        "It never leaves this computer. Others who can read this computer's files, such as IT staff, could read it.":
            'Die Daten verlassen diesen Computer nie. Wer Zugriff auf die Dateien dieses Computers hat, zum Beispiel die IT-Abteilung, kann sie lesen.',
        'After tidying, the file holds only this:':
            'Nach dem Aufräumen enthält die Datei nur noch dies:',
        'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
            'Alle gespeicherten Notizen, Datumsangaben und Pläne auf diesem Computer löschen? (j oder n, Eingabetaste zum Abbrechen) > ',
        'Nothing was deleted.':
            'Es wurde nichts gelöscht.',
        'Could not delete everything.':
            'Es konnte nicht alles gelöscht werden.',
        'Delete these yourself:':
            'Bitte löschen Sie diese selbst:',
        'Could not list the folder, so backup copies may remain:':
            'Der Ordner war nicht lesbar. Eventuell sind noch Sicherungskopien da:',
        'Done. Everything saved was deleted.':
            'Fertig. Alles Gespeicherte wurde gelöscht.',
        'Another open hello-world window cannot put it back.':
            'Ein anderes offenes hello-world-Fenster kann es nicht zurückholen.',
        'Close any other open hello-world window, or it may save its notes again.':
            'Schließen Sie alle anderen offenen hello-world-Fenster, sonst speichern diese ihre Notizen womöglich erneut.',
        'Everything saved was deleted in another window, so this was not saved.':
            'Alles Gespeicherte wurde in einem anderen Fenster gelöscht, daher wurde dies nicht gespeichert.',
        'The other open window had also finished a plan.':
            'Das andere offene Fenster hatte ebenfalls einen Plan erledigt.',
        'The other open window changed the plan, so its plan is kept.':
            'Das andere Fenster hat den Plan geändert, daher gilt dessen Plan.',
        'Type plan at the last prompt to set one.':
            'Geben Sie bei der letzten Frage „plan“ ein, um einen festzulegen.',
        'That looks like a command, not a plan, so nothing was saved.':
            'Das sieht nach einem Befehl aus, nicht nach einem Plan. Es wurde nichts gespeichert.',
        'Type your plan, or press Enter to go back.':
            'Geben Sie Ihren Plan ein, oder drücken Sie die Eingabetaste, um zurückzukehren.',
        'Finished lately:':
            'Zuletzt erledigt:',
        'Your plan today: ':
            'Ihr heutiger Plan: ',
        'Your plan from {date}: ':
            'Ihr Plan vom {date}: ',
        'Earlier plan: ':
            'Früherer Plan: ',
        'Type the next plan, or Enter to close > ':
            'Nächsten Plan eingeben oder Eingabetaste zum Schließen > ',
        'Type the next plan, same to reuse the earlier plan, or Enter to close > ':
            'Nächsten Plan eingeben, „wieder“ für den früheren Plan, oder Eingabetaste zum Schließen > ',
        "Type today's plan, or Enter to keep it > ":
            'Heutigen Plan eingeben oder Eingabetaste zum Behalten > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
            'Heutigen Plan eingeben, „wieder“ für den früheren Plan, oder Eingabetaste zum Behalten > ',
        "Type today's plan, or Enter to go back > ":
            'Heutigen Plan eingeben oder Eingabetaste zum Zurückkehren > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
            'Heutigen Plan eingeben, „wieder“ für den früheren Plan, oder Eingabetaste zum Zurückkehren > ',
        'Closing.':
            'Wird geschlossen.',
        'There is no earlier plan to reuse yet. Nothing changed.':
            'Es gibt noch keinen früheren Plan. Es wurde nichts geändert.',
        'Nothing changed.':
            'Es wurde nichts geändert.',
        'Could not save that on this computer. Your plan is unchanged.':
            'Speichern auf diesem Computer fehlgeschlagen. Ihr Plan ist unverändert.',
        'No finished plans are saved.':
            'Es sind keine erledigten Pläne gespeichert.',
        'Type the number to forget (1 to {n}), or Enter to keep them all > ':
            'Welche Nummer soll vergessen werden? (1 bis {n}, Eingabetaste behält alle) > ',
        'There is no number "{typed}" on the list. Type a number from 1 to {n}, or press Enter to keep them all.':
            'Die Nummer „{typed}“ steht nicht in der Liste. Geben Sie eine Zahl von 1 bis {n} ein, oder drücken Sie die Eingabetaste, um alle zu behalten.',
        'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
            'Auch als früheren Plan für „wieder“ vergessen? (j oder n, Eingabetaste, um ihn für „wieder“ zu behalten) > ',
        'Type y or n, or press Enter to keep it for same.':
            'Geben Sie j oder n ein, oder drücken Sie die Eingabetaste, um ihn für „wieder“ zu behalten.',
        'That plan was already forgotten. Nothing changed.':
            'Dieser Plan war bereits vergessen. Es wurde nichts geändert.',
        'Forgotten: ':
            'Vergessen: ',
        'Same still has it.':
            'Mit „wieder“ ist er noch abrufbar.',
        'Could not save that on this computer. Nothing changed.':
            'Speichern auf diesem Computer fehlgeschlagen. Es wurde nichts geändert.',
        'Options':
            'Optionen',
        'Show what is saved on this computer':
            'Zeigen, was auf diesem Computer gespeichert ist',
        'Open once a day at sign-in (turned off by your organization)':
            'Bei der Anmeldung öffnen (von Ihrer Organisation deaktiviert)',
        'Turn off: open once a day at sign-in (now on)':
            'Ausschalten: einmal täglich bei der Anmeldung öffnen (jetzt ein)',
        'Turn on: open once a day at sign-in (now off)':
            'Einschalten: einmal täglich bei der Anmeldung öffnen (jetzt aus)',
        'Days-in-a-row message (hidden by your organization)':
            'Hinweis zu Tagen in Folge (von Ihrer Organisation ausgeblendet)',
        'Hide the days-in-a-row message (now shown)':
            'Hinweis zu Tagen in Folge ausblenden (jetzt sichtbar)',
        'Show the days-in-a-row message (now hidden)':
            'Hinweis zu Tagen in Folge einblenden (jetzt ausgeblendet)',
        'Delete everything saved':
            'Alles Gespeicherte löschen',
        'Help':
            'Hilfe',
        "Set today's plan (turned off by your organization)":
            'Heutigen Plan festlegen (von Ihrer Organisation deaktiviert)',
        'Forget a finished plan (turned off by your organization)':
            'Erledigten Plan vergessen (von Ihrer Organisation deaktiviert)',
        "Set or change today's plan":
            'Heutigen Plan festlegen oder ändern',
        'Forget one finished plan':
            'Einen erledigten Plan vergessen',
        'Thought and tip (hidden by your organization)':
            'Gedanke und Tipp (von Ihrer Organisation ausgeblendet)',
        'Hide the thought and tip (now shown)':
            'Gedanken und Tipp ausblenden (jetzt sichtbar)',
        'Show the thought and tip (now hidden)':
            'Gedanken und Tipp einblenden (jetzt ausgeblendet)',
        '{date}: ':
            '{date}: ',
        'Enter':
            'Eingabetaste',
        'Back to the last prompt':
            'Zurück zur letzten Frage',
        'Choose 1 to 11, or Enter to go back > ':
            '1 bis 11 wählen oder Eingabetaste zum Zurückkehren > ',
        'Choose 1 to 11, m to list the options, or Enter to go back > ':
            '1 bis 11 wählen, m für die Optionen oder Eingabetaste zum Zurückkehren > ',
        'The saved file could not be read just now, so this may be out of date.':
            'Die gespeicherte Datei konnte gerade nicht gelesen werden, daher ist dies eventuell nicht aktuell.',
        'Type full to see the whole file, or Enter to go on > ':
            'Mit „alles“ die ganze Datei anzeigen, oder Eingabetaste zum Fortfahren > ',
        'Could not save that choice on this computer.':
            'Diese Auswahl konnte nicht auf diesem Computer gespeichert werden.',
        'Your organization has hidden the days-in-a-row message.':
            'Ihre Organisation hat den Hinweis zu Tagen in Folge ausgeblendet.',
        'Done. The days-in-a-row message is on.':
            'Fertig. Der Hinweis zu Tagen in Folge ist eingeschaltet.',
        'Done. The days-in-a-row message is off.':
            'Fertig. Der Hinweis zu Tagen in Folge ist ausgeschaltet.',
        'Plans are turned off by your organization.':
            'Pläne sind von Ihrer Organisation deaktiviert.',
        'Your organization has hidden the thought and tip.':
            'Ihre Organisation hat den Gedanken und den Tipp ausgeblendet.',
        'Done. The thought and tip are on.':
            'Fertig. Gedanke und Tipp sind eingeschaltet.',
        'Done. The thought and tip are off.':
            'Fertig. Gedanke und Tipp sind ausgeschaltet.',
        'Type 1 to 11, or press Enter to go back.':
            'Geben Sie 1 bis 11 ein, oder drücken Sie die Eingabetaste, um zurückzukehren.',
        'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
            'Soll sich hello-world einmal täglich bei der Anmeldung öffnen? (j oder n, Eingabetaste für später) > ',
        'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
            'Soll sich hello-world einmal täglich bei der Anmeldung öffnen, um nach Ihrem Plan zu fragen? (j oder n, Eingabetaste für später) > ',
        'Type y or n, or press Enter for not now.':
            'Geben Sie j oder n ein, oder drücken Sie die Eingabetaste für später.',
        'That was not understood. It will ask again on a later visit.':
            'Die Eingabe wurde nicht erkannt. Beim nächsten Mal wird erneut gefragt.',
        'It will ask again on a later visit. Menu option 2 also turns it on.':
            'Beim nächsten Mal wird erneut gefragt. Sie können es auch über Menüoption 2 einschalten.',
        'No problem. Menu option 2 turns it on later.':
            'Kein Problem. Sie können es später über Menüoption 2 einschalten.',
        "Okay. It won't ask again. Menu option 2 turns it on.":
            'In Ordnung. Es wird nicht mehr gefragt. Einschalten können Sie es über Menüoption 2.',
        'Okay. It will ask again on a later visit. Type n to stop it.':
            'In Ordnung. Beim nächsten Mal wird erneut gefragt. Geben Sie n ein, damit nicht mehr gefragt wird.',
        'When did you finish it?':
            'Wann haben Sie ihn erledigt?',
        'Today':
            'Heute',
        'Type a number from 1 to {n}, or Enter for 1 > ':
            'Zahl von 1 bis {n} eingeben oder Eingabetaste für 1 > ',
        'Type a number from 1 to {n}, or press Enter.':
            'Geben Sie eine Zahl von 1 bis {n} ein, oder drücken Sie die Eingabetaste.',
        'That looks like more than one thing. Finishing the first part still counts.':
            'Das klingt nach mehr als einer Sache. Wenn der erste Teil erledigt ist, zählt das schon.',
        'There is no plan to mark as done. Type plan to set one.':
            'Es gibt keinen Plan zum Abhaken. Geben Sie „plan“ ein, um einen festzulegen.',
        'Could not save that on this computer. The plan is still open.':
            'Speichern auf diesem Computer fehlgeschlagen. Der Plan ist noch offen.',
        'Your plan from over two weeks ago was put away. Type same at the plan prompt to bring it back.':
            'Ihr Plan von vor über zwei Wochen wurde beiseitegelegt. Geben Sie bei der Planfrage „wieder“ ein, um ihn zurückzuholen.',
        "Press Enter at each question to skip it, and once more to close. That's it.":
            'Drücken Sie bei jeder Frage die Eingabetaste, um sie zu überspringen, und noch einmal zum Schließen. Mehr braucht es nicht.',
        'Welcome.':
            'Willkommen.',
        'Each day you get one thought and one small thing to try, the same for everyone.':
            'Jeden Tag gibt es einen Gedanken und einen kleinen Tipp, für alle gleich.',
        'If you type a plan, it asks next time how it went. Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks.':
            'Wenn Sie einen Plan eingeben, fragt hello-world beim nächsten Mal, wie es lief. Ihre Notizen bleiben auf diesem Computer und werden nie gesendet. Wie jede Arbeitsdatei sind sie nicht geheim, also bleiben Sie bei alltäglichen Aufgaben.',
        'Type menu at the end for the options.':
            'Geben Sie am Ende „menü“ ein, um die Optionen zu sehen.',
        'Welcome back. Glad you are here.':
            'Willkommen zurück. Schön, dass Sie da sind.',
        'You have opened this {row} days in a row. Nice to see you.':
            'Sie haben hello-world {row} Tage in Folge geöffnet. Schön, Sie zu sehen.',
        'Last time you planned: ':
            'Ihr letzter Plan: ',
        'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
            'Haben Sie es geschafft? (j für ja, n für noch nicht, Eingabetaste zum Überspringen) > ',
        'Type y or n, or press Enter to skip.':
            'Geben Sie j oder n ein, oder drücken Sie die Eingabetaste zum Überspringen.',
        'Could not save that on this computer. Your answer was not counted.':
            'Speichern fehlgeschlagen. Ihre Antwort wurde nicht gezählt.',
        'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
            'Kein Problem. Für heute behalten? (j oder n, Eingabetaste zum Behalten) > ',
        'Type y to keep it, n to clear it, or press Enter to keep it.':
            'Geben Sie j zum Behalten ein, n zum Entfernen, oder drücken Sie die Eingabetaste zum Behalten.',
        'Cleared. Type same at a plan prompt if you want it back.':
            'Entfernt. Mit „wieder“ bei einer Planfrage holen Sie ihn zurück.',
        'Kept for today.':
            'Für heute behalten.',
        'That was not understood. Your plan is left as it was.':
            'Die Eingabe wurde nicht erkannt. Ihr Plan bleibt, wie er war.',
        'Your plan is still open.':
            'Ihr Plan ist noch offen.',
        'Thought for today:':
            'Gedanke des Tages:',
        'Try this today:':
            'Tipp des Tages:',
        'Your plan for today: ':
            'Ihr Plan für heute: ',
        'Still open since {date}:':
            'Offen seit {date}:',
        '(Enter to skip)':
            '(Eingabetaste zum Überspringen)',
        '(A plan typed here replaces the old one. Enter to skip)':
            '(Ein hier eingegebener Plan ersetzt den alten. Eingabetaste zum Überspringen)',
        '(Type same to reuse it, or Enter to skip)':
            '(Mit „wieder“ übernehmen, oder Eingabetaste zum Überspringen)',
        'What is one thing you want to get done today?':
            'Was möchten Sie heute erledigen? Eine Sache genügt.',
        'There is no earlier plan to reuse yet. Nothing was saved.':
            'Es gibt noch keinen früheren Plan. Es wurde nichts gespeichert.',
        'Your notes could not be saved on this computer. This screen still works.':
            'Ihre Notizen konnten auf diesem Computer nicht gespeichert werden. Diese Anzeige funktioniert trotzdem.',
        'Type menu, or Enter to close > ':
            '„menü“ eingeben, oder Eingabetaste zum Schließen > ',
        'Type done, plan or menu, or Enter to close > ':
            '„erledigt“, „plan“ oder „menü“ eingeben, oder Eingabetaste zum Schließen > ',
        'Type plan or menu, or Enter to close > ':
            '„plan“ oder „menü“ eingeben, oder Eingabetaste zum Schließen > ',
        'Type done, plan or menu, or press Enter to close.':
            'Geben Sie „erledigt“, „plan“ oder „menü“ ein, oder drücken Sie die Eingabetaste zum Schließen.',
        'Type plan or menu, or press Enter to close.':
            'Geben Sie „plan“ oder „menü“ ein, oder drücken Sie die Eingabetaste zum Schließen.',
        "The saved file can't be read right now, or it is damaged.":
            'Die gespeicherte Datei ist gerade nicht lesbar oder beschädigt.',
        'Nothing was changed. Saved in: ':
            'Nichts geändert. Gespeichert in: ',
        'Deleting saved notes needs a person at the keyboard.':
            'Zum Löschen gespeicherter Notizen muss jemand an der Tastatur sitzen.',
        '{option} needs on or off. Here are the options.':
            '{option} erwartet on oder off. Hier sind die Optionen.',
        'Unknown option: {option}. Here are the options.':
            'Unbekannte Option: {option}. Hier sind die Optionen.',
        '&Done':
            '&Erledigt',
        '&Not yet':
            '&Noch nicht',
        'S&kip':
            '&Überspringen',
        '&Save':
            '&Speichern',
        '&I did it':
            '&Geschafft',
        '&Options':
            '&Optionen',
        'Close':
            'Schließen',
        'Not today':
            'Heute nicht',
        'Did you do it?':
            'Haben Sie es geschafft?',
        'Done. A reminder comes when you sign in, if there is a plan to ask about.':
            'Fertig. Bei der Anmeldung kommt eine Erinnerung, wenn es einen Plan zum Nachfragen gibt.',
        'Done. The Start menu opens a window with buttons.':
            'Fertig. Das Startmenü öffnet ein Fenster mit Schaltflächen.',
        'Done. The Start menu opens this text screen.':
            'Fertig. Das Startmenü öffnet diesen Textbildschirm.',
        'More options':
            'Weitere Optionen',
        'Remind me when I sign in':
            'Bei der Anmeldung erinnern',
        'Show the thought and tip':
            'Gedanken und Tipp anzeigen',
        'Type your plan in the box.':
            'Geben Sie Ihren Plan in das Feld ein.',
        'Use a window with buttons (now this text screen)':
            'Fenster mit Schaltflächen verwenden (jetzt Textbildschirm)',
        'Use the text screen':
            'Textbildschirm verwenden',
        'Use this text screen (now a window with buttons)':
            'Diesen Textbildschirm verwenden (jetzt Fenster)',
        'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
            'Möchten Sie eine Erinnerung bei der Anmeldung? Sie zeigt Ihren Plan vom letzten Mal, und Sie antworten mit einem Klick. Unter Optionen können Sie sie ausschalten.',
        'Window or text screen (set by your organization)':
            'Fenster/Textbildschirm (von Ihrer Organisation festgelegt)',
        'Your organization has set hello-world to open as a text screen.':
            'Ihre Organisation hat hello-world auf den Textbildschirm festgelegt.',
        'Saved.':
            'Gespeichert.',
        'Save your plan before closing?':
            'Ihren Plan vor dem Schließen speichern?',
        'Delete all saved notes, dates and plans on this computer?':
            'Alle gespeicherten Notizen, Daten und Pläne auf diesem Computer löschen?',
        'Turn off: reminder when you sign in (now on)':
            'Ausschalten: Erinnerung bei der Anmeldung (jetzt an)',
        'Turn on: reminder when you sign in (now off)':
            'Einschalten: Erinnerung bei der Anmeldung (jetzt aus)',
        'Reminder when you sign in (turned off by your organization)':
            'Erinnerung bei der Anmeldung (von der Organisation aus)',
        'Reminder when you sign in: on.':
            'Erinnerung bei der Anmeldung: an.',
        'Reminder when you sign in: off.':
            'Erinnerung bei der Anmeldung: aus.',
        'Reminder when you sign in: turned off by your organization.':
            'Erinnerung bei der Anmeldung: von Ihrer Organisation ausgeschaltet.',
        'Show the days-in-a-row message':
            'Hinweis zu Tagen in Folge einblenden',
        'Done. The thought and tip show next time you open hello-world.':
            'Fertig. Gedanke und Tipp erscheinen beim nächsten Öffnen von hello-world.',
        "Clear today's plan?":
            'Den Plan für heute löschen?',
        'Next plan, if you want one:':
            'Nächster Plan, falls Sie möchten:',
        'A few things? Put ; between them.':
            'Mehrere Dinge? Trennen Sie sie mit ;',
        'A plan can be up to {n} characters.':
            'Ein Plan darf bis zu {n} Zeichen lang sein.',
        'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
            'Haben Sie sie geschafft? (j für alle, n für noch nicht, die Nummern der erledigten, Eingabetaste zum Überspringen) > ',
        'Last time you planned:':
            'Ihr letzter Plan:',
        'The rest is kept for today.':
            'Der Rest bleibt für heute.',
        'Tick the ones you did, then click Done. With none ticked, Done means all of them.':
            'Haken Sie die erledigten an und klicken Sie auf Erledigt. Ohne Haken gilt Erledigt für alle.',
        'Type y for all, n for not yet, or the numbers you did, such as 1 3. Enter skips.':
            'Geben Sie j für alle ein, n für noch nicht, oder die Nummern der erledigten, etwa 1 3. Eingabetaste überspringt.',
        'Your settings were kept.':
            'Ihre Einstellungen wurden behalten.',
        'Language (set by your organization)':
            'Sprache (von Ihrer Organisation festgelegt)',
        'Language (now {name})':
            'Sprache (jetzt {name})',
        'following Windows':
            'wie Windows',
        'Your organization shows hello-world in English.':
            'Ihre Organisation zeigt hello-world auf Englisch.',
        'Follow Windows':
            'Wie Windows',
        'Type a number from 1 to {n}, or Enter to keep it > ':
            'Geben Sie eine Zahl von 1 bis {n} ein, oder Eingabetaste zum Behalten > ',
        'Done. The new language shows next time you open hello-world.':
            'Fertig. Die neue Sprache erscheint beim nächsten Öffnen von hello-world.',
        'Language...':
            'Sprache...',
        'Hello, {name}!':
            'Hallo, {name}!',
        'One thing to get done today? Open hello-world to plan it.':
            'Eine Sache für heute? Öffnen Sie hello-world, um sie zu planen.',
        '&Open':
            'Ö&ffnen',
        'Reminder settings...':
            'Erinnerung einstellen...',
        'Greet me by name':
            'Mich mit Namen begrüßen',
        'At sign-in':
            'Bei der Anmeldung',
        'At {at}':
            'Um {at}',
        'Also on days with no plan':
            'Auch an Tagen ohne Plan',
        'Open hello-world after I answer':
            'hello-world nach meiner Antwort öffnen',
        'Not on weekends':
            'Nicht am Wochenende',
        'Done. A reminder comes at {at} each day, if there is a plan to ask about.':
            'Fertig. Jeden Tag um {at} kommt eine Erinnerung, wenn es einen Plan zum Nachfragen gibt.',
        'Send feedback...':
            'Rückmeldung senden...',
        '"holidays" must be a list of at most {n} dates.':
            '"holidays" muss eine Liste mit höchstens {n} Daten sein.',
        '"title" must be 1 to 40 characters of plain text, with no link or address.':
            '"title" muss 1 bis 40 Zeichen einfacher Text sein, ohne Link oder Adresse.',
        '"{list}" must be a list of {low} to {high} lines.':
            '"{list}" muss eine Liste mit {low} bis {high} Zeilen sein.',
        "Can't read {path}: {error}":
            '{path} kann nicht gelesen werden: {error}',
        'Could not save that on this computer.':
            'Das konnte auf diesem Computer nicht gespeichert werden.',
        'Days you opened hello-world: {n}':
            'Tage, an denen Sie hello-world geöffnet haben: {n}',
        'Keep a longer history':
            'Längeren Verlauf behalten',
        'Keep my numbers':
            'Meine Zahlen behalten',
        'Longest run of days: {n}':
            'Längste Folge von Tagen: {n}',
        "Mark today's plan done":
            'Heutigen Plan als erledigt markieren',
        "Mark today's plan done (plans are turned off)":
            'Heutigen Plan als erledigt markieren (Pläne aus)',
        'My numbers are off. Turn them on under Options, or with --set numbers on.':
            'Ihre Zahlen sind aus. Schalten Sie sie unter Optionen oder mit --set numbers on ein.',
        'My numbers...':
            'Meine Zahlen...',
        'Nothing finished yet this week. That is fine.':
            'Diese Woche noch nichts erledigt. Das ist in Ordnung.',
        'OK: {thoughts} thoughts and {tips} tips.':
            'OK: {thoughts} Gedanken und {tips} Tipps.',
        'Plans finished: {n}':
            'Erledigte Pläne: {n}',
        'Save my plans to a file':
            'Meine Pläne in einer Datei speichern',
        'Saved to {path}':
            'Gespeichert in {path}',
        "The file isn't valid JSON, or is over 200,000 characters.":
            'Die Datei ist kein gültiges JSON oder hat mehr als 200.000 Zeichen.',
        'The file must hold an object with two lists, "thoughts" and "tips", and may add "holidays" and "title".':
            'Die Datei muss ein Objekt mit zwei Listen enthalten, "thoughts" und "tips", und darf "holidays" und "title" ergänzen.',
        'This week you finished {n}:':
            'Diese Woche haben Sie {n} erledigt:',
        'This week...':
            'Diese Woche...',
        'holidays line {line} is not a date like 2026-12-25.':
            'Zeile {line} von holidays ist kein Datum wie 2026-12-25.',
        '{list} line {line} has a date.':
            'Zeile {line} von {list} enthält ein Datum.',
        '{list} line {line} has a link or an address.':
            'Zeile {line} von {list} enthält einen Link oder eine Adresse.',
        '{list} line {line} has control characters or extra spaces.':
            'Zeile {line} von {list} enthält Steuerzeichen oder zu viele Leerzeichen.',
        '{list} line {line} is not text.':
            'Zeile {line} von {list} ist kein Text.',
        '{list} line {line} must be {low} to {high} characters long.':
            'Zeile {line} von {list} muss {low} bis {high} Zeichen lang sein.',
    },
}

def _override(items, changes):
    """A list with some items replaced, by index, for a regional variant."""
    return tuple(changes.get(i, item) for i, item in enumerate(items))


# ---- Canadian French ----

_FR_CA_TEXT = {
    MENU_HELP:
        """Mots à taper à la dernière question :
  fait  marque le plan du jour comme terminé, puis demande le suivant
  plan  définit ou modifie le plan du jour
  menu  ouvre ces options
  q     ferme la fenêtre, tout comme Entrée
À une question de plan, reprendre ramène le plan antérieur non terminé.
À la question « L'avez-vous fait? », n veut dire pas encore, et
vous pouvez garder le plan pour aujourd'hui. q ferme depuis n'importe
quelle question.
Dans ce menu, 1 montre ce qui est enregistré, 7 oublie un plan terminé
et 8 masque la pensée et l'astuce.
Tapez m pour revoir les options. Rien n'est envoyé nulle part.""",
    GREETING:
        'Bonjour, le monde!',
    'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
        'Supprimer toutes les notes, dates et plans enregistrés sur cet ordinateur? (o ou n, Entrée pour annuler) > ',
    'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
        "L'oublier aussi comme plan à reprendre? (o ou n, Entrée pour le garder) > ",
    'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
        "Voulez-vous que hello-world s'ouvre une fois par jour à votre connexion? (o ou n, Entrée pour plus tard) > ",
    'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
        "Voulez-vous que hello-world s'ouvre une fois par jour à votre connexion pour vous demander où en est votre plan? (o ou n, Entrée pour plus tard) > ",
    'When did you finish it?':
        "Quand l'avez-vous terminé?",
    'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
        "L'avez-vous fait? (o pour oui, n pour pas encore, Entrée pour passer) > ",
    'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
        "Ce n'est pas grave. Le garder pour aujourd'hui? (o ou n, Entrée pour le garder) > ",
    'What is one thing you want to get done today?':
        "Quelle tâche voulez-vous accomplir aujourd'hui?",
    'Did you do it?':
        "L'avez-vous fait?",
    'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
        "Voulez-vous un rappel à la connexion? Il affiche votre plan de la dernière fois, et vous répondez d'un clic. Vous pouvez le désactiver dans Options.",
    'Save your plan before closing?':
        'Enregistrer votre plan avant de fermer?',
    'Delete all saved notes, dates and plans on this computer?':
        'Supprimer toutes les notes, dates et plans enregistrés sur cet ordinateur?',
    "Clear today's plan?":
        "Effacer le plan d'aujourd'hui?",
    'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
        'Les avez-vous faites? (o pour toutes, n pour pas encore, les numéros de celles faites, Entrée pour passer) > ',
    'Hello, {name}!':
        'Bonjour, {name}!',
    'One thing to get done today? Open hello-world to plan it.':
        "Une chose à faire aujourd'hui? Ouvrez hello-world pour la planifier.",
    'Not on weekends':
        'Pas la fin de semaine',
}
LANGUAGES["fr-CA"] = {**LANGUAGES["fr"],
    "text": {**LANGUAGES["fr"]["text"], **_FR_CA_TEXT},
    "thoughts": _override(LANGUAGES["fr"]["thoughts"], {
        13: "Une matinée sans entrain ne décide pas de l'après-midi. Vous pouvez recommencer après le dîner.",
        31: "Dînez loin de votre bureau aujourd'hui. La boîte de réception peut attendre le temps d'un sandwich.",
        45: 'Un petit bonjour et une question sur la fin de semaine peuvent être le meilleur moment de la matinée.',
        54: 'Envoyez le courriel qui attend dans vos brouillons. Il est sans doute très bien tel quel.',
        85: 'Tout le monde autour de vous a déjà envoyé un courriel à la mauvaise personne au moins une fois.',
    }),
    "tips": _override(LANGUAGES["fr"]["tips"], {
        14: "Désactivez les notifications d'un clavardage de groupe que vous ne faites que survoler.",
        20: 'Enregistrez un modèle pour un courriel que vous écrivez encore et encore.',
        52: 'Notez la tâche principale de demain sur un papillon adhésif ou dans vos notes.',
        55: "Archivez cinq vieux courriels dont vous n'avez plus besoin.",
        61: "Désabonnez-vous d'une infolettre que vous ne lisez jamais.",
        66: 'Videz le bac de recyclage ou la poubelle de votre bureau.',
        82: "Invitez quelqu'un de votre équipe à jaser quelques minutes autour d'un thé, d'un café ou lors d'un appel.",
    }),
}

# ---- Chinese ----

LANGUAGES["zh"] = {
    "days": ('星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'),
    "months": ('1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'),
    "date": '{year}年{month}{d}日 {day}',
    "thoughts": (
        '打开那份您一直在回避的文档，只读第一段。',
        '开始十分钟也是开始，而且往往会让接下来的十分钟更轻松。',
        '今天不需要完整的计划，只需要一个合理的第一步。',
        '先写下一个粗糙的第一句。有了它，之后才有东西可以改。',
        '把桌上的一个小角落收拾干净，您会发现其他地方看起来也平静多了。',
        '从清单上挑最小的一件事，做完再看其他的。',
        '趁着安静的早上开个不完美的头，也胜过等一个可能不会来的完美时机。',
        '把第一步写进日历，让它有个落脚的地方。',
        '大项目大多是由一个个普通的下午叠起来的，今天就争取做好一个下午。',
        '把下一步要做的事说出来，清单上的其他事先排队等着。',
        '有些日子节奏比您希望的慢，但这样的节奏同样算数。',
        '对自己说话，就像对刚入职一周的新同事那样温和。',
        '做了多年的事，您仍然可以边做边学。',
        '早上状态平平，不代表下午也是如此。午饭后可以重新开始。',
        '累了是一种信号，不是失败。调整一下计划，慢慢继续。',
        '您常常体谅别人，也请同样体谅自己。',
        '进步常常一阵子看不出来，然后忽然就有了写满的一页。',
        '有些内容要读第二遍才明白，这很正常。',
        '不必等到觉得准备好了。紧张着去做，也是在做。',
        '今天的尽力而为可能比昨天少一些，这没关系。',
        '关掉不用的标签页。几分钟内您就会觉得注意力集中了。',
        '一件事，一个窗口，二十五分钟。看看专注一阵能做多少。',
        '冒出杂念时就把它记下来，然后回到手头的事。',
        '如果可以，把手机静音一小时，专心做事。',
        '想想哪一件事能让今天成为不错的一天，并为它留出时间。',
        '一次只做一件事，通常比感觉上更快。',
        '一张简洁的三件事清单，胜过一张零散的二十件事清单。',
        '留意自己走神的时候，然后不加责备地把注意力拉回来。',
        '把最难的任务放在精力最好的时候，哪怕那不是一早。',
        '戴上耳机，烧上一壶水，关上门。环境布置好了，专注自然会来。',
        '离开屏幕五分钟。回来时头脑会清醒一些。',
        '今天离开工位吃午饭吧。邮件可以等您吃完。',
        '绕着大楼走一小圈，也是在为头脑做正事。',
        '在忙碌的下午离开屏幕一分钟，时间花得很值。',
        '活动一下肩膀，放松下巴。它们可能已经紧绷好几个小时了。',
        '如果可以，今晚准时下班。明天的您会感谢今晚的休息。',
        '休息也是工作的一部分，因为人累了容易重复犯同样的小错。',
        '让眼睛休息一会儿，把肩膀放松下来。',
        '好好休息一下，下半天就像重新开始。',
        '把晚上留给自己。晚上九点，收件箱里没有什么非您不可。',
        '今天向一位同事道声谢，谢谢对方主动帮忙的一件小事。',
        '大多数人都在尽力而为，他们要处理的事往往比您看到的多。',
        '记住同事喝茶还是喝咖啡、喜欢怎么喝。记住这些是一份小小的心意。',
        '如果有人对您说话有点冲，就当对方今天不顺，而不是在评判您。',
        '帮人扶一下门，分享一些零食，让别人把话说完。',
        '一声问好，再问一句周末过得怎样，可能是一个早上最愉快的时刻。',
        '新同事问到看似显而易见的问题时，想想您也曾这样问过。',
        '同事的想法让您的工作变得更好时，请当面说出来，把功劳归给对方。',
        '回复消息时多一点温度。不费什么，却让人舒服。',
        '找最近开会时比较安静的同事聊聊，问问对方近况如何。',
        '先把快完成的事做完，再开始新的。',
        '完成且够好，通常比完美却没做完更有用。',
        '今天了结一件悬而未决的事，感受一下随之而来的轻松。',
        '最后那百分之十，往往只需要几分钟的细心。今天就把它做完。',
        '把草稿箱里那封邮件发出去吧。它很可能已经可以了。',
        '标记为完成，深呼吸一下，为做完它高兴一下。',
        '做完的一件小事，比做了一半的大事更有价值。',
        '下班前把明天的第一步写在便条上，这样就不用记在脑子里了。',
        '再读一遍，改掉发现的问题，然后发出去。',
        '一天以一个整洁的成果收尾，晚上会觉得轻松些。',
        '早点提问，通常能省下之后一个小时的独自苦想。',
        '大多数人都乐意分享自己的知识。提问时不必道歉。',
        '“我卡住了”是一句清楚、有用的话，同事听了就知道怎么帮您。',
        '用简单的话说出您需要什么，给别人一个答应的机会。',
        '两个人一起看问题，往往比一个人苦苦盯着解决得更快。',
        '需要帮忙并不是给人添麻烦。您是团队的一员。',
        '带着具体的问题去问，对方才能给出具体的答案。',
        '如果说明不清楚，问清楚本身就是把工作做好的一部分。',
        '能帮忙时就帮，需要时就接受帮助。两者都会越练越自然。',
        '走廊那头可能就有人解决过这个问题。去找找吧。',
        '把这周弄明白的事简单记下来。积累起来会比您想的多。',
        '在新事物面前当新手，说明您还在成长。',
        '留意一位您欣赏的同事怎样处理一通棘手的电话，学上一招。',
        '休息时读上一页有用的东西，对头脑来说，今天就算收获不错。',
        '把一项工作讲给别人听，自己往往也会学得更透。',
        '说一句“这个我还不知道”，然后去弄清楚，完全没问题。',
        '任何不熟悉的系统，在用过几次之前看起来都让人困惑。',
        '问问更有经验的人是怎么学会的。答案常常让人安心。',
        '技能来自重复，把小事反复做，直到它变得容易。',
        '对平常的工作多一点好奇，可能会让它变得更有意思。',
        '早发现的错误只是一处更正，而大多数错误都会被及早发现。',
        '改正它，告诉需要知道的人，然后让那份难受慢慢过去。',
        '工作中几乎每个错误，一周后看都没有当时感觉的那么大。',
        '一次失误抹不掉您多年来认真的工作。',
        '出了问题时，先看流程，再看人。',
        '您身边的每个人，都至少有一次把邮件发给了不该发的人。',
        '从错误中记住一条教训，其余的就放下吧。',
        '坦然承认错误，通常比从不犯错更能赢得信任。',
        '细心的人也会有笨手笨脚的一天，到晚上就过去了。',
        '到下个月，今天的大多数小磕绊您都不会记得了。',
        '平静无事、不用救火的一天就是好日子，哪怕没人提起。',
        '留意那些小小的愉快：一杯热饮、清空的收件箱、安静的一分钟。',
        '不是每天都需要大成就。平稳愉快也是很好的工作方式。',
        '会议提前五分钟结束时，好好享受，随意安排这段时间。',
        '把平凡的一天过好，就值得默默为自己骄傲。',
        '好的工作从外面看往往不起眼，这没关系。',
        '愉快的下午就让它愉快地过，不必非要高效。',
        '一天中的小日常，第一杯咖啡、熟悉的面孔，都值得留意。',
        '今天您到岗了，也做好了自己的那份，这就足够了。',
        '今晚花一点时间，想想今天进展顺利的一件事。',
        '两件事之间安静的一分钟不算浪费，下一件事往往由此开个好头。',
    ),
    "tips": (
        '离开屏幕，慢慢喝一杯水。',
        '慢慢地向后转动肩膀五次。',
        '让眼睛休息二十秒：望向远处，或闭上眼睛。',
        '坐着或站着，把双臂举过头顶伸展一下，深吸一口气。',
        '去到您能去的最远的房间或窗边，再回来。',
        '检查一下坐姿，让肩膀放松下沉，远离耳朵。',
        '轻轻左右转动脖子，转到舒服的程度就好。',
        '双手张开、握拳十次，放松手指。',
        '把最常打开的那份文档固定起来，一点就能打开。',
        '到室外短暂走走或转转，选您方便的方式。',
        '倒一杯热饮或冷饮，离开屏幕慢慢享用。',
        '把注意力放在一样平静的东西上，比如一处景色、一种声音或一种触感。',
        '为一件做了一半的事写下下一步。',
        '双脚平放在地上，坐直或站直，做十次呼吸。',
        '把一个您只是随便扫一眼的群聊设为免打扰。',
        '松开咬紧的下巴，放松一下额头。',
        '用今天觉得舒服的任何方式活动两分钟。',
        '在日历上为一直拖着的那件事留出十五分钟。',
        '调整一下椅子、屏幕或键盘，让其中一样用起来更舒服。',
        '如果方便，去下一个会议或通话时绕点远路。',
        '为一封经常要写的邮件保存一个模板。',
        '为最常用的程序学一个快捷键。',
        '下一杯咖啡或茶之前，先喝完一整杯水。',
        '耸起肩膀贴近耳朵，然后让它们慢慢放松下来。',
        '走到室外或打开窗户，呼吸一分钟新鲜空气。',
        '慢慢呼吸五次，每次呼气都比上一次长一点。',
        '打开下一条消息前，安静地停一分钟。',
        '记下今天到目前为止发生的一件好事。',
        '闭上眼睛呼吸三次，感受一下自己现在的状态。',
        '说出您此刻注意到的三样东西，看到、听到、闻到都算。',
        '写下这周您期待的一件事。',
        '定一个两分钟的计时器，不看屏幕，就这样坐一会儿。',
        '欣赏身边的一样小东西，比如一盆植物或您喜欢的杯子。',
        '想一件这周您做得好的事，向自己点点头。',
        '不开别的程序，从头到尾听完一首喜欢的歌。',
        '吸气数四下，呼气数六下，重复三次。',
        '下次遇到小小的烦心事，先呼吸一次再反应。',
        '记下最近让您笑出来的一件事。',
        '花一分钟留意一样让人愉快的东西：一种声音、一种气味或手边摸到的东西。',
        '想一个您喜爱的地方，在脑海里想象它三十秒。',
        '对一件小任务说一句“现在这样就够好了”，然后继续往下做。',
        '写一句话，记下一件让您感激的事。',
        '细细品味下一口饮品，留意它的味道。',
        '在两件事之间短暂休息一下，再开始下一件。',
        '今天留意一件结果比预想更好的事。',
        '用一个词说说您希望下午过得怎样。',
        '让头脑休息六十秒，然后回到下一件事。',
        '感受双脚踩在地面上，让自己稳下来一会儿。',
        '想起一件别人为您做过的好事，回味一下。',
        '记下一个以后想再想想的点子，然后先放下。',
        '整理桌上的一个小角落，一个就好。',
        '回复一条已经等了一段时间的消息。',
        '把明天最重要的事写在便利贴或笔记里。',
        '关掉不再需要的浏览器标签页。',
        '为同事最近做的一件事向对方道声谢。',
        '归档五封不再需要的旧邮件。',
        '给一个名字很乱的文件重新命名，方便以后找。',
        '清掉桌面上一两个零散的文件。',
        '删除一个已经没用的旧提醒。',
        '给一份常打开的文档加一个清楚的标题。',
        '在待办清单上划掉一件小事。',
        '退订一份您从来不读的订阅邮件。',
        '用软布擦一擦键盘或屏幕。',
        '把笔、笔记本和水放在顺手的地方。',
        '给未来的自己写个简短的便条，记下今天做到哪里了。',
        '挑出今天下午最重要的一件事，先做它。',
        '倒掉工位旁的回收箱或垃圾桶。',
        '更新一条进度记录，让大家看到事情进展到哪一步。',
        '整理一下下载文件夹，先挪走一小批文件。',
        '为一件您容易忘记的事设个提醒。',
        '关掉一个并不真正需要的通知。',
        '把一个您总要去搜的网页加入收藏夹。',
        '趁着记忆犹新，用两行字总结一下会议。',
        '问问某个例会能否稍微缩短一些。',
        '说出接下来一小时的唯一目标，并写下来。',
        '问问同事今天过得怎么样，并认真倾听。',
        '把一个有用的链接分享给可能感兴趣的人。',
        '向一位还没说过话的人打个招呼。',
        '给最近帮过您的人发一句简短的感谢。',
        '下次通话开始时，热情地向同事问好。',
        '问问同事这周有什么期待的事。',
        '看到别人有个小进展，向对方道声贺。',
        '约同事喝杯茶或咖啡，或打个电话，简单聊聊。',
        '具体地称赞同事做得好的一件事。',
        '记住一个常见面但还不认识的人的名字。',
        '把一个实用的小窍门分享给可能用得上的同事。',
        '请别人推荐一首歌、一部剧或一本书。',
        '关心一下最近比较安静的同事。',
        '如果有人看起来很忙，主动帮忙做一件小事。',
        '热情地向下一个遇到的人问好。',
        '把听到的一句对同事的好话转告给对方。',
        '问问同事这周什么让工作轻松了一些。',
        '给以前的同事发一条友好的消息。',
        '感谢那些让公共区域保持整洁顺畅的人。',
        '介绍两位可能会聊得来的同事互相认识。',
        '问问同事，交接时您怎样做能让对方更方便。',
        '和身边的人分享一个无伤大雅的小笑话。',
        '下次说“请”和“谢谢”时，多带一点温暖。',
        '问问同事工作之外喜欢做什么。',
        '下一个人跟您说话时，放下其他事，认真听完。',
    ),
    "done": (
        '很好，这件完成了。',
        '不错。完成一件事的感觉真好。',
        '做得好。开始下一件之前，先稍微休息一下。',
        '很好。完成的小事会积少成多。',
        '完成了。可以为此高兴一下。',
        '很好。这件可以从清单上划掉了。',
    ),
    "text": {
        HELP:
            """hello-world 会显示一句问候、每日一句和一件可以试试的小事。

在最后一个提示处，输入 plan 设定今天的计划，完成后输入 done，
输入 menu（或 m）查看选项。按 Enter 关闭；在任何问题处输入 q、x
或 close 也可关闭。在计划提示处，输入 same 可找回之前未完成的计划。
输入 done 后，会列出您最近完成的 3 个计划。菜单选项 1 显示全部，
选项 7 删除其中一个，选项 8 隐藏每日一句和小建议。在菜单中按 Enter 返回。
您也可以在运行 hello.cmd 时加上以下任一选项：
  --plain         只显示问候语
  --stats         显示这台电脑上保存的内容
  --reset         删除所有保存的内容（会先询问）
  --remind on     每天登录时打开一次（off 为关闭）
  --streak off    隐藏连续天数提示（on 为显示）
  --version       显示版本
  --check-content FILE
                  检查组织内容文件
  --help          显示此说明

退出代码：0 表示成功，1 表示命令失败或无法写入屏幕，
2 表示未知选项。

保存的记录只留在这台电脑上您的用户文件夹中，不会发送到任何地方。
能读取这台电脑文件的 IT 人员可以看到这些记录。""",
        MENU_HELP:
            """可以在最后一个提示处输入的词：
  done  将今天的计划标记为完成，然后询问下一个计划
  plan  设定或更改今天的计划
  menu  打开这些选项
  q     关闭窗口，按 Enter 也可以
在计划提示处，输入 same 可找回之前未完成的计划。
询问“您完成了吗？”时，n 表示还没有，您可以把这个计划
留到今天。在任何问题处输入 q 都可关闭。
在此菜单中，1 显示保存的内容，7 删除一个已完成的计划，
8 隐藏每日一句和小建议。
输入 m 可再次查看选项。所有内容都不会发送出去。""",
        SAVED_PLAN:
            '已保存。完成后请输入 done，否则下次打开时会询问您。',
        GREETING:
            '你好，世界！',
        'hello.cmd is in this folder:':
            'hello.cmd 位于此文件夹：',
        'Shortened to {n} characters.':
            '已缩短为 {n} 个字符。',
        'Your saved file was damaged, so hello-world set it aside as a backup copy and started fresh. Your earlier days and plan could not be read. Menu option 4 deletes the backup.':
            '您保存的文件已损坏，hello-world 已将其另存为备份并重新开始。之前的天数和计划无法读取。菜单选项 4 可删除该备份。',
        'Backup copy: ':
            '备份副本：',
        'In the folder: ':
            '所在文件夹：',
        'Sorry, "{shown}" is not one of the choices.':
            '抱歉，“{shown}”不是可选项。',
        'A plan needs a word or two, so nothing was saved.':
            '计划至少要写几个字，因此没有保存。',
        'The sign-in reminder works on Windows only.':
            '登录提醒仅适用于 Windows。',
        'Your organization has turned off opening at sign-in.':
            '您的组织已关闭“登录时打开”。',
        'The reminder cannot be set up from this folder.':
            '无法从此文件夹设置提醒。',
        'Could not set up the reminder.':
            '无法设置提醒。',
        'Done. hello-world will open once a day when you sign in.':
            '好了。hello-world 会在您每天登录时打开一次。',
        'To stop it, choose option 2 in the menu.':
            '要关闭它，请在菜单中选择选项 2。',
        'Could not turn off the sign-in reminder.':
            '无法关闭登录提醒。',
        'Done. The sign-in reminder is off.':
            '好了。登录提醒已关闭。',
        'Saved on this computer in:':
            '已保存在这台电脑上的以下位置：',
        'Saved in your own user folder on this computer.':
            '保存在这台电脑上您自己的用户文件夹中。',
        'Days you opened it in the last {days} days: {n} (last 7 days: {recent})':
            '最近 {days} 天内打开的天数：{n}（最近 7 天：{recent}）',
        'Times you marked a plan done: {n}':
            '将计划标记为完成的次数：{n}',
        'Your current plan: ':
            '当前计划：',
        'Earlier plan (for same): ':
            '之前的计划（供 same 使用）：',
        'Days-in-a-row message: shown.':
            '连续天数提示：显示。',
        'Days-in-a-row message: hidden.':
            '连续天数提示：隐藏。',
        'Opens by itself at sign-in: turned off by your organization.':
            '登录时自动打开：已被您的组织关闭。',
        'Opens by itself at sign-in: on.':
            '登录时自动打开：已开启。',
        'Opens by itself at sign-in: off.':
            '登录时自动打开：已关闭。',
        "It never leaves this computer. Others who can read this computer's files, such as IT staff, could read it.":
            '这些内容不会离开这台电脑。能读取这台电脑文件的人（例如 IT 人员）可以看到。',
        'After tidying, the file holds only this:':
            '整理后，文件中只有以下内容：',
        'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
            '删除这台电脑上保存的所有记录、日期和计划吗？（y 或 n，按 Enter 取消）> ',
        'Nothing was deleted.':
            '未删除任何内容。',
        'Could not delete everything.':
            '无法全部删除。',
        'Delete these yourself:':
            '请您手动删除以下文件：',
        'Could not list the folder, so backup copies may remain:':
            '无法列出文件夹内容，可能还有备份副本残留：',
        'Done. Everything saved was deleted.':
            '好了。所有保存的内容都已删除。',
        'Another open hello-world window cannot put it back.':
            '其他打开的 hello-world 窗口无法恢复这些内容。',
        'Close any other open hello-world window, or it may save its notes again.':
            '请关闭其他打开的 hello-world 窗口，否则它可能会再次保存记录。',
        'Everything saved was deleted in another window, so this was not saved.':
            '所有保存的内容已在另一个窗口中删除，因此这次没有保存。',
        'The other open window had also finished a plan.':
            '另一个打开的窗口也完成了一个计划。',
        'The other open window changed the plan, so its plan is kept.':
            '另一个打开的窗口更改了计划，因此以那个窗口的计划为准。',
        'Type plan at the last prompt to set one.':
            '在最后一个提示处输入 plan 即可设定计划。',
        'That looks like a command, not a plan, so nothing was saved.':
            '这看起来像命令，不像计划，因此没有保存。',
        'Type your plan, or press Enter to go back.':
            '请输入您的计划，或按 Enter 返回。',
        'Finished lately:':
            '最近完成：',
        'Your plan today: ':
            '今天的计划：',
        'Your plan from {date}: ':
            '{date} 的计划：',
        'Earlier plan: ':
            '之前的计划：',
        'Type the next plan, or Enter to close > ':
            '输入下一个计划，或按 Enter 关闭 > ',
        'Type the next plan, same to reuse the earlier plan, or Enter to close > ':
            '输入下一个计划，输入 same 沿用之前的计划，或按 Enter 关闭 > ',
        "Type today's plan, or Enter to keep it > ":
            '输入今天的计划，或按 Enter 保留现有计划 > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
            '输入今天的计划，输入 same 沿用之前的计划，或按 Enter 保留现有计划 > ',
        "Type today's plan, or Enter to go back > ":
            '输入今天的计划，或按 Enter 返回 > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
            '输入今天的计划，输入 same 沿用之前的计划，或按 Enter 返回 > ',
        'Closing.':
            '正在关闭。',
        'There is no earlier plan to reuse yet. Nothing changed.':
            '还没有之前的计划可沿用。未作更改。',
        'Nothing changed.':
            '未作更改。',
        'Could not save that on this computer. Your plan is unchanged.':
            '无法保存到这台电脑。您的计划保持不变。',
        'No finished plans are saved.':
            '还没有保存已完成的计划。',
        'Type the number to forget (1 to {n}), or Enter to keep them all > ':
            '输入要删除的编号（1 到 {n}），或按 Enter 全部保留 > ',
        'There is no number "{typed}" on the list. Type a number from 1 to {n}, or press Enter to keep them all.':
            '列表中没有编号“{typed}”。请输入 1 到 {n} 之间的数字，或按 Enter 全部保留。',
        'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
            '也从 same 中删除它吗？（y 或 n，按 Enter 保留给 same）> ',
        'Type y or n, or press Enter to keep it for same.':
            '请输入 y 或 n，或按 Enter 保留给 same。',
        'That plan was already forgotten. Nothing changed.':
            '该计划之前已删除。未作更改。',
        'Forgotten: ':
            '已删除：',
        'Same still has it.':
            '仍可用 same 找回。',
        'Could not save that on this computer. Nothing changed.':
            '无法保存到这台电脑。未作更改。',
        'Options':
            '选项',
        'Show what is saved on this computer':
            '显示这台电脑上保存的内容',
        'Open once a day at sign-in (turned off by your organization)':
            '每天登录时打开一次（已被您的组织关闭）',
        'Turn off: open once a day at sign-in (now on)':
            '关闭：每天登录时打开一次（当前已开启）',
        'Turn on: open once a day at sign-in (now off)':
            '开启：每天登录时打开一次（当前已关闭）',
        'Days-in-a-row message (hidden by your organization)':
            '连续天数提示（已被您的组织隐藏）',
        'Hide the days-in-a-row message (now shown)':
            '隐藏连续天数提示（当前显示）',
        'Show the days-in-a-row message (now hidden)':
            '显示连续天数提示（当前隐藏）',
        'Delete everything saved':
            '删除所有保存的内容',
        'Help':
            '帮助',
        "Set today's plan (turned off by your organization)":
            '设定今天的计划（已被您的组织关闭）',
        'Forget a finished plan (turned off by your organization)':
            '删除一个已完成的计划（已被您的组织关闭）',
        "Set or change today's plan":
            '设定或更改今天的计划',
        'Forget one finished plan':
            '删除一个已完成的计划',
        'Thought and tip (hidden by your organization)':
            '每日一句和小建议（已被您的组织隐藏）',
        'Hide the thought and tip (now shown)':
            '隐藏每日一句和小建议（当前显示）',
        'Show the thought and tip (now hidden)':
            '显示每日一句和小建议（当前隐藏）',
        '{date}: ':
            '{date}：',
        'Enter':
            'Enter',
        'Back to the last prompt':
            '返回最后一个提示',
        'Choose 1 to 11, or Enter to go back > ':
            '请选择 1 到 11，或按 Enter 返回 > ',
        'Choose 1 to 11, m to list the options, or Enter to go back > ':
            '请选择 1 到 11，输入 m 列出选项，或按 Enter 返回 > ',
        'The saved file could not be read just now, so this may be out of date.':
            '暂时无法读取保存的文件，因此这些内容可能不是最新的。',
        'Type full to see the whole file, or Enter to go on > ':
            '输入 full 查看完整文件，或按 Enter 继续 > ',
        'Could not save that choice on this computer.':
            '无法将该选择保存到这台电脑。',
        'Your organization has hidden the days-in-a-row message.':
            '您的组织已隐藏连续天数提示。',
        'Done. The days-in-a-row message is on.':
            '好了。连续天数提示已开启。',
        'Done. The days-in-a-row message is off.':
            '好了。连续天数提示已关闭。',
        'Plans are turned off by your organization.':
            '您的组织已关闭计划功能。',
        'Your organization has hidden the thought and tip.':
            '您的组织已隐藏每日一句和小建议。',
        'Done. The thought and tip are on.':
            '好了。每日一句和小建议已开启。',
        'Done. The thought and tip are off.':
            '好了。每日一句和小建议已关闭。',
        'Type 1 to 11, or press Enter to go back.':
            '请输入 1 到 11，或按 Enter 返回。',
        'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
            '要让它在您每天登录时打开一次吗？（y 或 n，按 Enter 暂不设置）> ',
        'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
            '要让它在您每天登录时打开一次，问问您的计划吗？（y 或 n，按 Enter 暂不设置）> ',
        'Type y or n, or press Enter for not now.':
            '请输入 y 或 n，或按 Enter 暂不设置。',
        'That was not understood. It will ask again on a later visit.':
            '没有理解您的输入。下次打开时会再询问。',
        'It will ask again on a later visit. Menu option 2 also turns it on.':
            '下次打开时会再询问。菜单选项 2 也可以开启。',
        'No problem. Menu option 2 turns it on later.':
            '没问题。之后可以用菜单选项 2 开启。',
        "Okay. It won't ask again. Menu option 2 turns it on.":
            '好的。不会再询问。菜单选项 2 可以开启。',
        'Okay. It will ask again on a later visit. Type n to stop it.':
            '好的。下次打开时会再询问。输入 n 可不再询问。',
        'When did you finish it?':
            '您是什么时候完成的？',
        'Today':
            '今天',
        'Type a number from 1 to {n}, or Enter for 1 > ':
            '请输入 1 到 {n} 之间的数字，或按 Enter 选 1 > ',
        'Type a number from 1 to {n}, or press Enter.':
            '请输入 1 到 {n} 之间的数字，或按 Enter。',
        'That looks like more than one thing. Finishing the first part still counts.':
            '这看起来不止一件事。完成第一部分也算数。',
        'There is no plan to mark as done. Type plan to set one.':
            '没有可标记为完成的计划。输入 plan 设定一个。',
        'Could not save that on this computer. The plan is still open.':
            '无法保存到这台电脑。该计划仍未完成。',
        'Your plan from over two weeks ago was put away. Type same at the plan prompt to bring it back.':
            '您两周多以前的计划已收起。在计划提示处输入 same 可找回。',
        "Press Enter at each question to skip it, and once more to close. That's it.":
            '在每个问题处按 Enter 可跳过，再按一次即可关闭。就这么简单。',
        'Welcome.':
            '欢迎使用。',
        'Each day you get one thought and one small thing to try, the same for everyone.':
            '每天您会看到一句话和一件可以试试的小事，大家看到的都一样。',
        'If you type a plan, it asks next time how it went. Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks.':
            '如果您输入计划，下次会问您进展如何。您的记录只保存在这台电脑上，不会发送到任何地方。和其他工作文件一样，这些记录并不保密，所以请只写日常事务。',
        'Type menu at the end for the options.':
            '最后输入 menu 可查看选项。',
        'Welcome back. Glad you are here.':
            '欢迎回来，很高兴见到您。',
        'You have opened this {row} days in a row. Nice to see you.':
            '您已连续 {row} 天打开 hello-world。很高兴见到您。',
        'Last time you planned: ':
            '上次的计划：',
        'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
            '您完成了吗？（y 表示完成，n 表示还没有，按 Enter 跳过）> ',
        'Type y or n, or press Enter to skip.':
            '请输入 y 或 n，或按 Enter 跳过。',
        'Could not save that on this computer. Your answer was not counted.':
            '无法保存到这台电脑。您的回答未被记录。',
        'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
            '没关系。今天继续保留吗？（y 或 n，按 Enter 保留）> ',
        'Type y to keep it, n to clear it, or press Enter to keep it.':
            '输入 y 保留，n 清除，或按 Enter 保留。',
        'Cleared. Type same at a plan prompt if you want it back.':
            '已清除。如需找回，请在计划提示处输入 same。',
        'Kept for today.':
            '今天继续保留。',
        'That was not understood. Your plan is left as it was.':
            '没有理解您的输入。您的计划保持不变。',
        'Your plan is still open.':
            '您的计划仍未完成。',
        'Thought for today:':
            '今日一句：',
        'Try this today:':
            '今天试试：',
        'Your plan for today: ':
            '您今天的计划：',
        'Still open since {date}:':
            '自 {date} 起仍未完成：',
        '(Enter to skip)':
            '（按 Enter 跳过）',
        '(A plan typed here replaces the old one. Enter to skip)':
            '（在这里输入的计划会替换旧计划。按 Enter 跳过）',
        '(Type same to reuse it, or Enter to skip)':
            '（输入 same 沿用，或按 Enter 跳过）',
        'What is one thing you want to get done today?':
            '今天最想完成的一件事是什么？',
        'There is no earlier plan to reuse yet. Nothing was saved.':
            '还没有之前的计划可沿用。未保存任何内容。',
        'Your notes could not be saved on this computer. This screen still works.':
            '无法在这台电脑上保存您的记录。此界面仍可正常使用。',
        'Type menu, or Enter to close > ':
            '输入 menu，或按 Enter 关闭 > ',
        'Type done, plan or menu, or Enter to close > ':
            '输入 done、plan 或 menu，或按 Enter 关闭 > ',
        'Type plan or menu, or Enter to close > ':
            '输入 plan 或 menu，或按 Enter 关闭 > ',
        'Type done, plan or menu, or press Enter to close.':
            '请输入 done、plan 或 menu，或按 Enter 关闭。',
        'Type plan or menu, or press Enter to close.':
            '请输入 plan 或 menu，或按 Enter 关闭。',
        "The saved file can't be read right now, or it is damaged.":
            '暂时无法读取保存的文件，或文件已损坏。',
        'Nothing was changed. Saved in: ':
            '未作任何更改。保存位置：',
        'Deleting saved notes needs a person at the keyboard.':
            '删除保存的记录需要有人在键盘前操作。',
        '{option} needs on or off. Here are the options.':
            '{option} 需要加上 on 或 off。以下是可用选项。',
        'Unknown option: {option}. Here are the options.':
            '未知选项：{option}。以下是可用选项。',
        '&Done':
            '完成(&D)',
        '&Not yet':
            '还没有(&N)',
        'S&kip':
            '跳过(&K)',
        '&Save':
            '保存(&S)',
        '&I did it':
            '我完成了(&I)',
        '&Options':
            '选项(&O)',
        'Close':
            '关闭',
        'Not today':
            '今天先不',
        'Did you do it?':
            '您完成了吗？',
        'Done. A reminder comes when you sign in, if there is a plan to ask about.':
            '好了。登录时如果有计划需要询问，会提醒您。',
        'Done. The Start menu opens a window with buttons.':
            '好了。开始菜单将打开带按钮的窗口。',
        'Done. The Start menu opens this text screen.':
            '好了。开始菜单将打开此文本界面。',
        'More options':
            '更多选项',
        'Remind me when I sign in':
            '登录时提醒我',
        'Show the thought and tip':
            '显示每日一句和小建议',
        'Type your plan in the box.':
            '请在框中输入您的计划。',
        'Use a window with buttons (now this text screen)':
            '使用带按钮的窗口（当前为文本界面）',
        'Use the text screen':
            '使用文本界面',
        'Use this text screen (now a window with buttons)':
            '使用此文本界面（当前为带按钮的窗口）',
        'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
            '要在登录时提醒您吗？提醒会显示您上次的计划，点一下就能回答。您可以在“选项”中关闭。',
        'Window or text screen (set by your organization)':
            '窗口或文本界面（由您的组织设定）',
        'Your organization has set hello-world to open as a text screen.':
            '您的组织已将 hello-world 设为以文本界面打开。',
        'Saved.':
            '已保存。',
        'Save your plan before closing?':
            '关闭前保存您的计划吗？',
        'Delete all saved notes, dates and plans on this computer?':
            '删除这台电脑上保存的所有记录、日期和计划吗？',
        'Turn off: reminder when you sign in (now on)':
            '关闭：登录时提醒（当前已开启）',
        'Turn on: reminder when you sign in (now off)':
            '开启：登录时提醒（当前已关闭）',
        'Reminder when you sign in (turned off by your organization)':
            '登录时提醒（已被您的组织关闭）',
        'Reminder when you sign in: on.':
            '登录时提醒：已开启。',
        'Reminder when you sign in: off.':
            '登录时提醒：已关闭。',
        'Reminder when you sign in: turned off by your organization.':
            '登录时提醒：已被您的组织关闭。',
        'Show the days-in-a-row message':
            '显示连续天数提示',
        'Done. The thought and tip show next time you open hello-world.':
            '好了。下次打开 hello-world 时会显示每日一句和小建议。',
        "Clear today's plan?":
            '清除今天的计划吗？',
        'Next plan, if you want one:':
            '如果需要，可以写下一个计划：',
        'A few things? Put ; between them.':
            '有好几件事？用 ; 隔开。',
        'A plan can be up to {n} characters.':
            '计划最多 {n} 个字符。',
        'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
            '这些都完成了吗？（y 表示全部完成，n 表示还没有，或输入已完成的编号，按 Enter 跳过）> ',
        'Last time you planned:':
            '上次的计划：',
        'The rest is kept for today.':
            '其余的今天继续保留。',
        'Tick the ones you did, then click Done. With none ticked, Done means all of them.':
            '勾选已完成的事项，然后点击“完成”。如果一项都没勾选，“完成”表示全部完成。',
        'Type y for all, n for not yet, or the numbers you did, such as 1 3. Enter skips.':
            '输入 y 表示全部完成，n 表示还没有，或输入已完成的编号，例如 1 3。按 Enter 跳过。',
        'Your settings were kept.':
            '您的设置已保留。',
        'Language (set by your organization)':
            '语言（由您的组织设定）',
        'Language (now {name})':
            '语言（当前：{name}）',
        'following Windows':
            '跟随 Windows',
        'Your organization shows hello-world in English.':
            '您的组织已将 hello-world 设为英文显示。',
        'Follow Windows':
            '跟随 Windows',
        'Type a number from 1 to {n}, or Enter to keep it > ':
            '请输入 1 到 {n} 之间的数字，或按 Enter 保持不变 > ',
        'Done. The new language shows next time you open hello-world.':
            '好了。下次打开 hello-world 时将显示新语言。',
        'Language...':
            '语言...',
        'Hello, {name}!':
            '{name}，您好！',
        'One thing to get done today? Open hello-world to plan it.':
            '今天有什么想完成的事吗？打开 hello-world 写下计划吧。',
        '&Open':
            '打开(&O)',
        'Reminder settings...':
            '提醒设置...',
        'Greet me by name':
            '问候时称呼我的名字',
        'At sign-in':
            '登录时',
        'At {at}':
            '每天 {at}',
        'Also on days with no plan':
            '没有计划的日子也提醒',
        'Open hello-world after I answer':
            '回答后打开 hello-world',
        'Not on weekends':
            '周末不提醒',
        'Done. A reminder comes at {at} each day, if there is a plan to ask about.':
            '好了。如果有计划需要询问，每天 {at} 会提醒您。',
        'Send feedback...':
            '发送反馈...',
        '"holidays" must be a list of at most {n} dates.':
            '"holidays" 必须是最多包含 {n} 个日期的列表。',
        '"title" must be 1 to 40 characters of plain text, with no link or address.':
            '"title" 必须是 1 到 40 个字符的纯文本，不能包含链接或地址。',
        '"{list}" must be a list of {low} to {high} lines.':
            '"{list}" 必须是包含 {low} 到 {high} 行的列表。',
        "Can't read {path}: {error}":
            '无法读取 {path}：{error}',
        'Could not save that on this computer.':
            '无法保存到这台电脑。',
        'Days you opened hello-world: {n}':
            '打开 hello-world 的天数：{n}',
        'Keep a longer history':
            '保留更长的历史记录',
        'Keep my numbers':
            '保存我的统计数据',
        'Longest run of days: {n}':
            '最长连续天数：{n}',
        "Mark today's plan done":
            '将今天的计划标记为完成',
        "Mark today's plan done (plans are turned off)":
            '将今天的计划标记为完成（计划功能已关闭）',
        'My numbers are off. Turn them on under Options, or with --set numbers on.':
            '“我的统计”已关闭。可在“选项”中开启，或使用 --set numbers on。',
        'My numbers...':
            '我的统计...',
        'Nothing finished yet this week. That is fine.':
            '本周还没有完成任何事。没关系。',
        'OK: {thoughts} thoughts and {tips} tips.':
            '检查通过：共 {thoughts} 条想法、{tips} 条小建议。',
        'Plans finished: {n}':
            '已完成的计划：{n}',
        'Save my plans to a file':
            '将我的计划保存到文件',
        'Saved to {path}':
            '已保存到 {path}',
        "The file isn't valid JSON, or is over 200,000 characters.":
            '该文件不是有效的 JSON，或超过 200,000 个字符。',
        'The file must hold an object with two lists, "thoughts" and "tips", and may add "holidays" and "title".':
            '该文件必须包含一个对象，其中有 "thoughts" 和 "tips" 两个列表，还可以添加 "holidays" 和 "title"。',
        'This week you finished {n}:':
            '本周您完成了 {n} 件：',
        'This week...':
            '本周...',
        'holidays line {line} is not a date like 2026-12-25.':
            'holidays 第 {line} 行不是类似 2026-12-25 的日期。',
        '{list} line {line} has a date.':
            '{list} 第 {line} 行包含日期。',
        '{list} line {line} has a link or an address.':
            '{list} 第 {line} 行包含链接或地址。',
        '{list} line {line} has control characters or extra spaces.':
            '{list} 第 {line} 行包含控制字符或多余空格。',
        '{list} line {line} is not text.':
            '{list} 第 {line} 行不是文本。',
        '{list} line {line} must be {low} to {high} characters long.':
            '{list} 第 {line} 行的长度必须为 {low} 到 {high} 个字符。',
    },
}

# ---- Japanese ----

LANGUAGES["ja"] = {
    "days": ('月', '火', '水', '木', '金', '土', '日'),
    "months": ('1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'),
    "date": '{year}年{month}{d}日（{day}）',
    "thoughts": (
        '後回しにしている文書を一つ開いて、最初の段落だけ読んでみましょう。',
        '10分だけでも、始めたことに変わりはありません。次の10分もたいてい楽になります。',
        '今日、計画のすべてはいりません。無理のない最初の一歩があれば十分です。',
        '不格好な最初の一文を書いてみましょう。あとで直せる、形のあるものが手に入ります。',
        '机の一角だけ片付けてみると、ほかの場所まで落ち着いて見えてきます。',
        'リストでいちばん小さなタスクを選んで、ほかを見る前に終わらせましょう。',
        '静かな朝に不格好に始めるほうが、来るかわからない完璧な瞬間を待つよりずっといいです。',
        '最初の一歩をカレンダーに入れて、取り組む時間を確保しましょう。',
        '大きなプロジェクトも、ほとんどは数時間の作業の積み重ねです。まずは午後ひとつ分を目指しましょう。',
        '次にやることを一つだけ声に出して、残りのリストには順番を待ってもらいましょう。',
        '思うようにペースが上がらない日もあります。そのペースでも、ちゃんと前に進んでいます。',
        '入ったばかりの同僚に声をかけるように、自分にもやさしく話しかけてみましょう。',
        '何年もやってきたことでも、まだ学んでいる途中でかまいません。',
        '朝がいまひとつでも、午後まで決まるわけではありません。昼食のあとに仕切り直せます。',
        '疲れは失敗ではなく、ひとつの合図です。予定を調整して、無理せず続けましょう。',
        '人にはすぐ向けられる思いやりを、自分にも向けてあげましょう。',
        '進歩はしばらく何も見えず、ある日突然、仕上がった1ページとして現れたりします。',
        '2回読んでやっとわかることがあっても、問題ありません。',
        '準備ができたと感じなくても大丈夫です。緊張しながらでも、やっていることに変わりはありません。',
        '今日のベストが昨日より小さくても、それでかまいません。',
        '使っていないタブを閉じましょう。数分で集中しやすくなります。',
        'タスク一つ、ウィンドウ一つ、25分。静かな時間でどこまで進めるか試してみましょう。',
        'ふと浮かんだ考えはメモしておいて、やっていたことに戻りましょう。',
        'できれば1時間スマートフォンの通知を切って、仕事に集中してみましょう。',
        '今日をいい日にする一つのことを決めて、そのための時間を確保しましょう。',
        '一つずつ片付けるほうが、感じているより速く進むものです。',
        '散らかった20項目のリストより、すっきりした3項目のリストのほうが役に立ちます。',
        '気が散ったことに気づいたら、自分を責めずに、そっと戻しましょう。',
        'いちばん難しいタスクは、元気がいちばんある時間帯に。朝一番でなくてもかまいません。',
        'ヘッドホンをつけ、飲み物を用意し、ドアを閉める。場を整えれば、集中はあとからついてきます。',
        '5分だけ画面から離れましょう。戻ったとき、少し頭がすっきりしています。',
        '今日は机を離れて昼食をとりましょう。受信トレイは、昼食のあいだくらい待ってくれます。',
        '建物のまわりを少し歩くのも、頭にとっては立派な仕事です。',
        '忙しい午後でも、1分画面から離れるのはいい時間の使い方です。',
        '肩を伸ばして、歯の食いしばりをゆるめましょう。何時間も力が入っていたかもしれません。',
        'できれば今夜は定時で帰りましょう。明日の自分が、今夜の時間に感謝するはずです。',
        '休むことも仕事のうちです。疲れていると、同じミスを繰り返しやすくなります。',
        '少しのあいだ目を休めて、肩の力を抜きましょう。',
        'しっかり休憩をとると、一日の後半が新しいスタートのように感じられます。',
        '夜の時間は自分のために。夜9時に対応しなければならないメールはありません。',
        '頼まれてもいないのに誰かがしてくれた小さなことに、今日はお礼を伝えましょう。',
        'たいていの人は、見えないところで多くを抱えながら精いっぱいやっています。',
        '同僚のお茶やコーヒーの好みを覚えておきましょう。ささやかな気づかいになります。',
        '誰かがそっけなくても、自分への評価ではなく、その人が大変な一日なのだと考えましょう。',
        'ドアを押さえる、お菓子を分ける、相手の話を最後まで聞く。そんな小さなことを大切にしましょう。',
        'ちょっとしたあいさつと週末の話が、朝いちばんの楽しみになることもあります。',
        '新しく来た人が当たり前のことを聞いてきたら、自分も昔同じことを聞いたと思い出しましょう。',
        'チームメイトのアイデアで仕事が良くなったら、そのことを口に出して伝えましょう。',
        'メッセージの返信に、少しだけ温かみを添えましょう。手間はかからず、やさしく届きます。',
        '最近会議で口数の少ない同僚に、調子はどうか声をかけてみましょう。',
        '新しいことを始める前に、もうすぐ終わることを仕上げましょう。',
        '完璧でも終わっていないものより、十分な出来で終わったもののほうが役に立つことが多いです。',
        '今日はやりかけのことを一つ片付けて、そのあとのちょっとした安心感を味わいましょう。',
        '最後の10%は、丁寧な数分で済むことがよくあります。今日はその数分を使いましょう。',
        '下書きに残っているメールを送りましょう。たぶん、そのままで大丈夫です。',
        '完了にして、ひと息ついて、終わったことを喜びましょう。',
        '終わった小さなことは、途中で止まった大きなことより価値があります。',
        'ログオフする前に、明日の最初の一歩をメモしておきましょう。覚えておかなくて済みます。',
        'もう一度だけ読んで、見つけたところを直したら、送信しましょう。',
        '一つきちんと仕上げて一日を終えると、夜の気分が軽くなります。',
        '早めに質問すれば、あとで一人で1時間悩まずに済むことが多いです。',
        'たいていの人は、知っていることを聞かれるとうれしいものです。謝らずに聞いてみましょう。',
        '「行き詰まっています」は、同僚が手を貸しやすい、わかりやすくて役に立つ一言です。',
        '必要なことはわかりやすい言葉で頼みましょう。相手が「いいですよ」と言いやすくなります。',
        '一人で問題をにらむより、二人で見るほうが早く解決することがよくあります。',
        '手を借りるのは迷惑ではありません。チームの一員なのですから。',
        '具体的に質問すれば、相手も具体的に答えられます。',
        '指示がわかりにくいときに確認するのも、仕事をきちんとすることの一部です。',
        'できるときは手を貸し、必要なときは手を借りましょう。どちらも慣れるほど楽になります。',
        'これを前に解決した人が、きっと社内のどこかにいます。探しに行ってみましょう。',
        '今週わかったことを、小さくメモしておきましょう。思っている以上にたまっていきます。',
        '新しいことに初心者として取り組むのは、まだ成長を続けている証拠です。',
        '尊敬する同僚が難しい電話にどう対応しているか見て、一つ取り入れてみましょう。',
        '休憩中に役立つページを1ページ読めたら、それだけで頭にとってはいい一日です。',
        '誰かに作業を説明すると、意外なほど自分の理解も深まります。',
        '「まだわかりません」と言って、それから調べに行けば大丈夫です。',
        '慣れないシステムは、何度か使うまでは誰にとってもわかりにくいものです。',
        '経験のある人に、どうやって覚えたのか聞いてみましょう。たいてい安心できる答えが返ってきます。',
        'スキルは繰り返しで身につきます。小さなことを繰り返して、楽にできるようにしましょう。',
        'ありふれた作業も、少し興味を持ってみると、おもしろくなることがあります。',
        '早く見つけたミスは、直せば済みます。そして、ほとんどのミスは早く見つかります。',
        '直して、知らせるべき人に伝えたら、あとは気持ちが落ち着くのを待ちましょう。',
        '仕事のミスのほとんどは、1週間もすれば、その場で感じたより小さく思えます。',
        '一度のミスで、これまでの何年もの丁寧な仕事が消えるわけではありません。',
        '何かがうまくいかなかったら、人より先に、まずやり方を見直しましょう。',
        'まわりの誰もが、少なくとも一度はメールを送る相手を間違えています。',
        'ミスから学べることを一つだけ受け取って、残りは置いていきましょう。',
        'ミスを素直に認めるほうが、一度もミスしないことより信頼されることが多いものです。',
        '慎重な人にも、うっかりが続く日はあります。夕方には過ぎていきます。',
        '今日の小さなつまずきのほとんどは、来月には覚えていないでしょう。',
        '大きなトラブルのない静かな一日は、誰も何も言わなくても、いい一日です。',
        '温かいマグカップ、片付いた受信トレイ、静かな1分。小さな楽しみに目を向けましょう。',
        '毎日大きな成果がなくてもかまいません。穏やかに着実に進めるのも、立派な働き方です。',
        '会議が5分早く終わったら、その時間は好きに使いましょう。',
        'ありふれた一日をきちんと過ごせたら、それはひそかに誇っていいことです。',
        'いい仕事ほど、外からは目立たないことがあります。それでいいのです。',
        '気持ちのいい午後は、成果を気にせず、そのまま楽しみましょう。',
        '最初のコーヒーやいつもの顔ぶれなど、一日の小さな習慣にも目を向けてみましょう。',
        '今日も仕事に向き合い、自分の分を果たしました。それで十分です。',
        '今夜、今日うまくいったことを一つ思い出してみましょう。',
        'タスクの合間の静かな1分は、むだではありません。次のタスクをうまく始めるための時間です。',
    ),
    "tips": (
        '画面から離れて、水を一杯ゆっくり飲みましょう。',
        '肩をゆっくり5回、後ろに回しましょう。',
        '20秒間、目を休めましょう。遠くを見るか、目を閉じます。',
        '座ったままでも立っても、腕を頭の上に伸ばして深呼吸しましょう。',
        '行ける範囲でいちばん遠い部屋か窓まで行って、戻ってきましょう。',
        '姿勢を確かめて、肩を耳から離すように下ろしましょう。',
        '無理のない範囲で、首をゆっくり左右に回しましょう。',
        '手を10回、閉じたり開いたりして、指をほぐしましょう。',
        'いちばんよく開く文書をピン留めして、ワンクリックで開けるようにしましょう。',
        '歩いてでも車いすでも、自分に合った方法で少し外に出てみましょう。',
        '温かい飲み物か冷たい飲み物を用意して、画面から離れて楽しみましょう。',
        '景色や音、手ざわりなど、落ち着くものに意識を向けてみましょう。',
        '途中で止まっているタスクに、次の一歩を書き足しましょう。',
        '両足を床につけて、座ったままか立ったままで背筋を伸ばし、10回呼吸しましょう。',
        '流し読みしかしていないグループ チャットを一つミュートしましょう。',
        '少しのあいだ、あごの力を抜いて、額をゆるめましょう。',
        '今日の気分に合った動き方で、2分間体を動かしましょう。',
        '先延ばしにしているタスクのために、カレンダーに15分の枠を入れましょう。',
        '椅子、画面、キーボードのどれか一つを調整して、少し楽にしましょう。',
        'できれば、次の会議には少し遠回りして向かいましょう。',
        '何度も書いているメールを一つ、テンプレートとして保存しましょう。',
        'いちばんよく使うプログラムのショートカット キーを一つ覚えましょう。',
        '次のコーヒーやお茶の前に、水をコップ一杯飲みましょう。',
        '肩を耳まで持ち上げてから、すとんと力を抜きましょう。',
        '外に出るか窓を開けて、1分間新鮮な空気を吸いましょう。',
        'ゆっくり5回呼吸しましょう。吐く息を少しずつ長くします。',
        '次のメッセージを開く前に、1分間静かにひと息つきましょう。',
        '今日ここまでにあった、いいことを一つ書き留めましょう。',
        '目を閉じて3回呼吸し、今の気分を感じてみましょう。',
        '今気づいたことを三つ挙げてみましょう。見えるもの、聞こえるもの、何でもかまいません。',
        '今週楽しみにしていることを一つ書き出しましょう。',
        'タイマーを2分にセットして、画面を見ずにただ座ってみましょう。',
        '植物やお気に入りのマグカップなど、近くの小さなものを楽しみましょう。',
        '今週うまくできたことを一つ思い出して、自分をほめましょう。',
        '好きな曲を一曲、ほかに何も開かずに最初から最後まで聴きましょう。',
        '4つ数えて吸い、6つ数えて吐く。これを3回繰り返しましょう。',
        '次にちょっとイラッとしたら、反応する前にひと呼吸おきましょう。',
        '最近笑ったことを一つメモしましょう。',
        '1分間、音や香り、手ざわりなど、心地よいものに意識を向けましょう。',
        '好きな場所を思い出して、30秒間思い浮かべましょう。',
        '小さなタスクを一つ「今はこれで十分」と区切って、次に進みましょう。',
        '感謝していることを一文で書いてみましょう。',
        '次のひと口をゆっくり味わってみましょう。',
        '二つのタスクのあいだに、短い休憩をはさみましょう。',
        '今日、思っていたよりうまくいくことを一つ探してみましょう。',
        '午後をどんな気分で過ごしたいか、ひとことで決めてみましょう。',
        '60秒間頭を休めてから、次のタスクに戻りましょう。',
        '床についた足を感じて、少しのあいだ落ち着きましょう。',
        '誰かがしてくれた親切を一つ思い出して、その思い出を味わいましょう。',
        'あとで見直したいアイデアを一つメモして、いったん置いておきましょう。',
        '机の小さな一角を片付けましょう。一か所だけで大丈夫です。',
        'しばらく返信していないメッセージに、一つ返信しましょう。',
        '明日いちばんのタスクを、付箋かメモに書いておきましょう。',
        'もう使わないブラウザーのタブを閉じましょう。',
        '最近何かをしてくれた同僚にお礼を言いましょう。',
        'もう要らない古いメールを5通アーカイブしましょう。',
        'わかりにくい名前のファイルを一つ名前変更して、あとで見つけやすくしましょう。',
        'デスクトップに散らばったファイルを一つか二つ片付けましょう。',
        'もう必要のない古いリマインダーを一つ削除しましょう。',
        'よく開く文書に、わかりやすいタイトルを付けましょう。',
        'ToDo リストの小さな項目を一つ消しましょう。',
        '読んでいないメール マガジンの配信を一つ停止しましょう。',
        'キーボードか画面を柔らかい布でふきましょう。',
        'ペン、ノート、水を手の届くところに置きましょう。',
        '今日どこまで進んだか、未来の自分に短いメモを残しましょう。',
        '今日の午後いちばん大事なタスクを一つ選んで、最初に取りかかりましょう。',
        '机のそばのごみ箱を空にしましょう。',
        '進捗メモを一つ更新して、ほかの人にも状況がわかるようにしましょう。',
        'ダウンロード フォルダーのファイルを、いくつか移動して整理しましょう。',
        '忘れがちなことを一つ、リマインダーに設定しましょう。',
        'あまり必要のない通知を一つオフにしましょう。',
        'いつも検索しているページを一つブックマークしましょう。',
        '記憶が新しいうちに、会議の内容を2行でまとめましょう。',
        '定例会議を一つ、少し短くできないか相談してみましょう。',
        'この1時間の目標を一つ決めて、書き出しましょう。',
        '同僚に今日の調子を聞いて、しっかり耳を傾けましょう。',
        '役に立つリンクを、喜んでくれそうな人に共有しましょう。',
        'まだ話したことのない人にあいさつしましょう。',
        '最近助けてくれた人に、短いお礼のメッセージを送りましょう。',
        '次の通話の始めに、同僚に温かくあいさつしましょう。',
        'チームメイトに、今週楽しみにしていることを聞いてみましょう。',
        '誰かの小さな成功に気づいたら、声をかけてお祝いしましょう。',
        'お茶やコーヒー、または通話で、同僚を少しのおしゃべりに誘ってみましょう。',
        '同僚がうまくやったことを、具体的にほめましょう。',
        'よく見かけるけれど、まだ名前を知らない人の名前を覚えましょう。',
        '役に立ちそうなコツを、必要としていそうなチームメイトに教えましょう。',
        'おすすめの曲や番組、本を誰かに聞いてみましょう。',
        '最近口数の少ない同僚に、声をかけてみましょう。',
        '忙しそうな人がいたら、小さなことを一つ手伝うと申し出ましょう。',
        '次に会う人に、笑顔であいさつしましょう。',
        '同僚をほめる言葉を耳にしたら、本人に伝えましょう。',
        '同僚に、今週何があって楽になったか聞いてみましょう。',
        '以前一緒に働いていた人に、気軽なメッセージを送りましょう。',
        '共有スペースをいつも整えてくれている人にお礼を言いましょう。',
        '気が合いそうな同僚どうしを紹介しましょう。',
        '引き継ぎをもっと楽にするにはどうしたらいいか、チームメイトに聞いてみましょう。',
        '近くの人と、ちょっとした軽い冗談を言い合いましょう。',
        '次の「お願いします」と「ありがとう」に、少しだけ温かさを込めましょう。',
        '同僚に、仕事以外で楽しんでいることを聞いてみましょう。',
        '次に話しかけてきた人の話を、ほかのことをせずにしっかり聞きましょう。',
    ),
    "done": (
        'よかったです。これで一つ終わりました。',
        'いいですね。何かを終えるのは気持ちのいいものです。',
        'お疲れさまでした。次に取りかかる前に、少し休みましょう。',
        'いいですね。小さな完了が積み重なっていきます。',
        'これで完了です。ちょっと誇らしく思っていいですよ。',
        'よかったです。リストから一つ消えました。',
    ),
    "text": {
        HELP:
            """hello-world は、あいさつと今日のひとこと、ちょっと試してみることを表示します。

最後の入力欄では、plan で今日の予定を設定し、終わったら done と入力します。
menu（または m）でオプションを開きます。Enter で閉じます。q、x、close は
どの質問からでも閉じます。予定の入力欄で same と入力すると、終わっていない
前の予定を呼び戻せます。done のあとには、最近終えた予定を3件表示します。
メニューの1ですべて表示、7で1件を削除、8でひとこととヒントを非表示に
できます。メニューでは Enter で戻ります。
hello.cmd は次のオプションを付けて実行することもできます。
  --plain         あいさつだけを英語で表示
  --stats         このコンピューターに保存されている内容を表示
  --reset         保存内容をすべて削除（実行前に確認）
  --remind on     サインイン時に1日1回開く（off で停止）
  --streak off    連続日数のメッセージを非表示（on で表示）
  --version       バージョンを表示
  --check-content FILE
                  組織のコンテンツ ファイルをチェック
  --help          このテキストを表示

終了コード: 0 は成功、1 はコマンドの失敗または画面に書き込めなかった場合、
2 は不明なオプションです。

保存したメモは、このコンピューターのユーザー フォルダーに残ります。どこにも
送信されません。ただし、このコンピューターのファイルを読める IT 担当者は
読むことができます。""",
        MENU_HELP:
            """最後の入力欄で使える言葉:
  done  今日の予定を完了にして、次の予定をたずねます
  plan  今日の予定を設定・変更します
  menu  このオプションを開きます
  q     ウィンドウを閉じます（Enter でも閉じます）
予定の入力欄で same と入力すると、終わっていない前の予定を呼び戻せます。
「できましたか？」と聞かれたときの n は「まだ」の意味で、予定を今日に
持ち越せます。q はどの質問からでも閉じます。
このメニューでは、1で保存内容を表示、7で終えた予定を1件削除、
8でひとこととヒントを非表示にします。
m と入力すると、オプションをもう一度表示します。データはどこにも送信されません。""",
        SAVED_PLAN:
            '保存しました。終わったら done と入力してください。入力しなくても、次に開いたときにたずねます。',
        GREETING:
            'こんにちは、世界！',
        'hello.cmd is in this folder:':
            'hello.cmd はこのフォルダーにあります:',
        'Shortened to {n} characters.':
            '{n}文字に短くしました。',
        'Your saved file was damaged, so hello-world set it aside as a backup copy and started fresh. Your earlier days and plan could not be read. Menu option 4 deletes the backup.':
            '保存ファイルが壊れていたため、hello-world はバックアップとして別に保存し、新しく始めました。これまでの日数と予定は読み込めませんでした。バックアップはメニューの4で削除できます。',
        'Backup copy: ':
            'バックアップ: ',
        'In the folder: ':
            'フォルダー: ',
        'Sorry, "{shown}" is not one of the choices.':
            'すみません、「{shown}」は選択肢にありません。',
        'A plan needs a word or two, so nothing was saved.':
            '予定が短すぎるため、保存しませんでした。',
        'The sign-in reminder works on Windows only.':
            'サインイン時のリマインダーは Windows でのみ使えます。',
        'Your organization has turned off opening at sign-in.':
            'サインイン時に開く機能は、組織の設定でオフになっています。',
        'The reminder cannot be set up from this folder.':
            'このフォルダーからはリマインダーを設定できません。',
        'Could not set up the reminder.':
            'リマインダーを設定できませんでした。',
        'Done. hello-world will open once a day when you sign in.':
            '設定しました。hello-world はサインイン時に1日1回開きます。',
        'To stop it, choose option 2 in the menu.':
            '止めるには、メニューの2を選んでください。',
        'Could not turn off the sign-in reminder.':
            'サインイン時のリマインダーをオフにできませんでした。',
        'Done. The sign-in reminder is off.':
            '設定しました。サインイン時のリマインダーはオフです。',
        'Saved on this computer in:':
            'このコンピューターの保存先:',
        'Saved in your own user folder on this computer.':
            'このコンピューターの、ご自分のユーザー フォルダーに保存しています。',
        'Days you opened it in the last {days} days: {n} (last 7 days: {recent})':
            '過去{days}日間で開いた日数: {n}（直近7日間: {recent}）',
        'Times you marked a plan done: {n}':
            '予定を完了にした回数: {n}',
        'Your current plan: ':
            '現在の予定: ',
        'Earlier plan (for same): ':
            '前の予定（same 用）: ',
        'Days-in-a-row message: shown.':
            '連続日数のメッセージ: 表示',
        'Days-in-a-row message: hidden.':
            '連続日数のメッセージ: 非表示',
        'Opens by itself at sign-in: turned off by your organization.':
            'サインイン時に自動で開く: 組織の設定でオフ',
        'Opens by itself at sign-in: on.':
            'サインイン時に自動で開く: オン',
        'Opens by itself at sign-in: off.':
            'サインイン時に自動で開く: オフ',
        "It never leaves this computer. Others who can read this computer's files, such as IT staff, could read it.":
            'このコンピューターの外には出ません。ただし、IT 担当者など、このコンピューターのファイルを読める人は読むことができます。',
        'After tidying, the file holds only this:':
            '整理したあとのファイルの中身は、これだけです:',
        'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
            'このコンピューターに保存したメモ、日付、予定をすべて削除しますか？（y または n、Enter でキャンセル） > ',
        'Nothing was deleted.':
            '何も削除していません。',
        'Could not delete everything.':
            '一部を削除できませんでした。',
        'Delete these yourself:':
            '次のファイルは手動で削除してください:',
        'Could not list the folder, so backup copies may remain:':
            'フォルダーの一覧を取得できなかったため、バックアップが残っている可能性があります:',
        'Done. Everything saved was deleted.':
            '完了しました。保存内容をすべて削除しました。',
        'Another open hello-world window cannot put it back.':
            'ほかの hello-world ウィンドウが開いていても、データが復元されることはありません。',
        'Close any other open hello-world window, or it may save its notes again.':
            'ほかに開いている hello-world ウィンドウは閉じてください。開いたままだと、そのウィンドウがメモを再び保存することがあります。',
        'Everything saved was deleted in another window, so this was not saved.':
            '保存内容が別のウィンドウで削除されたため、これは保存しませんでした。',
        'The other open window had also finished a plan.':
            '別のウィンドウでも予定が完了になっていました。',
        'The other open window changed the plan, so its plan is kept.':
            '別のウィンドウで予定が変更されたため、そちらの予定を残しました。',
        'Type plan at the last prompt to set one.':
            '予定を設定するには、最後の入力欄で plan と入力してください。',
        'That looks like a command, not a plan, so nothing was saved.':
            'コマンドのようなので、予定としては保存しませんでした。',
        'Type your plan, or press Enter to go back.':
            '予定を入力してください。Enter で戻ります。',
        'Finished lately:':
            '最近終えた予定:',
        'Your plan today: ':
            '今日の予定: ',
        'Your plan from {date}: ':
            '{date}の予定: ',
        'Earlier plan: ':
            '前の予定: ',
        'Type the next plan, or Enter to close > ':
            '次の予定を入力（Enter で閉じる） > ',
        'Type the next plan, same to reuse the earlier plan, or Enter to close > ':
            '次の予定を入力（same で前の予定を使う、Enter で閉じる） > ',
        "Type today's plan, or Enter to keep it > ":
            '今日の予定を入力（Enter でそのまま） > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
            '今日の予定を入力（same で前の予定を使う、Enter でそのまま） > ',
        "Type today's plan, or Enter to go back > ":
            '今日の予定を入力（Enter で戻る） > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
            '今日の予定を入力（same で前の予定を使う、Enter で戻る） > ',
        'Closing.':
            '閉じます。',
        'There is no earlier plan to reuse yet. Nothing changed.':
            '呼び戻せる前の予定はまだありません。変更はありません。',
        'Nothing changed.':
            '変更はありません。',
        'Could not save that on this computer. Your plan is unchanged.':
            'このコンピューターに保存できませんでした。予定は変わっていません。',
        'No finished plans are saved.':
            '終えた予定は保存されていません。',
        'Type the number to forget (1 to {n}), or Enter to keep them all > ':
            '削除する番号を入力（1～{n}、Enter ですべて残す） > ',
        'There is no number "{typed}" on the list. Type a number from 1 to {n}, or press Enter to keep them all.':
            'リストに「{typed}」という番号はありません。1～{n}の番号を入力するか、Enter ですべて残してください。',
        'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
            'same 用の前の予定からも削除しますか？（y または n、Enter で same 用に残す） > ',
        'Type y or n, or press Enter to keep it for same.':
            'y か n を入力するか、Enter で same 用に残してください。',
        'That plan was already forgotten. Nothing changed.':
            'その予定はすでに削除されています。変更はありません。',
        'Forgotten: ':
            '削除しました: ',
        'Same still has it.':
            'same でまだ呼び戻せます。',
        'Could not save that on this computer. Nothing changed.':
            'このコンピューターに保存できませんでした。変更はありません。',
        'Options':
            'オプション',
        'Show what is saved on this computer':
            'このコンピューターに保存されている内容を表示',
        'Open once a day at sign-in (turned off by your organization)':
            'サインイン時に1日1回開く（組織の設定でオフ）',
        'Turn off: open once a day at sign-in (now on)':
            'オフにする: サインイン時に1日1回開く（現在オン）',
        'Turn on: open once a day at sign-in (now off)':
            'オンにする: サインイン時に1日1回開く（現在オフ）',
        'Days-in-a-row message (hidden by your organization)':
            '連続日数のメッセージ（組織の設定で非表示）',
        'Hide the days-in-a-row message (now shown)':
            '連続日数のメッセージを非表示にする（現在は表示）',
        'Show the days-in-a-row message (now hidden)':
            '連続日数のメッセージを表示する（現在は非表示）',
        'Delete everything saved':
            '保存内容をすべて削除',
        'Help':
            'ヘルプ',
        "Set today's plan (turned off by your organization)":
            '今日の予定を設定（組織の設定でオフ）',
        'Forget a finished plan (turned off by your organization)':
            '終えた予定を削除（組織の設定でオフ）',
        "Set or change today's plan":
            '今日の予定を設定・変更',
        'Forget one finished plan':
            '終えた予定を1件削除',
        'Thought and tip (hidden by your organization)':
            'ひとこととヒント（組織の設定で非表示）',
        'Hide the thought and tip (now shown)':
            'ひとこととヒントを非表示にする（現在は表示）',
        'Show the thought and tip (now hidden)':
            'ひとこととヒントを表示する（現在は非表示）',
        '{date}: ':
            '{date}: ',
        'Enter':
            'Enter',
        'Back to the last prompt':
            '最後の入力欄に戻る',
        'Choose 1 to 11, or Enter to go back > ':
            '1～11を選択（Enter で戻る） > ',
        'Choose 1 to 11, m to list the options, or Enter to go back > ':
            '1～11を選択（m でオプション一覧、Enter で戻る） > ',
        'The saved file could not be read just now, so this may be out of date.':
            '保存ファイルを今は読み込めなかったため、この内容は最新でない可能性があります。',
        'Type full to see the whole file, or Enter to go on > ':
            'ファイル全体を見るには full、続けるには Enter > ',
        'Could not save that choice on this computer.':
            'この選択をこのコンピューターに保存できませんでした。',
        'Your organization has hidden the days-in-a-row message.':
            '連続日数のメッセージは、組織の設定で非表示になっています。',
        'Done. The days-in-a-row message is on.':
            '設定しました。連続日数のメッセージはオンです。',
        'Done. The days-in-a-row message is off.':
            '設定しました。連続日数のメッセージはオフです。',
        'Plans are turned off by your organization.':
            '予定の機能は、組織の設定でオフになっています。',
        'Your organization has hidden the thought and tip.':
            'ひとこととヒントは、組織の設定で非表示になっています。',
        'Done. The thought and tip are on.':
            '設定しました。ひとこととヒントはオンです。',
        'Done. The thought and tip are off.':
            '設定しました。ひとこととヒントはオフです。',
        'Type 1 to 11, or press Enter to go back.':
            '1～11を入力するか、Enter で戻ってください。',
        'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
            'サインイン時に1日1回、自動で開くようにしますか？（y または n、Enter であとで） > ',
        'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
            '予定についてたずねられるよう、サインイン時に1日1回、自動で開くようにしますか？（y または n、Enter であとで） > ',
        'Type y or n, or press Enter for not now.':
            'y か n を入力してください。あとで決めるなら Enter を押してください。',
        'That was not understood. It will ask again on a later visit.':
            '入力を認識できませんでした。また今度たずねます。',
        'It will ask again on a later visit. Menu option 2 also turns it on.':
            'また今度たずねます。メニューの2でもオンにできます。',
        'No problem. Menu option 2 turns it on later.':
            'わかりました。あとでメニューの2からオンにできます。',
        "Okay. It won't ask again. Menu option 2 turns it on.":
            'わかりました。今後はたずねません。メニューの2でオンにできます。',
        'Okay. It will ask again on a later visit. Type n to stop it.':
            'わかりました。また今度たずねます。今後たずねないようにするには n と入力してください。',
        'When did you finish it?':
            'いつ終えましたか？',
        'Today':
            '今日',
        'Type a number from 1 to {n}, or Enter for 1 > ':
            '1～{n}の番号を入力（Enter で1） > ',
        'Type a number from 1 to {n}, or press Enter.':
            '1～{n}の番号を入力するか、Enter を押してください。',
        'That looks like more than one thing. Finishing the first part still counts.':
            'いくつかのことが含まれているようです。最初の一つを終えるだけでも、ちゃんと数に入ります。',
        'There is no plan to mark as done. Type plan to set one.':
            '完了にする予定がありません。plan と入力して設定してください。',
        'Could not save that on this computer. The plan is still open.':
            'このコンピューターに保存できませんでした。予定は未完了のままです。',
        'Your plan from over two weeks ago was put away. Type same at the plan prompt to bring it back.':
            '2週間以上前の予定は、いったんしまっておきました。予定の入力欄で same と入力すると呼び戻せます。',
        "Press Enter at each question to skip it, and once more to close. That's it.":
            '各質問で Enter を押すとスキップ、もう一度押すと閉じます。使い方はこれだけです。',
        'Welcome.':
            'ようこそ。',
        'Each day you get one thought and one small thing to try, the same for everyone.':
            '毎日、ひとことと、ちょっと試してみることが一つずつ表示されます。内容は全員共通です。',
        'If you type a plan, it asks next time how it went. Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks.':
            '予定を入力すると、次回どうだったかをたずねます。メモはこのコンピューターにだけ保存され、どこにも送信されません。ただし、ほかの仕事のファイルと同じく機密扱いではないので、書くのは日常の作業だけにしてください。',
        'Type menu at the end for the options.':
            'オプションを見るには、最後に menu と入力してください。',
        'Welcome back. Glad you are here.':
            'おかえりなさい。また会えてうれしいです。',
        'You have opened this {row} days in a row. Nice to see you.':
            '{row}日続けて開いています。今日も会えてうれしいです。',
        'Last time you planned: ':
            '前回の予定: ',
        'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
            'できましたか？（y: はい、n: まだ、Enter: スキップ） > ',
        'Type y or n, or press Enter to skip.':
            'y か n を入力するか、Enter でスキップしてください。',
        'Could not save that on this computer. Your answer was not counted.':
            'このコンピューターに保存できませんでした。回答は記録されていません。',
        'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
            '大丈夫です。今日に持ち越しますか？（y または n、Enter で持ち越す） > ',
        'Type y to keep it, n to clear it, or press Enter to keep it.':
            '持ち越すなら y、取り消すなら n を入力してください。Enter でも持ち越します。',
        'Cleared. Type same at a plan prompt if you want it back.':
            '取り消しました。戻したいときは、予定の入力欄で same と入力してください。',
        'Kept for today.':
            '今日に持ち越しました。',
        'That was not understood. Your plan is left as it was.':
            '入力を認識できませんでした。予定はそのままです。',
        'Your plan is still open.':
            '予定は未完了のままです。',
        'Thought for today:':
            '今日のひとこと:',
        'Try this today:':
            '今日試してみること:',
        'Your plan for today: ':
            '今日の予定: ',
        'Still open since {date}:':
            '{date}から未完了:',
        '(Enter to skip)':
            '（Enter でスキップ）',
        '(A plan typed here replaces the old one. Enter to skip)':
            '（ここに入力すると前の予定と置き換わります。Enter でスキップ）',
        '(Type same to reuse it, or Enter to skip)':
            '（same で再利用、Enter でスキップ）',
        'What is one thing you want to get done today?':
            '今日終わらせたいことを、一つ挙げるなら何ですか？',
        'There is no earlier plan to reuse yet. Nothing was saved.':
            '呼び戻せる前の予定はまだありません。何も保存していません。',
        'Your notes could not be saved on this computer. This screen still works.':
            'メモをこのコンピューターに保存できませんでした。この画面はそのまま使えます。',
        'Type menu, or Enter to close > ':
            'menu と入力、または Enter で閉じる > ',
        'Type done, plan or menu, or Enter to close > ':
            'done、plan、menu のどれかを入力、または Enter で閉じる > ',
        'Type plan or menu, or Enter to close > ':
            'plan か menu を入力、または Enter で閉じる > ',
        'Type done, plan or menu, or press Enter to close.':
            'done、plan、menu のどれかを入力するか、Enter を押して閉じてください。',
        'Type plan or menu, or press Enter to close.':
            'plan か menu を入力するか、Enter を押して閉じてください。',
        "The saved file can't be read right now, or it is damaged.":
            '保存ファイルを今は読み込めないか、ファイルが壊れています。',
        'Nothing was changed. Saved in: ':
            '何も変更していません。保存先: ',
        'Deleting saved notes needs a person at the keyboard.':
            '保存したメモを削除するには、キーボードの前に人がいる必要があります。',
        '{option} needs on or off. Here are the options.':
            '{option} には on か off を指定してください。オプションは次のとおりです。',
        'Unknown option: {option}. Here are the options.':
            '不明なオプションです: {option}。オプションは次のとおりです。',
        '&Done':
            '完了(&D)',
        '&Not yet':
            'まだ(&N)',
        'S&kip':
            'スキップ(&K)',
        '&Save':
            '保存(&S)',
        '&I did it':
            'できました(&I)',
        '&Options':
            'オプション(&O)',
        'Close':
            '閉じる',
        'Not today':
            '今日はやめておく',
        'Did you do it?':
            'できましたか？',
        'Done. A reminder comes when you sign in, if there is a plan to ask about.':
            '設定しました。たずねる予定があるときは、サインイン時にリマインダーが表示されます。',
        'Done. The Start menu opens a window with buttons.':
            '設定しました。スタート メニューからボタン付きのウィンドウが開きます。',
        'Done. The Start menu opens this text screen.':
            '設定しました。スタート メニューからこのテキスト画面が開きます。',
        'More options':
            'その他のオプション',
        'Remind me when I sign in':
            'サインイン時にリマインダーを表示',
        'Show the thought and tip':
            'ひとこととヒントを表示',
        'Type your plan in the box.':
            '予定をボックスに入力してください。',
        'Use a window with buttons (now this text screen)':
            'ボタン付きのウィンドウを使う（現在はこのテキスト画面）',
        'Use the text screen':
            'テキスト画面を使う',
        'Use this text screen (now a window with buttons)':
            'このテキスト画面を使う（現在はボタン付きのウィンドウ）',
        'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
            'サインイン時にリマインダーを表示しますか？前回の予定が表示され、ワンクリックで答えられます。オプションからオフにできます。',
        'Window or text screen (set by your organization)':
            'ウィンドウかテキスト画面か（組織が設定）',
        'Your organization has set hello-world to open as a text screen.':
            '組織の設定により、hello-world はテキスト画面で開きます。',
        'Saved.':
            '保存しました。',
        'Save your plan before closing?':
            '閉じる前に予定を保存しますか？',
        'Delete all saved notes, dates and plans on this computer?':
            'このコンピューターに保存したメモ、日付、予定をすべて削除しますか？',
        'Turn off: reminder when you sign in (now on)':
            'オフにする: サインイン時のリマインダー（現在オン）',
        'Turn on: reminder when you sign in (now off)':
            'オンにする: サインイン時のリマインダー（現在オフ）',
        'Reminder when you sign in (turned off by your organization)':
            'サインイン時のリマインダー（組織の設定でオフ）',
        'Reminder when you sign in: on.':
            'サインイン時のリマインダー: オン',
        'Reminder when you sign in: off.':
            'サインイン時のリマインダー: オフ',
        'Reminder when you sign in: turned off by your organization.':
            'サインイン時のリマインダー: 組織の設定でオフ',
        'Show the days-in-a-row message':
            '連続日数のメッセージを表示',
        'Done. The thought and tip show next time you open hello-world.':
            '設定しました。次に hello-world を開いたときから、ひとこととヒントが表示されます。',
        "Clear today's plan?":
            '今日の予定を取り消しますか？',
        'Next plan, if you want one:':
            '次の予定（必要なら）:',
        'A few things? Put ; between them.':
            '複数あるときは ; で区切ってください。',
        'A plan can be up to {n} characters.':
            '予定は{n}文字まで入力できます。',
        'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
            'できましたか？（y: すべて、n: まだ、番号: できたものだけ、Enter: スキップ） > ',
        'Last time you planned:':
            '前回の予定:',
        'The rest is kept for today.':
            '残りは今日に持ち越します。',
        'Tick the ones you did, then click Done. With none ticked, Done means all of them.':
            'できたものにチェックを付けて、[完了] をクリックしてください。何もチェックしないと、すべて完了になります。',
        'Type y for all, n for not yet, or the numbers you did, such as 1 3. Enter skips.':
            'すべてなら y、まだなら n、できたものだけなら 1 3 のように番号を入力してください。Enter でスキップします。',
        'Your settings were kept.':
            '設定は変更していません。',
        'Language (set by your organization)':
            '言語（組織が設定）',
        'Language (now {name})':
            '言語（現在: {name}）',
        'following Windows':
            'Windows の設定に従う',
        'Your organization shows hello-world in English.':
            '組織の設定により、hello-world は英語で表示されます。',
        'Follow Windows':
            'Windows の設定に従う',
        'Type a number from 1 to {n}, or Enter to keep it > ':
            '1～{n}の番号を入力（Enter でそのまま） > ',
        'Done. The new language shows next time you open hello-world.':
            '設定しました。次に hello-world を開いたときから、新しい言語で表示されます。',
        'Language...':
            '言語...',
        'Hello, {name}!':
            'こんにちは、{name}さん！',
        'One thing to get done today? Open hello-world to plan it.':
            '今日終わらせたいことはありますか？hello-world を開いて予定を立てましょう。',
        '&Open':
            '開く(&O)',
        'Reminder settings...':
            'リマインダーの設定...',
        'Greet me by name':
            'あいさつに名前を入れる',
        'At sign-in':
            'サインイン時',
        'At {at}':
            '{at}',
        'Also on days with no plan':
            '予定がない日も表示',
        'Open hello-world after I answer':
            '答えたあとに hello-world を開く',
        'Not on weekends':
            '週末は表示しない',
        'Done. A reminder comes at {at} each day, if there is a plan to ask about.':
            '設定しました。たずねる予定があるときは、毎日{at}にリマインダーが表示されます。',
        'Send feedback...':
            'フィードバックを送る...',
        '"holidays" must be a list of at most {n} dates.':
            '"holidays" は{n}件以下の日付のリストにしてください。',
        '"title" must be 1 to 40 characters of plain text, with no link or address.':
            '"title" は、リンクやアドレスを含まない1～40文字のプレーン テキストにしてください。',
        '"{list}" must be a list of {low} to {high} lines.':
            '"{list}" は{low}～{high}行のリストにしてください。',
        "Can't read {path}: {error}":
            '{path} を読み込めません: {error}',
        'Could not save that on this computer.':
            'このコンピューターに保存できませんでした。',
        'Days you opened hello-world: {n}':
            'hello-world を開いた日数: {n}',
        'Keep a longer history':
            'より長い履歴を残す',
        'Keep my numbers':
            '自分の記録を残す',
        'Longest run of days: {n}':
            '最長連続日数: {n}',
        "Mark today's plan done":
            '今日の予定を完了にする',
        "Mark today's plan done (plans are turned off)":
            '今日の予定を完了にする（予定はオフ）',
        'My numbers are off. Turn them on under Options, or with --set numbers on.':
            '記録はオフになっています。オプションまたは --set numbers on でオンにできます。',
        'My numbers...':
            '自分の記録...',
        'Nothing finished yet this week. That is fine.':
            '今週はまだ何も終えていません。それでも大丈夫です。',
        'OK: {thoughts} thoughts and {tips} tips.':
            'OK: ひとこと{thoughts}件、ヒント{tips}件。',
        'Plans finished: {n}':
            '終えた予定: {n}',
        'Save my plans to a file':
            '予定をファイルに保存',
        'Saved to {path}':
            '{path} に保存しました',
        "The file isn't valid JSON, or is over 200,000 characters.":
            'ファイルが有効な JSON ではないか、200,000文字を超えています。',
        'The file must hold an object with two lists, "thoughts" and "tips", and may add "holidays" and "title".':
            'ファイルには "thoughts" と "tips" の2つのリストを持つオブジェクトが必要です。"holidays" と "title" も追加できます。',
        'This week you finished {n}:':
            '今週終えた予定（{n}件）:',
        'This week...':
            '今週...',
        'holidays line {line} is not a date like 2026-12-25.':
            'holidays の{line}行目が、2026-12-25 のような日付になっていません。',
        '{list} line {line} has a date.':
            '{list} の{line}行目に日付が含まれています。',
        '{list} line {line} has a link or an address.':
            '{list} の{line}行目にリンクまたはアドレスが含まれています。',
        '{list} line {line} has control characters or extra spaces.':
            '{list} の{line}行目に制御文字または余分なスペースが含まれています。',
        '{list} line {line} is not text.':
            '{list} の{line}行目がテキストではありません。',
        '{list} line {line} must be {low} to {high} characters long.':
            '{list} の{line}行目は{low}～{high}文字にしてください。',
    },
}

# ---- Korean ----

LANGUAGES["ko"] = {
    "days": ('월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'),
    "months": ('1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'),
    "date": '{year}년 {month} {d}일 {day}',
    "thoughts": (
        '계속 피하던 문서 하나를 열고 첫 문단만 읽어 보세요.',
        '10분만 해도 시작은 시작이에요. 그러면 대개 다음 10분이 더 쉬워져요.',
        '오늘 계획을 다 세울 필요는 없어요. 괜찮은 첫걸음 하나면 돼요.',
        '어설픈 첫 문장을 써 보세요. 나중에 다듬을 진짜 재료가 생겨요.',
        '책상 한쪽 구석만 치워 보세요. 나머지도 한결 차분해 보일 거예요.',
        '목록에서 가장 작은 일을 골라, 다른 일을 보기 전에 끝내 보세요.',
        '오지 않을지도 모를 완벽한 순간을 기다리는 것보다, 조용한 아침에 서툴게라도 시작하는 게 나아요.',
        '첫 단계를 캘린더에 넣어 자리를 마련해 주세요.',
        '큰 프로젝트도 대부분 오후 몇 시간이 쌓여 이뤄져요. 오늘은 오후 한나절만 목표로 해 보세요.',
        '바로 다음에 할 일을 소리 내어 말해 보세요. 나머지 목록은 차례를 기다려도 돼요.',
        '생각보다 속도가 느린 날도 있어요. 그 속도도 충분히 의미가 있어요.',
        '첫 주를 보내는 새 동료를 대하듯 자신을 대해 보세요.',
        '몇 년째 해 온 일도 아직 배우는 중일 수 있어요.',
        '아침이 처졌다고 오후까지 정해지는 건 아니에요. 점심 먹고 다시 시작해도 돼요.',
        '피곤함은 실패가 아니라 신호예요. 계획을 조금 바꾸고 천천히 이어 가세요.',
        '다른 사람에게 선뜻 베푸는 너그러움을 자신에게도 베풀어 주세요.',
        '발전은 한동안 아무 티가 안 나다가, 어느 순간 완성된 한 페이지로 나타나요.',
        '한 번 더 읽어야 이해되는 것도 괜찮아요.',
        '준비됐다는 느낌이 없어도 돼요. 떨리는 채로 해도 한 거예요.',
        '오늘의 최선이 어제보다 작을 수도 있어요. 그래도 괜찮아요.',
        '안 쓰는 탭은 닫아 보세요. 몇 분 안에 집중이 한결 편해질 거예요.',
        '일 하나, 창 하나, 25분. 조용히 집중하면 어디까지 갈 수 있는지 보세요.',
        '불쑥 떠오른 생각은 적어 두고, 하던 일로 돌아가세요.',
        '할 수 있다면 한 시간 동안 휴대폰을 무음으로 두고 일에 온전히 집중해 보세요.',
        '오늘을 좋은 하루로 만들 한 가지를 정하고, 그 일을 할 시간을 지켜 주세요.',
        '한 번에 하나씩 하는 게 생각보다 빠를 때가 많아요.',
        '할 일 세 개를 깔끔하게 적은 목록이 스무 개가 흩어진 목록보다 나아요.',
        '마음이 딴 데로 가면 알아차리고, 탓하지 말고 살며시 돌아오세요.',
        '가장 어려운 일은 기운이 가장 좋을 때 하세요. 그게 아침 첫 시간이 아니어도요.',
        '헤드폰을 쓰고, 차 한 잔 준비하고, 문을 닫으세요. 분위기를 만들면 집중은 따라와요.',
        '5분만 화면에서 떨어져 보세요. 돌아오면 머리가 조금 맑아져 있을 거예요.',
        '오늘 점심은 책상을 떠나서 드세요. 메일은 점심 먹는 동안 기다려 줘요.',
        '건물 주변을 잠깐 걷는 것도 머리를 위한 엄연한 일이에요.',
        '바쁜 오후에 화면에서 1분 떨어지는 것도 시간을 잘 쓰는 거예요.',
        '어깨를 펴고 턱에 힘을 빼 보세요. 몇 시간째 긴장하고 있었을지도 몰라요.',
        '할 수 있다면 오늘은 제시간에 퇴근하세요. 내일의 내가 저녁 시간을 고마워할 거예요.',
        '쉬는 것도 일의 일부예요. 지치면 같은 실수를 반복하기 쉬우니까요.',
        '잠시 눈을 쉬게 하고 어깨에 힘을 빼세요.',
        '제대로 쉬고 나면 오후가 새로 시작하는 것처럼 느껴져요.',
        '저녁은 온전히 나를 위해 쓰세요. 밤 9시에 꼭 봐야 할 메일은 없어요.',
        '부탁하지 않았는데 작은 일을 해 준 사람에게 오늘 고맙다고 말해 보세요.',
        '대부분의 사람은 눈에 보이는 것보다 많은 일을 안고도 최선을 다하고 있어요.',
        '동료가 차나 커피를 어떻게 마시는지 알아 두세요. 기억해 주는 것만으로도 작은 선물이에요.',
        '누가 퉁명스럽게 굴면, 나에 대한 평가가 아니라 힘든 하루를 보내는 중이라고 생각하세요.',
        '문을 잡아 주고, 간식을 나누고, 남의 말은 끝까지 들어 주세요.',
        '가벼운 인사와 주말 이야기 한마디가 아침의 가장 좋은 순간이 될 수 있어요.',
        '새로 온 사람이 뻔한 걸 물으면, 나도 예전에 같은 걸 물었다는 걸 떠올려 보세요.',
        '동료의 아이디어 덕분에 일이 나아졌다면 그 동료 덕분이라고 모두 앞에서 말해 주세요.',
        '메시지에 답할 때 따뜻함을 조금 담아 보세요. 돈 드는 일도 아니고, 받는 사람 마음도 편해져요.',
        '요즘 회의에서 말이 없던 동료에게 잘 지내는지 물어보세요.',
        '새 일을 시작하기 전에 거의 다 된 일부터 끝내세요.',
        '완벽하지만 끝나지 않은 것보다 적당히 괜찮게 끝낸 것이 대개 더 쓸모 있어요.',
        '마무리 못 한 일 하나를 오늘 끝내고, 뒤따르는 작은 홀가분함을 느껴 보세요.',
        '마지막 10%는 대개 몇 분만 신경 쓰면 돼요. 오늘 그 몇 분을 내 보세요.',
        '임시 보관함에서 기다리는 메일을 보내세요. 아마 지금 그대로도 괜찮을 거예요.',
        '완료로 표시하고, 숨 한 번 쉬고, 끝냈다는 걸 기뻐하세요.',
        '반쯤 한 큰일보다 끝낸 작은 일이 더 값져요.',
        '퇴근 전에 내일 첫 단계를 메모해 두세요. 기억하려고 애쓰지 않아도 돼요.',
        '한 번 더 읽고, 보이는 것만 고친 다음 보내세요.',
        '깔끔한 결과 하나로 하루를 마치면 저녁이 가벼워져요.',
        '일찍 물어보면 나중에 혼자 끙끙대는 한 시간을 아낄 수 있어요.',
        '대부분은 자기가 아는 걸 물어봐 주면 좋아해요. 미안해하지 말고 물어보세요.',
        '"막혔어요"는 동료가 바로 도와줄 수 있는, 분명하고 쓸모 있는 말이에요.',
        '필요한 걸 쉬운 말로 부탁하고, 상대가 "좋아요"라고 할 기회를 주세요.',
        '혼자 붙잡고 있는 것보다 둘이 함께 보면 대개 더 빨리 풀려요.',
        '도움이 필요하다고 짐이 되는 게 아니에요. 같은 팀이니까요.',
        '구체적으로 물어보면 상대도 구체적으로 답해 줄 수 있어요.',
        '지시가 분명하지 않으면 확인하는 것도 일을 제대로 하는 과정이에요.',
        '도울 수 있을 때 돕고, 필요할 때 도움을 받으세요. 둘 다 할수록 쉬워져요.',
        '복도 저쪽 누군가는 아마 이걸 전에 해결해 봤을 거예요. 찾아가 보세요.',
        '이번 주에 알아낸 것들을 짧게 적어 두세요. 생각보다 많이 쌓여요.',
        '새로운 일에서 초보라는 건 아직 성장하고 있다는 뜻이에요.',
        '존경하는 동료가 까다로운 통화를 어떻게 처리하는지 보고, 한 가지만 배워 보세요.',
        '쉬는 시간에 유익한 글 한 페이지를 읽었다면, 오늘 공부는 그걸로 충분해요.',
        '다른 사람에게 일을 설명하다 보면 의외로 나도 잘 배우게 돼요.',
        '"그건 아직 모르겠어요"라고 말하고 알아보러 가도 괜찮아요.',
        '낯선 시스템도 몇 번 써 보기 전까지는 다 헷갈려 보여요.',
        '경험 많은 사람에게 그걸 어떻게 배웠는지 물어보세요. 대개 안심이 되는 답이 돌아와요.',
        '기술은 반복에서 나와요. 작은 일을 되풀이하다 보면 쉬워져요.',
        '평범한 일에도 호기심을 조금 가지면 더 재미있어질 수 있어요.',
        '일찍 발견한 실수는 수정 한 번이면 끝나요. 그리고 실수는 대부분 일찍 발견돼요.',
        '고치고, 알아야 할 사람에게 알리고, 그다음엔 속상함이 가라앉게 두세요.',
        '일하다 한 실수는 거의 다 그 순간보다 일주일 뒤에 더 작게 느껴져요.',
        '한 번의 실수가 그동안 꼼꼼히 해 온 몇 년을 지우지는 않아요.',
        '일이 잘못되면 사람을 탓하기 전에 과정부터 살펴보세요.',
        '주변 사람 모두 메일을 엉뚱한 사람에게 보낸 적이 한 번쯤은 있어요.',
        '실수가 주는 교훈 하나만 챙기고 나머지는 털어 버리세요.',
        '실수를 솔직하게 인정하면, 실수를 안 한 것보다 대개 더 신뢰를 얻어요.',
        '꼼꼼한 사람도 유난히 덜렁대는 날이 있어요. 저녁이면 지나가요.',
        '오늘의 작은 실수들은 다음 달이면 대부분 기억도 안 날 거예요.',
        '급한 불 없이 조용한 날은 좋은 날이에요. 아무도 말하지 않더라도요.',
        '작은 즐거움을 알아차려 보세요. 따뜻한 머그잔, 깔끔한 받은편지함, 조용한 1분.',
        '날마다 큰 성과가 필요하진 않아요. 꾸준하고 기분 좋게 일하는 것도 좋은 방식이에요.',
        '회의가 5분 일찍 끝나면 그 시간을 즐기고 마음대로 쓰세요.',
        '평범한 하루를 잘 보낸 것도 조용히 자랑스러워할 일이에요.',
        '좋은 일은 겉으로는 별것 아닌 것처럼 보일 때가 많아요. 그래도 괜찮아요.',
        '기분 좋은 오후라면, 꼭 뭔가를 해내지 않아도 그냥 즐기세요.',
        '첫 커피, 익숙한 얼굴들 같은 하루의 작은 일상도 눈여겨볼 만해요.',
        '오늘도 자리를 지키며 내 몫을 했어요. 그거면 충분해요.',
        '오늘 저녁, 잠깐 시간을 내서 오늘 잘된 일 하나를 떠올려 보세요.',
        '두 일 사이의 조용한 1분은 낭비가 아니에요. 다음 일을 잘 시작하는 방법이에요.',
    ),
    "tips": (
        '화면에서 떨어져 물 한 잔을 천천히 마셔 보세요.',
        '어깨를 뒤로 다섯 번, 천천히 돌려 보세요.',
        '20초 동안 눈을 쉬게 하세요. 먼 곳을 보거나 눈을 감아 보세요.',
        '앉아서든 서서든 팔을 머리 위로 뻗고 숨을 깊이 쉬어 보세요.',
        '갈 수 있는 가장 먼 방이나 창가까지 갔다 와 보세요.',
        '자세를 확인하고 어깨를 아래로 툭 내려 보세요.',
        '편한 만큼만 목을 좌우로 천천히 돌려 보세요.',
        '손을 열 번 쥐었다 폈다 하며 손가락을 풀어 보세요.',
        '가장 자주 여는 문서 하나를 고정해 클릭 한 번으로 열리게 하세요.',
        '걷든 휠체어로든, 편한 방법으로 잠깐 밖에 다녀오세요.',
        '따뜻하거나 시원한 음료를 한 잔 따라 화면에서 떨어져 즐겨 보세요.',
        '풍경, 소리, 촉감처럼 차분한 것에 잠시 주의를 기울여 보세요.',
        '하다 만 일 하나에 다음 단계를 적어 두세요.',
        '두 발을 바닥에 붙이고 바르게 앉거나 서서 열 번 숨 쉬어 보세요.',
        '훑어보기만 하는 단체 채팅방 하나의 알림을 꺼 보세요.',
        '턱에 힘을 빼고 이마도 잠깐 풀어 보세요.',
        '오늘 기분 좋은 방식으로 2분 동안 몸을 움직여 보세요.',
        '자꾸 미루는 일을 위해 캘린더에 15분을 잡아 두세요.',
        '의자, 화면, 키보드 중 하나를 조금 더 편하게 조정해 보세요.',
        '할 수 있다면 다음 회의나 통화하러 갈 때 조금 돌아서 가 보세요.',
        '자주 쓰는 메일 하나를 템플릿으로 저장해 두세요.',
        '가장 많이 쓰는 프로그램의 바로 가기 키 하나를 익혀 보세요.',
        '다음 커피나 차를 마시기 전에 물 한 잔을 다 마셔 보세요.',
        '어깨를 귀까지 으쓱 올렸다가 스르르 내려놓으세요.',
        '1분 동안 밖에 나가거나 창문을 열어 바람을 쐬세요.',
        '천천히 다섯 번 숨 쉬고, 내쉴 때마다 조금 더 길게 내쉬어 보세요.',
        '다음 메시지를 열기 전에 1분만 조용히 쉬어 보세요.',
        '오늘 지금까지 있었던 좋은 일 하나를 적어 보세요.',
        '눈을 감고 세 번 숨 쉬며 지금 기분을 살펴보세요.',
        '지금 느껴지는 것 세 가지를 떠올려 보세요. 어떤 감각이든 괜찮아요.',
        '이번 주에 기대되는 일 하나를 적어 보세요.',
        '2분 타이머를 맞추고 화면 없이 그냥 앉아 있어 보세요.',
        '화분이나 좋아하는 머그잔처럼 가까이 있는 작은 것을 즐겨 보세요.',
        '이번 주에 잘한 일 하나를 떠올리고 스스로 칭찬해 주세요.',
        '다른 창은 다 닫고 좋아하는 노래 한 곡을 처음부터 끝까지 들어 보세요.',
        '넷을 세며 들이쉬고 여섯을 세며 내쉬기를 세 번 해 보세요.',
        '다음에 사소한 짜증이 나면 반응하기 전에 숨 한 번 쉬어 보세요.',
        '최근에 웃었던 일 하나를 적어 보세요.',
        '1분 동안 소리, 냄새, 손에 닿는 것 중 기분 좋은 것 하나를 느껴 보세요.',
        '좋아하는 장소를 떠올리고 30초 동안 그려 보세요.',
        '작은 일 하나에 "지금은 이 정도면 됐어"라고 말하고 넘어가세요.',
        '고마운 일 하나를 한 문장으로 적어 보세요.',
        '다음 한 모금은 천천히 맛을 느끼며 마셔 보세요.',
        '다음 일을 시작하기 전에 두 일 사이에 잠깐 쉬어 가세요.',
        '오늘 생각보다 잘 풀린 일 하나를 찾아보세요.',
        '오후를 어떤 느낌으로 보내고 싶은지 한 단어로 정해 보세요.',
        '60초 동안 머리를 쉬게 한 다음 하던 일로 돌아가세요.',
        '바닥에 닿은 발을 느끼며 잠시 중심을 잡아 보세요.',
        '누군가 나에게 해 준 친절 하나를 떠올리고 그 기억을 즐겨 보세요.',
        '나중에 다시 보고 싶은 아이디어 하나를 적어 두고 잠시 내려놓으세요.',
        '책상 한쪽 구석을 정리해 보세요. 딱 한 곳만요.',
        '한동안 답하지 못한 메시지 하나에 답장해 보세요.',
        '내일 가장 중요한 일을 포스트잇이나 메모에 적어 두세요.',
        '더 이상 필요 없는 브라우저 탭을 닫아 보세요.',
        '최근에 도움을 준 동료에게 고맙다고 말해 보세요.',
        '필요 없는 오래된 메일 다섯 개를 보관함으로 옮겨 보세요.',
        '지저분한 파일 이름 하나를 나중에 찾기 쉽게 바꿔 보세요.',
        '바탕 화면에 흩어진 파일 한두 개를 정리해 보세요.',
        '이제 필요 없는 오래된 알림 하나를 지워 보세요.',
        '자주 여는 문서에 알아보기 쉬운 제목을 붙여 보세요.',
        '할 일 목록에서 작은 일 하나를 끝내고 지워 보세요.',
        '읽지 않는 뉴스레터 하나를 구독 취소하세요.',
        '부드러운 천으로 키보드나 화면을 닦아 보세요.',
        '펜, 노트, 물을 손 닿는 곳에 두세요.',
        '오늘 어디까지 했는지 미래의 나에게 짧은 메모를 남겨 보세요.',
        '오늘 오후 가장 중요한 일 하나를 골라 먼저 해 보세요.',
        '책상 옆 휴지통이나 재활용함을 비워 보세요.',
        '진행 상황 메모 하나를 업데이트해서 다른 사람도 현황을 알 수 있게 하세요.',
        '다운로드 폴더에서 파일 몇 개만 옮겨 정리해 보세요.',
        '자주 잊어버리는 일 하나에 알림을 설정하세요.',
        '꼭 필요하지 않은 알림 하나를 꺼 보세요.',
        '자꾸 검색하게 되는 페이지 하나를 즐겨찾기에 추가하세요.',
        '기억이 생생할 때 회의 내용을 두 줄로 요약해 보세요.',
        '정기 회의 하나를 조금 줄일 수 있는지 물어보세요.',
        '앞으로 한 시간 동안의 목표 하나를 정하고 적어 보세요.',
        '동료에게 오늘 어떻게 지내는지 묻고 귀 기울여 들어 보세요.',
        '좋아할 만한 사람에게 유용한 링크를 공유해 보세요.',
        '아직 이야기해 본 적 없는 사람에게 인사해 보세요.',
        '최근에 도와준 사람에게 짧은 감사 메시지를 보내 보세요.',
        '다음 통화를 시작할 때 동료에게 따뜻하게 인사해 보세요.',
        '팀원에게 이번 주에 기대되는 일이 있는지 물어보세요.',
        '눈에 띈 작은 성과를 축하해 주세요.',
        '동료에게 차나 커피, 아니면 통화로 잠깐 이야기하자고 해 보세요.',
        '동료가 잘한 일을 구체적으로 칭찬해 보세요.',
        '자주 마주치지만 아직 이름을 모르는 사람의 이름을 알아 두세요.',
        '도움이 될 만한 팁을 필요한 팀원에게 알려 주세요.',
        '누군가에게 노래나 드라마, 책을 추천해 달라고 해 보세요.',
        '요즘 말수가 적은 동료에게 안부를 물어보세요.',
        '바빠 보이는 사람이 있으면 작은 일 하나를 돕겠다고 해 보세요.',
        '다음에 만나는 사람에게 따뜻하게 인사해 보세요.',
        '동료에 대해 들은 좋은 말을 그 사람에게 전해 주세요.',
        '동료에게 이번 주에 무엇 덕분에 일이 수월했는지 물어보세요.',
        '예전에 함께 일했던 사람에게 반가운 메시지를 보내 보세요.',
        '공용 공간을 잘 관리해 주는 분께 고맙다고 말해 보세요.',
        '서로 알면 좋을 것 같은 동료 두 사람을 소개해 주세요.',
        '팀원에게 인수인계를 어떻게 하면 더 편할지 물어보세요.',
        '가까이 있는 사람과 부담 없는 농담을 나눠 보세요.',
        '다음 "부탁해요"와 "고마워요"에 따뜻함을 조금 더 담아 보세요.',
        '동료에게 일 말고 무엇을 즐겨 하는지 물어보세요.',
        '다음에 말을 거는 사람의 이야기를 다른 일 없이 온전히 들어 보세요.',
    ),
    "done": (
        '좋아요. 하나 끝냈어요.',
        '잘했어요. 뭔가를 끝내면 기분이 좋죠.',
        '수고했어요. 다음 일 전에 잠깐 쉬어 가세요.',
        '좋아요. 작은 일도 끝내다 보면 쌓여요.',
        '끝냈어요. 뿌듯해해도 돼요.',
        '좋아요. 목록에서 하나 지웠어요.',
    ),
    "text": {
        HELP:
            """hello-world는 인사, 생각 하나, 해 볼 만한 작은 일 하나를 보여 줘요.

마지막 질문에서 plan을 입력하면 오늘 계획을 정하고, 끝내면 done,
옵션을 보려면 menu(또는 m)를 입력하세요. Enter를 누르면 닫히고,
q, x, close는 어느 질문에서든 창을 닫아요. 계획 질문에서 same을
입력하면 끝내지 못한 이전 계획을 다시 불러와요. done 다음에는
최근에 끝낸 계획 3개를 보여 줘요. 메뉴 1번은 전체를 보여 주고,
7번은 하나를 지우고, 8번은 생각과 팁을 숨겨요.
메뉴에서 Enter를 누르면 돌아가요.
hello.cmd를 다음 옵션 중 하나와 함께 실행할 수도 있어요.
  --plain         인사만 영어로 표시
  --stats         이 컴퓨터에 저장된 내용 표시
  --reset         저장된 내용 모두 삭제(먼저 물어봄)
  --remind on     로그인할 때 하루 한 번 열기(끄려면 off)
  --streak off    연속 일수 메시지 숨기기(표시하려면 on)
  --version       버전 표시
  --check-content FILE
                  조직 콘텐츠 파일 검사
  --help          이 도움말 표시

종료 코드: 0은 성공, 1은 명령이 실패했거나 화면에 쓸 수 없을 때,
2는 알 수 없는 옵션일 때예요.

저장된 메모는 이 컴퓨터의 사용자 폴더에만 있고, 어디로도 보내지
않아요. 이 컴퓨터의 파일을 읽을 수 있는 IT 담당자는 볼 수 있어요.""",
        MENU_HELP:
            """마지막 질문에서 입력할 수 있는 단어:
  done  오늘 계획을 완료로 표시하고 다음 계획을 물어요
  plan  오늘 계획을 정하거나 바꿔요
  menu  이 옵션을 열어요
  q     창을 닫아요. Enter도 마찬가지예요
계획 질문에서 same을 입력하면 끝내지 못한 이전 계획을 불러와요.
"하셨나요?"라고 물을 때 n은 아직이라는 뜻이고, 계획을 오늘도
그대로 둘 수 있어요. q는 어느 질문에서든 창을 닫아요.
이 메뉴에서 1번은 저장된 내용을 보여 주고, 7번은 완료한 계획
하나를 지우고, 8번은 생각과 팁을 숨겨요.
옵션을 다시 보려면 m을 입력하세요. 어디로도 보내지 않아요.""",
        SAVED_PLAN:
            '저장했어요. 끝내면 done을 입력하세요. 아니면 다음에 열 때 물어볼게요.',
        GREETING:
            '안녕, 세상!',
        'hello.cmd is in this folder:':
            'hello.cmd는 이 폴더에 있어요:',
        'Shortened to {n} characters.':
            '{n}자로 줄였어요.',
        'Your saved file was damaged, so hello-world set it aside as a backup copy and started fresh. Your earlier days and plan could not be read. Menu option 4 deletes the backup.':
            '저장 파일이 손상되어 hello-world가 백업 사본으로 따로 두고 새로 시작했어요. 이전 기록과 계획은 읽을 수 없었어요. 메뉴 4번으로 백업을 삭제할 수 있어요.',
        'Backup copy: ':
            '백업 사본: ',
        'In the folder: ':
            '폴더: ',
        'Sorry, "{shown}" is not one of the choices.':
            '죄송해요, "{shown}"은(는) 선택지에 없어요.',
        'A plan needs a word or two, so nothing was saved.':
            '계획은 한두 단어라도 있어야 해서 저장하지 않았어요.',
        'The sign-in reminder works on Windows only.':
            '로그인 알림은 Windows에서만 작동해요.',
        'Your organization has turned off opening at sign-in.':
            '로그인할 때 자동으로 열리는 기능은 조직에서 꺼 두었어요.',
        'The reminder cannot be set up from this folder.':
            '이 폴더에서는 알림을 설정할 수 없어요.',
        'Could not set up the reminder.':
            '알림을 설정하지 못했어요.',
        'Done. hello-world will open once a day when you sign in.':
            '설정했어요. 이제 로그인하면 하루 한 번 hello-world가 열려요.',
        'To stop it, choose option 2 in the menu.':
            '끄려면 메뉴에서 2번을 선택하세요.',
        'Could not turn off the sign-in reminder.':
            '로그인 알림을 끄지 못했어요.',
        'Done. The sign-in reminder is off.':
            '로그인 알림을 껐어요.',
        'Saved on this computer in:':
            '이 컴퓨터의 저장 위치:',
        'Saved in your own user folder on this computer.':
            '이 컴퓨터의 내 사용자 폴더에 저장돼요.',
        'Days you opened it in the last {days} days: {n} (last 7 days: {recent})':
            '최근 {days}일 동안 연 날: {n} (최근 7일: {recent})',
        'Times you marked a plan done: {n}':
            '계획을 완료한 횟수: {n}',
        'Your current plan: ':
            '현재 계획: ',
        'Earlier plan (for same): ':
            '이전 계획(same용): ',
        'Days-in-a-row message: shown.':
            '연속 일수 메시지: 표시',
        'Days-in-a-row message: hidden.':
            '연속 일수 메시지: 숨김',
        'Opens by itself at sign-in: turned off by your organization.':
            '로그인할 때 자동으로 열기: 조직에서 끔',
        'Opens by itself at sign-in: on.':
            '로그인할 때 자동으로 열기: 켜짐',
        'Opens by itself at sign-in: off.':
            '로그인할 때 자동으로 열기: 꺼짐',
        "It never leaves this computer. Others who can read this computer's files, such as IT staff, could read it.":
            '이 컴퓨터 밖으로 나가지 않아요. 다만 IT 담당자처럼 이 컴퓨터의 파일을 읽을 수 있는 사람은 볼 수 있어요.',
        'After tidying, the file holds only this:':
            '정리하고 나면 파일에는 이것만 남아요:',
        'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
            '이 컴퓨터에 저장된 메모, 날짜, 계획을 모두 삭제할까요? (y 또는 n, Enter는 취소) > ',
        'Nothing was deleted.':
            '아무것도 삭제하지 않았어요.',
        'Could not delete everything.':
            '모두 삭제하지는 못했어요.',
        'Delete these yourself:':
            '다음 항목은 직접 삭제하세요:',
        'Could not list the folder, so backup copies may remain:':
            '폴더 목록을 읽지 못해서 백업 사본이 남아 있을 수 있어요:',
        'Done. Everything saved was deleted.':
            '저장된 내용을 모두 삭제했어요.',
        'Another open hello-world window cannot put it back.':
            '열려 있는 다른 hello-world 창도 이 내용을 되살릴 수 없어요.',
        'Close any other open hello-world window, or it may save its notes again.':
            '열려 있는 다른 hello-world 창은 닫으세요. 그렇지 않으면 그 창이 메모를 다시 저장할 수 있어요.',
        'Everything saved was deleted in another window, so this was not saved.':
            '다른 창에서 저장된 내용을 모두 삭제해서 이 내용은 저장하지 않았어요.',
        'The other open window had also finished a plan.':
            '열려 있던 다른 창에서도 계획을 완료했어요.',
        'The other open window changed the plan, so its plan is kept.':
            '열려 있던 다른 창에서 계획을 바꿔서 그 계획을 유지해요.',
        'Type plan at the last prompt to set one.':
            '계획을 정하려면 마지막 질문에서 plan을 입력하세요.',
        'That looks like a command, not a plan, so nothing was saved.':
            '계획이 아니라 명령어 같아서 저장하지 않았어요.',
        'Type your plan, or press Enter to go back.':
            '계획을 입력하거나 Enter를 눌러 돌아가세요.',
        'Finished lately:':
            '최근에 끝낸 일:',
        'Your plan today: ':
            '오늘의 계획: ',
        'Your plan from {date}: ':
            '{date}의 계획: ',
        'Earlier plan: ':
            '이전 계획: ',
        'Type the next plan, or Enter to close > ':
            '다음 계획을 입력하세요. Enter는 닫기 > ',
        'Type the next plan, same to reuse the earlier plan, or Enter to close > ':
            '다음 계획을 입력하세요. same은 이전 계획 다시 쓰기, Enter는 닫기 > ',
        "Type today's plan, or Enter to keep it > ":
            '오늘 계획을 입력하세요. Enter는 그대로 두기 > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
            '오늘 계획을 입력하세요. same은 이전 계획 다시 쓰기, Enter는 그대로 두기 > ',
        "Type today's plan, or Enter to go back > ":
            '오늘 계획을 입력하세요. Enter는 돌아가기 > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
            '오늘 계획을 입력하세요. same은 이전 계획 다시 쓰기, Enter는 돌아가기 > ',
        'Closing.':
            '닫을게요.',
        'There is no earlier plan to reuse yet. Nothing changed.':
            '다시 쓸 이전 계획이 아직 없어요. 바뀐 것은 없어요.',
        'Nothing changed.':
            '바뀐 것은 없어요.',
        'Could not save that on this computer. Your plan is unchanged.':
            '이 컴퓨터에 저장하지 못했어요. 계획은 그대로예요.',
        'No finished plans are saved.':
            '저장된 완료 계획이 없어요.',
        'Type the number to forget (1 to {n}), or Enter to keep them all > ':
            '지울 번호를 입력하세요(1~{n}). Enter는 모두 두기 > ',
        'There is no number "{typed}" on the list. Type a number from 1 to {n}, or press Enter to keep them all.':
            '목록에 "{typed}"에 해당하는 번호가 없어요. 1부터 {n}까지 번호를 입력하거나 Enter를 눌러 모두 그대로 두세요.',
        'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
            'same으로 불러올 이전 계획에서도 지울까요? (y 또는 n, Enter는 same용으로 두기) > ',
        'Type y or n, or press Enter to keep it for same.':
            'y 또는 n을 입력하거나, Enter를 눌러 same용으로 두세요.',
        'That plan was already forgotten. Nothing changed.':
            '이미 지운 계획이에요. 바뀐 것은 없어요.',
        'Forgotten: ':
            '지웠어요: ',
        'Same still has it.':
            'same으로는 아직 불러올 수 있어요.',
        'Could not save that on this computer. Nothing changed.':
            '이 컴퓨터에 저장하지 못했어요. 바뀐 것은 없어요.',
        'Options':
            '옵션',
        'Show what is saved on this computer':
            '이 컴퓨터에 저장된 내용 보기',
        'Open once a day at sign-in (turned off by your organization)':
            '로그인할 때 하루 한 번 열기(조직에서 끔)',
        'Turn off: open once a day at sign-in (now on)':
            '끄기: 로그인할 때 하루 한 번 열기(현재 켜짐)',
        'Turn on: open once a day at sign-in (now off)':
            '켜기: 로그인할 때 하루 한 번 열기(현재 꺼짐)',
        'Days-in-a-row message (hidden by your organization)':
            '연속 일수 메시지(조직에서 숨김)',
        'Hide the days-in-a-row message (now shown)':
            '연속 일수 메시지 숨기기(현재 표시)',
        'Show the days-in-a-row message (now hidden)':
            '연속 일수 메시지 표시(현재 숨김)',
        'Delete everything saved':
            '저장된 내용 모두 삭제',
        'Help':
            '도움말',
        "Set today's plan (turned off by your organization)":
            '오늘 계획 정하기(조직에서 끔)',
        'Forget a finished plan (turned off by your organization)':
            '완료한 계획 지우기(조직에서 끔)',
        "Set or change today's plan":
            '오늘 계획 정하기 또는 바꾸기',
        'Forget one finished plan':
            '완료한 계획 하나 지우기',
        'Thought and tip (hidden by your organization)':
            '생각과 팁(조직에서 숨김)',
        'Hide the thought and tip (now shown)':
            '생각과 팁 숨기기(현재 표시)',
        'Show the thought and tip (now hidden)':
            '생각과 팁 표시(현재 숨김)',
        '{date}: ':
            '{date}: ',
        'Enter':
            'Enter',
        'Back to the last prompt':
            '마지막 질문으로 돌아가기',
        'Choose 1 to 11, or Enter to go back > ':
            '1~11 중에서 선택하세요. Enter는 돌아가기 > ',
        'Choose 1 to 11, m to list the options, or Enter to go back > ':
            '1~11 중에서 선택하세요. m은 옵션 목록, Enter는 돌아가기 > ',
        'The saved file could not be read just now, so this may be out of date.':
            '지금은 저장 파일을 읽지 못해서 최신 내용이 아닐 수 있어요.',
        'Type full to see the whole file, or Enter to go on > ':
            '전체 파일을 보려면 full, 계속하려면 Enter > ',
        'Could not save that choice on this computer.':
            '이 선택을 이 컴퓨터에 저장하지 못했어요.',
        'Your organization has hidden the days-in-a-row message.':
            '조직에서 연속 일수 메시지를 숨겼어요.',
        'Done. The days-in-a-row message is on.':
            '연속 일수 메시지를 켰어요.',
        'Done. The days-in-a-row message is off.':
            '연속 일수 메시지를 껐어요.',
        'Plans are turned off by your organization.':
            '조직에서 계획 기능을 껐어요.',
        'Your organization has hidden the thought and tip.':
            '조직에서 생각과 팁을 숨겼어요.',
        'Done. The thought and tip are on.':
            '생각과 팁을 켰어요.',
        'Done. The thought and tip are off.':
            '생각과 팁을 껐어요.',
        'Type 1 to 11, or press Enter to go back.':
            '1~11 중에서 입력하거나 Enter를 눌러 돌아가세요.',
        'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
            '로그인할 때 하루 한 번 열리게 할까요? (y 또는 n, Enter는 나중에) > ',
        'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
            '로그인할 때 하루 한 번 열어서 계획을 물어볼까요? (y 또는 n, Enter는 나중에) > ',
        'Type y or n, or press Enter for not now.':
            'y 또는 n을 입력하세요. 나중에 하려면 Enter를 누르세요.',
        'That was not understood. It will ask again on a later visit.':
            '알아듣지 못했어요. 다음에 다시 물어볼게요.',
        'It will ask again on a later visit. Menu option 2 also turns it on.':
            '다음에 다시 물어볼게요. 메뉴 2번으로 켤 수도 있어요.',
        'No problem. Menu option 2 turns it on later.':
            '괜찮아요. 나중에 메뉴 2번으로 켤 수 있어요.',
        "Okay. It won't ask again. Menu option 2 turns it on.":
            '알겠어요. 다시 묻지 않을게요. 메뉴 2번으로 켤 수 있어요.',
        'Okay. It will ask again on a later visit. Type n to stop it.':
            '알겠어요. 다음에 다시 물어볼게요. 그만 물으려면 n을 입력하세요.',
        'When did you finish it?':
            '언제 끝냈나요?',
        'Today':
            '오늘',
        'Type a number from 1 to {n}, or Enter for 1 > ':
            '1부터 {n}까지 번호를 입력하세요. Enter는 1 > ',
        'Type a number from 1 to {n}, or press Enter.':
            '1부터 {n}까지 번호를 입력하거나 Enter를 누르세요.',
        'That looks like more than one thing. Finishing the first part still counts.':
            '여러 가지가 섞여 있는 것 같아요. 첫 번째만 끝내도 완료로 쳐요.',
        'There is no plan to mark as done. Type plan to set one.':
            '완료로 표시할 계획이 없어요. 계획을 정하려면 plan을 입력하세요.',
        'Could not save that on this computer. The plan is still open.':
            '이 컴퓨터에 저장하지 못했어요. 계획은 아직 진행 중이에요.',
        'Your plan from over two weeks ago was put away. Type same at the plan prompt to bring it back.':
            '2주 넘게 지난 계획은 따로 넣어 뒀어요. 계획 질문에서 same을 입력하면 다시 불러올 수 있어요.',
        "Press Enter at each question to skip it, and once more to close. That's it.":
            '질문마다 Enter를 누르면 건너뛰고, 한 번 더 누르면 닫혀요. 이게 다예요.',
        'Welcome.':
            '환영해요.',
        'Each day you get one thought and one small thing to try, the same for everyone.':
            '날마다 생각 하나와 해 볼 만한 작은 일 하나를 보여 드려요. 모두에게 같은 내용이에요.',
        'If you type a plan, it asks next time how it went. Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks.':
            '계획을 입력하면 다음번에 어떻게 됐는지 물어봐요. 메모는 이 컴퓨터에만 있고 어디로도 보내지 않아요. 다만 다른 업무 파일처럼 비밀은 아니니 평범한 업무 내용만 적어 주세요.',
        'Type menu at the end for the options.':
            '옵션을 보려면 마지막에 menu를 입력하세요.',
        'Welcome back. Glad you are here.':
            '다시 오셨네요. 반가워요.',
        'You have opened this {row} days in a row. Nice to see you.':
            '{row}일 연속으로 열었어요. 오늘도 만나서 좋네요.',
        'Last time you planned: ':
            '지난번 계획: ',
        'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
            '하셨나요? (y는 예, n은 아직, Enter는 건너뛰기) > ',
        'Type y or n, or press Enter to skip.':
            'y 또는 n을 입력하거나 Enter를 눌러 건너뛰세요.',
        'Could not save that on this computer. Your answer was not counted.':
            '이 컴퓨터에 저장하지 못해서 답이 반영되지 않았어요.',
        'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
            '괜찮아요. 오늘도 이 계획으로 할까요? (y 또는 n, Enter는 그대로 두기) > ',
        'Type y to keep it, n to clear it, or press Enter to keep it.':
            '그대로 두려면 y, 지우려면 n을 입력하세요. Enter를 눌러도 그대로 둬요.',
        'Cleared. Type same at a plan prompt if you want it back.':
            '지웠어요. 다시 쓰려면 계획 질문에서 same을 입력하세요.',
        'Kept for today.':
            '오늘도 그대로 둘게요.',
        'That was not understood. Your plan is left as it was.':
            '알아듣지 못했어요. 계획은 그대로 뒀어요.',
        'Your plan is still open.':
            '계획이 아직 진행 중이에요.',
        'Thought for today:':
            '오늘의 생각:',
        'Try this today:':
            '오늘 해 볼 일:',
        'Your plan for today: ':
            '오늘의 계획: ',
        'Still open since {date}:':
            '{date}부터 진행 중:',
        '(Enter to skip)':
            '(Enter는 건너뛰기)',
        '(A plan typed here replaces the old one. Enter to skip)':
            '(여기에 입력하면 기존 계획이 바뀌어요. Enter는 건너뛰기)',
        '(Type same to reuse it, or Enter to skip)':
            '(same을 입력하면 다시 쓰고, Enter는 건너뛰기)',
        'What is one thing you want to get done today?':
            '오늘 끝내고 싶은 일 하나가 있나요?',
        'There is no earlier plan to reuse yet. Nothing was saved.':
            '다시 쓸 이전 계획이 아직 없어요. 저장하지 않았어요.',
        'Your notes could not be saved on this computer. This screen still works.':
            '메모를 이 컴퓨터에 저장할 수 없어요. 이 화면은 그대로 쓸 수 있어요.',
        'Type menu, or Enter to close > ':
            'menu를 입력하세요. Enter는 닫기 > ',
        'Type done, plan or menu, or Enter to close > ':
            'done, plan, menu 중 하나를 입력하세요. Enter는 닫기 > ',
        'Type plan or menu, or Enter to close > ':
            'plan 또는 menu를 입력하세요. Enter는 닫기 > ',
        'Type done, plan or menu, or press Enter to close.':
            'done, plan, menu 중 하나를 입력하거나 Enter를 눌러 닫으세요.',
        'Type plan or menu, or press Enter to close.':
            'plan 또는 menu를 입력하거나 Enter를 눌러 닫으세요.',
        "The saved file can't be read right now, or it is damaged.":
            '지금은 저장 파일을 읽을 수 없거나 파일이 손상됐어요.',
        'Nothing was changed. Saved in: ':
            '바뀐 것은 없어요. 저장 위치: ',
        'Deleting saved notes needs a person at the keyboard.':
            '저장된 메모를 삭제하려면 키보드 앞에 사람이 있어야 해요.',
        '{option} needs on or off. Here are the options.':
            '{option}에는 on 또는 off가 필요해요. 옵션은 다음과 같아요.',
        'Unknown option: {option}. Here are the options.':
            '알 수 없는 옵션: {option}. 옵션은 다음과 같아요.',
        '&Done':
            '완료(&D)',
        '&Not yet':
            '아직(&N)',
        'S&kip':
            '건너뛰기(&K)',
        '&Save':
            '저장(&S)',
        '&I did it':
            '했어요(&I)',
        '&Options':
            '옵션(&O)',
        'Close':
            '닫기',
        'Not today':
            '오늘은 안 할게요',
        'Did you do it?':
            '하셨나요?',
        'Done. A reminder comes when you sign in, if there is a plan to ask about.':
            '설정했어요. 물어볼 계획이 있으면 로그인할 때 알림이 와요.',
        'Done. The Start menu opens a window with buttons.':
            '설정했어요. 이제 시작 메뉴에서 열면 버튼이 있는 창이 열려요.',
        'Done. The Start menu opens this text screen.':
            '설정했어요. 이제 시작 메뉴에서 열면 이 텍스트 화면이 열려요.',
        'More options':
            '옵션 더 보기',
        'Remind me when I sign in':
            '로그인할 때 알려 주기',
        'Show the thought and tip':
            '생각과 팁 표시',
        'Type your plan in the box.':
            '상자에 계획을 입력하세요.',
        'Use a window with buttons (now this text screen)':
            '버튼이 있는 창 사용(현재 텍스트 화면)',
        'Use the text screen':
            '텍스트 화면 사용',
        'Use this text screen (now a window with buttons)':
            '이 텍스트 화면 사용(현재 버튼이 있는 창)',
        'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
            '로그인할 때 알림을 받을까요? 지난번 계획을 보여 주고, 클릭 한 번으로 답할 수 있어요. 옵션에서 끌 수 있어요.',
        'Window or text screen (set by your organization)':
            '창 또는 텍스트 화면(조직에서 설정)',
        'Your organization has set hello-world to open as a text screen.':
            '조직에서 hello-world를 텍스트 화면으로 열도록 설정했어요.',
        'Saved.':
            '저장했어요.',
        'Save your plan before closing?':
            '닫기 전에 계획을 저장할까요?',
        'Delete all saved notes, dates and plans on this computer?':
            '이 컴퓨터에 저장된 메모, 날짜, 계획을 모두 삭제할까요?',
        'Turn off: reminder when you sign in (now on)':
            '끄기: 로그인 알림(현재 켜짐)',
        'Turn on: reminder when you sign in (now off)':
            '켜기: 로그인 알림(현재 꺼짐)',
        'Reminder when you sign in (turned off by your organization)':
            '로그인 알림(조직에서 끔)',
        'Reminder when you sign in: on.':
            '로그인 알림: 켜짐',
        'Reminder when you sign in: off.':
            '로그인 알림: 꺼짐',
        'Reminder when you sign in: turned off by your organization.':
            '로그인 알림: 조직에서 끔',
        'Show the days-in-a-row message':
            '연속 일수 메시지 표시',
        'Done. The thought and tip show next time you open hello-world.':
            '설정했어요. 다음에 hello-world를 열면 생각과 팁이 보여요.',
        "Clear today's plan?":
            '오늘 계획을 지울까요?',
        'Next plan, if you want one:':
            '원하면 다음 계획도 적어 보세요:',
        'A few things? Put ; between them.':
            '여러 가지인가요? 사이에 ;를 넣으세요.',
        'A plan can be up to {n} characters.':
            '계획은 {n}자까지 쓸 수 있어요.',
        'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
            '하셨나요? (y는 전부, n은 아직, 한 일은 번호로, Enter는 건너뛰기) > ',
        'Last time you planned:':
            '지난번 계획:',
        'The rest is kept for today.':
            '나머지는 오늘도 그대로 둬요.',
        'Tick the ones you did, then click Done. With none ticked, Done means all of them.':
            '한 일에 체크한 다음 완료를 클릭하세요. 아무것도 체크하지 않으면 전부 완료로 처리해요.',
        'Type y for all, n for not yet, or the numbers you did, such as 1 3. Enter skips.':
            '전부 했으면 y, 아직이면 n, 일부만 했으면 1 3처럼 번호를 입력하세요. Enter는 건너뛰기예요.',
        'Your settings were kept.':
            '설정은 그대로 뒀어요.',
        'Language (set by your organization)':
            '언어(조직에서 설정)',
        'Language (now {name})':
            '언어(현재 {name})',
        'following Windows':
            'Windows 설정 따름',
        'Your organization shows hello-world in English.':
            '조직에서 hello-world를 영어로 표시하도록 설정했어요.',
        'Follow Windows':
            'Windows 설정 따르기',
        'Type a number from 1 to {n}, or Enter to keep it > ':
            '1부터 {n}까지 번호를 입력하세요. Enter는 그대로 두기 > ',
        'Done. The new language shows next time you open hello-world.':
            '설정했어요. 다음에 hello-world를 열면 새 언어로 보여요.',
        'Language...':
            '언어...',
        'Hello, {name}!':
            '{name}님, 안녕하세요!',
        'One thing to get done today? Open hello-world to plan it.':
            '오늘 끝낼 일 하나 있나요? hello-world를 열어 계획해 보세요.',
        '&Open':
            '열기(&O)',
        'Reminder settings...':
            '알림 설정...',
        'Greet me by name':
            '이름으로 인사하기',
        'At sign-in':
            '로그인할 때',
        'At {at}':
            '{at}에',
        'Also on days with no plan':
            '계획이 없는 날에도',
        'Open hello-world after I answer':
            '답한 다음 hello-world 열기',
        'Not on weekends':
            '주말 제외',
        'Done. A reminder comes at {at} each day, if there is a plan to ask about.':
            '설정했어요. 물어볼 계획이 있으면 매일 {at}에 알림이 와요.',
        'Send feedback...':
            '의견 보내기...',
        '"holidays" must be a list of at most {n} dates.':
            '"holidays"는 날짜가 최대 {n}개인 목록이어야 합니다.',
        '"title" must be 1 to 40 characters of plain text, with no link or address.':
            '"title"은 링크나 주소가 없는 일반 텍스트로 1~40자여야 합니다.',
        '"{list}" must be a list of {low} to {high} lines.':
            '"{list}"은(는) {low}~{high}줄인 목록이어야 합니다.',
        "Can't read {path}: {error}":
            '{path}을(를) 읽을 수 없습니다: {error}',
        'Could not save that on this computer.':
            '이 컴퓨터에 저장하지 못했어요.',
        'Days you opened hello-world: {n}':
            'hello-world를 연 날: {n}',
        'Keep a longer history':
            '기록을 더 오래 보관하기',
        'Keep my numbers':
            '내 통계 보관하기',
        'Longest run of days: {n}':
            '최장 연속 일수: {n}',
        "Mark today's plan done":
            '오늘 계획 완료로 표시',
        "Mark today's plan done (plans are turned off)":
            '오늘 계획 완료로 표시(계획 기능 꺼짐)',
        'My numbers are off. Turn them on under Options, or with --set numbers on.':
            '내 통계가 꺼져 있어요. 옵션에서 켜거나 --set numbers on으로 켜세요.',
        'My numbers...':
            '내 통계...',
        'Nothing finished yet this week. That is fine.':
            '이번 주에는 아직 끝낸 일이 없어요. 괜찮아요.',
        'OK: {thoughts} thoughts and {tips} tips.':
            'OK: 생각 {thoughts}개, 팁 {tips}개.',
        'Plans finished: {n}':
            '끝낸 계획: {n}',
        'Save my plans to a file':
            '내 계획을 파일로 저장',
        'Saved to {path}':
            '{path}에 저장했어요',
        "The file isn't valid JSON, or is over 200,000 characters.":
            '올바른 JSON 파일이 아니거나 200,000자를 넘습니다.',
        'The file must hold an object with two lists, "thoughts" and "tips", and may add "holidays" and "title".':
            '파일에는 "thoughts"와 "tips" 두 목록이 있는 객체가 있어야 하며, "holidays"와 "title"을 추가할 수 있습니다.',
        'This week you finished {n}:':
            '이번 주에 끝낸 일 {n}개:',
        'This week...':
            '이번 주...',
        'holidays line {line} is not a date like 2026-12-25.':
            'holidays {line}번째 줄이 2026-12-25 같은 날짜 형식이 아닙니다.',
        '{list} line {line} has a date.':
            '{list} {line}번째 줄에 날짜가 있습니다.',
        '{list} line {line} has a link or an address.':
            '{list} {line}번째 줄에 링크나 주소가 있습니다.',
        '{list} line {line} has control characters or extra spaces.':
            '{list} {line}번째 줄에 제어 문자나 불필요한 공백이 있습니다.',
        '{list} line {line} is not text.':
            '{list} {line}번째 줄이 텍스트가 아닙니다.',
        '{list} line {line} must be {low} to {high} characters long.':
            '{list} {line}번째 줄은 {low}~{high}자여야 합니다.',
    },
}

# ---- Hebrew ----

LANGUAGES["he"] = {
    "days": ('יום שני', 'יום שלישי', 'יום רביעי', 'יום חמישי', 'יום שישי', 'שבת', 'יום ראשון'),
    "months": ('ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני', 'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'),
    "date": '{day}, {d} ב{month} {year}',
    "thoughts": (
        'לפתוח את המסמך שנדחה כבר זמן מה ולקרוא רק את הפסקה הראשונה.',
        'התחלה של עשר דקות היא עדיין התחלה, ובדרך כלל היא מקלה על עשר הדקות הבאות.',
        'לא צריך את כל התוכנית היום, רק צעד ראשון הגיוני.',
        'לכתוב את המשפט הראשון, גם אם הוא מכוער. כך יש משהו אמיתי לשפר אחר כך.',
        'לפנות פינה קטנה אחת בשולחן ולשים לב כמה רגוע יותר כל השאר.',
        'לבחור את המשימה הקטנה ביותר ברשימה ולסיים אותה לפני שמסתכלים על האחרות.',
        'התחלה עקומה בבוקר שקט עדיפה על המתנה לרגע מושלם שאולי לא יגיע.',
        'לשים את הצעד הראשון ביומן, כדי שיהיה לו מקום משלו.',
        'פרויקט גדול בנוי בעיקר מהרבה שעות עבודה קטנות, אז מספיק לכוון לאחר צהריים אחד.',
        'לומר בקול רק את הפעולה הבאה, ולתת לשאר הרשימה לחכות לתורה.',
        'יש ימים שהקצב איטי יותר מהרצוי, וגם הקצב הזה נחשב.',
        'לדבר אל עצמנו כמו אל עמית חדש בשבוע הראשון שלו.',
        'מותר עדיין ללמוד משהו שעושים כבר שנים.',
        'בוקר חלש לא קובע את אחר הצהריים. אפשר להתחיל מחדש אחרי ארוחת הצהריים.',
        'עייפות היא מידע, לא כישלון. מעדכנים את התוכנית וממשיכים בעדינות.',
        'לתת לעצמנו את אותה חמלה שאנחנו נותנים לאחרים כל כך בקלות.',
        'התקדמות נראית הרבה פעמים כמו כלום לזמן מה, ואז פתאום כמו עמוד גמור.',
        'זה בסדר לקרוא פעמיים לפני שהדברים מתבהרים.',
        'לא צריך להרגיש מוכנים. לעשות את זה עם קצת פחד זה עדיין לעשות.',
        'המיטב של היום יכול להיות קטן מהמיטב של אתמול, וזה בסדר.',
        'לסגור את הלשוניות שלא בשימוש. הריכוז יודה על כך תוך כמה דקות.',
        'משימה אחת, חלון אחד, עשרים וחמש דקות. לבדוק כמה רחוק מגיעים ברצף שקט.',
        'לרשום את המחשבה שקופצת פתאום, ואז לחזור למה שעשינו.',
        'אם אפשר, להשתיק את הטלפון לשעה ולתת לעבודה את מלוא תשומת הלב.',
        'להחליט מה הדבר האחד שיהפוך את היום לטוב, ולשמור לו זמן.',
        'לעשות דבר אחד בכל פעם בדרך כלל מהיר יותר ממה שזה מרגיש.',
        'רשימה מסודרת של שלושה דברים עדיפה על רשימה מפוזרת של עשרים.',
        'לשים לב כשהמחשבות נודדות, ולהחזיר אותן בלי לנזוף.',
        'לשבץ את המשימה הקשה ביותר בשעה שבה יש הכי הרבה אנרגיה, גם אם זה לא הדבר הראשון בבוקר.',
        'אוזניות על הראש, קומקום מלא, דלת סגורה. מכינים את הסביבה, והריכוז מגיע אחריה.',
        'להתרחק מהמסך לחמש דקות. חוזרים קצת יותר צלולים.',
        'לאכול היום צהריים לא ליד השולחן. תיבת הדואר יכולה לחכות לכריך.',
        'הליכה קצרה סביב הבניין היא עבודה אמיתית בשביל הראש.',
        'דקה הרחק מהמסך היא שימוש טוב באחר צהריים עמוס.',
        'למתוח את הכתפיים ולשחרר את הלסת. ייתכן שהן מכווצות כבר שעות.',
        'לצאת בזמן הערב, אם אפשר. ערב פנוי היום הוא מתנה למחר.',
        'מנוחה היא חלק מהעבודה, כי אנשים עייפים נוטים לחזור על אותה טעות פעמיים.',
        'לתת לעיניים לנוח לרגע ולהוריד את הכתפיים.',
        'הפסקה אמיתית הופכת את החצי השני של היום להתחלה חדשה.',
        'הערב הוא זמן פרטי. שום דבר בתיבת הדואר לא דחוף בתשע בערב.',
        'להגיד היום תודה למישהו על דבר קטן שעשה בלי שביקשו ממנו.',
        'רוב האנשים עושים כמיטב יכולתם, עם יותר על הצלחת ממה שרואים מבחוץ.',
        'לברר איך עמית אוהב את התה או הקפה שלו. מתנה קטנה לזכור את זה.',
        'אם מישהו עונה בקוצר רוח, כנראה עובר עליו יום קשה. זה לא שיפוט אישי.',
        'להחזיק את הדלת, לחלוק את העוגיות ולתת למישהו לסיים את המשפט.',
        'שלום קצר ושאלה על סוף השבוע יכולים להיות החלק הכי נעים בבוקר.',
        'כשמישהו חדש שואל משהו מובן מאליו, לזכור שפעם גם אנחנו שאלנו את זה.',
        'לתת קרדיט בקול כשרעיון של חבר צוות שיפר את העבודה שלנו.',
        'לענות להודעה עם קצת חום. זה לא עולה כלום ומתקבל בנעימות.',
        'לפנות לעמית שהיה שקט בישיבות לאחרונה ולשאול מה שלומו.',
        'לסיים את מה שכמעט גמור לפני שמתחילים משהו חדש.',
        'גמור וטוב מספיק שימושי בדרך כלל יותר ממושלם ולא גמור.',
        'לסגור היום עניין פתוח אחד ולשים לב להקלה הקטנה שבאה אחריו.',
        'עשרת האחוזים האחרונים הם לרוב רק כמה דקות של תשומת לב. אפשר לתת אותן היום.',
        'לשלוח את המייל שמחכה בטיוטות. כנראה הוא בסדר כמו שהוא.',
        'לסמן שהושלם, לנשום, ולשמוח שזה מאחורינו.',
        'דבר קטן שהושלם שווה יותר מדבר גדול שנעשה עד חציו.',
        'לפני סיום היום, לרשום על פתק את הצעד הראשון של מחר, כדי שלא יהיה צריך לזכור אותו.',
        'לקרוא עוד פעם, לתקן את מה שמוצאים, ואז לשלוח.',
        'סיום היום עם תוצאה מסודרת אחת עושה את הערב קל יותר.',
        'שאלה מוקדמת חוסכת בדרך כלל שעה של התלבטות שקטה בהמשך.',
        'רוב האנשים נהנים כשפונים אליהם בגלל הידע שלהם. אפשר לשאול בלי להתנצל.',
        '"נתקעתי" זה משפט ברור ושימושי שעמיתים יכולים לעבוד איתו.',
        'לבקש את מה שצריך במילים פשוטות, ולתת לאנשים הזדמנות להגיד כן.',
        'שני אנשים שמסתכלים על בעיה פותרים אותה לרוב מהר יותר מאדם אחד שבוהה בה לבד.',
        'לבקש עזרה זה לא להיות נטל. ככה עובד צוות.',
        'עם שאלה ממוקדת, אפשר לקבל תשובה ממוקדת.',
        'אם ההנחיות לא ברורות, לבקש הבהרה זה חלק מלעשות את העבודה כמו שצריך.',
        'להציע עזרה כשאפשר ולקבל אותה כשצריך. שני הדברים נעשים קלים יותר עם הזמן.',
        'מישהו במסדרון כנראה כבר פתר את זה בעבר. שווה ללכת לחפש אותו.',
        'לרשום בפתק קטן דברים שהתבררו השבוע. זה מצטבר ליותר ממה שנדמה.',
        'להיות בהתחלה של משהו חדש זה סימן שעדיין מתפתחים בעבודה.',
        'לשים לב איך עמית שמעריכים מתמודד עם שיחה מסובכת, ולאמץ ממנו דבר אחד.',
        'לקרוא עמוד אחד מועיל בהפסקה. זה כבר יום טוב לראש.',
        'להסביר משימה למישהו אחר זו דרך טובה להפליא ללמוד אותה בעצמנו.',
        'זה בסדר להגיד "את זה עוד לא למדתי", ואז ללכת לברר.',
        'כל מערכת לא מוכרת נראית מבלבלת עד שמשתמשים בה כמה פעמים.',
        'לשאול מישהו מנוסה יותר איך הוא למד את זה. התשובה לרוב מרגיעה.',
        'מיומנות באה מחזרה, אז חוזרים על הדבר הקטן עד שהוא נעשה קל.',
        'קצת סקרנות לגבי משימה רגילה יכולה להפוך אותה למעניינת יותר.',
        'טעות שנתפסת מוקדם היא רק תיקון, ורוב הטעויות נתפסות מוקדם.',
        'לתקן, לעדכן את מי שצריך לדעת, ולתת לעקיצה לחלוף.',
        'כמעט כל טעות בעבודה נראית קטנה יותר אחרי שבוע מאשר ברגע עצמו.',
        'מעידה אחת לא מוחקת שנים של עבודה קפדנית.',
        'כשמשהו משתבש, לבדוק קודם את התהליך ורק אחר כך את האדם.',
        'כל מי שסביבנו שלח לפחות פעם אחת מייל לאדם הלא נכון.',
        'לקחת מהטעות את הלקח האחד שלה ולהשאיר את כל השאר מאחור.',
        'לקחת אחריות על טעות בפשטות בונה לרוב יותר אמון מאשר לא לטעות אף פעם.',
        'גם לאנשים זהירים יש ימים מגושמים, והם חולפים עד הערב.',
        'בעוד חודש, רוב המעידות הקטנות של היום כבר יישכחו.',
        'יום שקט שבו שום דבר לא בוער הוא יום טוב, גם אם אף אחד לא מזכיר את זה.',
        'לשים לב להנאות הקטנות: ספל חם, תיבת דואר ריקה, דקה של שקט.',
        'לא כל יום צריך ניצחון גדול. יציב ונעים זו דרך טובה לעבוד.',
        'ליהנות מישיבה שמסתיימת חמש דקות מוקדם ולנצל את הזמן איך שרוצים.',
        'יום רגיל שנעשה היטב הוא סיבה לגאווה שקטה.',
        'עבודה טובה נראית לרוב לא מרשימה מבחוץ, וזה בסדר.',
        'לתת לאחר צהריים נעים להיות פשוט נעים, בלי לחכות שיהיה פרודוקטיבי.',
        'השגרות הקטנות של היום, הקפה הראשון והפרצופים המוכרים, שוות תשומת לב.',
        'היום הגענו ועשינו את החלק שלנו, וזה די והותר.',
        'לקחת רגע הערב כדי להיזכר בדבר אחד שהלך טוב היום.',
        'דקה שקטה בין שתי משימות היא לא בזבוז; ככה המשימה הבאה מתחילה טוב.',
    ),
    "tips": (
        'ללגום כוס מים לאט, הרחק מהמסך.',
        'לגלגל את הכתפיים לאחור חמש פעמים, לאט ובנחת.',
        'לתת לעיניים לנוח עשרים שניות: להסתכל רחוק, או לעצום אותן.',
        'למתוח את הידיים מעל הראש, בישיבה או בעמידה, ולנשום עמוק.',
        'להגיע לחדר או לחלון הרחוקים ביותר שאפשר, ולחזור.',
        'לבדוק את היציבה ולהוריד את הכתפיים הרחק מהאוזניים.',
        'לסובב את הצוואר בעדינות מצד לצד, רק עד כמה שנוח.',
        'לפתוח ולסגור את כפות הידיים עשר פעמים כדי לשחרר את האצבעות.',
        'להצמיד את המסמך שנפתח הכי הרבה, כדי שיהיה במרחק לחיצה.',
        'לצאת לסיבוב קצר בחוץ, בכל דרך שמתאימה.',
        'למזוג משקה חם או קר וליהנות ממנו הרחק מהמסך.',
        'להתמקד במשהו רגוע: נוף, צליל או מרקם.',
        'לרשום את הצעד הבא במשימה אחת שנשארה באמצע.',
        'להניח את שתי כפות הרגליים על הרצפה ולשבת זקוף, או לעמוד זקוף, לעשר נשימות.',
        "להשתיק קבוצת צ'אט אחת שרק מרפרפים עליה.",
        'לשחרר את הלסת ולהרפות את המצח לרגע.',
        'לזוז שתי דקות בכל דרך שמרגישה טוב היום.',
        'לשריין ביומן רבע שעה למשימה שכל הזמן נדחית.',
        'לכוונן את הכיסא, המסך או המקלדת כך שדבר אחד יהיה נוח יותר.',
        'ללכת בדרך הארוכה לישיבה או לשיחה הבאה, אם אפשר.',
        'לשמור תבנית למייל אחד שנכתב שוב ושוב.',
        'ללמוד קיצור מקשים אחד בתוכנה שעובדים בה הכי הרבה.',
        'לשתות כוס מים מלאה לפני הקפה או התה הבא.',
        'להרים את הכתפיים עד האוזניים, ואז לתת להן לרדת לאט.',
        'לצאת החוצה או לפתוח חלון לדקה של אוויר צח.',
        'לקחת חמש נשימות איטיות, וכל נשיפה קצת יותר ארוכה.',
        'לעצור לדקה של שקט לפני שפותחים את ההודעה הבאה.',
        'לרשום דבר טוב אחד שקרה היום עד עכשיו.',
        'לעצום עיניים לשלוש נשימות ולשים לב להרגשה.',
        'לשים לב עכשיו לשלושה דברים, בכל חוש שהוא.',
        'לרשום דבר אחד שמחכים לו השבוע.',
        'לכוון טיימר לשתי דקות ופשוט לשבת בלי מסך.',
        'ליהנות ממשהו קטן בסביבה, כמו עציץ או ספל אהוב.',
        'להיזכר בדבר אחד שהצליח השבוע ולטפוח לעצמנו על השכם.',
        'להאזין לשיר אהוב אחד מההתחלה ועד הסוף, בלי שום דבר אחר פתוח.',
        'לשאוף בספירה עד ארבע ולנשוף בספירה עד שש, שלוש פעמים.',
        'לקחת נשימה אחת לפני שמגיבים למטרד הקטן הבא.',
        'לרשום דבר אחד שהצחיק לאחרונה.',
        'במשך דקה, לשים לב למשהו נעים: צליל, ריח או מגע.',
        'להיזכר במקום אהוב ולדמיין אותו שלושים שניות.',
        'להגיד "מספיק טוב בינתיים" על משימה קטנה אחת ולהמשיך הלאה.',
        'לכתוב משפט אחד על משהו שמודים עליו.',
        'ליהנות מהלגימה הבאה ולשים לב לטעם.',
        'לקחת הפסקה קצרה בין שתי משימות לפני שמתחילים את הבאה.',
        'לחפש היום דבר אחד שיוצא טוב מהצפוי.',
        'לבחור מילה אחת שמתארת איך אחר הצהריים אמור להרגיש.',
        'לתת לראש לנוח שישים שניות, ואז לחזור למשימה הבאה.',
        'לשים לב לכפות הרגליים על הרצפה ולהרגיש יציבות לרגע.',
        'להיזכר במעשה טוב שמישהו עשה פעם וליהנות מהזיכרון.',
        'לרשום רעיון אחד שכדאי לחזור אליו אחר כך, ולהניח לו.',
        'לסדר פינה קטנה אחת בשולחן, רק אחת.',
        'לענות להודעה אחת שמחכה כבר זמן מה.',
        'לרשום את המשימה החשובה של מחר על פתק דביק או בהערות.',
        'לסגור את לשוניות הדפדפן שכבר לא צריך.',
        'להגיד תודה לעמית על משהו שעשה לאחרונה.',
        'להעביר לארכיון חמישה מיילים ישנים שכבר לא צריך.',
        'לשנות שם לקובץ מבולגן אחד כדי שיהיה קל למצוא אותו אחר כך.',
        'לפנות קובץ או שניים משולחן העבודה.',
        'למחוק תזכורת ישנה אחת שכבר לא רלוונטית.',
        'לתת כותרת ברורה למסמך שנפתח הרבה.',
        'לסמן כבוצע פריט קטן אחד ברשימת המשימות.',
        'לבטל מינוי לניוזלטר אחד שאף פעם לא נקרא.',
        'לנגב את המקלדת או המסך במטלית רכה.',
        'לשים עט, מחברת ומים במקום שקל להגיע אליו.',
        'לכתוב פתק קצר לעצמנו של מחר על המקום שבו עצרנו היום.',
        'לבחור את המשימה החשובה ביותר אחר הצהריים ולעשות אותה ראשונה.',
        'לרוקן את פח המיחזור או האשפה ליד השולחן.',
        'לעדכן הערת התקדמות אחת כדי שאחרים יראו איפה הדברים עומדים.',
        'לסדר קצת את תיקיית ההורדות ולהעביר ממנה חופן קבצים אחד.',
        'להגדיר תזכורת לדבר אחד שנוטים לשכוח.',
        'לכבות התראה אחת שלא באמת צריך.',
        'לשמור בסימניות עמוד אחד שכל הזמן מחפשים.',
        'לכתוב סיכום של שתי שורות לישיבה כל עוד היא טרייה.',
        'לשאול אם אפשר לקצר קצת ישיבה קבועה אחת.',
        'לקבוע מטרה אחת לשעה הקרובה ולרשום אותה.',
        'לשאול עמית איך עובר עליו היום ולהקשיב באמת.',
        'לשתף קישור שימושי עם מישהו שעשוי ליהנות ממנו.',
        'להגיד שלום למישהו שעוד לא יצא לדבר איתו.',
        'לשלוח הודעת תודה קצרה למישהו שעזר לאחרונה.',
        'לברך עמית בחום בתחילת השיחה הבאה.',
        'לשאול חבר צוות למה הוא מחכה השבוע.',
        'לפרגן למישהו על הצלחה קטנה.',
        'להזמין עמית לשיחה קצרה, על כוס תה או קפה או בטלפון.',
        'להחמיא לעמית על משהו מסוים שעשה טוב.',
        'ללמוד את השם של מישהו שרואים הרבה אבל עוד לא מכירים.',
        'לשתף טיפ שימושי עם חבר צוות שאולי צריך אותו.',
        'לבקש ממישהו המלצה על שיר, סדרה או ספר.',
        'לבדוק מה שלומו של עמית שהיה שקט לאחרונה.',
        'להציע עזרה בדבר קטן אחד אם מישהו נראה עמוס.',
        'לברך את האדם הבא שפוגשים בשלום חם.',
        'להעביר הלאה מילה טובה שנאמרה על עמית.',
        'לשאול עמית מה הקל עליו השבוע.',
        'לשלוח הודעה ידידותית למישהו שעבדו איתו פעם.',
        'להודות למי שדואג שהמרחבים המשותפים יתפקדו כמו שצריך.',
        'להכיר בין שני עמיתים שעשויים ליהנות מההיכרות.',
        'לשאול חבר צוות איך להקל עליו בהעברת עבודה.',
        'לשתף בדיחה קטנה ותמימה עם מישהו בסביבה.',
        'להוסיף קצת יותר חום ל"בבקשה" ול"תודה" הבאים.',
        'לשאול עמית מה הוא אוהב לעשות מחוץ לעבודה.',
        'להקשיב עד הסוף לאדם הבא שמדבר, בלי לעשות דברים אחרים במקביל.',
    ),
    "done": (
        'יופי. זה הושלם.',
        'נהדר. טוב לסיים משהו.',
        'כל הכבוד. כדאי לקחת הפסקה קצרה לפני הדבר הבא.',
        'יופי. משימות קטנות שהושלמו מצטברות.',
        'זה גמור. אפשר להיות מרוצים מזה.',
        'יופי. עוד דבר ירד מהרשימה.',
    ),
    "text": {
        HELP:
            """hello-world מציג ברכה, מחשבה ודבר קטן לנסות.

בשאלה האחרונה, להקליד plan לתוכנית של היום, done בסיום שלה,
או menu (או m) לאפשרויות. Enter סוגר, ו-q, x ו-close סוגרים
מכל שאלה. בשאלת תוכנית, same מחזיר תוכנית קודמת שלא הושלמה.
אחרי done מוצגות 3 התוכניות האחרונות שהושלמו. אפשרות 1 בתפריט
מציגה את כולן, אפשרות 7 מוחקת אחת, ואפשרות 8 מסתירה את המחשבה
ואת הטיפ. בתפריט, Enter חוזר אחורה.
אפשר גם להריץ את hello.cmd עם אחת מהאפשרויות האלה:
  --plain         מציג רק את הברכה, באנגלית
  --stats         מציג מה שמור במחשב הזה
  --reset         מוחק את כל מה שנשמר (שואל קודם)
  --remind on     נפתח פעם ביום בכניסה למערכת (off להפסקה)
  --streak off    מסתיר את הודעת הימים ברצף (on להצגה)
  --version       מציג את הגרסה
  --check-content FILE
                  בודק קובץ תוכן של הארגון
  --help          מציג את הטקסט הזה

קודי יציאה: 0 כשהפעולה הצליחה, 1 כשפקודה נכשלה או שלא ניתן היה
לכתוב למסך, 2 לאפשרות לא מוכרת.

המידע השמור נשאר במחשב הזה, בתיקיית המשתמש. שום דבר לא נשלח
לשום מקום. אנשי IT שיכולים לקרוא את הקבצים במחשב הזה יכולים
לקרוא גם אותו.""",
        MENU_HELP:
            """מילים שאפשר להקליד בשאלה האחרונה:
  done  מסמן שהתוכנית של היום הושלמה, ואז שואל על הבאה
  plan  קובע או משנה את התוכנית של היום
  menu  פותח את האפשרויות האלה
  q     סוגר את החלון, וכך גם Enter
בשאלת תוכנית, same מחזיר את התוכנית הקודמת שלא הושלמה.
בשאלה "זה בוצע?", n פירושו עוד לא, ואפשר להשאיר את התוכנית
להיום. q סוגר מכל שאלה.
בתפריט הזה, 1 מציג מה שמור, 7 מוחק תוכנית אחת שהושלמה,
ו-8 מסתיר את המחשבה והטיפ.
להקליד m כדי לראות שוב את האפשרויות. שום דבר לא נשלח לשום מקום.""",
        SAVED_PLAN:
            'נשמר. בסיום אפשר להקליד done, או לענות על השאלה בפעם הבאה.',
        GREETING:
            'שלום, עולם!',
        'hello.cmd is in this folder:':
            'הקובץ hello.cmd נמצא בתיקייה הזו:',
        'Shortened to {n} characters.':
            'קוצר ל-{n} תווים.',
        'Your saved file was damaged, so hello-world set it aside as a backup copy and started fresh. Your earlier days and plan could not be read. Menu option 4 deletes the backup.':
            'הקובץ השמור נפגם, ולכן hello-world העביר אותו הצידה כעותק גיבוי והתחיל מחדש. לא ניתן היה לקרוא את הימים ואת התוכנית הקודמים. אפשרות 4 בתפריט מוחקת את הגיבוי.',
        'Backup copy: ':
            'עותק גיבוי: ',
        'In the folder: ':
            'בתיקייה: ',
        'Sorry, "{shown}" is not one of the choices.':
            'סליחה, "{shown}" לא נמצא בין האפשרויות.',
        'A plan needs a word or two, so nothing was saved.':
            'תוכנית צריכה מילה או שתיים, ולכן שום דבר לא נשמר.',
        'The sign-in reminder works on Windows only.':
            'התזכורת בכניסה למערכת עובדת רק ב-Windows.',
        'Your organization has turned off opening at sign-in.':
            'הארגון כיבה את הפתיחה בכניסה למערכת.',
        'The reminder cannot be set up from this folder.':
            'אי אפשר להגדיר את התזכורת מהתיקייה הזו.',
        'Could not set up the reminder.':
            'לא ניתן היה להגדיר את התזכורת.',
        'Done. hello-world will open once a day when you sign in.':
            'בוצע. hello-world ייפתח פעם ביום בכניסה למערכת.',
        'To stop it, choose option 2 in the menu.':
            'כדי להפסיק, לבחור באפשרות 2 בתפריט.',
        'Could not turn off the sign-in reminder.':
            'לא ניתן היה לכבות את התזכורת בכניסה למערכת.',
        'Done. The sign-in reminder is off.':
            'בוצע. התזכורת בכניסה למערכת כבויה.',
        'Saved on this computer in:':
            'נשמר במחשב הזה במיקום:',
        'Saved in your own user folder on this computer.':
            'נשמר בתיקיית המשתמש האישית במחשב הזה.',
        'Days you opened it in the last {days} days: {n} (last 7 days: {recent})':
            'ימי שימוש ב-{days} הימים האחרונים: {n} (ב-7 האחרונים: {recent})',
        'Times you marked a plan done: {n}':
            'פעמים שתוכנית סומנה כבוצעה: {n}',
        'Your current plan: ':
            'התוכנית הנוכחית: ',
        'Earlier plan (for same): ':
            'תוכנית קודמת (עבור same): ',
        'Days-in-a-row message: shown.':
            'הודעת הימים ברצף: מוצגת.',
        'Days-in-a-row message: hidden.':
            'הודעת הימים ברצף: מוסתרת.',
        'Opens by itself at sign-in: turned off by your organization.':
            'פתיחה אוטומטית בכניסה למערכת: כבויה על ידי הארגון.',
        'Opens by itself at sign-in: on.':
            'פתיחה אוטומטית בכניסה למערכת: פועלת.',
        'Opens by itself at sign-in: off.':
            'פתיחה אוטומטית בכניסה למערכת: כבויה.',
        "It never leaves this computer. Others who can read this computer's files, such as IT staff, could read it.":
            'המידע לא יוצא מהמחשב הזה. מי שיכול לקרוא את הקבצים במחשב, כמו אנשי IT, יכול לקרוא גם אותו.',
        'After tidying, the file holds only this:':
            'אחרי הסידור, הקובץ מכיל רק את זה:',
        'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
            'למחוק את כל הרשומות, התאריכים והתוכניות השמורים במחשב הזה? (y או n, Enter לביטול) > ',
        'Nothing was deleted.':
            'שום דבר לא נמחק.',
        'Could not delete everything.':
            'לא ניתן היה למחוק הכול.',
        'Delete these yourself:':
            'את אלה צריך למחוק ידנית:',
        'Could not list the folder, so backup copies may remain:':
            'לא ניתן היה להציג את תוכן התיקייה, ולכן ייתכן שנשארו עותקי גיבוי:',
        'Done. Everything saved was deleted.':
            'בוצע. כל מה שנשמר נמחק.',
        'Another open hello-world window cannot put it back.':
            'גם חלון hello-world פתוח אחר לא יוכל לשחזר אותו.',
        'Close any other open hello-world window, or it may save its notes again.':
            'כדאי לסגור כל חלון hello-world אחר שפתוח, אחרת הוא עלול לשמור שוב את הרשומות שלו.',
        'Everything saved was deleted in another window, so this was not saved.':
            'כל מה שנשמר נמחק בחלון אחר, ולכן זה לא נשמר.',
        'The other open window had also finished a plan.':
            'גם בחלון הפתוח השני הושלמה תוכנית.',
        'The other open window changed the plan, so its plan is kept.':
            'החלון הפתוח השני שינה את התוכנית, ולכן התוכנית שלו נשארת.',
        'Type plan at the last prompt to set one.':
            'כדי לקבוע תוכנית, להקליד plan בשאלה האחרונה.',
        'That looks like a command, not a plan, so nothing was saved.':
            'זה נראה כמו פקודה ולא כמו תוכנית, ולכן שום דבר לא נשמר.',
        'Type your plan, or press Enter to go back.':
            'להקליד את התוכנית, או ללחוץ Enter כדי לחזור.',
        'Finished lately:':
            'הושלמו לאחרונה:',
        'Your plan today: ':
            'התוכנית להיום: ',
        'Your plan from {date}: ':
            'התוכנית מ-{date}: ',
        'Earlier plan: ':
            'תוכנית קודמת: ',
        'Type the next plan, or Enter to close > ':
            'להקליד את התוכנית הבאה, או Enter לסגירה > ',
        'Type the next plan, same to reuse the earlier plan, or Enter to close > ':
            'להקליד את התוכנית הבאה, same לתוכנית הקודמת, או Enter לסגירה > ',
        "Type today's plan, or Enter to keep it > ":
            'להקליד את התוכנית להיום, או Enter כדי להשאיר אותה > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
            'להקליד את התוכנית להיום, same לתוכנית הקודמת, או Enter כדי להשאיר אותה > ',
        "Type today's plan, or Enter to go back > ":
            'להקליד את התוכנית להיום, או Enter לחזרה > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
            'להקליד את התוכנית להיום, same לתוכנית הקודמת, או Enter לחזרה > ',
        'Closing.':
            'נסגר.',
        'There is no earlier plan to reuse yet. Nothing changed.':
            'עדיין אין תוכנית קודמת לשימוש חוזר. שום דבר לא השתנה.',
        'Nothing changed.':
            'שום דבר לא השתנה.',
        'Could not save that on this computer. Your plan is unchanged.':
            'לא ניתן היה לשמור את זה במחשב הזה. התוכנית לא השתנתה.',
        'No finished plans are saved.':
            'אין עדיין תוכניות שהושלמו.',
        'Type the number to forget (1 to {n}), or Enter to keep them all > ':
            'להקליד את המספר למחיקה (1 עד {n}), או Enter כדי להשאיר את כולן > ',
        'There is no number "{typed}" on the list. Type a number from 1 to {n}, or press Enter to keep them all.':
            'אין מספר "{typed}" ברשימה. להקליד מספר מ-1 עד {n}, או ללחוץ Enter כדי להשאיר את כולן.',
        'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
            'למחוק אותה גם כתוכנית הקודמת עבור same? (y או n, Enter כדי להשאיר אותה עבור same) > ',
        'Type y or n, or press Enter to keep it for same.':
            'להקליד y או n, או ללחוץ Enter כדי להשאיר אותה עבור same.',
        'That plan was already forgotten. Nothing changed.':
            'התוכנית הזו כבר נמחקה. שום דבר לא השתנה.',
        'Forgotten: ':
            'נמחקה: ',
        'Same still has it.':
            'היא עדיין זמינה דרך same.',
        'Could not save that on this computer. Nothing changed.':
            'לא ניתן היה לשמור את זה במחשב הזה. שום דבר לא השתנה.',
        'Options':
            'אפשרויות',
        'Show what is saved on this computer':
            'הצגת מה ששמור במחשב הזה',
        'Open once a day at sign-in (turned off by your organization)':
            'פתיחה פעם ביום בכניסה למערכת (כבויה על ידי הארגון)',
        'Turn off: open once a day at sign-in (now on)':
            'כיבוי: פתיחה פעם ביום בכניסה למערכת (כרגע פועלת)',
        'Turn on: open once a day at sign-in (now off)':
            'הפעלה: פתיחה פעם ביום בכניסה למערכת (כרגע כבויה)',
        'Days-in-a-row message (hidden by your organization)':
            'הודעת הימים ברצף (מוסתרת על ידי הארגון)',
        'Hide the days-in-a-row message (now shown)':
            'הסתרת הודעת הימים ברצף (כרגע מוצגת)',
        'Show the days-in-a-row message (now hidden)':
            'הצגת הודעת הימים ברצף (כרגע מוסתרת)',
        'Delete everything saved':
            'מחיקת כל מה שנשמר',
        'Help':
            'עזרה',
        "Set today's plan (turned off by your organization)":
            'קביעת התוכנית להיום (כבויה על ידי הארגון)',
        'Forget a finished plan (turned off by your organization)':
            'מחיקת תוכנית שהושלמה (כבויה על ידי הארגון)',
        "Set or change today's plan":
            'קביעה או שינוי של התוכנית להיום',
        'Forget one finished plan':
            'מחיקת תוכנית אחת שהושלמה',
        'Thought and tip (hidden by your organization)':
            'מחשבה וטיפ (מוסתרים על ידי הארגון)',
        'Hide the thought and tip (now shown)':
            'הסתרת המחשבה והטיפ (כרגע מוצגים)',
        'Show the thought and tip (now hidden)':
            'הצגת המחשבה והטיפ (כרגע מוסתרים)',
        '{date}: ':
            '{date}: ',
        'Enter':
            'Enter',
        'Back to the last prompt':
            'חזרה לשאלה האחרונה',
        'Choose 1 to 11, or Enter to go back > ':
            'לבחור 1 עד 11, או Enter לחזרה > ',
        'Choose 1 to 11, m to list the options, or Enter to go back > ':
            'לבחור 1 עד 11, m להצגת האפשרויות, או Enter לחזרה > ',
        'The saved file could not be read just now, so this may be out of date.':
            'לא ניתן היה לקרוא את הקובץ השמור כרגע, ולכן ייתכן שהמידע לא עדכני.',
        'Type full to see the whole file, or Enter to go on > ':
            'להקליד full כדי לראות את כל הקובץ, או Enter כדי להמשיך > ',
        'Could not save that choice on this computer.':
            'לא ניתן היה לשמור את הבחירה הזו במחשב הזה.',
        'Your organization has hidden the days-in-a-row message.':
            'הארגון הסתיר את הודעת הימים ברצף.',
        'Done. The days-in-a-row message is on.':
            'בוצע. הודעת הימים ברצף מוצגת.',
        'Done. The days-in-a-row message is off.':
            'בוצע. הודעת הימים ברצף מוסתרת.',
        'Plans are turned off by your organization.':
            'התוכניות כבויות על ידי הארגון.',
        'Your organization has hidden the thought and tip.':
            'הארגון הסתיר את המחשבה והטיפ.',
        'Done. The thought and tip are on.':
            'בוצע. המחשבה והטיפ מוצגים.',
        'Done. The thought and tip are off.':
            'בוצע. המחשבה והטיפ מוסתרים.',
        'Type 1 to 11, or press Enter to go back.':
            'להקליד 1 עד 11, או ללחוץ Enter כדי לחזור.',
        'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
            'לפתוח את התוכנה פעם ביום בכניסה למערכת? (y או n, Enter לדחייה) > ',
        'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
            'לפתוח את התוכנה פעם ביום בכניסה למערכת, כדי שתשאל על התוכנית? (y או n, Enter לדחייה) > ',
        'Type y or n, or press Enter for not now.':
            'להקליד y או n, או ללחוץ Enter לדחייה.',
        'That was not understood. It will ask again on a later visit.':
            'התשובה לא הובנה. השאלה תחזור בפעם אחרת.',
        'It will ask again on a later visit. Menu option 2 also turns it on.':
            'השאלה תחזור בפעם אחרת. אפשר גם להפעיל את זה באפשרות 2 בתפריט.',
        'No problem. Menu option 2 turns it on later.':
            'אין בעיה. אפשר להפעיל את זה בהמשך באפשרות 2 בתפריט.',
        "Okay. It won't ask again. Menu option 2 turns it on.":
            'בסדר. השאלה לא תחזור. אפשרות 2 בתפריט מפעילה את זה.',
        'Okay. It will ask again on a later visit. Type n to stop it.':
            'בסדר. השאלה תחזור בפעם אחרת. כדי שלא תחזור, להקליד n.',
        'When did you finish it?':
            'מתי זה הושלם?',
        'Today':
            'היום',
        'Type a number from 1 to {n}, or Enter for 1 > ':
            'להקליד מספר מ-1 עד {n}, או Enter ל-1 > ',
        'Type a number from 1 to {n}, or press Enter.':
            'להקליד מספר מ-1 עד {n}, או ללחוץ Enter.',
        'That looks like more than one thing. Finishing the first part still counts.':
            'זה נראה כמו יותר מדבר אחד. גם השלמת החלק הראשון נחשבת.',
        'There is no plan to mark as done. Type plan to set one.':
            'אין תוכנית לסמן כבוצעה. להקליד plan כדי לקבוע אחת.',
        'Could not save that on this computer. The plan is still open.':
            'לא ניתן היה לשמור את זה במחשב הזה. התוכנית עדיין פתוחה.',
        'Your plan from over two weeks ago was put away. Type same at the plan prompt to bring it back.':
            'התוכנית מלפני יותר משבועיים הועברה הצידה. כדי להחזיר אותה, להקליד same בשאלת התוכנית.',
        "Press Enter at each question to skip it, and once more to close. That's it.":
            'בכל שאלה, Enter מדלג עליה, ועוד Enter אחד סוגר. זה הכול.',
        'Welcome.':
            'ברוכים הבאים.',
        'Each day you get one thought and one small thing to try, the same for everyone.':
            'בכל יום יש מחשבה אחת ודבר קטן אחד לנסות, אותם לכולם.',
        'If you type a plan, it asks next time how it went. Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks.':
            'אם מקלידים תוכנית, בפעם הבאה תופיע שאלה איך זה הלך. הרשומות נשארות במחשב הזה ולא נשלחות לשום מקום. כמו כל קובץ עבודה, הן לא סודיות, אז עדיף לכתוב בהן רק משימות יומיומיות.',
        'Type menu at the end for the options.':
            'להקליד menu בסוף כדי לראות את האפשרויות.',
        'Welcome back. Glad you are here.':
            'ברוכים השבים. טוב לראות אותך.',
        'You have opened this {row} days in a row. Nice to see you.':
            'זה היום ה-{row} ברצף. טוב לראות אותך.',
        'Last time you planned: ':
            'בפעם הקודמת התוכנית הייתה: ',
        'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
            'זה בוצע? (y כן, n עוד לא, Enter לדילוג) > ',
        'Type y or n, or press Enter to skip.':
            'להקליד y או n, או ללחוץ Enter לדילוג.',
        'Could not save that on this computer. Your answer was not counted.':
            'לא ניתן היה לשמור את זה במחשב הזה. התשובה לא נספרה.',
        'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
            'זה בסדר. להשאיר אותה להיום? (y או n, Enter כדי להשאיר) > ',
        'Type y to keep it, n to clear it, or press Enter to keep it.':
            'להקליד y כדי להשאיר, n כדי לנקות, או ללחוץ Enter כדי להשאיר.',
        'Cleared. Type same at a plan prompt if you want it back.':
            'נוקתה. כדי להחזיר אותה, להקליד same בשאלת תוכנית.',
        'Kept for today.':
            'נשארת להיום.',
        'That was not understood. Your plan is left as it was.':
            'התשובה לא הובנה. התוכנית נשארה כמו שהייתה.',
        'Your plan is still open.':
            'התוכנית עדיין פתוחה.',
        'Thought for today:':
            'מחשבה להיום:',
        'Try this today:':
            'לנסות היום:',
        'Your plan for today: ':
            'התוכנית להיום: ',
        'Still open since {date}:':
            'פתוחה מאז {date}:',
        '(Enter to skip)':
            '(Enter לדילוג)',
        '(A plan typed here replaces the old one. Enter to skip)':
            '(תוכנית שתוקלד כאן תחליף את הקודמת. Enter לדילוג)',
        '(Type same to reuse it, or Enter to skip)':
            '(להקליד same כדי להשתמש בה שוב, או Enter לדילוג)',
        'What is one thing you want to get done today?':
            'מה הדבר האחד שחשוב להספיק היום?',
        'There is no earlier plan to reuse yet. Nothing was saved.':
            'עדיין אין תוכנית קודמת לשימוש חוזר. שום דבר לא נשמר.',
        'Your notes could not be saved on this computer. This screen still works.':
            'לא ניתן היה לשמור את הרשומות במחשב הזה. המסך הזה עדיין עובד.',
        'Type menu, or Enter to close > ':
            'להקליד menu, או Enter לסגירה > ',
        'Type done, plan or menu, or Enter to close > ':
            'להקליד done, plan או menu, או Enter לסגירה > ',
        'Type plan or menu, or Enter to close > ':
            'להקליד plan או menu, או Enter לסגירה > ',
        'Type done, plan or menu, or press Enter to close.':
            'להקליד done, plan או menu, או ללחוץ Enter לסגירה.',
        'Type plan or menu, or press Enter to close.':
            'להקליד plan או menu, או ללחוץ Enter לסגירה.',
        "The saved file can't be read right now, or it is damaged.":
            'לא ניתן לקרוא את הקובץ השמור כרגע, או שהוא פגום.',
        'Nothing was changed. Saved in: ':
            'שום דבר לא השתנה. מיקום השמירה: ',
        'Deleting saved notes needs a person at the keyboard.':
            'מחיקת הרשומות השמורות דורשת מישהו ליד המקלדת.',
        '{option} needs on or off. Here are the options.':
            '{option} דורש on או off. הנה האפשרויות.',
        'Unknown option: {option}. Here are the options.':
            'אפשרות לא מוכרת: {option}. הנה האפשרויות.',
        '&Done':
            'בוצע(&D)',
        '&Not yet':
            'עוד לא(&N)',
        'S&kip':
            'דילוג(&K)',
        '&Save':
            'שמירה(&S)',
        '&I did it':
            'עשיתי(&I)',
        '&Options':
            'אפשרויות(&O)',
        'Close':
            'סגירה',
        'Not today':
            'לא היום',
        'Did you do it?':
            'זה בוצע?',
        'Done. A reminder comes when you sign in, if there is a plan to ask about.':
            'בוצע. תזכורת תופיע בכניסה למערכת, אם יש תוכנית לשאול עליה.',
        'Done. The Start menu opens a window with buttons.':
            'בוצע. תפריט התחל יפתח חלון עם לחצנים.',
        'Done. The Start menu opens this text screen.':
            'בוצע. תפריט התחל יפתח את מסך הטקסט הזה.',
        'More options':
            'אפשרויות נוספות',
        'Remind me when I sign in':
            'להזכיר לי בכניסה למערכת',
        'Show the thought and tip':
            'הצגת המחשבה והטיפ',
        'Type your plan in the box.':
            'להקליד את התוכנית בתיבה.',
        'Use a window with buttons (now this text screen)':
            'שימוש בחלון עם לחצנים (כרגע מסך טקסט)',
        'Use the text screen':
            'שימוש במסך הטקסט',
        'Use this text screen (now a window with buttons)':
            'שימוש במסך הטקסט הזה (כרגע חלון עם לחצנים)',
        'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
            "רוצים תזכורת בכניסה למערכת? היא מציגה את התוכנית מהפעם הקודמת, ועונים בלחיצה אחת. אפשר לכבות אותה דרך 'אפשרויות'.",
        'Window or text screen (set by your organization)':
            'חלון או מסך טקסט (נקבע על ידי הארגון)',
        'Your organization has set hello-world to open as a text screen.':
            'הארגון הגדיר ש-hello-world ייפתח כמסך טקסט.',
        'Saved.':
            'נשמר.',
        'Save your plan before closing?':
            'לשמור את התוכנית לפני הסגירה?',
        'Delete all saved notes, dates and plans on this computer?':
            'למחוק את כל הרשומות, התאריכים והתוכניות השמורים במחשב הזה?',
        'Turn off: reminder when you sign in (now on)':
            'כיבוי: תזכורת בכניסה למערכת (כרגע פועלת)',
        'Turn on: reminder when you sign in (now off)':
            'הפעלה: תזכורת בכניסה למערכת (כרגע כבויה)',
        'Reminder when you sign in (turned off by your organization)':
            'תזכורת בכניסה למערכת (כבויה על ידי הארגון)',
        'Reminder when you sign in: on.':
            'תזכורת בכניסה למערכת: פועלת.',
        'Reminder when you sign in: off.':
            'תזכורת בכניסה למערכת: כבויה.',
        'Reminder when you sign in: turned off by your organization.':
            'תזכורת בכניסה למערכת: כבויה על ידי הארגון.',
        'Show the days-in-a-row message':
            'הצגת הודעת הימים ברצף',
        'Done. The thought and tip show next time you open hello-world.':
            'בוצע. המחשבה והטיפ יוצגו בפעם הבאה ש-hello-world ייפתח.',
        "Clear today's plan?":
            'לנקות את התוכנית להיום?',
        'Next plan, if you want one:':
            'התוכנית הבאה, אם רוצים:',
        'A few things? Put ; between them.':
            'כמה דברים? להפריד ביניהם בתו ;',
        'A plan can be up to {n} characters.':
            'תוכנית יכולה להכיל עד {n} תווים.',
        'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
            'הם בוצעו? (y לכולם, n לעוד לא, מספרים לאלה שבוצעו, Enter לדילוג) > ',
        'Last time you planned:':
            'בפעם הקודמת התוכנית הייתה:',
        'The rest is kept for today.':
            'כל השאר נשאר להיום.',
        'Tick the ones you did, then click Done. With none ticked, Done means all of them.':
            "לסמן את מה שבוצע וללחוץ על 'בוצע'. בלי סימון, 'בוצע' פירושו הכול.",
        'Type y for all, n for not yet, or the numbers you did, such as 1 3. Enter skips.':
            'להקליד y לכולם, n לעוד לא, או את המספרים שבוצעו, למשל 1 3. Enter מדלג.',
        'Your settings were kept.':
            'ההגדרות נשארו כמו שהיו.',
        'Language (set by your organization)':
            'שפה (נקבעה על ידי הארגון)',
        'Language (now {name})':
            'שפה (כרגע {name})',
        'following Windows':
            'לפי Windows',
        'Your organization shows hello-world in English.':
            'הארגון קבע ש-hello-world יוצג באנגלית.',
        'Follow Windows':
            'לפי Windows',
        'Type a number from 1 to {n}, or Enter to keep it > ':
            'להקליד מספר מ-1 עד {n}, או Enter כדי להשאיר > ',
        'Done. The new language shows next time you open hello-world.':
            'בוצע. השפה החדשה תוצג בפעם הבאה ש-hello-world ייפתח.',
        'Language...':
            'שפה...',
        'Hello, {name}!':
            'שלום, {name}!',
        'One thing to get done today? Open hello-world to plan it.':
            'דבר אחד להספיק היום? אפשר לפתוח את hello-world ולתכנן אותו.',
        '&Open':
            'פתיחה(&O)',
        'Reminder settings...':
            'הגדרות תזכורת...',
        'Greet me by name':
            'לפנות אליי בשמי',
        'At sign-in':
            'בכניסה למערכת',
        'At {at}':
            'בשעה {at}',
        'Also on days with no plan':
            'גם בימים בלי תוכנית',
        'Open hello-world after I answer':
            'לפתוח את hello-world אחרי התשובה',
        'Not on weekends':
            'לא בסופי שבוע',
        'Done. A reminder comes at {at} each day, if there is a plan to ask about.':
            'בוצע. תזכורת תופיע כל יום בשעה {at}, אם יש תוכנית לשאול עליה.',
        'Send feedback...':
            'שליחת משוב...',
        '"holidays" must be a list of at most {n} dates.':
            '"holidays" חייב להיות רשימה של עד {n} תאריכים.',
        '"title" must be 1 to 40 characters of plain text, with no link or address.':
            '"title" חייב להיות טקסט פשוט באורך 1 עד 40 תווים, בלי קישור או כתובת.',
        '"{list}" must be a list of {low} to {high} lines.':
            '"{list}" חייב להיות רשימה של {low} עד {high} שורות.',
        "Can't read {path}: {error}":
            'לא ניתן לקרוא את {path}: {error}',
        'Could not save that on this computer.':
            'לא ניתן היה לשמור את זה במחשב הזה.',
        'Days you opened hello-world: {n}':
            'ימים שבהם hello-world נפתח: {n}',
        'Keep a longer history':
            'שמירת היסטוריה ארוכה יותר',
        'Keep my numbers':
            'שמירת המספרים שלי',
        'Longest run of days: {n}':
            'הרצף הארוך ביותר (בימים): {n}',
        "Mark today's plan done":
            'סימון התוכנית להיום כבוצעה',
        "Mark today's plan done (plans are turned off)":
            'סימון התוכנית להיום כבוצעה (התוכניות כבויות)',
        'My numbers are off. Turn them on under Options, or with --set numbers on.':
            "'המספרים שלי' כבוי. אפשר להפעיל אותו דרך 'אפשרויות', או עם --set numbers on.",
        'My numbers...':
            'המספרים שלי...',
        'Nothing finished yet this week. That is fine.':
            'עוד לא הושלם כלום השבוע. זה בסדר.',
        'OK: {thoughts} thoughts and {tips} tips.':
            'OK: {thoughts} מחשבות ו-{tips} טיפים.',
        'Plans finished: {n}':
            'תוכניות שהושלמו: {n}',
        'Save my plans to a file':
            'שמירת התוכניות שלי בקובץ',
        'Saved to {path}':
            'נשמר ב-{path}',
        "The file isn't valid JSON, or is over 200,000 characters.":
            'הקובץ אינו JSON תקין, או שהוא ארוך מ-200,000 תווים.',
        'The file must hold an object with two lists, "thoughts" and "tips", and may add "holidays" and "title".':
            'הקובץ חייב להכיל אובייקט עם שתי רשימות, "thoughts" ו-"tips", ואפשר להוסיף "holidays" ו-"title".',
        'This week you finished {n}:':
            'השבוע הושלמו {n}:',
        'This week...':
            'השבוע...',
        'holidays line {line} is not a date like 2026-12-25.':
            'שורה {line} ב-holidays אינה תאריך בפורמט 2026-12-25.',
        '{list} line {line} has a date.':
            'בשורה {line} של {list} יש תאריך.',
        '{list} line {line} has a link or an address.':
            'בשורה {line} של {list} יש קישור או כתובת.',
        '{list} line {line} has control characters or extra spaces.':
            'בשורה {line} של {list} יש תווי בקרה או רווחים מיותרים.',
        '{list} line {line} is not text.':
            'שורה {line} של {list} אינה טקסט.',
        '{list} line {line} must be {low} to {high} characters long.':
            'שורה {line} של {list} חייבת להיות באורך {low} עד {high} תווים.',
    },
}

# ---- European Portuguese ----

_PT_PT_TEXT = {
    HELP:
        """hello-world mostra uma saudação, um pensamento e uma pequena coisa
para experimentar.

Na última pergunta, escreva plan para o plano de hoje, feito quando
o terminar, ou menu (ou m) para ver as opções. Enter fecha; q, x e
sair fecham a partir de qualquer pergunta. Na pergunta do plano,
repetir recupera um plano anterior por terminar. Depois de feito,
mostra os 3 últimos planos concluídos. A opção 1 do menu mostra-os
todos, a 7 esquece um e a 8 oculta o pensamento e a sugestão.
No menu, Enter volta atrás.
Também pode executar o hello.cmd com uma destas opções:
  --plain         Mostra só a saudação, em inglês
  --stats         Mostra o que está guardado neste computador
  --reset         Elimina tudo o que está guardado (pergunta antes)
  --remind on     Abre uma vez por dia ao iniciar sessão (off: desliga)
  --streak off    Oculta a mensagem de dias seguidos (on: mostra)
  --version       Mostra a versão
  --check-content FICHEIRO
                  Verifica um ficheiro de conteúdo da organização
  --help          Mostra este texto

Códigos de saída: 0 se correu bem, 1 se um comando falhou ou não foi
possível escrever no ecrã, 2 para uma opção desconhecida.

As notas guardadas ficam neste computador, na sua pasta de
utilizador. Nada é enviado para lado nenhum. Quem trabalha na
informática e tem acesso aos ficheiros deste computador pode lê-las.""",
    MENU_HELP:
        """Palavras que pode escrever na última pergunta:
  feito  marca o plano de hoje como concluído e pede o seguinte
  plan   define ou altera o plano de hoje
  menu   abre estas opções
  q      fecha a janela, tal como Enter
Na pergunta do plano, repetir recupera o plano anterior por terminar.
Quando aparece "Conseguiu fazer?", n quer dizer ainda não, e pode
manter o plano para hoje. q fecha a partir de qualquer pergunta.
Neste menu, 1 mostra o que está guardado, 7 esquece um plano
concluído e 8 oculta o pensamento e a sugestão.
Escreva m para ver de novo as opções. Nada é enviado para lado nenhum.""",
    SAVED_PLAN:
        'Guardado. Escreva feito quando o terminar; caso contrário, a pergunta aparece da próxima vez que abrir o hello-world.',
    GREETING:
        'Olá, mundo!',
    'hello.cmd is in this folder:':
        'O hello.cmd está nesta pasta:',
    'Shortened to {n} characters.':
        'Encurtado para {n} caracteres.',
    'Your saved file was damaged, so hello-world set it aside as a backup copy and started fresh. Your earlier days and plan could not be read. Menu option 4 deletes the backup.':
        'O ficheiro guardado estava danificado, por isso o hello-world pô-lo de parte como cópia de segurança e recomeçou do zero. Não foi possível ler os dias nem o plano anteriores. A opção 4 do menu elimina a cópia de segurança.',
    'Backup copy: ':
        'Cópia de segurança: ',
    'In the folder: ':
        'Na pasta: ',
    'Sorry, "{shown}" is not one of the choices.':
        'Desculpe, "{shown}" não é uma das opções.',
    'A plan needs a word or two, so nothing was saved.':
        'Um plano precisa de uma ou duas palavras, por isso não foi guardado nada.',
    'The sign-in reminder works on Windows only.':
        'O lembrete ao iniciar sessão só funciona no Windows.',
    'Your organization has turned off opening at sign-in.':
        'A sua organização desativou a abertura ao iniciar sessão.',
    'The reminder cannot be set up from this folder.':
        'Não é possível configurar o lembrete a partir desta pasta.',
    'Could not set up the reminder.':
        'Não foi possível configurar o lembrete.',
    'Done. hello-world will open once a day when you sign in.':
        'Pronto. O hello-world vai abrir uma vez por dia ao iniciar sessão.',
    'To stop it, choose option 2 in the menu.':
        'Para o desativar, escolha a opção 2 do menu.',
    'Could not turn off the sign-in reminder.':
        'Não foi possível desativar o lembrete ao iniciar sessão.',
    'Done. The sign-in reminder is off.':
        'Pronto. O lembrete ao iniciar sessão está desativado.',
    'Saved on this computer in:':
        'Guardado neste computador em:',
    'Saved in your own user folder on this computer.':
        'Guardado na sua pasta de utilizador neste computador.',
    'Days you opened it in the last {days} days: {n} (last 7 days: {recent})':
        'Dias em que o abriu nos últimos {days} dias: {n} (últimos 7 dias: {recent})',
    'Times you marked a plan done: {n}':
        'Vezes que marcou um plano como feito: {n}',
    'Your current plan: ':
        'Plano atual: ',
    'Earlier plan (for same): ':
        'Plano anterior (para repetir): ',
    'Days-in-a-row message: shown.':
        'Mensagem de dias seguidos: visível.',
    'Days-in-a-row message: hidden.':
        'Mensagem de dias seguidos: oculta.',
    'Opens by itself at sign-in: turned off by your organization.':
        'Abertura automática ao iniciar sessão: desativada pela sua organização.',
    'Opens by itself at sign-in: on.':
        'Abertura automática ao iniciar sessão: ativada.',
    'Opens by itself at sign-in: off.':
        'Abertura automática ao iniciar sessão: desativada.',
    "It never leaves this computer. Others who can read this computer's files, such as IT staff, could read it.":
        'Nunca sai deste computador. Quem puder ler os ficheiros deste computador, como a equipa de informática, poderá lê-lo.',
    'After tidying, the file holds only this:':
        'Depois de arrumado, o ficheiro contém apenas isto:',
    'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
        'Eliminar todas as notas, datas e planos guardados neste computador? (s ou n, Enter para cancelar) > ',
    'Nothing was deleted.':
        'Não foi eliminado nada.',
    'Could not delete everything.':
        'Não foi possível eliminar tudo.',
    'Delete these yourself:':
        'Elimine estes ficheiros manualmente:',
    'Could not list the folder, so backup copies may remain:':
        'Não foi possível listar a pasta; podem ter ficado cópias de segurança:',
    'Done. Everything saved was deleted.':
        'Pronto. Tudo o que estava guardado foi eliminado.',
    'Another open hello-world window cannot put it back.':
        'Outra janela aberta do hello-world não o consegue repor.',
    'Close any other open hello-world window, or it may save its notes again.':
        'Feche qualquer outra janela aberta do hello-world; caso contrário, pode voltar a guardar as notas dela.',
    'Everything saved was deleted in another window, so this was not saved.':
        'Tudo o que estava guardado foi eliminado noutra janela, por isso isto não foi guardado.',
    'The other open window had also finished a plan.':
        'A outra janela aberta também tinha concluído um plano.',
    'The other open window changed the plan, so its plan is kept.':
        'A outra janela aberta alterou o plano, por isso fica o plano dela.',
    'Type plan at the last prompt to set one.':
        'Escreva plan na última pergunta para definir um.',
    'That looks like a command, not a plan, so nothing was saved.':
        'Isso parece um comando, não um plano, por isso não foi guardado nada.',
    'Type your plan, or press Enter to go back.':
        'Escreva o plano ou prima Enter para voltar.',
    'Finished lately:':
        'Concluídos recentemente:',
    'Your plan today: ':
        'Plano de hoje: ',
    'Your plan from {date}: ':
        'Plano de {date}: ',
    'Earlier plan: ':
        'Plano anterior: ',
    'Type the next plan, or Enter to close > ':
        'Escreva o plano seguinte, ou Enter para fechar > ',
    'Type the next plan, same to reuse the earlier plan, or Enter to close > ':
        'Escreva o plano seguinte, repetir para reutilizar o plano anterior, ou Enter para fechar > ',
    "Type today's plan, or Enter to keep it > ":
        'Escreva o plano de hoje, ou Enter para o manter > ',
    "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
        'Escreva o plano de hoje, repetir para reutilizar o plano anterior, ou Enter para o manter > ',
    "Type today's plan, or Enter to go back > ":
        'Escreva o plano de hoje, ou Enter para voltar > ',
    "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
        'Escreva o plano de hoje, repetir para reutilizar o plano anterior, ou Enter para voltar > ',
    'Closing.':
        'A fechar.',
    'There is no earlier plan to reuse yet. Nothing changed.':
        'Ainda não há um plano anterior para reutilizar. Nada foi alterado.',
    'Nothing changed.':
        'Nada foi alterado.',
    'Could not save that on this computer. Your plan is unchanged.':
        'Não foi possível guardar neste computador. O plano não foi alterado.',
    'No finished plans are saved.':
        'Não há planos concluídos guardados.',
    'Type the number to forget (1 to {n}), or Enter to keep them all > ':
        'Escreva o número a esquecer (1 a {n}), ou Enter para manter todos > ',
    'There is no number "{typed}" on the list. Type a number from 1 to {n}, or press Enter to keep them all.':
        'Não há nenhum número "{typed}" na lista. Escreva um número de 1 a {n}, ou prima Enter para manter todos.',
    'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
        'Esquecê-lo também como plano anterior para repetir? (s ou n, Enter para o manter para repetir) > ',
    'Type y or n, or press Enter to keep it for same.':
        'Escreva s ou n, ou prima Enter para o manter para repetir.',
    'That plan was already forgotten. Nothing changed.':
        'Esse plano já tinha sido esquecido. Nada foi alterado.',
    'Forgotten: ':
        'Esquecido: ',
    'Same still has it.':
        'Continua disponível com repetir.',
    'Could not save that on this computer. Nothing changed.':
        'Não foi possível guardar neste computador. Nada foi alterado.',
    'Options':
        'Opções',
    'Show what is saved on this computer':
        'Mostrar o que está guardado neste computador',
    'Open once a day at sign-in (turned off by your organization)':
        'Abrir ao iniciar sessão (desativado pela organização)',
    'Turn off: open once a day at sign-in (now on)':
        'Desativar: abrir uma vez por dia ao iniciar sessão (agora ativado)',
    'Turn on: open once a day at sign-in (now off)':
        'Ativar: abrir uma vez por dia ao iniciar sessão (agora desativado)',
    'Days-in-a-row message (hidden by your organization)':
        'Mensagem de dias seguidos (oculta pela sua organização)',
    'Hide the days-in-a-row message (now shown)':
        'Ocultar a mensagem de dias seguidos (agora visível)',
    'Show the days-in-a-row message (now hidden)':
        'Mostrar a mensagem de dias seguidos (agora oculta)',
    'Delete everything saved':
        'Eliminar tudo o que está guardado',
    'Help':
        'Ajuda',
    "Set today's plan (turned off by your organization)":
        'Definir o plano de hoje (desativado pela sua organização)',
    'Forget a finished plan (turned off by your organization)':
        'Esquecer um plano concluído (desativado pela sua organização)',
    "Set or change today's plan":
        'Definir ou alterar o plano de hoje',
    'Forget one finished plan':
        'Esquecer um plano concluído',
    'Thought and tip (hidden by your organization)':
        'Pensamento e sugestão (ocultos pela sua organização)',
    'Hide the thought and tip (now shown)':
        'Ocultar o pensamento e a sugestão (agora visíveis)',
    'Show the thought and tip (now hidden)':
        'Mostrar o pensamento e a sugestão (agora ocultos)',
    '{date}: ':
        '{date}: ',
    'Enter':
        'Enter',
    'Back to the last prompt':
        'Voltar à última pergunta',
    'Choose 1 to 11, or Enter to go back > ':
        'Escolha de 1 a 11, ou Enter para voltar > ',
    'Choose 1 to 11, m to list the options, or Enter to go back > ':
        'Escolha de 1 a 11, m para ver as opções, ou Enter para voltar > ',
    'The saved file could not be read just now, so this may be out of date.':
        'Não foi possível ler o ficheiro guardado neste momento, por isso isto pode estar desatualizado.',
    'Type full to see the whole file, or Enter to go on > ':
        'Escreva full para ver o ficheiro completo, ou Enter para continuar > ',
    'Could not save that choice on this computer.':
        'Não foi possível guardar essa escolha neste computador.',
    'Your organization has hidden the days-in-a-row message.':
        'A sua organização ocultou a mensagem de dias seguidos.',
    'Done. The days-in-a-row message is on.':
        'Pronto. A mensagem de dias seguidos está ativada.',
    'Done. The days-in-a-row message is off.':
        'Pronto. A mensagem de dias seguidos está desativada.',
    'Plans are turned off by your organization.':
        'Os planos foram desativados pela sua organização.',
    'Your organization has hidden the thought and tip.':
        'A sua organização ocultou o pensamento e a sugestão.',
    'Done. The thought and tip are on.':
        'Pronto. O pensamento e a sugestão estão ativados.',
    'Done. The thought and tip are off.':
        'Pronto. O pensamento e a sugestão estão desativados.',
    'Type 1 to 11, or press Enter to go back.':
        'Escreva de 1 a 11, ou prima Enter para voltar.',
    'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
        'Quer que o hello-world abra uma vez por dia ao iniciar sessão? (s ou n, Enter para mais tarde) > ',
    'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
        'Quer que o hello-world abra uma vez por dia ao iniciar sessão, para perguntar pelo plano? (s ou n, Enter para mais tarde) > ',
    'Type y or n, or press Enter for not now.':
        'Escreva s ou n, ou prima Enter para mais tarde.',
    'That was not understood. It will ask again on a later visit.':
        'Resposta não percebida. A pergunta volta numa próxima visita.',
    'It will ask again on a later visit. Menu option 2 also turns it on.':
        'A pergunta volta numa próxima visita. A opção 2 do menu também o ativa.',
    'No problem. Menu option 2 turns it on later.':
        'Não há problema. A opção 2 do menu ativa-o mais tarde.',
    "Okay. It won't ask again. Menu option 2 turns it on.":
        'Está bem. Não volta a perguntar. A opção 2 do menu ativa-o.',
    'Okay. It will ask again on a later visit. Type n to stop it.':
        'Está bem. A pergunta volta numa próxima visita. Escreva n para não voltar a perguntar.',
    'When did you finish it?':
        'Quando o concluiu?',
    'Today':
        'Hoje',
    'Type a number from 1 to {n}, or Enter for 1 > ':
        'Escreva um número de 1 a {n}, ou Enter para 1 > ',
    'Type a number from 1 to {n}, or press Enter.':
        'Escreva um número de 1 a {n}, ou prima Enter.',
    'That looks like more than one thing. Finishing the first part still counts.':
        'Isso parece mais do que uma coisa. Concluir a primeira parte já conta.',
    'There is no plan to mark as done. Type plan to set one.':
        'Não há nenhum plano para marcar como feito. Escreva plan para definir um.',
    'Could not save that on this computer. The plan is still open.':
        'Não foi possível guardar neste computador. O plano continua aberto.',
    'Your plan from over two weeks ago was put away. Type same at the plan prompt to bring it back.':
        'O plano de há mais de duas semanas foi posto de parte. Escreva repetir na pergunta do plano para o recuperar.',
    "Press Enter at each question to skip it, and once more to close. That's it.":
        'Prima Enter em cada pergunta para a saltar, e mais uma vez para fechar. É só isto.',
    'Welcome.':
        'Damos-lhe as boas-vindas.',
    'Each day you get one thought and one small thing to try, the same for everyone.':
        'Todos os dias há um pensamento e uma pequena coisa para experimentar, iguais para toda a gente.',
    'If you type a plan, it asks next time how it went. Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks.':
        'Se escrever um plano, da próxima vez é perguntado como correu. As notas ficam neste computador e nunca são enviadas para lado nenhum. Como qualquer ficheiro de trabalho, não são secretas, por isso use-as só para tarefas do dia a dia.',
    'Type menu at the end for the options.':
        'Escreva menu no fim para ver as opções.',
    'Welcome back. Glad you are here.':
        'Olá outra vez. Ainda bem que voltou.',
    'You have opened this {row} days in a row. Nice to see you.':
        'Abriu o hello-world {row} dias seguidos. Que bom.',
    'Last time you planned: ':
        'Último plano: ',
    'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
        'Conseguiu fazer? (s para sim, n para ainda não, Enter para saltar) > ',
    'Type y or n, or press Enter to skip.':
        'Escreva s ou n, ou prima Enter para saltar.',
    'Could not save that on this computer. Your answer was not counted.':
        'Não foi possível guardar neste computador. A resposta não foi contada.',
    'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
        'Não faz mal. Manter para hoje? (s ou n, Enter para manter) > ',
    'Type y to keep it, n to clear it, or press Enter to keep it.':
        'Escreva s para manter, n para limpar, ou prima Enter para manter.',
    'Cleared. Type same at a plan prompt if you want it back.':
        'Plano removido. Escreva repetir numa pergunta de plano para o recuperar.',
    'Kept for today.':
        'Mantido para hoje.',
    'That was not understood. Your plan is left as it was.':
        'Não foi possível perceber a resposta. O plano ficou como estava.',
    'Your plan is still open.':
        'O plano continua por concluir.',
    'Thought for today:':
        'Pensamento do dia:',
    'Try this today:':
        'Para experimentar hoje:',
    'Your plan for today: ':
        'Plano para hoje: ',
    'Still open since {date}:':
        'Por concluir desde {date}:',
    '(Enter to skip)':
        '(Enter para saltar)',
    '(A plan typed here replaces the old one. Enter to skip)':
        '(Um plano escrito aqui substitui o anterior. Enter para saltar)',
    '(Type same to reuse it, or Enter to skip)':
        '(Escreva repetir para o reutilizar, ou Enter para saltar)',
    'What is one thing you want to get done today?':
        'Qual é a coisa que quer deixar feita hoje?',
    'There is no earlier plan to reuse yet. Nothing was saved.':
        'Ainda não há um plano anterior para reutilizar. Nada foi guardado.',
    'Your notes could not be saved on this computer. This screen still works.':
        'Não foi possível guardar as notas neste computador. Este ecrã continua a funcionar.',
    'Type menu, or Enter to close > ':
        'Escreva menu, ou Enter para fechar > ',
    'Type done, plan or menu, or Enter to close > ':
        'Escreva feito, plan ou menu, ou Enter para fechar > ',
    'Type plan or menu, or Enter to close > ':
        'Escreva plan ou menu, ou Enter para fechar > ',
    'Type done, plan or menu, or press Enter to close.':
        'Escreva feito, plan ou menu, ou prima Enter para fechar.',
    'Type plan or menu, or press Enter to close.':
        'Escreva plan ou menu, ou prima Enter para fechar.',
    "The saved file can't be read right now, or it is damaged.":
        'Não é possível ler agora o ficheiro guardado, ou está danificado.',
    'Nothing was changed. Saved in: ':
        'Nada foi alterado. Guardado em: ',
    'Deleting saved notes needs a person at the keyboard.':
        'Para eliminar as notas guardadas, é preciso estar alguém ao teclado.',
    '{option} needs on or off. Here are the options.':
        '{option} precisa de on ou off. Estas são as opções.',
    'Unknown option: {option}. Here are the options.':
        'Opção desconhecida: {option}. Estas são as opções.',
    '&Done':
        '&Feito',
    '&Not yet':
        '&Ainda não',
    'S&kip':
        '&Saltar',
    '&Save':
        '&Guardar',
    '&I did it':
        '&Já está',
    '&Options':
        '&Opções',
    'Close':
        'Fechar',
    'Not today':
        'Hoje não',
    'Did you do it?':
        'Conseguiu fazer?',
    'Done. A reminder comes when you sign in, if there is a plan to ask about.':
        'Pronto. Ao iniciar sessão, aparece um lembrete se houver um plano sobre o qual perguntar.',
    'Done. The Start menu opens a window with buttons.':
        'Pronto. O menu Iniciar abre uma janela com botões.',
    'Done. The Start menu opens this text screen.':
        'Pronto. O menu Iniciar abre este ecrã de texto.',
    'More options':
        'Mais opções',
    'Remind me when I sign in':
        'Lembrar-me ao iniciar sessão',
    'Show the thought and tip':
        'Mostrar o pensamento e a sugestão',
    'Type your plan in the box.':
        'Escreva o plano na caixa.',
    'Use a window with buttons (now this text screen)':
        'Usar uma janela com botões (agora este ecrã de texto)',
    'Use the text screen':
        'Usar o ecrã de texto',
    'Use this text screen (now a window with buttons)':
        'Usar este ecrã de texto (agora uma janela com botões)',
    'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
        'Quer um lembrete ao iniciar sessão? Mostra o plano da última vez e basta um clique para responder. Pode desativá-lo em Opções.',
    'Window or text screen (set by your organization)':
        'Janela ou ecrã de texto (definido pela sua organização)',
    'Your organization has set hello-world to open as a text screen.':
        'A sua organização definiu o hello-world para abrir como ecrã de texto.',
    'Saved.':
        'Guardado.',
    'Save your plan before closing?':
        'Guardar o plano antes de fechar?',
    'Delete all saved notes, dates and plans on this computer?':
        'Eliminar todas as notas, datas e planos guardados neste computador?',
    'Turn off: reminder when you sign in (now on)':
        'Desativar: lembrete ao iniciar sessão (agora ativado)',
    'Turn on: reminder when you sign in (now off)':
        'Ativar: lembrete ao iniciar sessão (agora desativado)',
    'Reminder when you sign in (turned off by your organization)':
        'Lembrete ao iniciar sessão (desativado pela sua organização)',
    'Reminder when you sign in: on.':
        'Lembrete ao iniciar sessão: ativado.',
    'Reminder when you sign in: off.':
        'Lembrete ao iniciar sessão: desativado.',
    'Reminder when you sign in: turned off by your organization.':
        'Lembrete ao iniciar sessão: desativado pela sua organização.',
    'Show the days-in-a-row message':
        'Mostrar a mensagem de dias seguidos',
    'Done. The thought and tip show next time you open hello-world.':
        'Pronto. O pensamento e a sugestão aparecem da próxima vez que abrir o hello-world.',
    "Clear today's plan?":
        'Limpar o plano de hoje?',
    'Next plan, if you want one:':
        'Próximo plano, se quiser:',
    'A few things? Put ; between them.':
        'Várias coisas? Separe-as com ;',
    'A plan can be up to {n} characters.':
        'Um plano pode ter até {n} caracteres.',
    'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
        'Conseguiu fazê-las? (s para todas, n para ainda não, os números das que fez, Enter para saltar) > ',
    'Last time you planned:':
        'Último plano:',
    'The rest is kept for today.':
        'O resto fica para hoje.',
    'Tick the ones you did, then click Done. With none ticked, Done means all of them.':
        'Assinale as que fez e clique em Feito. Sem nenhuma assinalada, Feito vale para todas.',
    'Type y for all, n for not yet, or the numbers you did, such as 1 3. Enter skips.':
        'Escreva s para todas, n para ainda não, ou os números das que fez, por exemplo 1 3. Enter salta.',
    'Your settings were kept.':
        'As definições foram mantidas.',
    'Language (set by your organization)':
        'Idioma (definido pela sua organização)',
    'Language (now {name})':
        'Idioma (agora {name})',
    'following Windows':
        'de acordo com o Windows',
    'Your organization shows hello-world in English.':
        'A sua organização mostra o hello-world em inglês.',
    'Follow Windows':
        'Seguir o Windows',
    'Type a number from 1 to {n}, or Enter to keep it > ':
        'Escreva um número de 1 a {n}, ou Enter para manter > ',
    'Done. The new language shows next time you open hello-world.':
        'Pronto. O novo idioma aparece da próxima vez que abrir o hello-world.',
    'Language...':
        'Idioma...',
    'Hello, {name}!':
        'Olá, {name}!',
    'One thing to get done today? Open hello-world to plan it.':
        'Uma coisa para fazer hoje? Abra o hello-world para a planear.',
    '&Open':
        '&Abrir',
    'Reminder settings...':
        'Definições do lembrete...',
    'Greet me by name':
        'Cumprimentar-me pelo nome',
    'At sign-in':
        'Ao iniciar sessão',
    'At {at}':
        'Às {at}',
    'Also on days with no plan':
        'Também nos dias sem plano',
    'Open hello-world after I answer':
        'Abrir o hello-world depois de responder',
    'Not on weekends':
        'Não aos fins de semana',
    'Done. A reminder comes at {at} each day, if there is a plan to ask about.':
        'Pronto. Todos os dias às {at} aparece um lembrete, se houver um plano sobre o qual perguntar.',
    'Send feedback...':
        'Enviar comentários...',
    '"holidays" must be a list of at most {n} dates.':
        '"holidays" tem de ser uma lista com, no máximo, {n} datas.',
    '"title" must be 1 to 40 characters of plain text, with no link or address.':
        '"title" tem de ter de 1 a 40 caracteres de texto simples, sem ligações nem endereços.',
    '"{list}" must be a list of {low} to {high} lines.':
        '"{list}" tem de ser uma lista de {low} a {high} linhas.',
    "Can't read {path}: {error}":
        'Não é possível ler {path}: {error}',
    'Could not save that on this computer.':
        'Não foi possível guardar neste computador.',
    'Days you opened hello-world: {n}':
        'Dias em que abriu o hello-world: {n}',
    'Keep a longer history':
        'Guardar um histórico mais longo',
    'Keep my numbers':
        'Guardar os meus números',
    'Longest run of days: {n}':
        'Maior sequência de dias: {n}',
    "Mark today's plan done":
        'Marcar o plano de hoje como feito',
    "Mark today's plan done (plans are turned off)":
        'Marcar o plano de hoje como feito (planos desativados)',
    'My numbers are off. Turn them on under Options, or with --set numbers on.':
        'Os meus números estão desativados. Pode ativá-los em Opções ou com --set numbers on.',
    'My numbers...':
        'Os meus números...',
    'Nothing finished yet this week. That is fine.':
        'Ainda nada concluído esta semana. Não faz mal.',
    'OK: {thoughts} thoughts and {tips} tips.':
        'OK: {thoughts} pensamentos e {tips} sugestões.',
    'Plans finished: {n}':
        'Planos concluídos: {n}',
    'Save my plans to a file':
        'Guardar os meus planos num ficheiro',
    'Saved to {path}':
        'Guardado em {path}',
    "The file isn't valid JSON, or is over 200,000 characters.":
        'O ficheiro não é JSON válido ou tem mais de 200 000 caracteres.',
    'The file must hold an object with two lists, "thoughts" and "tips", and may add "holidays" and "title".':
        'O ficheiro tem de conter um objeto com duas listas, "thoughts" e "tips", e pode acrescentar "holidays" e "title".',
    'This week you finished {n}:':
        'Esta semana concluiu {n}:',
    'This week...':
        'Esta semana...',
    'holidays line {line} is not a date like 2026-12-25.':
        'A linha {line} de holidays não é uma data como 2026-12-25.',
    '{list} line {line} has a date.':
        'A linha {line} de {list} tem uma data.',
    '{list} line {line} has a link or an address.':
        'A linha {line} de {list} tem uma ligação ou um endereço.',
    '{list} line {line} has control characters or extra spaces.':
        'A linha {line} de {list} tem caracteres de controlo ou espaços a mais.',
    '{list} line {line} is not text.':
        'A linha {line} de {list} não é texto.',
    '{list} line {line} must be {low} to {high} characters long.':
        'A linha {line} de {list} tem de ter entre {low} e {high} caracteres.',
}
LANGUAGES["pt-PT"] = {**LANGUAGES["pt"],
    "text": {**LANGUAGES["pt"]["text"], **_PT_PT_TEXT},
    "thoughts": _override(LANGUAGES["pt"]["thoughts"], {
        0: 'Abrir aquele documento que tem andado a adiar e ler só o primeiro parágrafo.',
        1: 'Dez minutos de arranque já são um começo, e costumam tornar os dez seguintes mais fáceis.',
        2: 'Hoje não é preciso ter o plano todo, só um primeiro passo sensato.',
        3: 'Escrever a primeira frase, mesmo que fique feia. Dá algo real para melhorar depois.',
        4: 'Arrumar um cantinho da secretária e reparar como o resto parece logo mais calmo.',
        5: 'Escolher a tarefa mais pequena da lista e terminá-la antes de olhar para as outras.',
        6: 'Começar mal numa manhã calma é melhor do que esperar por um momento perfeito que pode não chegar.',
        7: 'Pôr o primeiro passo no calendário, para que tenha um lugar seu.',
        8: 'Os grandes projetos são sobretudo pequenas tardes umas atrás das outras. O objetivo é uma tarde de cada vez.',
        9: 'Dizer em voz alta a próxima ação e deixar o resto da lista esperar pela sua vez.',
        10: 'Há dias em que o ritmo é mais lento do que gostaria, e esse ritmo também conta.',
        11: 'Falar consigo da mesma forma que falaria com alguém novo na equipa, na primeira semana.',
        12: 'Não há mal nenhum em continuar a aprender algo que faz há anos.',
        13: 'Uma manhã fraca não decide a tarde. Pode recomeçar depois do almoço.',
        14: 'O cansaço é informação, não uma falha. Ajustar o plano e continuar com calma.',
        15: 'Tratar-se com a mesma compreensão que oferece tão facilmente aos outros.',
        16: 'O progresso muitas vezes parece nada durante algum tempo e, de repente, é uma página terminada.',
        17: 'Não faz mal precisar de ler algo duas vezes para fazer sentido.',
        18: 'Não é preciso sentir-se a postos. Fazer com nervos também é fazer.',
        19: 'O melhor de hoje pode ser menos do que o de ontem, e não faz mal.',
        20: 'Fechar os separadores que não estão a ser usados. A atenção agradece em poucos minutos.',
        21: 'Uma tarefa, uma janela, vinte e cinco minutos. Ver até onde chega um bocado de sossego.',
        22: 'Anotar o pensamento solto que aparecer e voltar ao que estava a fazer.',
        23: 'Se possível, silenciar o telemóvel durante uma hora e dar ao trabalho toda a atenção.',
        24: 'Decidir que coisa faria de hoje um bom dia e guardar tempo para ela.',
        25: 'Fazer uma coisa de cada vez costuma ser mais rápido do que parece.',
        26: 'Uma lista arrumada de três coisas vale mais do que uma lista dispersa de vinte.',
        27: 'Reparar quando a mente se distrai e trazê-la de volta sem ralhar.',
        28: 'Pôr a tarefa mais difícil na hora em que há mais energia, mesmo que não seja logo de manhã.',
        29: 'Auscultadores postos, chaleira cheia, porta fechada. Preparar o ambiente e a concentração vem a seguir.',
        30: 'Afastar-se do ecrã durante cinco minutos. No regresso, a cabeça vem um pouco mais clara.',
        31: 'Hoje, almoçar longe da secretária. A caixa de entrada pode esperar por uma sandes.',
        32: 'Uma volta curta ao edifício também é trabalho a sério para a cabeça.',
        33: 'Um minuto longe do ecrã é uma boa forma de usar uma tarde atarefada.',
        34: 'Esticar os ombros e descontrair o maxilar. Talvez estejam tensos há horas.',
        35: 'Se possível, sair a horas hoje. Amanhã vai agradecer o serão livre.',
        36: 'Descansar faz parte do trabalho, porque o cansaço leva a repetir o mesmo deslize.',
        37: 'Descansar os olhos um momento e deixar cair os ombros.',
        38: 'Uma pausa a sério faz a segunda metade do dia parecer um novo começo.',
        39: 'O serão é seu. Nada na caixa de entrada precisa de resposta às nove da noite.',
        40: 'Agradecer hoje a alguém uma pequena coisa que fez sem ninguém pedir.',
        41: 'A maioria das pessoas está a fazer o melhor que pode, com mais coisas em mãos do que se vê.',
        42: 'Descobrir como alguém da equipa gosta do chá ou do café. Lembrar-se disso é um pequeno presente.',
        43: 'Se alguém responder de forma seca, pensar num dia difícil e não num julgamento.',
        44: 'Segurar a porta, partilhar as bolachas e deixar a outra pessoa acabar a frase.',
        45: 'Um olá rápido e uma pergunta sobre o fim de semana podem ser o melhor da manhã.',
        46: 'Quando alguém novo perguntar algo óbvio, lembrar-se de que também já fez essa pergunta.',
        47: 'Reconhecer em voz alta quando a ideia de alguém da equipa melhorou o trabalho.',
        48: 'Responder a uma mensagem com um pouco de simpatia. Não custa nada e é bem recebido.',
        49: 'Falar com alguém da equipa que tem falado pouco nas reuniões e perguntar como está.',
        50: 'Terminar o que está quase feito antes de começar algo novo.',
        51: 'Terminado e suficientemente bom costuma ser mais útil do que perfeito e por terminar.',
        52: 'Fechar hoje um assunto pendente e reparar no pequeno alívio que vem a seguir.',
        53: 'Os últimos dez por cento são muitas vezes só uns minutos de cuidado. Vale a pena dedicá-los hoje.',
        54: 'Enviar o e-mail que está à espera nos rascunhos. Provavelmente está bem assim.',
        55: 'Marcar como concluído, respirar fundo e ficar contente por estar feito.',
        56: 'Uma coisa pequena terminada vale mais do que uma grande a meio.',
        57: 'Antes de terminar a sessão, anotar o primeiro passo de amanhã para não ter de se lembrar dele.',
        58: 'Ler mais uma vez, corrigir o que encontrar e depois enviar.',
        59: 'Acabar o dia com um resultado arrumado torna o serão mais leve.',
        60: 'Perguntar cedo costuma poupar uma hora de luta em silêncio mais tarde.',
        61: 'A maioria das pessoas gosta que lhe peçam o que sabe. Perguntar sem pedir desculpa.',
        62: '"Não sei como avançar" é uma frase clara e útil, com a qual a equipa pode trabalhar.',
        63: 'Pedir o que precisa em palavras simples e dar aos outros a oportunidade de dizer que sim.',
        64: 'Duas pessoas a olhar para um problema resolvem-no muitas vezes mais depressa do que uma sozinha.',
        65: 'Precisar de ajuda não faz de ninguém um fardo. Faz parte de trabalhar em equipa.',
        66: 'Levar uma pergunta concreta permite a quem responde dar uma resposta concreta.',
        67: 'Se as instruções não forem claras, pedir esclarecimentos faz parte de fazer bem o trabalho.',
        68: 'Oferecer ajuda quando puder e aceitá-la quando precisar. As duas coisas ficam mais fáceis com a prática.',
        69: 'Provavelmente alguém ao fundo do corredor já resolveu isto. Vale a pena ir procurar essa pessoa.',
        70: 'Tomar nota do que conseguiu resolver esta semana. Soma mais do que parece.',
        71: 'Ser principiante em algo novo é sinal de que o trabalho continua a crescer.',
        72: 'Reparar como alguém que admira lida com uma chamada difícil e aproveitar uma coisa.',
        73: 'Ler uma página útil durante a pausa e dar o dia por bem aproveitado para a cabeça.',
        74: 'Explicar uma tarefa a outra pessoa é uma forma surpreendentemente boa de a aprender.',
        75: 'Não faz mal dizer "ainda não sei" e depois ir descobrir.',
        76: 'Qualquer sistema desconhecido parece confuso até ser usado meia dúzia de vezes.',
        77: 'Perguntar a alguém com mais experiência como aprendeu. A resposta costuma tranquilizar.',
        78: 'As competências vêm da repetição. Repetir a coisa pequena até ficar fácil.',
        79: 'Um pouco de curiosidade sobre uma tarefa comum pode torná-la mais interessante.',
        80: 'Um erro apanhado cedo é só uma correção, e a maioria é apanhada cedo.',
        81: 'Corrigir, avisar quem precisa de saber e deixar passar o incómodo.',
        82: 'Quase todos os erros no trabalho parecem mais pequenos uma semana depois.',
        83: 'Um deslize não apaga os anos de trabalho cuidadoso que ficaram para trás.',
        84: 'Quando algo corre mal, olhar primeiro para o processo e só depois para a pessoa.',
        85: 'Toda a gente à sua volta já enviou um e-mail à pessoa errada pelo menos uma vez.',
        86: 'Ficar com a lição que um erro traz e deixar o resto para trás.',
        87: 'Assumir um erro com simplicidade costuma gerar mais confiança do que nunca ter errado.',
        88: 'Até as pessoas cuidadosas têm dias desastrados, e esses dias passam até ao fim da tarde.',
        89: 'Daqui a um mês, a maioria dos pequenos tropeções de hoje já estará esquecida.',
        90: 'Um dia calmo sem nada a arder é um bom dia, mesmo que ninguém o diga.',
        91: 'Reparar nos pequenos prazeres: uma caneca quente, uma caixa de entrada vazia, um minuto de sossego.',
        92: 'Nem todos os dias precisam de uma grande vitória. Com constância e bom ambiente também se trabalha bem.',
        93: 'Aproveitar a reunião que acaba cinco minutos mais cedo e usar esse tempo como quiser.',
        94: 'Um dia normal bem feito é motivo para um orgulho tranquilo.',
        95: 'O bom trabalho muitas vezes não se nota de fora, e não faz mal.',
        96: 'Deixar uma tarde agradável ser agradável, sem esperar que seja produtiva.',
        97: 'As pequenas rotinas do dia, o primeiro café e as caras conhecidas, merecem atenção.',
        98: 'Hoje esteve cá e fez a sua parte, e isso chega.',
        99: 'Ao fim do dia, tirar um momento para recordar uma coisa que correu bem hoje.',
        100: 'Um minuto de sossego entre duas tarefas não é tempo perdido; é assim que a seguinte começa bem.',
    }),
    "tips": _override(LANGUAGES["pt"]["tips"], {
        0: 'Beber um copo de água devagar, longe do ecrã.',
        1: 'Rodar os ombros para trás cinco vezes, bem devagar.',
        2: 'Descansar os olhos vinte segundos: olhar para longe ou fechá-los.',
        3: 'Esticar os braços para cima, na cadeira ou de pé, e respirar fundo.',
        4: 'Ir até à sala ou janela mais distante que conseguir e voltar.',
        5: 'Verificar a postura e deixar os ombros descer, longe das orelhas.',
        6: 'Rodar o pescoço devagar de um lado para o outro, só até onde for confortável.',
        7: 'Abrir e fechar as mãos dez vezes para soltar os dedos.',
        8: 'Afixar o documento que abre mais vezes, para ficar à distância de um clique.',
        9: 'Dar um pequeno passeio lá fora, a pé ou em cadeira de rodas, como for melhor.',
        10: 'Servir uma bebida quente ou fresca e apreciá-la longe do ecrã.',
        11: 'Pousar a atenção em algo calmo: uma vista, um som ou uma textura.',
        12: 'Escrever o próximo passo de uma tarefa que ficou a meio.',
        13: 'Assentar bem os pés no chão e endireitar as costas, na cadeira ou de pé, durante dez respirações.',
        14: 'Silenciar um chat de grupo que só lê na diagonal.',
        15: 'Descontrair o maxilar e relaxar a testa por um momento.',
        16: 'Mexer-se durante dois minutos, da forma que souber melhor hoje.',
        17: 'Reservar quinze minutos no calendário para a tarefa que anda sempre a adiar.',
        18: 'Ajustar a cadeira, o ecrã ou o teclado para que uma coisa fique mais confortável.',
        19: 'Se possível, ir pelo caminho mais longo para a próxima reunião ou chamada.',
        20: 'Guardar um modelo para um e-mail que escreve vezes sem conta.',
        21: 'Aprender um atalho de teclado do programa que mais usa.',
        22: 'Beber um copo de água cheio antes do próximo café ou chá.',
        23: 'Encolher os ombros até às orelhas e depois deixá-los descer devagar.',
        24: 'Sair um minuto ou abrir uma janela para apanhar ar fresco.',
        25: 'Respirar devagar cinco vezes, com cada expiração um pouco mais longa.',
        26: 'Fazer uma pausa de um minuto em silêncio antes de abrir a próxima mensagem.',
        27: 'Anotar uma coisa boa que já aconteceu hoje.',
        28: 'Fechar os olhos durante três respirações e reparar em como se sente.',
        29: 'Nomear três coisas que nota neste momento, com qualquer um dos sentidos.',
        30: 'Escrever uma coisa boa que vem aí esta semana.',
        31: 'Pôr um temporizador de dois minutos e ficar simplesmente sem ecrã.',
        32: 'Apreciar algo pequeno por perto, como uma planta ou a caneca preferida.',
        33: 'Pensar numa coisa que fez bem esta semana e reconhecê-la.',
        34: 'Ouvir uma canção preferida do princípio ao fim, sem mais nada aberto.',
        35: 'Inspirar a contar até quatro e expirar a contar até seis, três vezes.',
        36: 'Respirar uma vez antes de reagir ao próximo pequeno incómodo.',
        37: 'Anotar uma coisa que deu vontade de rir há pouco tempo.',
        38: 'Durante um minuto, reparar em algo agradável: um som, um cheiro ou algo em que toca.',
        39: 'Recordar um sítio de que gosta muito e imaginá-lo durante trinta segundos.',
        40: 'Dizer "por agora está bom assim" sobre uma tarefa pequena e seguir em frente.',
        41: 'Escrever uma frase sobre algo pelo qual sente gratidão.',
        42: 'Saborear o próximo gole da bebida e reparar no sabor.',
        43: 'Fazer uma pequena pausa entre duas tarefas antes de começar a seguinte.',
        44: 'Procurar hoje uma coisa que corra melhor do que esperava.',
        45: 'Escolher uma palavra para a forma como quer que a tarde seja.',
        46: 'Deixar a mente descansar sessenta segundos e depois voltar à próxima tarefa.',
        47: 'Sentir os pés no chão e a firmeza que isso dá, durante um momento.',
        48: 'Recordar algo simpático que alguém fez por si e aproveitar a memória.',
        49: 'Anotar uma ideia para retomar mais tarde e deixá-la repousar.',
        50: 'Arrumar um pequeno canto da secretária, só um.',
        51: 'Responder a uma mensagem que está à espera há algum tempo.',
        52: 'Apontar a tarefa principal de amanhã num post-it ou nas notas.',
        53: 'Fechar os separadores do browser que já não são precisos.',
        54: 'Agradecer a alguém da equipa uma coisa que fez recentemente.',
        55: 'Arquivar cinco e-mails antigos que já não são precisos.',
        56: 'Mudar o nome de um ficheiro desarrumado para o encontrar facilmente mais tarde.',
        57: 'Tirar um ou dois ficheiros perdidos do ambiente de trabalho.',
        58: 'Apagar um lembrete antigo que já não se aplica.',
        59: 'Dar um título claro a um documento que abre muitas vezes.',
        60: 'Riscar uma tarefa pequena da lista de tarefas.',
        61: 'Cancelar a subscrição de uma newsletter que nunca lê.',
        62: 'Limpar o teclado ou o ecrã com um pano macio.',
        63: 'Deixar uma caneta, um caderno e água ao alcance da mão.',
        64: 'Escrever uma nota curta para amanhã a dizer onde ficou hoje.',
        65: 'Escolher a tarefa mais importante desta tarde e fazê-la primeiro.',
        66: 'Esvaziar o caixote do lixo ou da reciclagem junto à secretária.',
        67: 'Atualizar uma nota de progresso para que os outros vejam em que ponto estão as coisas.',
        68: 'Arrumar a pasta Transferências: mover só uma mão-cheia de ficheiros.',
        69: 'Criar um lembrete para uma coisa que costuma esquecer.',
        70: 'Desativar uma notificação que não faz mesmo falta.',
        71: 'Adicionar aos favoritos uma página que está sempre a procurar.',
        72: 'Escrever um resumo de duas linhas de uma reunião enquanto ainda está fresca.',
        73: 'Perguntar se uma reunião recorrente podia ser um pouco mais curta.',
        74: 'Definir um único objetivo para a próxima hora e escrevê-lo.',
        75: 'Perguntar a alguém da equipa como está a correr o dia e ouvir com atenção.',
        76: 'Partilhar uma ligação útil com alguém que possa gostar dela.',
        77: 'Cumprimentar alguém com quem ainda não falou.',
        78: 'Enviar uma nota rápida de agradecimento a alguém que ajudou recentemente.',
        79: 'Cumprimentar toda a gente com simpatia no início da próxima chamada.',
        80: 'Perguntar a alguém da equipa o que de bom vem aí esta semana.',
        81: 'Dar os parabéns a alguém por uma pequena vitória em que reparou.',
        82: 'Convidar alguém do trabalho para uma conversa rápida com um chá, um café ou numa chamada.',
        83: 'Elogiar algo concreto que alguém do trabalho fez bem.',
        84: 'Aprender o nome de alguém que vê muitas vezes mas ainda não conhece.',
        85: 'Partilhar um conselho útil com alguém da equipa que possa precisar dele.',
        86: 'Pedir a alguém que recomende uma música, uma série ou um livro.',
        87: 'Ir saber de alguém do trabalho que tem falado pouco ultimamente.',
        88: 'Oferecer ajuda numa coisa pequena se alguém parecer ter muito trabalho.',
        89: 'Cumprimentar com simpatia a próxima pessoa com quem se cruzar.',
        90: 'Passar a alguém do trabalho uma palavra simpática que ouviu sobre essa pessoa.',
        91: 'Perguntar a alguém do trabalho o que lhe facilitou a semana.',
        92: 'Enviar uma mensagem simpática a alguém com quem já trabalhou.',
        93: 'Agradecer a quem mantém os espaços partilhados a funcionar bem.',
        94: 'Apresentar duas pessoas do trabalho que possam gostar de se conhecer.',
        95: 'Perguntar a alguém da equipa como pode facilitar a passagem de uma tarefa.',
        96: 'Partilhar uma piada pequena e inofensiva com alguém por perto.',
        97: 'Pôr um pouco mais de simpatia no próximo pedido e no próximo agradecimento.',
        98: 'Perguntar a alguém do trabalho o que gosta de fazer nos tempos livres.',
        99: 'Ouvir com toda a atenção a próxima pessoa que falar consigo, sem fazer outras coisas ao mesmo tempo.',
    }),
    "done": _override(LANGUAGES["pt"]["done"], {
        0: 'Muito bem. Esse já está.',
        1: 'Boa. Sabe bem terminar alguma coisa.',
        2: 'Muito bem. Agora uma pequena pausa antes do próximo.',
        3: 'Boa. As pequenas tarefas concluídas vão somando.',
        4: 'Está feito. É motivo para ficar contente.',
        5: 'Boa. Menos uma coisa na lista.',
    }),
}

# ---- Arabic ----

LANGUAGES["ar"] = {
    "days": ('الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد'),
    "months": ('يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'),
    "date": '{day}، {d} {month} {year}',
    "thoughts": (
        'يكفي فتح المستند الذي طال تأجيله وقراءة فقرته الأولى فقط.',
        'عشر دقائق من البدء تبقى بداية، وغالبًا ما تجعل الدقائق العشر التالية أسهل.',
        'لا حاجة إلى الخطة كاملة اليوم، تكفي خطوة أولى معقولة.',
        'الجملة الأولى الركيكة تستحق الكتابة، فهي تمنحك شيئًا حقيقيًا لتحسينه لاحقًا.',
        'ترتيب زاوية صغيرة من المكتب يجعل بقيته تبدو أهدأ بكثير.',
        'البدء بأصغر مهمة في القائمة وإنهاؤها قبل النظر إلى البقية.',
        'بداية متعثرة في صباح هادئ أفضل من انتظار لحظة مثالية قد لا تأتي.',
        'وضع الخطوة الأولى في التقويم يمنحها مكانًا ثابتًا.',
        'المشاريع الكبيرة في معظمها جلسات عمل صغيرة متراكمة، فلتكن الغاية جلسة واحدة.',
        'يكفي تسمية الخطوة التالية بصوت مسموع، ولتنتظر بقية القائمة دورها.',
        'في بعض الأيام يكون الإيقاع أبطأ مما نحب، وهذا الإيقاع يُحتسب أيضًا.',
        'لنتحدث إلى أنفسنا كما نتحدث إلى زميل جديد في أسبوعه الأول.',
        'لا بأس في أن نظل نتعلم شيئًا نفعله منذ سنوات.',
        'الصباح الفاتر لا يحدد شكل ما بعد الظهر. يمكن البدء من جديد بعد الغداء.',
        'التعب معلومة، لا تقصير. نعدّل الخطة ونكمل بهدوء.',
        'لنمنح أنفسنا التسامح نفسه الذي نمنحه للآخرين بسهولة.',
        'كثيرًا ما يبدو التقدم كأنه لا شيء لفترة، ثم يصير فجأة صفحة مكتملة.',
        'لا بأس في الحاجة إلى قراءة ثانية حتى تتضح الأمور.',
        'ليس شرطًا أن نشعر بالاستعداد. العمل مع شيء من التوتر يبقى عملًا.',
        'قد يكون أفضل ما نقدر عليه اليوم أقل مما كان بالأمس، ولا بأس بذلك.',
        'إغلاق علامات التبويب غير المستخدمة يريح الانتباه خلال دقائق.',
        'مهمة واحدة، نافذة واحدة، خمس وعشرون دقيقة. لنرَ إلى أين تصل فترة هادئة.',
        'تدوين الفكرة العابرة حين تخطر، ثم العودة إلى ما كنا نفعله.',
        'إسكات الهاتف لساعة إن أمكن، ومنح العمل كامل الانتباه.',
        'ما الشيء الواحد الذي يجعل اليوم يومًا جيدًا؟ يستحق أن يُحجز له وقت.',
        'إنجاز الأمور واحدًا تلو الآخر أسرع عادةً مما يبدو.',
        'قائمة مرتبة من ثلاثة أشياء أفضل من قائمة مبعثرة من عشرين.',
        'حين يشرد الذهن، نعيده بهدوء ومن دون لوم.',
        'أصعب مهمة تستحق أفضل أوقات النشاط، حتى لو لم يكن ذلك أول الصباح.',
        'سماعات على الأذنين، وإبريق الشاي جاهز، وباب مغلق. حين تتهيأ الأجواء يأتي التركيز.',
        'خمس دقائق بعيدًا عن الشاشة تعيدنا إليها بذهن أصفى قليلًا.',
        'غداء اليوم بعيدًا عن المكتب. يمكن للبريد أن ينتظر ريثما ينتهي الغداء.',
        'جولة قصيرة حول المبنى عمل حقيقي لصالح الذهن.',
        'دقيقة بعيدًا عن الشاشة وقت في محله، حتى في يوم مزدحم.',
        'إرخاء الكتفين وفك انقباض الفك. ربما بقيا مشدودين لساعات.',
        'المغادرة في الموعد الليلة إن أمكن. غدًا ستشكرك نفسك على هذا المساء.',
        'الراحة جزء من العمل، فالتعب يدفع إلى تكرار الخطأ نفسه.',
        'إراحة العينين لحظة، وترك الكتفين ينخفضان.',
        'استراحة حقيقية تجعل النصف الثاني من اليوم يبدو كبداية جديدة.',
        'المساء لك. لا شيء في البريد يحتاج إليك في التاسعة ليلًا.',
        'كلمة شكر اليوم لشخص قام بشيء صغير من دون أن يُطلب منه.',
        'معظم الناس يبذلون ما في وسعهم، وعلى كاهلهم أكثر مما يظهر.',
        'معرفة كيف يحب الزميل شايه أو قهوته هدية صغيرة تستحق التذكر.',
        'إن بدا أحدهم حادًّا معك، فالأرجح أن يومه صعب، لا أنه يحكم عليك.',
        'إمساك الباب، ومشاركة البسكويت، وترك الآخرين يكملون كلامهم.',
        'تحية سريعة وسؤال عن عطلة نهاية الأسبوع قد يكونان أجمل ما في الصباح.',
        'حين يسأل زميل جديد عن شيء بديهي، لنتذكر أننا سألنا عنه يومًا.',
        'فكرة زميل حسّنت عملك؟ ذِكر فضله أمام الآخرين لفتة جميلة.',
        'قليل من الدفء في الرد على رسالة لا يكلف شيئًا ويصل بلطف.',
        'زميل كان هادئًا في الاجتماعات مؤخرًا قد يسعده سؤال عن حاله.',
        'إنهاء ما أوشك على الاكتمال قبل البدء بشيء جديد.',
        'المنجَز الجيد بما يكفي أنفع عادةً من الكامل غير المنجَز.',
        'إغلاق مسألة معلقة واحدة اليوم، وملاحظة الارتياح الصغير الذي يليه.',
        'الجزء الأخير غالبًا ليس سوى دقائق قليلة من العناية. اليوم وقت مناسب لها.',
        'الرسالة المنتظرة في المسودات جاهزة على الأرجح كما هي. حان وقت إرسالها.',
        'وضع علامة الاكتمال، وأخذ نفس، والرضا بأنه انتهى.',
        'شيء صغير مكتمل أثمن من شيء كبير نصف مكتمل.',
        'قبل تسجيل الخروج، تدوين أول خطوة للغد على ورقة يغني عن تذكرها.',
        'قراءة أخيرة، وتصحيح ما يظهر، ثم الإرسال.',
        'إنهاء اليوم بنتيجة واحدة مرتبة يجعل المساء أخف.',
        'السؤال المبكر يوفر غالبًا ساعة من المعاناة الصامتة لاحقًا.',
        'معظم الناس يسعدهم أن يُسألوا عما يعرفون. لا داعي للاعتذار عند السؤال.',
        '"أحتاج إلى مساعدة هنا" جملة واضحة ومفيدة يستطيع الزملاء البناء عليها.',
        'طلب ما نحتاج إليه بكلمات بسيطة يمنح الآخرين فرصة لقول نعم.',
        'اثنان ينظران إلى مشكلة يحلانها غالبًا أسرع من واحد يحدق فيها وحده.',
        'طلب المساعدة لا يجعلك عبئًا. أنت جزء من الفريق.',
        'السؤال المحدد يلقى إجابة محددة.',
        'حين تكون التعليمات غير واضحة، فطلب التوضيح جزء من أداء العمل كما ينبغي.',
        'تقديم المساعدة عند الإمكان، وقبولها عند الحاجة. كلاهما يسهل بالممارسة.',
        'على الأرجح أن أحدًا في آخر الممر حلّ هذا من قبل. يستحق أن نبحث عنه.',
        'قائمة صغيرة بما تعلمناه هذا الأسبوع تكبر أسرع مما نظن.',
        'أن نكون مبتدئين في شيء جديد علامة على أن عملنا لا يزال ينمو.',
        'مراقبة كيف يتعامل زميل نقدّره مع مكالمة صعبة، واستعارة شيء واحد منه.',
        'قراءة صفحة مفيدة واحدة في الاستراحة تكفي ليكون اليوم جيدًا للذهن.',
        'شرح مهمة لشخص آخر طريقة جيدة على نحو مفاجئ لتعلّمها.',
        'لا بأس بقول "لا أعرف ذلك بعد"، ثم البحث عن الإجابة.',
        'كل نظام غير مألوف يبدو مربكًا حتى نستخدمه بضع مرات.',
        'سؤال صاحب الخبرة عن طريقة تعلّمه كثيرًا ما يأتي بإجابة مطمئنة.',
        'المهارة تأتي من التكرار، فلنكرر الشيء الصغير حتى يصبح سهلًا.',
        'قليل من الفضول تجاه مهمة عادية قد يجعلها أكثر إمتاعًا.',
        'الخطأ الذي يُكتشف مبكرًا مجرد تصحيح، ومعظم الأخطاء تُكتشف مبكرًا.',
        'الإصلاح، ثم إبلاغ من يلزم، ثم ترك الانزعاج يتلاشى.',
        'كل خطأ تقريبًا في العمل يبدو بعد أسبوع أصغر مما بدا في لحظته.',
        'زلة واحدة لا تمحو سنوات العمل المتقن خلفك.',
        'حين يحدث خطأ، ننظر في الإجراءات أولًا، ثم في الأشخاص.',
        'كل من حولك أرسل بريدًا إلى الشخص الخطأ مرة واحدة على الأقل.',
        'من كل خطأ درس واحد نأخذه، والباقي نتركه خلفنا.',
        'الاعتراف بالخطأ بوضوح يكسب ثقة أكبر عادةً من ألا يخطئ المرء أبدًا.',
        'اليوم المتعثر يمر به الحريصون أيضًا، وينتهي بحلول المساء.',
        'معظم عثرات اليوم الصغيرة لن يبقى منها شيء في الذاكرة الشهر المقبل.',
        'يوم هادئ بلا حرائق يوم جيد، حتى لو لم يذكره أحد.',
        'المتع الصغيرة تستحق الانتباه: كوب دافئ، وبريد فارغ، ودقيقة هادئة.',
        'ليس كل يوم بحاجة إلى إنجاز كبير. الثبات والهدوء طريقة جيدة للعمل.',
        'اجتماع ينتهي قبل موعده بخمس دقائق متعة صغيرة، والدقائق الخمس لك.',
        'يوم عادي أُنجز جيدًا أمر يستحق فخرًا هادئًا.',
        'العمل الجيد يبدو غالبًا عاديًا من الخارج، ولا بأس بذلك.',
        'إن كان العصر هادئًا لطيفًا، فليبقَ كذلك من دون انتظار أن يكون مثمرًا.',
        'تفاصيل اليوم الصغيرة، كالقهوة الأولى والوجوه المألوفة، تستحق الانتباه.',
        'اليوم حضرت وقمت بنصيبك، وهذا كافٍ تمامًا.',
        'لحظة هذا المساء لتذكّر شيء واحد سار على ما يرام اليوم.',
        'دقيقة هادئة بين مهمتين ليست وقتًا ضائعًا، بل بها تبدأ المهمة التالية جيدًا.',
    ),
    "tips": (
        'ارتشاف كوب ماء ببطء، بعيدًا عن الشاشة.',
        'تدوير الكتفين إلى الخلف خمس مرات، على مهل.',
        'إراحة العينين عشرين ثانية: بالنظر بعيدًا، أو بإغماضهما.',
        'مدّ الذراعين فوق الرأس، جلوسًا أو وقوفًا، مع نفس عميق.',
        'الذهاب إلى أبعد غرفة أو نافذة يمكن الوصول إليها، ثم العودة.',
        'الانتباه إلى وضعية الجلوس، وإرخاء الكتفين بعيدًا عن الأذنين.',
        'تحريك الرقبة برفق من جانب إلى آخر، في حدود الراحة فقط.',
        'فتح اليدين وإغلاقهما عشر مرات لإرخاء الأصابع.',
        'تثبيت المستند الأكثر استخدامًا ليصبح على بعد نقرة واحدة.',
        'جولة قصيرة في الخارج، مشيًا أو بالكرسي المتحرك، حسب ما يناسب.',
        'تحضير مشروب دافئ أو بارد والاستمتاع به بعيدًا عن الشاشة.',
        'إراحة الانتباه على شيء هادئ: منظر، أو صوت، أو ملمس.',
        'كتابة الخطوة التالية لمهمة توقفت في منتصفها.',
        'وضع القدمين على الأرض والجلوس أو الوقوف باستقامة لعشرة أنفاس.',
        'كتم صوت مجموعة دردشة لا تُقرأ إلا على عجل.',
        'إرخاء الفك والجبهة للحظة.',
        'الحركة لدقيقتين بأي طريقة مريحة اليوم.',
        'حجز ربع ساعة في التقويم للمهمة التي تتأجل باستمرار.',
        'ضبط الكرسي أو الشاشة أو لوحة المفاتيح لجعل شيء واحد أكثر راحة.',
        'سلوك الطريق الأطول إلى الاجتماع أو المكالمة التالية، إن أمكن.',
        'حفظ قالب لرسالة بريد تتكرر كتابتها.',
        'تعلّم اختصار لوحة مفاتيح واحد للبرنامج الأكثر استخدامًا.',
        'شرب كوب ماء كامل قبل القهوة أو الشاي التالي.',
        'رفع الكتفين نحو الأذنين، ثم تركهما ينسدلان.',
        'الخروج أو فتح نافذة لدقيقة من الهواء النقي.',
        'خمسة أنفاس بطيئة، مع إطالة كل زفير قليلًا.',
        'دقيقة هدوء قبل فتح الرسالة التالية.',
        'تدوين شيء جيد حدث اليوم حتى الآن.',
        'إغماض العينين لثلاثة أنفاس، والانتباه إلى الشعور الحالي.',
        'تسمية ثلاثة أشياء ملحوظة الآن، بأي حاسة.',
        'تدوين شيء يُنتظر بشوق هذا الأسبوع.',
        'ضبط مؤقت لدقيقتين والجلوس ببساطة بلا شاشة.',
        'الاستمتاع بشيء صغير قريب، مثل نبتة أو كوب مفضل.',
        'تذكّر شيء أُنجز جيدًا هذا الأسبوع، والرضا عنه للحظة.',
        'الاستماع إلى أغنية مفضلة من أولها إلى آخرها، بلا أي شيء آخر مفتوح.',
        'شهيق لأربع عدّات وزفير لست، ثلاث مرات.',
        'نفس واحد قبل الرد على الإزعاج الصغير التالي.',
        'تدوين شيء أضحكك مؤخرًا.',
        'دقيقة لملاحظة شيء لطيف: صوت، أو رائحة، أو ملمس.',
        'استحضار مكان محبب وتخيّله لثلاثين ثانية.',
        'قول "جيد بما يكفي الآن" عن مهمة صغيرة، ثم المضي قدمًا.',
        'كتابة جملة واحدة عن شيء يبعث على الامتنان.',
        'تذوّق الرشفة التالية من المشروب والانتباه إلى طعمها.',
        'استراحة قصيرة بين مهمتين قبل بدء التالية.',
        'البحث اليوم عن شيء واحد يأتي أفضل من المتوقع.',
        'اختيار كلمة واحدة تصف الشعور المرجو لفترة ما بعد الظهر.',
        'إراحة الذهن ستين ثانية، ثم العودة إلى المهمة التالية.',
        'الإحساس بالقدمين على الأرض، والثبات للحظة.',
        'تذكّر لطف قدّمه أحدهم لك، والاستمتاع بالذكرى.',
        'تدوين فكرة للعودة إليها لاحقًا، ثم تركها جانبًا.',
        'ترتيب زاوية صغيرة من المكتب، واحدة فقط.',
        'الرد على رسالة واحدة تنتظر منذ مدة.',
        'كتابة أهم مهمة للغد على ورقة لاصقة أو في الملاحظات.',
        'إغلاق علامات تبويب المتصفح التي لم تعد لازمة.',
        'شكر زميل على شيء قام به مؤخرًا.',
        'أرشفة خمس رسائل قديمة لم تعد لازمة.',
        'إعادة تسمية ملف واحد غير مرتب لتسهيل العثور عليه لاحقًا.',
        'إزالة ملف أو ملفين متناثرين من سطح المكتب.',
        'حذف تذكير قديم لم يعد له داعٍ.',
        'إضافة عنوان واضح لمستند يُفتح كثيرًا.',
        'شطب بند صغير من قائمة المهام.',
        'إلغاء الاشتراك في نشرة بريدية لا تُقرأ أبدًا.',
        'مسح لوحة المفاتيح أو الشاشة بقطعة قماش ناعمة.',
        'وضع قلم ودفتر وماء في متناول اليد.',
        'كتابة ملاحظة قصيرة للغد عن النقطة التي توقف عندها العمل اليوم.',
        'اختيار أهم مهمة بعد الظهر والبدء بها أولًا.',
        'إفراغ سلة المهملات أو إعادة التدوير بجانب المكتب.',
        'تحديث ملاحظة تقدّم واحدة ليعرف الآخرون أين وصلت الأمور.',
        'ترتيب مجلد التنزيلات بنقل حفنة من الملفات.',
        'ضبط تذكير لشيء يُنسى كثيرًا.',
        'إيقاف إشعار واحد لا حاجة حقيقية إليه.',
        'إضافة صفحة يتكرر البحث عنها إلى المفضلة.',
        'كتابة ملخص من سطرين لاجتماع ما دامت تفاصيله حاضرة.',
        'السؤال عمّا إذا كان يمكن تقصير اجتماع متكرر قليلًا.',
        'تحديد هدف واحد للساعة القادمة وكتابته.',
        'سؤال زميل عن يومه، والإصغاء حقًا.',
        'مشاركة رابط مفيد مع شخص قد يستمتع به.',
        'إلقاء التحية على شخص لم يسبق الحديث معه.',
        'إرسال كلمة شكر سريعة لشخص قدّم مساعدة مؤخرًا.',
        'تحية زميل بحرارة في بداية المكالمة التالية.',
        'سؤال زميل في الفريق عمّا ينتظره بشوق هذا الأسبوع.',
        'تهنئة شخص على إنجاز صغير لوحظ.',
        'دعوة زميل إلى دردشة قصيرة على شاي أو قهوة، أو في مكالمة.',
        'الثناء على زميل لشيء محدد أتقنه.',
        'السؤال عن اسم شخص يتكرر لقاؤه ولم يُعرف اسمه بعد.',
        'مشاركة نصيحة مفيدة مع زميل قد يحتاج إليها.',
        'طلب ترشيح أغنية أو مسلسل أو كتاب من أحدهم.',
        'الاطمئنان على زميل كان هادئًا مؤخرًا.',
        'عرض المساعدة في أمر صغير إذا بدا أحدهم مشغولًا.',
        'تحية الشخص التالي بحرارة.',
        'نقل كلمة طيبة سُمعت عن زميل إليه.',
        'سؤال زميل عمّا جعل أسبوعه أسهل.',
        'إرسال رسالة ودية إلى زميل عمل سابق.',
        'شكر من يحافظ على المساحات المشتركة منظمة.',
        'تعريف زميلين قد يسعدهما التعارف.',
        'سؤال زميل عن طريقة لتسهيل تسليم العمل إليه.',
        'مشاركة نكتة صغيرة لطيفة مع شخص قريب.',
        'إضافة قليل من الدفء إلى «من فضلك» و«شكرًا» التاليتين.',
        'سؤال زميل عمّا يحب فعله خارج العمل.',
        'الإصغاء الكامل للشخص التالي الذي يتحدث إليك، دون الانشغال بشيء آخر.',
    ),
    "done": (
        'جيد. انتهت هذه.',
        'رائع. إنهاء شيء ما شعور جميل.',
        'أحسنت. استراحة قصيرة قبل التالية.',
        'جيد. المهام الصغيرة المنجزة تتراكم.',
        'تم ذلك. يحق لك أن تفرح به.',
        'جيد. شُطبت هذه من قائمتك.',
    ),
    "text": {
        HELP:
            """يعرض hello-world تحية وفكرة وشيئًا بسيطًا للتجربة.

في السؤال الأخير: plan لكتابة خطة اليوم، و done عند إنجازها، و menu
(أو m) للخيارات. Enter يغلق البرنامج، وكذلك q و x و close من أي سؤال.
في سؤال الخطة، same يعيد خطة سابقة لم تكتمل. بعد done تظهر آخر 3
خطط مكتملة. الخيار 1 في القائمة يعرضها كلها، والخيار 7 يزيل واحدة،
والخيار 8 يخفي الفكرة والاقتراح. في القائمة، Enter للرجوع.
يمكن أيضًا تشغيل hello.cmd مع أحد هذه الخيارات:
  --plain         عرض التحية فقط
  --stats         عرض ما هو محفوظ على هذا الكمبيوتر
  --reset         حذف كل ما هو محفوظ (بعد السؤال)
  --remind on     الفتح مرة يوميًا عند تسجيل الدخول (off لإيقافه)
  --streak off    إخفاء رسالة الأيام المتتالية (on لإظهارها)
  --version       عرض الإصدار
  --check-content FILE
                  فحص ملف محتوى خاص بالمؤسسة
  --help          عرض هذا النص

رموز الخروج: 0 عند النجاح، و1 عند فشل أمر أو تعذّر الكتابة على
الشاشة، و2 لخيار غير معروف.

تبقى الملاحظات المحفوظة على هذا الكمبيوتر، في مجلد المستخدم. لا يُرسل
أي شيء إلى أي مكان. لكن موظفي تقنية المعلومات الذين يمكنهم قراءة ملفات
هذا الكمبيوتر قد يقرؤونها.""",
        MENU_HELP:
            """كلمات يمكن كتابتها في السؤال الأخير:
  done  تسجيل خطة اليوم كمكتملة، ثم طلب الخطة التالية
  plan  كتابة خطة اليوم أو تغييرها
  menu  فتح هذه الخيارات
  q     إغلاق النافذة، وكذلك Enter
في سؤال الخطة، same يعيد خطتك السابقة التي لم تكتمل.
عند سؤال "هل أنجزتها؟"، تعني n ليس بعد، ويمكن إبقاء الخطة
لليوم. q يغلق البرنامج من أي سؤال.
في هذه القائمة، 1 يعرض ما هو محفوظ، و7 يزيل خطة مكتملة،
و8 يخفي الفكرة والاقتراح.
يمكن كتابة m لسماع الخيارات مرة أخرى. لا يُرسل أي شيء إلى أي مكان.""",
        SAVED_PLAN:
            'تم الحفظ. يمكن كتابة done عند إنجازها، وإلا فسيأتي السؤال عنها في المرة القادمة.',
        GREETING:
            'مرحبًا بالعالم!',
        'hello.cmd is in this folder:':
            'يوجد hello.cmd في هذا المجلد:',
        'Shortened to {n} characters.':
            'عدد الأحرف بعد الاختصار: {n}.',
        'Your saved file was damaged, so hello-world set it aside as a backup copy and started fresh. Your earlier days and plan could not be read. Menu option 4 deletes the backup.':
            'كان الملف المحفوظ تالفًا، لذا نقله hello-world جانبًا كنسخة احتياطية وبدأ من جديد. تعذّرت قراءة أيامك وخطتك السابقة. الخيار 4 في القائمة يحذف النسخة الاحتياطية.',
        'Backup copy: ':
            'النسخة الاحتياطية: ',
        'In the folder: ':
            'في المجلد: ',
        'Sorry, "{shown}" is not one of the choices.':
            'عذرًا، "{shown}" ليس من الخيارات المتاحة.',
        'A plan needs a word or two, so nothing was saved.':
            'تحتاج الخطة إلى كلمة أو كلمتين، لذا لم يُحفظ شيء.',
        'The sign-in reminder works on Windows only.':
            'تذكير تسجيل الدخول يعمل على Windows فقط.',
        'Your organization has turned off opening at sign-in.':
            'أوقفت مؤسستك الفتح عند تسجيل الدخول.',
        'The reminder cannot be set up from this folder.':
            'لا يمكن إعداد التذكير من هذا المجلد.',
        'Could not set up the reminder.':
            'تعذّر إعداد التذكير.',
        'Done. hello-world will open once a day when you sign in.':
            'تم. سيُفتح hello-world مرة واحدة يوميًا عند تسجيل الدخول.',
        'To stop it, choose option 2 in the menu.':
            'يمكن إيقافه من الخيار 2 في القائمة.',
        'Could not turn off the sign-in reminder.':
            'تعذّر إيقاف تذكير تسجيل الدخول.',
        'Done. The sign-in reminder is off.':
            'تم. تذكير تسجيل الدخول متوقف.',
        'Saved on this computer in:':
            'محفوظ على هذا الكمبيوتر في:',
        'Saved in your own user folder on this computer.':
            'محفوظ في مجلد المستخدم الخاص بك على هذا الكمبيوتر.',
        'Days you opened it in the last {days} days: {n} (last 7 days: {recent})':
            'أيام الفتح خلال آخر {days} يومًا: {n} (آخر 7 أيام: {recent})',
        'Times you marked a plan done: {n}':
            'عدد مرات تسجيل خطة كمكتملة: {n}',
        'Your current plan: ':
            'خطتك الحالية: ',
        'Earlier plan (for same): ':
            'الخطة السابقة (متاحة عبر same): ',
        'Days-in-a-row message: shown.':
            'رسالة الأيام المتتالية: ظاهرة.',
        'Days-in-a-row message: hidden.':
            'رسالة الأيام المتتالية: مخفية.',
        'Opens by itself at sign-in: turned off by your organization.':
            'الفتح تلقائيًا عند تسجيل الدخول: أوقفته مؤسستك.',
        'Opens by itself at sign-in: on.':
            'الفتح تلقائيًا عند تسجيل الدخول: مُفعّل.',
        'Opens by itself at sign-in: off.':
            'الفتح تلقائيًا عند تسجيل الدخول: متوقف.',
        "It never leaves this computer. Others who can read this computer's files, such as IT staff, could read it.":
            'لا يغادر هذا الكمبيوتر أبدًا. لكن من يمكنه قراءة ملفات هذا الكمبيوتر، مثل موظفي تقنية المعلومات، قد يقرؤه.',
        'After tidying, the file holds only this:':
            'بعد الترتيب، لا يحتوي الملف إلا على هذا:',
        'Delete all saved notes, dates and plans on this computer? (y or n, Enter to cancel) > ':
            'حذف كل الملاحظات والتواريخ والخطط المحفوظة على هذا الكمبيوتر؟ (y أو n، أو Enter للإلغاء) > ',
        'Nothing was deleted.':
            'لم يُحذف شيء.',
        'Could not delete everything.':
            'تعذّر حذف كل شيء.',
        'Delete these yourself:':
            'يلزم حذف هذه يدويًا:',
        'Could not list the folder, so backup copies may remain:':
            'تعذّر عرض محتويات المجلد، لذا قد تبقى نسخ احتياطية:',
        'Done. Everything saved was deleted.':
            'تم. حُذف كل ما كان محفوظًا.',
        'Another open hello-world window cannot put it back.':
            'لن تتمكن نافذة hello-world أخرى مفتوحة من إعادته.',
        'Close any other open hello-world window, or it may save its notes again.':
            'يُرجى إغلاق أي نافذة hello-world أخرى مفتوحة، وإلا فقد تحفظ ملاحظاتها من جديد.',
        'Everything saved was deleted in another window, so this was not saved.':
            'حُذف كل ما كان محفوظًا من نافذة أخرى، لذا لم يُحفظ هذا.',
        'The other open window had also finished a plan.':
            'النافذة الأخرى المفتوحة أنهت خطة هي أيضًا.',
        'The other open window changed the plan, so its plan is kept.':
            'النافذة الأخرى المفتوحة غيّرت الخطة، لذا أُبقي على خطتها.',
        'Type plan at the last prompt to set one.':
            'لوضع خطة، يمكن كتابة plan في السؤال الأخير.',
        'That looks like a command, not a plan, so nothing was saved.':
            'يبدو هذا أمرًا وليس خطة، لذا لم يُحفظ شيء.',
        'Type your plan, or press Enter to go back.':
            'يمكن كتابة الخطة، أو الضغط على Enter للرجوع.',
        'Finished lately:':
            'ما اكتمل مؤخرًا:',
        'Your plan today: ':
            'خطتك اليوم: ',
        'Your plan from {date}: ':
            'خطتك بتاريخ {date}: ',
        'Earlier plan: ':
            'الخطة السابقة: ',
        'Type the next plan, or Enter to close > ':
            'الخطة التالية، أو Enter للإغلاق > ',
        'Type the next plan, same to reuse the earlier plan, or Enter to close > ':
            'الخطة التالية، أو same لإعادة الخطة السابقة، أو Enter للإغلاق > ',
        "Type today's plan, or Enter to keep it > ":
            'خطة اليوم، أو Enter لإبقائها > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
            'خطة اليوم، أو same لإعادة الخطة السابقة، أو Enter لإبقائها > ',
        "Type today's plan, or Enter to go back > ":
            'خطة اليوم، أو Enter للرجوع > ',
        "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
            'خطة اليوم، أو same لإعادة الخطة السابقة، أو Enter للرجوع > ',
        'Closing.':
            'جارٍ الإغلاق.',
        'There is no earlier plan to reuse yet. Nothing changed.':
            'لا توجد خطة سابقة لإعادتها بعد. لم يتغير شيء.',
        'Nothing changed.':
            'لم يتغير شيء.',
        'Could not save that on this computer. Your plan is unchanged.':
            'تعذّر الحفظ على هذا الكمبيوتر. خطتك لم تتغير.',
        'No finished plans are saved.':
            'لا توجد خطط مكتملة محفوظة.',
        'Type the number to forget (1 to {n}), or Enter to keep them all > ':
            'رقم الخطة المراد إزالتها (من 1 إلى {n})، أو Enter لإبقائها كلها > ',
        'There is no number "{typed}" on the list. Type a number from 1 to {n}, or press Enter to keep them all.':
            'لا يوجد رقم "{typed}" في القائمة. يُرجى كتابة رقم من 1 إلى {n}، أو الضغط على Enter لإبقائها كلها.',
        'Also forget it as the earlier plan for same? (y or n, Enter to keep it for same) > ':
            'هل تُزال أيضًا من same؟ (y أو n، أو Enter لإبقائها في same) > ',
        'Type y or n, or press Enter to keep it for same.':
            'يُرجى كتابة y أو n، أو الضغط على Enter لإبقائها في same.',
        'That plan was already forgotten. Nothing changed.':
            'هذه الخطة أُزيلت من قبل. لم يتغير شيء.',
        'Forgotten: ':
            'أُزيلت: ',
        'Same still has it.':
            'لا تزال متاحة عبر same.',
        'Could not save that on this computer. Nothing changed.':
            'تعذّر الحفظ على هذا الكمبيوتر. لم يتغير شيء.',
        'Options':
            'الخيارات',
        'Show what is saved on this computer':
            'عرض ما هو محفوظ على هذا الكمبيوتر',
        'Open once a day at sign-in (turned off by your organization)':
            'الفتح مرة يوميًا عند تسجيل الدخول (أوقفته مؤسستك)',
        'Turn off: open once a day at sign-in (now on)':
            'إيقاف: الفتح مرة يوميًا عند تسجيل الدخول (مُفعّل الآن)',
        'Turn on: open once a day at sign-in (now off)':
            'تفعيل: الفتح مرة يوميًا عند تسجيل الدخول (متوقف الآن)',
        'Days-in-a-row message (hidden by your organization)':
            'رسالة الأيام المتتالية (أخفتها مؤسستك)',
        'Hide the days-in-a-row message (now shown)':
            'إخفاء رسالة الأيام المتتالية (ظاهرة الآن)',
        'Show the days-in-a-row message (now hidden)':
            'إظهار رسالة الأيام المتتالية (مخفية الآن)',
        'Delete everything saved':
            'حذف كل ما هو محفوظ',
        'Help':
            'تعليمات',
        "Set today's plan (turned off by your organization)":
            'وضع خطة اليوم (أوقفته مؤسستك)',
        'Forget a finished plan (turned off by your organization)':
            'إزالة خطة مكتملة (أوقفتها مؤسستك)',
        "Set or change today's plan":
            'وضع خطة اليوم أو تغييرها',
        'Forget one finished plan':
            'إزالة خطة مكتملة',
        'Thought and tip (hidden by your organization)':
            'الفكرة والاقتراح (أخفتهما مؤسستك)',
        'Hide the thought and tip (now shown)':
            'إخفاء الفكرة والاقتراح (ظاهران الآن)',
        'Show the thought and tip (now hidden)':
            'إظهار الفكرة والاقتراح (مخفيان الآن)',
        '{date}: ':
            '{date}: ',
        'Enter':
            'Enter',
        'Back to the last prompt':
            'الرجوع إلى السؤال الأخير',
        'Choose 1 to 11, or Enter to go back > ':
            'رقم من 1 إلى 11، أو Enter للرجوع > ',
        'Choose 1 to 11, m to list the options, or Enter to go back > ':
            'رقم من 1 إلى 11، أو m لعرض الخيارات، أو Enter للرجوع > ',
        'The saved file could not be read just now, so this may be out of date.':
            'تعذّرت قراءة الملف المحفوظ الآن، لذا قد لا تكون هذه المعلومات محدّثة.',
        'Type full to see the whole file, or Enter to go on > ':
            'full لعرض الملف كاملًا، أو Enter للمتابعة > ',
        'Could not save that choice on this computer.':
            'تعذّر حفظ هذا الاختيار على هذا الكمبيوتر.',
        'Your organization has hidden the days-in-a-row message.':
            'أخفت مؤسستك رسالة الأيام المتتالية.',
        'Done. The days-in-a-row message is on.':
            'تم. رسالة الأيام المتتالية مُفعّلة.',
        'Done. The days-in-a-row message is off.':
            'تم. رسالة الأيام المتتالية متوقفة.',
        'Plans are turned off by your organization.':
            'أوقفت مؤسستك الخطط.',
        'Your organization has hidden the thought and tip.':
            'أخفت مؤسستك الفكرة والاقتراح.',
        'Done. The thought and tip are on.':
            'تم. الفكرة والاقتراح مُفعّلان.',
        'Done. The thought and tip are off.':
            'تم. الفكرة والاقتراح متوقفان.',
        'Type 1 to 11, or press Enter to go back.':
            'يُرجى كتابة رقم من 1 إلى 11، أو الضغط على Enter للرجوع.',
        'Want it to open once a day when you sign in? (y or n, Enter for not now) > ':
            'هل يُفتح البرنامج مرة يوميًا عند تسجيل الدخول؟ (y أو n، أو Enter لتأجيل ذلك) > ',
        'Want it to open once a day when you sign in so it can ask about your plan? (y or n, Enter for not now) > ':
            'هل يُفتح البرنامج مرة يوميًا عند تسجيل الدخول ليسألك عن خطتك؟ (y أو n، أو Enter لتأجيل ذلك) > ',
        'Type y or n, or press Enter for not now.':
            'يُرجى كتابة y أو n، أو الضغط على Enter لتأجيل ذلك.',
        'That was not understood. It will ask again on a later visit.':
            'لم يُفهم الرد. سيأتي السؤال مرة أخرى في زيارة لاحقة.',
        'It will ask again on a later visit. Menu option 2 also turns it on.':
            'سيأتي السؤال مرة أخرى في زيارة لاحقة. ويمكن تفعيله أيضًا من الخيار 2 في القائمة.',
        'No problem. Menu option 2 turns it on later.':
            'لا مشكلة. يمكن تفعيله لاحقًا من الخيار 2 في القائمة.',
        "Okay. It won't ask again. Menu option 2 turns it on.":
            'حسنًا. لن يتكرر السؤال. يمكن تفعيله من الخيار 2 في القائمة.',
        'Okay. It will ask again on a later visit. Type n to stop it.':
            'حسنًا. سيأتي السؤال مرة أخرى في زيارة لاحقة. ولإيقاف السؤال نهائيًا، يمكن كتابة n.',
        'When did you finish it?':
            'متى أنجزتها؟',
        'Today':
            'اليوم',
        'Type a number from 1 to {n}, or Enter for 1 > ':
            'رقم من 1 إلى {n}، أو Enter لاختيار 1 > ',
        'Type a number from 1 to {n}, or press Enter.':
            'يُرجى كتابة رقم من 1 إلى {n}، أو الضغط على Enter.',
        'That looks like more than one thing. Finishing the first part still counts.':
            'يبدو أن هذه أكثر من مهمة واحدة. إنجاز الجزء الأول وحده يُحتسب.',
        'There is no plan to mark as done. Type plan to set one.':
            'لا توجد خطة لتسجيلها كمكتملة. يمكن كتابة plan لوضع خطة.',
        'Could not save that on this computer. The plan is still open.':
            'تعذّر الحفظ على هذا الكمبيوتر. الخطة لا تزال معلّقة.',
        'Your plan from over two weeks ago was put away. Type same at the plan prompt to bring it back.':
            'خطتك التي مضى عليها أكثر من أسبوعين وُضعت جانبًا. لاستعادتها، يمكن كتابة same في سؤال الخطة.',
        "Press Enter at each question to skip it, and once more to close. That's it.":
            'الضغط على Enter عند أي سؤال يتخطاه، وضغطة أخرى تغلق البرنامج. هذا كل شيء.',
        'Welcome.':
            'مرحبًا بك.',
        'Each day you get one thought and one small thing to try, the same for everyone.':
            'كل يوم فكرة وشيء بسيط للتجربة، والجميع يرون الشيء نفسه.',
        'If you type a plan, it asks next time how it went. Your notes stay on this computer and are never sent anywhere. Like any work file they are not secret, so keep them to everyday tasks.':
            'إذا كتبت خطة، فسيسألك في المرة القادمة كيف سارت. تبقى ملاحظاتك على هذا الكمبيوتر ولا تُرسل إلى أي مكان. لكنها، مثل أي ملف عمل، ليست سرية، لذا يُفضّل أن تقتصر على المهام اليومية.',
        'Type menu at the end for the options.':
            'يمكن كتابة menu في النهاية لعرض الخيارات.',
        'Welcome back. Glad you are here.':
            'أهلًا بعودتك. يسعدنا وجودك هنا.',
        'You have opened this {row} days in a row. Nice to see you.':
            'هذا يومك الـ{row} على التوالي. يسعدنا أن نراك.',
        'Last time you planned: ':
            'خطتك في المرة الماضية: ',
        'Did you do it? (y for yes, n for not yet, Enter to skip) > ':
            'هل أنجزتها؟ (y نعم، n ليس بعد، Enter للتخطي) > ',
        'Type y or n, or press Enter to skip.':
            'يُرجى كتابة y أو n، أو الضغط على Enter للتخطي.',
        'Could not save that on this computer. Your answer was not counted.':
            'تعذّر الحفظ على هذا الكمبيوتر. لم تُحتسب إجابتك.',
        'That is fine. Keep it for today? (y or n, Enter to keep it) > ':
            'لا بأس. هل تبقى لليوم؟ (y أو n، أو Enter لإبقائها) > ',
        'Type y to keep it, n to clear it, or press Enter to keep it.':
            'يُرجى كتابة y لإبقائها، أو n لإزالتها، أو الضغط على Enter لإبقائها.',
        'Cleared. Type same at a plan prompt if you want it back.':
            'أُزيلت. لاستعادتها، يمكن كتابة same في سؤال الخطة.',
        'Kept for today.':
            'ستبقى لليوم.',
        'That was not understood. Your plan is left as it was.':
            'لم يُفهم الرد. بقيت خطتك كما هي.',
        'Your plan is still open.':
            'خطتك لا تزال معلّقة.',
        'Thought for today:':
            'فكرة اليوم:',
        'Try this today:':
            'للتجربة اليوم:',
        'Your plan for today: ':
            'خطتك لليوم: ',
        'Still open since {date}:':
            'معلّقة منذ {date}:',
        '(Enter to skip)':
            '(Enter للتخطي)',
        '(A plan typed here replaces the old one. Enter to skip)':
            '(أي خطة تُكتب هنا تحل محل القديمة. Enter للتخطي)',
        '(Type same to reuse it, or Enter to skip)':
            '(same لإعادة استخدامها، أو Enter للتخطي)',
        'What is one thing you want to get done today?':
            'ما الشيء الواحد الذي يستحق الإنجاز اليوم؟',
        'There is no earlier plan to reuse yet. Nothing was saved.':
            'لا توجد خطة سابقة لإعادتها بعد. لم يُحفظ شيء.',
        'Your notes could not be saved on this computer. This screen still works.':
            'تعذّر حفظ ملاحظاتك على هذا الكمبيوتر. لكن هذه الشاشة لا تزال تعمل.',
        'Type menu, or Enter to close > ':
            'menu، أو Enter للإغلاق > ',
        'Type done, plan or menu, or Enter to close > ':
            'done أو plan أو menu، أو Enter للإغلاق > ',
        'Type plan or menu, or Enter to close > ':
            'plan أو menu، أو Enter للإغلاق > ',
        'Type done, plan or menu, or press Enter to close.':
            'يُرجى كتابة done أو plan أو menu، أو الضغط على Enter للإغلاق.',
        'Type plan or menu, or press Enter to close.':
            'يُرجى كتابة plan أو menu، أو الضغط على Enter للإغلاق.',
        "The saved file can't be read right now, or it is damaged.":
            'تتعذّر قراءة الملف المحفوظ الآن، أو أنه تالف.',
        'Nothing was changed. Saved in: ':
            'لم يتغير شيء. محفوظ في: ',
        'Deleting saved notes needs a person at the keyboard.':
            'يتطلب حذف الملاحظات المحفوظة وجود شخص أمام لوحة المفاتيح.',
        '{option} needs on or off. Here are the options.':
            '{option} يحتاج إلى on أو off. هذه هي الخيارات.',
        'Unknown option: {option}. Here are the options.':
            'خيار غير معروف: {option}. هذه هي الخيارات.',
        '&Done':
            'تم(&D)',
        '&Not yet':
            'ليس بعد(&N)',
        'S&kip':
            'تخطي(&K)',
        '&Save':
            'حفظ(&S)',
        '&I did it':
            'أنجزتها(&I)',
        '&Options':
            'الخيارات(&O)',
        'Close':
            'إغلاق',
        'Not today':
            'ليس اليوم',
        'Did you do it?':
            'هل أنجزتها؟',
        'Done. A reminder comes when you sign in, if there is a plan to ask about.':
            'تم. سيظهر تذكير عند تسجيل الدخول إذا كانت هناك خطة للسؤال عنها.',
        'Done. The Start menu opens a window with buttons.':
            'تم. قائمة ابدأ تفتح الآن نافذة بأزرار.',
        'Done. The Start menu opens this text screen.':
            'تم. قائمة ابدأ تفتح الآن هذه الشاشة النصية.',
        'More options':
            'خيارات إضافية',
        'Remind me when I sign in':
            'تذكيري عند تسجيل الدخول',
        'Show the thought and tip':
            'إظهار الفكرة والاقتراح',
        'Type your plan in the box.':
            'يمكن كتابة خطتك في المربع.',
        'Use a window with buttons (now this text screen)':
            'استخدام نافذة بأزرار (حاليًا هذه الشاشة النصية)',
        'Use the text screen':
            'استخدام الشاشة النصية',
        'Use this text screen (now a window with buttons)':
            'استخدام هذه الشاشة النصية (حاليًا نافذة بأزرار)',
        'Want a reminder when you sign in? It shows your plan from last time, and you answer with one click. You can turn it off under Options.':
            'ما رأيك بتذكير عند تسجيل الدخول؟ يعرض خطتك من المرة الماضية، ويكفي للرد نقرة واحدة. ويمكن إيقافه من الخيارات.',
        'Window or text screen (set by your organization)':
            'نافذة أو شاشة نصية (تحددها مؤسستك)',
        'Your organization has set hello-world to open as a text screen.':
            'ضبطت مؤسستك hello-world ليُفتح كشاشة نصية.',
        'Saved.':
            'تم الحفظ.',
        'Save your plan before closing?':
            'حفظ خطتك قبل الإغلاق؟',
        'Delete all saved notes, dates and plans on this computer?':
            'حذف كل الملاحظات والتواريخ والخطط المحفوظة على هذا الكمبيوتر؟',
        'Turn off: reminder when you sign in (now on)':
            'إيقاف: التذكير عند تسجيل الدخول (مُفعّل الآن)',
        'Turn on: reminder when you sign in (now off)':
            'تفعيل: التذكير عند تسجيل الدخول (متوقف الآن)',
        'Reminder when you sign in (turned off by your organization)':
            'التذكير عند تسجيل الدخول (أوقفته مؤسستك)',
        'Reminder when you sign in: on.':
            'التذكير عند تسجيل الدخول: مُفعّل.',
        'Reminder when you sign in: off.':
            'التذكير عند تسجيل الدخول: متوقف.',
        'Reminder when you sign in: turned off by your organization.':
            'التذكير عند تسجيل الدخول: أوقفته مؤسستك.',
        'Show the days-in-a-row message':
            'إظهار رسالة الأيام المتتالية',
        'Done. The thought and tip show next time you open hello-world.':
            'تم. ستظهر الفكرة والاقتراح في المرة القادمة التي يُفتح فيها hello-world.',
        "Clear today's plan?":
            'مسح خطة اليوم؟',
        'Next plan, if you want one:':
            'الخطة التالية، إن أردت:',
        'A few things? Put ; between them.':
            'أكثر من مهمة؟ يُفصل بينها بالرمز ;',
        'A plan can be up to {n} characters.':
            'عدد أحرف الخطة لا يتجاوز {n}.',
        'Did you do them? (y for all, n for not yet, numbers for the ones you did, Enter to skip) > ':
            'هل أنجزتها؟ (y للكل، n ليس بعد، أو أرقام ما أُنجز، Enter للتخطي) > ',
        'Last time you planned:':
            'خطتك في المرة الماضية:',
        'The rest is kept for today.':
            'وتبقى البقية لليوم.',
        'Tick the ones you did, then click Done. With none ticked, Done means all of them.':
            'تحديد ما أُنجز ثم النقر على «تم». ومن دون تحديد، تعني «تم» الكل.',
        'Type y for all, n for not yet, or the numbers you did, such as 1 3. Enter skips.':
            'يُرجى كتابة y للكل، أو n لـ«ليس بعد»، أو أرقام ما أُنجز، مثل 1 3. Enter للتخطي.',
        'Your settings were kept.':
            'تم الإبقاء على إعداداتك.',
        'Language (set by your organization)':
            'اللغة (تحددها مؤسستك)',
        'Language (now {name})':
            'اللغة (حاليًا {name})',
        'following Windows':
            'حسب Windows',
        'Your organization shows hello-world in English.':
            'تعرض مؤسستك hello-world باللغة الإنجليزية.',
        'Follow Windows':
            'حسب Windows',
        'Type a number from 1 to {n}, or Enter to keep it > ':
            'رقم من 1 إلى {n}، أو Enter لإبقائها > ',
        'Done. The new language shows next time you open hello-world.':
            'تم. ستظهر اللغة الجديدة في المرة القادمة التي يُفتح فيها hello-world.',
        'Language...':
            'اللغة...',
        'Hello, {name}!':
            'مرحبًا يا {name}!',
        'One thing to get done today? Open hello-world to plan it.':
            'مهمة واحدة لإنجازها اليوم؟ يمكن التخطيط لها في hello-world.',
        '&Open':
            'فتح(&O)',
        'Reminder settings...':
            'إعدادات التذكير...',
        'Greet me by name':
            'مناداتي باسمي في التحية',
        'At sign-in':
            'عند تسجيل الدخول',
        'At {at}':
            'في الساعة {at}',
        'Also on days with no plan':
            'في الأيام التي بلا خطة أيضًا',
        'Open hello-world after I answer':
            'فتح hello-world بعد الرد',
        'Not on weekends':
            'باستثناء عطلة نهاية الأسبوع',
        'Done. A reminder comes at {at} each day, if there is a plan to ask about.':
            'تم. سيصل تذكير يوميًا في الساعة {at} إذا كانت هناك خطة للسؤال عنها.',
        'Send feedback...':
            'إرسال ملاحظات...',
        '"holidays" must be a list of at most {n} dates.':
            '"holidays" يجب أن تكون قائمة لا يتجاوز عدد تواريخها {n}.',
        '"title" must be 1 to 40 characters of plain text, with no link or address.':
            '"title" يجب أن يكون نصًا عاديًا من 1 إلى 40 حرفًا، بلا روابط أو عناوين.',
        '"{list}" must be a list of {low} to {high} lines.':
            '"{list}" يجب أن تكون قائمة يتراوح عدد أسطرها بين {low} و{high}.',
        "Can't read {path}: {error}":
            'تتعذّر قراءة {path}: {error}',
        'Could not save that on this computer.':
            'تعذّر الحفظ على هذا الكمبيوتر.',
        'Days you opened hello-world: {n}':
            'عدد أيام فتح hello-world: {n}',
        'Keep a longer history':
            'الاحتفاظ بسجل أطول',
        'Keep my numbers':
            'الاحتفاظ بأرقامي',
        'Longest run of days: {n}':
            'أطول سلسلة أيام متتالية: {n}',
        "Mark today's plan done":
            'تسجيل خطة اليوم كمكتملة',
        "Mark today's plan done (plans are turned off)":
            'تسجيل خطة اليوم كمكتملة (الخطط متوقفة)',
        'My numbers are off. Turn them on under Options, or with --set numbers on.':
            'أرقامي متوقفة. يمكن تفعيلها من الخيارات، أو باستخدام --set numbers on.',
        'My numbers...':
            'أرقامي...',
        'Nothing finished yet this week. That is fine.':
            'لم يكتمل شيء بعد هذا الأسبوع. لا بأس.',
        'OK: {thoughts} thoughts and {tips} tips.':
            'صالح: الأفكار {thoughts}، والاقتراحات {tips}.',
        'Plans finished: {n}':
            'الخطط المكتملة: {n}',
        'Save my plans to a file':
            'حفظ خططي في ملف',
        'Saved to {path}':
            'تم الحفظ في {path}',
        "The file isn't valid JSON, or is over 200,000 characters.":
            'الملف ليس JSON صالحًا، أو يتجاوز 200,000 حرف.',
        'The file must hold an object with two lists, "thoughts" and "tips", and may add "holidays" and "title".':
            'يجب أن يحتوي الملف على كائن فيه قائمتان، "thoughts" و"tips"، ويمكن أن يضيف "holidays" و"title".',
        'This week you finished {n}:':
            'ما أنجزته هذا الأسبوع ({n}):',
        'This week...':
            'هذا الأسبوع...',
        'holidays line {line} is not a date like 2026-12-25.':
            'السطر {line} في holidays ليس تاريخًا مثل 2026-12-25.',
        '{list} line {line} has a date.':
            'السطر {line} في {list} يحتوي على تاريخ.',
        '{list} line {line} has a link or an address.':
            'السطر {line} في {list} يحتوي على رابط أو عنوان.',
        '{list} line {line} has control characters or extra spaces.':
            'السطر {line} في {list} يحتوي على أحرف تحكم أو مسافات زائدة.',
        '{list} line {line} is not text.':
            'السطر {line} في {list} ليس نصًا.',
        '{list} line {line} must be {low} to {high} characters long.':
            'السطر {line} في {list} يجب أن يتراوح عدد أحرفه بين {low} و{high}.',
    },
}

if __name__ == "__main__":
    sys.exit(main())
