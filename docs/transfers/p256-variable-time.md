# Transfer: variable-time P-256

The shipping path is libcrypto (OpenSSL) NIST P-256, curve NID 415. Signing
and verification on that path are OpenSSL's, and the low `s` is chosen with
`BN_cmp` against the order shifted once, then `BN_sub`. That path is the
one `p256_backend()` reports as `openssl`.

The pure-Python ladder in `server/counts_server.py` does not branch on the
scalar. CPython's big integers are still variable-time, so the ladder is not
constant-time and it is not the shipping path. Reed Mallory does not accept
it.

## It stays off

`es256_sign`, `es256_verify`, and `p256_public` use libcrypto when it loads.
If it does not load, they raise `P256Unavailable` (verify returns false)
unless both of the following are set:

- `HELLO_P256_VARIABLE_TIME=1`
- `HELLO_P256_TRANSFER` points at a regular file, not a symlink, of at most
  4000 bytes:

```
acceptor: <name that is not Reed Mallory>
accepts: variable-time-p256
```

A name that is Reed Mallory, or that starts with Reed Mallory, does not
open the gate. Even with the gate open, libcrypto is still preferred.
`p256_backend()` stays `openssl` when libcrypto loads.

## Who holds it

The operator named in that file. They are accepting a variable-time scalar
multiply on a machine that has no libcrypto. A counts server started with
`--remind` and no libcrypto and no transfer fails at startup rather than
sign with the ladder. A server without `--remind` still starts.
