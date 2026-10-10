"""Write phone/content.js from hello.py, so the phone shows the same
thought and tip as the PC on the same day, in every language hello.py has.

    python tools/build_phone.py

The tests fail when phone/content.js is out of date with hello.py.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import hello  # noqa: E402


def content():
    langs = {"en": {"thoughts": list(hello.THOUGHTS), "tips": list(hello.TIPS)}}
    for code, data in sorted(hello.LANGUAGES.items()):
        langs[code] = {"thoughts": list(data["thoughts"]), "tips": list(data["tips"])}
    return {"topics": list(hello.TOPICS), "langs": langs}


def text():
    return ("// Made by tools/build_phone.py from hello.py; don't edit by hand.\n"
            "const CONTENT = " + json.dumps(content(), ensure_ascii=False, indent=1) + ";\n")


def main():
    with open(os.path.join(ROOT, "phone", "content.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
