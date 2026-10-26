# Private-repository Windows PowerShell 5.1 / PowerShell 7 smoke test.
# Run from the root of a cloned num-ta-reen repository with Python on PATH.
# Never log authored language content or full adapter JSON records.

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$corpusPath = Join-Path $repoRoot 'data/corpus.json'

if (-not (Test-Path $corpusPath)) { throw 'Private corpus fixture missing' }
$corpus = Get-Content -LiteralPath $corpusPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($corpus.records.Count -ne 30) { throw 'Expected 30 source-attested records' }

function Invoke-ReferenceAdapter {
    param([Parameter(Mandatory = $true)] [string] $Direction,
          [Parameter(Mandatory = $true)] [string] $Text)
    if ($Direction -notin @('nt-en', 'en-nt')) {
        throw 'Invalid test translation direction'
    }
    # The only interpolated value is strict Base64. The direction is an
    # allowlisted ASCII literal, so this JSON cannot depend on PowerShell 5.1
    # ConvertTo-Json's treatment of true-name chord notation or code pages.
    $utf8 = [System.Text.UTF8Encoding]::new($false, $true)
    $encoded = [System.Convert]::ToBase64String($utf8.GetBytes($Text))
    $payload = '{"direction":"' + $Direction + '","text_base64":"' + $encoded + '"}'
    if ([System.Text.Encoding]::ASCII.GetByteCount($payload) -gt 65536) {
        throw 'Private test fixture unexpectedly exceeds protocol frame cap'
    }
    $start = New-Object System.Diagnostics.ProcessStartInfo
    $start.FileName = 'python'
    $start.Arguments = '-m numtareen.interop'
    $start.WorkingDirectory = $repoRoot
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $proc = [System.Diagnostics.Process]::Start($start)
    try {
        # The payload is already entirely ASCII (Unicode is UTF-8 Base64).
        # Write exact bytes to bypass Windows PowerShell 5.1's
        # .NET Framework StreamWriter encoding/preamble behavior. One LF ends
        # the frame; closing the underlying stream signals EOF to Python.
        $bytes = [System.Text.Encoding]::ASCII.GetBytes($payload + "`n")
        $stdin = $proc.StandardInput.BaseStream
        $stdin.Write($bytes, 0, $bytes.Length)
        $stdin.Flush()
        $stdin.Close()
        $output = $proc.StandardOutput.ReadToEnd()
        $errors = $proc.StandardError.ReadToEnd()
        $proc.WaitForExit()
        if ($proc.ExitCode -ne 0) {
            # Never dump stderr/stdout because the private translation can be
            # present there. Report only a bounded diagnostic category.
            throw 'Adapter process exited nonzero'
        }
        if (-not $output.Trim()) {
            throw 'Adapter process produced empty output'
        }
        $result = $output.Trim() | ConvertFrom-Json
        if (-not $result.ok) {
            $code = [string]$result.error.code
            if ($code -notmatch '^[A-Z_]{1,40}$') { $code = 'UNCLASSIFIED' }
            throw "Adapter rejected request: $code"
        }
        if ($null -eq $result.record) {
            throw 'Adapter returned incomplete success envelope'
        }
        $record = $result.record
        if ($record.qualification_eligible -ne $false -or
            $record.learner_visible -ne $false -or
            $record.source_independence -ne 'SINGLE_AUTHOR_REFERENCE' -or
            $record.semantic_atoms -ne $null) {
            throw 'Adapter breached the author-reference evidence boundary'
        }
        return $record
    } finally {
        if (-not $proc.HasExited) { $proc.Kill() }
        $proc.Dispose()
    }
}

$first = $corpus.records[0]
$attested = Invoke-ReferenceAdapter -Direction 'nt-en' -Text $first.orthography_index
if ($attested.evidence_class -ne 'AUTHOR_ATTESTED_CORPUS' -or
    $attested.origin.record_id -ne $first.id -or
    $attested.target_text -cne $first.english) {
    throw 'Source-attested private reference roundtrip failed'
}
Write-Output 'Private adapter attested smoke passed'

$nonBmp = [char]::ConvertFromUtf32(0x1F680)
$probe = 'unattested "quoted" ' + $nonBmp + ' n' + [char]0x00FB + 'm'
$unknown = Invoke-ReferenceAdapter -Direction 'nt-en' -Text $probe
if ($unknown.source_text -cne $probe -or $unknown.target_text -ne $null) {
    throw 'Unicode, quotation, or unknown-text handling failed'
}
Write-Output 'Private adapter unknown Unicode smoke passed'

$trueName = $corpus.records | Where-Object { $_.id -eq 'E26' } | Select-Object -First 1
if ($null -eq $trueName) { throw 'Missing true-name source record' }
$withheld = Invoke-ReferenceAdapter -Direction 'nt-en' -Text $trueName.orthography_index
if ($withheld.withheld -ne $true -or $withheld.target_text -ne $null -or
    $withheld.source_text -ne $null -or $withheld.origin.record_id -ne 'E26') {
    throw 'True-name chord was exposed as an ordinary target'
}

Write-Output 'Private Windows adapter smoke PASS (attested, Unicode, unknown, withheld)'
