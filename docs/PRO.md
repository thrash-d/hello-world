# Selling Pro

Pro is $5 once ($4 for the first 60 days after launch), or $8 once for a
household, with no account and no subscription. A key is checked on the buyer's PC with the public half of
the owner's signing key, so hello-world never contacts anyone to unlock it.
Businesses keep their own per-seat terms, outside this file.

What Pro adds: a second check-in in the afternoon or evening on days with an
open plan, and window colours. A household key adds the shared household
list. History and the This year page, pets, reminders, and everything the
free version did before Pro existed, stay free. That split came from the
simulated rounds: the Gen Z and pessimist panels said history only matters
after months and the core loop must never be paid, and the indie developer
said free pets bring people in.

Every place a key is pasted says keys come only from the official store and
that hello-world never calls, texts or emails to sell or check one (the red
team's Ponzi). Sell only through the store you name there.

## One time: make the signing key

    python tools/pro_keys.py new owner.key

Keep `owner.key` secret, backed up, and out of the repository (`*.key` is
ignored). Anyone who has it can make keys. Put the printed `PRO_PUBLIC_KEY`
line in `hello.py` and release. Until then, no key works.

## Each sale

    python tools/pro_keys.py issue owner.key "Ana Lopez"

For a household ($8):

    python tools/pro_keys.py issue owner.key "The Lopez household" --family

Send the printed key to the buyer. They paste it in **Options > Pro...** in
the window (it reads it from the clipboard), type `pro` at the end of the
text screen, or run `hello.cmd pro <key>`. The name is shown back to them and
is the only thing in the key.

## Where to sell

The repository can't do this part; it needs the owner's accounts:

- A payment service that sends a key after payment, such as Lemon Squeezy or
  Paddle: upload a batch of keys made with `issue`, or call `issue` from the
  service's webhook on a machine that holds `owner.key`.
- The Microsoft Store, if the package is listed there.

Refunds: a key can't be taken back offline. Treat a refund as a lost $5;
that's the price of no account.
