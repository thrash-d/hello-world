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

    POST /v1/growth                 a batch of streak notes, stored as JSON
                                   lines under growth/ and never a network
                                   address. consent must be true. There is
                                   no route that reads them back.

With --phone FOLDER it also serves the phone app (the repository's phone
folder) at /phone/, so one https address does both. The phone app keeps its
plans on the phone. With --growth the served page is told to offer streak
notes to this same server; without it the page keeps its placeholder address.

The week is the boss fight: every tip anyone does that week is one hit. Its
hit points are 70% of last week's tips, at least 20, so a small company can
win too, or a fixed number with --boss-hp. It is worked out from the day
files, so nothing more is stored.

The reactions are love, ha, dead and eyeroll.

Only today and the day either side, in UTC, are accepted, so time zones work
and nobody can fill the disk with old dates.

Counts below --min-group (10) are sent as "few", and larger ones rounded to
5, so in a small office a count before and after can't show who did the tip
(the red team's Ivan IV). The numbers sent out change only once an hour
(--refresh), so checking before and after one person's tap shows nothing
(Noor). The day files keep the exact numbers; they never leave the server.

Writes are limited so nobody can fill the disk (the red team's Capone): at
most --sync-quota encrypted copies in all (an existing one can still be
updated when it's full), 20 new labels and 60 writes a minute from one
address, counted in memory only with the same daily key as the counts, and an
hourly sweep removes copies untouched for a year. The per-address limits
live in memory, so a restart resets them: rate-limit at the https proxy in
front as well.
"""

import argparse
import base64
import ctypes
import ctypes.util
import datetime
import hashlib
import json
import os
import re
import secrets
import stat
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
PUSH_SENT = re.compile(r"^\d{4}-\d{2}-\d{2}T([01]\d|2[0-3]):[0-5]\d$")
MAX_PUSH_TIMES = 2
# A failed push is tried again through this many minutes, then dropped.
PUSH_GRACE_MINUTES = 15
# The browser makers' push services; nothing else is ever called.
PUSH_HOSTS = ("fcm.googleapis.com", "push.services.mozilla.com", "push.apple.com",
              "notify.windows.com")
# Who runs this server, for the push services (the VAPID "sub" claim).
PUSH_CONTACT = "https://github.com/thrash-d/hello-world"
WEEK_PATH = re.compile(r"^/v1/week/(\d{4}-\d{2}-\d{2})$")
BOSS_FLOOR = 20
MIN_GROUP = 10
SYNC_QUOTA = 100_000
NEW_LABELS_A_DAY = 20
WRITES_A_MINUTE = 60
REFRESH = 3600
DAY_PATH = re.compile(r"^/v1/day/(\d{4}-\d{2}-\d{2})(/tip|/react/(?:%s))?$" % "|".join(REACTIONS))


class Counts:
    """The day files and today's in-memory set of who already counted."""

    def __init__(self, folder, boss_hp=None, min_group=MIN_GROUP, sync_quota=SYNC_QUOTA,
                 refresh=REFRESH):
        self.folder = folder
        self.refresh = refresh
        # (day, period) -> the numbers sent out for that day in that period.
        self.published = {}
        self.boss_hp = boss_hp
        self.min_group = min_group
        self.sync_quota = sync_quota
        # Per address, hashed with the daily key: new labels today, and
        # writes in the current minute.
        self.labels_today = {}
        self.minute = (None, {})
        # How many copies each folder holds, counted once and then kept up
        # to date, so a new copy never lists a large folder under the lock.
        self.stored = {}
        # 0777 masked by a 022 umask is 0755, so another account could list
        # the day files. Those files hold the exact counts. The published
        # numbers are the rounded ones. A symlink is not chmod'd: chmod
        # would follow it onto whatever it points at.
        if not os.path.islink(folder):
            os.makedirs(folder, exist_ok=True)
            tighten(folder, 0o700)
        self.lock = threading.Lock()
        # Held while a sync copy is checked and replaced, so two writers
        # can't both pass the same If-Match.
        self.write_lock = threading.Lock()
        self.salt_day = None
        self.salt = b""
        # Hash of who counted, mapped to the reaction they gave, or True.
        self.seen = {}

    def path(self, day):
        return os.path.join(self.folder, f"{day}.json")

    def read(self, day):
        """The day's numbers: {"tip": n, "react": {reaction: n}}."""
        path = self.path(day)
        # open() would follow a symlink and parse whatever it points at.
        if os.path.islink(path):
            data = {}
        else:
            try:
                fd = open_nofollow(path, os.O_RDONLY)
                with os.fdopen(fd, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError, RecursionError):
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
        hp = max(5, self.min_group, 5 * round(hp / 5))
        total, defeated = 0, None
        for n, hits in enumerate(tips[7:]):
            total += hits
            # The day it fell is judged on the rounded total, like the hits
            # sent out, so the two always agree.
            if defeated is None and self.week_hits(total) >= hp:
                defeated = (start + datetime.timedelta(days=n)).isoformat()
        # Rounded like the day counts, and nothing below the minimum group,
        # so a week's numbers can't single out a day's one tip either.
        return {"hp": hp, "hits": self.week_hits(total), "defeated": defeated}

    def week_hits(self, total):
        return 0 if total < self.min_group else 5 * round(total / 5)

    def fresh_salt(self):
        """The daily key, made new at midnight UTC, which also forgets every
        address seen. Call with the lock held."""
        today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        if self.salt_day != today:
            self.salt_day, self.salt, self.seen = today, secrets.token_bytes(32), {}
            self.labels_today = {}

    def shown(self, n):
        """A count as it may leave the server: "few" below the minimum group,
        else rounded to 5."""
        if n <= 0:
            return 0
        if n < self.min_group:
            return "few"
        return max(self.min_group, 5 * round(n / 5))

    def public(self, data):
        return {"tip": self.shown(data["tip"]),
                "react": {r: self.shown(n) for r, n in data["react"].items()}}

    def publish(self, day, week=False):
        """The day's numbers, or the week's boss, as sent out: fixed for each
        refresh period, so they can't be watched for one person's change."""
        make = (lambda: self.week(day)) if week else (lambda: self.public(self.read(day)))
        if not self.refresh:
            return make()
        period = int(time.time() // self.refresh)
        with self.lock:
            key = (week, day, period)
            if key not in self.published:
                self.published = {k: v for k, v in self.published.items() if k[2] == period}
                self.published[key] = make()
            return self.published[key]

    def may_write(self, address, new, kind="sync"):
        """None when this address may write now, else why not: too many
        writes this minute, too many new labels today, or the quota full.
        Call it only for a write that will happen, so a refused body costs
        nothing; `kind` is the folder whose quota counts."""
        with self.lock:
            self.fresh_salt()
            key = hashlib.sha256(self.salt + f"write|{address}".encode()).digest()
            minute = int(time.time() // 60)
            if self.minute[0] != minute:
                self.minute = (minute, {})
            writes = self.minute[1]
            if writes.get(key, 0) >= WRITES_A_MINUTE:
                return 429, "too many writes; try again in a minute"
            if new:
                if self.labels_today.get(key, 0) >= NEW_LABELS_A_DAY:
                    return 429, "too many new copies from here today"
                if self.stored_count(kind) >= self.sync_quota:
                    return 507, "this server is full"
                self.labels_today[key] = self.labels_today.get(key, 0) + 1
                self.stored[kind] += 1
            writes[key] = writes.get(key, 0) + 1
            return None

    def stored_count(self, kind="sync"):
        """Copies in the folder. Call with the lock held."""
        if kind not in self.stored:
            try:
                self.stored[kind] = sum(
                    1 for n in os.listdir(os.path.join(self.folder, kind))
                    if not n.endswith(".tmp"))
            except OSError:
                self.stored[kind] = 0
        return self.stored[kind]

    def sync_count(self):
        with self.lock:
            return self.stored_count("sync")

    def removed(self, kind="sync", n=1):
        """Copies deleted, so the quota frees up."""
        with self.lock:
            if kind in self.stored:
                self.stored[kind] = max(0, self.stored[kind] - n)

    def sweep(self, now=None):
        """Remove encrypted copies untouched for a year, without waiting for
        someone to ask for them. Returns how many went."""
        now = now or time.time()
        folder = os.path.join(self.folder, "sync")
        gone = 0
        try:
            names = os.listdir(folder)
        except OSError:
            return 0
        for name in names:
            path = os.path.join(folder, name)
            try:
                st = os.lstat(path)
                # getmtime follows a link. A link is removed as a link.
                # The file it pointed at is left where it was.
                if stat.S_ISLNK(st.st_mode):
                    os.unlink(path)
                    gone += 1
                    continue
                if now - st.st_mtime > SYNC_DAYS * 86400:
                    os.remove(path)
                    gone += 1
            except OSError:
                pass
        # Counted again next time, which also catches stray temporary files.
        with self.lock:
            self.stored.pop("sync", None)
            self.stored.pop("push", None)
        return gone

    def run_sweep(self):
        while True:
            self.sweep()
            time.sleep(3600)

    def add(self, day, what, address):
        """Count the tip once a PC a day, or set its one reaction, moving it
        when it changes. Returns the day's numbers."""
        with self.lock:
            # A fresh key each day forgets yesterday's hashes for good.
            self.fresh_salt()
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
            # A symlink named for this day is not opened. write_private
            # replaces the link. The file it pointed at is not written.
            if os.path.islink(self.path(day)):
                try:
                    os.unlink(self.path(day))
                except OSError:
                    return data
            write_private(self.path(day), json.dumps(data))
            return data


# ECDSA on P-256 with SHA-256 (ES256), for the Web Push VAPID signature.
# The shipping path is libcrypto's NIST P-256, which is constant-time.
# The pure-Python ladder below does not branch on the scalar. It is not the
# shipping path: CPython's big integers are still variable-time, so it runs
# only when an operator who is not Reed Mallory has taken that residual in
# writing. Reed Mallory does not accept it.
P256_P = 2**256 - 2**224 + 2**192 + 2**96 - 1
P256_N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
P256_B = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
P256_A = (-3) % P256_P
P256_G = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
          0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
# Projective infinity for the complete addition law. Not a secret.
_P256_INF = (0, 1, 0)


class P256Unavailable(OSError):
    """libcrypto is missing and nobody but Reed has taken the other path."""


def _transfer_ok(path, token):
    """True when a regular file names an acceptor who is not Reed Mallory.

    The file is not followed if it is a symlink. `token` is the whole
    `accepts:` line, for example `variable-time-p256`.
    """
    if not path or os.path.islink(path):
        return False
    try:
        info = os.lstat(path)
        if not stat.S_ISREG(info.st_mode) or info.st_size > 4000:
            return False
        with open(path, encoding="utf-8") as handle:
            text = handle.read(4000)
    except (OSError, UnicodeError):
        return False
    acceptor = ""
    accepts = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("acceptor:"):
            acceptor = stripped.split(":", 1)[1].strip()
        if stripped.lower() == f"accepts: {token}":
            accepts = True
    folded = " ".join(acceptor.lower().split())
    if not accepts or not (2 <= len(acceptor) <= 80):
        return False
    if folded == "reed mallory" or folded.startswith("reed mallory "):
        return False
    return True


def p256_variable_time_allowed():
    """The ladder, only with the environment gate and a transfer file."""
    if os.environ.get("HELLO_P256_VARIABLE_TIME") != "1":
        return False
    return _transfer_ok(os.environ.get("HELLO_P256_TRANSFER", ""), "variable-time-p256")


def sync_review_status():
    """`external` only when an operator who is not Reed Mallory says so.

    The internal review is `docs/SYNC-CRYPTO-REVIEW.md`. That file is not
    an outside audit, and this function does not call it one.
    """
    if _transfer_ok(os.environ.get("HELLO_SYNC_EXTERNAL_REVIEW", ""), "sync-external-review"):
        return "external"
    return "internal-only"


def _ct_gt(a, b):
    """1 when a > b, else 0. Both are non-negative and fit in 256 bits."""
    diff = (b - a) & ((1 << 512) - 1)
    return (diff >> 511) & 1


def _ct_select(a, b, bit):
    """a when bit is 1, else b. bit must be 0 or 1."""
    mask = -(bit & 1)
    return (a & mask) | (b & ~mask)


def _low_s(s):
    """The low representative. The choice does not branch on s."""
    return _ct_select(P256_N - s, s, _ct_gt(s, P256_N // 2))


def _libcrypto():
    """The libcrypto this process already uses, or None."""
    if getattr(_libcrypto, "done", False):
        return getattr(_libcrypto, "lib", None)
    _libcrypto.done = True
    _libcrypto.lib = None
    path = None
    try:
        with open("/proc/self/maps", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if "libcrypto" in line and "deleted" not in line:
                    candidate = line.split()[-1]
                    if os.path.exists(candidate):
                        path = candidate
                        break
    except OSError:
        path = None
    if path is None:
        try:
            path = ctypes.util.find_library("crypto")
        except Exception:
            path = None
    if path is None:
        import importlib.util
        import sys
        spec = importlib.util.find_spec("_ssl")
        names = ("libcrypto-3.dll", "libcrypto-3-x64.dll", "libcrypto-1_1.dll",
                 "libcrypto.so.3", "libcrypto.so.1.1", "libcrypto.dylib")
        folders = []
        if spec and spec.origin:
            origin = os.path.dirname(spec.origin)
            folders.extend((origin, os.path.join(os.path.dirname(origin), "DLLs")))
        folders.append(os.path.dirname(sys.executable))
        for folder in folders:
            for name in names:
                candidate = os.path.join(folder, name)
                if os.path.exists(candidate):
                    path = candidate
                    break
            if path:
                break
    if not path:
        return None
    try:
        lib = ctypes.CDLL(path)
        _bind_libcrypto(lib)
        # Touch the curve once so a missing symbol fails here, not mid-sign.
        probe = lib.EC_KEY_new_by_curve_name(415)
        if not probe:
            return None
        lib.EC_KEY_free(probe)
    except (OSError, AttributeError):
        return None
    _libcrypto.lib = lib
    return lib


def _bind_libcrypto(lib):
    """Argument sizes for the NIST P-256 calls. Pointers stay pointer-sized."""
    void = ctypes.c_void_p
    cint = ctypes.c_int
    csize = ctypes.c_size_t
    void_p = ctypes.POINTER(void)

    def bind(name, restype, *args):
        fn = getattr(lib, name)
        fn.restype = restype
        fn.argtypes = list(args)
        return fn

    bind("EC_KEY_new_by_curve_name", void, cint)
    bind("EC_KEY_free", None, void)
    bind("EC_KEY_get0_group", void, void)
    bind("EC_KEY_set_private_key", cint, void, void)
    bind("EC_KEY_set_public_key", cint, void, void)
    bind("EC_POINT_new", void, void)
    bind("EC_POINT_free", None, void)
    bind("EC_POINT_mul", cint, void, void, void, void, void, void)
    bind("EC_POINT_point2oct", csize, void, void, cint, void, csize, void)
    bind("EC_POINT_oct2point", cint, void, void, void, csize, void)
    bind("BN_bin2bn", void, void, cint, void)
    bind("BN_new", void)
    bind("BN_free", None, void)
    bind("BN_bn2binpad", cint, void, void, cint)
    bind("BN_cmp", cint, void, void)
    bind("BN_dup", void, void)
    bind("BN_sub", cint, void, void, void)
    bind("BN_rshift1", cint, void, void)
    bind("BN_CTX_new", void)
    bind("BN_CTX_free", None, void)
    bind("EC_GROUP_get_order", cint, void, void, void)
    bind("ECDSA_do_sign", void, void, cint, void)
    bind("ECDSA_do_verify", cint, void, cint, void, void)
    bind("ECDSA_SIG_new", void)
    bind("ECDSA_SIG_free", None, void)
    bind("ECDSA_SIG_get0", None, void, void_p, void_p)
    bind("ECDSA_SIG_set0", cint, void, void, void)
    if hasattr(lib, "ERR_clear_error"):
        bind("ERR_clear_error", None)


def _bn_bytes(lib, bn):
    buf = ctypes.create_string_buffer(32)
    if lib.BN_bn2binpad(bn, buf, 32) != 32:
        raise OSError("bignum")
    return buf.raw


def _ossl_public(lib, d):
    """Uncompressed point from libcrypto. The scalar multiply is OpenSSL's."""
    key = point = bn = None
    try:
        if hasattr(lib, "ERR_clear_error"):
            lib.ERR_clear_error()
        key = lib.EC_KEY_new_by_curve_name(415)
        raw = int(d).to_bytes(32, "big")
        bn = lib.BN_bin2bn(raw, 32, None)
        if not key or not bn or lib.EC_KEY_set_private_key(key, bn) != 1:
            raise OSError("p256 key")
        group = lib.EC_KEY_get0_group(key)
        point = lib.EC_POINT_new(group)
        if not point or lib.EC_POINT_mul(group, point, bn, None, None, None) != 1:
            raise OSError("p256 mul")
        if lib.EC_KEY_set_public_key(key, point) != 1:
            raise OSError("p256 public")
        buf = ctypes.create_string_buffer(65)
        if lib.EC_POINT_point2oct(group, point, 4, buf, 65, None) != 65:
            raise OSError("p256 encode")
        return buf.raw
    finally:
        if point:
            lib.EC_POINT_free(point)
        if bn:
            lib.BN_free(bn)
        if key:
            lib.EC_KEY_free(key)


def _ossl_sign(lib, d, message):
    """r || s, low s, from ECDSA_do_sign. Retries only when r or s is zero."""
    digest = hashlib.sha256(message).digest()
    key = bn = None
    try:
        key = lib.EC_KEY_new_by_curve_name(415)
        raw = int(d).to_bytes(32, "big")
        bn = lib.BN_bin2bn(raw, 32, None)
        if not key or not bn or lib.EC_KEY_set_private_key(key, bn) != 1:
            raise OSError("p256 key")
        group = lib.EC_KEY_get0_group(key)
        point = lib.EC_POINT_new(group)
        try:
            if not point or lib.EC_POINT_mul(group, point, bn, None, None, None) != 1:
                raise OSError("p256 mul")
            if lib.EC_KEY_set_public_key(key, point) != 1:
                raise OSError("p256 public")
        finally:
            if point:
                lib.EC_POINT_free(point)
        order = lib.BN_new()
        half = lib.BN_new()
        ctx = lib.BN_CTX_new()
        try:
            if (not order or not half or not ctx
                    or lib.EC_GROUP_get_order(group, order, ctx) != 1
                    or lib.BN_rshift1(half, order) != 1):
                raise OSError("p256 order")
            for _ in range(8):
                if hasattr(lib, "ERR_clear_error"):
                    lib.ERR_clear_error()
                sig = lib.ECDSA_do_sign(digest, 32, key)
                if not sig:
                    continue
                try:
                    r_ptr = ctypes.c_void_p()
                    s_ptr = ctypes.c_void_p()
                    lib.ECDSA_SIG_get0(sig, ctypes.byref(r_ptr), ctypes.byref(s_ptr))
                    if lib.BN_cmp(s_ptr, half) > 0:
                        r_copy = lib.BN_dup(r_ptr)
                        s_low = lib.BN_new()
                        if (not r_copy or not s_low
                                or lib.BN_sub(s_low, order, s_ptr) != 1
                                or lib.ECDSA_SIG_set0(sig, r_copy, s_low) != 1):
                            if r_copy:
                                lib.BN_free(r_copy)
                            if s_low:
                                lib.BN_free(s_low)
                            raise OSError("p256 low s")
                        lib.ECDSA_SIG_get0(sig, ctypes.byref(r_ptr), ctypes.byref(s_ptr))
                    r_raw = _bn_bytes(lib, r_ptr)
                    s_raw = _bn_bytes(lib, s_ptr)
                except OSError:
                    lib.ECDSA_SIG_free(sig)
                    raise
                else:
                    lib.ECDSA_SIG_free(sig)
                if int.from_bytes(r_raw, "big") and int.from_bytes(s_raw, "big"):
                    return r_raw + s_raw
        finally:
            if order:
                lib.BN_free(order)
            if half:
                lib.BN_free(half)
            if ctx:
                lib.BN_CTX_free(ctx)
    finally:
        if bn:
            lib.BN_free(bn)
        if key:
            lib.EC_KEY_free(key)
    raise OSError("p256 sign")


def _ossl_verify(lib, public, message, signature):
    digest = hashlib.sha256(message).digest()
    key = point = sig = r_bn = s_bn = None
    try:
        if hasattr(lib, "ERR_clear_error"):
            lib.ERR_clear_error()
        key = lib.EC_KEY_new_by_curve_name(415)
        if not key:
            return False
        group = lib.EC_KEY_get0_group(key)
        point = lib.EC_POINT_new(group)
        if not point or lib.EC_POINT_oct2point(group, point, public, 65, None) != 1:
            return False
        if lib.EC_KEY_set_public_key(key, point) != 1:
            return False
        sig = lib.ECDSA_SIG_new()
        r_bn = lib.BN_bin2bn(signature[:32], 32, None)
        s_bn = lib.BN_bin2bn(signature[32:], 32, None)
        if not sig or not r_bn or not s_bn or lib.ECDSA_SIG_set0(sig, r_bn, s_bn) != 1:
            return False
        # set0 took ownership of both bignums.
        r_bn = s_bn = None
        return lib.ECDSA_do_verify(digest, 32, sig, key) == 1
    except OSError:
        return False
    finally:
        if r_bn:
            lib.BN_free(r_bn)
        if s_bn:
            lib.BN_free(s_bn)
        if sig:
            lib.ECDSA_SIG_free(sig)
        if point:
            lib.EC_POINT_free(point)
        if key:
            lib.EC_KEY_free(key)


def _add_complete(p1, p2):
    """Complete addition on P-256 (Renes, Costello, Batina, a = -3).

    Every step runs for every pair of points, including infinity and P + P.
    The formula is exception-free. It does not look at the scalar.
    """
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    p = P256_P
    b3 = (P256_B * 3) % p
    t0 = (x1 * x2) % p
    t1 = (y1 * y2) % p
    t2 = (z1 * z2) % p
    t3 = (x1 + y1) % p
    t4 = (x2 + y2) % p
    t3 = (t3 * t4) % p
    t4 = (t0 + t1) % p
    t3 = (t3 - t4) % p
    t4 = (x1 + z1) % p
    t5 = (x2 + z2) % p
    t4 = (t4 * t5) % p
    t5 = (t0 + t2) % p
    t4 = (t4 - t5) % p
    t5 = (y1 + z1) % p
    x3 = (y2 + z2) % p
    t5 = (t5 * x3) % p
    x3 = (t1 + t2) % p
    t5 = (t5 - x3) % p
    z3 = (P256_A * t4) % p
    x3 = (b3 * t2) % p
    z3 = (x3 + z3) % p
    x3 = (t1 - z3) % p
    z3 = (t1 + z3) % p
    y3 = (x3 * z3) % p
    t1 = (t0 + t0) % p
    t1 = (t1 + t0) % p
    t2 = (P256_A * t2) % p
    t4 = (b3 * t4) % p
    t1 = (t1 + t2) % p
    t2 = (t0 - t2) % p
    t2 = (P256_A * t2) % p
    t4 = (t4 + t2) % p
    t0 = (t1 * t4) % p
    y3 = (y3 + t0) % p
    t0 = (t5 * t4) % p
    x3 = (t3 * x3) % p
    x3 = (x3 - t0) % p
    t0 = (t3 * t1) % p
    z3 = (t5 * z3) % p
    z3 = (z3 + t0) % p
    return x3 % p, y3 % p, z3 % p


def _select_point(p1, p2, bit):
    return tuple(_ct_select(a, b, bit) for a, b in zip(p1, p2))


def _to_affine(point):
    x, y, z = point
    if z % P256_P == 0:
        return None
    inv = pow(z, P256_P - 2, P256_P)
    return (x * inv) % P256_P, (y * inv) % P256_P


def _mul_ladder(k, affine):
    """Fixed 256-step ladder. The Python path does not branch on bits of k.

    CPython multiplies in variable time. Callers use this only behind
    p256_variable_time_allowed().
    """
    x, y = affine
    base = (x % P256_P, y % P256_P, 1)
    r0, r1 = _P256_INF, base
    for shift in range(255, -1, -1):
        bit = (k >> shift) & 1
        added = _add_complete(r0, r1)
        double0 = _add_complete(r0, r0)
        double1 = _add_complete(r1, r1)
        r0 = _select_point(added, double0, bit)
        r1 = _select_point(double1, added, bit)
    return _to_affine(r0)


def on_curve(point):
    x, y = point
    return (y * y - (x ** 3 - 3 * x + P256_B)) % P256_P == 0


def p256_backend():
    """`openssl` on the shipping path, else `variable-time` or `unavailable`."""
    if _libcrypto():
        return "openssl"
    if p256_variable_time_allowed():
        return "variable-time"
    return "unavailable"


def p256_public(d):
    """The uncompressed public point, 65 bytes."""
    if not isinstance(d, int) or isinstance(d, bool) or not 1 <= d < P256_N:
        raise ValueError("scalar")
    lib = _libcrypto()
    if lib:
        return _ossl_public(lib, d)
    if p256_variable_time_allowed():
        x, y = _mul_ladder(d, P256_G)
        return b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")
    raise P256Unavailable(
        "P-256 needs libcrypto. The variable-time ladder is off. "
        "Reed Mallory has not accepted it.")


def _sign_variable_time(d, message):
    e = int.from_bytes(hashlib.sha256(message).digest(), "big")
    for _ in range(8):
        k = secrets.randbelow(P256_N - 1) + 1
        point = _mul_ladder(k, P256_G)
        r = point[0] % P256_N
        # Fixed exponent. Still not constant-time inside CPython.
        s = _low_s(pow(k, P256_N - 2, P256_N) * (e + r * d) % P256_N)
        if r and s:
            return r.to_bytes(32, "big") + s.to_bytes(32, "big")
    raise OSError("p256 sign")


def es256_sign(d, message):
    """r || s, 64 bytes, low s, as JWS wants."""
    if not isinstance(d, int) or isinstance(d, bool) or not 1 <= d < P256_N:
        raise ValueError("scalar")
    if not isinstance(message, (bytes, bytearray)):
        raise TypeError("message")
    lib = _libcrypto()
    if lib:
        return _ossl_sign(lib, d, bytes(message))
    if p256_variable_time_allowed():
        return _sign_variable_time(d, bytes(message))
    raise P256Unavailable(
        "P-256 needs libcrypto. The variable-time ladder is off. "
        "Reed Mallory has not accepted it.")


def _project(affine):
    if affine is None:
        return _P256_INF
    return affine[0], affine[1], 1


def _verify_variable_time(public, message, signature):
    q = (int.from_bytes(public[1:33], "big"), int.from_bytes(public[33:], "big"))
    r = int.from_bytes(signature[:32], "big")
    s = int.from_bytes(signature[32:], "big")
    if q[0] >= P256_P or q[1] >= P256_P:
        return False
    if not (on_curve(q) and 0 < r < P256_N and 0 < s < P256_N):
        return False
    e = int.from_bytes(hashlib.sha256(message).digest(), "big")
    w = pow(s, P256_N - 2, P256_N)
    point = _to_affine(_add_complete(
        _project(_mul_ladder(e * w % P256_N, P256_G)),
        _project(_mul_ladder(r * w % P256_N, q)),
    ))
    return point is not None and point[0] % P256_N == r


def es256_verify(public, message, signature):
    if (not isinstance(public, (bytes, bytearray)) or not isinstance(signature, (bytes, bytearray))
            or not isinstance(message, (bytes, bytearray))):
        return False
    if len(public) != 65 or public[0] != 4 or len(signature) != 64:
        return False
    lib = _libcrypto()
    if lib:
        return _ossl_verify(lib, bytes(public), bytes(message), bytes(signature))
    if p256_variable_time_allowed():
        return _verify_variable_time(bytes(public), bytes(message), bytes(signature))
    return False


def tighten(path, mode):
    """Best-effort mode on a path that already exists.

    Windows only toggles the read-only bit, and 0600 still includes write,
    so a key stays writable there. A symlink is left alone, so a link
    planted in the push folder cannot change some other file. A refusal
    is left as it is.
    """
    if os.path.islink(path):
        return
    try:
        os.chmod(path, mode)
    except OSError:
        pass


def private_dir(path, unlink_link=False):
    """A real directory at mode 0700. A symlink is not a directory.

    With unlink_link, a symlink of this name is removed (the link only)
    and a real directory is made. The data folder itself is not unlinked:
    that path is the operator's. sync, push and growth are.
    """
    if os.path.islink(path):
        if not unlink_link:
            return False
        try:
            os.unlink(path)
        except OSError:
            return False
    if os.path.islink(path):
        return False
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        return False
    if os.path.islink(path):
        return False
    tighten(path, 0o700)
    return True


def security_note(folder, event, **fields):
    """One local line. No network address, no plan text, no push URL.

    The file stops growing at 100 KB. A symlink is not written through.
    """
    if not folder or os.path.islink(folder):
        return
    path = os.path.join(folder, "security-audit.jsonl")
    if os.path.islink(path):
        return
    safe = {}
    for key, value in fields.items():
        if isinstance(value, bool) or not isinstance(value, (str, int)):
            continue
        if isinstance(value, str):
            value = "".join(ch for ch in value if ch >= " " and ch != "\x7f")[:80]
        safe[str(key)[:20]] = value
    line = json.dumps({
        "at": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "event": "".join(ch for ch in str(event) if ch >= " " and ch != "\x7f")[:40],
        **safe,
    }, ensure_ascii=False) + "\n"
    try:
        if os.path.isfile(path) and not os.path.islink(path) and os.path.getsize(path) > 100_000:
            return
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        fd = open_nofollow(path, flags, 0o600)
    except OSError:
        return
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(fd, 0o600)
        os.write(fd, line.encode("utf-8"))
    except OSError:
        pass
    finally:
        os.close(fd)


def open_nofollow(path, flags, mode=0o666):
    """Open `path` without following a symlink or junction at the final name.

    POSIX sets O_NOFOLLOW. Windows opens with FILE_FLAG_OPEN_REPARSE_POINT
    and refuses a reparse point, so a name swapped in after a check is the
    link itself and not the file it points at. The descriptor owns the object
    that was opened.
    """
    if os.name != "nt":
        return os.open(path, flags | getattr(os, "O_NOFOLLOW", 0), mode)
    return _win_open_nofollow(path, flags, mode)



def _win_open_nofollow(path, flags, mode):
    """CreateFileW with FILE_FLAG_OPEN_REPARSE_POINT. A reparse point is refused."""
    import ctypes
    import errno
    import msvcrt
    from ctypes import wintypes
    creat = bool(flags & getattr(os, "O_CREAT", 0))
    excl = bool(flags & getattr(os, "O_EXCL", 0))
    trunc = bool(flags & getattr(os, "O_TRUNC", 0))
    append = bool(flags & getattr(os, "O_APPEND", 0))
    rdwr = bool(flags & getattr(os, "O_RDWR", 0))
    write = bool(flags & getattr(os, "O_WRONLY", 0)) or rdwr or append
    generic_read = 0x80000000
    generic_write = 0x40000000
    file_append = 0x0004
    if append:
        access = file_append
    elif write and rdwr:
        access = generic_read | generic_write
    elif write:
        access = generic_write
    else:
        access = generic_read
    if creat and excl:
        disposition = 1  # CREATE_NEW
    elif creat and trunc:
        disposition = 2  # CREATE_ALWAYS
    elif creat:
        disposition = 4  # OPEN_ALWAYS
    else:
        disposition = 3  # OPEN_EXISTING
    # FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT
    attributes = 0x80 | 0x00200000
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    handle = kernel.CreateFileW(path, access, 7, None, disposition, attributes, None)
    invalid = ctypes.c_void_p(-1).value
    if not handle or handle == invalid:
        err = ctypes.get_last_error() or errno.EINVAL
        raise OSError(err, os.strerror(err), path)

    class Info(ctypes.Structure):
        _fields_ = [
            ("attrs", wintypes.DWORD),
            ("create_low", wintypes.DWORD), ("create_high", wintypes.DWORD),
            ("access_low", wintypes.DWORD), ("access_high", wintypes.DWORD),
            ("write_low", wintypes.DWORD), ("write_high", wintypes.DWORD),
            ("volume", wintypes.DWORD),
            ("size_high", wintypes.DWORD), ("size_low", wintypes.DWORD),
            ("links", wintypes.DWORD),
            ("index_high", wintypes.DWORD), ("index_low", wintypes.DWORD),
        ]

    info = Info()
    kernel.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(Info)]
    kernel.GetFileInformationByHandle.restype = wintypes.BOOL
    if not kernel.GetFileInformationByHandle(handle, ctypes.byref(info)):
        kernel.CloseHandle(handle)
        err = ctypes.get_last_error() or errno.EINVAL
        raise OSError(err, os.strerror(err), path)
    if info.attrs & 0x400:  # FILE_ATTRIBUTE_REPARSE_POINT
        kernel.CloseHandle(handle)
        raise OSError(getattr(errno, "ELOOP", 40), "is a link", path)
    return msvcrt.open_osfhandle(int(handle), 0)



def seal_windows_fd(fd, folder):
    """Owner-only access list on Windows. A refusal is the operator's note.

    Unix mode is the control everywhere else. Reed Mallory does not accept
    a volume that ignores both.
    """
    if os.name != "nt" or fd is None:
        return
    try:
        import importlib
        hello = importlib.import_module("hello")
        if not hello.seal_owner_fd(fd):
            hello.note_dacl_transfer(folder)
    except (ImportError, OSError):
        pass


def write_private(path, text):
    """Write `text` so a shared machine cannot read it (mode 0600).

    The VAPID private key and a phone's push address are secrets. Windows
    ignores the Unix mode; the notes file has the same limit. A file that
    was already on disk is tightened when it is loaded, not only when it
    is created. A symlink sitting on the temp name is removed once and the
    write is tried again.
    """
    tmp = path + ".tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    try:
        fd = open_nofollow(tmp, flags, 0o600)
    except OSError:
        if os.path.islink(tmp):
            os.unlink(tmp)
            fd = open_nofollow(tmp, flags, 0o600)
        else:
            raise
    try:
        seal_windows_fd(fd, os.path.dirname(path))
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
    os.replace(tmp, path)
    tighten(path, 0o600)


def etag(raw):
    """A sync copy's version, for If-Match."""
    return '"' + hashlib.sha256(raw).hexdigest()[:32] + '"'


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def push_slot(when, clock):
    """The scheduled minute at or before `when`, while the retry window is open."""
    hour, minute = (int(part) for part in clock.split(":"))
    slot = when.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if slot > when:
        slot -= datetime.timedelta(days=1)
    if (when - slot).total_seconds() > PUSH_GRACE_MINUTES * 60:
        return ""
    return slot.strftime("%Y-%m-%dT%H:%M")


def push_address_ok(endpoint):
    """An https address at a browser maker's push service, and nothing else.

    A space or a control character in the path still parses as that host.
    urllib then refuses to send it (InvalidURL), and that exception is not
    an OSError. One such registration used to kill the reminder thread,
    which is the only thread sending every phone's reminder. Those
    characters are refused here, before anything is stored.
    """
    if not isinstance(endpoint, str) or not endpoint or len(endpoint) > 1000:
        return False
    if any(ord(c) < 33 or ord(c) == 127 or c in "\\#" for c in endpoint):
        return False
    try:
        url = urllib.parse.urlsplit(endpoint)
        port = url.port
    except (ValueError, TypeError):
        return False
    host = (url.hostname or "").lower()
    # An empty user name is still a user name. `not url.username` would
    # let https://:secret@host/ through.
    if url.username is not None or url.password is not None or url.fragment:
        return False
    if not re.fullmatch(r"[a-z0-9.-]+", host or ""):
        return False
    return (url.scheme == "https"
            and port in (None, 443)
            and any(host == h or host.endswith("." + h) for h in PUSH_HOSTS))


class Push:
    """Reminders for phones: a file per random token with the push address
    and up to two UTC times, and a key pair for the VAPID signature."""

    def __init__(self, folder):
        self.folder = os.path.join(folder, "push")
        self.ready = True
        # A symlink named push is the folder the next write would follow.
        # Remove the link itself. If it is still a link, do not use it.
        if os.path.islink(self.folder):
            try:
                os.unlink(self.folder)
            except OSError:
                pass
        if os.path.islink(self.folder):
            self.ready = False
        else:
            os.makedirs(self.folder, exist_ok=True)
            # 0755 from a 022 umask would let anyone on the machine list the
            # tokens. The token in the file name is what authorizes a change.
            tighten(self.folder, 0o700)
        self.lock = threading.Lock()
        key = os.path.join(folder, "vapid.json")
        # open() follows a symlink. A link named vapid.json is replaced
        # with a new key, and the file it pointed at is not read.
        if os.path.islink(key):
            self.d = secrets.randbelow(P256_N - 1) + 1
            write_private(key, json.dumps({"d": format(self.d, "064x")}))
        else:
            try:
                fd = open_nofollow(key, os.O_RDONLY)
                with os.fdopen(fd, "r", encoding="utf-8") as f:
                    self.d = int(json.load(f)["d"], 16)
                if not 1 <= self.d < P256_N:
                    raise ValueError("scalar")
                # A key written before 1.64.0 can still be mode 0644. Creating
                # a new file at 0600 does not change the one already on disk.
                tighten(key, 0o600)
            except (OSError, ValueError, KeyError, TypeError, RecursionError):
                self.d = secrets.randbelow(P256_N - 1) + 1
                write_private(key, json.dumps({"d": format(self.d, "064x")}))
        names = []
        if self.ready:
            try:
                names = os.listdir(self.folder)
            except OSError:
                names = []
        for name in names:
            path = os.path.join(self.folder, name)
            if re.fullmatch(r"[0-9a-f]{32}", name) and not os.path.islink(path):
                tighten(path, 0o600)
        self.public = p256_public(self.d)

    def path(self, token):
        return os.path.join(self.folder, token)

    @staticmethod
    def acceptable(data):
        """A push address on an allowed host and one or two times."""
        if not isinstance(data, dict) or not push_address_ok(data.get("endpoint", "")):
            return False
        times = data.get("times")
        return (isinstance(times, list) and 1 <= len(times) <= MAX_PUSH_TIMES
                and all(isinstance(t, str) and PUSH_TIME.match(t) for t in times))

    def save(self, token, data):
        """Keep a phone's push address and times. False when they aren't
        acceptable. The same times keep the record of what was already sent,
        so opening the app during the retry window does not send it again."""
        if not self.acceptable(data) or not self.ready:
            return False
        times = sorted(set(data["times"]))
        with self.lock:
            sent = []
            path = self.path(token)
            # A symlink is replaced below. It is not opened.
            if not os.path.islink(path):
                try:
                    fd = open_nofollow(path, os.O_RDONLY)
                    with os.fdopen(fd, "r", encoding="utf-8") as f:
                        old = json.load(f)
                    # The same address and the same times keep what was already
                    # sent. A new address is a new subscription, and a file whose
                    # times are not strings must not stop the phone updating it.
                    old_times = old.get("times") if isinstance(old, dict) else None
                    same_address = isinstance(old, dict) and old.get("endpoint") == data["endpoint"]
                    if (same_address and isinstance(old_times, list)
                            and sorted(t for t in old_times if isinstance(t, str)) == times
                            and all(isinstance(t, str) for t in old_times)):
                        marks = old.get("sent")
                        if isinstance(marks, str):
                            marks = [marks]
                        if isinstance(marks, list):
                            sent = [m for m in marks if isinstance(m, str) and PUSH_SENT.fullmatch(m)]
                except (OSError, ValueError, TypeError):
                    sent = []
            body = {"endpoint": data["endpoint"], "times": times}
            if sent:
                body["sent"] = sent
            write_private(path, json.dumps(body))
        return True

    def forget(self, token):
        """True when there was something to forget."""
        if not self.ready:
            return False
        with self.lock:
            try:
                os.remove(self.path(token))
                return True
            except FileNotFoundError:
                return False

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
        """One push with no content. The push service's status, or 0.

        A redirect comes back as that status. The next host is not called,
        so the VAPID header stays on the address that was stored.
        """
        request = urllib.request.Request(endpoint, data=b"", method="POST", headers={
            "TTL": "3600", "Urgency": "normal", "Content-Length": "0",
            "Authorization": self.header(endpoint, now)})

        class Halt(urllib.request.HTTPRedirectHandler):
            def http_error_302(self, req, fp, code, msg, headers):
                raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)

            http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302

        try:
            with urllib.request.build_opener(Halt).open(request, timeout=10) as answer:
                return answer.status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception:
            # InvalidURL is not an OSError. It must not leave this function.
            return 0

    def due(self, when, send=None):
        """Send reminders whose UTC minute is `when`, or missed it by a few
        minutes. A push the service did not accept is tried again. Returns
        how many went out."""
        if not self.ready:
            return 0
        send = send or self.send
        sent = 0
        for token in os.listdir(self.folder):
            if not re.fullmatch(r"[0-9a-f]{32}", token):
                continue
            path = self.path(token)
            if os.path.islink(path):
                continue
            try:
                if time.time() - os.path.getmtime(path) > SYNC_DAYS * 86400:
                    self.forget(token)
                    continue
                fd = open_nofollow(path, os.O_RDONLY)
                with os.fdopen(fd, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                continue
            endpoint = data.get("endpoint", "")
            if not push_address_ok(endpoint):
                # Still the bad address, not a newer registration that
                # replaced it while this loop was running.
                self._forget_if_same(path, endpoint if isinstance(endpoint, str) else "")
                continue
            marks = data.get("sent")
            if isinstance(marks, str):
                marks = [marks]
            elif not isinstance(marks, list):
                marks = []
            marks = [m for m in marks if isinstance(m, str)]
            stamps = []
            for clock in data.get("times") or []:
                if not isinstance(clock, str) or not PUSH_TIME.match(clock):
                    continue
                stamp = push_slot(when, clock)
                if stamp and stamp not in marks and stamp not in stamps:
                    stamps.append(stamp)
            if not stamps:
                continue
            # One call per time. A single success used to mark every time
            # that had fallen inside the window, so the later one never went.
            times = [t for t in (data.get("times") or []) if isinstance(t, str)]
            accepted = []
            for stamp in stamps:
                status = send(endpoint, when.timestamp())
                if status in (404, 410):
                    # The phone unsubscribed or the browser dropped it.
                    # Only if this file still names the address we called:
                    # a newer registration may have replaced it while we waited.
                    self._forget_if_same(path, endpoint)
                    accepted = []
                    break
                if not 200 <= status < 300:
                    break
                sent += 1
                accepted.append(stamp)
            if accepted:
                cutoff = (when - datetime.timedelta(days=2)).strftime("%Y-%m-%dT%H:%M")
                self._mark_sent(path, endpoint, times, marks + accepted, cutoff)
        return sent

    def _registration(self, path, endpoint, times):
        """The file as stored, when it still names this address and these times."""
        if os.path.islink(path):
            return None
        try:
            fd = open_nofollow(path, os.O_RDONLY)
            with os.fdopen(fd, "r", encoding="utf-8") as f:
                current = json.load(f)
        except (OSError, ValueError):
            return None
        current_times = current.get("times")
        if current.get("endpoint") != endpoint or not isinstance(current_times, list):
            return None
        if sorted(set(t for t in current_times if isinstance(t, str))) != sorted(set(times)):
            return None
        return current

    def _mark_sent(self, path, endpoint, times, marks, cutoff):
        """Record the times that went out. A check-in that landed while the
        push was in flight keeps its own address and times."""
        with self.lock:
            current = self._registration(path, endpoint, times)
            if current is None:
                return
            kept = []
            for mark in marks:
                if isinstance(mark, str) and mark >= cutoff and mark not in kept:
                    kept.append(mark)
            current["sent"] = kept
            try:
                # The file's time stays the phone's last visit.
                stat = os.stat(path)
                write_private(path, json.dumps(current))
                os.utime(path, (stat.st_atime, stat.st_mtime))
            except OSError:
                pass

    def _forget_if_same(self, path, endpoint):
        """Drop the registration only when it is still the one we called."""
        with self.lock:
            if os.path.islink(path):
                return
            try:
                fd = open_nofollow(path, os.O_RDONLY)
                with os.fdopen(fd, "r", encoding="utf-8") as f:
                    current = json.load(f)
            except (OSError, ValueError):
                return
            if current.get("endpoint") != endpoint:
                return
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

    def run(self):
        """Check each minute, in a thread for as long as the server runs.

        One bad registration must not end the thread. Every phone's
        reminder is sent from here.
        """
        while True:
            now = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)
            try:
                self.due(now)
            except Exception:
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


GROWTH_EVENTS = 50
GROWTH_DAY_BYTES = 5_000_000
GROWTH_EVENT = re.compile(r"^[a-z0-9_]{1,40}$")
GROWTH_ID = re.compile(r"^[0-9a-f]{32}$")


class Growth:
    """Streak-note batches. One JSON line per batch, under growth/, and the
    client's address is not written. Files older than 30 days are removed.
    A symlink is not followed. The folder is mode 0700 so other accounts
    on the machine cannot list the day files."""

    def __init__(self, folder):
        self.folder = os.path.join(folder, "growth")
        self.ready = True
        # A symlink named growth is the directory the next write would
        # follow. Remove the link itself. If it is still a link, do not
        # use it. The file it pointed at is left in place.
        if os.path.islink(self.folder):
            try:
                os.unlink(self.folder)
            except OSError:
                pass
        if os.path.islink(self.folder):
            self.ready = False
        else:
            try:
                os.makedirs(self.folder, exist_ok=True)
                tighten(self.folder, 0o700)
            except OSError:
                self.ready = False
        self.lock = threading.Lock()

    def take(self, payload):
        """(status, stored count or an error string)."""
        if not self.ready or os.path.islink(self.folder):
            return 500, "not stored"
        if not isinstance(payload, dict) or payload.get("consent") is not True:
            return 400, "consent required"
        cid = payload.get("id")
        if not isinstance(cid, str) or not GROWTH_ID.fullmatch(cid):
            return 400, "id"
        events = payload.get("events")
        if not isinstance(events, list) or not events or len(events) > GROWTH_EVENTS:
            return 400, "events"
        kept = []
        for event in events:
            if not isinstance(event, dict):
                continue
            name = event.get("event")
            if not isinstance(name, str) or not GROWTH_EVENT.fullmatch(name):
                continue
            plan = event.get("plan")
            if isinstance(plan, str):
                plan = "".join(ch for ch in plan if ch >= " " and ch != "\x7f")[:400] or None
            else:
                plan = None
            session = event.get("session")
            kept.append({
                "event": name,
                "at": event.get("at") if isinstance(event.get("at"), str) else "",
                "session": session if isinstance(session, str) and GROWTH_ID.fullmatch(session) else "",
                "streak": event["streak"] if isinstance(event.get("streak"), int)
                and not isinstance(event.get("streak"), bool) else 0,
                "best": event["best"] if isinstance(event.get("best"), int)
                and not isinstance(event.get("best"), bool) else 0,
                "plan": plan,
                "v": event.get("v") if isinstance(event.get("v"), str) else "",
                "lang": event.get("lang") if isinstance(event.get("lang"), str) else "",
            })
        if not kept:
            return 400, "events"
        day = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        path = os.path.join(self.folder, day + ".jsonl")
        line = (json.dumps({"id": cid, "events": kept}, ensure_ascii=False) + "\n").encode()
        with self.lock:
            if not self.ready or os.path.islink(self.folder):
                return 500, "not stored"
            self.trim()
            if os.path.islink(path):
                return 500, "not stored"
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            if size + len(line) > GROWTH_DAY_BYTES:
                return 413, "full"
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
            try:
                fd = open_nofollow(path, flags, 0o600)
            except OSError:
                return 500, "not stored"
            try:
                # The mode passed to open is masked by umask. 0600 has no
                # group bits, so a normal umask leaves it. fchmod sets it.
                if hasattr(os, "fchmod"):
                    os.fchmod(fd, 0o600)
                seal_windows_fd(fd, self.folder)
                os.write(fd, line)
            finally:
                os.close(fd)
        return 200, len(kept)

    def trim(self):
        """Drop day files older than 30 days. Call with the lock held."""
        cutoff = (datetime.datetime.now(datetime.timezone.utc).date()
                  - datetime.timedelta(days=30)).isoformat()
        try:
            names = os.listdir(self.folder)
        except OSError:
            return
        for name in names:
            if not name.endswith(".jsonl") or name[:10] >= cutoff:
                continue
            path = os.path.join(self.folder, name)
            if os.path.islink(path):
                try:
                    os.unlink(path)
                except OSError:
                    pass
                continue
            try:
                os.remove(path)
            except OSError:
                pass


PHONE_FILES = {"index.html": "text/html; charset=utf-8", "app.js": "text/javascript; charset=utf-8",
               "content.js": "text/javascript; charset=utf-8", "sw.js": "text/javascript; charset=utf-8",
               "manifest.webmanifest": "application/manifest+json", "icon.svg": "image/svg+xml"}
# The page is static. blob: is the plans export. https: is a growth address
# the person typed. http is only this computer, which is what the page allows.
PHONE_CSP = (
    "default-src 'self' blob:; script-src 'self'; style-src 'self' 'unsafe-inline'; "
    "img-src 'self'; connect-src 'self' https: http://127.0.0.1:* http://localhost:*; "
    "worker-src 'self'; manifest-src 'self'; object-src 'none'; base-uri 'none'; "
    "frame-ancestors 'none'"
)


def handler(counts, phone=None, push=None, growth=None, growth_page=False):
    class Handler(BaseHTTPRequestHandler):
        server_version = "hello-world-counts"
        sys_version = ""

        def shield(self):
            """Headers on every answer. The sync label is in the URL, so a
            referrer must not carry this page anywhere else."""
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")

        def reply(self, status, body=None):
            raw = json.dumps(body).encode() if body is not None else b""
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.shield()
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
                    self.shield()
                    self.end_headers()
                    return
                full = os.path.join(phone, name)
                # A symlink named app.js would be sent as the script.
                if os.path.islink(full):
                    return self.reply(404, {"error": "not found"})
                with open(full, "rb") as f:
                    raw = f.read()
                # --growth tells this page to upload to the server that
                # served it. Otherwise the placeholder in the file stays.
                if growth_page and name == "index.html":
                    raw = raw.replace(
                        b'<meta name="growth-server" content="">',
                        b'<meta name="growth-server" content="same-origin">',
                        1)
                self.send_response(200)
                self.send_header("Content-Type", PHONE_FILES[name])
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Cache-Control", "no-cache")
                self.shield()
                if name == "index.html":
                    self.send_header("Content-Security-Policy", PHONE_CSP)
                    self.send_header("X-Frame-Options", "DENY")
                self.end_headers()
                self.wfile.write(raw)
                return
            if self.path == "/v1/push/key" and push:
                return self.reply(200, {"key": b64url(push.public)})
            if SYNC_PATH.match(self.path):
                path = self.sync_file()
                if not path or os.path.islink(path):
                    if path and os.path.islink(path):
                        security_note(counts.folder, "symlink", where="sync")
                    return self.reply(404, {"error": "not found"})
                try:
                    st = os.lstat(path)
                    if stat.S_ISLNK(st.st_mode):
                        security_note(counts.folder, "symlink", where="sync")
                        return self.reply(404, {"error": "not found"})
                    if time.time() - st.st_mtime > SYNC_DAYS * 86400:
                        os.remove(path)
                        return self.reply(404, {"error": "not found"})
                    fd = open_nofollow(path, os.O_RDONLY)
                    try:
                        raw = os.read(fd, MAX_SYNC)
                    finally:
                        os.close(fd)
                except OSError:
                    return self.reply(404, {"error": "not found"})
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("ETag", etag(raw))
                self.send_header("Cache-Control", "no-store")
                self.shield()
                self.end_headers()
                self.wfile.write(raw)
                return
            if week := WEEK_PATH.match(self.path):
                if not this_week(week.group(1)):
                    return self.reply(404, {"error": "not found"})
                return self.reply(200, counts.publish(week.group(1), week=True))
            day, add = self.route()
            if day is None or add:
                return self.reply(404, {"error": "not found"})
            self.reply(200, counts.publish(day))

        def address(self):
            # Behind a proxy every request comes from the proxy, so the
            # address it passes on counts instead, when it is set to.
            address = self.client_address[0]
            if self.server.trust_proxy:
                # The last entry is the one the proxy added; the ones before
                # it are whatever the sender claimed.
                address = (self.headers.get("X-Forwarded-For") or address).split(",")[-1].strip()
            return address

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
            # A symlink named sync is the directory the next write would
            # follow. The link is removed. The directory it pointed at stays.
            if not private_dir(folder, unlink_link=True):
                return None
            return os.path.join(folder, match.group(1))

        def do_PUT(self):
            if (match := PUSH_PATH.match(self.path)) and push:
                raw = self.body()
                try:
                    data = json.loads(raw or b"")
                except (ValueError, RecursionError):
                    data = None
                if not push.acceptable(data):
                    return self.reply(400, {"error": "not a push address and times"})
                refused = counts.may_write(self.address(), not os.path.exists(push.path(match.group(1))),
                                           "push")
                if refused:
                    return self.reply(refused[0], {"error": refused[1]})
                push.save(match.group(1), data)
                return self.reply(200, {"ok": True})
            path = self.sync_file()
            if path is None:
                return self.reply(404, {"error": "not found"})
            # The body is checked first, so a refused one uses up no writes.
            raw = self.body()
            if not raw:
                return self.reply(413, {"error": "too large or empty"})
            with counts.write_lock:
                link = os.path.islink(path)
                current = None
                if not link:
                    try:
                        fd = open_nofollow(path, os.O_RDONLY)
                        try:
                            current = etag(os.read(fd, MAX_SYNC))
                        finally:
                            os.close(fd)
                    except OSError:
                        current = None
                # If-Match names the copy the writer last read. A missing
                # header used to replace whatever was already stored.
                # Creating still allows no header, or "missing".
                wanted = self.headers.get("If-Match")
                if isinstance(wanted, str):
                    wanted = wanted.strip()
                if link or current is None:
                    if wanted not in (None, "missing"):
                        return self.reply(412, {"error": "changed since you read it"})
                else:
                    if not wanted:
                        security_note(counts.folder, "sync_precondition")
                        return self.reply(428, {"error": "If-Match required"})
                    if wanted != current:
                        return self.reply(412, {"error": "changed since you read it"})
                refused = counts.may_write(self.address(), current is None and not link)
                if refused:
                    return self.reply(refused[0], {"error": refused[1]})
                if link:
                    try:
                        os.unlink(path)
                    except OSError:
                        return self.reply(500, {"error": "not stored"})
                tmp = f"{path}.{secrets.token_hex(4)}.tmp"
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                try:
                    fd = open_nofollow(tmp, flags, 0o600)
                except OSError:
                    return self.reply(500, {"error": "not stored"})
                try:
                    if hasattr(os, "fchmod"):
                        os.fchmod(fd, 0o600)
                    seal_windows_fd(fd, os.path.dirname(path))
                    os.write(fd, raw)
                except OSError:
                    try:
                        os.remove(tmp)
                    except OSError:
                        pass
                    return self.reply(500, {"error": "not stored"})
                finally:
                    os.close(fd)
                os.replace(tmp, path)
                tighten(path, 0o600)
            self.reply(200, {"ok": True})

        def do_DELETE(self):
            if (match := PUSH_PATH.match(self.path)) and push:
                if push.forget(match.group(1)):
                    counts.removed("push")
                return self.reply(200, {"ok": True})
            path = self.sync_file()
            if path is None:
                return self.reply(404, {"error": "not found"})
            with counts.write_lock:
                try:
                    os.remove(path)
                    counts.removed("sync")
                except FileNotFoundError:
                    pass
            self.reply(200, {"ok": True})

        def do_POST(self):
            path = self.path.split("?", 1)[0]
            if path == "/v1/growth":
                if growth is None:
                    return self.reply(404, {"error": "not found"})
                raw = self.body()
                if raw is None:
                    return self.reply(413, {"error": "too large or empty"})
                try:
                    payload = json.loads(raw or b"")
                except (ValueError, RecursionError):
                    return self.reply(400, {"error": "events"})
                # A refused body does not count as a write.
                if not isinstance(payload, dict) or payload.get("consent") is not True:
                    return self.reply(400, {"error": "consent required"})
                refused = counts.may_write(self.address(), False, "growth")
                if refused:
                    return self.reply(refused[0], {"error": refused[1]})
                status, stored = growth.take(payload)
                if status != 200:
                    return self.reply(status, {"error": stored})
                return self.reply(200, {"ok": True, "stored": stored})
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
            what = "tip" if add == "/tip" else add.rsplit("/", 1)[1]
            counts.add(day, what, self.address())
            self.reply(200, counts.publish(day))

        def log_message(self, format, *args):
            # No access log: it would hold addresses.
            pass

    return Handler


def serve(port=8080, folder="counts", host="0.0.0.0", trust_proxy=False, boss_hp=None, phone=None,
          remind=False, min_group=MIN_GROUP, sync_quota=SYNC_QUOTA, refresh=REFRESH,
          growth_page=False):
    """The server. With remind, phones' reminders are kept and sent too.

    Streak notes are accepted at POST /v1/growth. growth_page rewrites the
    phone page so it offers them to this server; otherwise that page keeps
    the placeholder address baked into it.
    """
    push = Push(folder) if remind else None
    counts = Counts(folder, boss_hp, min_group, sync_quota, refresh)
    growth = Growth(folder)
    server = ThreadingHTTPServer((host, port), handler(counts, phone, push, growth, growth_page))
    server.counts = counts
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
    parser.add_argument("--min-group", type=int, default=MIN_GROUP,
                        help="counts below this are shown as \"few\" (default 10)")
    parser.add_argument("--sync-quota", type=int, default=SYNC_QUOTA,
                        help="most encrypted sync copies kept in all (default 100000)")
    parser.add_argument("--refresh", type=int, default=REFRESH,
                        help="seconds the published counts stay fixed (default 3600)")
    parser.add_argument("--remind", action="store_true",
                        help="keep and send phones' reminders, by Web Push with no content")
    parser.add_argument("--growth", action="store_true",
                        help="tell the phone page to offer streak notes to this server")
    args = parser.parse_args(argv)
    server = serve(args.port, args.data, args.host, args.trust_proxy, args.boss_hp, args.phone,
                   args.remind, max(1, args.min_group), max(1, args.sync_quota),
                   max(60, args.refresh), args.growth)
    threading.Thread(target=server.counts.run_sweep, daemon=True).start()
    if server.push:
        threading.Thread(target=server.push.run, daemon=True).start()
    review = sync_review_status()
    backend = p256_backend()
    security_note(args.data, "p256_backend", result=backend)
    security_note(args.data, "sync_review", result=review)
    print(f"hello-world counts on {args.host}:{server.server_address[1]}, data in {args.data}")
    # The internal review is not an outside audit. Wide promotion stays with
    # the deploying organization. Reed Mallory is not the acceptor.
    print(f"sync review: {review}; P-256: {backend}")
    server.serve_forever()


if __name__ == "__main__":
    main()
