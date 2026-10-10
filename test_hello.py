import atexit
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import re
import unittest

HELLO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hello.py")
_MADE = []


def mkdtemp():
    """A temp folder that is removed when the test run ends."""
    path = tempfile.mkdtemp(prefix="hello-test-")
    _MADE.append(path)
    return path


@atexit.register
def _remove_temp_folders():
    for path in _MADE:
        shutil.rmtree(path, ignore_errors=True)

# Imports hello.py, sets its test values from argv[2], and runs it with the
# remaining arguments. hello.py itself reads no test settings from anywhere.
LAUNCH = (
    "import importlib.util, json, sys\n"
    "spec = importlib.util.spec_from_file_location('hello', sys.argv[1])\n"
    "hello = importlib.util.module_from_spec(spec)\n"
    "spec.loader.exec_module(hello)\n"
    "for name, value in json.loads(sys.argv[2]).items():\n"
    "    setattr(hello, name, value)\n"
    "sys.argv = sys.argv[1:2] + sys.argv[3:]\n"
    "sys.exit(hello.main())\n"
)


def launch(args=(), prelude="", **values):
    # UTF-8 mode, because on Windows a child reads piped text in the console's
    # code page, which differs between PowerShell and Git Bash.
    return [sys.executable, "-X", "utf8", "-c", prelude + LAUNCH, HELLO,
            json.dumps(values), *args]


def run(args=(), text=None, day="2026-10-01", home=None, startup=None,
        policy=None, env=None, lang="en", count=True, lock="plain", extra=None):
    """Run hello.py with its own data folder. text is typed at the prompts.

    Without text, stdin is the null device, so the result doesn't depend on
    what the test runner's own stdin is.
    """
    home = home or mkdtemp()
    # "" means no Startup folder, so on Windows a test never writes the real
    # one. The sign-in offer then appears only where a test asks for it.
    values = {"TODAY": day, "HOME": home,
              "STARTUP_DIR": "" if startup is None else startup,
              "FORCE_INTERACTIVE": text is not None,
              # Policies come from here, never from the real registry.
              "POLICY": policy or {},
              "LANGUAGE": lang,
              # The done count is kept only with My numbers on; most tests
              # check it, so they keep it.
              "COUNT_ALWAYS": count,
              # Never the real Task Scheduler.
              "TASKS": [],
              # Plain notes, so tests can read the file; the lock has its own.
              "LOCK": lock, **(extra or {})}
    stdin = {"input": text} if text is not None else {"stdin": subprocess.DEVNULL}
    p = subprocess.run(launch(args, **values), capture_output=True,
                       encoding="utf-8", env=env, **stdin)
    p.home = home
    return p


def notes(home):
    with open(os.path.join(home, "notes.json")) as f:
        return json.load(f)


def dead_pipe(args=(), dead_stderr=False):
    # A pipe with its read end closed makes every write to it fail.
    r, w = os.pipe()
    os.close(r)
    try:
        return subprocess.run(launch(args, HOME=mkdtemp()), stdout=w,
                              stderr=w if dead_stderr else subprocess.PIPE,
                              stdin=subprocess.DEVNULL)
    finally:
        os.close(w)


def test_plain_prints_only_the_greeting():
    p = run(["--plain"])
    assert (p.returncode, p.stdout) == (0, "Hello, world!\n")
    assert not os.path.exists(os.path.join(p.home, "notes.json"))


def test_first_run_welcomes_and_saves_the_plan():
    p = run(text="Send the invoice\n\n")
    assert p.returncode == 0
    lines = p.stdout.splitlines()
    assert lines[0] == "Hello, world!"
    assert lines[1] == "Thursday, 1 October 2026"
    assert "Welcome." in p.stdout and "never sent anywhere" in p.stdout
    assert "Thought for today:" in p.stdout and "Try this today:" in p.stdout
    saved = notes(p.home)
    assert saved["visits"] == ["2026-10-01"]
    assert saved["intent"] == {"text": "Send the invoice", "date": "2026-10-01"}


def test_output_is_plain_ascii_and_short():
    p = run(text="\n\n")
    assert p.stdout.isascii()
    assert all(len(line) <= 72 for line in p.stdout.splitlines() if "> " not in line)


def test_no_prompts_and_no_waiting_without_a_person():
    # stdin is the null device, which Windows also reports as a terminal
    p = run()
    assert p.returncode == 0 and "> " not in p.stdout
    assert p.stdout.startswith("Hello, world!")
    # nothing is recorded, so the next real visit still gets its questions
    assert not os.path.exists(os.path.join(p.home, "notes.json"))


def test_hello_variables_in_the_environment_are_ignored():
    home = mkdtemp()
    other = mkdtemp()
    env = dict(os.environ, HELLO_HOME=home, HELLO_TODAY="2000-01-01",
               HELLO_INTERACTIVE="1", HOME=other, LOCALAPPDATA=other,
               APPDATA=other, XDG_DATA_HOME=other)
    p = subprocess.run([sys.executable, HELLO, "--stats"], capture_output=True,
                       text=True, stdin=subprocess.DEVNULL, env=env)
    assert p.returncode == 0 and home not in p.stdout
    assert "2000" not in p.stdout
    assert not os.listdir(home)


def test_other_errors_are_not_reported_as_a_dead_stdout():
    p = run(day="not a date")
    assert p.returncode == 1
    assert "something went wrong (ValueError)" in p.stderr
    assert "cannot write to stdout" not in p.stderr


def test_opening_again_the_same_day_asks_nothing_new():
    first = run(text="Send the invoice\n\n")
    second = run(text="\n", home=first.home)
    assert "What is one thing" not in second.stdout
    assert "Your plan for today: Send the invoice" in second.stdout
    assert notes(first.home)["visits"] == ["2026-10-01"]


def test_next_day_follow_up_done():
    first = run(text="Send the invoice\n\n")
    p = run(text="y\nCall back\n\n", day="2026-10-02", home=first.home)
    assert "Yesterday you planned: Send the invoice" in p.stdout
    assert notes(first.home)["intent"]["text"] == "Call back"
    # With the days-in-a-row message off, only the latest date is kept.
    assert notes(first.home)["visits"] == ["2026-10-02"]


def test_next_day_not_done_can_be_kept():
    first = run(text="Send the invoice\n\n")
    p = run(text="n\ny\n\n", day="2026-10-02", home=first.home)
    assert "What is one thing" not in p.stdout
    assert notes(first.home)["intent"] == {"text": "Send the invoice",
                                           "date": "2026-10-02",
                                           "since": "2026-10-01"}


def test_in_a_row_line_appears_at_milestones_only():
    home = mkdtemp()
    run(["--streak", "on"], home=home)
    outs = [run(text="\n\n", day=f"2026-10-0{n}", home=home).stdout
            for n in range(1, 8)]
    shown = [n for n, out in enumerate(outs, 1) if "in a row" in out]
    assert shown == [3, 7]
    assert "3 days in a row" in outs[2]
    home = mkdtemp()
    run(["--streak", "on"], home=home)
    for n in (1, 2):
        run(text="\n\n", day=f"2026-10-0{n}", home=home)
    run(["--streak", "off"], home=home)
    assert "in a row" not in run(text="\n\n", day="2026-10-03", home=home).stdout


def test_the_days_in_a_row_message_is_off_until_turned_on_and_keeps_one_date():
    home = mkdtemp()
    outs = [run(text="\n\n", day=f"2026-10-0{n}", home=home).stdout
            for n in range(1, 4)]
    assert not any("in a row" in out for out in outs)
    saved = notes(home)
    assert saved["streak"] is False and saved["visits"] == ["2026-10-03"]
    # A file from before 1.29.0 saved true, and keeps it.
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["2026-10-01", "2026-10-02"], "streak": True}, f)
    assert "3 days in a row" in run(text="\n\n", day="2026-10-03", home=home).stdout


def test_streak_option_exit_codes():
    assert run(["--streak", "off"]).returncode == 0
    blocker = tempfile.NamedTemporaryFile()
    bad = run(["--streak", "off"], home=os.path.join(blocker.name, "sub"))
    assert bad.returncode == 1 and "Could not save" in bad.stdout


def test_remind_exit_code_follows_the_result():
    startup = mkdtemp()
    assert run(["--remind", "on"], startup=startup).returncode == 0
    assert run(["--remind", "off"], startup=startup).returncode == 0


def test_p_at_the_last_prompt_sets_the_plan():
    home = mkdtemp()
    run(text="\np\nWrite the report\n", home=home)
    assert notes(home)["intent"]["text"] == "Write the report"


def test_a_notes_file_with_a_byte_order_mark_is_read_not_moved_aside():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w", encoding="utf-8-sig") as f:
        json.dump({"visits": ["2026-09-30"], "intent": None, "streak": True}, f)
    run(text="\n\n", home=home)
    assert not os.path.exists(os.path.join(home, "notes.json.bak"))
    assert notes(home)["visits"] == ["2026-09-30", "2026-10-01"]


def test_thought_and_tip_never_repeat_each_other_on_one_screen():
    import hello
    for i in range(len(hello.TIPS)):
        t = hello.TIPS[i].lower()
        h = hello.THOUGHTS[(i + 37) % len(hello.THOUGHTS)].lower()
        assert not ("glass of water" in t and "glass of water" in h)


def test_welcome_back_after_a_long_gap_and_no_shaming():
    home = mkdtemp()
    run(text="\n\n", home=home)
    p = run(text="\n\n", day="2026-10-20", home=home)
    assert "Welcome back" in p.stdout
    for word in ("missed", "lost", "broke", "streak"):
        assert word not in p.stdout.lower()


def test_content_changes_from_day_to_day():
    a = run(day="2026-10-01").stdout
    b = run(day="2026-10-02").stdout
    assert a.split("Thought for today:")[1] != b.split("Thought for today:")[1]


def test_damaged_notes_file_gives_a_fresh_start():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        f.write('{"visits": [1, "nope"], "intent": 5')
    p = run(text="\n\n", home=home)
    assert p.returncode == 0 and "Welcome." in p.stdout
    assert notes(home)["visits"] == ["2026-10-01"]


def test_unsavable_notes_still_greet():
    blocker = tempfile.NamedTemporaryFile()  # a file where the folder should be
    p = run(text="\n\n", home=os.path.join(blocker.name, "sub"))
    assert p.returncode == 0 and "could not be saved" in p.stdout
    assert p.stdout.startswith("Hello, world!")


def test_non_english_plan_text_is_kept():
    p = run(text="Envoyer la facture \u00e9t\u00e9\n\n")
    assert notes(p.home)["intent"]["text"] == "Envoyer la facture \u00e9t\u00e9"


def test_stats_and_where_show_the_saved_file():
    first = run(text="Send the invoice\n\n")
    p = run(["--stats"], home=first.home)
    assert first.home in p.stdout and "Send the invoice" in p.stdout


def test_reset_deletes_after_confirmation():
    first = run(text="Send the invoice\n\n")
    run(["--reset"], text="n\n", home=first.home)
    assert os.path.exists(os.path.join(first.home, "notes.json"))
    run(["--reset"], text="y\n", home=first.home)
    # Only the marker that tells other windows the notes were deleted is left.
    saved = notes(first.home)
    assert saved["intent"] is None and saved["visits"] == [] and saved["epoch"]
    assert run(["--reset"], home=first.home).returncode == 1


def test_menu_shows_saved_data_and_toggles_the_in_a_row_line():
    first = run(text="Send the invoice\n\n")
    p = run(text="y\nBuy milk\nm\n1\n\n3\n\n", home=first.home, day="2026-10-02")
    assert "Options" in p.stdout and "Buy milk" in p.stdout
    assert notes(first.home)["streak"] is True


def test_reminder_writes_and_removes_only_the_launcher():
    startup = mkdtemp()
    path = os.path.join(startup, "hello-world-daily.cmd")
    run(["--remind", "on"], startup=startup)
    with open(path) as f:
        text = f.read()
    assert text.startswith("@echo off") and text.rstrip().endswith("--startup")
    assert "hello.py" in text and "hello.cmd" not in text
    run(["--remind", "off"], startup=startup)
    assert not os.path.exists(path)


def test_startup_run_is_silent_if_already_opened_today():
    first = run(text="\n\n")
    p = run(["--startup"], text="\n", home=first.home)
    assert p.returncode == 0 and p.stdout == ""


def test_unknown_option_exits_2_and_shows_the_options():
    p = run(["--nope"])
    assert p.returncode == 2 and "--plain" in p.stdout


def test_help_in_the_usual_spellings():
    for arg in ("--help", "-h", "/?", "-?", "--HELP"):
        p = run([arg])
        assert p.returncode == 0 and "--plain" in p.stdout, arg
    assert "!" not in run(["--help"]).stdout


def test_follow_up_keeps_the_plan_unless_the_answer_is_clear():
    first = run(text="Book travel\n\n")
    run(text="\n\n\n", day="2026-10-02", home=first.home)  # Enter skips
    assert notes(first.home)["intent"]["text"] == "Book travel"
    run(text="maybe\n\n\n", day="2026-10-03", home=first.home)
    assert notes(first.home)["intent"]["text"] == "Book travel"


def test_enter_at_keep_for_today_keeps_the_plan_and_n_drops_it():
    first = run(text="Book travel\n\n")
    run(text="n\n\n\n", day="2026-10-02", home=first.home)  # Enter at keep
    assert notes(first.home)["intent"] == {"text": "Book travel",
                                           "date": "2026-10-02",
                                           "since": "2026-10-01"}
    run(text="n\nn\n\n", day="2026-10-03", home=first.home)
    assert notes(first.home)["intent"] is None


def test_menu_sets_or_changes_todays_plan():
    first = run(text="\n\n")  # skipped the plan on the first visit
    run(text="m\n6\nCall the bank\n\n", home=first.home)
    assert notes(first.home)["intent"] == {"text": "Call the bank",
                                           "date": "2026-10-01"}
    run(text="m\n6\n\n\n", home=first.home)  # Enter keeps it
    assert notes(first.home)["intent"]["text"] == "Call the bank"


def test_reset_also_deletes_backup_and_temp_copies():
    first = run(text="Send the invoice\n\n")
    for name in ("notes.json.bak", "notes.json.bak2", "notes.json.123.tmp"):
        with open(os.path.join(first.home, name), "w") as f:
            f.write("old plan")
    run(["--reset"], text="y\n", home=first.home)
    # notes.lock is the empty lock file; it holds nothing.
    assert sorted(os.listdir(first.home)) == ["notes.json", "notes.lock"]
    assert os.path.getsize(os.path.join(first.home, "notes.lock")) == 0
    assert "Send the invoice" not in json.dumps(notes(first.home))


def test_menu_does_not_save_over_a_file_it_could_not_read():
    home = mkdtemp()
    os.mkdir(os.path.join(home, "notes.json"))  # opening it fails
    p = run(text="\nm\n3\n6\nCall the bank\n\n", home=home)
    assert p.stdout.count("Could not save") == 2
    assert os.path.isdir(os.path.join(home, "notes.json"))


def test_friendly_yes_words_count():
    for word in ("yep", "Yes!", "done", "ya", "ok", "Okay.", "did it", "yup"):
        first = run(text="Book travel\n\n")
        p = run(text=word + "\n\n\n", day="2026-10-02", home=first.home)
        assert "Yesterday you planned: Book travel" in p.stdout
        assert notes(first.home)["intent"] is None, word


def test_a_hostile_notes_file_cannot_write_controls_to_the_screen():
    home = mkdtemp()
    bad = {"visits": ["2026-09-30"],
           "intent": {"text": "\x1b[31mEVIL\r\nFAKE", "date": "2026-09-30"}}
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump(bad, f)
    p = run(text="y\n\n\n", home=home)
    assert "\x1b" not in p.stdout and "\r" not in p.stdout
    assert "Yesterday you planned: [31mEVIL FAKE" in p.stdout
    assert "\x1b" not in run(["--stats"], home=home).stdout


def test_pasted_tabs_and_odd_spaces_become_spaces():
    p = run(text="call\tBob\u00a0now\n\n")
    assert notes(p.home)["intent"]["text"] == "call Bob now"


def test_very_deep_json_gives_a_fresh_start_and_keeps_a_copy():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        f.write("[" * 200000)
    p = run(text="\n\n", home=home)
    assert p.returncode == 0 and "Welcome." in p.stdout
    assert os.path.exists(os.path.join(home, "notes.json.bak"))


def test_a_damaged_file_is_kept_as_a_backup():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        f.write('{"visits":["2026-10-0')
    run(text="\n\n", home=home)
    with open(os.path.join(home, "notes.json.bak")) as f:
        assert f.read() == '{"visits":["2026-10-0'


def test_a_bad_plan_date_does_not_turn_the_in_a_row_line_back_on():
    home = mkdtemp()
    bad = {"visits": ["2026-10-01", "2026-10-02"],
           "intent": {"text": "x", "date": "junk"}, "streak": False}
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump(bad, f)
    p = run(text="\n\n", day="2026-10-03", home=home)
    assert "in a row" not in p.stdout
    assert notes(home)["streak"] is False


def test_odd_date_spellings_are_normalised():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["20261001"], "intent": None}, f)
    run(text="\n\n", home=home)
    assert notes(home)["visits"] == ["2026-10-01"]


def test_long_plans_wrap_within_72_columns():
    first = run(text="word " * 24 + "\n\n")
    p = run(text="\n\n\n", day="2026-10-02", home=first.home)
    assert all(len(x) <= 72 for x in p.stdout.splitlines() if "> " not in x)


def test_a_plan_dated_in_the_future_becomes_todays_plan():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["2026-12-01"],
                   "intent": {"text": "Pay rent", "date": "2026-12-01"}}, f)
    p = run(text="\n", day="2026-10-04", home=home)
    assert "Your plan for today: Pay rent" in p.stdout


def test_dead_stdout_exits_1_with_one_line_on_stderr():
    for args in ([], ["--plain"]):
        p = dead_pipe(args)
        assert p.returncode == 1
        # bytes, since a localized OS error after the prefix may not be UTF-8
        assert p.stderr.startswith(b"hello.py: cannot write to stdout:")
        assert len(p.stderr.splitlines()) == 1


def test_dead_stdout_and_stderr_exits_1():
    assert dead_pipe(dead_stderr=True).returncode == 1


def test_closed_stdout_exits_1():
    if os.name != "posix":
        raise unittest.SkipTest("needs preexec_fn, posix only")
    p = subprocess.run(launch(HOME=mkdtemp()), stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                       preexec_fn=lambda: os.close(1))
    assert p.returncode == 1
    assert p.stderr.startswith(b"hello.py: cannot write to stdout:")


def test_stdout_closed_after_start_exits_1():
    # sys.stdout.close() makes print() raise ValueError, not OSError
    p = subprocess.run(launch(prelude="sys_ = __import__('sys'); sys_.stdout.close()\n",
                              HOME=mkdtemp()),
                       stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    assert p.returncode == 1
    assert p.stderr.startswith(b"hello.py: cannot write to stdout:")


def _load_hello(day="2026-10-01"):
    import importlib.util
    spec = importlib.util.spec_from_file_location("hello_mod", HELLO)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.TODAY = day
    mod.STARTUP_DIR = ""  # never the real Startup folder
    mod.POLICY = {}  # never the real policy registry
    mod.LANGUAGE = "en"
    mod.COUNT_ALWAYS = True
    mod.LOCK = "plain"
    return mod


def test_visits_dated_after_today_are_dropped_from_the_file():
    home = mkdtemp()
    path = os.path.join(home, "notes.json")
    with open(path, "w") as f:
        json.dump({"visits": ["2026-09-30", "2030-01-01"], "streak": True}, f)
    p = run(text="\n", day="2026-10-01", home=home)
    assert "opened this" not in p.stdout
    with open(path) as f:
        saved = json.load(f)["visits"]
    assert saved == ["2026-09-30", "2026-10-01"]


def test_a_plan_of_only_joiners_is_empty_and_a_long_plan_says_it_was_cut():
    hello = _load_hello()
    assert hello.clean("\u200d \u200c") == ""
    p = run(text="x" * 410 + "\n\n")
    assert "Shortened to 400 characters." in p.stdout


def test_a_second_damaged_file_does_not_overwrite_the_first_backup():
    hello = _load_hello()
    hello.HOME = mkdtemp()
    os.makedirs(os.path.dirname(hello.data_file()), exist_ok=True)
    for text in ("first", "second"):
        with open(hello.data_file(), "w") as f:
            f.write(text)
        hello.load()
    with open(hello.data_file() + ".bak") as f:
        assert f.read() == "first"
    with open(hello.data_file() + ".bak2") as f:
        assert f.read() == "second"


def test_a_decode_error_at_the_prompt_counts_as_no_answer():
    hello = _load_hello()
    hello.FORCE_INTERACTIVE = True

    def bad(_prompt):
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad")
    hello.input = bad
    assert hello.ask("> ") is None


def test_joiner_characters_survive_cleaning():
    hello = _load_hello()
    assert hello.clean("a\u200cb\u200dc") == "a\u200cb\u200dc"
    assert hello.clean("a\u202eb") == "ab"


def test_visits_dated_after_today_are_dropped_on_load():
    hello = _load_hello()
    home = mkdtemp()
    hello.HOME = home
    os.makedirs(os.path.dirname(hello.data_file()), exist_ok=True)
    with open(hello.data_file(), "w", encoding="utf-8") as f:
        json.dump({"visits": ["2026-09-30", "2030-01-01"], "streak": True}, f)
    state, _ = hello.load()
    assert state["visits"] == ["2026-09-30"]


def test_powershell_scripts_are_ascii():
    root = os.path.dirname(HELLO)
    for name in ("install.ps1", "uninstall.ps1"):
        with open(os.path.join(root, name), "rb") as f:
            f.read().decode("ascii")


def test_documented_tag_matches_version():
    root = os.path.dirname(HELLO)
    with open(os.path.join(root, "VERSION")) as f:
        tag = "$tag = 'v" + f.read().strip() + "'"
    for name in ("README.md", "install.ps1"):
        with open(os.path.join(root, name), encoding="utf-8") as f:
            assert tag in f.read(), name


def test_failed_reset_exits_1_and_declining_exits_0():
    first = run(text="Send the invoice\n\n")
    assert run(["--reset"], text="n\n", home=first.home).returncode == 0
    home = mkdtemp()
    os.mkdir(os.path.join(home, "notes.json"))  # a delete of this fails
    p = run(["--reset"], text="y\n", home=home)
    assert p.returncode == 1 and "Could not delete" in p.stdout


def test_reset_still_deletes_the_other_copies_when_one_delete_fails():
    home = mkdtemp()
    os.mkdir(os.path.join(home, "notes.json"))  # a delete of this fails
    bak = os.path.join(home, "notes.json.bak")
    with open(bak, "w") as f:
        f.write("old plan")
    p = run(["--reset"], text="y\n", home=home)
    assert p.returncode == 1 and not os.path.exists(bak)


def test_a_repaired_file_is_announced():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        f.write("{")
    p = run(text="\n", home=home)
    assert "set it" in p.stdout and "notes.json.bak" in p.stdout
    assert all(len(line) <= 72 for line in p.stdout.splitlines() if "> " not in line)
    assert os.path.exists(os.path.join(home, "notes.json.bak"))


def test_stats_does_not_move_a_damaged_file():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        f.write('{"visits":["2026-10-0')
    p = run(["--stats"], home=home)
    assert p.returncode == 1 and "damaged" in p.stdout
    assert os.path.exists(os.path.join(home, "notes.json"))
    assert not os.path.exists(os.path.join(home, "notes.json.bak"))


def test_cut_plan_has_no_trailing_space():
    import hello
    n = hello.MAX_PLAN
    assert hello.clean("a" * (n - 1) + " b") == "a" * (n - 1)


def test_second_damaged_file_notice_names_the_real_backup():
    home = mkdtemp()
    for _ in range(2):
        with open(os.path.join(home, "notes.json"), "w") as f:
            f.write("{")
        p = run(text="\n", home=home)
    assert "notes.json.bak2" in p.stdout and home in p.stdout
    assert "\n\nHello, world!" in p.stdout


def test_first_run_explains_tomorrow_and_confirms_the_plan():
    p = run(text="write the report\n\n")
    assert "asks next time" in p.stdout
    assert "Saved. Type done when you finish it, or it asks next time you open this." in p.stdout
    assert "Type done, plan or menu" in p.stdout


def test_sign_in_offer_is_made_once_on_the_second_visit():
    home, startup = mkdtemp(), mkdtemp()
    run(text="\n\n", home=home, startup=startup, day="2026-10-01")
    p = run(text="\nn\n\n", home=home, startup=startup, day="2026-10-02")
    assert "when you sign in so it can ask" in p.stdout
    assert notes(home)["offered"] is True
    p = run(text="\n\n", home=home, startup=startup, day="2026-10-03")
    assert "when you sign in so it can ask" not in p.stdout
    assert os.listdir(startup) == []


def test_sign_in_offer_yes_turns_it_on():
    home, startup = mkdtemp(), mkdtemp()
    run(text="\n\n", home=home, startup=startup, day="2026-10-01")
    run(text="\ny\n\n", home=home, startup=startup, day="2026-10-02")
    assert os.listdir(startup) == ["hello-world-daily.cmd"]


def test_unknown_input_is_named_and_outcomes_are_echoed():
    p = run(text="\nbanana\n\n")
    assert 'Sorry, "banana" is not one of the choices.' in p.stdout
    assert "Type plan or menu, or press Enter to close." in p.stdout
    p = run(["--nope"])
    assert "Unknown option: --nope" in p.stdout and p.returncode == 2
    p = run(["--remind"])
    assert "needs on or off" in p.stdout


def test_existing_user_with_many_visits_is_offered_the_reminder():
    home, startup = mkdtemp(), mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["2026-09-25", "2026-09-26", "2026-09-28",
                              "2026-09-29", "2026-09-30"]}, f)
    p = run(text="\ny\n\n", home=home, startup=startup)
    assert "when you sign in so it can ask" in p.stdout
    assert os.listdir(startup) == ["hello-world-daily.cmd"]


def test_offer_comes_right_after_the_first_plan():
    home, startup = mkdtemp(), mkdtemp()
    p = run(text="Send the invoice\ny\n\n", home=home, startup=startup)
    assert p.stdout.index("Saved. Type done") < p.stdout.index("so it can ask")
    assert os.listdir(startup) == ["hello-world-daily.cmd"]



def test_the_sign_in_question_is_asked_once():
    home, startup = mkdtemp(), mkdtemp()
    run(text="Plan one\n\n\n\n", home=home, startup=startup, day="2026-10-01")
    saved = notes(home)
    assert saved["offered"] is True and saved["offer_skips"] == 1
    p = run(text="\n\n\n", home=home, startup=startup, day="2026-10-02")
    assert "so it can ask" not in p.stdout
    assert os.listdir(startup) == []


def test_done_does_not_turn_on_the_sign_in_reminder():
    home, startup = mkdtemp(), mkdtemp()
    run(text="Plan one\ndone\n\n", home=home, startup=startup)
    assert os.listdir(startup) == []


def test_plan_typed_on_a_later_day_is_confirmed():
    first = run(text="\n\n")
    p = run(text="Write the report\n\n", home=first.home, day="2026-10-02")
    assert "Saved. Type done when you finish it, or it asks next time you open this." in p.stdout


def test_result_of_plan_command_stays_until_enter():
    p = run(text="\nplan\nWrite the report\n\n")
    assert "Saved. Type done when you finish it" in p.stdout
    # The same prompt comes back, so the result stays on screen and the
    # person can go on, instead of any typed word closing the window.
    after = p.stdout.split("Saved. Type done when you finish it")[1]
    assert "Type done, plan or menu, or Enter to close >" in after


def test_wrong_answers_never_close_the_window_and_the_choices_are_listed():
    p = run(text="\nbanana\napple\nplan\nWrite it\n\n\n")
    assert p.stdout.count("not one of the choices") == 2
    assert "Closing now" not in p.stdout
    assert "Saved. Type done when you finish it" in p.stdout


def test_quit_and_help_words_work_at_the_last_prompt():
    for word in ("q", "quit", "exit"):
        p = run(text=f"\n{word}\n")
        assert "not one of the choices" not in p.stdout, word
    p = run(text="\n?\n5\n\n")
    assert "Words you can type at the last prompt" in p.stdout



def test_same_brings_back_an_unfinished_plan_but_never_a_finished_one():
    first = run(text="Send the invoice\n\n")
    run(text="n\nn\n\n", home=first.home, day="2026-10-02")  # cleared, not done
    assert notes(first.home)["previous"] == "Send the invoice"
    p = run(text="same\n\n", home=first.home, day="2026-10-03")
    assert "Earlier plan: Send the invoice" in p.stdout
    assert "Type same to reuse it" in p.stdout
    assert notes(first.home)["intent"]["text"] == "Send the invoice"
    # Finishing it means it is no longer offered back.
    run(text="y\n\n\n", home=first.home, day="2026-10-04")
    p = run(text="\n\n", home=first.home, day="2026-10-05")
    assert "Earlier plan" not in p.stdout
    assert "previous" not in notes(first.home)


def test_plans_done_are_counted_and_shown_privately():
    first = run(text="One\n\n")
    run(text="y\nTwo\n\n", home=first.home, day="2026-10-02")
    p = run(text="y\n\n", home=first.home, day="2026-10-03")
    # No running tally after a finish; the count is only in option 1.
    assert "done so far" not in p.stdout
    p = run(text="m\n1\n\n\n", home=first.home, day="2026-10-03")
    assert "Times you marked a plan done: 2" in p.stdout
    assert "IT staff, could read it" in p.stdout
    assert "Only you can see this" not in p.stdout
    assert '"visits"' not in p.stdout
    p = run(text="m\n1\nfull\n\n\n", home=first.home, day="2026-10-03")
    assert '"visits"' in p.stdout


def test_an_unanswered_plan_is_still_shown_when_reopened_the_same_day():
    first = run(text="Book travel\n\n")
    run(text="\n\n\n", home=first.home, day="2026-10-02")
    p = run(text="\n", home=first.home, day="2026-10-02")
    assert "Still open since" in p.stdout and "Book travel" in p.stdout


def test_an_expired_plan_is_announced_and_kept_as_same():
    first = run(text="Old plan\n\n")
    p = run(text="same\n\n", home=first.home, day="2026-10-30")
    assert "over two weeks ago was put away" in p.stdout
    assert notes(first.home)["intent"]["text"] == "Old plan"


def test_not_yet_at_the_sign_in_offer_is_not_a_final_no():
    home, startup = mkdtemp(), mkdtemp()
    run(text="Plan\nnot yet\n\n", home=home, startup=startup)
    assert "offered" not in notes(home)


def test_saved_file_is_private_on_posix():
    if os.name != "posix":
        raise unittest.SkipTest("POSIX permissions")
    p = run(text="Plan\n\n")
    mode = os.stat(os.path.join(p.home, "notes.json")).st_mode & 0o777
    assert mode == 0o600, oct(mode)


def test_delete_needs_a_clear_yes():
    first = run(text="Plan\n\n")
    run(["--reset"], text="done\n", home=first.home)
    assert os.path.exists(os.path.join(first.home, "notes.json"))


def test_menu_toggles_say_the_action_and_menu_help_is_for_employees():
    p = run(text="\nm\n5\n\n")
    assert "Turn on: reminder when you sign in (now off)" in p.stdout
    assert "Words you can type at the last prompt" in p.stdout
    assert "hello.cmd" not in p.stdout.split("Words you can type")[1]


def test_help_says_where_hello_cmd_is():
    p = run(["--help"])
    assert "hello.cmd is in this folder:" in p.stdout


def test_hyphenated_words_in_content_do_not_split():
    mod = _load_hello()
    assert mod.indent("x " * 33 + "ten-minute").count("-") == 1
    assert "ten-\n" not in mod.indent("a " * 31 + "ten-minute start")


def test_help_lines_fit_72_columns():
    assert all(len(line) <= 72 for line in run(["--help"]).stdout.splitlines())



def test_done_at_the_last_prompt_counts_the_plan_the_same_day():
    first = run(text="Send the invoice\ndone\n\n")
    assert "Type done, plan or menu" in first.stdout
    assert "Type the next plan" in first.stdout
    saved = notes(first.home)
    assert saved["intent"] is None and saved["done"] == 1
    assert "previous" not in saved
    # Tomorrow it neither asks about it nor offers it back.
    p = run(text="\n\n", home=first.home, day="2026-10-02")
    assert "Did you do it?" not in p.stdout
    assert "Earlier plan" not in p.stdout


def test_after_done_the_next_plan_is_asked_in_the_same_session():
    p = run(text="Send the invoice\ndone\nCall the bank\n\n")
    saved = notes(p.home)
    assert saved["done"] == 1 and "previous" not in saved
    assert saved["intent"]["text"] == "Call the bank"


def test_after_done_one_enter_really_closes():
    p = run(text="Send the invoice\ndone\n\n")
    assert "Closing." in p.stdout and "tomorrow" not in p.stdout.split("Closing")[1]
    # The last prompt is shown once before done and never again.
    assert p.stdout.count("or menu, or Enter to close > ") == 1
    assert notes(p.home)["intent"] is None and notes(p.home)["done"] == 1


def test_plan_with_no_plan_to_finish_does_not_close_the_window():
    p = run(text="\ndone\nplan\nWrite it\n\n")
    assert "There is no plan to mark as done." in p.stdout
    assert notes(p.home)["intent"]["text"] == "Write it"


def test_command_words_are_not_saved_as_the_plan():
    p = run(text="done\n\n")
    assert "looks like a command" in p.stdout and "at the last prompt" in p.stdout
    assert notes(p.home)["intent"] is None
    # menu there opens the menu instead of saying where it lives.
    p = run(text="menu\n6\nWrite it\n\n\n")
    assert "Options" in p.stdout and "looks like a command" not in p.stdout
    assert notes(p.home)["intent"]["text"] == "Write it"
    p = run(text="\nplan\nmenu\n\n")
    assert "Type your plan, or press Enter to go back." in " ".join(p.stdout.split())
    assert notes(p.home)["intent"] is None


def test_declining_to_plan_is_not_lectured():
    for word in ("no", "none", "skip"):
        p = run(text=word + "\n\n")
        assert "looks like a command" not in p.stdout
        assert notes(p.home)["intent"] is None


def test_closing_the_menu_returns_to_the_last_prompt():
    p = run(text="Pay rent\nm\n\ndone\n\n")
    assert notes(p.home)["done"] == 1
    assert "or Enter to close" in p.stdout.split("Options")[-1]


def test_a_window_left_at_a_prompt_cannot_undo_a_newer_save():
    mod = _load_hello()
    home = mkdtemp()
    mod.HOME, mod.TODAY, mod.FORCE_INTERACTIVE = home, "2026-10-01", True
    mod.say = lambda text="": None
    first, _ = mod.load()
    first["intent"] = {"text": "Old", "date": "2026-09-30"}
    first["visits"] = ["2026-09-30"]
    assert mod.save(first)
    answers = iter(["y", "Mine", ""])

    def ask(prompt):
        # While this window waits at its first prompt, another one finishes
        # a plan and saves.
        if prompt.startswith("Did you do it"):
            other, _ = mod.load()
            other["done"] = 5
            other["previous"] = "Other window"
            assert mod.save(other)
        return next(answers)

    mod.ask = ask
    mod.daily(startup=False)
    saved = notes(home)
    assert saved["done"] == 6, saved
    assert saved["intent"]["text"] == "Mine", saved
    assert "2026-10-01" in saved["visits"]


def test_set_plan_rereads_the_file_after_the_prompt():
    mod = _load_hello()
    home = mkdtemp()
    mod.HOME, mod.TODAY, mod.FORCE_INTERACTIVE = home, "2026-10-01", True
    mod.say = lambda text="": None
    state, _ = mod.load()
    assert mod.save(state)

    def ask(prompt):
        other, _ = mod.load()
        other["done"] = 3
        assert mod.save(other)
        return "Mine"

    mod.ask = ask
    mod.set_plan(state, True)
    assert notes(home)["done"] == 3 and notes(home)["intent"]["text"] == "Mine"


def test_finished_plans_are_listed_after_done_and_kept_to_seven():
    p = run(text="A\ndone\nB\ndone\n\n")
    assert "Finished lately" in p.stdout
    assert "A" in p.stdout.split("Finished lately")[1]
    assert [i["text"] for i in notes(p.home)["finished"]] == ["A", "B"]
    mod = _load_hello()
    state = mod.new_state()
    import datetime
    for i in range(60):
        mod.finish_plan(state, f"Plan {i}", datetime.date(2026, 10, 1))
    assert len(state["finished"]) == mod.MAX_FINISHED
    assert state["finished"][-1]["text"] == "Plan 59"


def test_finished_plans_come_back_after_a_gap_and_in_the_summary():
    first = run(text="A\ndone\nB\ndone\n\n")
    p = run(text="\n\n", home=first.home, day="2026-10-12")
    assert "Welcome back" in p.stdout and "Finished lately" in p.stdout
    assert "Finished lately" in run(["--stats"], home=first.home).stdout


def test_a_damaged_finished_list_is_ignored():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["2026-09-30"], "finished": [1, {"text": 5},
                   {"text": "ok", "date": "2026-09-30"}, {"text": "x", "date": "bad"}]}, f)
    p = run(text="\n\n", home=home)
    assert "Traceback" not in p.stderr
    assert [i["text"] for i in notes(home).get("finished", [])] == ["ok"]


def test_turning_the_reminder_on_from_the_menu_ends_the_offer():
    home, startup = mkdtemp(), mkdtemp()
    run(text="\nm\n2\n\n\n", home=home, startup=startup)
    assert notes(home)["offered"] is True


def test_done_is_named_not_taken_at_keep_it_for_today():
    first = run(text="Send the invoice\n\n")
    p = run(text="n\ndone\n\n\n", home=first.home, day="2026-10-02")
    assert '"done" is not one of the choices' in p.stdout
    assert notes(first.home)["intent"]["text"] == "Send the invoice"


def test_three_misunderstood_answers_say_what_happened():
    first = run(text="Send the invoice\n\n")
    p = run(text="a\nb\nc\n\n", home=first.home, day="2026-10-02")
    assert "That was not understood. Your plan is left as it was." in p.stdout
    assert notes(first.home)["intent"]["text"] == "Send the invoice"


def test_a_second_window_cannot_overwrite_what_the_first_saved():
    mod = _load_hello()
    home = mkdtemp()
    mod.HOME, mod.TODAY = home, "2026-10-01"
    mod.FORCE_INTERACTIVE = True
    stale, _ = mod.load()
    stale["intent"] = {"text": "Old plan", "date": "2026-10-01"}
    assert mod.save(stale)
    newer, _ = mod.load()
    newer["intent"] = {"text": "New plan", "date": "2026-10-01"}
    newer["previous"] = "Before"
    assert mod.save(newer)
    mod.say = lambda text="": None
    assert mod.mark_done_now(stale, True, mod.today())
    saved = notes(home)
    # Finishing "New plan" leaves the unfinished "Before" as the earlier plan.
    assert saved["previous"] == "Before" and saved["done"] == 1


def test_a_failed_done_save_is_not_celebrated():
    mod = _load_hello()
    mod.HOME, mod.TODAY = mkdtemp(), "2026-10-01"
    shown = []
    mod.say = lambda text="": shown.append(text)
    state, _ = mod.load()
    state["intent"] = {"text": "Plan", "date": "2026-10-01"}
    assert mod.save(state)
    mod.save = lambda s: False
    assert not mod.mark_done_now(state, True, mod.today())
    assert state["intent"] and state.get("done", 0) == 0
    assert any("still open" in t for t in shown)
    assert not any("times you have marked" in t or t in mod.DONE_LINES
                   for t in shown)


def test_thoughts_and_tips_do_not_repeat_as_a_pair_every_100_days():
    import datetime
    mod = _load_hello()
    start = datetime.date(2026, 1, 1)
    pairs = {mod.todays_pair(start + datetime.timedelta(days=n))
             for n in range(len(mod.TIPS) * 2)}
    assert len(pairs) == len(mod.TIPS) * 2


def test_wrapping_follows_a_narrow_window():
    import shutil
    import hello
    real = shutil.get_terminal_size
    # hello.shutil is the shared module, so put it back for later tests.
    shutil.get_terminal_size = lambda fallback=(80, 24): os.terminal_size((40, 24))
    try:
        assert all(len(x) <= 38 for x in hello.wrapped("Earlier plan: ", "word " * 30).splitlines())
    finally:
        shutil.get_terminal_size = real


def test_done_with_no_plan_says_so_and_done_is_not_offered():
    p = run(text="\ndone\n\n")
    assert "type done" not in p.stdout.split("Thought for today")[1]
    assert "There is no plan to mark as done." in p.stdout


def test_menu_accepts_q_and_help_and_names_a_wrong_word():
    p = run(text="\nm\nbanana\nhelp\nq\n")
    assert 'Sorry, "banana" is not one of the choices. Type 1 to 12' in p.stdout
    assert "Words you can type at the last prompt" in p.stdout
    assert p.returncode == 0


def test_a_mistyped_yes_or_no_is_named_and_asked_again():
    first = run(text="Send the invoice\n\n")
    p = run(text="yse\ny\n\n", home=first.home, day="2026-10-02")
    assert '"yse" is not one of the choices' in p.stdout
    assert notes(first.home)["done"] == 1
    # Three misunderstood answers leave the plan as it was.
    second = run(text="Write it\n\n")
    p = run(text="a\nb\nc\n\n", home=second.home, day="2026-10-02")
    assert p.stdout.count("not one of the choices") == 3
    assert "Left as it was." not in p.stdout
    assert notes(second.home)["intent"]["text"] == "Write it"


def test_a_mistyped_sign_in_answer_is_named_and_not_counted_as_a_skip():
    home, startup = mkdtemp(), mkdtemp()
    run(text="\n\n", home=home, startup=startup, day="2026-10-01")
    p = run(text="\nyse\nn\n\n", home=home, startup=startup, day="2026-10-02")
    assert '"yse" is not one of the choices' in p.stdout
    saved = notes(home)
    assert saved.get("offered") is True and "offer_skips" not in saved
    assert os.listdir(startup) == []


def test_same_with_nothing_remembered_is_not_saved_as_a_plan():
    p = run(text="same\n\n")
    assert "There is no earlier plan to reuse yet." in p.stdout
    assert notes(p.home)["intent"] is None
    p = run(text="\nplan\nsame\n\n\n")
    assert "There is no earlier plan to reuse yet." in p.stdout
    assert notes(p.home)["intent"] is None


def test_not_yet_at_the_keep_prompt_keeps_the_plan():
    first = run(text="Write it\n\n")
    p = run(text="n\nnot yet\n\n", home=first.home, day="2026-10-02")
    assert "Kept for today." in p.stdout
    assert notes(first.home)["intent"]["text"] == "Write it"


def _two_windows():
    import copy
    mod = _load_hello()
    mod.HOME = mkdtemp()
    mod.say = lambda text="": None
    first, _ = mod.load()
    other, _ = mod.load()
    return mod, copy, first, copy.deepcopy(first), other, copy.deepcopy(other)


def test_two_windows_that_both_finish_keep_both_finished_plans():
    mod, copy, first, base1, other, base2 = _two_windows()
    mod.finish_plan(other, "B", mod.today())
    assert mod.commit(other, base2, True)
    mod.finish_plan(first, "A", mod.today())
    assert mod.commit(first, base1, True)
    saved = notes(mod.HOME)
    assert sorted(i["text"] for i in saved["finished"]) == ["A", "B"]
    assert saved["done"] == 2 and "previous" not in saved


def test_counts_only_add_and_skips_from_two_windows_both_count():
    mod, copy, first, base1, other, base2 = _two_windows()
    other["done"], other["offer_skips"] = 3, 1
    assert mod.commit(other, base2, True)
    first["offer_skips"] = 1
    assert mod.commit(first, base1, True)
    base = copy.deepcopy(first)
    first["done"] = 1  # a lower count must never subtract
    assert mod.commit(first, base, True)
    saved = notes(mod.HOME)
    assert saved["done"] == 3 and saved["offer_skips"] == 1


def test_one_finished_plan_can_be_forgotten():
    first = run(text="A\ndone\nB\ndone\n\n")
    p = run(text="m\n7\n1\ny\n\n\n", home=first.home)
    assert "Forgotten: B" in p.stdout
    saved = notes(first.home)
    assert [i["text"] for i in saved["finished"]] == ["A"]
    assert "previous" not in saved and saved["done"] == 1



def test_forgetting_from_the_list_keeps_same_unless_asked():
    # Older versions kept a finished plan as same, so the question still
    # comes up for files they wrote.
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["2026-10-01"], "previous": "A", "done": 1,
                   "finished": [{"text": "A", "date": "2026-10-01"}]}, f)
    p = run(text="m\n7\n1\n\n\n\n", home=home)
    assert "Same still has it." in p.stdout
    saved = notes(home)
    assert "finished" not in saved and saved["previous"] == "A"


def test_the_menu_says_enter_goes_back():
    p = run(text="\nm\n\n\n")
    assert "Enter  Back to the last prompt" in p.stdout
    assert "Enter  Close" not in p.stdout


def test_a_failed_yes_at_the_sign_in_offer_leaves_it_open():
    blocker = tempfile.NamedTemporaryFile()
    p = run(text="Write it\ny\n\n", startup=os.path.join(blocker.name, "sub"))
    assert "Could not set up the reminder." in p.stdout
    assert "Menu option 2" in p.stdout
    assert "offered" not in notes(p.home)


def test_no_after_done_goes_back_to_the_last_prompt():
    p = run(text="A\ndone\nno\n\n")
    assert "Closing." not in p.stdout
    assert p.stdout.count("or menu, or Enter to close > ") == 2
    assert notes(p.home)["intent"] is None


def test_the_first_finished_plan_is_listed():
    p = run(text="A\ndone\n\n")
    assert "Finished lately" in p.stdout


def test_finished_dates_far_off_are_dropped():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["2026-09-30"], "finished": [
            {"text": "far", "date": "9999-01-01"},
            {"text": "old", "date": "1990-01-01"},
            {"text": "ok", "date": "2026-09-30"}]}, f)
    run(text="\n\n", home=home)
    assert [i["text"] for i in notes(home)["finished"]] == ["ok"]


def test_the_launcher_is_not_written_from_a_folder_it_cannot_quote():
    mod = _load_hello()
    mod.STARTUP_DIR = mkdtemp()
    mod.say = lambda text="": None
    for folder in ("a%b",):
        mod.__file__ = os.path.join(mkdtemp(), folder, "hello.py")
        assert not mod.remind(True)
        assert os.listdir(mod.STARTUP_DIR) == []


def test_help_names_same_the_finished_list_and_the_menu_enter():
    out = run(["--help"]).stdout
    flat = " ".join(out.split())
    assert "same brings back" in flat and "last 3 finished plans" in flat
    assert "q, x and close" in " ".join(out.split())
    assert "Enter goes back" in out


def test_a_delete_in_one_window_is_not_undone_by_another():
    mod, copy, first, _, other, base = _two_windows()
    first["intent"] = {"text": "Secret", "date": "2026-10-01"}
    first["visits"] = ["2026-10-01"]
    assert mod.save(first)
    other, _ = mod.load()
    base = copy.deepcopy(other)
    deleter, _ = mod.load()
    mod.ask = lambda prompt: "y"
    assert mod.reset(deleter)
    mod.finish_plan(other, "Secret", mod.today())
    other["intent"] = None
    assert not mod.commit(other, base, True)
    assert other == base and other["intent"] is None
    saved = notes(mod.HOME)
    assert saved["intent"] is None and saved["visits"] == []
    assert "finished" not in saved and "previous" not in saved
    # The window that deleted can still save afterwards.
    base = copy.deepcopy(deleter)
    deleter["streak"] = False
    assert mod.commit(deleter, base, True)
    assert notes(mod.HOME)["streak"] is False


def test_tidying_an_old_plan_does_not_overwrite_the_other_windows_plan():
    mod = _load_hello()
    home = mod.HOME = mkdtemp()
    mod.FORCE_INTERACTIVE = True
    mod.say = lambda text="": None
    state, _ = mod.load()
    state["visits"] = ["2026-09-01"]
    state["intent"] = {"text": "Old", "date": "2026-09-01"}
    assert mod.save(state)

    def ask(prompt):
        if prompt.startswith("What is one thing"):
            other, _ = mod.load()
            other["intent"] = {"text": "New", "date": "2026-10-01"}
            assert mod.save(other)
        return ""

    mod.ask = ask
    mod.daily(startup=False)
    saved = notes(home)
    assert saved["intent"]["text"] == "New" and "2026-10-01" in saved["visits"]


def test_the_same_finish_in_two_windows_counts_once():
    mod, copy, first, base1, other, base2 = _two_windows()
    mod.finish_plan(other, "A", mod.today())
    assert mod.commit(other, base2, True)
    mod.finish_plan(first, "A", mod.today())
    assert mod.commit(first, base1, True)
    saved = notes(mod.HOME)
    assert saved["done"] == 1 and len(saved["finished"]) == 1


def test_the_other_window_finishing_too_is_said():
    mod, copy, first, base1, other, base2 = _two_windows()
    mod.finish_plan(other, "B", mod.today())
    assert mod.commit(other, base2, True)
    shown = []
    mod.say = lambda text="": shown.append(text)
    mod.finish_plan(first, "A", mod.today())
    assert mod.commit(first, base1, True)
    assert "The other open window had also finished a plan." in shown


def test_forgetting_a_plan_already_gone_keeps_same():
    mod, copy, first, _, other, _ = _two_windows()
    mod.finish_plan(first, "A", mod.today())
    first["previous"] = "A"  # as an older version saved it
    assert mod.save(first)

    def ask(prompt):
        if prompt.startswith("Also forget"):
            gone, _ = mod.load()
            base = copy.deepcopy(gone)
            gone["finished"] = []
            assert mod.commit(gone, base, True)
            return "y"
        return "1"

    mod.ask = ask
    mod.FORCE_INTERACTIVE = True
    state, _ = mod.load()
    mod.forget_finished(state, True)
    assert notes(mod.HOME)["previous"] == "A"


def test_a_wrong_number_at_forget_says_what_to_type():
    first = run(text="A\ndone\n\n")
    p = run(text="m\n7\n9\n\n\n\n", home=first.home)
    assert 'There is no number "9" on the list. Type a number from 1 to 1' in p.stdout
    assert "not one of the choices" not in p.stdout


def test_the_file_never_holds_more_than_the_visit_limit():
    import datetime
    mod = _load_hello()
    day = datetime.date(2026, 10, 1)
    state = dict(mod.new_state(), streak=True)
    state["visits"] = [(day - datetime.timedelta(days=n)).isoformat()
                       for n in range(mod.MAX_VISITS + 50)]
    out = mod.file_form(state)["visits"]
    assert len(out) == mod.MAX_VISITS and out[-1] == day.isoformat()


def test_the_launcher_quotes_a_folder_with_brackets_and_ampersands():
    mod = _load_hello()
    mod.STARTUP_DIR = mkdtemp()
    mod.say = lambda text="": None
    folder = os.path.join(mkdtemp(), "Tools (x86), a=b @~ & !")
    mod.__file__ = os.path.join(folder, "hello.py")
    assert mod.remind(True)
    with open(os.path.join(mod.STARTUP_DIR, "hello-world-daily.cmd")) as f:
        text = f.read()
    assert f'-I "{mod.__file__}" --startup' in text


def test_unknown_keys_and_wrong_types_in_the_file_are_dropped():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": "2026-09-30", "intent": 5, "done": "7",
                   "finished": {"text": "x"}, "streak": "no", "previous": [1],
                   "offered": "yes", "epoch": {"a": 1},
                   "unknown": {"nested": "data"}}, f)
    p = run(text="\n\n", home=home)
    assert p.returncode == 0 and "Traceback" not in p.stderr
    saved = notes(home)
    assert "unknown" not in saved and saved["visits"] == ["2026-10-01"]
    assert saved["intent"] is None and saved["streak"] is False
    assert run(["--stats"], home=home).returncode == 0


def test_a_day_old_temp_copy_is_swept_and_a_new_one_is_left():
    import time
    mod = _load_hello()
    mod.HOME = mkdtemp()
    old = os.path.join(mod.HOME, "notes.json.111.tmp")
    new = os.path.join(mod.HOME, "notes.json.222.tmp")
    for path in (old, new):
        with open(path, "w") as f:
            f.write("{}")
    os.utime(old, (time.time() - 2 * 86400,) * 2)
    assert mod.save(mod.new_state())
    assert not os.path.exists(old) and os.path.exists(new)


def test_version_matches_the_version_file():
    with open(os.path.join(os.path.dirname(HELLO), "VERSION")) as f:
        version = f.read().strip()
    for arg in ("--version", "-v"):
        p = run([arg])
        assert (p.returncode, p.stdout) == (0, f"hello-world {version}\n")
    assert "--version" in run(["--help"]).stdout


def test_help_lists_the_exit_codes():
    out = " ".join(run(["--help"]).stdout.split())
    assert "Exit codes: 0 when it worked, 1 when a command failed" in out


def test_a_save_blocked_for_a_moment_is_tried_again():
    mod = _load_hello()
    mod.HOME = mkdtemp()
    real, calls = mod.os.replace, []

    def flaky(src, dst):
        calls.append(dst)
        if len(calls) < 3:
            raise PermissionError("held by another program")
        real(src, dst)

    mod.os.replace = flaky
    try:
        assert mod.save(mod.new_state())
    finally:
        mod.os.replace = real
    assert len(calls) == 3 and os.path.exists(mod.data_file())


def test_option_1_says_when_the_file_could_not_be_read():
    home = mkdtemp()
    os.mkdir(os.path.join(home, "notes.json"))  # opening it fails
    p = run(text="\nm\n1\n\n\n\n", home=home)
    assert "could not be read just now" in p.stdout


def test_the_launcher_leaves_no_temp_copy():
    startup = mkdtemp()
    assert run(["--remind", "on"], startup=startup).returncode == 0
    assert os.listdir(startup) == ["hello-world-daily.cmd"]


def test_two_real_windows_merge_their_saves():
    import threading
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["2026-10-01"],
                   "intent": {"text": "Send it", "date": "2026-10-01"}}, f)
    values = {"TODAY": "2026-10-02", "HOME": home, "STARTUP_DIR": "",
              "FORCE_INTERACTIVE": True, "COUNT_ALWAYS": True, "LOCK": "plain"}
    a = subprocess.Popen(launch(**values), stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         encoding="utf-8")
    seen, waiting = [], threading.Event()

    def read():
        while ch := a.stdout.read(1):
            seen.append(ch)
            if "Did you do it?" in "".join(seen[-60:]):
                waiting.set()

    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    try:
        # Window A now waits at its first question while window B runs.
        assert waiting.wait(30), "".join(seen)
        assert run(text="y\n\n\n", day="2026-10-02", home=home).returncode == 0
        a.stdin.write("y\nWrite the report\n\n")
        a.stdin.close()
        assert a.wait(30) == 0
    finally:
        if a.poll() is None:
            a.kill()
    reader.join(5)
    saved = notes(home)
    # Both finished the same plan on the same day: one row, counted once.
    assert saved["done"] == 1 and [i["text"] for i in saved["finished"]] == ["Send it"]
    assert saved["intent"]["text"] == "Write the report"
    assert "The other open window had also finished a plan." in "".join(seen)


def test_the_saved_keys_are_frozen():
    # A new key needs a merge rule in commit() and a test for it, so adding
    # one must change this list on purpose.
    keys = {"visits", "intent", "streak", "offered", "offer_skips",
            "previous", "done", "finished", "epoch", "tips", "text",
            "notified", "lang", "nudge", "open_after", "weekends", "name",
            "remind_at", "no_startup_visits"}
    full = {"visits": ["2026-09-30"], "streak": False, "offered": True,
            "offer_skips": 1, "previous": "p", "done": 2, "epoch": "abc",
            "tips": False, "text": True, "notified": "2026-09-30", "lang": "fr",
            "nudge": True, "open_after": True, "weekends": True,
            "name": True, "remind_at": "09:00", "no_startup_visits": True,
            "intent": {"text": "x", "date": "2026-09-30", "since": "2026-09-29",
                       "skips": 1},
            "finished": [{"text": "f", "date": "2026-09-30"}]}
    assert set(full) == keys
    mod = _load_hello()
    mod.HOME = mkdtemp()
    with open(mod.data_file(), "w") as f:
        json.dump(full, f)
    state, _ = mod.load()
    out = mod.file_form(state)
    assert set(out) == keys | {"schema"} and out["schema"] == mod.SCHEMA
    assert set(out["intent"]) == {"text", "date", "since", "skips"}



def test_a_plan_carried_for_two_weeks_is_put_away():
    first = run(text="Write it\n\n")
    run(text="n\ny\n\n", day="2026-10-02", home=first.home)
    run(text="n\ny\n\n", day="2026-10-03", home=first.home)
    intent = notes(first.home)["intent"]
    assert intent["date"] == "2026-10-03" and intent["since"] == "2026-10-01"
    p = run(text="\n\n", day="2026-10-16", home=first.home)
    assert "over two weeks ago was put away" in p.stdout
    saved = notes(first.home)
    assert saved["intent"] is None and saved["previous"] == "Write it"


def test_after_done_only_the_last_three_finished_plans_are_read():
    p = run(text="A\ndone\nB\ndone\nC\ndone\nD\ndone\n\n")
    last = p.stdout.split("Finished lately")[-1]
    assert ": D" in last and ": B" in last and ": A" not in last
    assert len(notes(p.home)["finished"]) == 4


def test_the_first_run_says_enter_is_all_you_need():
    p = run(text="\n\n")
    assert "Press Enter at each question to skip it, and once more to" in p.stdout


def test_no_prompt_uses_an_equals_sign_for_enter():
    with open(HELLO, encoding="utf-8") as f:
        assert "Enter = " not in f.read()


def test_done_is_still_offered_after_the_sign_in_question():
    home, startup = mkdtemp(), mkdtemp()
    p = run(text="Send the invoices\nn\ndone\n\n", home=home, startup=startup)
    assert "Type done, plan or menu, or Enter to close >" in p.stdout
    assert notes(home)["done"] == 1


def test_yes_is_answered_at_once_and_dated_to_the_plan_day():
    first = run(text="Send the invoice\n\n")
    p = run(text="y\n\n\n", home=first.home, day="2026-10-02")
    shown = [p.stdout.index(line) for line in _load_hello().DONE_LINES
             if line in p.stdout]
    assert shown and shown[0] < p.stdout.index("Thought for today:")
    # A yes gets the praise only; the list comes with done and in option 1.
    assert "Finished lately" not in p.stdout
    assert notes(first.home)["finished"] == [{"text": "Send the invoice",
                                               "date": "2026-10-01"}]


def test_q_closes_from_any_question_and_still_counts_the_visit():
    first = run(text="Send the invoice\n\n")
    p = run(text="q\n", home=first.home, day="2026-10-02")
    assert p.stdout.rstrip().endswith("Closing.")
    saved = notes(first.home)
    assert "2026-10-02" in saved["visits"]
    assert saved["intent"]["text"] == "Send the invoice"
    p = run(text="q\n")
    assert p.stdout.rstrip().endswith("Closing.")
    assert notes(p.home)["visits"] == ["2026-10-01"]


def test_in_a_row_survives_a_friday_off_and_a_weekend():
    import datetime
    mod = _load_hello()
    assert mod.in_a_row(["2026-10-01"], datetime.date(2026, 10, 5)) == 2
    assert mod.in_a_row(["2026-10-01"], datetime.date(2026, 10, 6)) == 1


def test_the_thought_and_tip_never_share_a_body_topic():
    import datetime
    mod = _load_hello()
    start = datetime.date(2026, 1, 1)
    for n in range(len(mod.TIPS) * len(mod.THOUGHTS)):
        thought, tip = mod.todays_pair(start + datetime.timedelta(days=n))
        shared = [w for w in mod.TOPICS if w in thought.lower() and w in tip.lower()]
        assert not shared, (thought, tip)


def test_the_menu_is_listed_once_and_m_lists_it_again():
    p = run(text="\nm\n3\n3\nm\n\n\n\n")
    assert p.stdout.count("Options") == 2
    assert "m to list the options" in p.stdout


def test_option_1_reads_no_file_path():
    home = mkdtemp()
    p = run(text="\nm\n1\n\n\n\n", home=home)
    assert "Saved in your own user folder" in p.stdout
    assert home not in p.stdout
    assert home in run(["--stats"], home=home).stdout


def test_a_yes_after_a_delete_in_another_window_does_not_bring_the_plan_back():
    mod = _load_hello()
    home = mod.HOME = mkdtemp()
    mod.FORCE_INTERACTIVE = True
    mod.say = lambda text="": None
    state, _ = mod.load()
    state["visits"] = ["2026-09-30"]
    state["intent"] = {"text": "secret plan", "date": "2026-09-30"}
    assert mod.save(state)

    def ask(prompt):
        if prompt.startswith("Did you do it"):
            other, _ = mod.load()
            mod.ask = lambda prompt: "y"
            assert mod.reset(other)
            mod.ask = ask
            return "y"
        return ""

    mod.ask = ask
    mod.daily(startup=False)
    assert "secret plan" not in json.dumps(notes(home))


def test_the_same_plan_finished_twice_in_a_day_is_two_rows():
    p = run(text="email\ndone\nemail\ndone\n\n")
    saved = notes(p.home)
    assert saved["done"] == 2 and [i["text"] for i in saved["finished"]] == ["email", "email"]


def test_q_closes_from_the_menu_plan_forget_and_delete_prompts():
    for text in ("\nm\nq\n", "\nplan\nq\n", "\nm\n6\nq\n", "\nm\n4\nq\n"):
        p = run(text=text)
        assert p.stdout.rstrip().endswith("Closing."), text
    first = run(text="A\ndone\n\n")
    p = run(text="m\n7\nq\n", home=first.home)
    assert p.stdout.rstrip().endswith("Closing.")
    p = run(text="close\n")
    assert p.stdout.rstrip().endswith("Closing.") and notes(p.home)["intent"] is None


def test_a_plan_corrected_the_same_day_is_not_kept_for_same():
    p = run(text="Reaplce the keyboard\nplan\nReplace the keyboard\ndone\n\n")
    saved = notes(p.home)
    assert "previous" not in saved
    assert [i["text"] for i in saved["finished"]] == ["Replace the keyboard"]


def test_a_late_yes_asks_which_day_it_was_finished():
    first = run(text="Send the invoice\n\n")
    p = run(text="y\n5\n\n\n", home=first.home, day="2026-10-05")
    assert "When did you finish it?" in p.stdout and "  5  Today" in p.stdout
    assert notes(first.home)["finished"][0]["date"] == "2026-10-05"
    first = run(text="Send the invoice\n\n")
    run(text="y\n\n\n\n", home=first.home, day="2026-10-05")
    assert notes(first.home)["finished"][0]["date"] == "2026-10-01"
    first = run(text="Send the invoice\n\n")
    p = run(text="y\n\n\n", home=first.home, day="2026-10-02")
    assert "When did you finish it?" not in p.stdout


def test_two_skips_stop_the_question_and_the_plan_stays_open():
    first = run(text="Write it\n\n")
    run(text="\n\n\n", home=first.home, day="2026-10-02")
    run(text="\n\n\n", home=first.home, day="2026-10-03")
    p = run(text="\ndone\n\n", home=first.home, day="2026-10-04")
    assert "Did you do it?" not in p.stdout
    assert "Still open since Thursday, 1 October 2026:\n  Write it" in p.stdout
    assert notes(first.home)["done"] == 1


def test_q_at_the_question_asks_again_on_a_second_open_the_same_day():
    first = run(text="Write it\n\n")
    run(text="q\n", home=first.home, day="2026-10-02")
    p = run(text="y\n\n", home=first.home, day="2026-10-02")
    assert "Did you do it?" in p.stdout and notes(first.home)["done"] == 1


def test_option_8_hides_the_thought_and_tip():
    first = run(text="\nm\n8\n\n\n")
    assert notes(first.home)["tips"] is False
    p = run(text="\n\n", home=first.home, day="2026-10-02")
    assert "Thought for today" not in p.stdout and "Try this today" not in p.stdout
    run(text="m\n8\n\n\n", home=first.home, day="2026-10-02")
    assert "tips" not in notes(first.home)


def test_a_plan_of_several_things_gets_one_gentle_nudge():
    p = run(text="Write the deck and fix the banner\n\n")
    assert p.stdout.count("more than one thing") == 1
    assert "more than one thing" not in run(text="Write the deck\n\n").stdout


def test_ctrl_c_at_a_prompt_skips_only_that_prompt():
    mod = _load_hello()
    mod.FORCE_INTERACTIVE = True
    mod.say = lambda text="": None

    def interrupted(_prompt):
        raise KeyboardInterrupt
    mod.input = interrupted
    assert mod.ask("Did you do it? > ") is None


def test_visits_older_than_60_days_are_not_kept():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["2025-01-05", "2026-07-01", "2026-09-30"],
                   "streak": True}, f)
    run(text="\n\n", home=home)
    assert notes(home)["visits"] == ["2026-09-30", "2026-10-01"]


def test_the_delete_marker_must_be_hex():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": [], "epoch": "\u202eevil\u009b31m"}, f)
    out = run(["--stats"], home=home).stdout
    assert "\u202e" not in out and "\u009b" not in out


def test_a_file_deleted_by_hand_does_not_block_the_next_save():
    mod = _load_hello()
    mod.HOME = mkdtemp()
    mod.say = lambda text="": None
    assert mod.save(mod.new_state())
    state, _ = mod.load()  # has an empty epoch, like any older file
    import copy
    base = copy.deepcopy(state)
    os.remove(mod.data_file())
    state["intent"] = {"text": "Mine", "date": "2026-10-01"}
    assert mod.commit(state, base, True)
    assert notes(mod.HOME)["intent"]["text"] == "Mine"


def test_the_lock_keeps_a_second_window_out_while_a_change_is_saved():
    # A delete in one window can't land between another window's read and
    # write: while one holds notes.lock, a second process can't take it.
    mod = _load_hello()
    mod.HOME = mkdtemp()
    probe = (
        "import os, sys" + chr(10)
        + "fd = os.open(sys.argv[1], os.O_RDWR)" + chr(10)
        + "try:" + chr(10)
        + "    if os.name == 'nt':" + chr(10)
        + "        import msvcrt; msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)" + chr(10)
        + "    else:" + chr(10)
        + "        import fcntl; fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)" + chr(10)
        + "    print('got it')" + chr(10)
        + "except OSError:" + chr(10)
        + "    print('kept out')" + chr(10)
    )
    lock = os.path.join(mod.HOME, "notes.lock")
    with mod.file_lock():
        held = subprocess.run([sys.executable, "-c", probe, lock],
                              capture_output=True, text=True).stdout.strip()
    free = subprocess.run([sys.executable, "-c", probe, lock],
                          capture_output=True, text=True).stdout.strip()
    assert (held, free) == ("kept out", "got it")


def test_new_emoji_are_kept_and_mark_floods_are_capped():
    mod = _load_hello()
    assert mod.clean("Finish \U0001FAE9 report") == "Finish \U0001FAE9 report"
    assert mod.clean("e" + "\u0301" * 50).count("\u0301") == mod.MAX_MARKS


def test_a_stale_launcher_temp_file_is_cleared():
    startup = mkdtemp()
    stale = os.path.join(startup, "hello-world-daily.cmd.99.tmp")
    with open(stale, "w") as f:
        f.write("x")
    run(["--remind", "on"], startup=startup)
    assert os.listdir(startup) == ["hello-world-daily.cmd"]


def test_a_long_prompt_wraps_and_keeps_its_choices_visible():
    import shutil as sh
    mod = _load_hello()
    mod.FORCE_INTERACTIVE = True
    shown, asked = [], []
    mod.say = lambda text="": shown.append(text)
    mod.input = lambda prompt: asked.append(prompt) or ""
    real = sh.get_terminal_size
    sh.get_terminal_size = lambda fallback=(80, 24): os.terminal_size((40, 24))
    try:
        mod.ask("Want it to open once a day when you sign in so it can ask "
                "about your plan? (y or n, Enter for not now) > ")
    finally:
        sh.get_terminal_size = real
    assert all(len(line) <= 38 for line in shown + asked)
    assert asked[0].rstrip().endswith(">")


def test_option_1_says_whether_sign_in_opening_is_on():
    home, startup = mkdtemp(), mkdtemp()
    p = run(text="\nm\n1\n\n\n\n", home=home, startup=startup)
    assert "Reminder when you sign in: off." in p.stdout


def _registry_test_key():
    if os.name != "nt":
        raise unittest.SkipTest("the Run value is Windows only")
    return rf"Software\hello-world-test-{os.getpid()}\Run"


def _drop_registry_test_key(key):
    import winreg

    def drop(sub):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub) as k:
                children = [winreg.EnumKey(k, i)
                            for i in range(winreg.QueryInfoKey(k)[0])]
            for child in children:
                drop(sub + "\\" + child)
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, sub)
        except OSError:
            pass
    drop(key)
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key.rsplit("\\", 1)[0])
    except OSError:
        pass


def test_the_launcher_is_a_run_value_with_the_reminder_and_its_answers():
    key = _registry_test_key()
    import winreg
    mod = _load_hello()
    mod.STARTUP_DIR, mod.RUN_KEY = None, key
    mod.CLASSES_KEY = key + "\\Classes"
    mod.say = lambda text="": None
    appdata = os.environ.get("APPDATA")
    os.environ["APPDATA"] = mkdtemp()  # keep the real Startup folder out of it
    try:
        assert mod.remind(True) and mod.launcher_on()
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            value, _ = winreg.QueryValueEx(k, mod.RUN_VALUE)
        assert value.lower().endswith(f'pythonw.exe" -i "{HELLO}" --startup'.lower())
        command = key + "\\Classes\\hello-world\\shell\\open\\command"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, command) as k:
            assert winreg.QueryValueEx(k, "")[0].endswith('--answer "%1"')
        name = key + "\\Classes\\AppUserModelId\\hello-world"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, name) as k:
            assert winreg.QueryValueEx(k, "DisplayName")[0] == "hello-world"
        assert mod.remind(False) and not mod.launcher_on()
        for gone in (command, name):
            try:
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, gone).Close()
                raise AssertionError(gone + " is still there")
            except FileNotFoundError:
                pass
    finally:
        os.environ["APPDATA"] = appdata
        _drop_registry_test_key(key)


def test_an_old_startup_launcher_becomes_the_run_value():
    key = _registry_test_key()
    appdata = mkdtemp()
    startup = os.path.join(appdata, "Microsoft", "Windows", "Start Menu",
                           "Programs", "Startup")
    os.makedirs(startup)
    old = os.path.join(startup, "hello-world-daily.cmd")
    with open(old, "w") as f:
        f.write("@echo off\r\nstart hello.cmd --startup\r\n")
    env = dict(os.environ, APPDATA=appdata)
    values = {"TODAY": "2026-10-01", "HOME": mkdtemp(), "STARTUP_DIR": None,
              "FORCE_INTERACTIVE": True, "POLICY": {}, "RUN_KEY": key,
              "LOCK": "plain"}
    try:
        p = subprocess.run(launch((), **values), input="\n\n", capture_output=True,
                           encoding="utf-8", env=env)
        assert p.returncode == 0, p.stdout + p.stderr
        assert not os.path.exists(old)
        mod = _load_hello()
        mod.STARTUP_DIR, mod.RUN_KEY = None, key
        assert mod.launcher_on()
    finally:
        _drop_registry_test_key(key)


def test_policy_hides_the_thought_tip_and_days_in_a_row():
    home = mkdtemp()
    for day in ("2026-10-01", "2026-10-02"):
        run(text="\n\n", home=home, day=day)
    p = run(text="\n\n", home=home, day="2026-10-03",
            policy={"HideThoughtAndTip": 1, "HideDaysInARow": 1})
    assert "Thought for today" not in p.stdout and "in a row" not in p.stdout
    p = run(text="m\n\n\n\n", home=home, day="2026-10-03",
            policy={"HideThoughtAndTip": 1, "HideDaysInARow": 1})
    assert "hidden by your organization" in p.stdout


def test_policy_turns_off_the_sign_in_launcher():
    home, startup = mkdtemp(), mkdtemp()
    run(["--remind", "on"], startup=startup)
    assert os.listdir(startup) == ["hello-world-daily.cmd"]
    pol = {"DisableSignInLauncher": 1}
    p = run(text="Write it\n\n\n\n", home=home, startup=startup, policy=pol)
    assert os.listdir(startup) == []  # an existing launcher is removed
    assert "so it can ask" not in p.stdout
    p = run(["--remind", "on"], startup=startup, policy=pol)
    assert p.returncode == 1 and "turned off opening at sign-in" in p.stdout
    p = run(text="m\n2\n\n\n\n", home=home, startup=startup, policy=pol)
    assert "turned off by your organization" in p.stdout
    assert os.listdir(startup) == []


def test_policy_turns_plans_off_and_drops_saved_plan_text():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["2026-09-30"], "previous": "old secret",
                   "intent": {"text": "secret plan", "date": "2026-09-30"},
                   "done": 3, "finished": [{"text": "done secret", "date": "2026-09-29"}]}, f)
    pol = {"DisablePlans": 1}
    p = run(text="m\n6\n\n\n", home=home, policy=pol)
    assert "Did you do it?" not in p.stdout and "What is one thing" not in p.stdout
    assert "Type menu, or Enter to close >" in p.stdout
    assert "Plans are turned off by your organization." in p.stdout
    saved = json.dumps(notes(home))
    assert "secret" not in saved and '"done"' not in saved
    p = run(text="plan\n\n", home=home, policy=pol, day="2026-10-02")
    assert "Plans are turned off by your organization." in p.stdout


def test_the_first_run_welcome_matches_the_policies():
    p = run(text="\n\n", policy={"HideThoughtAndTip": 1, "DisablePlans": 1})
    welcome = " ".join(p.stdout.split("Welcome.")[1].split())
    assert "thought" not in welcome.split("Type menu")[0]
    assert "plan" not in welcome.split("Type menu")[0]
    assert "Type menu at the end" in welcome


def test_hiding_days_in_a_row_keeps_only_the_latest_visit():
    home = mkdtemp()
    for day in ("2026-10-01", "2026-10-02", "2026-10-03"):
        run(text="\n\n", home=home, day=day, policy={"HideDaysInARow": 1})
    assert len(notes(home)["visits"]) <= 2


def test_the_policy_template_matches_the_policies_the_program_reads():
    import re
    with open(HELLO, encoding="utf-8") as f:
        source = f.read()
        read = set(re.findall(r'policy\("([A-Za-z]+)"\)', source))
        read |= set(re.findall(r'policy_value\("([A-Za-z]+)"', source))
    admx = os.path.join(os.path.dirname(HELLO), "policy", "hello-world.admx")
    with open(admx, encoding="utf-8") as f:
        offered = set(re.findall(r'valueName="([A-Za-z]+)"', f.read()))
    assert read == offered and read


SAMPLE = os.path.join(os.path.dirname(HELLO), "examples", "content.json")


def _content(**changes):
    with open(SAMPLE, encoding="utf-8") as f:
        data = json.load(f)
    data.update(changes)
    return data


def test_the_sample_content_file_passes_the_check():
    p = run(["--check-content", SAMPLE])
    assert p.returncode == 0
    assert p.stdout.startswith("OK: 20 thoughts and 20 tips.")


def test_organization_content_replaces_the_built_in_lists():
    hello = _load_hello()
    hello.CONTENT = SAMPLE
    data = _content()
    for day in range(7):
        thought, tip = hello.todays_pair(hello.datetime.date(2026, 10, 1 + day))
        assert thought in data["thoughts"] and tip in data["tips"]


def test_content_that_breaks_a_rule_is_ignored_whole():
    hello = _load_hello()
    path = os.path.join(mkdtemp(), "content.json")
    data = _content()
    data["tips"][3] = "Read the news at https://intranet.example today."
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    hello.CONTENT = path
    assert hello.content_lists() == (hello.THOUGHTS, hello.TIPS)
    hello.CONTENT = os.path.join(mkdtemp(), "missing.json")
    assert hello.content_lists() == (hello.THOUGHTS, hello.TIPS)


def test_content_rules_catch_links_dates_length_and_shape():
    hello = _load_hello()
    ok = _content()
    assert hello.content_problems(ok) == []
    cases = {
        "Email the team at help@example.com.": "link or an address",
        "The office closes on 12/24 this year.": "has a date",
        "Remember the party on Friday, December the fifth.": "has a date",
        "Short.": "characters long",
        "x" * 121: "characters long",
        "Two  spaces inside this line.": "extra spaces",
    }
    for text, expected in cases.items():
        data = _content()
        data["thoughts"][0] = text
        problems = hello.content_problems(data)
        assert len(problems) == 1 and expected in problems[0], (text, problems)
    # "May" is a word as well as a month.
    data = _content()
    data["thoughts"][0] = "You may find the quiet hour helps you focus."
    assert hello.content_problems(data) == []
    assert hello.content_problems({"thoughts": ok["thoughts"]})
    assert hello.content_problems(_content(tips=ok["tips"][:6]))
    assert hello.content_problems(_content(tips=[1] * 7))


def test_check_content_fails_on_bad_json_and_missing_files():
    path = os.path.join(mkdtemp(), "content.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write("{not json")
    p = run(["--check-content", path])
    assert p.returncode == 1 and "isn't valid JSON" in p.stdout
    p = run(["--check-content", path + ".missing"])
    assert p.returncode == 1 and "Can't read" in p.stdout


def test_todays_pair_ends_when_every_thought_shares_the_tips_topic():
    hello = _load_hello()
    path = os.path.join(mkdtemp(), "content.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"thoughts": [f"Drink some water, take {n}." for n in "abcdefg"],
                   "tips": [f"Fill a glass of water, round {n}." for n in "abcdefg"]},
                  f)
    hello.CONTENT = path
    thought, tip = hello.todays_pair(hello.datetime.date(2026, 10, 1))
    assert "water" in thought and "water" in tip


def _screen_keys():
    import ast
    hello = _load_hello()
    with open(HELLO, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    # t() is tr() in content_problems() and check_content() under --local.
    keys = [n.args[0].value for n in ast.walk(tree)
            if isinstance(n, ast.Call) and getattr(n.func, "id", "") in ("tr", "t")
            and n.args and isinstance(n.args[0], ast.Constant)]
    keys += [hello.HELP, hello.MENU_HELP, hello.SAVED_PLAN, hello.GREETING]
    # say() doesn't wrap, so what it prints as is must fit 72 columns, less
    # the "  2  " in front of a menu line.
    raw = {n.args[0].value: isinstance(call.args[0], ast.BinOp)
           for call in ast.walk(tree)
           if isinstance(call, ast.Call) and getattr(call.func, "id", "") == "say"
           and call.args
           for n in ast.walk(call.args[0])
           if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "tr"
           and isinstance(n.args[0], ast.Constant)}
    return hello, set(keys), raw


def test_every_language_translates_every_screen_string():
    hello, keys, raw = _screen_keys()
    assert len(keys) > 100 and len(raw) > 50
    assert set(hello.LANGUAGES) == (set(hello.WINDOWS_LANGUAGES.values())
                                    | set(hello.WINDOWS_VARIANTS.values()))
    for code, data in hello.LANGUAGES.items():
        text = data["text"]
        # A key no call uses is a translation nobody sees.
        assert set(text) == keys, (code, sorted(keys ^ set(text))[:3])
        for en, t in text.items():
            # Word order differs between languages, so only the set must match.
            assert sorted(re.findall(r"\{\w+\}", en)) == sorted(re.findall(r"\{\w+\}", t)), (code, en)
            assert en.endswith("> ") == t.endswith("> "), (code, en)
        # The text screen shows English for these scripts, so the console
        # width doesn't apply to them.
        for en, prefixed in raw.items() if code not in hello.WINDOW_ONLY else ():
            for t in (en, text[en]):
                limit = 66 if prefixed else 72
                assert all(len(line) <= limit for line in t.splitlines()), (code, t)


def test_nothing_on_screen_skips_the_translation():
    import ast
    with open(HELLO, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    english_only = {"check_content", "main"}
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef) or fn.name in english_only:
            continue
        for n in ast.walk(fn):
            if not (isinstance(n, ast.Call) and n.args
                    and getattr(n.func, "id", "") in ("say", "para", "ask")):
                continue
            arg = n.args[0]
            # A literal with letters in it; "  " + path and the like are fine.
            plain = (isinstance(arg, ast.JoinedStr)
                     or isinstance(arg, ast.Constant) and arg.value.strip())
            assert not plain, f"{fn.name} line {n.lineno} is not translated"


def test_every_language_has_the_lists_and_dates():
    hello = _load_hello()
    for code, data in hello.LANGUAGES.items():
        assert len(data["thoughts"]) == len(hello.THOUGHTS), code
        assert len(data["tips"]) == len(hello.TIPS), code
        assert len(data["done"]) == len(hello.DONE_LINES), code
        assert len(data["tips_floor"]) == len(hello.TIPS_FLOOR), code
        for line in data["thoughts"] + data["tips"] + data["done"] + data["tips_floor"]:
            assert line == hello.tidy(line) and len(line) <= 140, (code, line)
        assert len(data["days"]) == 7 and len(data["months"]) == 12, code
        hello.LANGUAGE = code
        assert "2026" in hello.long_date(hello.datetime.date(2026, 10, 5)), code
    first = hello.datetime.date(2026, 10, 1)
    for code, expected in (("fr", "jeudi 1er octobre 2026"), ("de", "Donnerstag, 1. Oktober 2026"),
                           ("pt", "quinta-feira, 1º de outubro de 2026")):
        hello.LANGUAGE = code
        assert hello.long_date(first) == expected


def test_command_words_mean_one_thing_in_every_language():
    hello = _load_hello()
    groups = {"yes": hello.STRICT_YES + hello.DID_WORDS + tuple(
                  {w for ws in hello.LETTER_YES.values() for w in ws}), "no": hello.NO, "quit": hello.QUIT_WORDS,
              "plan": hello.PLAN_WORDS, "menu": hello.MENU_WORDS,
              "help": hello.HELP_WORDS, "same": hello.SAME_WORDS,
              "done": hello.DONE_WORDS}
    seen = {}
    for name, words in groups.items():
        for word in words:
            assert word not in seen, f"{word} is both {seen[word]} and {name}"
            seen[word] = name
    assert not set(hello.DECLINE_WORDS) & (set(hello.COMMAND_WORDS) | set(hello.SAME_WORDS))


def test_a_spanish_day_reads_in_spanish():
    p = run(text="Llamar al cliente\n\n", day="2026-10-05", lang="es")
    out = p.stdout
    assert out.startswith("¡Hola, mundo!\nLunes, 5 de octubre de 2026\n")
    assert "Te damos la bienvenida." in out and "Idea para hoy:" in out
    assert "¿Qué cosa quieres terminar hoy?" in out
    assert "Guardado. Escribe hecho" in out
    later = run(text="hecho\n\n\n", day="2026-10-06", lang="es", home=p.home)
    assert "¿Lo hiciste?" in later.stdout
    assert notes(p.home)["done"] == 1


def test_every_language_shows_a_whole_day_without_english():
    hello = _load_hello()
    for code, data in hello.LANGUAGES.items():
        if code in hello.WINDOW_ONLY:
            continue
        p = run(text="Plan A\n\n", day="2026-10-05", lang=code)
        out = p.stdout
        assert out.startswith(data["text"][hello.GREETING] + "\n"), code
        for english in ("Welcome", "Thought for today", "Type ", "Saved."):
            assert english not in out, (code, english)
        assert notes(p.home)["intent"]["text"] == "Plan A", code
        # The done word of this language finishes the plan the next day.
        done = {"es": "hecho", "fr": "fait", "pt": "feito", "de": "erledigt"}[code[:2]]
        later = run(text=f"{done}\n\n\n", day="2026-10-06", lang=code, home=p.home)
        assert notes(later.home)["done"] == 1, code
        assert "Plan A" in later.stdout, code


def test_other_languages_words_work_in_english_too():
    for done, quit_word in (("hecho", "salir"), ("fait", "quitter"),
                            ("feito", "sair"), ("erledigt", "beenden")):
        p = run(text=f"Send the invoice\n{done}\n{quit_word}\n")
        assert notes(p.home)["done"] == 1, done
        assert p.stdout.rstrip().endswith("Closing."), quit_word
    for same in ("repetir", "reprendre", "wieder"):
        q = run(text="Old plan\n\n", day="2026-09-20")
        r = run(text=f"n\nn\n{same}\n\n", home=q.home)
        assert notes(r.home)["intent"]["text"] == "Old plan", same


def test_force_english_policy_wins_over_every_language():
    hello = _load_hello()
    for code in hello.LANGUAGES:
        p = run(lang=code, policy={"ForceEnglish": 1})
        assert p.stdout.startswith("Hello, world!\n"), code
        assert run(["--plain"], lang=code).stdout == "Hello, world!\n", code
    assert run(["--help"], lang="es").stdout.startswith("hello-world muestra")


def test_every_language_fits_72_columns():
    hello = _load_hello()
    for code in hello.LANGUAGES:
        for args in (["--help"], ["--bogus"]):
            out = run(args, lang=code).stdout
            assert all(len(line) <= 72 for line in out.splitlines()), (code, args)
        menu = run(text="\nplan\nm\nm\n5\n\n\n", lang=code).stdout
        # Prompts run into the next line here, since piped input has no echo.
        assert all(len(line) <= 72 for line in menu.splitlines()
                   if "> " not in line), code
    assert "Palabras que puedes escribir" in run(text="\nm\n5\n\n\n", lang="es").stdout


ADML = {"es": "es-ES", "fr": "fr-FR", "pt": "pt-BR", "de": "de-DE",
        "fr-CA": "fr-CA", "pt-PT": "pt-PT", "zh": "zh-CN", "ja": "ja-JP",
        "ko": "ko-KR", "ar": "ar-SA", "he": "he-IL"}


def test_every_language_has_a_policy_template_with_every_string():
    hello = _load_hello()
    root = os.path.join(os.path.dirname(HELLO), "policy")
    ids = {}
    for folder in ["en-US"] + [ADML[code] for code in hello.LANGUAGES]:
        with open(os.path.join(root, folder, "hello-world.adml"), encoding="utf-8") as f:
            ids[folder] = re.findall(r'<string id="(\w+)"', f.read())
    assert all(found == ids["en-US"] for found in ids.values()) and ids["en-US"]

def test_quote_marks_around_a_typed_word_are_ignored():
    p = run(text='Send the invoice\n„erledigt“\n"q"\n')
    assert notes(p.home)["done"] == 1
    assert p.stdout.rstrip().endswith("Closing.")


if __name__ == "__main__":
    import traceback
    failed = []
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
            except unittest.SkipTest as e:
                print(f"SKIPPED {name}: {e}")
            # Any exception counts as a failure, and the remaining tests still run.
            except Exception:
                failed.append(name)
                print(f"FAILED {name}")
                traceback.print_exc()
    if failed:
        print(f"FAILED {len(failed)}: {', '.join(failed)}")
        sys.exit(1)
    print("ok")


def test_one_letter_yes_words_count_only_in_their_own_language():
    # In English, s is a slip or "skip", and must not finish the plan.
    for word in ("s", "o", "j"):
        first = run(text="Book travel\n\n")
        p = run(text=word + "\n\n\n\n\n", day="2026-10-02", home=first.home)
        assert f'"{word}" is not one of the choices' in p.stdout, word
        assert notes(first.home)["intent"]["text"] == "Book travel", word
    for code, word in (("es", "s"), ("pt", "s"), ("fr", "o"), ("de", "j")):
        first = run(text="Plan A\n\n", lang=code)
        run(text=word + "\n\n\n", day="2026-10-02", home=first.home, lang=code)
        assert notes(first.home)["intent"] is None, code


def test_natural_no_words_keep_the_plan_open():
    for word in ("nah", "not really"):
        first = run(text="Book travel\n\n")
        p = run(text=word + "\n\n\n\n", day="2026-10-02", home=first.home)
        assert "Keep it for today?" in p.stdout, word
        assert notes(first.home)["intent"]["text"] == "Book travel", word


def test_a_menu_number_is_not_saved_as_the_plan():
    for typed in ("1", "2.", "#4", "  7 "):
        first = run(text="Write the report\n\n")
        p = run(text=f"\n{typed}\n\n\n", day="2026-10-02", home=first.home)
        assert "A plan needs a word or two" in p.stdout, typed
        assert notes(first.home)["intent"]["text"] == "Write the report", typed
    p = run(text="Call 3 clients\n\n")
    assert notes(p.home)["intent"]["text"] == "Call 3 clients"


def test_menu_at_the_plan_question_opens_the_menu_and_keeps_the_plan():
    first = run(text="Write the report\n\n")
    p = run(text="\nm\n1\n\n\n\n", day="2026-10-02", home=first.home)
    assert "Options" in p.stdout
    assert "Show what is saved" in p.stdout
    assert notes(first.home)["intent"]["text"] == "Write the report"
    assert p.stdout.count("What is one thing you want to get done today?") == 1


def test_the_last_prompt_does_not_name_q_but_q_still_closes():
    p = run(text="Plan A\nq\n")
    assert " or q" not in p.stdout
    assert p.returncode == 0 and p.stdout.count("Enter to close >") == 1


def _window_hello(day="2026-10-02", home=None):
    mod = _load_hello(day)
    mod.HOME = home or mkdtemp()
    mod.WINDOW = True
    return mod


def test_the_window_asks_about_yesterdays_plan_and_answers_like_the_text_screen():
    for choice in ("yes", "no", "skip"):
        first = run(text="Write the report\n\n")
        hello = _window_hello(home=first.home)
        visit = hello.Visit()
        assert visit.followup == "Write the report", choice
        message = visit.answer(choice)
        saved = notes(first.home)
        assert "2026-10-02" in saved["visits"], choice
        assert visit.followup is None, choice
        if choice == "yes":
            assert saved["done"] == 1 and saved["intent"] is None
            assert saved["finished"][0]["date"] == "2026-10-01"
            assert message in hello.DONE_LINES
        elif choice == "no":
            assert saved["intent"] == {"text": "Write the report",
                                       "date": "2026-10-02", "since": "2026-10-01"}
            assert visit.plan() == "Write the report" and message.startswith("Kept for today.")
        else:
            assert saved["intent"]["skips"] == 1 and visit.plan() == ""


def test_the_window_saves_a_plan_and_refuses_what_is_not_one():
    hello = _window_hello()
    visit = hello.Visit()
    close, message, saved = visit.save("menu")
    assert not close and not saved
    assert "command" in message and "last prompt" not in message
    close, message, saved = visit.save("12")
    assert not close and not saved and "A plan needs a word or two" in message
    assert visit.save("skip") == (True, "", False) and visit.plan() == ""
    close, message, saved = visit.save("  ")
    assert not close and not saved and "Type a plan in the box first" in message
    assert visit.save("Call the bank") == (False, "Saved.", True)
    assert visit.save("  ") == (True, "", False)
    assert visit.save("x" * 410)[1] == "Saved. Shortened to 400 characters."
    assert visit.save("Call the bank") == (False, "Saved.", True)
    assert notes(hello.HOME)["intent"]["text"] == "Call the bank"
    assert visit.save("Call the bank") == (True, "", False)
    assert visit.did_it() in hello.DONE_LINES
    saved = notes(hello.HOME)
    assert saved["done"] == 1 and saved["intent"] is None


def test_the_window_replacing_an_unanswered_plan_keeps_it_for_same():
    first = run(text="Old plan\n\n")
    hello = _window_hello(home=first.home)
    visit = hello.Visit()
    assert visit.save("New plan") == (False, "Saved.", True)
    saved = notes(first.home)
    assert saved["intent"]["text"] == "New plan" and saved["previous"] == "Old plan"


def test_the_window_offers_the_reminder_once():
    hello = _window_hello()
    hello.STARTUP_DIR = mkdtemp()
    visit = hello.Visit()
    assert visit.offer_due()
    assert "reminder comes when you sign in" in visit.set_reminder(True)
    assert os.listdir(hello.STARTUP_DIR) == ["hello-world-daily.cmd"]
    assert notes(hello.HOME)["offered"] is True and not visit.offer_due()
    assert "off" in visit.set_reminder(False)
    assert os.listdir(hello.STARTUP_DIR) == [] and not visit.offer_due()


def test_the_window_switches_to_the_text_screen_and_back():
    hello = _window_hello()
    visit = hello.Visit()
    assert not hello.text_screen(visit.state)
    assert visit.toggle("text") and notes(hello.HOME)["text"] is True
    assert hello.text_screen(hello.load()[0])
    assert visit.toggle("text") and "text" not in notes(hello.HOME)
    hello.POLICY = {"UseTextScreen": 1}
    assert hello.text_screen(hello.load()[0])


def test_menu_option_9_switches_the_start_menu_and_policy_can_set_it():
    p = run(text="\nm\n9\n\n\n")
    assert "Use this text screen (now a window with buttons)" in p.stdout
    assert "The Start menu opens this text screen." in p.stdout
    assert notes(p.home)["text"] is True
    p = run(text="\nm\n9\n\n\n", home=p.home, day="2026-10-02")
    assert "The Start menu opens a window with buttons." in p.stdout
    assert "text" not in notes(p.home)
    p = run(text="\nm\n9\n\n\n", policy={"UseTextScreen": 1})
    assert "Window or text screen (set by your organization)" in p.stdout
    assert "set hello-world to open as a text screen" in p.stdout


def test_the_sign_in_reminder_asks_about_a_plan_once_a_day():
    import xml.etree.ElementTree as ET
    first = run(text="Report & slides\n\n")
    hello = _window_hello(home=first.home)
    hello.SHOWN = []
    assert hello.sign_in() == 0 and len(hello.SHOWN) == 1
    toast = ET.fromstring(hello.SHOWN[0])
    texts = [t.text for t in toast.iter("text")]
    # The plan's words stay out of it unless the person turns them on.
    assert texts == ["Did you do it?"]
    key = hello.plan_key("Report & slides", "2026-10-01")
    assert [a.get("arguments") for a in toast.iter("action")] == [
        f"hello-world:{w}/{key}" for w in ("done", "notyet", "skip")]
    assert [a.get("content") for a in toast.iter("action")] == [
        "Done", "Not yet", "Skip"]
    assert notes(first.home)["notified"] == "2026-10-02"
    hello.sign_in()
    assert len(hello.SHOWN) == 1
    # Quiet with no plan, and after hello-world was opened that day.
    hello.TODAY = "2026-10-03"
    hello.Visit()
    hello.sign_in()
    assert len(hello.SHOWN) == 1
    quiet = _window_hello(home=run(text="\n\n").home)
    quiet.SHOWN = []
    quiet.sign_in()
    assert quiet.SHOWN == []


def test_the_reminder_answers_with_no_window_and_refuses_other_links():
    key = _load_hello().plan_key("Write the report", "2026-10-01")
    for link, check in ((f"hello-world:done/{key}", lambda s: s["done"] == 1),
                        (f"HELLO-WORLD:notyet/{key}/", lambda s: s["intent"]["date"] == "2026-10-02")):
        first = run(text="Write the report\n\n")
        p = run(["--answer", link], day="2026-10-02", home=first.home)
        saved = notes(first.home)
        assert p.returncode == 0 and check(saved), link
        assert saved["visits"] == ["2026-10-01"], link
    first = run(text="Write the report\n\n")
    # No key, or another plan's key, as from an old notification or a web page.
    other = _load_hello().plan_key("Another plan", "2026-10-01")
    for link in ("hello-world:delete", "other:done", "hello-world", "hello-world:done",
                 f"hello-world:done/{other}"):
        p = run(["--answer", link], day="2026-10-02", home=first.home)
        assert p.returncode in (0, 2) and "done" not in notes(first.home), link
    assert notes(first.home)["intent"]["date"] == "2026-10-01"


def test_the_saved_file_keeps_only_a_valid_text_choice_and_reminder_date():
    hello = _window_hello()
    with open(os.path.join(hello.HOME, "notes.json"), "w") as f:
        json.dump({"text": True, "notified": "2026-10-01"}, f)
    state, _ = hello.load()
    assert state["text"] is True and state["notified"] == "2026-10-01"
    for bad in ({"text": "yes", "notified": "2030-01-01"}, {"notified": 5}):
        with open(os.path.join(hello.HOME, "notes.json"), "w") as f:
            json.dump(bad, f)
        state, _ = hello.load()
        assert "text" not in state and "notified" not in state


@unittest.skipUnless(os.name == "nt", "the window is Windows only")
def test_the_window_opens_and_closes_in_every_language():
    for lang in ["en"] + sorted(_load_hello().LANGUAGES):
        for plan_first in (True, False):
            home = run(text="Write the report & more\n\n").home if plan_first else None
            hello = _window_hello(home=home)
            hello.LANGUAGE = lang
            hello.CLOSE_WINDOW_AFTER = 200
            window = hello.Window(hello.Visit())
            window.run()
            assert window.error is None, lang


def test_the_window_tab_order_reads_top_to_bottom_and_left_to_right():
    for home in (run(text="Write the report\n\n").home, None):
        hello = _window_hello(home=home)
        items, _ = hello.Window(hello.Visit()).layout()
        places = [(y, x) for _, _, _, _, x, y, _, _ in items]
        assert places == sorted(places)


def test_i_did_it_finishes_what_is_in_the_box_when_it_was_edited():
    first = run(text="Finish the backlog\n\n")
    hello = _window_hello(home=first.home, day="2026-10-01")
    visit = hello.Visit()
    assert visit.did_it("Get the backlog under 20") in hello.DONE_LINES
    saved = notes(first.home)
    assert [f["text"] for f in saved["finished"]] == ["Get the backlog under 20"]
    assert "previous" not in saved  # a same-day change is a correction
    assert "A plan needs a word or two" in visit.did_it("42")


def test_the_window_says_saved_and_nudges_a_plan_of_several_things():
    hello = _window_hello()
    close, message, saved = hello.Visit().save("Email Ana and call the bank")
    assert saved and not close
    assert message.startswith("Saved.") and "more than one thing" in message


def test_the_window_shows_what_is_saved_and_deletes_it():
    first = run(text="Write the report\n\n")
    hello = _window_hello(home=first.home)
    visit = hello.Visit()
    summary = visit.saved_summary()
    assert "Write the report" in summary and hello.data_file() in summary
    assert "Everything saved was deleted" in visit.delete_all()
    assert visit.plan() == "" and visit.followup is None
    assert set(notes(first.home)) == {"schema", "visits", "intent", "streak", "epoch"}


def test_the_text_menu_names_the_sign_in_choice_by_what_it_does():
    p = run(text="\nm\n\n\n")
    assert "Turn on: reminder when you sign in (now off)" in p.stdout
    first = run(text="\nm\n9\n\n\n")
    p = run(text="\nm\n\n\n", home=first.home, day="2026-10-02")
    assert "Turn on: open once a day at sign-in (now off)" in p.stdout


def test_the_text_menu_opened_from_the_window_closes_on_enter():
    p = run(["--menu"], text="\n")
    assert "Enter  Close" in p.stdout and "Back to the last prompt" not in p.stdout
    assert p.returncode == 0


def test_the_window_clears_a_plan_and_names_the_days_in_a_row_choice():
    first = run(text="Write the report\n\n")
    hello = _window_hello(home=first.home, day="2026-10-01")
    visit = hello.Visit()
    assert "Cleared" in visit.clear() and visit.plan() == ""
    saved = notes(first.home)
    assert saved["intent"] is None and saved["previous"] == "Write the report"
    assert visit.toggle("streak") and notes(first.home)["streak"] is True
    summary = visit.saved_summary()
    assert "Days-in-a-row message: shown." in summary
    assert '"visits"' not in summary and hello.data_file() in summary


def test_done_on_the_reminder_says_thank_you():
    first = run(text="Write the report\n\n")
    hello = _window_hello(home=first.home)
    hello.SHOWN = []
    key = hello.plan_key("Write the report", "2026-10-01")
    assert hello.answer_reminder(f"hello-world:done/{key}") == 0
    assert len(hello.SHOWN) == 1 and "<actions>" not in hello.SHOWN[0]
    assert any(line in hello.SHOWN[0] for line in hello.DONE_LINES)
    first = run(text="Write the report\n\n")
    hello = _window_hello(home=first.home)
    hello.SHOWN = []
    hello.answer_reminder(f"hello-world:notyet/{key}")
    assert hello.SHOWN == []


def test_a_plan_of_several_things_is_split_and_each_is_finished_on_its_own():
    hello = _load_hello()
    assert hello.plan_parts("Call Ana; ; send the report ") == ["Call Ana", "send the report"]
    assert hello.plan_parts("one thing") == ["one thing"]
    assert len(hello.plan_parts(";".join("abcdefghijkl"))) == hello.MAX_PARTS
    # Nothing to do in "--", but an emoji alone is something.
    assert hello.plan_parts("Call Ana; --; \U0001f680") == ["Call Ana", "\U0001f680"]
    first = run(text="Call Ana; send the report; book travel\n\n")
    p = run(text="1 3\n\n", day="2026-10-02", home=first.home)
    assert "1  Call Ana" in p.stdout and "The rest is kept for today." in p.stdout
    saved = notes(first.home)
    # Stored last-first, so newest_first shows them in plan order.
    assert [f["text"] for f in saved["finished"]] == ["book travel", "Call Ana"]
    assert saved["done"] == 2
    assert saved["intent"]["text"] == "send the report"
    assert saved["intent"]["since"] == "2026-10-01"
    p = run(text="y\n\n\n", day="2026-10-03", home=first.home)
    assert notes(first.home)["done"] == 3


def test_all_of_a_plan_of_several_things_and_not_yet():
    first = run(text="Call Ana; send the report\n\n")
    run(text="y\n\n\n", day="2026-10-02", home=first.home)
    assert notes(first.home)["done"] == 2 and notes(first.home)["intent"] is None
    first = run(text="Call Ana; send the report\n\n")
    p = run(text="1 2\n\n\n", day="2026-10-02", home=first.home)
    assert "The rest is kept" not in p.stdout and notes(first.home)["done"] == 2
    first = run(text="Call Ana; send the report\n\n")
    p = run(text="banana\nn\n\n\n", day="2026-10-02", home=first.home)
    assert 'Sorry, "banana" is not one of the choices.' in p.stdout
    assert notes(first.home)["intent"]["text"] == "Call Ana; send the report"


def test_the_window_ticks_some_things_done_and_keeps_the_rest():
    first = run(text="Call Ana; send the report; book travel\n\n")
    hello = _window_hello(home=first.home)
    visit = hello.Visit()
    message = visit.answer("yes", [1])
    assert message.endswith("The rest is kept for today.")
    saved = notes(first.home)
    assert [f["text"] for f in saved["finished"]] == ["send the report"]
    assert visit.plan() == "Call Ana; book travel"
    assert visit.did_it("Call Ana; book travel") == "Good. 2 things are off your list."
    assert notes(first.home)["done"] == 3


def test_skip_on_the_reminder_counts_a_skip():
    first = run(text="Write the report\n\n")
    key = _load_hello().plan_key("Write the report", "2026-10-01")
    p = run(["--answer", f"hello-world:skip/{key}"], day="2026-10-02", home=first.home)
    assert p.returncode == 0 and notes(first.home)["intent"]["skips"] == 1


def test_delete_everything_keeps_the_settings():
    first = run(text="Write the report\n\n")
    hello = _window_hello(home=first.home)
    visit = hello.Visit()
    assert visit.toggle("streak") and visit.toggle("tips")
    said = visit.delete_all()
    assert ("Your settings were kept: thought and tip hidden, days-in-a-row message."
            in " ".join(said.split()))
    saved = notes(first.home)
    assert saved["streak"] is True and saved["tips"] is False
    assert saved["intent"] is None and "finished" not in saved


def test_ctrl_c_twice_closes_and_once_only_skips():
    hello = _load_hello()
    hello.FORCE_INTERACTIVE = True
    calls = []

    def interrupted(prompt=""):
        calls.append(prompt)
        raise KeyboardInterrupt

    hello.say = lambda text="": None
    import builtins
    real = builtins.input
    builtins.input = interrupted
    try:
        assert hello.ask("Question > ") is None
        try:
            hello.ask("Question > ")
            raise AssertionError("a second Ctrl+C should close")
        except hello.Quit:
            pass
        hello.INTERRUPTED = 0.0
        assert hello.ask("Question > ") is None
    finally:
        builtins.input = real


def test_a_person_can_choose_their_language():
    p = run(text="\nm\n10\n2\n\n\n")
    assert "Language (now following Windows)" in p.stdout
    assert "2  Español" in p.stdout
    assert "The new language shows next time" in p.stdout
    assert notes(p.home)["lang"] == "es"
    p = run(text="\n\n", home=p.home, day="2026-10-02")
    assert "¡Hola, mundo!" in p.stdout
    p = run(text="\n\n", home=p.home, day="2026-10-03", policy={"ForceEnglish": 1})
    assert "Hello, world!" in p.stdout
    hello = _window_hello(home=p.home)
    visit = hello.Visit()
    assert hello.set_language(visit.state, visit.can_save, None)
    assert "lang" not in notes(p.home)


def test_the_reminder_can_come_on_days_with_no_plan_and_skips_days_off():
    import datetime
    hello = _window_hello(day="2026-10-05")
    state = hello.new_state()
    d = datetime.date(2026, 10, 5)
    assert hello.reminder_due(state, d) is None
    state["nudge"] = True
    assert hello.reminder_due(state, d) == ""
    assert hello.reminder_due(state, datetime.date(2026, 10, 10)) is None
    state["weekends"] = True
    assert hello.reminder_due(state, datetime.date(2026, 10, 10)) == ""
    state.pop("weekends")
    content = os.path.join(mkdtemp(), "content.json")
    with open(content, "w") as f:
        json.dump({"thoughts": ["A calm line of ten chars"] * 7,
                   "tips": ["Another line, ten chars"] * 7,
                   "holidays": ["2026-10-05"], "title": "Good day, team"}, f)
    hello.CONTENT = content
    assert hello.reminder_due(state, d) is None
    assert hello.greeting(state) == "Good day, team"
    hello.SHOWN = []
    hello.TODAY = "2026-10-06"
    with open(os.path.join(hello.HOME, "notes.json"), "w") as f:
        json.dump({"visits": ["2026-10-05"], "nudge": True}, f)
    hello.sign_in()
    assert len(hello.SHOWN) == 1 and "hello-world:open" in hello.SHOWN[0]
    assert "One thing to get done today?" in hello.SHOWN[0]


def test_content_holidays_and_title_are_checked():
    hello = _load_hello()
    base = {"thoughts": ["A calm line of ten chars"] * 7,
            "tips": ["Another line, ten chars"] * 7}
    assert hello.content_problems(base) == []
    assert hello.content_problems(dict(base, holidays=["2026-12-25"], title="Hi all")) == []
    assert hello.content_problems(dict(base, holidays=["Christmas"]))
    assert hello.content_problems(dict(base, title="See www.example.com"))
    assert hello.content_problems(dict(base, title=""))
    assert hello.content_problems(dict(base, extra=1))


def test_a_reminder_at_a_set_time_replaces_the_sign_in_one():
    hello = _window_hello()
    hello.STARTUP_DIR = mkdtemp()
    hello.TASKS = []
    visit = hello.Visit()
    assert "9:00" in visit.reminder_at("09:00")
    assert hello.TASKS == ["09:00"] and hello.task_on() and hello.reminder_on()
    assert not hello.launcher_on()
    saved = notes(hello.HOME)
    assert saved["remind_at"] == "09:00" and saved["offered"] is True
    visit.set_reminder(True)
    assert hello.TASKS[-1] is None and hello.launcher_on()
    assert "remind_at" not in notes(hello.HOME)


def test_open_after_answering_and_greeting_by_name():
    first = run(text="Write the report\n\n")
    hello = _window_hello(home=first.home)
    visit = hello.Visit()
    assert visit.toggle("open_after") and visit.toggle("name")
    opened = []
    hello.show_window = lambda: opened.append(1) or 0
    hello.SHOWN = []
    hello.TODAY = "2026-10-03"
    hello.answer_reminder("hello-world:done/" + hello.plan_key("Write the report", "2026-10-01"))
    assert opened == [1] and hello.SHOWN == []
    hello.first_name = lambda: "Ana"
    assert hello.greeting(notes(first.home)) == "Hello, Ana!"


def test_the_turn_on_reminder_policy_turns_it_on_once():
    first = run(text="\n\n")
    startup = mkdtemp()
    run(text="\n\n", home=first.home, startup=startup, day="2026-10-02",
        policy={"TurnOnReminder": 1})
    assert os.listdir(startup) == ["hello-world-daily.cmd"]
    assert notes(first.home)["offered"] is True
    run(["--remind", "off"], startup=startup, home=first.home)
    run(text="\n\n", home=first.home, startup=startup, day="2026-10-03",
        policy={"TurnOnReminder": 1})
    assert os.listdir(startup) == []


@unittest.skipUnless(os.name == "nt", "scheduled tasks are Windows only")
def test_the_reminder_task_is_created_and_removed_for_this_user():
    hello = _load_hello()
    hello.TASK_NAME = "hello-world test " + os.urandom(4).hex()
    try:
        assert hello.reminder_task("09:00") and hello.task_on()
    finally:
        assert hello.reminder_task(None)
    assert not hello.task_on()


def test_usage_events_and_the_error_log_are_opt_in_and_hold_no_plan_text():
    first = run(text="Secret plan name\n\n")
    hello = _window_hello(home=first.home)
    hello.EVENTS = []
    hello.Visit().answer("yes")
    assert hello.EVENTS == []
    hello.POLICY = {"ReportUsage": 1}
    first = run(text="Secret plan name\n\n")
    hello.HOME = first.home
    hello.Visit().answer("yes")
    assert hello.EVENTS == ["hello-world: opened", "hello-world: plan finished"]
    assert not any("Secret" in e for e in hello.EVENTS)
    hello.POLICY = {"LogErrors": 1}
    try:
        raise ValueError("Secret plan name")
    except ValueError as e:
        hello.log_error(e)
    with open(os.path.join(hello.HOME, "errors.log")) as f:
        logged = f.read()
    assert "ValueError" in logged and "Secret" not in logged


def test_feedback_opens_a_mail_only_to_a_plain_address():
    hello = _window_hello()
    hello.STARTED = []
    assert not hello.send_feedback()
    for bad in ("not an address", "a@b", "a@b.com?bcc=x@y.com", "a b@c.com"):
        hello.POLICY = {"FeedbackAddress": bad}
        assert hello.feedback_address() is None, bad
    hello.POLICY = {"FeedbackAddress": "helpdesk@example.com"}
    assert hello.send_feedback()
    assert hello.STARTED[0].startswith("mailto:helpdesk@example.com?subject=hello-world")


def test_backups_can_be_timestamped_and_capped():
    hello = _load_hello()
    hello.HOME = mkdtemp()
    os.makedirs(hello.HOME, exist_ok=True)
    hello.POLICY = {"TimestampBackups": 1, "MaxBackups": 2}
    for n in range(4):
        with open(hello.data_file(), "w") as f:
            f.write("damaged " + str(n))
        hello.load()
    backups = [n for n in os.listdir(hello.HOME) if n.endswith(".bak")]
    assert len(backups) == 2 and all(n.count(".") == 3 for n in backups)


def test_a_damaged_file_can_be_left_alone_when_nobody_is_there():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        f.write("damaged")
    run(["--startup"], home=home, policy={"LeaveDamagedFile": 1})
    assert os.listdir(home) == ["notes.json"]
    run(["--startup"], home=home)
    assert "notes.json.bak" in os.listdir(home)


def test_sign_in_runs_can_be_left_out_of_the_days_in_a_row():
    first = run(["--streak", "on"])
    run(["--count-sign-in", "off"], home=first.home)
    run(["--startup"], text="\n\n", home=first.home, day="2026-10-02")
    assert notes(first.home)["visits"] == []
    run(["--count-sign-in", "on"], home=first.home)
    run(["--startup"], text="\n\n", home=first.home, day="2026-10-02")
    assert notes(first.home)["visits"] == ["2026-10-02"]


def test_each_user_has_their_own_reminder_task_name():
    hello = _load_hello()
    assert hello.TASK_NAME.startswith("hello-world reminder ")
    assert hello.TASK_NAME != "hello-world reminder "


def test_a_longer_history_numbers_week_and_export():
    first = run(["--set", "long_history", "on"])
    run(["--set", "numbers", "on"], home=first.home)
    for n in range(1, 10):
        run(text=f"Plan {n}\ndone\n\n", home=first.home, day=f"2026-10-0{n}")
    saved = notes(first.home)
    assert len(saved["finished"]) == 9 and saved["opens"] == 9
    assert saved["best_run"] == 9
    p = run(["--numbers"], home=first.home, day="2026-10-09")
    assert "Days you opened hello-world: 9" in p.stdout
    p = run(["--week"], home=first.home, day="2026-10-09")
    assert "This week you finished 5:" in p.stdout and "Plan 5" in p.stdout
    hello = _load_hello("2026-10-09")
    hello.HOME, hello.EXPORT_DIR = first.home, mkdtemp()
    path = hello.export_plans(hello.load()[0])
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert text.startswith("# hello-world") and "- 2026-10-09: Plan 9" in text


def test_the_done_count_and_finished_list_can_be_switched_off():
    first = run(["--set", "no_count", "on"])
    run(["--set", "hide_finished", "on"], home=first.home)
    p = run(text="Call Ana\ndone\n\n", home=first.home)
    assert "Finished lately" not in p.stdout
    assert "done" not in notes(first.home) and notes(first.home)["finished"]
    assert run(["--set", "nonsense", "on"], home=first.home).returncode == 2


def test_same_can_expire_after_30_days():
    first = run(["--set", "expire_same", "on"])
    run(text="Old plan\n\n", home=first.home, day="2026-10-01")
    run(text="n\nn\n\n\n", home=first.home, day="2026-10-02")
    assert notes(first.home)["previous"] == "Old plan"
    assert notes(first.home)["previous_date"] == "2026-10-02"
    p = run(text="\n\n", home=first.home, day="2026-11-15")
    assert "Earlier plan" not in p.stdout and "previous" not in notes(first.home)


def test_prompts_can_end_in_a_colon_and_close_after_the_next_plan():
    first = run(["--set", "colon_prompts", "on"])
    p = run(text="\n\n", home=first.home)
    assert "Enter to close:" in p.stdout and "close >" not in p.stdout
    first = run(["--set", "close_after_done", "on"])
    p = run(text="Plan A\ndone\nPlan B\n", home=first.home)
    assert p.returncode == 0 and notes(first.home)["intent"]["text"] == "Plan B"
    assert p.stdout.count("Type done, plan or menu, or Enter to close") == 1


def test_direction_marks_stay_and_overrides_go():
    hello = _load_hello()
    assert hello.tidy("a\u200fb") == "a\u200fb"
    assert hello.tidy("a\u202eb") == "ab"


def test_check_content_can_answer_in_the_persons_language():
    path = os.path.join(mkdtemp(), "content.json")
    with open(path, "w") as f:
        f.write("not json")
    assert "isn't valid JSON" in run(["--check-content", path], lang="es").stdout
    p = run(["--check-content", path, "--local"], lang="es")
    assert "no es JSON válido" in p.stdout
    assert run(["--plain-local"], lang="es").stdout.strip() == "¡Hola, mundo!"
    assert run(["--plain"], lang="es").stdout.strip() == "Hello, world!"


def test_the_text_menu_marks_todays_plan_done():
    first = run(text="Plan A\n\n")
    p = run(text="m\n11\n\n\n", home=first.home)
    assert "Mark today's plan done" in p.stdout
    assert notes(first.home)["done"] == 1


def test_an_old_sign_in_value_is_rewritten():
    startup = mkdtemp()
    path = os.path.join(startup, "hello-world-daily.cmd")
    with open(path, "w") as f:
        f.write('@echo off\r\ncmd /d /c if exist "x\\hello.cmd" start "" hello.cmd --startup\r\n')
    run(text="\n\n", startup=startup)
    with open(path) as f:
        assert "hello.cmd" not in f.read()


def test_window_only_scripts_show_in_the_window_and_english_in_the_text_screen():
    hello = _load_hello()
    for code in hello.WINDOW_ONLY:
        hello.LANGUAGE, hello.WINDOW = code, False
        assert hello.language() == "en", code
        hello.WINDOW = True
        assert hello.language() == code, code
        assert hello.tr(hello.GREETING) != hello.GREETING, code
    p = run(text="\n\n", lang="ja")
    assert p.stdout.startswith("Hello, world!\n")


def test_regional_variants_follow_the_whole_windows_language():
    hello = _load_hello()
    assert hello.WINDOWS_VARIANTS[0x0C0C] == "fr-CA"
    assert hello.WINDOWS_VARIANTS[0x0816] == "pt-PT"
    hello.LANGUAGE = "fr-CA"
    assert hello.tr("Also on weekends") == "Aussi la fin de semaine"
    assert hello.tr("Saved.") == hello.LANGUAGES["fr"]["text"]["Saved."]


def test_translations_load_from_their_own_files_and_a_broken_one_is_skipped():
    import shutil
    hello = _load_hello()
    folder = mkdtemp()
    for code in ("es", "fr", "fr-CA"):
        shutil.copy(os.path.join(os.path.dirname(HELLO), f"hello.{code}.json"), folder)
    with open(os.path.join(folder, "hello.de.json"), "w") as f:
        f.write("{ broken")
    with open(os.path.join(folder, "hello.xx.json"), "w") as f:
        f.write('{"text": {}}')
    hello.load_languages(folder)
    assert sorted(hello.LANGUAGES) == ["es", "fr", "fr-CA"]
    assert hello.LANGUAGES["fr-CA"]["text"]["Also on weekends"] == "Aussi la fin de semaine"
    assert hello.LANGUAGES["fr-CA"]["text"]["Saved."] == hello.LANGUAGES["fr"]["text"]["Saved."]
    assert len(hello.LANGUAGES["fr-CA"]["tips_floor"]) == len(hello.TIPS_FLOOR)


def test_content_can_come_per_language():
    import shutil
    hello = _load_hello()
    folder = mkdtemp()
    shutil.copy(HELLO, folder)
    base = {"thoughts": ["A calm line of ten chars"] * 7}
    for name, tip in (("content.json", "An English tip, ten chars"),
                      ("content.es.json", "Un consejo en español")):
        with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
            json.dump(dict(base, tips=[tip] * 7), f)
    hello.__file__ = os.path.join(folder, "hello.py")
    hello.LANGUAGE = "es"
    assert hello.org_content()["tips"][0] == "Un consejo en español"
    hello.LANGUAGE = "fr"
    assert hello.org_content()["tips"][0] == "An English tip, ten chars"


def test_floor_tips_replace_the_tips_when_chosen():
    first = run(["--set", "floor_tips", "on"])
    p = run(text="\n\n", home=first.home)
    hello = _load_hello()
    assert any(tip in p.stdout.replace("\n  ", " ") for tip in hello.TIPS_FLOOR)
    p = run(text="\n\n", home=first.home, lang="es", day="2026-10-02")
    spanish = hello.LANGUAGES["es"]["tips_floor"]
    assert any(tip in p.stdout.replace("\n  ", " ") for tip in spanish)


@unittest.skipUnless(os.name == "nt", "known folders are Windows only")
def test_the_startup_folder_comes_from_the_known_folder_api():
    hello = _load_hello()
    hello.STARTUP_DIR = None
    path = hello.legacy_launcher()
    assert path and path.endswith(os.path.join("Startup", "hello-world-daily.cmd"))


def test_a_reminder_shared_screen_leaves_the_plan_out():
    import xml.etree.ElementTree as ET
    hello = _load_hello()
    hello.SHOWN = []
    hello.show_reminder("Secret plan", "2026-10-01", private=True)
    texts = [t.text for t in ET.fromstring(hello.SHOWN[0]).iter("text")]
    assert texts == ["Did you do it?"]


def test_the_sign_in_run_honours_the_launcher_and_damaged_file_policies():
    first = run(text="Write the report\n\n")
    hello = _window_hello(home=first.home)
    hello.SHOWN, hello.TASKS = [], ["09:00"]
    hello.POLICY = {"DisableSignInLauncher": 1}
    hello.sign_in()
    assert hello.SHOWN == [] and hello.TASKS[-1] is None
    with open(os.path.join(first.home, "notes.json"), "w") as f:
        f.write("damaged")
    hello.POLICY = {"LeaveDamagedFile": 1}
    hello.sign_in()
    hello.answer_reminder("hello-world:done/x")
    assert os.listdir(first.home) == ["notes.json"] or "notes.lock" in os.listdir(first.home)
    assert not any(n.endswith(".bak") for n in os.listdir(first.home))


def test_a_broken_translation_file_never_stops_the_program():
    import shutil
    hello = _load_hello()
    folder = mkdtemp()
    shutil.copy(os.path.join(os.path.dirname(HELLO), "hello.fr.json"), folder)
    bad = {"hello.es.json": {"text": {"a": "b"}, "days": [1]},
           "hello.fr-CA.json": {"base": "fr", "text": {}, "tips": [1, 2]},
           "hello.pt-PT.json": {"base": ["fr"], "text": {}},
           "hello.de.json": {"text": {"a": 5}}}
    for name, data in bad.items():
        with open(os.path.join(folder, name), "w") as f:
            json.dump(data, f)
    hello.load_languages(folder)
    assert sorted(hello.LANGUAGES) == ["fr"]


def test_a_language_chosen_now_shows_from_the_next_open():
    hello = _window_hello()
    visit = hello.Visit()
    assert hello.language() == "en"
    assert hello.set_language(visit.state, visit.can_save, "ar")
    assert hello.language() == "en"
    assert hello.set_language(visit.state, visit.can_save, None)
    assert hello.language() == "en"


def test_finished_plans_older_than_two_weeks_go():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": [], "finished": [{"text": "old", "date": "2026-09-01"},
                                               {"text": "new", "date": "2026-09-28"}]}, f)
    hello = _load_hello()
    hello.HOME = home
    assert [i["text"] for i in hello.load()[0]["finished"]] == ["new"]


def test_some_parts_of_todays_plan_can_be_finished_from_the_window():
    first = run(text="Call Ana; send the report; book travel\n\n")
    hello = _window_hello(home=first.home, day="2026-10-01")
    visit = hello.Visit()
    message = visit.finish_parts(["Call Ana", "book travel"])
    assert message == "Good. 2 things are off your list. The rest is kept for today."
    saved = notes(first.home)
    assert [i["text"] for i in saved["finished"]] == ["book travel", "Call Ana"]
    assert saved["intent"]["text"] == "send the report"


def test_ticks_from_a_plan_another_window_changed_finish_nothing():
    first = run(text="x; y; z\n\n")
    hello = _window_hello(home=first.home, day="2026-10-01")
    visit = hello.Visit()
    other = hello.Visit()
    other.clear()
    other.save("p; q")
    assert "changed the plan" in visit.finish_parts(["x"])
    saved = notes(first.home)
    assert "finished" not in saved and saved["intent"]["text"] == "p; q"


def test_a_plan_of_several_things_gets_open_instead_of_done_in_the_reminder():
    hello = _load_hello()
    hello.SHOWN = []
    hello.show_reminder("Call Ana; send it", "2026-10-01")
    hello.show_reminder("Call Ana", "2026-10-01")
    several, one = hello.SHOWN
    assert 'arguments="hello-world:open"' in several and "done/" not in several
    assert "hello-world:done/2026-10-01-" in one


def test_the_week_shows_last_week_too():
    hello = _load_hello(day="2026-10-07")
    state = hello.new_state()
    state["finished"] = [{"text": "old", "date": "2026-09-28"},
                         {"text": "older", "date": "2026-09-20"}]
    text = hello.week_text(state, hello.today())
    assert text.startswith("Nothing finished yet this week.")
    assert "Last week you finished 1:" in text and "old" in text and "older" not in text


def test_forgetting_one_of_two_identical_rows_keeps_the_other():
    first = run(text="Call Ana; Call Ana\ndone\ny\n\n")
    hello = _window_hello(home=first.home, day="2026-10-01")
    visit = hello.Visit()
    item = notes(first.home)["finished"][0]
    visit.forget(item)
    assert [i["text"] for i in notes(first.home)["finished"]] == ["Call Ana"]


def test_turning_my_numbers_on_again_keeps_the_numbers():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["2026-10-02"], "opens": 40, "run": 3,
                   "best_run": 30}, f)
    hello = _window_hello(home=home)
    visit = hello.Visit()
    assert visit.toggle("numbers")
    saved = notes(home)
    assert saved["opens"] == 40 and saved["best_run"] == 30


def test_a_translation_with_a_wrong_placeholder_or_empty_floor_tips_is_skipped():
    hello = _load_hello()
    hello.load_languages()
    good = dict(hello.LANGUAGES["es"])
    assert hello.language_fits(good)
    assert not hello.language_fits(dict(good, tips_floor=()))
    assert not hello.language_fits(dict(good, tips_floor="abc"))
    text = dict(good["text"])
    text["Longest run of days: {n}"] = "Racha: {m}"
    assert not hello.language_fits(dict(good, text=text))


def test_a_finished_plan_can_be_forgotten_from_the_window():
    first = run(text="Call Ana\ndone\n\n")
    hello = _window_hello(home=first.home, day="2026-10-01")
    visit = hello.Visit()
    item = notes(first.home)["finished"][0]
    assert visit.forget(item) == "Forgotten: Call Ana"
    saved = notes(first.home)
    assert "finished" not in saved and saved.get("done", 0) == 0
    assert "already forgotten" in visit.forget(item)


def test_numbers_count_today_from_the_moment_they_are_on():
    hello = _window_hello()
    visit = hello.Visit()
    assert visit.toggle("numbers")
    assert "Days you opened hello-world: 1" in hello.numbers_text(visit.state)
    assert hello.numbers_text(hello.new_state()) == "My numbers are off."


def test_the_summary_says_the_last_day_when_only_that_is_kept():
    first = run(text="\n\n")
    p = run(["--stats"], home=first.home, day="2026-10-03")
    assert "Last opened: Thursday, 1 October 2026" in p.stdout
    assert "Days you opened it" not in p.stdout


def test_the_floor_tips_policy_sets_them_for_everyone():
    hello = _load_hello()
    hello.POLICY = {"FloorTips": 1}
    assert hello.built_in_lists()[1] == hello.TIPS_FLOOR


def test_no_done_count_is_kept_without_my_numbers():
    p = run(text="Call Ana\ndone\n\n", count=False)
    saved = notes(p.home)
    assert "done" not in saved
    run(["--set", "numbers", "on"], home=p.home, count=False)
    run(text="Send it\ndone\n\n", home=p.home, day="2026-10-02", count=False)
    assert notes(p.home)["done"] == 1


def test_a_task_under_the_old_name_moves_to_the_new_one():
    import subprocess as sp
    hello = _load_hello()
    hello.os.name, real_name = "nt", hello.os.name
    hello.OLD_TASK_NAME, hello.TASK_NAME = "old", "new"
    calls, made = [], []
    xml = "<Task><StartBoundary>2026-01-01T09:00:00</StartBoundary></Task>".encode("utf-16")

    def fake(args, **kw):
        calls.append(args[1])
        return sp.CompletedProcess(args, 0, xml if args[1] == "/Query" else b"", b"")
    real_run, sp.run = sp.run, fake
    hello.reminder_task = made.append
    try:
        hello.move_old_task()
        hello.POLICY = {"DisableSignInLauncher": 1}
        hello.move_old_task()
    finally:
        sp.run, hello.os.name = real_run, real_name
    assert calls == ["/Query", "/Delete"] * 2 and made == ["09:00"]


def test_menu_option_12_has_the_windows_other_settings():
    p = run(text="\nm\n12\n1\n12\n7\n12\n5\ny\n12\nbanana\n\n\n")
    assert "12  More settings..." in p.stdout
    assert "Greet me by name (now off)" in p.stdout
    assert "The greeting uses your first name." in p.stdout
    assert "Finished plans are kept for 90 days instead of 14." in p.stdout
    assert "Days you opened hello-world: 1" in p.stdout
    assert 'Type a number from 1 to 12, or press Enter to go back.' in p.stdout
    saved = notes(p.home)
    assert saved["name"] is True and saved["long_history"] is True
    assert saved["numbers"] is True


def test_the_text_menu_sets_a_reminder_time_and_forgets_the_earlier_plan(capsys):
    first = run(text="Call Ana\n\n", day="2026-09-30")
    hello = _window_hello(home=first.home, day="2026-10-01")
    hello.STARTUP_DIR, hello.TASKS = mkdtemp(), []
    saved = notes(first.home)
    saved["previous"] = "Call Ana"
    with open(os.path.join(first.home, "notes.json"), "w") as f:
        json.dump(saved, f)
    state, can_save = hello.load()
    answers = iter(["1", "3", "1", "8", "13", "y"])
    hello.ask = lambda prompt: next(answers)
    hello.more_settings(state, can_save)
    out = capsys.readouterr().out
    assert "At 9:00 (now off)" in out and "Also on weekends (now off)" in out
    assert hello.TASKS == ["09:00"]
    hello.more_settings(state, can_save)
    assert notes(first.home)["weekends"] is True
    hello.more_settings(state, can_save)
    assert "previous" not in notes(first.home)
    assert "The earlier plan is forgotten." in capsys.readouterr().out


def test_done_in_the_text_screen_asks_which_of_several():
    p = run(text="Call Ana; send it; book travel\ndone\n1 3\n\n")
    assert "Good. 2 things are off your list. The rest is kept for today." in p.stdout
    saved = notes(p.home)
    assert [i["text"] for i in saved["finished"]] == ["book travel", "Call Ana"]
    assert saved["intent"]["text"] == "send it"
    p = run(text="done\n\n", home=p.home)
    assert "Which did you finish?" not in p.stdout
    assert "send it" in [i["text"] for i in notes(p.home)["finished"]]


def test_a_new_plan_keeps_todays_unfinished_things_and_says_so():
    first = run(text="Call Ana; send it\ndone\n1\nBook travel\n\n")
    assert "Still on your list from before: send it." in first.stdout
    assert notes(first.home)["intent"]["text"] == "Book travel; send it"
    hello = _window_hello(home=first.home, day="2026-10-01")
    visit = hello.Visit()
    assert hello.leftovers(visit.state, "Write report", visit.iso) == [
        "Book travel", "send it"]
    assert hello.leftovers(visit.state, "Book travel; x", visit.iso) == []


def test_a_long_plan_is_cut_at_a_word_and_stray_semicolons_go():
    hello = _load_hello()
    cut = hello.clean("word " * 100)
    assert len(cut) <= hello.MAX_PLAN and cut.endswith("word")
    assert hello.clean("a; ;; b;") == "a; b"


def test_the_text_menu_turns_off_a_reminder_at_a_set_time():
    hello = _window_hello()
    hello.STARTUP_DIR, hello.TASKS = mkdtemp(), []
    visit = hello.Visit()
    visit.reminder_at("09:00")
    assert hello.reminder_on()
    message = hello.Visit.using(*hello.load()).set_reminder(False)
    assert message == "The sign-in reminder is off."
    assert not hello.reminder_on() and "remind_at" not in notes(hello.HOME)


def test_weekend_reminders_are_off_unless_asked_for_and_the_thought_hides_alone():
    hello = _load_hello()
    state = hello.new_state()
    state["nudge"] = True
    saturday = hello.datetime.date(2026, 10, 10)
    assert hello.reminder_due(state, saturday) is None
    state["weekends"] = True
    assert hello.reminder_due(state, saturday) == ""
    p = run(text="\n")
    assert "Thought for today:" in p.stdout
    with open(os.path.join(p.home, "notes.json")) as f:
        saved = json.load(f)
    saved["hide_thought"] = True
    with open(os.path.join(p.home, "notes.json"), "w") as f:
        json.dump(saved, f)
    p = run(text="\n", home=p.home)
    assert "Thought for today:" not in p.stdout and "Try this today:" in p.stdout


def test_the_notification_for_several_things_says_what_open_is_for():
    hello = _load_hello()
    hello.SHOWN = []
    hello.show_reminder("Call Ana; send it", "2026-10-01")
    assert "Open it to tick the ones you did." in hello.SHOWN[0]
    assert "Did you do it?" not in hello.SHOWN[0]


def test_a_plan_carried_from_an_earlier_day_asks_before_it_is_dropped():
    hello = _load_hello()
    state = hello.new_state()
    state["intent"] = {"text": "Fix dock door", "date": "2026-10-02",
                       "since": "2026-10-01"}
    assert hello.leftovers(state, "Ship orders", "2026-10-02") == ["Fix dock door"]
    assert hello.leftovers(state, "fix dock door", "2026-10-02") == []
    del state["intent"]["since"]
    assert hello.leftovers(state, "Ship orders", "2026-10-02") == []


def test_a_long_new_plan_is_kept_whole_before_the_unfinished_ones():
    p = run(text="Call Ana; send it\ndone\n1\n" + "x" * 395 + "\n\n")
    assert notes(p.home)["intent"]["text"] == "x" * 395
    assert "Things left out: 1." in p.stdout


def test_a_cut_after_a_semicolon_saves_the_same_text_it_loads():
    hello = _load_hello()
    cut = hello.clean("x" * 395 + "; next thing")
    assert cut == hello.clean(cut) and not cut.endswith(";")
    many = "; ".join(f"thing {n}" for n in range(60))
    assert "Things left out: " in hello.shortened(many, hello.clean(many))


def test_done_numbers_take_ranges():
    hello = _load_hello()
    assert hello.picked(["1-3"], 4) == [0, 1, 2]
    assert hello.picked(["1", "1", "3"], 3) == [0, 2]
    for wrong in (["2-5"], ["3-1"], ["0"], ["y"], ["1-"]):
        assert hello.picked(wrong, 4) is None
    p = run(text="Call Ana; send it; book travel\ndone\n1-2\n\n")
    assert notes(p.home)["intent"]["text"] == "book travel"


def test_the_text_menu_points_to_its_own_options():
    p = run(text="m\n11\n6\nCall Ana\n\n\n")
    assert "There is no plan to mark as done. Choose 6 to set one." in p.stdout
    assert "Saved. Choose 11 when you finish it" in p.stdout


def test_turning_on_the_sign_in_reminder_keeps_the_timed_one_when_it_fails():
    hello = _window_hello()
    hello.STARTUP_DIR, hello.TASKS = mkdtemp(), []
    visit = hello.Visit()
    visit.reminder_at("09:00")
    hello.remind = lambda on, quiet=False: False
    visit.set_reminder(True)
    assert hello.task_on() and notes(hello.HOME)["remind_at"] == "09:00"


def test_old_no_weekends_scripts_still_work():
    p = run(args=["--set", "no_weekends", "off"])
    assert p.returncode == 0 and notes(p.home).get("weekends") is True
    p = run(args=["--set", "no_weekends", "on"], home=p.home)
    assert p.returncode == 0 and "weekends" not in notes(p.home)


def test_welcome_back_comes_after_a_missed_workday_not_a_weekend():
    hello = _load_hello()
    friday, monday = "2026-10-02", hello.datetime.date(2026, 10, 5)
    assert not hello.missed_a_workday(friday, monday)
    assert hello.missed_a_workday("2026-10-05", hello.datetime.date(2026, 10, 7))
    assert not hello.missed_a_workday("2026-10-05", hello.datetime.date(2026, 10, 6))
    first = run(text="\n", day="2026-10-05")
    assert "Welcome back" in run(text="\n", day="2026-10-07", home=first.home).stdout


def test_a_due_date_is_shown_and_carried_with_the_plan():
    first = run(text="Send the invoice\n\n")
    hello = _window_hello(day="2026-10-01", home=first.home)
    visit = hello.Visit()
    assert visit.set_due("2026-10-05") == "Due Monday, 5 October 2026."
    hello = _window_hello(day="2026-10-02", home=first.home)
    visit = hello.Visit()
    assert visit.answer("no").startswith("Kept for today.")
    assert notes(first.home)["intent"]["due"] == "2026-10-05"
    hello.SHOWN = []
    hello.show_reminder("Send the invoice", "2026-10-02", due=hello.due_note(
        visit.state["intent"], hello.datetime.date(2026, 10, 5)))
    assert "Due today." in hello.SHOWN[0]
    p = run(text="\n", day="2026-10-06", home=first.home)
    assert "It was due Monday, 5 October 2026." in p.stdout
    assert visit.set_due(None) == "The plan has no due date now."
    assert "due" not in notes(first.home)["intent"]


def test_the_export_has_a_spreadsheet_copy_and_can_be_deleted():
    first = run(text="Call Ana; send it\n\n")
    hello = _window_hello(day="2026-10-01", home=first.home)
    hello.EXPORT_DIR = mkdtemp()
    hello.list_separator = lambda: ";"
    visit = hello.Visit()
    assert "ending in .csv" in hello.exported(hello.export_plans(visit.state))
    with open(hello.export_file(".csv"), encoding="utf-8-sig") as f:
        assert f.read().splitlines()[:2] == ["Date;Plan;Due;Finished",
                                             "2026-10-01;Call Ana;;"]
    assert hello.delete_export() == "The plans file you saved is deleted."
    assert not os.listdir(hello.EXPORT_DIR)


def test_formulas_typed_into_a_plan_stay_text_in_the_spreadsheet_copy():
    first = run(text="=HYPERLINK(\"http://x\"); +1+1; @SUM(A1); -2 hours\n\n")
    hello = _window_hello(day="2026-10-01", home=first.home)
    hello.EXPORT_DIR = mkdtemp()
    hello.list_separator = lambda: ","
    hello.export_plans(hello.Visit().state)
    with open(hello.export_file(".csv"), encoding="utf-8-sig", newline="") as f:
        plans = [row[1] for row in csv.reader(f)][1:]
    assert plans == ["'=HYPERLINK(\"http://x\")", "'+1+1", "'@SUM(A1)", "'-2 hours"]


def test_a_date_written_in_a_plan_becomes_its_due_date():
    hello = _load_hello()
    hello.DATE_ORDER = "dmy"
    monday = hello.datetime.date(2026, 10, 26)
    due = hello.typed_due
    assert due("Send boleto 30/10", monday) == "2026-10-30"
    assert due("call bob 2026-10-28", monday) == "2026-10-28"
    assert due("write report by fri", monday) == "2026-10-30"
    assert due("email x due tomorrow", monday) == "2026-10-27"
    assert due("Staff schedule Friday", monday) == "2026-10-30"
    assert due("baby shower gifts; 3.5 hours", monday) is None
    # A date already past, a fraction, or a number months away is no due date.
    assert due("Pay rent 1/10", monday) is None
    assert due("Read 2026-09-01 audit", monday) is None
    assert due("Read chapters 3/4", monday) is None
    assert due("Finish 1/2 of the report", monday) is None
    assert due("Fix 24/7 support rota", monday) is None
    assert due("Pay rent 1/11", monday) == "2026-11-01"
    assert due("Budget 2027-03-01", monday) == "2027-03-01"
    hello.DATE_ORDER = "mdy"
    assert due("Send it 10/30", monday) == "2026-10-30"
    first = run(text="Inventory report by Friday\n\n", day="2026-10-26")
    assert notes(first.home)["intent"]["due"] == "2026-10-30"


def test_done_over_part_of_todays_plan_finishes_that_part_only():
    first = run(text="Call Ana; Send report\n\n")
    hello = _window_hello(day="2026-10-01", home=first.home)
    visit = hello.Visit()
    visit.did_it("send report")
    saved = notes(first.home)
    assert saved["intent"]["text"] == "Call Ana"
    assert [i["text"] for i in saved["finished"]] == ["Send report"]


def test_a_due_date_stays_when_todays_plan_is_corrected():
    first = run(text="Call Ana\n\n")
    hello = _window_hello(day="2026-10-01", home=first.home)
    visit = hello.Visit()
    visit.set_due("2026-10-05")
    visit.save("Call Ana; send the contract")
    assert notes(first.home)["intent"]["due"] == "2026-10-05"


def test_exported_files_are_found_in_any_language_and_digits_never_crash():
    hello = _window_hello(day="2026-10-01")
    hello.EXPORT_DIR = mkdtemp()
    hello.load_languages()
    for name in ("hello-world Pläne.csv", "hello-world plans.md"):
        open(os.path.join(hello.EXPORT_DIR, name), "w").close()
    assert len(hello.exported_files()) == 2
    hello.delete_export()
    assert not os.listdir(hello.EXPORT_DIR)
    assert hello.picked(["\u00b2"], 3) is None


def test_notes_are_locked_on_disk_and_read_back():
    p = run(text="Call my sister about Dad's surgery\n\n", lock="test")
    with open(os.path.join(p.home, "notes.json"), encoding="utf-8") as f:
        raw = f.read()
    assert "sister" not in raw and json.loads(raw)["locked"] == "test"
    later = run(text="\n\n\n", day="2026-10-02", home=p.home, lock="test")
    assert "Call my sister about Dad's surgery" in later.stdout


def test_a_plain_file_from_before_is_read_and_locked_at_the_next_save():
    first = run(text="Book travel\n\n")
    assert notes(first.home)["intent"]["text"] == "Book travel"
    later = run(text="\n\n\n", day="2026-10-02", home=first.home, lock="test")
    assert "Yesterday you planned: Book travel" in later.stdout
    with open(os.path.join(first.home, "notes.json"), encoding="utf-8") as f:
        assert set(json.load(f)) == {"locked", "data"}


def test_notes_locked_to_another_account_are_set_aside_not_lost():
    home = mkdtemp()
    with open(os.path.join(home, "notes.json"), "w", encoding="utf-8") as f:
        json.dump({"locked": "dpapi", "data": "bm90IGEgcmVhbCBibG9i"}, f)
    p = run(text="\n\n", home=home, lock="test")
    assert "locked to a Windows account" in " ".join(p.stdout.split())
    assert any(n.startswith("notes.json.bak") for n in os.listdir(home))


def test_the_welcome_invites_any_plan_only_where_notes_are_locked():
    locked = " ".join(run(text="\n\n", lock="test").stdout.split())
    assert "at work or not" in locked and "not secret" not in locked
    assert "full admin control" in locked
    plain = " ".join(run(text="\n\n").stdout.split())
    assert "not secret" in plain and "at work or not" not in plain


@unittest.skipUnless(os.name == "nt", "the Data Protection API is Windows only")
def test_windows_locks_notes_to_the_account():
    hello = _load_hello()
    hello.LOCK = None
    assert hello.lock_kind() == "dpapi"
    sealed = hello.seal('{"visits": [], "intent": null}')
    assert json.loads(sealed)["locked"] == "dpapi"
    assert hello.unseal(json.loads(sealed)) == {"visits": [], "intent": None}
    hello.POLICY = {"UnlockedNotes": 1}
    assert hello.lock_kind() == "plain"


def _counts_server():
    """The reference counts server on a free local port, in a thread."""
    import importlib.util
    import threading
    path = os.path.join(os.path.dirname(HELLO), "server", "counts_server.py")
    spec = importlib.util.spec_from_file_location("counts_server", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    folder = mkdtemp()
    server = mod.serve(0, folder, "127.0.0.1")
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}", folder


def _utc_today():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).date().isoformat()


def test_the_counts_server_counts_each_pc_once_a_day_and_keeps_only_numbers():
    import urllib.error
    import urllib.request
    server, url, folder = _counts_server()
    day = _utc_today()
    try:
        def call(path, post=False):
            request = urllib.request.Request(url + path, data=b"{}" if post else None,
                                             method="POST" if post else "GET")
            with urllib.request.urlopen(request, timeout=5) as r:
                return json.loads(r.read())
        none = {"love": 0, "ha": 0, "dead": 0, "eyeroll": 0}
        assert call(f"/v1/day/{day}") == {"tip": 0, "react": none}
        assert call(f"/v1/day/{day}/tip", post=True) == {"tip": 1, "react": none}
        assert call(f"/v1/day/{day}/tip", post=True)["tip"] == 1
        # One reaction a PC a day: a second one moves it, the same one is kept.
        assert call(f"/v1/day/{day}/react/love", post=True)["react"] == dict(none, love=1)
        assert call(f"/v1/day/{day}/react/ha", post=True)["react"] == dict(none, ha=1)
        assert call(f"/v1/day/{day}/react/ha", post=True)["react"] == dict(none, ha=1)
        for bad in ("/v1/day/2020-01-01", "/v1/day/nonsense", "/v1/day/../../etc",
                    f"/v1/day/{day}/react/hate"):
            try:
                call(bad)
                raise AssertionError(bad)
            except urllib.error.HTTPError as e:
                assert e.code == 404, bad
        with open(os.path.join(folder, f"{day}.json"), encoding="utf-8") as f:
            assert json.load(f) == {"tip": 1, "react": dict(none, ha=1)}
        assert os.listdir(folder) == [f"{day}.json"]
    finally:
        server.shutdown()


def test_the_text_screen_offers_the_shared_count_and_counts_the_tip():
    server, url, _ = _counts_server()
    day = _utc_today()
    policy = {"SharedCountsServer": url}
    try:
        p = run(text="y\nCall Ana about the secret project\ntip\n\n", day=day, policy=policy)
        out = " ".join(p.stdout.split())
        assert "See how many people do each day's tip?" in out
        assert "People who did today's tip so far: 0" in out
        assert "Counted. People who did today's tip so far: 1" in out
        saved = notes(p.home)
        assert saved["shared"] is True and saved["tip_day"] == day
        # Typed again the same day, it isn't counted twice.
        again = run(text="tip\n\n", day=day, policy=policy, home=p.home)
        assert "so far: 1" in again.stdout
        # Someone who says no is asked once and sends nothing.
        q = run(text="n\n\n\n", day=day, policy=policy)
        assert "Menu option 12 can turn it on later." in q.stdout
        assert "so far" not in q.stdout and "shared" not in notes(q.home)
        assert "See how many" not in run(text="\n\n", day=day, policy=policy,
                                         home=q.home).stdout
    finally:
        server.shutdown()


def test_without_a_server_or_with_the_policy_nothing_is_asked_or_sent():
    assert "See how many" not in run(text="\n\n\n").stdout
    server, url, folder = _counts_server()
    try:
        p = run(text="\n\n\n", day=_utc_today(),
                policy={"SharedCountsServer": url, "TurnOffSharedCounts": 1})
        assert "See how many" not in p.stdout and not os.listdir(folder)
    finally:
        server.shutdown()
    hello = _load_hello()
    for address in ("http://counts.example.com", "ftp://x", "counts.example.com"):
        hello.POLICY = {"SharedCountsServer": address}
        assert hello.counts_server() == "", address
    hello.POLICY = {"SharedCountsServer": "https://counts.example.com/"}
    assert hello.counts_server() == "https://counts.example.com"


def test_an_unreachable_server_shows_nothing_and_does_not_stall():
    import time
    start = time.time()
    p = run(text="y\n\ntip\n\n", day=_utc_today(),
            policy={"SharedCountsServer": "http://127.0.0.1:9"})
    assert "so far" not in p.stdout.split("Counted")[0]
    assert "can't be reached just now" in p.stdout
    assert time.time() - start < 15


def test_the_window_counts_the_tip():
    server, url, _ = _counts_server()
    day = _utc_today()
    try:
        first = run(text="y\n\n\n", day=day, policy={"SharedCountsServer": url})
        hello = _window_hello(day=day, home=first.home)
        hello.POLICY = {"SharedCountsServer": url}
        visit = hello.Visit()
        # The numbers come in the background; the window doesn't wait.
        assert visit.counts_thread is not None
        items, _ = hello.Window(visit).layout()
        texts = {cid: text for _, cid, text, *_ in items}
        assert texts[hello.Window.TIP_COUNT] == "Counting..."
        visit.counts_thread.join(5)
        assert visit.tip_people == 0
        assert visit.did_tip() == "Counted. People who did today's tip so far: 1"
        assert visit.tip_people == 1
        assert visit.shared_switch() == "Nothing is sent, and no count shows."
        assert "shared" not in notes(first.home)
    finally:
        server.shutdown()


def test_reactions_stay_hidden_until_this_pc_reacts():
    server, url, _ = _counts_server()
    day = _utc_today()
    policy = {"SharedCountsServer": url}
    try:
        first = run(text="y\n\n\n", day=day, policy=policy)
        out = " ".join(first.stdout.split())
        assert "React to the thought: type love, ha, dead or eyeroll" in out
        assert "Reactions so far" not in out
        p = run(text="\U0001F480\n\n", day=day, policy=policy, home=first.home)
        out = " ".join(p.stdout.split())
        assert "Reactions so far: love 0, ha 0, dead 1, eyeroll 0" in out
        saved = notes(p.home)
        assert saved["react_day"] == day and saved["react"] == "dead"
        # Changing it moves the one reaction, and the counts now show.
        again = run(text="love\n\n", day=day, policy=policy, home=first.home)
        out = " ".join(again.stdout.split())
        assert out.count("Reactions so far: love 0, ha 0, dead 1, eyeroll 0") == 1
        assert "Reactions so far: love 1, ha 0, dead 0, eyeroll 0" in out
    finally:
        server.shutdown()


def test_yesterdays_top_reaction_shows_and_the_window_reacts():
    import datetime
    server, url, folder = _counts_server()
    day = _utc_today()
    yesterday = (datetime.date.fromisoformat(day) - datetime.timedelta(days=1)).isoformat()
    with open(os.path.join(folder, f"{yesterday}.json"), "w", encoding="utf-8") as f:
        json.dump({"tip": 3, "react": {"love": 2, "ha": 5}}, f)
    try:
        first = run(text="y\n\n\n", day=day, policy={"SharedCountsServer": url})
        assert "Yesterday's top reaction: ha" in " ".join(first.stdout.split())
        hello = _window_hello(day=day, home=first.home)
        hello.POLICY = {"SharedCountsServer": url}
        visit = hello.Visit()
        visit.counts_thread.join(5)
        assert visit.yesterday_top == "ha"
        window = hello.Window(visit)
        assert window.react_label("love") == "\u2764\ufe0f love"
        assert visit.react("love") == "Reactions so far: love 1, ha 0, dead 0, eyeroll 0"
        assert visit.reacted()
        assert window.react_label("love") == "\u2713 \u2764\ufe0f 1"
        assert window.react_label("ha") == "\U0001F602 0"
    finally:
        server.shutdown()


def _handoff(text, when, folder, policy=None, home=None, lock="plain"):
    policy = {"ShiftHandoff": 1, **(policy or {})}
    return run(text=text, day=when[:10], home=home, policy=policy, lock=lock,
               extra={"NOW": when, "HANDOFF_DIR": folder})


def test_shift_handoff_is_off_unless_the_organization_turns_it_on():
    p = run(text="\nhandoff\n\n")
    assert "Shift handoff" not in p.stdout and "Left for the next shift" not in p.stdout
    assert '"handoff" is not one of the choices' in p.stdout


def test_a_handoff_note_is_shown_to_the_next_person_with_its_age():
    folder = mkdtemp()
    first = _handoff("\nhandoff\nForklift 2 pulling left; Dave out Thu\nn\n\n",
                     "2026-10-06T22:40", folder)
    out = " ".join(first.stdout.split())
    assert "No handoff notes in the last 72 hours." in out
    assert "Everyone who uses this PC sees handoff notes." in out
    assert "Not a safety or defect record." in out
    assert "Note left for the next shift, 22:40." in out
    # Someone else, with their own notes, on the same PC the next morning.
    later = _handoff("\n\n", "2026-10-07T06:55", folder)
    assert "1. 8 h ago: Forklift 2 pulling left; Dave out Thu" in later.stdout
    assert "Forklift" not in json.dumps(notes(later.home))


def test_old_handoff_notes_go_but_kept_ones_stay_until_cleared():
    folder = mkdtemp()
    _handoff("\nhandoff\nBlocked fire door by dock 3\ny\n\n", "2026-10-01T08:00", folder)
    _handoff("\nhandoff\nAisle 9 short on pallets\nn\n\n", "2026-10-01T09:00", folder)
    p = _handoff("\n\n", "2026-10-05T09:00", folder)
    assert "Kept until cleared. Blocked fire door" in p.stdout
    assert "Aisle 9" not in p.stdout and "4 d ago" in p.stdout
    shorter = _handoff("\n\n", "2026-10-02T10:00", folder, {"HandoffHours": 24})
    assert "Aisle 9" not in shorter.stdout
    cleared = _handoff("\nhandoff\nclear\n1\n\n", "2026-10-05T09:05", folder)
    assert "Cleared." in cleared.stdout
    assert "Blocked fire door" not in _handoff("\n\n", "2026-10-05T09:10", folder).stdout


def test_handoff_keeps_the_last_five_and_is_locked_to_the_pc():
    folder = mkdtemp()
    for n in range(7):
        _handoff(f"\nhandoff\nNote {n}\nn\n\n", f"2026-10-05T0{n}:00", folder, lock="test")
    with open(os.path.join(folder, "handoff.json"), encoding="utf-8") as f:
        raw = f.read()
    assert "Note" not in raw and json.loads(raw)["locked"] == "test"
    p = _handoff("\n\n", "2026-10-05T08:00", folder, lock="test")
    assert "Note 6" in p.stdout and "Note 2" in p.stdout and "Note 1" not in p.stdout


def test_a_unit_folder_shares_plain_notes_between_pcs():
    unit = mkdtemp()
    _handoff("\nhandoff\nBladder scanner in 22\nn\n\n", "2026-10-05T07:00", mkdtemp(),
             {"HandoffFolder": unit}, lock="test")
    with open(os.path.join(unit, "handoff.json"), encoding="utf-8") as f:
        assert "Bladder scanner in 22" in f.read()
    other_pc = _handoff("\n\n", "2026-10-05T07:30", mkdtemp(), {"HandoffFolder": unit})
    assert "Bladder scanner in 22" in other_pc.stdout


def test_a_new_handoff_note_opens_hello_world_but_your_own_does_not():
    folder = mkdtemp()
    hello = _window_hello(day="2026-10-02")
    hello.POLICY, hello.NOW, hello.HANDOFF_DIR = {"ShiftHandoff": 1}, "2026-10-02T07:00", folder
    state, can_save = hello.load()
    assert not hello.new_handoff(state)
    hello.leave_handoff("Mine", state=state, can_save=can_save)
    assert not hello.new_handoff(state)
    # Someone else's note, from another Windows login.
    hello.NOW = "2026-10-02T07:30"
    hello.leave_handoff("Theirs")
    state, _ = hello.load()
    assert hello.new_handoff(state)
    # Showing the window counts as seeing them, and that is saved.
    hello.Visit()
    state, _ = hello.load()
    assert state["handoff_seen"] == "2026-10-02T07:30"
    assert not hello.new_handoff(state)
    # On a shared login nobody can be told apart, so any note opens it.
    hello.POLICY["HandoffSharedLogin"] = 1
    assert hello.new_handoff(state)


def test_signing_adds_the_first_name_only_to_new_notes():
    folder = mkdtemp()
    hello = _window_hello(day="2026-10-02")
    hello.POLICY, hello.NOW, hello.HANDOFF_DIR = {"ShiftHandoff": 1}, "2026-10-02T07:00", folder
    hello.first_name = lambda: "Ana"
    hello.leave_handoff("Before the policy")
    hello.POLICY["HandoffSignNames"] = 1
    hello.leave_handoff("Dock door sticks")
    texts = [n["text"] for n in hello.read_handoff()]
    assert texts == ["Before the policy", "Dock door sticks (Ana)"]
    items, _ = hello.Window(hello.Visit()).layout()
    rules = {cid: text for _, cid, text, *_ in items}[hello.Window.HANDOFF_RULES]
    assert "Your first name will be shown with your note." in rules
    # Never on a shared login, where the name would be the login's.
    hello.POLICY["HandoffSharedLogin"] = 1
    assert not hello.signing()
    hello.leave_handoff("Scanner in 22")
    assert hello.read_handoff()[-1]["text"] == "Scanner in 22"


def test_the_window_shows_handoff_notes():
    folder = mkdtemp()
    _handoff("\nhandoff\nPump recall done\nn\n\n", "2026-10-02T06:00", folder)
    hello = _window_hello(day="2026-10-02")
    hello.POLICY, hello.NOW, hello.HANDOFF_DIR = {"ShiftHandoff": 1}, "2026-10-02T07:00", folder
    items, _ = hello.Window(hello.Visit()).layout()
    texts = {cid: text for _, cid, text, *_ in items}
    assert "1 h ago: Pump recall done" in texts[hello.Window.HANDOFF]
    assert hello.Window.HANDOFF_LEAVE in texts
    assert hello.leave_handoff("Scanner in 22", keep=True) == "Note left for the next shift, 07:00."
    assert hello.clear_handoff(9) == "Nothing changed."

def test_a_new_plan_is_never_overdue_the_moment_it_is_saved():
    p = run(text="Pay rent 1/10\n\n\n", day="2026-10-05")
    assert "It was due" not in p.stdout
    assert "due" not in notes(p.home)["intent"]


def test_not_sure_keeps_the_plan_without_a_mark_and_offers_quiet_once():
    first = run(text="Call the dentist\n\n")
    p = run(text="?\n\n\n", day="2026-10-02", home=first.home)
    out = " ".join(p.stdout.split())
    assert "Yesterday you planned: Call the dentist" in out
    assert "? if you're not sure" in out
    assert "That's fine. It's kept for today." in out
    assert "Prefer no follow-up questions? Type gentle at the end" in out
    saved = notes(first.home)
    assert saved["intent"]["text"] == "Call the dentist" and "done" not in saved
    assert saved["unsure"] == [{"text": "Call the dentist", "date": "2026-10-01"}]
    again = run(text="n\n\n\n\n", day="2026-10-03", home=first.home)
    assert "Prefer no follow-up questions?" not in again.stdout


def test_the_question_names_the_day_with_its_date():
    first = run(text="Ask Linda about the folder\n\n", day="2026-10-02")
    p = run(text="\n\n\n", day="2026-10-05", home=first.home)
    assert "On Friday, 2 October 2026 you planned: Ask Linda" in " ".join(p.stdout.split())


def test_no_follow_up_questions_stops_asking_and_folds_old_plans_away():
    first = run(text="Reply to Dana\ngentle\n\n")
    assert "It won't ask about your plans." in first.stdout
    assert notes(first.home)["gentle"] is True
    p = run(text="\n\n\n", day="2026-10-02", home=first.home)
    assert "Did you do it?" not in p.stdout and "Still open since" in p.stdout
    q = run(text="\nplan\nCall mum Sunday\n\n", day="2026-10-03", home=first.home)
    assert "Due" not in q.stdout and "due" not in notes(first.home)["intent"]
    r = run(text="\n\n\n", day="2026-10-07", home=first.home)
    assert "Earlier plan: Call mum Sunday" in r.stdout and "Still open" not in r.stdout
    assert "put away" not in r.stdout
    assert notes(first.home)["previous"] == "Call mum Sunday"


def test_what_i_did_shows_every_day_and_a_done_can_be_taken_back():
    hello = _window_hello(day="2026-10-05")
    hello.PRINTED = []
    state = {"visits": [], "intent": {"text": "Ask Linda", "date": "2026-10-05"},
             "streak": False, "done": 1,
             "finished": [{"text": "Called the dentist", "date": "2026-10-02"}],
             "unsure": [{"text": "Posted the letter", "date": "2026-10-01"}]}
    page = hello.what_i_did(state, hello.datetime.date(2026, 10, 5))
    assert page[0] == "What I did"
    assert page[1] == "Monday, 5 October 2026: Ask Linda (still open)"
    assert "Friday, 2 October 2026: Called the dentist (done)" in page
    assert "Thursday, 1 October 2026: Posted the letter (not sure)" in page
    assert "Saturday, 3 October 2026: nothing noted" in page and len(page) == 15
    assert hello.print_page(page) == "Sent to the printer."
    assert hello.PRINTED[0].startswith("What I did\n")
    with open(os.path.join(hello.HOME, "notes.json"), "w") as f:
        json.dump(state, f)
    state, can_save = hello.load()
    message = hello.take_back(state, can_save, state["finished"][0], hello.datetime.date(2026, 10, 5))
    assert message == "Taken back. It's on today's plan again."
    saved = notes(hello.HOME)
    assert "finished" not in saved and saved["intent"]["text"] == "Ask Linda; Called the dentist"


def test_the_window_has_not_sure_and_large_text():
    first = run(text="Write the report\n\n")
    hello = _window_hello(home=first.home)
    visit = hello.Visit()
    assert visit.followup == "Write the report"
    items, _ = hello.Window(visit).layout()
    texts = {cid: text for _, cid, text, *_ in items}
    assert texts[hello.Window.UNSURE] == "I'm not s&ure"
    assert texts[hello.Window.PLANNED] == "Yesterday you planned: Write the report"
    message = visit.answer("unsure")
    assert message.startswith("That's fine. It's kept for today.")
    assert "Options > What the window shows" in message
    assert notes(first.home)["unsure"][0]["text"] == "Write the report"
    plain = hello.Window(visit).template()
    visit.state["large_text"] = True
    large = hello.Window(visit).template()
    assert plain != large


def test_the_support_line_is_in_the_menu_only_when_set():
    p = run(text="\nm\n\n\n", policy={"SupportLine": "Employee Assistance: 0800 123 456"})
    assert ("If things feel heavy, someone to talk to: Employee Assistance: 0800 123 456"
            in " ".join(p.stdout.split()))
    assert "If things feel heavy" not in run(text="\nm\n\n\n").stdout


def test_the_reminder_leaves_the_plan_out_unless_it_is_turned_on():
    import xml.etree.ElementTree as ET
    first = run(text="Report & slides\n\n")
    hello = _window_hello(home=first.home)
    hello.SHOWN = []
    state, _ = hello.load()
    state["plan_in_reminder"] = True
    hello.save(state)
    assert hello.sign_in() == 0
    texts = [t.text for t in ET.fromstring(hello.SHOWN[0]).iter("text")]
    assert texts == ["Yesterday you planned: Report & slides", "Did you do it?"]


def test_the_command_line_sets_shows_and_finishes_a_plan():
    p = run(["plan", "Fix flaky test; review PR 88 by Friday"], day="2026-10-05")
    assert p.returncode == 0
    assert "Saved. Due Friday, 9 October 2026: review PR 88 by Friday" in p.stdout
    shown = run(["plan"], day="2026-10-05", home=p.home)
    assert shown.stdout.splitlines()[:2] == ["1  Fix flaky test", "2  review PR 88 by Friday"]
    data = json.loads(run(["plan", "--json"], day="2026-10-05", home=p.home).stdout)
    assert data == {"version": 2, "date": "2026-10-05", "due": "2026-10-09", "things": [
        {"n": 1, "text": "Fix flaky test", "due": None, "done": False},
        {"n": 2, "text": "review PR 88 by Friday", "due": "2026-10-09", "done": False}]}
    assert run(["add", "ship 1.2"], day="2026-10-05", home=p.home).returncode == 0
    again = run(["add", "Ship 1.2"], day="2026-10-05", home=p.home)
    assert "already on the plan" in again.stdout
    # A bare done on several things refuses, so a standup never overstates.
    bare = run(["done"], day="2026-10-05", home=p.home)
    assert bare.returncode == 2 and "done all" in bare.stdout
    assert run(["done", "7"], day="2026-10-05", home=p.home).returncode == 2
    two = run(["done", "2"], day="2026-10-05", home=p.home)
    assert two.stdout.strip() == "Done: review PR 88 by Friday. The rest is kept for today."
    assert notes(p.home)["intent"]["text"] == "Fix flaky test; ship 1.2"
    assert run(["done", "all"], day="2026-10-05", home=p.home).returncode == 0
    assert notes(p.home)["intent"] is None
    assert run(["done"], day="2026-10-05", home=p.home).returncode == 1
    assert run(["plan"], day="2026-10-05", home=p.home).stdout.strip() == "No plan for today."


def test_the_command_line_respects_plans_turned_off():
    p = run(["plan", "Anything"], policy={"DisablePlans": 1})
    assert p.returncode == 1 and "Plans are turned off by your organization." in p.stdout


def test_todo_txt_import_reads_open_tasks_and_never_duplicates():
    folder = mkdtemp()
    path = os.path.join(folder, "todo.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("(A) 2026-10-01 Call Ana +hiring @phone due:2026-10-08\n"
                "x 2026-10-02 Done already\n\n"
                "Review PR 88; carefully +core\n"
                "Write the RFC due:2026-10-20\n")
    listed = run(["import", path], day="2026-10-05")
    assert listed.returncode == 2
    assert "1  Call Ana +hiring @phone (due:2026-10-08)" in listed.stdout
    assert "Done already" not in listed.stdout
    p = run(["import", path, "--pick", "1", "2"], day="2026-10-05", home=listed.home)
    assert p.returncode == 0
    assert "Due Thursday, 8 October 2026: Call Ana +hiring @phone" in p.stdout
    saved = notes(p.home)["intent"]
    assert saved["text"] == "Call Ana +hiring @phone; Review PR 88, carefully +core"
    assert saved["due"] == "2026-10-08"
    assert saved["dues"] == {"Call Ana +hiring @phone": "2026-10-08"}
    # Running it again adds only what isn't there yet.
    again = run(["import", path, "--pick", "1-3"], day="2026-10-05", home=p.home)
    assert notes(again.home)["intent"]["text"].count("Call Ana") == 1
    assert notes(again.home)["intent"]["text"].endswith("; Write the RFC")
    with open(path, encoding="utf-8") as f:
        assert "x 2026-10-02 Done already" in f.read()
    typed = run(["import", path], text="3\n", day="2026-10-05")
    assert notes(typed.home)["intent"]["text"] == "Write the RFC"
    assert run(["import", os.path.join(folder, "missing.txt")]).returncode == 1


def _git(folder, *args, when=None, email="pri@example.com"):
    env = dict(os.environ, GIT_AUTHOR_NAME="P", GIT_COMMITTER_NAME="P",
               GIT_AUTHOR_EMAIL=email, GIT_COMMITTER_EMAIL=email)
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    subprocess.run(["git", "-C", folder, *args], check=True, env=env,
                   capture_output=True)


def test_standup_covers_since_the_last_workday_with_commits_from_several_repos():
    if not shutil.which("git"):
        raise unittest.SkipTest("needs git")
    root = mkdtemp()
    for name in ("api", "web"):
        repo = os.path.join(root, name)
        os.makedirs(repo)
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "pri@example.com")
        _git(repo, "commit", "-q", "--allow-empty", "-m", f"old {name}",
             when="2026-09-30T10:00:00")
        _git(repo, "commit", "-q", "--allow-empty", "-m", f"fix {name} flake",
             when="2026-10-02T10:00:00")
        _git(repo, "commit", "-q", "--allow-empty", "-m", "someone else",
             when="2026-10-02T11:00:00", email="other@example.com")
    # Friday's plan, finished Friday; Monday's standup covers Friday.
    p = run(["plan", "Fix flaky test; review PR 88"], day="2026-10-02")
    run(["done", "1"], day="2026-10-02", home=p.home)
    up = run(["standup", "--git", "--repos", os.path.join(root, "*")],
             day="2026-10-05", home=p.home)
    assert up.returncode == 0
    assert up.stdout.splitlines() == [
        "Since Friday, 2 October 2026:", "- Fix flaky test", "Commits:",
        "- api: fix api flake", "- web: fix web flake", "Today:", "- review PR 88"]
    # Remembered, a plain standup uses the same repos, and --author adds more.
    run(["standup", "--repos", os.path.join(root, "*"), "--author", "pri@example.com",
         "other@example.com", "--remember"], day="2026-10-05", home=p.home)
    assert notes(p.home)["standup"]["git"] is True
    data = json.loads(run(["standup", "--json"], day="2026-10-05", home=p.home).stdout)
    assert data["since"] == "2026-10-02" and len(data["commits"]) == 4
    off = run(["standup", "--no-git"], day="2026-10-05", home=p.home)
    assert "Commits:" not in off.stdout
    assert run(["standup", "--bogus"], day="2026-10-05", home=p.home).returncode == 2


def test_export_prints_plain_text_to_grep():
    p = run(["plan", "Fix flaky test; review PR 88"], day="2026-10-05")
    run(["done", "1"], day="2026-10-05", home=p.home)
    out = run(["export"], day="2026-10-06", home=p.home).stdout.splitlines()
    assert out == ["2026-10-05\tdone\tFix flaky test", "2026-10-05\topen\treview PR 88"]


def test_the_bash_shim_is_written_the_same_by_both_installers():
    shims = []
    for name in ("install.ps1", "install-user.ps1"):
        with open(os.path.join(os.path.dirname(__file__), name), encoding="utf-8") as f:
            block = re.search(r"\$shim = @\(\r?\n(.*?)\r?\n\s*\)", f.read(), re.S).group(1)
        shims.append([line.strip().rstrip(",")[1:-1].replace("''", "'")
                      for line in block.splitlines()])
    assert shims[0] == shims[1] and shims[0][0] == "#!/usr/bin/env bash"
    check = subprocess.run(["bash", "-n"], input="\n".join(shims[0]) + "\n", text=True)
    assert check.returncode == 0


def test_the_desk_pet_is_opt_in_gets_things_and_never_dies():
    p = run(text="Call bank\n\n", day="2026-10-05")
    assert "(o.o)" not in p.stdout
    on = run(text="pet\ny\nBiscuit\n\n", day="2026-10-05", home=p.home)
    out = " ".join(on.stdout.split())
    assert "Say hello to Biscuit." in out
    assert "5 more finished things until Biscuit's next surprise." in out
    done = run(text="done\n\n", day="2026-10-05", home=p.home)
    assert "(o.o) Biscuit does a little hop." in " ".join(done.stdout.split())
    # Four more things, and the fifth brings the first one, which it wears.
    run(["plan", "a; b; c; d"], day="2026-10-05", home=p.home)
    fifth = run(text="done\ny\n\n", day="2026-10-05", home=p.home)
    out = " ".join(fifth.stdout.split())
    assert "(o.o)~ Biscuit got a scarf!" in out
    assert "5 more finished things until Biscuit's next surprise." in out
    # Days away: it slept, and nothing is lost.
    back = run(text="\n\n", day="2026-10-12", home=p.home)
    assert "(o.o)~ Biscuit slept while you were away and is glad you're here." in \
        " ".join(back.stdout.split())
    off = run(text="pet\noff\n\n", day="2026-10-12", home=p.home)
    assert "It keeps its things for next time." in " ".join(off.stdout.split())
    assert "(o.o)" not in run(text="\n\n", day="2026-10-13", home=p.home).stdout
    again = run(text="pet\ny\n\n\n", day="2026-10-13", home=p.home)
    assert "Say hello to Biscuit." in " ".join(again.stdout.split())
    assert notes(p.home)["pet"]["done"] == 5


def test_pet_items_never_run_out():
    hello = _load_hello()
    count = len(hello.PET_LOOKS)
    assert hello.pet_item(0)[0] == "a scarf"
    assert hello.pet_item(count)[0] == "a scarf, in a new colour"


def test_plans_put_aside_are_plain_and_come_back_by_number():
    p = run(text="Clean the garage\n\n", day="2026-10-05")
    run(text="n\nn\nWrite the report\n\n", day="2026-10-06", home=p.home)
    listed = run(text="aside\n1\n\n", day="2026-10-06", home=p.home)
    out = " ".join(listed.stdout.split())
    assert "1. Clean the garage, put aside Tuesday, 6 October 2026." in out
    assert "It " not in out.split("put aside Tuesday, 6 October 2026.")[1][:4]
    assert "Back on today's plan: Clean the garage" in out
    assert notes(p.home)["intent"]["text"] == "Write the report; Clean the garage"
    assert "put_aside" not in notes(p.home)


def test_funny_farewells_are_a_switch_and_never_with_no_follow_up():
    hello = _load_hello()
    state = {"intent": None, "put_aside": [{"text": "Organize Drive", "date": "2026-10-05"}]}
    plain = hello.aside_lines(state)[1][0]
    assert plain == "1. Organize Drive, put aside Monday, 5 October 2026."
    state["farewells"] = True
    funny = hello.aside_lines(state)[1][0]
    assert funny.startswith(plain + " It ")
    for word in ("Here lies", "RIP", "gave up", "good idea at the time"):
        assert all(word not in line for line in hello.farewells())
    state["gentle"] = True
    assert hello.aside_lines(state)[1][0] == plain


def test_the_boss_adapts_to_last_week_and_falls():
    import datetime
    server, url, folder = _counts_server()
    today = datetime.date.fromisoformat(_utc_today())
    monday = today - datetime.timedelta(days=today.weekday())
    try:
        import urllib.request

        def week(when):
            with urllib.request.urlopen(f"{url}/v1/week/{when}", timeout=5) as r:
                return json.loads(r.read())
        assert week(monday.isoformat()) == {"hp": 20, "hits": 0, "defeated": None}
        # Last week had 100 tips: this week's boss has 70.
        for n in range(1, 8):
            with open(os.path.join(folder, f"{monday - datetime.timedelta(days=n)}.json"),
                      "w", encoding="utf-8") as f:
                json.dump({"tip": 100 // 7 + (1 if n <= 100 % 7 else 0)}, f)
        with open(os.path.join(folder, f"{monday}.json"), "w", encoding="utf-8") as f:
            json.dump({"tip": 80}, f)
        assert week(monday.isoformat()) == {"hp": 70, "hits": 80, "defeated": monday.isoformat()}
        for bad in ((monday - datetime.timedelta(days=14)).isoformat(),
                    (monday + datetime.timedelta(days=1)).isoformat()):
            try:
                week(bad)
                raise AssertionError(bad)
            except urllib.error.HTTPError as e:
                assert e.code == 404
        # The text screen names the boss, and every pet gets the trophy.
        p = run(text="y\n\npet\ny\n\n\n", day=today.isoformat(), policy={"SharedCountsServer": url})
        hello = _load_hello()
        name, trophy = hello.bosses()[hello.boss_index(monday)]
        again = run(text="\n\n", day=today.isoformat(), home=p.home,
                    policy={"SharedCountsServer": url})
        out = " ".join(again.stdout.split())
        assert f"{name} fell on" in out and "Everyone did that." in out
        assert f"Pip is showing off {trophy}." in out
        assert notes(p.home)["pet"]["trophies"] == [monday.isoformat()]
    finally:
        server.shutdown()


def test_the_window_shows_the_pet_under_the_plan_and_fetches_the_boss():
    server, url, _ = _counts_server()
    day = _utc_today()
    try:
        first = run(text="y\nCall bank\npet\ny\nBiscuit\n\n", day=day,
                    policy={"SharedCountsServer": url})
        hello = _window_hello(day=day, home=first.home)
        hello.POLICY = {"SharedCountsServer": url}
        visit = hello.Visit()
        visit.counts_thread.join(5)
        assert visit.boss["hp"] == 20
        assert hello.boss_line(visit.boss).endswith("0 of 20 hit points gone, from everyone's tips.")
        items, _ = hello.Window(visit).layout()
        ids = [cid for _, cid, *_ in items]
        assert ids.index(hello.Window.PET) > ids.index(hello.Window.PLAN)
        texts = {cid: text for _, cid, text, *_ in items}
        assert texts[hello.Window.PET].startswith("(o.o)  Biscuit ")
        assert "Biscuit does a little hop." in (visit.finish_parts(["Call bank"]) and visit.pet_text)
    finally:
        server.shutdown()


def test_things_finished_together_list_in_plan_order():
    p = run(["plan", "Call Ana; send it; book travel"], day="2026-10-05")
    run(["done", "all"], day="2026-10-05", home=p.home)
    out = run(["standup"], day="2026-10-06", home=p.home).stdout.splitlines()
    assert out[1:4] == ["- Call Ana", "- send it", "- book travel"]
    shown = run(text="m\n1\n\n\n", day="2026-10-06", home=p.home).stdout
    assert shown.index("Call Ana") < shown.index("send it") < shown.index("book travel")


def test_back_after_months_is_welcomed_back_not_as_new():
    p = run(text="Call the bank\n\n", day="2026-06-01")
    later = run(text="\n\n", day="2026-10-01", home=p.home)
    out = " ".join(later.stdout.split())
    assert "Welcome back. Glad you are here." in out
    assert "Welcome. Each day" not in out
    assert "Call the bank" in out


def test_a_deadline_word_after_the_day_reads_in_chinese_japanese_and_korean():
    # 2026-10-05 is a Monday.
    for lang, plan, due in (("ja", "報告書を金曜まで", "2026-10-09"),
                            ("ja", "見積もりを明日までに", "2026-10-06"),
                            ("ja", "金額を確認する", None),
                            ("ko", "보고서 금요일까지", "2026-10-09"),
                            ("ko", "보고서를 내일까지", "2026-10-06"),
                            ("zh", "周五前交报告", "2026-10-09"),
                            ("zh", "明天之前回复", "2026-10-06")):
        p = run(["plan", plan], day="2026-10-05", lang=lang)
        assert notes(p.home)["intent"].get("due") == due, (lang, plan)


def test_a_due_date_belongs_to_the_thing_it_is_written_in():
    p = run(["plan", "call the bank by Friday; water plants; ship 1.2 by tomorrow"], day="2026-10-05")
    saved = notes(p.home)["intent"]
    assert saved["due"] == "2026-10-06"
    assert saved["dues"] == {"call the bank by Friday": "2026-10-09",
                             "ship 1.2 by tomorrow": "2026-10-06"}
    assert "Due tomorrow: ship 1.2 by tomorrow" in p.stdout
    # Finishing the thing with the nearest date moves to the next one.
    done = run(["done", "3"], day="2026-10-05", home=p.home)
    assert done.returncode == 0
    saved = notes(p.home)["intent"]
    assert saved["due"] == "2026-10-09" and list(saved["dues"]) == ["call the bank by Friday"]
    shown = run(["plan"], day="2026-10-05", home=p.home).stdout
    assert "Due Friday, 9 October 2026: call the bank by Friday" in shown
    run(["done", "1"], day="2026-10-05", home=p.home)
    saved = notes(p.home)["intent"]
    assert saved["text"] == "water plants" and "due" not in saved and "dues" not in saved
