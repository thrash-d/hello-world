# Transfer: phone sync keys

The phone stores the sync keys in IndexedDB (`hello-world-sync-keys`, store
`secrets`) as non-extractable HMAC `CryptoKey`s. The personal id is
`personal`. A household id is `house:<label>`. After that write succeeds,
`localStorage` key `hello-world-sync` is removed. Household key bytes are
not written into the notes JSON once that write has succeeded. The notes
keep `{label, locked:"idb"}`, `locked:"memory"`, or `locked:"raw"`. The
loader reads that pointer and, for `idb`, loads the keys back, so the
household list is still there after a refresh. A copy that still has the
raw 32-byte arrays is migrated on the next open, and the arrays stay in
the notes until that migration finishes, so a refresh in that gap does
not drop the list.

Leaving the household, or making a new code, deletes the old
`house:<label>` entry. If that delete throws, the phone's security note
says `kept`. Delete everything still clears the database and the local
storage key.

## What the browser will not close

A script that already runs on the same origin can use a non-extractable key
without exporting it. The counts server's content security policy from
1.68.0 is the fence on pages that server sends. Opening the files from
another host is that host's page. Reed Mallory does not accept this residual.

## Who holds it

The organization that serves `app.js`.

If IndexedDB cannot be opened, the keys stay in memory for that visit and
the raw `localStorage` copy is removed. They are written back as raw arrays
only when `localStorage` key `hello-world-sync-raw-acceptor` is a name that
is not Reed Mallory. Spaces inside the name are folded first. A name that
is his, or that starts with his, does not keep the raw copy. An empty
value does not either. That other name is the acceptor of the raw copy.

The cache name is `hello-world-phone-v16`, so a phone that already cached
the previous page fetches this one.
