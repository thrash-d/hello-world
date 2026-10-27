# Sync encryption and push signing: internal review

Date: 2026-10-27. Version reviewed: 1.69.0.

This is an internal design review of the scheme hello-world already ships.
It is not an outside audit, not a lab report, and not a sign-off that the
scheme has been promoted. Reed Mallory did not write it as an auditor and
he does not sign the word audited. The screen still says the encryption has
not had an outside audit. The outside signature, when someone who is not him
is willing to put their name on it, is `docs/transfers/sync-external-review.md`.

The key derivation, the salts, the round count, and the blob layout were
not changed. An existing sealed copy, and a phone that still has the
previous page cached, still open. Changing them would break those copies.

## What the scheme is

Both the PC (`hello.py`) and the phone (`phone/app.js`) derive 96 bytes
with PBKDF2-SHA256:

- personal salt: `hello-world sync v1`
- household salt: `hello-world household v1`
- 200,000 rounds
- the code, lower-cased, restricted to the sync alphabet, is the password

The first 32 bytes are the label, hex-encoded, and are the name of the
server object. The next 32 are the encryption key. The last 32 are the MAC
key. The server stores the blob under the label and does not see the code.

`seal_sync` writes `v1`, a 16-byte nonce, the ciphertext, and a 32-byte
HMAC-SHA256 tag. The stream is HMAC-SHA256 in counter mode: each block is
`HMAC(enc, nonce || counter)` with the counter as 4 big-endian bytes,
starting at 0. The tag is over `v1 || nonce || ciphertext`. `open_sync`
checks the tag with `hmac.compare_digest` before it decodes the plaintext.
The phone does the same steps with Web Crypto HMAC.

A blob longer than 64,000 bytes is rejected. A key that is not 32 bytes is
rejected. A plaintext that is not UTF-8 JSON object is rejected. Those
checks do not change a blob that was already valid.

## A test vector

Code `aaaaa-aaaaa-aaaaa-aaaaa-aaaaa`, personal salt, 200,000 rounds.

| Field | Value |
| --- | --- |
| label | `0063908f781e7cfe1ec69d95dfc75cb2dfcff1a04f7b5cd3dff664f3ee25f3dc` |
| enc | `7423f3a3438387008569dc19e8b07bb20189f3faa11d29390d8c7a995c372e39` |
| mac | `bd306fa4ce6a02a7c0a9d75dcfc77c0ca788f87f06eca1c74734dcb8b28f4c81` |
| nonce | 16 zero bytes |
| blob | `763100000000000000000000000000000000290ab3766fab016843bd8baf5090029112a68b9f85c3bc77904062ff2e6c25c343a3edb80ccb4437102b7de26d4cb449e1d9fea441b7` |

That blob opens to `{"v": 1, "text": "bread"}`. A tag that is one byte short
does not open. A blob over 64,000 bytes does not open.

## What this review is willing to say

- The tag is checked before the plaintext is used, and the compare is
  `hmac.compare_digest` on the PC.
- The nonce is random on a real seal (`os.urandom(16)`). The zero nonce
  above is only the test vector.
- The label is not the encryption key. Publishing the label does not publish
  the code. The code is about 123 bits from a 31-character alphabet, 25
  characters, and the app makes it. A person cannot type their own.
- A stored copy that already exists requires `If-Match` (1.68.0). Replacing
  the blob is not silent.
- The phone's keys are non-extractable HMAC keys in IndexedDB (1.69.0).
  See `docs/transfers/phone-sync-keys.md` for the case IndexedDB is missing
  and for a script that already runs on the same origin.

## What this review will not say

- It will not say the construction is a standard AEAD. It is HMAC in counter
  mode, then HMAC, built from what Python's library and a browser both have.
  There is no associated data. The version byte is inside the tagged prefix.
- It will not say the salt is secret. The salt is a fixed string. Two people
  who pick the same code derive the same keys. The code is the secret.
- It will not say 200,000 PBKDF2-SHA256 rounds are a modern password
  hasher's work factor. They are the rounds already in every shipped copy.
  Raising them would make old copies fail to open. That change is not in
  this version.
- It will not say a person who has the code cannot write the blob. They can.
  The code is the only key. That is the design, and the scam line says
  nobody real will ask for the code.
- It will not say this file is the outside review `TODO.md` asks for before
  wide promotion. That signature is the deploying organization's.

## Push signing

Web Push VAPID uses ES256. The shipping implementation is libcrypto's NIST
P-256 (NID 415): `EC_POINT_mul`, `ECDSA_do_sign`, `ECDSA_do_verify`. The low
`s` is `N - s` when `BN_cmp` says `s` is above `N >> 1`. The public API is
unchanged: `p256_public` returns a 65-byte uncompressed point, `es256_sign`
returns 64-byte `r || s`, `es256_verify` checks it.

A pure-Python ladder is in the same file. It uses a fixed 256-step complete
addition (Renes–Costello–Batina, add-2015-rcb, `a = -3`). CPython's integers
are not constant-time, so that ladder does not run unless
`docs/transfers/p256-variable-time.md` is followed by someone who is not
Reed Mallory. If libcrypto is missing and that gate is off, signing raises
`P256Unavailable` and verify returns false.

Checked against OpenSSL on this machine: scalar
`C9AFA9D845BA75166B5C215767B1D6934E50C3DB36E89B127B8A622B120F6721`
produces the NIST P-256 public point, and signatures from `es256_sign` have
`s <= N/2` and verify. That check is in `reviews/round-52.md`. It is not a
push-service test. No reminder was sent to a live host.

## Startup line

The counts server prints `sync review: internal-only; P-256: openssl` when
libcrypto loads and no outside signature is on file. It also appends those
two words to `security-audit.jsonl`. `external` appears only after the
transfer file in `docs/transfers/sync-external-review.md`.
