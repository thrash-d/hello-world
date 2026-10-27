# Transfer: phone sync keys

The phone stores the sync keys in IndexedDB (`hello-world-sync-keys`, store
`secrets`) as non-extractable HMAC `CryptoKey`s. The personal id is
`personal`. A household id is `house:<label>`. After that write succeeds,
`localStorage` key `hello-world-sync` is removed. Household key bytes are
not written into the notes JSON. The notes keep `{label, locked:"idb"}` or
`locked:"memory"`.

Delete everything still clears the database and the local storage key.

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
is not Reed Mallory. That name is the acceptor of the raw copy. An empty
value, or his name, does not keep the raw copy.

The cache name is `hello-world-phone-v15`, so a phone that already cached
the previous page fetches this one.
