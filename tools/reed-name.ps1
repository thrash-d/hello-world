# Reed Mallory's name, after NFKC, confusables, and a whitespace fold.
# A certificate subject is checked name by name. A hex subject is decoded:
# RFC 4514 \HH octets, and a #hex BER string (UTF-8, Printable, BMP).
# A blank that only looks like a space, including U+2800, becomes a space.
# "not Reed Mallory" does not start with his name. Format characters,
# quote marks, and backslashes are not part of the name.
# The four install scripts repeat these steps. They are copied away from
# this file, so they cannot dot-source it.

function ConvertFrom-ReedEscapes([string]$Text) {
    if (-not $Text) { return '' }
    $bytes = New-Object System.Collections.Generic.List[byte]
    $utf8 = [Text.Encoding]::UTF8
    $i = 0
    while ($i -lt $Text.Length) {
        $ch = $Text[$i]
        if ($ch -eq [char]92 -and ($i + 1) -lt $Text.Length) {
            if (($i + 2) -lt $Text.Length -and $Text.Substring($i + 1, 2) -match '^[0-9A-Fa-f]{2}$') {
                [void]$bytes.Add([Convert]::ToByte($Text.Substring($i + 1, 2), 16))
                $i += 3
                continue
            }
            foreach ($b in $utf8.GetBytes([string]$Text[$i + 1])) { [void]$bytes.Add($b) }
            $i += 2
            continue
        }
        foreach ($b in $utf8.GetBytes([string]$ch)) { [void]$bytes.Add($b) }
        $i += 1
    }
    return $utf8.GetString($bytes.ToArray())
}

function ConvertTo-ReedStrip([string]$Text) {
    if (-not $Text) { return '' }
    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $Text.ToCharArray()) {
        $cp = [int]$ch
        $quote = $cp -in 0x22, 0x27, 0x60, 0x201C, 0x201D, 0x201E, 0x201F, 0x2018, 0x2019, 0x201A, 0x201B, 0x00AB, 0x00BB
        $format = [char]::GetUnicodeCategory($ch) -eq [Globalization.UnicodeCategory]::Format
        if ($ch -eq [char]92 -or $quote -or $format) { continue }
        [void]$sb.Append($ch)
    }
    return $sb.ToString()
}

function Test-ReedReadable([string]$Text) {
    if (-not $Text -or $Text.Length -gt 200) { return $false }
    if ($Text -match '\p{Cc}') { return $false }
    return [bool]($Text -match '\p{L}')
}

function ConvertFrom-ReedBer([byte[]]$Data) {
    if ($null -eq $Data -or $Data.Length -lt 2) { return $null }
    $tag = [int]$Data[0]
    if (@(0x0C, 0x13, 0x14, 0x16, 0x1A, 0x1E, 0x1C) -notcontains $tag) { return $null }
    $length = [int]$Data[1]
    $start = 2
    if ($length -band 0x80) {
        $n = $length -band 0x7F
        if ($n -lt 1 -or $n -gt 2 -or $Data.Length -lt (2 + $n)) { return $null }
        $length = 0
        for ($k = 0; $k -lt $n; $k++) { $length = ($length -shl 8) -bor [int]$Data[2 + $k] }
        $start = 2 + $n
    }
    if ($length -ne ($Data.Length - $start) -or $length -gt 240 -or $length -lt 0) { return $null }
    $content = New-Object byte[] $length
    [Array]::Copy($Data, $start, $content, 0, $length)
    try {
        if ($tag -eq 0x1E) {
            if ($content.Length % 2) { return $null }
            $text = [Text.Encoding]::BigEndianUnicode.GetString($content)
        } elseif ($tag -eq 0x1C) {
            if ($content.Length % 4) { return $null }
            $chars = New-Object System.Text.StringBuilder
            for ($k = 0; $k -lt $content.Length; $k += 4) {
                $cp = ([int]$content[$k] -shl 24) -bor ([int]$content[$k + 1] -shl 16) -bor ([int]$content[$k + 2] -shl 8) -bor [int]$content[$k + 3]
                if ($cp -lt 0 -or $cp -gt 0x10FFFF) { return $null }
                [void]$chars.Append([char]::ConvertFromUtf32($cp))
            }
            $text = $chars.ToString()
        } else {
            $strict = New-Object System.Text.UTF8Encoding $false, $true
            $text = $strict.GetString($content)
        }
    } catch { return $null }
    if (Test-ReedReadable $text) { return $text }
    return $null
}

function ConvertFrom-ReedPlain([byte[]]$Data) {
    $found = New-Object System.Collections.Generic.List[string]
    if ($null -eq $Data) { return $found }
    $strict = New-Object System.Text.UTF8Encoding $false, $true
    try {
        $utf8 = $strict.GetString($Data)
        if (Test-ReedReadable $utf8) { [void]$found.Add($utf8) }
    } catch { }
    $hasNul = $false
    foreach ($b in $Data) { if ($b -eq 0) { $hasNul = $true; break } }
    if ($Data.Length -gt 0 -and ($Data.Length % 2) -eq 0 -and $hasNul) {
        try {
            $be = [Text.Encoding]::BigEndianUnicode.GetString($Data)
            if (Test-ReedReadable $be) { [void]$found.Add($be) }
        } catch { }
        try {
            $le = [Text.Encoding]::Unicode.GetString($Data)
            if (Test-ReedReadable $le) { [void]$found.Add($le) }
        } catch { }
    }
    return $found
}

function ConvertFrom-ReedHex([string]$Hex) {
    $found = New-Object System.Collections.Generic.List[string]
    if (-not $Hex -or $Hex.Length -gt 480 -or ($Hex.Length % 2) -ne 0 -or $Hex -notmatch '^[0-9A-Fa-f]+$') { return $found }
    $bytes = New-Object byte[] ($Hex.Length / 2)
    for ($i = 0; $i -lt $bytes.Length; $i++) {
        $bytes[$i] = [Convert]::ToByte($Hex.Substring($i * 2, 2), 16)
    }
    $ber = ConvertFrom-ReedBer $bytes
    if ($ber) { [void]$found.Add($ber) }
    foreach ($plain in (ConvertFrom-ReedPlain $bytes)) { [void]$found.Add($plain) }
    return $found
}

function Get-ReedPieces([string]$Text) {
    $pieces = New-Object System.Collections.Generic.List[string]
    [void]$pieces.Add($Text.Trim())
    foreach ($part in ($Text -split ',')) {
        $value = $part.Trim()
        $eq = $value.LastIndexOf('=')
        if ($eq -ge 0) { $value = $value.Substring($eq + 1).Trim() }
        [void]$pieces.Add($value)
    }
    return $pieces
}

function ConvertFrom-ReedPiece([string]$Piece) {
    $value = if ($Piece) { $Piece.Trim() } else { '' }
    if ($value.StartsWith('#')) {
        $compact = [regex]::Replace($value.Substring(1), '\s+', '')
        return ConvertFrom-ReedHex $compact
    }
    if ($value.Length -ge 8 -and ($value.Length % 2) -eq 0 -and $value -match '^[0-9A-Fa-f]+$') {
        return ConvertFrom-ReedHex $value
    }
    return @()
}

function Get-ReedCandidates([string]$Name) {
    $raw = ConvertFrom-ReedEscapes $Name
    $visible = ConvertTo-ReedStrip $raw
    $texts = New-Object System.Collections.Generic.List[string]
    foreach ($text in @($raw, $visible)) {
        if (-not $texts.Contains($text)) { [void]$texts.Add($text) }
        foreach ($piece in (Get-ReedPieces $text)) {
            foreach ($decoded in @(ConvertFrom-ReedPiece $piece)) {
                if ($decoded -and -not $texts.Contains($decoded)) { [void]$texts.Add([string]$decoded) }
            }
        }
    }
    return $texts
}

function Get-ReedMap {
    if ($script:ReedMapReady) { return $script:ReedMap }
    $map = @{}
    $pairs = @(
        0x0430, 'a', 0x0410, 'a', 0x0435, 'e', 0x0415, 'e', 0x0451, 'e', 0x0401, 'e',
        0x043E, 'o', 0x041E, 'o', 0x0440, 'p', 0x0420, 'p', 0x0441, 'c', 0x0421, 'c',
        0x0443, 'y', 0x0423, 'y', 0x0445, 'x', 0x0425, 'x', 0x0456, 'i', 0x0406, 'i',
        0x0455, 's', 0x0405, 's', 0x0458, 'j', 0x0408, 'j', 0x04BB, 'h', 0x04BA, 'h',
        0x0501, 'd', 0x0500, 'd', 0x043C, 'm', 0x041C, 'm', 0x0442, 't', 0x0422, 't',
        0x0412, 'b', 0x0432, 'b', 0x041A, 'k', 0x043A, 'k', 0x041D, 'h', 0x043D, 'h',
        0x04CF, 'l', 0x04C0, 'l', 0x0391, 'a', 0x03B1, 'a', 0x0395, 'e', 0x03B5, 'e',
        0x039F, 'o', 0x03BF, 'o', 0x0399, 'i', 0x03B9, 'i', 0x039A, 'k', 0x03BA, 'k',
        0x03A1, 'p', 0x03C1, 'p', 0x03A4, 't', 0x03C4, 't', 0x03A5, 'y', 0x03C5, 'u',
        0x03A7, 'x', 0x03C7, 'x', 0x0142, 'l', 0x0141, 'l', 0x0131, 'i', 0x017F, 's',
        0x00F8, 'o', 0x00D8, 'o'
    )
    for ($i = 0; $i -lt $pairs.Length; $i += 2) {
        $map[[char]$pairs[$i]] = [string]$pairs[$i + 1]
    }
    $script:ReedMap = $map
    $script:ReedMapReady = $true
    return $map
}

function ConvertTo-ReedFold([string]$Name) {
    if (-not $Name) { return '' }
    $text = $Name.Normalize([Text.NormalizationForm]::FormKC).Normalize([Text.NormalizationForm]::FormD)
    $text = [regex]::Replace($text, '\p{Mn}|\p{Me}', '')
    $map = Get-ReedMap
    $blanks = @{}
    foreach ($cp in 0x115F, 0x1160, 0x1361, 0x2420, 0x2422, 0x2800, 0x303F, 0x3164, 0xFFA0, 0xA8F9) {
        $blanks[[char]$cp] = $true
    }
    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $text.ToCharArray()) {
        if ($map.ContainsKey($ch)) { $ch = [char]$map[$ch] }
        $cp = [int]$ch
        $quote = $cp -in 0x22, 0x27, 0x60, 0x201C, 0x201D, 0x201E, 0x201F, 0x2018, 0x2019, 0x201A, 0x201B, 0x00AB, 0x00BB
        $format = [char]::GetUnicodeCategory($ch) -eq [Globalization.UnicodeCategory]::Format
        if ($ch -eq [char]92 -or $quote -or $format) { continue }
        if ($blanks.ContainsKey($ch) -or [char]::IsWhiteSpace($ch)) {
            [void]$sb.Append(' ')
            continue
        }
        [void]$sb.Append($ch)
    }
    return ([regex]::Replace($sb.ToString().ToLowerInvariant(), '\s+', ' ')).Trim()
}

function Test-ReedPrefix([string]$Folded) {
    if (-not $Folded) { return $false }
    $values = New-Object System.Collections.Generic.List[string]
    [void]$values.Add($Folded)
    foreach ($part in ($Folded -split ',')) {
        $value = $part.Trim()
        $eq = $value.LastIndexOf('=')
        if ($eq -ge 0) { $value = $value.Substring($eq + 1).Trim() }
        [void]$values.Add($value)
    }
    foreach ($value in $values) {
        if ($value.StartsWith('reed mallory', [StringComparison]::Ordinal)) { return $true }
    }
    return $false
}

function Test-ReedMalloryName([string]$Name) {
    # A name the fold cannot read is his, so it does not open a gate.
    try {
        foreach ($text in (Get-ReedCandidates $Name)) {
            if (Test-ReedPrefix (ConvertTo-ReedFold $text)) { return $true }
        }
    } catch {
        return $true
    }
    return $false
}
