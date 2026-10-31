# Reed Mallory's name, after spaces are folded.
# A certificate subject is checked name by name, so "CN=Reed  Mallory",
# "CN=Reed Mallory.", and "CN=""Reed Mallory""" are still his.
# "not Reed Mallory" does not start with his name. One pair of matching
# quotes is not part of the name. He does not accept that name on a signature.
# The four install scripts repeat these steps. They are copied away from
# this file, so they cannot dot-source it.

function Test-ReedMalloryName([string]$Name) {
    $raw = [string]$Name
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
        if ($value.Length -ge 2) {
            $a = $value[0]
            $b = $value[$value.Length - 1]
            if (($a -eq '"' -or $a -eq "'") -and ($a -eq $b)) {
                $value = $value.Substring(1, $value.Length - 2).Trim()
            }
        }
        if ($value.StartsWith('reed mallory')) { return $true }
    }
    return $false
}
