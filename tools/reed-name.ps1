# Reed Mallory's name, after spaces are folded.
# A certificate subject is checked name by name, so "CN=Reed  Mallory",
# "CN=Reed Mallory.", "CN=""Reed Mallory""", a curly-quoted name, and a
# zero-width space between the words are still his.
# "not Reed Mallory" does not start with his name. Format characters,
# quote marks, and backslashes are not part of the name.
# A hex subject is not decoded. He does not accept that name on a signature.
# The four install scripts repeat these steps. They are copied away from
# this file, so they cannot dot-source it.

function Test-ReedMalloryName([string]$Name) {
    $raw = [regex]::Replace([string]$Name, '\\', '')
    $raw = [regex]::Replace($raw, '\p{Cf}', '')
    $raw = [regex]::Replace($raw, '["''\u201C\u201D\u201E\u201F\u2018\u2019\u201A\u201B\u00AB\u00BB`]', '')
    $folded = ([regex]::Replace($raw.ToLowerInvariant(), '\s+', ' ')).Trim()
    $checks = New-Object System.Collections.Generic.List[string]
    [void]$checks.Add($folded)
    foreach ($part in ($folded -split ',')) {
        $value = $part.Trim()
        $eq = $value.LastIndexOf('=')
        if ($eq -ge 0) { $value = $value.Substring($eq + 1).Trim() }
        [void]$checks.Add($value)
    }
    foreach ($value in $checks) {
        if ($value.StartsWith('reed mallory')) { return $true }
    }
    return $false
}
