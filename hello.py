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
import base64
import collections
import contextlib
import copy
import csv
import datetime
import io
import json
import os
import re
import shutil
import sys
import textwrap
import unicodedata
import time

# "dmy" or "mdy" for 30/10 against 10/30; None asks Windows.
DATE_ORDER = None

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        "Sunday")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
GREETING = "Hello, world!"

# Chosen by date, so everyone sees the same line on the same day and the
# lists repeat every 100 days (the pairing much later).
TIPS = (
    'Sip a glass of water slowly, away from your screen.',
    'Raise your screen so its top edge is at eye level, with a book under it if needed.',
    'Rest your eyes for twenty seconds: look far away, or close them.',
    'Stretch your arms overhead, seated or standing, and take a deep breath.',
    'Move to the farthest room or window you can reach, and back.',
    'Check your posture and let your shoulders drop away from your ears.',
    'Turn your neck gently side to side, only as far as feels easy.',
    'Open and close your hands ten times to loosen your fingers.',
    'Pin the one document you open most so it is one click away.',
    'Take a short walk or roll outside, whatever suits you.',
    'Pour a warm or cool drink and enjoy it away from your screen.',
    'Turn your screen brightness down a step if it is brighter than the room.',
    'Write the next step on one task you left half done.',
    'Plant both feet flat and sit tall, or stand tall, for ten breaths.',
    'Mute one group chat you only ever skim.',
    'Unclench your jaw and relax your forehead for a moment.',
    'Take your next phone call standing up or away from your desk, if you can.',
    'Block fifteen minutes in your calendar for the task you keep putting off.',
    'Adjust your chair, screen or keyboard so one thing sits more comfortably.',
    'Take the long way to your next meeting or call, if you can.',
    'Save a template for one email you write again and again.',
    'Learn one keyboard shortcut for the program you use most.',
    'Drink a full glass of water before your next coffee or tea.',
    'Set a timer for fifty minutes, and when it rings, stand up or stretch before you start it again.',
    'Step outside or open a window for a minute of fresh air.',
    'Take five slow breaths, making each exhale a little longer.',
    'Pause for one quiet minute before you open your next message.',
    'Note one good thing that has happened so far today.',
    'Close your eyes for three breaths and notice how you feel.',
    'Name three things you notice right now, with any sense.',
    'Write down one thing you are looking forward to this week.',
    'Set a timer for two minutes and simply sit with no screen.',
    'Put one thing you like, such as a photo or a plant, where you can see it from your chair.',
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
    'Before you leave, write down one thing that went better than you expected today.',
    'Write the three things you will do this afternoon, in the order you will do them.',
    'Let your mind rest for sixty seconds, then go back to your next task.',
    'Notice your feet on the floor and feel steady for a moment.',
    'Write down one thing you learned this week, so you can find it again.',
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
    'Join your next call a minute early and say hello to whoever is already there.',
    'Ask a teammate what they are looking forward to this week.',
    'Congratulate someone on a small win you noticed.',
    'Invite a colleague for a short chat over tea, coffee, or a call.',
    'Compliment a colleague on something specific they did well.',
    'Learn the name of someone you see often but do not know yet.',
    'Share a helpful tip with a teammate who may need it.',
    'Ask someone to recommend a song, show, or book.',
    'Check in with a colleague who has been quiet lately.',
    'Offer to help with one small thing if someone seems busy.',
    'After a meeting that went well, post a one-line thank-you in its chat.',
    'When someone praises a colleague to you, pass it on to that colleague.',
    'Ask a coworker what made their week easier.',
    'Send a friendly message to someone you used to work with.',
    'Thank someone who keeps shared spaces running smoothly.',
    'Introduce two colleagues who might enjoy meeting each other.',
    'Ask a teammate how you can make a handoff easier for them.',
    'Save a seat for someone at the next meeting or lunch.',
    'In your next request, say why you need it and by when.',
    'Ask a colleague what they enjoy doing outside of work.',
    'Listen fully to the next person who speaks to you, without multitasking.',
)

# For warehouses, factories and shift work, chosen with "floor_tips".
TIPS_FLOOR = (
    'Check that your walkway is clear before the first job of the shift.',
    'Drink a full bottle of water before your first break.',
    'Lift with your legs and keep the load close, even for small boxes.',
    'Stretch your calves for thirty seconds while you wait for the next job.',
    'Say good morning to the person at the next station.',
    'Tell the next shift one thing they should know.',
    'Wipe down the screen or scanner you use most.',
    'Swap hands or sides on a repeated task for a few minutes.',
    'Take your full break, away from the floor if you can.',
    'Point out one small hazard to the person who can fix it.',
    'Check that your gloves, boots or vest are still in good shape.',
    'Between loads, set everything down and stand straight for one breath.',
    'Thank someone who helped you catch up today.',
    'Look at something far away for twenty seconds between close-up tasks.',
    'Put one tool back where the next person will look for it.',
    'Ask a newer teammate how their week is going.',
    'Eat something before you get too hungry to think about it.',
    'Walk the long way to your break and loosen up.',
    'Note one thing that slowed you down today and mention it at the handover.',
    'Stand tall for a moment and take three slow breaths.',
    'Check that your phone or radio is charged for the rest of the shift.',
    'Give someone a hand with a heavy or awkward job.',
    'Rest your eyes in a quiet, dim spot for a minute.',
    'Learn the name of someone from another team you see every day.',
    'Plan your break for a moment when things are quiet.',
    'Keep your water where you can reach it without leaving your spot.',
    'Clear one thing off a shared bench or table.',
    'Shake out your hands and wrists between scans.',
    'Tell your lead about a near miss, so it stays a near miss.',
    'Pick one task to finish properly before the end of the shift.',
    'Hold the door or gate for the next person carrying something.',
    'Shift your footing or posture every so often when you stand a long time.',
    'Write down one number or detail you keep forgetting.',
    'Check the time once, then let the clock be for a while.',
    'Share a quick tip that makes a job easier for the rest of the crew.',
    'Step outside for fresh air on your break if you can.',
    'Take a sip of water each time you finish a job.',
    'Leave your station a little tidier than you found it.',
    'Thank the person who hands over to you.',
    'On the way home, think of one thing that went well on the shift.',
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
    'Stuck for more than twenty minutes? Write down the question and ask someone.',
    'You are allowed to still be learning something you have done for years.',
    'If the morning went nowhere, pick one task after lunch and start it before you check messages.',
    'If you are tired, move the hardest task to tomorrow morning and do an easy one now.',
    'When you catch a mistake of yours, fix it, note what caused it, and move on.',
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
    'Before you ask a busy colleague for something, check whether the answer is already written down.',
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
8 hides the thought and tip, and 12 has the reminder times and the
other settings.
Type m to see the options again. Nothing is sent anywhere."""


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
    """The organization's content for the person's language: content.<code>.json,
    then the base language's for a regional one, then content.json. A file
    that breaks the rules is ignored whole, and the next one is tried."""
    folder = os.path.dirname(os.path.abspath(__file__))
    code = language()
    names = [f"content.{code}.json", f"content.{code.split('-')[0]}.json", "content.json"]
    for path in [CONTENT] if CONTENT else [os.path.join(folder, n) for n in dict.fromkeys(names)]:
        try:
            with open(path, encoding="utf-8-sig") as f:
                data = json.loads(f.read(200_000))
        except (OSError, ValueError, RecursionError):
            continue
        if not content_problems(data):
            return data
    return None


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
    thoughts = data["thoughts"] if data else THOUGHTS
    if FLOOR_TIPS or policy("FloorTips"):
        return thoughts, data.get("tips_floor", TIPS_FLOOR) if data else TIPS_FLOOR
    return thoughts, data["tips"] if data else TIPS


def help_text():
    here = os.path.dirname(os.path.abspath(__file__))
    return tr(HELP) + "\n\n" + tr("hello.cmd is in this folder:") + "\n  " + here

VERSION = "1.46.0"
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
TIP_WORDS = ("tip", "consejo", "astuce", "dica", "tipp")
HANDOFF_WORDS = ("handoff", "relevo", "relève", "passagem", "übergabe", "ubergabe")
CLEAR_WORDS = ("clear", "borrar", "effacer", "limpar", "löschen", "loschen")
HELP_WORDS = ("h", "help", "?", "ayuda", "aide", "ajuda", "hilfe")
LIST_WORDS = ("list", "lista", "liste")
FULL_WORDS = ("full", "todo", "tout", "tudo", "alles")

# The tests set these after importing the module, to run against a fixed date,
# a temporary folder, and typed input. Nothing outside the program sets them.
# Tests that check the done count set this rather than turn on My numbers.
COUNT_ALWAYS = False
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
# How the notes file is locked: "plain" or "test" in tests; None locks it to
# the person's Windows account on Windows.
LOCK = None
# In tests: the time as "2026-10-05T22:40", and the shift handoff's folder.
NOW = None
HANDOFF_DIR = None
# True while the window runs, so nothing waits for typed input.
WINDOW = False
# When Ctrl+C last skipped a question, for "twice in a row closes".
INTERRUPTED = 0.0
# "colon_prompts": prompts end in ":" instead of " >".
PROMPT_COLON = False
# "floor_tips": the tips for floor and shift work, read from the file.
FLOOR_TIPS = False
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


def missed_a_workday(last, d):
    """True when a weekday passed between the last opening (an ISO date) and
    d without one, so a weekend away isn't a missed day."""
    gap = range(1, (d - datetime.date.fromisoformat(last)).days)
    days = (d - datetime.timedelta(days=n) for n in gap)
    return any(when.weekday() < 5 and not holiday(when) for when in days)


def carried_due(intent):
    """The due date of a plan carried to another day, as dict items."""
    return {"due": intent["due"]} if intent.get("due") else {}


def due_note(intent, d):
    """"Due today." and the like for a plan with a due date, or ""."""
    due = intent and intent.get("due")
    if not due:
        return ""
    when = datetime.date.fromisoformat(due)
    if when == d:
        return tr("Due today.")
    if when == d + datetime.timedelta(days=1):
        return tr("Due tomorrow.")
    return (tr("Due {date}.") if when > d else tr("It was due {date}.")).format(
        date=long_date(when))


def due_choices(d):
    """The dates a due date can be set to: the next ten workdays from d."""
    days, when = [], d
    while len(days) < 10:
        if when.weekday() < 5 and not holiday(when):
            days.append(when)
        when += datetime.timedelta(days=1)
    return days


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


# The shared counts server: "212 people did today's tip". A package for
# people outside an organization sets this; an organization's policy wins.
# Empty means no server, and nothing is ever sent.
COUNTS_SERVER = ""
COUNTS_TIMEOUT = 2


def counts_server():
    """The shared counts server's address, or "" when there is none. Only
    https, except a server on this same computer, for testing one."""
    if policy("TurnOffSharedCounts"):
        return ""
    url = (policy_value("SharedCountsServer", "text") or COUNTS_SERVER).strip().rstrip("/")
    local = url.startswith(("http://localhost:", "http://127.0.0.1:"))
    return url if url.startswith("https://") or local else ""


def shared_on(state):
    return bool(counts_server() and state.get("shared"))


def net(path, send=False):
    """Ask the counts server for a JSON object, or post to it. None when it
    can't be reached in COUNTS_TIMEOUT seconds or answers nonsense, so a
    missing server never gets in the way. Nothing about the person is sent:
    the path holds only a date and what was done."""
    import urllib.request
    request = urllib.request.Request(
        counts_server() + path, data=b"{}" if send else None,
        method="POST" if send else "GET",
        headers={"Content-Type": "application/json",
                 "User-Agent": "hello-world"})
    try:
        with urllib.request.urlopen(request, timeout=COUNTS_TIMEOUT) as answer:
            data = json.loads(answer.read(10_000) or b"{}")
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def tip_count(d, add=False):
    """How many people did the day's tip, after counting this person when
    add is set; None when the server can't say."""
    data = net(f"/v1/day/{d.isoformat()}" + ("/tip" if add else ""), send=add)
    n = (data or {}).get("tip")
    return n if isinstance(n, int) and not isinstance(n, bool) and n >= 0 else None


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
    """The Startup .cmd that versions before 1.23 wrote, on Windows only. The
    folder comes from the Known Folder API, which follows a redirected
    profile, and from APPDATA where that fails."""
    if STARTUP_DIR is not None or os.name != "nt":
        return None
    folders = []
    if os.environ.get("APPDATA"):
        folders.append(os.path.join(os.environ["APPDATA"], "Microsoft", "Windows",
                                    "Start Menu", "Programs", "Startup"))
    folders.append(known_folder("B97D20BB-F46A-4C97-BA10-5E3608430854"))  # FOLDERID_Startup
    paths = [os.path.join(f, "hello-world-daily.cmd") for f in folders if f]
    # The one that has the old launcher, when the two folders differ.
    return next((p for p in paths if os.path.isfile(p)), paths[0] if paths else None)


def known_folder(guid):
    """A Windows known folder's path, or None."""
    try:
        import ctypes
        import uuid
        from ctypes import wintypes
        raw = (ctypes.c_ubyte * 16).from_buffer_copy(uuid.UUID(guid).bytes_le)
        path = wintypes.LPWSTR()
        shell = ctypes.windll.shell32
        if shell.SHGetKnownFolderPath(ctypes.byref(raw), 0, None, ctypes.byref(path)):
            return None
        try:
            return path.value
        finally:
            ctypes.windll.ole32.CoTaskMemFree(path)
    except (AttributeError, OSError, ValueError):
        return None


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
SWITCHES = ("nudge", "open_after", "weekends", "name", "no_startup_visits",
            "long_history", "hide_finished", "expire_same", "no_count",
            "numbers", "close_after_done", "colon_prompts", "floor_tips",
            "private_reminder", "hide_thought", "shared", "shared_asked")
SETTINGS = ("streak", "tips", "text", "offered", "offer_skips", "lang",
            "remind_at") + SWITCHES


def new_state():
    return {"visits": [], "intent": None, "streak": False}


MAX_PLAN = 400
# A plan can be a few things with ; between them, each finished on its own.
MAX_PARTS = 10
SAVED_PLAN = "Saved. Type done when you finish it, or it asks next time you open this."
MAX_FINISHED = 50
# Finished plans are kept for 14 days, or 90 with "long_history", and at most
# this many, so "This week" always has the whole week.
LONG_FINISHED = 300


def finished_cap(state):
    return LONG_FINISHED if state.get("long_history") else MAX_FINISHED


def keep_days(state):
    return 90 if state.get("long_history") else 14
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
LANGUAGE_READ = False


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
    text = tidy(text)
    if ";" in text:
        text = "; ".join(plan_parts(text))
    if len(text) > MAX_PLAN:
        cut = text[:MAX_PLAN]
        space = cut.rfind(" ", MAX_PLAN - 40)
        text = cut[:space] if space > 0 and not text[MAX_PLAN].isspace() else cut
        text = text.rstrip(" ;\u200c\u200d")
    return tidy(text.rstrip(" \u200c\u200d"))


def shortened(raw, text):
    """What to say when the saved plan is shorter than the typed one, or ""."""
    if len(tidy(raw)) <= MAX_PLAN:
        return ""
    # Counted without plan_parts, which folds parts past MAX_PARTS into one.
    lost = (sum(1 for part in tidy(raw).split(";") if part.strip())
            - sum(1 for part in text.split(";") if part.strip()))
    return tr("Shortened to {n} characters.").format(n=MAX_PLAN) + (
        " " + tr("Things left out: {n}.").format(n=lost) if lost > 0 else "")


def typed_plan(raw):
    """Clean a typed plan, and say so when it is cut."""
    text = clean(raw)
    if cut := shortened(raw, text):
        say(cut)
    return text


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


def lock_kind():
    """How notes are locked when saved: "dpapi" to the person's Windows
    account, or "plain" where that isn't possible or policy keeps them open.
    """
    if LOCK is not None:
        return LOCK
    if os.name == "nt" and not policy("UnlockedNotes"):
        return "dpapi"
    return "plain"


def notes_locked():
    return lock_kind() != "plain"


# Ties the lock to this program, so another program running as the same
# person can't open the notes by accident.
LOCK_ENTROPY = b"hello-world notes"


def _dpapi(data, protect, machine=False):
    """Windows' Data Protection API, scoped to the signed-in account, or to
    this PC so every account on it can read the data."""
    import ctypes
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_char))]

    def blob(raw):
        buffer = ctypes.create_string_buffer(raw, len(raw))
        return Blob(len(raw), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char))), buffer

    crypt = ctypes.windll.crypt32
    source, keep = blob(data)
    entropy, keep_entropy = blob(LOCK_ENTROPY)
    out = Blob()
    call = crypt.CryptProtectData if protect else crypt.CryptUnprotectData
    # CRYPTPROTECT_UI_FORBIDDEN: never ask anything on screen, and
    # CRYPTPROTECT_LOCAL_MACHINE for data every account on the PC shares.
    if not call(ctypes.byref(source), None, ctypes.byref(entropy), None, None,
                0x1 | (0x4 if machine else 0), ctypes.byref(out)):
        raise OSError("the notes could not be " + ("locked" if protect else "unlocked"))
    try:
        return ctypes.string_at(out.pbData, out.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(out.pbData)


def seal(text, machine=False):
    """The file's contents for the state's JSON text, locked if possible:
    to the person, or with machine set to everyone on this PC."""
    kind = lock_kind()
    if kind == "plain":
        return text
    if kind == "dpapi" and machine:
        kind = "dpapi-pc"
    data = text.encode("utf-8")
    sealed = _dpapi(data, True, kind == "dpapi-pc") if kind.startswith("dpapi") else data[::-1]
    return json.dumps({"locked": kind,
                       "data": base64.b64encode(sealed).decode("ascii")})


def unseal(raw):
    """The state dict inside a locked file, or raw as it is. ValueError when
    it can't be unlocked, such as a file from another Windows account."""
    if set(raw) != {"locked", "data"}:
        return raw
    try:
        data = base64.b64decode(raw["data"], validate=True)
        if raw["locked"] in ("dpapi", "dpapi-pc"):
            data = _dpapi(data, False, raw["locked"] == "dpapi-pc")
        elif raw["locked"] == "test":
            data = data[::-1]
        else:
            raise ValueError("unknown lock")
        inner = json.loads(data.decode("utf-8"))
    except (OSError, AttributeError, TypeError, UnicodeError) as e:
        raise ValueError("locked") from e
    if not isinstance(inner, dict):
        raise ValueError("not an object")
    return inner


def privacy_note():
    """The first-run sentence about plans and who can read them. It invites
    any kind of plan only where the notes are locked to the person."""
    if notes_locked():
        return tr("If you type a plan, it asks next time how it went. It can "
                  "be anything you want to get done, at work or not. Your "
                  "notes are locked to your Windows account and never sent "
                  "anywhere. Only someone with full admin control of this PC "
                  "could get to them.")
    return tr("If you type a plan, it asks next time how it went. Your notes "
              "stay on this computer and are never sent anywhere. Like any "
              "work file they are not secret, so keep them to everyday tasks.")


def load(repair=True):
    """Read the saved file. Returns (state, can_save).

    A missing file or a damaged one gives a fresh start; a damaged file is kept
    as notes.json.bak. A file that exists but can't be read right now is left
    alone, so a locked file is never overwritten with an empty one. With
    repair=False a damaged file is left where it is and can_save is False.
    """
    state = new_state()
    path = data_file()
    locked = False
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
        locked = set(raw) == {"locked", "data"}
        raw = unseal(raw)
    except (ValueError, RecursionError, MemoryError):
        if not repair:
            return state, False
        backup = backup_name(path)
        try:
            os.replace(path, backup)
        except OSError:
            return state, False
        if locked:
            para(tr("Your saved notes are locked to a Windows account that "
                    "can't open them here, so hello-world set them aside as a "
                    "backup copy and started fresh. Menu option 4 deletes "
                    "the backup."))
        else:
            para(tr("Your saved file was damaged, so hello-world set it aside "
                    "as a backup copy and started fresh. Your earlier days and "
                    "plan could not be read. Menu option 4 deletes the "
                    "backup."))
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
    global PROMPT_COLON, FLOOR_TIPS
    PROMPT_COLON = bool(state.get("colon_prompts"))
    FLOOR_TIPS = bool(state.get("floor_tips"))
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
    try:
        if day(raw.get("tip_day")) <= today().isoformat():
            state["tip_day"] = day(raw["tip_day"])
    except ValueError:
        pass
    global CHOSEN_LANGUAGE, LANGUAGE_READ
    if raw.get("lang") in LANGUAGE_NAMES:
        state["lang"] = raw["lang"]
    # Read once per run, so a choice made now shows from the next open and a
    # window never changes language half-way.
    if not LANGUAGE_READ:
        CHOSEN_LANGUAGE, LANGUAGE_READ = state.get("lang"), True
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
    n = raw.get("done") if raw.get("numbers") is True or COUNT_ALWAYS else None
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
                try:
                    if intent.get("due") is not None:
                        state["intent"]["due"] = day(intent["due"])
                except ValueError:
                    pass
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
    oldest_kept = (today() - datetime.timedelta(days=keep_days(state))).isoformat()
    finished = [item for item in finished if item["date"] >= oldest_kept]
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
            f.write(seal(json.dumps(file_form(state), indent=2)))
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
    if state["streak"] and not policy("HideDaysInARow"):
        para(tr("Days you opened it in the last {days} days: {n} (last 7 days: "
                "{recent})").format(days=KEEP_VISIT_DAYS, n=len(state["visits"]),
                                    recent=len(recent)))
    elif state["visits"]:
        # Only the latest date is kept when nothing counts days.
        say(tr("Last opened: {date}").format(date=long_date(
            datetime.date.fromisoformat(state["visits"][-1]))))
        para(tr("Only this date is kept, so it can say welcome back after a "
                "while away."))
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
    para(tr("It never leaves this computer. It is locked to your Windows "
            "account, so other people who use this computer or copy its "
            "files can't read it. Someone with full admin control of this PC "
            "still could.") if notes_locked() else
         tr("It never leaves this computer. Others who can read this "
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
    if left := exported_files():
        para(tr("The plans file you saved yourself is not deleted: {path}")
             .format(path="; ".join(left)) + " " + tr(
            "To delete it, choose Delete the plans file I saved."))
    if save(state):
        say(tr("A hello-world window still open elsewhere won't save it again."))
    else:
        para(tr("Close any other open hello-world window, or it may save its "
                "notes again."))
    return True


@contextlib.contextmanager
def file_lock(folder=None, name="notes.lock"):
    """Hold notes.lock while a change reads and writes the file, or another
    lock file in another folder, such as the shift handoff's.

    Without it, a delete in one window could land between another window's
    read and write, and that write would bring the deleted notes back.
    """
    try:
        if folder is None:
            folder = data_dir()
            os.makedirs(folder, mode=0o700, exist_ok=True)
        fd = os.open(os.path.join(folder, name),
                     os.O_RDWR | os.O_CREAT, 0o600 if folder == data_dir() else 0o666)
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
        elif gained < 0 and key == "done" and removed:
            # A forgotten finished plan takes its done back, but a window
            # that merely holds an older, lower count never subtracts.
            fresh[key] = max(fresh.get(key, 0) - min(-gained, sum(removed.values())), 0)
            if not fresh[key]:
                fresh.pop(key)
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


def set_plan(state, can_save, iso=None, after_done=False, in_menu=False):
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
        if note := due_note(old, datetime.date.fromisoformat(iso)):
            say(note)
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
    raw, kept = keep_leftovers(state, text, iso)
    if kept:
        text = clean(raw)
        if cut := shortened(raw, text):
            say(cut)
    base = copy.deepcopy(state)
    # Changing today's plan is a correction, so only a plan carried over from
    # an earlier day is kept for same.
    if old and old["text"] != text and old["date"] != iso:
        state["previous"] = old["text"]
    state["intent"] = {"text": text, "date": iso, **plan_due(
        old, text, datetime.date.fromisoformat(iso))}
    if commit(state, base, can_save):
        para(tr("Saved. Choose 11 when you finish it, or it asks next time "
                "you open this.") if in_menu else tr(SAVED_PLAN))
        if note := kept_note(kept, text):
            para(note)
        if note := due_note(state["intent"], datetime.date.fromisoformat(iso)):
            say(note)
        nudge_if_several(text)
    else:
        undo(state, base)
        say(tr("Could not save that on this computer. Your plan is unchanged."))
    return False


def forget_finished(state, can_save):
    """Remove one finished plan from the file, and leave everything else."""
    refresh(state, can_save)
    shown = newest_first(state.get("finished") or [])
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
                        "go back > ").format(n=len(shown)))
        if (choice or "").lower().strip(TRIM) in QUIT_WORDS:
            raise Quit
        if not choice or choice in numbers:
            break
        para(tr('There is no number "{typed}" on the list. Type a number from '
                "1 to {n}, or press Enter to go back.").format(
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
    state["finished"].remove(item)
    if state.get("done"):
        state["done"] -= 1
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
        reminding = reminder_on()
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
            say(" 12  " + tr("More settings..."))
            say("  " + tr("Enter") + "  " + (tr("Close") if alone else
                                             tr("Back to the last prompt")))
            listed = True
            choice = ask(tr("Choose 1 to 12, or Enter to go back > "))
        else:
            choice = ask(tr("Choose 1 to 12, m to list the options, or Enter to "
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
            # It also marks the offer as answered, so it doesn't come back.
            para(Visit.using(state, can_save).set_reminder(not reminding))
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
            set_plan(state, can_save, iso, in_menu=True)
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
            mark_done_now(state, can_save, today(), in_menu=True)
        elif choice == "12":
            more_settings(state, can_save)
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
            not_a_choice(choice, tr("Type 1 to 12, or press Enter to go back."))


def more_settings(state, can_save):
    """Menu option 12: the settings the window's Options has that the menu
    above doesn't, by number."""
    v = Visit.using(state, can_save)
    yes_no = " " + tr("(y or n, Enter to go back) > ")
    hint = tr("Type y or n, or press Enter to go back.")

    def marked(label, on):
        return (tr("{setting} (now on)") if on else
                tr("{setting} (now off)")).format(setting=label)

    def pick(entries):
        for n, (label, _) in enumerate(entries, 1):
            say(wrapped(f" {n:>2}  ", label))
        choice = (ask(tr("Type a number from 1 to {n}, or Enter to go back > ")
                      .format(n=len(entries))) or "").strip(TRIM)
        if choice.lower() in QUIT_WORDS:
            raise Quit
        if choice in [str(n) for n in range(1, len(entries) + 1)]:
            entries[int(choice) - 1][1]()
        elif choice:
            not_a_choice(choice, tr("Type a number from 1 to {n}, or press Enter "
                                    "to go back.").format(n=len(entries)))

    def flip(key, on_text, off_text):
        return lambda: para(v.switch(key, on_text, off_text))

    def reminders():
        at, on = state.get("remind_at"), reminder_on()
        entries = [(marked(tr("At sign-in"), on and not at),
                    lambda: para(v.set_reminder(True)))]
        entries += [(marked(tr("At {at}").format(at=t.lstrip("0")), on and at == t),
                     lambda t=t: para(v.reminder_at(t))) for t in REMINDER_TIMES]
        entries += [(marked(label, state.get(key)), flip(key, on_text, off_text))
                    for key, label, on_text, off_text in reminder_switches()
                    # The text screen opens whole at sign-in, so only the
                    # weekend setting means anything to it.
                    if key == "weekends" or not text_screen(state)]
        entries.append((marked(tr("No reminder"), not on),
                        lambda: para(v.set_reminder(False))))
        pick(entries)

    def numbers():
        if not state.get("numbers"):
            answer = ask_choice(
                tr("Keep my numbers from now on? They count the days you open "
                   "hello-world and the plans you finish, on this computer "
                   "only.") + yes_no, strict_yes(), NO_THANKS, hint)
            if answer != "yes":
                if answer == "no":
                    say(tr("Nothing changed."))
                return
            if not v.toggle("numbers"):
                say(tr("Could not save that choice on this computer."))
                return
        for line in numbers_text(state).split("\n"):
            para(line)

    def week():
        for line in week_text(state, today()).split("\n"):
            say(line)

    def export():
        para(exported(export_plans(state)))

    def due():
        days = due_choices(today())
        pick([(long_date(when), lambda when=when: para(v.set_due(when.isoformat())))
              for when in days] + [(tr("No due date"), lambda: para(v.set_due(None)))])

    def forget_previous():
        if ask_choice(tr("Forget the earlier plan? {text}").format(
                text=state["previous"]) + yes_no, strict_yes(), NO_WORDS,
                hint) != "yes":
            say(tr("Nothing changed."))
        elif v.setting("previous", None):
            say(tr("Done. The earlier plan is forgotten."))
        else:
            say(tr("Could not save that on this computer. Nothing changed."))

    entries = []
    if (launcher_place()[0] and not plans_off()
            and not policy("DisableSignInLauncher")):
        entries.append((tr("Reminder settings..."), reminders))
    entries.append((marked(tr("Greet me by name"), state.get("name")), flip(
        "name", tr("Done. The greeting uses your first name."),
        tr("Done. The greeting is back to the usual one."))))
    if not policy("HideThoughtAndTip") and state.get("tips", True):
        entries.append((marked(tr("Also show the thought"), not state.get("hide_thought")),
                        flip("hide_thought", tr("Done. The thought is off."),
                             tr("Done. The thought is on."))))
    if not (policy("HideThoughtAndTip") or policy("FloorTips") or org_content()):
        entries.append((marked(tr("Tips for floor and shift work"),
                               state.get("floor_tips")), flip(
            "floor_tips", tr("Floor and shift tips are on."),
            tr("Floor and shift tips are off."))))
    if not plans_off():
        entries += [
            (tr("This week..."), week),
            (tr("My numbers..."), numbers),
            (tr("Save my plans to a file"), export),
            (marked(tr("Keep a longer history"), state.get("long_history")), flip(
                "long_history",
                tr("Done. Finished plans are kept for 90 days instead of 14."),
                tr("Done. Finished plans are kept for 14 days, as usual.")))]
        # Entries that come and go are last, so the others keep their numbers.
        if state.get("previous"):
            entries.append((tr("Forget the earlier plan"), forget_previous))
        if state["intent"]:
            entries.append((tr("Due date for my plan..."), due))
        if exported_files():
            entries.append((tr("Delete the plans file I saved"),
                            lambda: para(delete_export())))
    if counts_server() and state.get("tips", True) and not policy("HideThoughtAndTip"):
        entries.append((marked(tr("Show how many people did the tip"), state.get("shared")),
                        lambda: para(v.shared_switch())))
    pick(entries)


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
    answer = ask(tr("Type a number from 1 to {n}, or Enter to go back > ")
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
    parts = [part.strip() for part in text.split(";")
             if any(c.isalnum() or unicodedata.category(c) == "So" for c in part)]
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
        # A count only for someone who keeps "My numbers".
        if (state.get("numbers") or COUNT_ALWAYS) and not state.get("no_count"):
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


def done_message(state, d, n):
    """The day's done line for one thing, or a count for several."""
    if n > 1:
        return tr("Good. {n} things are off your list.").format(n=n)
    return done_lines(state, d)[0]


def ask_parts(parts):
    """"Did you do them?" for a plan of several things. Returns (answer,
    parts done): ("yes", None) for all, ("yes", [0, 2]) for some, or the
    "no", "" or None of ask_choice()."""
    say(tr("Last time you planned:"))
    for n, part in enumerate(parts, 1):
        say(wrapped(f"  {n}  ", part))
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
        if (done := picked(words, len(parts))) is not None:
            return "yes", (None if len(done) == len(parts) else done)
        if text in strict_yes() + DONE_WORDS + DID_WORDS:
            return "yes", None
        if text in NO:
            return "no", None
        not_a_choice(typed, hint)
    return None, None


def picked(words, count):
    """The indexes that numbers such as "1 3" or "2-4" name, or None when a
    word isn't one of 1 to count or a range of them."""
    done = set()
    for word in words:
        low, dash, high = word.partition("-")
        high = high if dash else low
        if not (low.isdecimal() and high.isdecimal()):
            return None
        low, high = int(low), int(high)
        if not 1 <= low <= high <= count:
            return None
        done.update(range(low - 1, high))
    return sorted(done) if done else None


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


def leftovers(state, text, iso):
    """Today's unfinished things that a new plan sharing none of them would
    drop: a plan of several things, what is left after finishing some, or a
    plan carried over from an earlier day."""
    old = state["intent"]
    if not old or old["date"] != iso or not text:
        return []
    before = plan_parts(old["text"])
    if {p.casefold() for p in before} & {p.casefold() for p in plan_parts(text)}:
        return []
    if (len(before) > 1 or old.get("since", iso) < iso
            or any(i["date"] == iso for i in state.get("finished", []))):
        return before
    return []


def newest_first(finished):
    """Finished things newest first, by the day they were finished."""
    return sorted(reversed(finished), key=lambda item: item["date"], reverse=True)


def keep_leftovers(state, text, iso):
    """A new plan with today's unfinished things after it, so typing over
    them never drops them. Returns (plan before cleaning, things kept). The
    new plan goes first, so a cut at MAX_PLAN takes the oldest things."""
    kept = leftovers(state, text, iso)
    return (text + "; " + "; ".join(kept) if kept else text), kept


def kept_note(kept, text):
    """What to say about the unfinished things a new plan kept, or ""."""
    still = [part for part in kept if part in plan_parts(text)]
    if not still:
        return ""
    note = tr("Still on your list from before: {text}").format(text="; ".join(still))
    # The plan's own words end it, so the sentence may still need its stop.
    return note if note[-1] in ".!?。" else note + "."


def typed_due(text, d):
    """The earliest date on or after d written in a plan, as ISO, or None:
    2026-10-30, 30/10 (or 10/30 where Windows writes the month first), a
    weekday's full name, or "by" and the like followed by a weekday, today or
    tomorrow."""
    # ponytail: a weekday's full name anywhere counts, so "Friday meeting
    # notes" gets a due date; it shows, and No due date removes it.
    low = text.lower()
    found = []
    for y, m, n in re.findall(r"(?<!\d)(\d{4})-(\d{1,2})-(\d{1,2})(?!\d)", low):
        found.append((int(y), int(m), int(n)))
    month_first = DATE_ORDER == "mdy" if DATE_ORDER else short_date_month_first()
    # 30.10 alone could be a number, so a date with dots needs its year.
    numeric = (re.findall(r"(?<![\d/.-])(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?(?![\d/.])", low)
               + re.findall(r"(?<![\d/.-])(\d{1,2})\.(\d{1,2})\.(\d{2,4})(?![\d/.])", low))
    for a, b, y in numeric:
        m, n = (a, b) if month_first else (b, a)
        if y:
            found.append((int(y) + (2000 if len(y) == 2 else 0), int(m), int(n)))
        else:
            found.append((None, int(m), int(n)))
    dates = []
    for y, m, n in found:
        try:
            when = datetime.date(y or d.year, m, n)
        except ValueError:
            continue
        if y is None and (d - when).days > 180:
            when = when.replace(year=d.year + 1)
        dates.append(when)
    names = [DAYS] + ([translation()["days"]] if translation() else [])
    cues = [w for w in tr("by|due|before").lower().split("|") if w]
    after_cue = [re.split(r"(?<!\w)" + re.escape(cue) + r"(?!\w)", low, maxsplit=1)[1].split()[:1]
                 for cue in cues
                 if re.search(r"(?<!\w)" + re.escape(cue) + r"(?!\w)", low)]
    after_cue = [words[0].strip(".,;:!") for words in after_cue if words]
    for weekday in range(7):
        for days in names:
            full = days[weekday].lower()
            short = {full, full.split("-")[0], full[:3] if days is DAYS else full}
            if (re.search(r"(?<!\w)" + re.escape(full) + r"(?!\w)", low)
                    or any(word in short for word in after_cue)):
                dates.append(d + datetime.timedelta(days=(weekday - d.weekday()) % 7))
    for word in after_cue:
        if word in tr("today").lower().split("|"):
            dates.append(d)
        elif word in tr("tomorrow").lower().split("|"):
            dates.append(d + datetime.timedelta(days=1))
    dates = [when for when in dates if (d - when).days <= 180]
    return min(dates).isoformat() if dates else None


def short_date_month_first():
    """True where Windows writes short dates month first, as in the US."""
    try:
        import ctypes
        buffer = ctypes.create_unicode_buffer(80)
        # LOCALE_SSHORTDATE of the user's default locale.
        if ctypes.windll.kernel32.GetLocaleInfoEx(None, 0x1F, buffer, 80):
            return buffer.value.lstrip("'").upper().startswith("M")
    except (AttributeError, OSError):
        pass
    return False


def plan_due(old, text, d):
    """The due date for a plan saved over `old`, as dict items: one written
    in the plan, else the old one while the plan keeps any of its things."""
    if found := typed_due(text, d):
        return {"due": found}
    if old and ({p.casefold() for p in plan_parts(old["text"])}
                & {p.casefold() for p in plan_parts(text)}):
        return carried_due(old)
    return {}


def nudge_if_several(text):
    """A plan of several things joined together is hard to finish. A list
    with ; is several on purpose, and each part is finished on its own."""
    if ";" in text:
        return
    padded = f" {text.lower()} "
    if any(joint in padded for joint in (" and ", " & ", " y ")) or "+" in text:
        para(tr("That looks like more than one thing. Finishing the first "
                "part still counts."))


def mark_done_now(state, can_save, d, which=True, in_menu=False):
    """Same-day done: the plan on screen is finished, so say so at once. For
    a plan of several things it asks which, unless `which` is False."""
    refresh(state, can_save)
    plan = state["intent"]
    if not plan:
        para(tr("There is no plan to mark as done. Choose 6 to set one.")
             if in_menu else
             tr("There is no plan to mark as done. Type plan to set one."))
        return False
    every = plan_parts(plan["text"])
    chosen = None
    if len(every) > 1 and which:
        answered, chosen = ask_which(every)
        if not answered:
            say(tr("Nothing changed."))
            return False
        refresh(state, can_save)
        if state["intent"] != plan:
            say(tr("The other open window changed the plan, so its plan is kept."))
            return False
    base = copy.deepcopy(state)
    rest = finish_plan(state, plan["text"], d, chosen)
    state["intent"] = dict(plan, text=rest) if rest else None
    if not commit(state, base, can_save):
        undo(state, base)
        say(tr("Could not save that on this computer. The plan is still open."))
        return False
    say(done_message(state, d, len(chosen) if chosen else len(every)) + (
        " " + tr("The rest is kept for today.") if rest else ""))
    show_finished(state, SHOWN_AFTER_DONE)
    return True


def ask_which(parts):
    """Which of today's things are finished. Returns (True, indexes), with
    None for all of them, or (False, None) for Enter or no answer."""
    for n, part in enumerate(parts, 1):
        say(wrapped(f"  {n}  ", part))
    for _ in range(3):
        typed = ask(tr("Which did you finish? Type numbers such as 1 3 or 1-3, "
                       "y for all, or Enter to go back > "))
        text = (typed or "").lower().strip(TRIM)
        if not text:
            return False, None
        if text in QUIT_WORDS:
            raise Quit
        words = text.replace(",", " ").split()
        if (done := picked(words, len(parts))) is not None:
            return True, (None if len(done) == len(parts) else done)
        if text in strict_yes() + DONE_WORDS + DID_WORDS:
            return True, None
        not_a_choice(typed, tr("Type numbers from 1 to {n}, such as 1 3 or 1-3, "
                               "y for all, or press Enter to go back.").format(n=len(parts)))
    return False, None


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
        return tr("My numbers are off.")
    return "\n".join([
        tr("Days you opened hello-world: {n}").format(n=state.get("opens", 0)),
        tr("Longest run of days: {n}").format(n=state.get("best_run", 0)),
        tr("Plans finished: {n}").format(n=state.get("done", 0)), "",
        tr("A run goes on over a gap of up to three days, such as a weekend."),
        tr("They count from the day you turned them on, and stay on this "
           "computer. Nobody else gets them.")])


def week_text(state, d):
    """What was finished since Monday."""
    start = d - datetime.timedelta(days=d.weekday())
    monday, before = start.isoformat(), (start - datetime.timedelta(days=7)).isoformat()
    finished = state.get("finished", [])
    items = [i for i in finished if i["date"] >= monday]
    earlier = [i for i in finished if before <= i["date"] < monday]

    def rows(found):
        return ["  " + tr("{date}: ").format(date=long_date(
            datetime.date.fromisoformat(i["date"]))) + i["text"] for i in found]
    lines = ([tr("This week you finished {n}:").format(n=len(items))] + rows(items)
             if items else [tr("Nothing finished yet this week. That is fine.")])
    if earlier:
        lines += ["", tr("Last week you finished {n}:").format(n=len(earlier))] + rows(earlier)
    return "\n".join(lines)


# Where --export and Options save the plans; None is the Documents folder.
EXPORT_DIR = None


def export_file(ext=".md"):
    """Where Save my plans to a file writes, in the person's Documents: the
    Markdown file, or with ext=".csv" its copy for spreadsheets."""
    # The Known Folder API follows OneDrive and redirected Documents folders.
    folder = (EXPORT_DIR or known_folder("FDD39AD0-238F-46AF-ADB4-6C85480369C7")
              or os.path.join(os.path.expanduser("~"), "Documents"))
    # The name is translated, so it is checked for a character Windows refuses.
    return os.path.join(folder, file_name(tr("hello-world plans")) + ext)


def file_name(name):
    """A translated file name, or the English one where Windows would refuse
    it."""
    if not name.strip(" .") or any(c in name for c in '<>:"/\\|?*'):
        return "hello-world plans"
    return name


def exported_files():
    """The exported files there are, under the name of any language, since
    the language may have changed since the export."""
    folder = os.path.dirname(export_file())
    names = {"hello-world plans"} | {
        file_name(data["text"]["hello-world plans"]) for data in LANGUAGES.values()
        if "hello-world plans" in data.get("text", {})}
    return [path for name in sorted(names) for ext in (".md", ".csv")
            if os.path.exists(path := os.path.join(folder, name + ext))]


def list_separator():
    """The separator Excel expects in a .csv on this computer, which is ;
    where the decimal mark is a comma, as in Brazil or Spain."""
    try:
        import ctypes
        buffer = ctypes.create_unicode_buffer(4)
        # LOCALE_SLIST of the user's default locale.
        if ctypes.windll.kernel32.GetLocaleInfoEx(None, 0x0C, buffer, 4):
            if len(buffer.value) == 1:
                return buffer.value
    except (AttributeError, OSError):
        pass
    return ","


def export_plans(state):
    """Write the current and finished plans to a Markdown file in the
    person's Documents folder, and the same as a .csv for spreadsheets.
    Returns the Markdown file's path, or None."""
    path = export_file()
    lines = ["# hello-world", ""]
    if state["intent"]:
        lines += ["## " + tr("Your current plan: ").strip(), ""]
        lines += [f"- {part}" for part in plan_parts(state["intent"]["text"])] + [""]
    if state.get("finished"):
        lines += ["## " + tr("Finished lately:"), ""]
        lines += [f"- {i['date']}: {i['text']}" for i in newest_first(state["finished"])]
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines).rstrip() + "\n")
    except OSError:
        return None
    try:
        # The byte order mark makes Excel read the file as UTF-8.
        with open(export_file(".csv"), "w", encoding="utf-8-sig", newline="") as f:
            rows = csv.writer(f, delimiter=list_separator())
            rows.writerow([tr("Date"), tr("Plan"), tr("Due"), tr("Finished")])
            if state["intent"]:
                rows.writerows([state["intent"]["date"], part,
                                state["intent"].get("due", ""), ""]
                               for part in plan_parts(state["intent"]["text"]))
            rows.writerows([i["date"], i["text"], "", tr("yes")]
                           for i in newest_first(state.get("finished", [])))
    except OSError:
        # The .md was saved; a .csv open in Excel stays as it was.
        pass
    return path


def delete_export():
    """Delete the files Save my plans to a file wrote. Returns the message."""
    try:
        for path in exported_files():
            os.remove(path)
    except OSError:
        return tr("Could not delete the plans file. Close it if it is open, "
                  "then try again.")
    return tr("Done. The plans file you saved is deleted.")


def exported(path):
    """What to say after Save my plans to a file."""
    return (tr("Saved to {path}").format(path=path) + "\n" + tr(
        "A copy for spreadsheets is next to it, ending in .csv.")) if path else tr(
        "Could not save that on this computer.")


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
    move_old_task()
    if policy("DisableSignInLauncher"):
        if launcher_on() or legacy_launcher() and os.path.isfile(legacy_launcher()):
            remind(False, quiet=True)
        # The timed reminder too, which the policy covers the same way.
        if task_on():
            reminder_task(None)
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

    Returns (saved, message). Finishing counts on the plan's own day: the
    question is about last time, and the pilots read the answer's day as
    wrong.
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
        rest = finish_plan(state, text, datetime.date.fromisoformat(intent["date"]), parts)
        state["intent"] = rest and {"text": rest, "date": d.isoformat(),
                                    "since": intent.get("since", intent["date"]), **carried_due(intent)}
        state["intent"] = state["intent"] or None
    elif choice == "no":
        state["intent"] = {"text": text, "date": d.isoformat(),
                           "since": intent.get("since", intent["date"]), **carried_due(intent)}
    else:
        state["intent"] = dict(intent, skips=intent.get("skips", 0) + 1)
    if not commit(state, base, can_save):
        undo(state, base)
        return False, tr("Could not save that on this computer. Your answer "
                         "was not counted.")
    if choice == "yes":
        n = len(set(parts)) if parts else len(plan_parts(text))
        return True, done_message(state, d, n) + (
            " " + tr("The rest is kept for today.") if rest else "")
    return True, tr("Kept for today.") if choice == "no" else tr(
        "Skipped. It asks again next time.")


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

    if handoff_on():
        for line in handoff_lines():
            say(wrapped("", line))
        say(tr("Type handoff at the end to leave a note or clear one."))
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
            welcome.append(privacy_note())
        welcome.append(tr("Type menu at the end for the options."))
        para(" ".join(welcome))
        say()
    elif not seen_today:
        row = in_a_row(state["visits"], d)
        if missed_a_workday(state["visits"][-1], d):
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
            if note := due_note(intent, d):
                say(note)
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
                    "since": intent.get("since", intent["date"]), **carried_due(intent)} or None
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
                              "since": intent.get("since", intent["date"]), **carried_due(intent)}
                    say(tr("Kept for today."))
            elif answer is None and person:
                say(tr("That was not understood. Your plan is left as it was."))
            elif answer is not None:
                intent = dict(intent, skips=intent.get("skips", 0) + 1)
                say(tr("Skipped. It asks again next time."))
            say()

        if state.get("tips", True) and not policy("HideThoughtAndTip"):
            thought, tip = todays_pair(d)
            if not state.get("hide_thought"):
                say(tr("Thought for today:"))
                say(indent(thought))
                say()
            say(tr("Try this today:"))
            say(indent(tip))
            if person and not seen_today:
                offer_shared(state)
            if shared_on(state) and (n := tip_count(d)) is not None:
                say(indent(tr("People who did today's tip so far: {n}").format(n=n)))
                if state.get("tip_day") != iso:
                    say(indent(tr("Type tip at the end once you have done it.")))
            say()

        if intent and intent["date"] == iso:
            say(wrapped(tr("Your plan for today: "), intent["text"]))
            if note := due_note(intent, d):
                say(note)
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
                    intent = {"text": text, "date": iso, **plan_due(intent, text, d)}
                    typed_new = True
                    if note := due_note(intent, d):
                        say(note)
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


def offer_shared(state):
    """Ask once whether to see how many people did the day's tip. The
    answer is saved with the rest of the visit."""
    if not counts_server() or state.get("shared_asked"):
        return
    answer = ask_choice(
        tr("See how many people do each day's tip? It sends only that you "
           "did the tip, never your plans or your name. (y or n, Enter for "
           "no) > "),
        strict_yes(), NO_THANKS, tr("Type y or n, or press Enter for no."))
    if answer is None:
        return
    state["shared_asked"] = True
    if answer == "yes":
        state["shared"] = True
    else:
        say(tr("No problem. Menu option 12 can turn it on later."))


def did_tip(state, can_save, d):
    """Count this person once for the day's tip. Returns what to say."""
    iso = d.isoformat()
    if state.get("tip_day") == iso:
        n = tip_count(d)
    else:
        n = tip_count(d, add=True)
        if n is not None:
            refresh(state, can_save)
            base = copy.deepcopy(state)
            state["tip_day"] = iso
            if not commit(state, base, can_save):
                undo(state, base)
    if n is None:
        return tr("The shared count can't be reached just now.")
    return tr("Counted. People who did today's tip so far: {n}").format(n=n)


# Shift handoff: notes left on a shared PC for whoever uses it next. They are
# the PC's, not a person's, so everyone who signs in to it reads them.
MAX_HANDOFF = 5
MAX_KEPT = 5


def now():
    return (datetime.datetime.fromisoformat(NOW) if NOW
            else datetime.datetime.now().replace(second=0, microsecond=0))


def handoff_on():
    return policy("ShiftHandoff")


def handoff_shared_folder():
    """The folder the HandoffFolder policy names, so every PC on a unit
    shows the same notes, or ""."""
    return (policy_value("HandoffFolder", "text") or "").strip()


def handoff_dir():
    if shared := handoff_shared_folder():
        return shared
    if HANDOFF_DIR:
        return HANDOFF_DIR
    if os.name == "nt":
        return os.path.join(os.environ.get("ProgramData") or r"C:\ProgramData",
                            "hello-world")
    return os.path.join(os.path.expanduser("~"), ".local", "share", "hello-world-pc")


def handoff_hours():
    hours = policy_value("HandoffHours", "number")
    return min(max(hours, 1), 336) if hours else 72


def read_handoff():
    """Every handoff note saved on this PC or unit, oldest first."""
    try:
        with open(os.path.join(handoff_dir(), "handoff.json"), encoding="utf-8") as f:
            raw = json.loads(f.read(100_000))
        raw = unseal(raw) if isinstance(raw, dict) else {}
    except (OSError, ValueError, RecursionError):
        return []
    notes = []
    for note in raw.get("notes", []) if isinstance(raw.get("notes"), list) else []:
        try:
            at = datetime.datetime.fromisoformat(note["at"])
            text = clean(note["text"])
        except (TypeError, KeyError, ValueError):
            continue
        if text:
            notes.append({"text": text, "at": at.isoformat(timespec="minutes"),
                          "keep": note.get("keep") is True})
    return notes


def write_handoff(notes):
    """Save the notes: locked to this PC, or plain in a shared unit folder,
    where the folder's own permissions decide who reads them."""
    folder = handoff_dir()
    text = json.dumps({"notes": notes}, ensure_ascii=False)
    try:
        os.makedirs(folder, exist_ok=True)
        if not handoff_shared_folder():
            text = seal(text, machine=True)
        tmp = os.path.join(folder, f"handoff.json.{os.getpid()}.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, os.path.join(folder, "handoff.json"))
        return True
    except OSError:
        return False


def shown_handoff():
    """The notes to show, newest first: kept ones, and the rest within the
    policy's hours."""
    cutoff = now() - datetime.timedelta(hours=handoff_hours())
    notes = [n for n in read_handoff()
             if n["keep"] or datetime.datetime.fromisoformat(n["at"]) >= cutoff]
    return notes


def handoff_order(notes):
    """Kept notes first, then the newest."""
    newest = sorted(notes, key=lambda n: n["at"], reverse=True)
    return [n for n in newest if n["keep"]] + [n for n in newest if not n["keep"]]


def age(at):
    """How long ago, in the largest whole unit, so nobody does date sums."""
    minutes = max(0, int((now() - datetime.datetime.fromisoformat(at)).total_seconds() // 60))
    if minutes < 60:
        return tr("{n} min ago").format(n=minutes)
    if minutes < 48 * 60:
        return tr("{n} h ago").format(n=minutes // 60)
    return tr("{n} d ago").format(n=minutes // (24 * 60))


def handoff_lines():
    """The handoff block for the screen, as lines."""
    notes = handoff_order(shown_handoff())
    lines = [tr("Shift handoff on this PC (turned on by your organization):")]
    if not notes:
        lines.append(tr("No handoff notes in the last {n} hours.").format(n=handoff_hours()))
    for n, note in enumerate(notes, 1):
        kept = tr("Kept until cleared. ") if note["keep"] else ""
        lines.append(f"{n}. {age(note['at'])}: {kept}{note['text']}")
    return lines


def leave_handoff(text, keep=False):
    """Add a note. Returns what to say."""
    text = clean(text)
    if not text:
        return tr("Nothing changed.")
    with file_lock(handoff_dir(), "handoff.lock") if os.path.isdir(handoff_dir()) else contextlib.nullcontext():
        notes = read_handoff()
        notes.append({"text": text, "at": now().isoformat(timespec="minutes"), "keep": keep})
        kept = [n for n in notes if n["keep"]][-MAX_KEPT:]
        rest = [n for n in notes if not n["keep"]][-MAX_HANDOFF:]
        if not write_handoff(sorted(kept + rest, key=lambda n: n["at"])):
            return tr("Could not save the handoff note on this PC.")
    report_usage("handoff note left")
    return tr("Left for the next shift.")


def clear_handoff(number):
    """Remove the note shown with this number. Returns what to say."""
    with file_lock(handoff_dir(), "handoff.lock") if os.path.isdir(handoff_dir()) else contextlib.nullcontext():
        shown = handoff_order(shown_handoff())
        if not 1 <= number <= len(shown):
            return tr("Nothing changed.")
        gone = shown[number - 1]
        notes = [n for n in read_handoff() if n != gone]
        if not write_handoff(notes):
            return tr("Could not save the handoff note on this PC.")
    return tr("Cleared.")


def handoff_prompt():
    """The text screen's handoff: leave a note, or clear one."""
    para(tr("Everyone who uses this PC sees handoff notes. No patient or "
            "customer details. Not a safety or defect record."))
    para(tr("Sign it if the next shift may need to ask you."))
    typed = ask(tr("Type a note for the next shift, clear to remove one, or "
                   "Enter to go back > "))
    word = (typed or "").lower().strip(TRIM)
    if word in QUIT_WORDS:
        raise Quit
    if not word:
        return
    if word in CLEAR_WORDS:
        for line in handoff_lines()[1:]:
            say(wrapped("  ", line))
        choice = (ask(tr("Which note to clear? Type its number, or Enter to go "
                         "back > ")) or "").strip(TRIM)
        if choice.isdecimal():
            para(clear_handoff(int(choice)))
        return
    keep = ask_choice(tr("Keep it until someone clears it? (y or n, Enter for "
                         "no) > "), strict_yes(), NO_WORDS,
                      tr("Type y or n, or press Enter for no.")) == "yes"
    para(leave_handoff(typed, keep))


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
        elif answer in TIP_WORDS and shared_on(state):
            say(did_tip(state, can_save, d))
            continue
        elif answer in HANDOFF_WORDS and handoff_on():
            handoff_prompt()
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
    if argv[:2] == ["--set", "no_weekends"] and len(argv) == 3:
        # The 1.39.0 name, kept so scripts written for it still work.
        argv = ["--set", "weekends", {"on": "off", "off": "on"}.get(argv[2], "")]
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
            say(exported(path))
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
        Visit.using(*load()).drop_timed()
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
        message, keep = None, None
        while True:
            window = Window(Visit(redraw=keep is not None), message, keep)
            window.run()
            if window.reopened is None:
                break
            message, keep = window.reopened, window.keep
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
TASK_NAME = "hello-world reminder " + "-".join(
    filter(None, (os.environ.get("USERDOMAIN"), os.environ.get("USERNAME") or "user")))
# Before 1.37.0 the task carried only the user name.
OLD_TASK_NAME = "hello-world reminder " + (os.environ.get("USERNAME") or "user")
REMINDER_TIMES = ("08:00", "09:00", "10:00", "13:00")


def reminder_switches():
    """The reminder's on-or-off settings: key, label, and what to say when it
    turns on and when it turns off."""
    return (("nudge", tr("Also on days with no plan"),
             tr("Done. The reminder also comes on days with no plan."),
             tr("Done. The reminder comes only when there is a plan.")),
            ("open_after", tr("Open hello-world after I answer"),
             tr("Done. hello-world opens after you answer."),
             tr("Done. Answering no longer opens hello-world.")),
            ("weekends", tr("Also on weekends"),
             tr("Done. The reminder comes on weekends too."),
             tr("Done. No reminder on Saturday or Sunday.")),
            ("private_reminder", tr("Leave my plan out of the reminder"),
             tr("Done. The reminder leaves your plan out."),
             tr("Done. The reminder shows your plan.")))


def move_old_task():
    """Remove a reminder task under its pre-1.37.0 name, which nothing else
    finds, and set it up again under the current name at the same time unless
    the policy turns reminders off."""
    if TASKS is not None or os.name != "nt" or OLD_TASK_NAME == TASK_NAME:
        return
    import subprocess
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    r = subprocess.run(["schtasks", "/Query", "/XML", "/TN", OLD_TASK_NAME],
                       capture_output=True, creationflags=flags)
    if r.returncode:
        return
    found = re.search(rb"StartBoundary>[^<T]*T(\d\d:\d\d)", r.stdout.replace(b"\0", b""))
    subprocess.run(["schtasks", "/Delete", "/F", "/TN", OLD_TASK_NAME],
                   capture_output=True, creationflags=flags)
    at = found and found.group(1).decode()
    if at in REMINDER_TIMES and not policy("DisableSignInLauncher"):
        reminder_task(at)


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
    unless the person asked for them, and not on the organization's holidays.
    """
    iso = d.isoformat()
    if (iso in state["visits"] or state.get("notified") == iso or holiday(d)
            or not state.get("weekends") and d.weekday() >= 5):
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
    # Nobody is at the screen yet, so a damaged file waits under the policy.
    state, can_save = load(repair=not policy("LeaveDamagedFile"))
    if policy("DisableSignInLauncher"):
        quietly(tidy_launcher)
        return 0
    if text_screen(state):
        if not (holiday(d) or not state.get("weekends") and d.weekday() >= 5):
            open_console("--startup")
        return 0
    text = reminder_due(state, d)
    if text is None:
        return 0
    base = copy.deepcopy(state)
    state["notified"] = d.isoformat()
    shown = (show_reminder(text, state["intent"]["date"], state.get("private_reminder"),
                           due_note(state["intent"], d))
             if text else show_nudge())
    # Unsaved, it would come again at the next sign-in today. A window opens
    # in a process of its own, outside the scheduled task's time limit.
    if commit(state, base, can_save) and not shown:
        open_window()
    return 0


def open_window():
    """Start the window in a new pythonw.exe."""
    import subprocess
    subprocess.Popen([window_python(), "-I", os.path.abspath(__file__), "--window"],
                     creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))


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


def plan_key(text, date):
    """What a reminder's answer links name, so a click answers only the plan
    it asked about: its date and a short digest of its text."""
    import hashlib
    return date + "-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def show_reminder(text, date=None, private=False, due=""):
    """Show a Windows notification with the plan and three answers. False when
    Windows would not show it, such as where PowerShell is locked down.
    `private` leaves the plan's words out, for a shared screen."""
    escape = xml_text
    key = plan_key(text, date or "")
    several = len(plan_parts(text)) > 1
    ask = tr("Open it to tick the ones you did.") if several else tr("Did you do it?")
    shown = ask if private else tr("Last time you planned: ") + text
    # One Done would finish every thing, so several open the tick boxes.
    first = ((tr("&Open"), "hello-world:open") if several
             else (tr("&Done"), f"hello-world:done/{key}"))
    return notify('<toast activationType="protocol" launch="hello-world:open">'
           '<visual><binding template="ToastGeneric">'
           f'<text>{escape(shown)}</text>'
           + ("" if private else f'<text>{escape(ask)}</text>')
           + (f'<text>{escape(due)}</text>' if due else "")
           + '</binding></visual>'
           '<actions>'
           f'<action content="{escape(first[0].replace("&", ""))}" '
           f'activationType="protocol" arguments="{first[1]}"/>'
           f'<action content="{escape(tr("&Not yet").replace("&", ""))}" '
           f'activationType="protocol" arguments="hello-world:notyet/{key}"/>'
           f'<action content="{escape(tr("S&kip").replace("&", ""))}" '
           f'activationType="protocol" arguments="hello-world:skip/{key}"/>'
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
    word, _, key = word.partition("/")
    if word == "open" and not key:
        return show_window()
    if word not in ("done", "notyet", "skip") or not key:
        return 2
    d = today()
    state, can_save = load(repair=not policy("LeaveDamagedFile"))
    intent = state["intent"]
    # An old notification, or a link from anywhere else, names another plan.
    if asks_followup(intent, d) and plan_key(intent["text"], intent["date"]) == key:
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

    @classmethod
    def using(cls, state, can_save):
        """A Visit over state already loaded, for the text menu's settings,
        without counting another opening."""
        visit = cls.__new__(cls)
        visit.state, visit.can_save, visit.d = state, can_save, today()
        visit.iso = visit.d.isoformat()
        return visit

    def __init__(self, redraw=False):
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
                notes.append(privacy_note())
        elif not seen:
            row = in_a_row(state["visits"], d)
            if missed_a_workday(state["visits"][-1], d):
                notes.append(tr("Welcome back. Glad you are here."))
            elif (state["streak"] and not policy("HideDaysInARow")
                  and (row in (3, 7, 14) or row % 30 == 0)):
                notes.append(tr("You have opened this {row} days in a row. "
                                "Nice to see you.").format(row=row))
        state["intent"] = intent
        if not redraw:
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
        self.tip_people = tip_count(d) if self.pair and shared_on(state) else None

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
        if not tidy(typed) and not self.plan():
            return False, tr("Type a plan in the box first. Not today closes "
                             "the window."), False
        if not tidy(typed) or clean(typed) == self.plan():
            return True, "", False
        if is_same(typed) and not self.state.get("previous"):
            return False, tr("There is no earlier plan to reuse yet. Nothing "
                             "was saved."), False
        command, said = quietly(is_command, typed, tr("Type your plan in the box."))
        if command:
            # A word like "skip" or "none" is a choice to plan nothing.
            return not said, said, False
        state = self.state
        raw, kept = keep_leftovers(state, clean(reuse(state, typed)), self.iso)
        text = clean(raw)
        base = copy.deepcopy(state)
        old = state["intent"]
        if old and old["text"] != text and old["date"] != self.iso:
            state["previous"] = old["text"]
        state["intent"] = {"text": text, "date": self.iso,
                           **plan_due(old, text, self.d)}
        saved, said = quietly(commit, state, base, self.can_save)
        if not saved:
            undo(state, base)
            return False, said or tr("Could not save that on this computer. "
                                     "Your plan is unchanged."), False
        self.followup = None
        _, several = quietly(nudge_if_several, text)
        notes = [shortened(raw if kept else typed, text), kept_note(kept, text),
                 due_note(state["intent"], self.d), several]
        return False, " ".join([tr("Saved.")] + [n for n in notes if n]), True

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
            quietly(refresh, self.state, self.can_save)
            mine = plan_parts(clean(typed))
            today = {p.casefold(): p for p in plan_parts(self.plan())} if self.plan() else {}
            # The box edited down to some of today's things finishes those.
            if today and all(p.casefold() in today for p in mine):
                return self.finish_parts([today[p.casefold()] for p in mine])
            close, message, saved = self.save(typed)
            if not saved:
                return message
            now = plan_parts(self.plan())
            names = [p for p in mine if p in now]
            if not names:
                return message
            if len(names) < len(now):
                return self.finish_parts(names)
        _, said = quietly(mark_done_now, self.state, self.can_save, self.d, False)
        # The finished list after it is for the text screen.
        return said.split(tr("Finished lately:"))[0].strip()

    def finish_parts(self, names):
        """The things in today's plan with these words are finished; the rest
        stay today's. Another window may have changed the plan since these
        were ticked, so a name it no longer has changes nothing."""
        quietly(refresh, self.state, self.can_save)
        intent = self.state["intent"]
        if not intent or intent["date"] != self.iso:
            return tr("There is no plan to mark as done. Type a plan in the box "
                      "to set one.")
        every = plan_parts(intent["text"])
        if not names or any(name not in every for name in names):
            return tr("The other open window changed the plan, so its plan "
                      "is kept.")
        parts = [every.index(name) for name in names]
        base = copy.deepcopy(self.state)
        rest = finish_plan(self.state, intent["text"], self.d, parts)
        self.state["intent"] = dict(intent, text=rest) if rest else None
        saved, said = quietly(commit, self.state, base, self.can_save)
        if not saved:
            undo(self.state, base)
            return said or tr("Could not save that on this computer. The plan is still open.")
        return done_message(self.state, self.d, len(set(parts))) + (
            " " + tr("The rest is kept for today.") if rest else "")

    def forget(self, item):
        """Forget one finished plan, as text menu option 7 does."""
        quietly(refresh, self.state, self.can_save)
        if item not in self.state.get("finished", []):
            return tr("That plan was already forgotten. Nothing changed.")
        base = copy.deepcopy(self.state)
        self.state["finished"].remove(item)
        if self.state.get("done"):
            self.state["done"] -= 1
        saved, said = quietly(commit, self.state, base, self.can_save)
        if not saved:
            undo(self.state, base)
            return said or tr("Could not save that on this computer. Nothing changed.")
        return tr("Forgotten: ") + item["text"]

    def offer_due(self):
        """True when the window should ask once about the sign-in reminder."""
        return bool(launcher_place()[0] and not policy("DisableSignInLauncher")
                    and not plans_off() and not self.state.get("offered")
                    and not launcher_on())

    def drop_timed(self):
        """Remove the reminder at a set time, if there is one."""
        if self.state.get("remind_at") or task_on():
            quietly(reminder_task, None)
            self.setting("remind_at", None)

    def set_reminder(self, on):
        """Turn the reminder on at sign-in, or off. Returns the message.
        The reminder at a set time goes only once that worked, so a failed
        switch leaves the person with the reminder they had."""
        if not on:
            self.drop_timed()
        worked, said = quietly(remind, on)
        if worked and on:
            self.drop_timed()
        quietly(refresh, self.state, self.can_save)
        base = copy.deepcopy(self.state)
        self.state["offered"] = True
        quietly(commit, self.state, base, self.can_save)
        if not worked:
            return said
        if on and text_screen(self.state):
            # The text screen opens at sign-in whether or not there is a plan.
            return (tr("Done. hello-world will open once a day when you sign in.")
                    + " " + tr("To stop it, choose option 2 in the menu."))
        return (tr("Done. A reminder comes when you sign in, if there is a "
                   "plan to ask about.") if on else
                tr("Done. The sign-in reminder is off."))

    def set_due(self, due):
        """Give today's plan a due date (ISO), or none. Returns the message."""
        quietly(refresh, self.state, self.can_save)
        intent = self.state["intent"]
        if not intent:
            return tr("There is no plan to give a due date. Type a plan first.")
        base = copy.deepcopy(self.state)
        self.state["intent"] = {k: v for k, v in intent.items() if k != "due"}
        if due:
            self.state["intent"]["due"] = due
        saved, said = quietly(commit, self.state, base, self.can_save)
        if not saved:
            undo(self.state, base)
            return said or tr("Could not save that on this computer. Nothing changed.")
        return (tr("Done. {note}").format(note=due_note(self.state["intent"], self.d)) if due
                else tr("Done. The plan has no due date."))

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
        if text_screen(self.state):
            return tr("Done. hello-world opens at {at} each day.").format(
                at=at.lstrip("0"))
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
                # Today counts from the moment numbers are on.
                if key == "numbers" and self.iso in self.state["visits"]:
                    for count in ("opens", "run", "best_run"):
                        self.state.setdefault(count, 1)
        elif self.state.pop("text", None) is None:
            self.state["text"] = True
        saved, _ = quietly(commit, self.state, base, self.can_save)
        if not saved:
            undo(self.state, base)
        return saved

    def did_tip(self):
        """Count this person for the day's tip. Returns what to say."""
        message, _ = quietly(did_tip, self.state, self.can_save, self.d)
        self.tip_people = tip_count(self.d)
        return message

    def shared_switch(self):
        """Turn the shared count on or off. Returns what to say."""
        message = self.switch("shared", tr("Done. You'll see how many people did the tip."),
                              tr("Done. Nothing is sent, and no count shows."))
        self.setting("shared_asked", True)
        return message

    def switch(self, key, on_text, off_text):
        """Flip an on-or-off setting. Returns what to say."""
        if not self.toggle(key):
            return tr("Could not save that choice on this computer.")
        return on_text if self.state.get(key) else off_text


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
    THOUGHT_LABEL, THOUGHT, TIP_LABEL, TIP, TIP_COUNT, TIP_DONE = range(110, 116)
    PLAN_LABEL, PLAN, STATUS, OPTIONS, DID_IT = range(120, 125)
    TICK = 130  # to 139, one tick box for each thing in the plan
    HANDOFF_LABEL, HANDOFF, HANDOFF_EDIT, HANDOFF_KEEP, HANDOFF_LEAVE, HANDOFF_RULES = range(140, 146)
    SAVE, CLOSE = 1, 2  # IDOK and IDCANCEL, so Enter and Esc work

    def __init__(self, visit, message=None, keep=None):
        self.visit = visit
        self.message = message  # shown in the status line after a reopen
        # What was typed and ticked before a reopen, put back after it.
        self.keep = keep
        self.fresh = False  # a reopen draws the new plan, not what was typed
        self.parts = []
        self.reopened = None
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
        if handoff_on():
            lines = handoff_lines()
            para(self.HANDOFF_LABEL, lines[0], 2)
            para(self.HANDOFF, "\n".join(lines[1:]), 4)
            para(self.HANDOFF_RULES, tr("Everyone who uses this PC sees handoff "
                                        "notes. No patient or customer details. "
                                        "Not a safety or defect record.") + " "
                 + tr("Sign it if the next shift may need to ask you."), 2)
            add(edit, self.HANDOFF_EDIT, "", tab | 0x800000 | 0x80, m, 15)
            y += 18
            add(button, self.HANDOFF_KEEP, tr("&Keep until cleared"), tab | 0x3, m, 14, 120)
            add(button, self.HANDOFF_LEAVE, tr("&Leave note"), tab, m + w - 64, 16, 64)
            y += 24

        def ticks(parts):
            nonlocal y
            self.parts = parts
            for n, part in enumerate(parts):
                h = self.lines(part) * line
                # A tick box draws & as an underline, so it is doubled.
                add(button, self.TICK + n, part.replace("&", "&&"),
                    tab | 0x3 | 0x2000, m + 6, h,
                    w - 6)  # BS_AUTOCHECKBOX | BS_MULTILINE
                y += h + 2
            y += 4

        parts = plan_parts(v.followup) if v.followup else []
        since = tr("Your plan from {date}: ").format(date=long_date(
            datetime.date.fromisoformat(v.state["intent"]["date"]))) if v.followup else ""
        if len(parts) > 1:
            para(self.PLANNED, since.strip(), 2)
            para(self.ASK, tr("Tick the ones you did, then click Done."), 2)
            ticks(parts)
        elif v.followup:
            para(self.PLANNED, since + v.followup, 2)
            para(self.ASK, tr("Did you do it?"), 4)
        if v.followup:
            for n, (cid, label) in enumerate(((self.DONE, tr("&Done")),
                                              (self.NOT_YET, tr("&Not yet")),
                                              (self.SKIP, tr("S&kip")))):
                add(button, cid, label, tab, m + n * 70, 16, 64)
            y += 26
        if v.pair and not v.state.get("hide_thought"):
            para(self.THOUGHT_LABEL, tr("Thought for today:"), 1)
            para(self.THOUGHT, v.pair[0], 6)
        if v.pair:
            para(self.TIP_LABEL, tr("Try this today:"), 1)
            para(self.TIP, v.pair[1], 8)
            if v.tip_people is not None:
                para(self.TIP_COUNT, tr("People who did today's tip so far: {n}")
                     .format(n=v.tip_people), 2)
                if v.state.get("tip_day") != v.iso:
                    add(button, self.TIP_DONE, tr("I did this &tip"), tab, m, 16, 100)
                    y += 22
        if not plans_off():
            para(self.PLAN_LABEL, self.plan_label(), 2)
            add(edit, self.PLAN, v.plan(), tab | 0x800000 | 0x80, m, 15)
            y += 19
            today_parts = plan_parts(v.plan()) if v.plan() and not v.followup else []
            if len(today_parts) > 1:
                para(self.ASK, tr("Tick the ones you finish, then click Done."), 2)
                ticks(today_parts)
        due = due_note(v.state["intent"], v.d) if v.plan() or v.followup else ""
        add(static, self.STATUS, "" if plans_off() else due or tr(
            "A few things? Put ; between them."), text_style, m, 2 * line)
        y += 2 * line + 6
        add(button, self.OPTIONS, tr("&Options"), tab, m, 16, 64)
        right = m + w
        # Added left to right, which is the Tab order.
        if not plans_off():
            add(button, self.DID_IT, tr("&Done"), tab, right - 204, 16, 64)
            add(button, self.SAVE, tr("&Save"), tab | 1, right - 134, 16, 64)
            add(button, self.CLOSE, self.close_label(), tab, right - 64, 16, 64)
        else:
            add(button, self.CLOSE, tr("Close"), tab | 1, right - 64, 16, 64)
        return items, y + 26

    def plan_label(self):
        return (tr("Your plan for today: ").strip() if self.visit.plan() else
                tr("Next plan, if you want one:") if self.finished else
                tr("What do you want to get done today?"))

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
        if self.item(self.HANDOFF_EDIT):
            user.SendMessageW(self.item(self.HANDOFF_EDIT), 0xC5, MAX_PLAN, 0)  # EM_LIMITTEXT
        for cid in (self.STATUS, self.PLANNED):
            if self.item(cid):
                live_region(self.item(cid))
        # One Done at a time: while it asks about an earlier plan, its own.
        self.show(self.DID_IT, bool(self.visit.plan()) and not self.asking)
        if self.visit.followup:
            self.focus(self.DONE)
        else:
            self.focus_plan()
        if self.message:
            self.set_text(self.STATUS, self.message)
        if self.keep:
            typed, ticked = self.keep
            if typed and self.item(self.PLAN):
                self.set_text(self.PLAN, typed)
                self.focus_plan()
            for n, part in enumerate(self.parts):
                if part in ticked:
                    user.SendMessageW(self.item(self.TICK + n), 0xF1, 1, 0)  # BM_SETCHECK
        if CLOSE_WINDOW_AFTER:
            user.SetTimer(self.hwnd, 1, CLOSE_WINDOW_AFTER, None)

    def ticked(self):
        """The indexes of the ticked things."""
        return [n for n in range(len(self.parts))
                if self.user.SendMessageW(self.item(self.TICK + n), 0xF0, 0, 0)]  # BM_GETCHECK

    def command(self, cid):
        v = self.visit
        if cid in (self.DONE, self.NOT_YET, self.SKIP):
            ticks = self.ticked()
            # A tick missed by mistake must not finish everything.
            if (cid == self.DONE and self.item(self.TICK) and not ticks
                    and not self.confirm(tr("Mark all of them done?"))):
                return
            typed = self.typed()
            message = v.answer({self.DONE: "yes", self.NOT_YET: "no"}.get(cid, "skip"),
                               ticks if cid == self.DONE and ticks else None)
            if tidy(typed) and not v.followup and clean(typed) != v.plan():
                _, said, saved = v.save(typed)
                if said:
                    message += " " + said
            if v.followup:
                self.set_text(self.STATUS, message)
                return
            if len(plan_parts(v.plan())) > 1:
                # Today's plan of several things gets its own tick boxes.
                self.fresh = True
                self.reopen(message)
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
        elif cid == self.HANDOFF_LEAVE:
            import ctypes
            buffer = ctypes.create_unicode_buffer(MAX_PLAN + 2)
            self.user.GetWindowTextW(self.item(self.HANDOFF_EDIT), buffer, MAX_PLAN + 2)
            keep = bool(self.user.SendMessageW(self.item(self.HANDOFF_KEEP), 0xF0, 0, 0))
            message = leave_handoff(buffer.value, keep)
            self.fresh = True
            self.reopen(message)
        elif cid == self.TIP_DONE:
            self.set_text(self.STATUS, v.did_tip())
            if v.tip_people is not None:
                self.set_text(self.TIP_COUNT, tr("People who did today's tip so far: {n}")
                              .format(n=v.tip_people))
            self.show(self.TIP_DONE, False)
            self.focus_plan()
        elif cid == self.DID_IT:
            if self.parts and clean(self.typed()) in ("", v.plan()):
                names = [self.parts[n] for n in self.ticked()]
                if not names and not self.confirm(tr("Mark all of them done?")):
                    return
                self.fresh = True
                self.reopen(v.finish_parts(names or self.parts))
                return
            else:
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
            elif self.save_typed(redraw=True) is None:
                self.user.EndDialog(self.hwnd, 1)
        elif cid == self.CLOSE:
            if (self.item(self.PLAN) and any(c.isalpha() for c in self.typed())
                    and clean(self.typed()) != v.plan()
                    and self.confirm(tr("Save your plan before closing?"))
                    and self.save_typed() is False):
                return
            self.user.EndDialog(self.hwnd, 2)
        elif cid == self.OPTIONS:
            self.options()

    def save_typed(self, redraw=False):
        """Save the box. True when saved, False when refused (the window
        says why), None when there was nothing to save. With `redraw`, a plan
        of several things reopens the window to show its tick boxes."""
        v = self.visit
        typed = self.typed()
        command, _ = quietly(is_command, typed)
        earlier = ""
        if (self.asking and v.followup and tidy(typed) and not command
                and not is_same(typed) and clean(typed) != v.followup):
            # Typing a new plan instead of answering keeps the earlier one.
            earlier = v.followup
            typed = typed + "; " + earlier
        close, message, saved = v.save(typed)
        if close:
            return None
        if saved and earlier:
            message += " " + kept_note(plan_parts(earlier), v.plan())
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
            if redraw and (self.parts or len(plan_parts(v.plan())) > 1):
                self.fresh = True
                self.reopen(message)
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
        self.show(self.DID_IT, bool(self.visit.plan()) and not self.asking)

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
        switches = reminder_switches()
        for n, (key, label, _, _) in enumerate(switches):
            entries.append((checked if v.state.get(key) else 0, 20 + n, label))
        choice = self.popup(entries)
        if choice == 1:
            self.set_text(self.STATUS, v.set_reminder(True))
        elif 2 <= choice < 2 + len(REMINDER_TIMES):
            self.set_text(self.STATUS, v.reminder_at(REMINDER_TIMES[choice - 2]))
        elif 20 <= choice < 20 + len(switches):
            key, _, on_text, off_text = switches[choice - 20]
            self.set_text(self.STATUS, v.switch(key, on_text, off_text))

    def options(self):
        """A short menu, with the rest in four submenus."""
        v, checked, grayed = self.visit, 0x8, 0x1
        entries = []
        if launcher_place()[0] and not plans_off():
            on = reminder_on()
            entries.append(((checked if on else 0) | (
                grayed if policy("DisableSignInLauncher") and not on else 0),
                1, tr("Remind me when I sign in")))
            if not policy("DisableSignInLauncher"):
                entries.append((0, 9, tr("Reminder settings...")))
        entries.append((0, 20, tr("What the window shows...")))
        if not plans_off():
            entries.append((0, 21, tr("My plans...")))
        entries.append((0, 22, tr("My saved notes...")))
        if not policy("ForceEnglish"):
            entries.append((0, 8, tr("Language...")))
        if feedback_address():
            entries.append((0, 11, tr("Send feedback...")))
        if handoff_on() and shown_handoff():
            entries.append((0, 12, tr("Clear a handoff note...")))
        entries.append((0x800, 0, None))  # MF_SEPARATOR
        entries.append(((grayed if policy("UseTextScreen") else 0)
                        | (checked if text_screen(v.state) else 0), 3,
                        tr("Use the text screen")))
        entries.append((0, 4, tr("Open the text menu")))
        choice = self.popup(entries)
        if choice == 1:
            self.set_text(self.STATUS, v.set_reminder(not reminder_on()))
        elif choice == 9:
            self.reminder_settings()
        elif choice == 20:
            self.shows_menu()
        elif choice == 21:
            self.plans_menu()
        elif choice == 22:
            self.saved_menu()
        elif choice == 8:
            self.language_menu()
        elif choice == 11:
            send_feedback()
        elif choice == 12:
            notes = handoff_lines()[1:]
            picked = self.popup([(0, n, line[:80]) for n, line in enumerate(notes, 1)])
            if picked:
                self.fresh = True
                self.reopen(clear_handoff(picked))
        elif choice == 3:
            if reminder_on():
                self.inform(tr("At sign-in, this text screen now opens instead "
                               "of a notification."))
            if v.toggle("text"):
                open_console()
                self.user.EndDialog(self.hwnd, 2)
            else:
                self.set_text(self.STATUS, tr("Could not save that choice on "
                                              "this computer."))
        elif choice == 4:
            open_console("--menu")
            self.user.EndDialog(self.hwnd, 2)

    def reopen(self, message):
        """Draw the window again, so a change to what it shows shows now.
        What was typed and ticked comes back, unless `fresh` is set."""
        self.reopened = message
        typed = self.typed()
        self.keep = ("", set()) if self.fresh else (
            typed if clean(typed) != self.visit.plan() else "",
            {self.parts[n] for n in self.ticked()})
        self.user.EndDialog(self.hwnd, 2)

    def toggled(self, key, on_text, off_text):
        """Flip a setting and reopen the window to show it."""
        if not self.visit.toggle(key):
            self.set_text(self.STATUS, tr("Could not save that choice on this computer."))
            return
        on = bool(self.visit.state.get(key, key == "tips"))
        self.reopen(on_text if on else off_text)

    def shows_menu(self):
        v, checked, grayed = self.visit, 0x8, 0x1
        entries = [(checked if v.state.get("name") else 0, 10, tr("Greet me by name"))]
        if not policy("HideThoughtAndTip"):
            entries.append((checked if v.state.get("tips", True) else 0, 2,
                            tr("Show the thought and tip")))
            if v.state.get("tips", True):
                entries.append((0 if v.state.get("hide_thought") else checked, 16,
                                tr("Also show the thought")))
            if not org_content():
                entries.append(((checked if v.state.get("floor_tips") or policy("FloorTips")
                                 else 0) | (grayed if policy("FloorTips") else 0), 17,
                                tr("Tips for floor and shift work")))
        if not policy("HideDaysInARow"):
            entries.append((checked if v.state["streak"] else 0, 7,
                            tr("Show the days-in-a-row message")))
        if counts_server() and v.state.get("tips", True) and not policy("HideThoughtAndTip"):
            entries.append((checked if v.state.get("shared") else 0, 18,
                            tr("Show how many people did the tip")))
        choice = self.popup(entries)
        if choice == 18:
            self.reopen(v.shared_switch())
        if choice == 10:
            self.toggled("name", tr("Done. The greeting uses your first name."),
                         tr("Done. The greeting is back to the usual one."))
        elif choice == 2:
            self.toggled("tips", tr("Done. The thought and tip are on."),
                         tr("Done. The thought and tip are off."))
        elif choice == 16:
            self.toggled("hide_thought", tr("Done. The thought is off."),
                         tr("Done. The thought is on."))
        elif choice == 17:
            self.toggled("floor_tips", tr("Floor and shift tips are on."),
                         tr("Floor and shift tips are off."))
        elif choice == 7:
            self.toggled("streak", tr("Done. The days-in-a-row message is on."),
                         tr("Done. The days-in-a-row message is off."))

    def plans_menu(self):
        v, checked = self.visit, 0x8
        entries = [(0, 12, tr("This week...")),
                   (0, 13, tr("My numbers...")),
                   (0, 14, tr("Save my plans to a file"))]
        if v.plan():
            entries.insert(0, (0, 16, tr("Due date for my plan...")))
        if exported_files():
            entries.append((0, 11, tr("Delete the plans file I saved")))
        entries.append((checked if v.state.get("long_history") else 0, 15,
                        tr("Keep a longer history")))
        if v.state.get("finished"):
            entries.append((0, 18, tr("Forget a finished plan...")))
        choice = self.popup(entries)
        if choice == 12:
            self.inform(week_text(v.state, v.d))
        elif choice == 13:
            if not v.state.get("numbers") and self.confirm(tr(
                    "Keep my numbers from now on? They count the days you open "
                    "hello-world and the plans you finish, on this computer only.")):
                if not v.toggle("numbers"):
                    self.set_text(self.STATUS, tr("Could not save that choice on "
                                                  "this computer."))
                    return
            self.inform(numbers_text(v.state))
        elif choice == 14:
            self.set_text(self.STATUS, exported(export_plans(v.state)))
        elif choice == 16:
            days = due_choices(v.d)
            due = v.state["intent"].get("due") if v.state["intent"] else None
            when = self.popup([(0x8 if due == d.isoformat() else 0, 300 + n, long_date(d))
                               for n, d in enumerate(days)]
                              + [(0x8 if not due else 0, 299, tr("No due date"))])
            if when:
                self.set_text(self.STATUS, v.set_due(
                    None if when == 299 else days[when - 300].isoformat()))
                self.set_text(self.PLAN_LABEL, self.plan_label())
        elif choice == 11:
            if self.confirm(tr("Delete the plans file you saved?")):
                self.set_text(self.STATUS, delete_export())
        elif choice == 15:
            self.set_text(self.STATUS, v.switch(
                "long_history",
                tr("Done. Finished plans are kept for 90 days instead of 14."),
                tr("Done. Finished plans are kept for 14 days, as usual.")))
        elif choice == 18:
            items = newest_first(v.state["finished"])[:20]
            picked = self.popup([(0, 200 + n, tr("{date}: ").format(date=long_date(
                datetime.date.fromisoformat(i["date"]))) + i["text"])
                for n, i in enumerate(items)])
            if picked and self.confirm(tr("Forget this finished plan? {text}").format(
                    text=items[picked - 200]["text"])):
                self.set_text(self.STATUS, v.forget(items[picked - 200]))

    def saved_menu(self):
        v = self.visit
        entries = [(0, 5, tr("Show what is saved on this computer"))]
        if v.state.get("previous"):
            entries.append((0, 19, tr("Forget the earlier plan")))
        entries.append((0, 6, tr("Delete everything saved")))
        choice = self.popup(entries)
        if choice == 19:
            if self.confirm(tr("Forget the earlier plan? {text}").format(
                    text=v.state["previous"])):
                self.set_text(self.STATUS, tr("Done. The earlier plan is forgotten.")
                              if v.setting("previous", None) else
                              tr("Could not save that on this computer. Nothing changed."))
        elif choice == 5:
            self.inform(v.saved_summary())
        elif choice == 6:
            if self.confirm(tr("Delete all saved notes, dates and plans on this "
                               "computer?")):
                self.fresh = True
                self.reopen(v.delete_all())
                return
            else:
                self.set_text(self.STATUS, tr("Nothing was deleted."))

    def language_menu(self):
        v = self.visit
        codes = list(LANGUAGE_NAMES) + [None]
        current = v.state.get("lang")
        picked = self.popup([(0x8 if code == current else 0, 100 + n,
                              LANGUAGE_NAMES[code] if code else tr("Follow Windows"))
                             for n, code in enumerate(codes)])
        if picked:
            saved, _ = quietly(set_language, v.state, v.can_save, codes[picked - 100])
            if saved:
                global LANGUAGE_READ
                LANGUAGE_READ = False
                self.reopen("")
            else:
                self.set_text(self.STATUS, tr("Could not save that choice on this computer."))


# ==== Translations ====
# Each language is hello.<code>.json next to this file, with the English text
# as the keys of "text". A regional variant names its "base" language and
# holds only what differs: strings, and thoughts, tips and done lines by
# index. The installer copies and checks them like hello.py.


PLACEHOLDER = re.compile(r"\{(\w*)\}")


def language_fits(data):
    """True when a language has everything the screens read from it."""
    lists = ("days", "months", "thoughts", "tips", "done")
    return (isinstance(data.get("text"), dict) and isinstance(data.get("date"), str)
            and all(isinstance(data.get(k), tuple) and data[k]
                    and all(isinstance(x, str) for x in data[k]) for k in lists)
            and len(data["days"]) == 7 and len(data["months"]) == 12
            and isinstance(data.get("tips_floor", ("",)), tuple)
            and all(isinstance(x, str) for x in data.get("tips_floor", ("",)))
            and data.get("tips_floor", ("",)) != ()
            # The same {names} as the English, or showing it raises KeyError.
            and all(set(PLACEHOLDER.findall(k)) == set(PLACEHOLDER.findall(v))
                    for k, v in data["text"].items()))


def load_languages(folder=None):
    """Read every hello.<code>.json into LANGUAGES. A file that can't be read
    or doesn't fit is skipped, so that language shows English."""
    folder = folder or os.path.dirname(os.path.abspath(__file__))
    found, variants = {}, {}
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        names = []
    for name in names:
        code = name[len("hello."):-len(".json")]
        if not (name.startswith("hello.") and name.endswith(".json")
                and code in LANGUAGE_NAMES and code != "en"):
            continue
        try:
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or not all(
                    isinstance(k, str) and isinstance(v, str)
                    for k, v in (data.get("text") or {1: 1}).items()):
                continue
            if "base" in data:
                variants[code] = data
                continue
            language_data = {k: tuple(v) if isinstance(v, list) else v
                             for k, v in data.items()}
            if language_fits(language_data):
                found[code] = language_data
        except (OSError, ValueError, RecursionError, TypeError, AttributeError):
            continue
    for code, data in variants.items():
        try:
            base = found.get(data["base"])
            if not base:
                continue
            merged = dict(base, text={**base["text"], **data["text"]})
            for key in ("thoughts", "tips", "done", "tips_floor"):
                if key not in base:
                    continue
                changes = {int(i): v for i, v in data.get(key, {}).items()}
                if not all(isinstance(v, str) for v in changes.values()):
                    raise ValueError(key)
                merged[key] = tuple(changes.get(i, item) for i, item in enumerate(base[key]))
            if language_fits(merged):
                found[code] = merged
        except (ValueError, TypeError, AttributeError, KeyError):
            continue
    LANGUAGES.clear()
    LANGUAGES.update(found)


load_languages()

if __name__ == "__main__":
    sys.exit(main())
