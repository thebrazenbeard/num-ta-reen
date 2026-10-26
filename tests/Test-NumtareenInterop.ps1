# Private-repository Windows PowerShell 5.1 / PowerShell 7 smoke test.
# Run from the root of a cloned num-ta-reen repository with Python on PATH.
# Never log authored language content or full adapter JSON records.

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$corpusPath = Join-Path $repoRoot 'data/corpus.json'

if (-not (Test-Path $corpusPath)) { throw 'Private corpus fixture missing' }
$corpus = Get-Content -LiteralPath $corpusPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($corpus.records.Count -ne 30) { throw 'Expected 30 source-attested records' }

function ConvertTo-AsciiJson {
    param([Parameter(Mandatory = $true)] $Value)
    $json = ConvertTo-Json -InputObject $Value -Compress -Depth 12
    # Native Windows PowerShell pipelines can use legacy code pages. Encode
    # every non-ASCII UTF-16 code unit as a JSON \u escape; pairs survive.
    $builder = New-Object System.Text.StringBuilder
    foreach ($ch in $json.ToCharArray()) {
        $n = [int][char]$ch
        if ($n -gt 127) {
            [void]$builder.AppendFormat('\u{0:x4}', $n)
        } else {
            [void]$builder.Append($ch)
        }
    }
    return $builder.ToString()
}

function Invoke-ReferenceAdapter {
    param([Parameter(Mandatory = $true)] [string] $Direction,
          [Parameter(Mandatory = $true)] [string] $Text)
    $payload = ConvertTo-AsciiJson @{ direction = $Direction; text = $Text }
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
        $proc.StandardInput.WriteLine($payload)
        $proc.StandardInput.Close()
        $output = $proc.StandardOutput.ReadToEnd()
        $errors = $proc.StandardError.ReadToEnd()
        $proc.WaitForExit()
        if ($proc.ExitCode -ne 0 -or -not $output.Trim()) {
            # Never dump stderr/stdout because the private translation can be
            # present there. Report only a bounded diagnostic category.
            throw 'Adapter process failed or produced empty output'
        }
        $result = $output.Trim() | ConvertFrom-Json
        if (-not $result.ok -or $null -eq $result.record) {
            throw 'Adapter returned an error or an incomplete success envelope'
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

$nonBmp = [char]::ConvertFromUtf32(0x1F680)
$probe = 'unattested "quoted" ' + $nonBmp + ' nûm'
$unknown = Invoke-ReferenceAdapter -Direction 'nt-en' -Text $probe
if ($unknown.source_text -cne $probe -or $unknown.target_text -ne $null) {
    throw 'Unicode, quotation, or unknown-text handling failed'
}

$trueName = $corpus.records | Where-Object { $_.id -eq 'E26' } | Select-Object -First 1
if ($null -eq $trueName) { throw 'Missing true-name source record' }
$withheld = Invoke-ReferenceAdapter -Direction 'nt-en' -Text $trueName.orthography_index
if ($withheld.withheld -ne $true -or $withheld.target_text -ne $null) {
    throw 'True-name chord was exposed as an ordinary target'
}

Write-Output 'Private Windows adapter smoke PASS (attested, Unicode, unknown, withheld)'
