"""The shared counts server for hello-world: "212 people did today's tip".

Run it anywhere Python 3.11 or later runs, behind any https front end
(a reverse proxy, a cloud load balancer, or a platform that terminates TLS):

    python counts_server.py --port 8080 --data ./counts

Then point hello-world at the https address, through the SharedCountsServer
Group Policy, or COUNTS_SERVER in hello.py for a package of your own.

It keeps one small JSON file per day holding only numbers. It never writes a
network address to disk. To count each PC once per day it keeps, in memory
only, a hash of the address with a random key made fresh each day, so the
hashes can't be matched to addresses or across days, and are gone at a
restart or at midnight UTC.

    GET  /v1/day/2026-10-05             {"tip": 212, "react": {"love": 4, ...}}
    POST /v1/day/2026-10-05/tip         counts one, then the same answer
    POST /v1/day/2026-10-05/react/love  one reaction a PC a day; a second
                                        moves it rather than adding one
    GET  /health                        {"ok": true}

The reactions are love, ha, dead and eyeroll.

Only today and the day either side, in UTC, are accepted, so time zones work
and nobody can fill the disk with old dates.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REACTIONS = ("love", "ha", "dead", "eyeroll")
DAY_PATH = re.compile(r"^/v1/day/(\d{4}-\d{2}-\d{2})(/tip|/react/(?:%s))?$" % "|".join(REACTIONS))


class Counts:
    """The day files and today's in-memory set of who already counted."""

    def __init__(self, folder):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        self.lock = threading.Lock()
        self.salt_day = None
        self.salt = b""
        # Hash of who counted, mapped to the reaction they gave, or True.
        self.seen = {}

    def path(self, day):
        return os.path.join(self.folder, f"{day}.json")

    def read(self, day):
        """The day's numbers: {"tip": n, "react": {reaction: n}}."""
        try:
            with open(self.path(day), encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            data = {}
        tip = data.get("tip")
        react = data.get("react") if isinstance(data.get("react"), dict) else {}
        return {"tip": tip if isinstance(tip, int) and tip >= 0 else 0,
                "react": {r: react[r] if isinstance(react.get(r), int) and react[r] >= 0 else 0
                          for r in REACTIONS}}

    def add(self, day, what, address):
        """Count the tip once a PC a day, or set its one reaction, moving it
        when it changes. Returns the day's numbers."""
        with self.lock:
            today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
            if self.salt_day != today:
                # A fresh key each day forgets yesterday's hashes for good.
                self.salt_day, self.salt, self.seen = today, secrets.token_bytes(32), {}
            kind = "tip" if what == "tip" else "react"
            key = hashlib.sha256(self.salt + f"{day}|{kind}|{address}".encode()).digest()
            data = self.read(day)
            before = self.seen.get(key)
            if kind == "tip" and before is None:
                data["tip"] += 1
            elif kind == "react" and before != what:
                if before in data["react"]:
                    data["react"][before] = max(0, data["react"][before] - 1)
                data["react"][what] += 1
            else:
                return data
            self.seen[key] = True if kind == "tip" else what
            tmp = self.path(day) + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f)
            os.replace(tmp, self.path(day))
            return data


def allowed(day):
    try:
        when = datetime.date.fromisoformat(day)
    except ValueError:
        return False
    today = datetime.datetime.now(datetime.timezone.utc).date()
    return abs((when - today).days) <= 1


def handler(counts):
    class Handler(BaseHTTPRequestHandler):
        server_version = "hello-world-counts"
        sys_version = ""

        def reply(self, status, body=None):
            raw = json.dumps(body).encode() if body is not None else b""
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)

        def route(self):
            match = DAY_PATH.match(self.path)
            if not match or not allowed(match.group(1)):
                return None, None
            return match.group(1), match.group(2)

        def do_GET(self):
            if self.path == "/health":
                return self.reply(200, {"ok": True})
            day, add = self.route()
            if day is None or add:
                return self.reply(404, {"error": "not found"})
            self.reply(200, counts.read(day))

        def do_POST(self):
            # Bodies are ignored, and refused when large, so nothing else
            # can be sent here.
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                length = -1
            if not 0 <= length <= 1024:
                return self.reply(413, {"error": "too large"})
            self.rfile.read(length)
            day, add = self.route()
            if day is None or not add:
                return self.reply(404, {"error": "not found"})
            # Behind a proxy every request comes from the proxy, so the
            # address it passes on counts instead, when it is set to.
            address = self.client_address[0]
            if self.server.trust_proxy:
                address = (self.headers.get("X-Forwarded-For") or address).split(",")[0].strip()
            what = "tip" if add == "/tip" else add.rsplit("/", 1)[1]
            self.reply(200, counts.add(day, what, address))

        def log_message(self, format, *args):
            # No access log: it would hold addresses.
            pass

    return Handler


def serve(port=8080, folder="counts", host="0.0.0.0", trust_proxy=False):
    server = ThreadingHTTPServer((host, port), handler(Counts(folder)))
    server.trust_proxy = trust_proxy
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--data", default="counts", help="folder for the day files")
    parser.add_argument("--trust-proxy", action="store_true",
                        help="count by X-Forwarded-For, behind your own https proxy")
    args = parser.parse_args(argv)
    server = serve(args.port, args.data, args.host, args.trust_proxy)
    print(f"hello-world counts on {args.host}:{server.server_address[1]}, data in {args.data}")
    server.serve_forever()


if __name__ == "__main__":
    main()
