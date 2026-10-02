import json
import os
import subprocess
import sys
import tempfile
import unittest

HELLO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hello.py")

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


def run(args=(), text=None, day="2026-10-01", home=None, startup=None):
    """Run hello.py with its own data folder. text is typed at the prompts.

    Without text, stdin is the null device, so the result doesn't depend on
    what the test runner's own stdin is.
    """
    home = home or tempfile.mkdtemp()
    values = {"TODAY": day, "HOME": home, "STARTUP_DIR": startup,
              "FORCE_INTERACTIVE": text is not None}
    stdin = {"input": text} if text is not None else {"stdin": subprocess.DEVNULL}
    p = subprocess.run(launch(args, **values), capture_output=True,
                       encoding="utf-8", **stdin)
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
        return subprocess.run(launch(args, HOME=tempfile.mkdtemp()), stdout=w,
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
    assert "Welcome." in p.stdout and "sends nothing anywhere" in p.stdout
    assert "Thought for today:" in p.stdout and "Try this today:" in p.stdout
    saved = notes(p.home)
    assert saved["visits"] == ["2026-10-01"]
    assert saved["intent"] == {"text": "Send the invoice", "date": "2026-10-01"}


def test_output_is_plain_ascii_and_short():
    p = run(text="\n\n")
    assert p.stdout.isascii()
    assert all(len(line) <= 72 for line in p.stdout.splitlines() if "> " not in line)
    assert "!" not in p.stdout.replace("Hello, world!", "")


def test_no_prompts_and_no_waiting_without_a_person():
    # stdin is the null device, which Windows also reports as a terminal
    p = run()
    assert p.returncode == 0 and "> " not in p.stdout
    assert p.stdout.startswith("Hello, world!")
    # nothing is recorded, so the next real visit still gets its questions
    assert not os.path.exists(os.path.join(p.home, "notes.json"))


def test_hello_variables_in_the_environment_are_ignored():
    home = tempfile.mkdtemp()
    other = tempfile.mkdtemp()
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
    assert "Last time you planned: Send the invoice" in p.stdout
    assert notes(first.home)["intent"]["text"] == "Call back"
    assert notes(first.home)["visits"] == ["2026-10-01", "2026-10-02"]


def test_next_day_not_done_can_be_kept():
    first = run(text="Send the invoice\n\n")
    p = run(text="n\ny\n\n", day="2026-10-02", home=first.home)
    assert "What is one thing" not in p.stdout
    assert notes(first.home)["intent"] == {"text": "Send the invoice",
                                           "date": "2026-10-02"}


def test_in_a_row_line_appears_at_milestones_only():
    home = tempfile.mkdtemp()
    outs = [run(text="\n\n", day=f"2026-10-0{n}", home=home).stdout
            for n in range(1, 8)]
    shown = [n for n, out in enumerate(outs, 1) if "in a row" in out]
    assert shown == [3, 7]
    assert "3 times in a row" in outs[2]
    home = tempfile.mkdtemp()
    for n in (1, 2):
        run(text="\n\n", day=f"2026-10-0{n}", home=home)
    run(["--streak", "off"], home=home)
    assert "in a row" not in run(text="\n\n", day="2026-10-03", home=home).stdout


def test_streak_option_exit_codes():
    assert run(["--streak", "off"]).returncode == 0
    blocker = tempfile.NamedTemporaryFile()
    bad = run(["--streak", "off"], home=os.path.join(blocker.name, "sub"))
    assert bad.returncode == 1 and "Could not save" in bad.stdout


def test_remind_exit_code_follows_the_result():
    startup = tempfile.mkdtemp()
    assert run(["--remind", "on"], startup=startup).returncode == 0
    assert run(["--remind", "off"], startup=startup).returncode == 0


def test_p_at_the_last_prompt_sets_the_plan():
    home = tempfile.mkdtemp()
    run(text="\np\nWrite the report\n", home=home)
    assert notes(home)["intent"]["text"] == "Write the report"


def test_a_notes_file_with_a_byte_order_mark_is_read_not_moved_aside():
    home = tempfile.mkdtemp()
    with open(os.path.join(home, "notes.json"), "w", encoding="utf-8-sig") as f:
        json.dump({"visits": ["2026-09-30"], "intent": None}, f)
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
    home = tempfile.mkdtemp()
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
    home = tempfile.mkdtemp()
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
    assert not os.path.exists(os.path.join(first.home, "notes.json"))
    assert run(["--reset"], home=first.home).returncode == 1


def test_menu_shows_saved_data_and_toggles_the_in_a_row_line():
    first = run(text="Send the invoice\n\n")
    p = run(text="y\nBuy milk\nm\n1\n3\n\n", home=first.home, day="2026-10-02")
    assert "Options" in p.stdout and "Buy milk" in p.stdout
    assert notes(first.home)["streak"] is False


def test_reminder_writes_and_removes_only_the_launcher():
    startup = tempfile.mkdtemp()
    path = os.path.join(startup, "hello-world-daily.cmd")
    run(["--remind", "on"], startup=startup)
    with open(path) as f:
        text = f.read()
    assert text.startswith("@echo off") and text.rstrip().endswith("--startup")
    assert "hello.cmd" in text
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
                                           "date": "2026-10-02"}
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
    assert os.listdir(first.home) == []


def test_menu_does_not_save_over_a_file_it_could_not_read():
    home = tempfile.mkdtemp()
    os.mkdir(os.path.join(home, "notes.json"))  # opening it fails
    p = run(text="\nm\n3\n6\nCall the bank\n\n", home=home)
    assert p.stdout.count("Could not save") == 2
    assert os.path.isdir(os.path.join(home, "notes.json"))


def test_friendly_yes_words_count():
    for word in ("yep", "Yes!", "done", "ya"):
        first = run(text="Book travel\n\n")
        p = run(text=word + "\n\n\n", day="2026-10-02", home=first.home)
        assert "Last time you planned: Book travel" in p.stdout
        assert notes(first.home)["intent"] is None, word


def test_a_hostile_notes_file_cannot_write_controls_to_the_screen():
    home = tempfile.mkdtemp()
    bad = {"visits": ["2026-09-30"],
           "intent": {"text": "\x1b[31mEVIL\r\nFAKE", "date": "2026-09-30"}}
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump(bad, f)
    p = run(text="y\n\n\n", home=home)
    assert "\x1b" not in p.stdout and "\r" not in p.stdout
    assert "Last time you planned: [31mEVIL FAKE" in p.stdout
    assert "\x1b" not in run(["--stats"], home=home).stdout


def test_pasted_tabs_and_odd_spaces_become_spaces():
    p = run(text="call\tBob\u00a0now\n\n")
    assert notes(p.home)["intent"]["text"] == "call Bob now"


def test_very_deep_json_gives_a_fresh_start_and_keeps_a_copy():
    home = tempfile.mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        f.write("[" * 200000)
    p = run(text="\n\n", home=home)
    assert p.returncode == 0 and "Welcome." in p.stdout
    assert os.path.exists(os.path.join(home, "notes.json.bak"))


def test_a_damaged_file_is_kept_as_a_backup():
    home = tempfile.mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        f.write('{"visits":["2026-10-0')
    run(text="\n\n", home=home)
    with open(os.path.join(home, "notes.json.bak")) as f:
        assert f.read() == '{"visits":["2026-10-0'


def test_a_bad_plan_date_does_not_turn_the_in_a_row_line_back_on():
    home = tempfile.mkdtemp()
    bad = {"visits": ["2026-10-01", "2026-10-02"],
           "intent": {"text": "x", "date": "junk"}, "streak": False}
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump(bad, f)
    p = run(text="\n\n", day="2026-10-03", home=home)
    assert "in a row" not in p.stdout
    assert notes(home)["streak"] is False


def test_odd_date_spellings_are_normalised():
    home = tempfile.mkdtemp()
    with open(os.path.join(home, "notes.json"), "w") as f:
        json.dump({"visits": ["20261001"], "intent": None}, f)
    run(text="\n\n", home=home)
    assert notes(home)["visits"] == ["2026-10-01"]


def test_long_plans_wrap_within_72_columns():
    first = run(text="word " * 24 + "\n\n")
    p = run(text="\n\n\n", day="2026-10-02", home=first.home)
    assert all(len(x) <= 72 for x in p.stdout.splitlines() if "> " not in x)


def test_a_plan_dated_in_the_future_becomes_todays_plan():
    home = tempfile.mkdtemp()
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
    p = subprocess.run(launch(HOME=tempfile.mkdtemp()), stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                       preexec_fn=lambda: os.close(1))
    assert p.returncode == 1
    assert p.stderr.startswith(b"hello.py: cannot write to stdout:")


def test_stdout_closed_after_start_exits_1():
    # sys.stdout.close() makes print() raise ValueError, not OSError
    p = subprocess.run(launch(prelude="sys_ = __import__('sys'); sys_.stdout.close()\n",
                              HOME=tempfile.mkdtemp()),
                       stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    assert p.returncode == 1
    assert p.stderr.startswith(b"hello.py: cannot write to stdout:")


def _load_hello(day="2026-10-01"):
    import importlib.util
    spec = importlib.util.spec_from_file_location("hello_mod", HELLO)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.TODAY = day
    return mod


def test_future_visits_are_kept_in_the_file_but_not_counted():
    home = tempfile.mkdtemp()
    path = os.path.join(home, "notes.json")
    with open(path, "w") as f:
        json.dump({"visits": ["2026-09-30", "2030-01-01"]}, f)
    p = run(text="\n", day="2026-10-01", home=home)
    assert "opened this" not in p.stdout
    with open(path) as f:
        saved = json.load(f)["visits"]
    assert saved == ["2026-09-30", "2026-10-01", "2030-01-01"]


def test_a_plan_of_only_joiners_is_empty_and_a_long_plan_says_it_was_cut():
    hello = _load_hello()
    assert hello.clean("\u200d \u200c") == ""
    p = run(text="x" * 130 + "\n\n")
    assert "Shortened to 120 characters." in p.stdout


def test_a_second_damaged_file_does_not_overwrite_the_first_backup():
    hello = _load_hello()
    hello.HOME = tempfile.mkdtemp()
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
    home = tempfile.mkdtemp()
    hello.HOME = home
    os.makedirs(os.path.dirname(hello.data_file()), exist_ok=True)
    with open(hello.data_file(), "w", encoding="utf-8") as f:
        json.dump({"visits": ["2026-09-30", "2030-01-01"]}, f)
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


def test_cut_plan_has_no_trailing_space():
    import hello
    assert hello.clean("a" * 119 + " b") == "a" * 119


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
