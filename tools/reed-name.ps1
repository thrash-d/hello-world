# Reed Mallory's name, after spaces are folded.
# A certificate subject is checked name by name, so "CN=Reed  Mallory"
# and "CN=Reed Mallory." are still his. "not Reed Mallory" does not
# start with his name. He does not accept that name on a signature.

function Test-ReedMalloryName([string]$Name) {
    $raw = [string]$Name
    $folded = ([regex]::Replace($raw.ToLowerInvariant(), '\s+', ' ')).Trim()
    if ($folded.StartsWith('reed mallory')) { return $true }
    foreach ($part in ($folded -split ',')) {
        $value = $part.Trim()
        $eq = $value.LastIndexOf('=')
        if ($eq -ge 0) { $value = $value.Substring($eq + 1).Trim() }
        if ($value.StartsWith('reed mallory')) { return $true }
    }
    return $false
}
