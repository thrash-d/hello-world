"""Make hello-world Pro keys. Only the owner runs this, with a private key
that is never committed.

    python tools/pro_keys.py new owner.key
        Makes a signing key pair. Keep owner.key secret and backed up, and put
        the printed public key in PRO_PUBLIC_KEY in hello.py before a release.

    python tools/pro_keys.py issue owner.key "Ana Lopez"
        Prints a Pro key for one buyer, to send them after they pay. The name
        is shown back to them when they paste it, and nothing else is in it.

    python tools/pro_keys.py issue owner.key "The Lopez household" --family
        Prints a household key ($8): Pro on every device in the household,
        and the shared household list.

A key is "HW1." then the note {"to": name, "on": date}, with "kind":
"family" for a household key, and its Ed25519 signature, both base64.
hello.py checks it with the public key alone.
"""

import base64
import datetime
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hello  # noqa: E402


def _expand(secret):
    h = hashlib.sha512(secret).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def _compress(point):
    p = hello._P
    zinv = pow(point[2], p - 2, p)
    x, y = point[0] * zinv % p, point[1] * zinv % p
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def public_key(secret):
    return _compress(hello._ed_mul(_expand(secret)[0], hello._ED_BASE))


def sign(secret, message):
    """RFC 8032 Ed25519."""
    a, prefix = _expand(secret)
    public = _compress(hello._ed_mul(a, hello._ED_BASE))
    r = int.from_bytes(hashlib.sha512(prefix + message).digest(), "little") % hello._L
    big_r = _compress(hello._ed_mul(r, hello._ED_BASE))
    h = int.from_bytes(hashlib.sha512(big_r + public + message).digest(), "little") % hello._L
    return big_r + int.to_bytes((r + h * a) % hello._L, 32, "little")


def _b64(raw):
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def issue(secret, name, on=None, family=False):
    data = {"to": name, "on": on or datetime.date.today().isoformat()}
    if family:
        data["kind"] = "family"
    note = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode()
    return "HW1." + _b64(note) + "." + _b64(sign(secret, hello.PRO_CONTEXT + note))


def main(argv):
    if len(argv) == 2 and argv[0] == "new":
        if os.path.exists(argv[1]):
            sys.exit(f"{argv[1]} already exists; not overwriting a signing key.")
        secret = os.urandom(32)
        fd = os.open(argv[1], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(secret.hex() + "\n")
        print("PRO_PUBLIC_KEY =", repr(public_key(secret).hex()))
        return 0
    if len(argv) in (3, 4) and argv[0] == "issue" and argv[3:] in ([], ["--family"]):
        with open(argv[1]) as f:
            secret = bytes.fromhex(f.read().strip())
        print(issue(secret, argv[2], family=argv[3:] == ["--family"]))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
