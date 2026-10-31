# Transfer: unsigned PowerShell scripts

The scripts in git are not Authenticode-signed. Signing needs a private key
this repository does not have. Reed Mallory does not accept that residual,
and he is not the signer.

## Who holds it

The deploying organization. A name that is Reed Mallory, or that starts with
Reed Mallory, is not an acceptor.

## How to close it

Sign the four scripts, then check each one:

```powershell
tools\sign-scripts.ps1 -CertificateThumbprint <thumbprint> -TimestampServer <RFC 3161 URL> -OutDir <empty folder>
```

Or sign them as part of the package:

```powershell
tools\build-package.ps1 -OutDir <empty folder> -CertificateThumbprint <thumbprint> -TimestampServer <RFC 3161 URL>
```

Both sign `install.ps1`, `uninstall.ps1`, `install-user.ps1` and
`uninstall-user.ps1` with SHA-256. `Get-AuthenticodeSignature` must return
`Valid`. A certificate whose subject names Reed Mallory is refused.
Spaces inside that subject are folded first, and each name is checked, so
`CN=Reed  Mallory` and `CN=Reed Mallory.` are still refused. `CN=not Reed
Mallory` does not start with his name. `tools\build-package.ps1` uses the
same check before it signs. The check lives in `tools\reed-name.ps1`.
`docs/ENTERPRISE.md` has the AllSigned and WDAC notes. CI already installs
a package signed with a throwaway certificate.

## While a copy is still unsigned

The script warns once and names the acceptor:

- `-UnsignedAcceptor`, if that name is not Reed Mallory
- otherwise `HELLO_UNSIGNED_ACCEPTOR`, on the same rule
- otherwise the words `deploying organization`

Spaces inside the name are folded before that check, so "Reed  Mallory" and
"Reed Mallory." are still not acceptors.

The install is not refused. Refusing it would remove the documented way to
install from a clone. The package hash is the hash of the unsigned files
until a thumbprint is passed. No extra file is added to the package.

`tools\build-package.ps1` without a thumbprint prints the same acceptor and
throws if the name is Reed Mallory.
