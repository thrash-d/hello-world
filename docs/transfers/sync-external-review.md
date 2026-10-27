# Transfer: outside review of the sync encryption

`docs/SYNC-CRYPTO-REVIEW.md` is an internal review of the scheme that is
already shipping. It is not an outside audit. Reed Mallory does not sign
the word audited, and the screen still says the encryption has not had an
outside audit.

## Who holds the outside signature

The deploying organization, before the scheme is promoted widely. The same
signature covers the push signing described in that review.

## How to record it

Write a regular file, not a symlink, of at most 4000 bytes:

```
acceptor: <name that is not Reed Mallory>
accepts: sync-external-review
```

Point the counts server at it:

```
HELLO_SYNC_EXTERNAL_REVIEW=<path to that file>
```

`sync_review_status()` then returns `external`. Without the file it returns
`internal-only`, which is what startup prints. A name that is Reed Mallory,
or that starts with Reed Mallory, is ignored. The file is not followed if
it is a symlink.

The internal review does not change the key derivation, the salt, or the
blob format. An existing copy still opens.
