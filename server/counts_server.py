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
    GET  /v1/week/2026-10-05            {"hp": 150, "hits": 212,
                                         "defeated": "2026-10-08"}
    GET  /health                        {"ok": true}

    GET    /v1/sync/<64 hex>   one device's encrypted copy, for sync
    PUT    /v1/sync/<64 hex>   replace it (at most 64 kB)
    DELETE /v1/sync/<64 hex>   remove it

Sync copies are encrypted on the PC or phone before they're sent, with a
key this server never sees; the label is made from the same secret. Each is
one file in the sync folder; a copy untouched for a year is removed.

    GET    /v1/push/key            the server's public key for Web Push
    PUT    /v1/push/<32 hex>       {"endpoint": "https://...", "times": ["07:00"]}
    DELETE /v1/push/<32 hex>       stop and forget it

A phone that turns on its reminder sends a random token of its own, its
browser's push address and up to two times of day in UTC, and nothing else:
no plan, no language, no time zone. At each time the server sends a push
with no content at all; the phone itself decides what to show from what it
keeps on the phone. Push addresses are only accepted at the browser makers'
push services, so the server can't be used to call anywhere else. A push
service that says the address is gone, turning the reminder off, or a year
untouched removes the file.

With --phone FOLDER it also serves the phone app (the repository's phone
folder) at /phone/, so one https address does both. The phone app keeps its
plans on the phone and asks this server for nothing.

The week is the boss fight: every tip anyone does that week is one hit. Its
hit points are 70% of last week's tips, at least 20, so a small company can
win too, or a fixed number with --boss-hp. It is worked out from the day
files, so nothing more is stored.

The reactions are love, ha, dead and eyeroll.

Only today and the day either side, in UTC, are accepted, so time zones work
and nobody can fill the disk with old dates.
"""

import argparse
import base64
import datetime
import hashlib
import json
import os
import re
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REACTIONS = ("love", "ha", "dead", "eyeroll")
SYNC_PATH = re.compile(r"^/v1/sync/([0-9a-f]{64})$")
MAX_SYNC = 64_000
SYNC_DAYS = 366
PUSH_PATH = re.compile(r"^/v1/push/([0-9a-f]{32})$")
PUSH_TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
MAX_PUSH_TIMES = 2
# The browser makers' push services; nothing else is ever called.
PUSH_HOSTS = ("fcm.googleapis.com", "push.services.mozilla.com", "push.apple.com",
              "notify.windows.com")
# Who runs this server, for the push services (the VAPID "sub" claim).
PUSH_CONTACT = "https://github.com/thrash-d/hello-world"
WEEK_PATH = re.compile(r"^/v1/week/(\d{4}-\d{2}-\d{2})$")
BOSS_FLOOR = 20
DAY_PATH = re.compile(r"^/v1/day/(\d{4}-\d{2}-\d{2})(/tip|/react/(?:%s))?$" % "|".join(REACTIONS))


class Counts:
    """The day files and today's in-memory set of who already counted."""

    def __init__(self, folder, boss_hp=None):
        self.folder = folder
        self.boss_hp = boss_hp
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

    def week(self, monday):
        """The week's boss: its hit points, the hits so far, and the day it
        fell, if it did."""
        start = datetime.date.fromisoformat(monday)
        tips = [self.read((start + datetime.timedelta(days=n)).isoformat())["tip"]
                for n in range(-7, 7)]
        hp = self.boss_hp or max(BOSS_FLOOR, round(sum(tips[:7]) * 0.7))
        total, defeated = 0, None
        for n, hits in enumerate(tips[7:]):
            total += hits
            if defeated is None and total >= hp:
                defeated = (start + datetime.timedelta(days=n)).isoformat()
        return {"hp": hp, "hits": total, "defeated": defeated}

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


# ECDSA on P-256 with SHA-256 (ES256), for the Web Push VAPID signature,
# with only the standard library.
P256_P = 2**256 - 2**224 + 2**192 + 2**96 - 1
P256_N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
P256_B = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
P256_G = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
          0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)


def _add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    p = P256_P
    if a[0] == b[0] and (a[1] + b[1]) % p == 0:
        return None
    if a == b:
        m = (3 * a[0] * a[0] - 3) * pow(2 * a[1], -1, p) % p
    else:
        m = (b[1] - a[1]) * pow(b[0] - a[0], -1, p) % p
    x = (m * m - a[0] - b[0]) % p
    return x, (m * (a[0] - x) - a[1]) % p


def _mul(k, point):
    out = None
    while k:
        if k & 1:
            out = _add(out, point)
        point = _add(point, point)
        k >>= 1
    return out


def on_curve(point):
    x, y = point
    return (y * y - (x ** 3 - 3 * x + P256_B)) % P256_P == 0


def p256_public(d):
    """The uncompressed public point, 65 bytes."""
    x, y = _mul(d, P256_G)
    return b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")


def es256_sign(d, message):
    """r || s, 64 bytes, as JWS wants."""
    e = int.from_bytes(hashlib.sha256(message).digest(), "big")
    while True:
        k = secrets.randbelow(P256_N - 1) + 1
        r = _mul(k, P256_G)[0] % P256_N
        s = pow(k, -1, P256_N) * (e + r * d) % P256_N
        if r and s:
            return r.to_bytes(32, "big") + s.to_bytes(32, "big")


def es256_verify(public, message, signature):
    if len(public) != 65 or public[0] != 4 or len(signature) != 64:
        return False
    q = (int.from_bytes(public[1:33], "big"), int.from_bytes(public[33:], "big"))
    r, s = int.from_bytes(signature[:32], "big"), int.from_bytes(signature[32:], "big")
    if not (on_curve(q) and 0 < r < P256_N and 0 < s < P256_N):
        return False
    e = int.from_bytes(hashlib.sha256(message).digest(), "big")
    w = pow(s, -1, P256_N)
    point = _add(_mul(e * w % P256_N, P256_G), _mul(r * w % P256_N, q))
    return point is not None and point[0] % P256_N == r


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def push_address_ok(endpoint):
    """An https address at a browser maker's push service, and nothing else."""
    try:
        url = urllib.parse.urlsplit(endpoint)
        port = url.port
    except (ValueError, TypeError):
        return False
    host = (url.hostname or "").lower()
    return (url.scheme == "https" and len(endpoint) <= 1000 and not url.username
            and port in (None, 443)
            and any(host == h or host.endswith("." + h) for h in PUSH_HOSTS))


class Push:
    """Reminders for phones: a file per random token with the push address
    and up to two UTC times, and a key pair for the VAPID signature."""

    def __init__(self, folder):
        self.folder = os.path.join(folder, "push")
        os.makedirs(self.folder, exist_ok=True)
        self.lock = threading.Lock()
        key = os.path.join(folder, "vapid.json")
        try:
            with open(key, encoding="utf-8") as f:
                self.d = int(json.load(f)["d"], 16)
        except (OSError, ValueError, KeyError, TypeError):
            self.d = secrets.randbelow(P256_N - 1) + 1
            tmp = key + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"d": format(self.d, "064x")}, f)
            os.replace(tmp, key)
        self.public = p256_public(self.d)

    def path(self, token):
        return os.path.join(self.folder, token)

    def save(self, token, data):
        """Keep a phone's push address and times. False when they aren't
        acceptable."""
        if not isinstance(data, dict) or not push_address_ok(data.get("endpoint", "")):
            return False
        times = data.get("times")
        if (not isinstance(times, list) or not 1 <= len(times) <= MAX_PUSH_TIMES
                or not all(isinstance(t, str) and PUSH_TIME.match(t) for t in times)):
            return False
        with self.lock:
            tmp = self.path(token) + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"endpoint": data["endpoint"], "times": sorted(set(times))}, f)
            os.replace(tmp, self.path(token))
        return True

    def forget(self, token):
        with self.lock:
            try:
                os.remove(self.path(token))
            except FileNotFoundError:
                pass

    def header(self, endpoint, now):
        """The Authorization header for one push service."""
        url = urllib.parse.urlsplit(endpoint)
        head = b64url(json.dumps({"typ": "JWT", "alg": "ES256"}).encode())
        claims = b64url(json.dumps({"aud": f"{url.scheme}://{url.netloc}",
                                    "exp": int(now) + 12 * 3600,
                                    "sub": PUSH_CONTACT}).encode())
        signed = f"{head}.{claims}".encode()
        jwt = f"{head}.{claims}.{b64url(es256_sign(self.d, signed))}"
        return f"vapid t={jwt}, k={b64url(self.public)}"

    def send(self, endpoint, now):
        """One push with no content. The push service's status, or 0."""
        request = urllib.request.Request(endpoint, data=b"", method="POST", headers={
            "TTL": "3600", "Urgency": "normal", "Content-Length": "0",
            "Authorization": self.header(endpoint, now)})
        try:
            with urllib.request.urlopen(request, timeout=10) as answer:
                return answer.status
        except urllib.error.HTTPError as e:
            return e.code
        except (OSError, ValueError):
            return 0

    def due(self, when, send=None):
        """Send every reminder set for the UTC minute `when`, once each.
        Returns how many were sent."""
        send = send or self.send
        minute = when.strftime("%H:%M")
        stamp = when.strftime("%Y-%m-%dT%H:%M")
        sent = 0
        for token in os.listdir(self.folder):
            if not re.fullmatch(r"[0-9a-f]{32}", token):
                continue
            path = self.path(token)
            try:
                if time.time() - os.path.getmtime(path) > SYNC_DAYS * 86400:
                    self.forget(token)
                    continue
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                continue
            if minute not in data.get("times", []) or data.get("sent") == stamp:
                continue
            status = send(data["endpoint"], when.timestamp())
            if status in (404, 410):
                # The phone unsubscribed or the browser dropped it.
                self.forget(token)
                continue
            sent += 1
            data["sent"] = stamp
            with self.lock:
                if os.path.exists(path):
                    tmp = path + ".tmp"
                    with open(tmp, "w", encoding="utf-8") as f:
                        json.dump(data, f)
                    # The file's time stays the phone's last visit.
                    stat = os.stat(path)
                    os.replace(tmp, path)
                    os.utime(path, (stat.st_atime, stat.st_mtime))
        return sent

    def run(self):
        """Check each minute, in a thread for as long as the server runs."""
        while True:
            now = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)
            try:
                self.due(now)
            except OSError:
                pass
            time.sleep(60 - datetime.datetime.now().second + 1)


def this_week(monday):
    """A Monday whose week holds today or a day either side, in UTC."""
    try:
        start = datetime.date.fromisoformat(monday)
    except ValueError:
        return False
    today = datetime.datetime.now(datetime.timezone.utc).date()
    return (start.weekday() == 0
            and start - datetime.timedelta(days=1) <= today <= start + datetime.timedelta(days=7))


def allowed(day):
    try:
        when = datetime.date.fromisoformat(day)
    except ValueError:
        return False
    today = datetime.datetime.now(datetime.timezone.utc).date()
    return abs((when - today).days) <= 1


PHONE_FILES = {"index.html": "text/html; charset=utf-8", "app.js": "text/javascript; charset=utf-8",
               "content.js": "text/javascript; charset=utf-8", "sw.js": "text/javascript; charset=utf-8",
               "manifest.webmanifest": "application/manifest+json", "icon.svg": "image/svg+xml"}


def handler(counts, phone=None, push=None):
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
            if phone and self.path in ("/phone", "/phone/") or (
                    phone and self.path.startswith("/phone/") and self.path[7:] in PHONE_FILES):
                name = self.path[7:] or "index.html"
                if self.path == "/phone":
                    self.send_response(301)
                    self.send_header("Location", "/phone/")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                with open(os.path.join(phone, name), "rb") as f:
                    raw = f.read()
                self.send_response(200)
                self.send_header("Content-Type", PHONE_FILES[name])
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(raw)
                return
            if self.path == "/v1/push/key" and push:
                return self.reply(200, {"key": b64url(push.public)})
            if SYNC_PATH.match(self.path):
                path = self.sync_file()
                try:
                    if time.time() - os.path.getmtime(path) > SYNC_DAYS * 86400:
                        os.remove(path)
                    with open(path, "rb") as f:
                        raw = f.read(MAX_SYNC)
                except OSError:
                    return self.reply(404, {"error": "not found"})
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(raw)
                return
            if week := WEEK_PATH.match(self.path):
                if not this_week(week.group(1)):
                    return self.reply(404, {"error": "not found"})
                return self.reply(200, counts.week(week.group(1)))
            day, add = self.route()
            if day is None or add:
                return self.reply(404, {"error": "not found"})
            self.reply(200, counts.read(day))

        def body(self):
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                return None
            if not 0 <= length <= MAX_SYNC:
                return None
            return self.rfile.read(length)

        def sync_file(self):
            match = SYNC_PATH.match(self.path)
            if not match:
                return None
            folder = os.path.join(counts.folder, "sync")
            os.makedirs(folder, exist_ok=True)
            return os.path.join(folder, match.group(1))

        def do_PUT(self):
            if (match := PUSH_PATH.match(self.path)) and push:
                raw = self.body()
                try:
                    data = json.loads(raw or b"")
                except ValueError:
                    data = None
                if not push.save(match.group(1), data):
                    return self.reply(400, {"error": "not a push address and times"})
                return self.reply(200, {"ok": True})
            path = self.sync_file()
            if path is None:
                return self.reply(404, {"error": "not found"})
            raw = self.body()
            if not raw:
                return self.reply(413, {"error": "too large or empty"})
            tmp = path + ".tmp"
            with open(tmp, "wb") as f:
                f.write(raw)
            os.replace(tmp, path)
            self.reply(200, {"ok": True})

        def do_DELETE(self):
            if (match := PUSH_PATH.match(self.path)) and push:
                push.forget(match.group(1))
                return self.reply(200, {"ok": True})
            path = self.sync_file()
            if path is None:
                return self.reply(404, {"error": "not found"})
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            self.reply(200, {"ok": True})

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


def serve(port=8080, folder="counts", host="0.0.0.0", trust_proxy=False, boss_hp=None, phone=None,
          remind=False):
    """The server. With remind, phones' reminders are kept and sent too."""
    push = Push(folder) if remind else None
    server = ThreadingHTTPServer((host, port), handler(Counts(folder, boss_hp), phone, push))
    server.trust_proxy = trust_proxy
    server.push = push
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--data", default="counts", help="folder for the day files")
    parser.add_argument("--trust-proxy", action="store_true",
                        help="count by X-Forwarded-For, behind your own https proxy")
    parser.add_argument("--boss-hp", type=int, default=None,
                        help="fixed hit points for the weekly boss, instead of 70%% of last week")
    parser.add_argument("--phone", default=None,
                        help="the phone app's folder, served at /phone/")
    parser.add_argument("--remind", action="store_true",
                        help="keep and send phones' reminders, by Web Push with no content")
    args = parser.parse_args(argv)
    server = serve(args.port, args.data, args.host, args.trust_proxy, args.boss_hp, args.phone,
                   args.remind)
    if server.push:
        threading.Thread(target=server.push.run, daemon=True).start()
    print(f"hello-world counts on {args.host}:{server.server_address[1]}, data in {args.data}")
    server.serve_forever()


if __name__ == "__main__":
    main()
