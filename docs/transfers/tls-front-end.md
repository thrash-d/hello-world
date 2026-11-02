# Transfer: TLS front end

The counts server speaks HTTP. It is meant to sit behind a TLS front end
the deploying organization runs. Reed Mallory does not accept the two
residuals below, and he is not the acceptor.

## Strict-Transport-Security

A `Strict-Transport-Security` header on this process would not protect the
cleartext bytes, and a browser that stored it would then refuse the
documented local run on `http://127.0.0.1`. The header belongs on the TLS
terminator, after the organization has chosen the HTTPS name.

## A rate limit that survives a restart

The process allows 120 requests a minute from one address, 60 writes a
minute, and 20 new labels a day. Those counts live in memory, with the
daily key, and a restart clears them. The server does not write a network
address to disk, so it cannot keep the counter there. The front end keeps
the durable limit.

## Who holds it

The deploying organization. A name that is Reed Mallory, or that starts
with Reed Mallory, is not an acceptor. The same name fold as
`tools/reed-name.ps1` applies: a hex-encoded subject is decoded, and a
lookalike space is folded.
