import json
import os
import subprocess
import sys
import tempfile
import unittest

HELLO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hello.py")


def run(args=(), text=None, day="2026-10-01", home=None, startup=None):
    """Run hello.py with its own data folder. text is typed at the prompts."""
    home = home or tempfile.mkdtemp()
    env = dict(os.environ, HELLO_HOME=home, HELLO_TODAY=day)
    if startup:
        env["HELLO_STARTUP_DIR"] = startup
    if text is not None:
        env["HELLO_INTERACTIVE"] = "1"
    p = subprocess.run([sys.executable, HELLO, *args], input=text,
                       capture_output=True, text=True, env=env)
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
        return subprocess.run([sys.executable, HELLO, *args], stdout=w,
                              stderr=w if dead_stderr else subprocess.PIPE,
                              stdin=subprocess.DEVNULL,
                              env=dict(os.environ, HELLO_HOME=tempfile.mkdtemp()))
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
    p = run()  # stdin is not a terminal here
    assert p.returncode == 0 and "> " not in p.stdout
    assert notes(p.home)["intent"] is None


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


def test_skipping_the_follow_up_clears_the_plan():
    first = run(text="Send the invoice\n\n")
    run(text="\n\n\n", day="2026-10-02", home=first.home)
    assert notes(first.home)["intent"] is None


def test_in_a_row_line_appears_on_the_third_visit_only():
    home = tempfile.mkdtemp()
    outs = [run(text="\n\n", day=f"2026-10-0{n}", home=home).stdout
            for n in (1, 2, 3)]
    assert "in a row" not in outs[0] and "in a row" not in outs[1]
    assert "3 times in a row" in outs[2]
    run(["--streak", "off"], home=home)
    assert "in a row" not in run(text="\n\n", day="2026-10-04", home=home).stdout


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


def test_unknown_option_exits_2():
    p = run(["--nope"])
    assert p.returncode == 2 and "--help" in p.stdout


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
    p = subprocess.run([sys.executable, HELLO], stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                       env=dict(os.environ, HELLO_HOME=tempfile.mkdtemp()),
                       preexec_fn=lambda: os.close(1))
    assert p.returncode == 1
    assert p.stderr.startswith(b"hello.py: cannot write to stdout:")


def test_stdout_closed_after_start_exits_1():
    # sys.stdout.close() makes print() raise ValueError, not OSError
    code = ("import runpy, sys; sys.stdout.close(); "
            f"runpy.run_path({HELLO!r}, run_name='__main__')")
    p = subprocess.run([sys.executable, "-c", code], stderr=subprocess.PIPE,
                       stdin=subprocess.DEVNULL,
                       env=dict(os.environ, HELLO_HOME=tempfile.mkdtemp()))
    assert p.returncode == 1
    assert p.stderr.startswith(b"hello.py: cannot write to stdout:")


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
            except unittest.SkipTest as e:
                print(f"SKIPPED {name}: {e}")
            except AssertionError:
                failed += 1
                print(f"FAILED {name}")
                import traceback
                traceback.print_exc()
    print("FAILED" if failed else "ok")
    sys.exit(1 if failed else 0)
