<#
.SYNOPSIS
Qualifies the actual Num'ta'reen -GlossSpans launcher on the current PowerShell host.
.DESCRIPTION
Run from the repository root in Windows PowerShell 5.1 and PowerShell 7.
The script intentionally invokes the public PowerShell wrapper and parses its
native Python child output, not the Python explorer directly. No translation
fluency or author attestation is inferred from lexical span candidates.
#>

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$root = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path (Join-Path $root 'scripts') 'Translate-Numtareen.ps1'
if (-not (Test-Path -LiteralPath $launcher -PathType Leaf)) {
    throw "Missing translator launcher: $launcher"
}

function Invoke-GlossSpans([string]$Text) {
    $lines = @(& $launcher -Direction en-nt -GlossSpans -Text $Text)
    if ($LASTEXITCODE -ne 0) {
        throw "Gloss-span launcher exited $LASTEXITCODE"
    }
    $serialized = $lines -join "`n"
    try {
        $document = ConvertFrom-Json -InputObject $serialized -ErrorAction Stop
        return $document
    } catch {
        throw "Gloss-span output was not one valid JSON document: $_"
    }
}

# Source-backed multiword dictionary entry, embedded in a longer clause.
# This does not establish a fluent generated translation.
$utterance = 'I noticed witnessed alignment. yesterday'
$result = Invoke-GlossSpans $utterance
if ($result.schema -cne 'numtareen.experimental.english_gloss_spans.v0') {
    throw 'Unexpected gloss-span schema'
}
if ($result.input -cne $utterance) {
    throw 'PowerShell launcher changed the requested English input'
}
if ($result.status -cne 'partial') {
    throw 'Expected a partial lexical span result with unknown words'
}
$attestedGlossCandidate = @($result.spans | Where-Object {
    $_.english_span -ceq 'witnessed alignment' -and
    @($_.candidates | Where-Object {
        $_.headword -ceq ('ech' + [char]0x2019 + 'n' + [char]0x00FB + 'm')
    }).Count -ge 1
})
if ($attestedGlossCandidate.Count -lt 1) {
    throw 'Missing known source dictionary candidate for the multiword English span'
}
if (@($result.uncovered).Count -lt 1) {
    throw 'Unmatched words were silently discarded'
}
if (@($result.PSObject.Properties.Name) -contains 'translation') {
    throw 'The lexical explorer fabricated a complete sentence translation'
}

# Probe UTF-8, a non-BMP code point, literal shell-looking text, and quotes.
# Nothing in the input should be evaluated as PowerShell syntax or dropped.
$nonBmp = [char]::ConvertFromUtf32(0x1F680)
$quoted = 'witnessed alignment; emb"edded $([math]::Abs(-7)) ' + $nonBmp
$escaped = Invoke-GlossSpans $quoted
if ($escaped.input -cne $quoted) {
    throw 'UTF-8/Base64 transport altered Unicode, quotes, or literal shell syntax'
}

# Parentheses belong to an attested dictionary gloss, not throwaway punctuation.
$parenthetical = Invoke-GlossSpans 'this is home-realm (endonym), perhaps'
if (@($parenthetical.spans | Where-Object {
    $_.english_span -ceq 'home-realm (endonym)'
}).Count -lt 1) {
    throw 'Parenthetical multiword dictionary gloss was lost'
}

# A wrong direction is rejected at the wrapper boundary, before Python launch.
$rejected = $false
try {
    & $launcher -Direction nt-en -GlossSpans -Text 'witnessed alignment' | Out-Null
} catch {
    if ($_.Exception.Message -notlike '*requires -Direction en-nt*') {
        throw
    }
    $rejected = $true
}
if (-not $rejected) {
    throw 'PowerShell wrapper accepted the invalid gloss-span direction'
}

Write-Output 'PowerShell gloss-span wrapper: PASS (JSON, source phrase, Unicode, quotes, direction gate)'
