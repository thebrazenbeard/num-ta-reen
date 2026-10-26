<#
.SYNOPSIS
Retrieves author-attested Num'ta'reen IPA from a local repository.
.DESCRIPTION
Returns an evidence object, including source ID and status. Does NOT infer
pronunciation for arbitrary phrases or reconstruct native resonance. Requires
Python 3.10+ and a complete repository clone; no network or packages.
.EXAMPLE
(./scripts/Get-NumtareenPronunciation.ps1 -Text 'Nûm ta=en ech.').ipa
.EXAMPLE
./scripts/Get-NumtareenPronunciation.ps1 -Text 'unattested phrase'
.EXAMPLE
./scripts/Get-NumtareenPronunciation.ps1 -Text 'veyl' -AsJson
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [AllowEmptyString()]
    [string]$Text,

    [switch]$AsJson,

    # Supports running independent tests against a source-pinned checkout.
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

Set-StrictMode -Version Latest
$runner = Join-Path $PSScriptRoot 'phonetic_cli.py'
if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) {
    throw 'Pronunciation transport module is missing; use a complete repository clone.'
}
$package = Join-Path (Join-Path $RepoRoot 'numtareen') 'phonetic_bridge.py'
if (-not (Test-Path -LiteralPath $package -PathType Leaf)) {
    throw 'Source-attested pronunciation module is missing; use a complete repository clone.'
}

$pythonExe = $null
$pythonPrefix = @()
$candidates = @(
    @{ Name = 'py'; Prefix = @('-3') },
    @{ Name = 'python3'; Prefix = @() },
    @{ Name = 'python'; Prefix = @() }
)
foreach ($candidate in $candidates) {
    $command = Get-Command -Name $candidate.Name -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -eq $command) { continue }
    try {
        $probeArgs = @($candidate.Prefix) + @('--version')
        $probe = & $command.Source @probeArgs 2>$null
        $probeStatus = $LASTEXITCODE
    } catch { continue }
    if ($probeStatus -ne 0) { continue }
    if (("$probe").Trim() -match '^Python\s+([0-9]+)\.([0-9]+)(\.|$)') {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
            $pythonExe = $command.Source
            $pythonPrefix = @($candidate.Prefix)
            break
        }
    }
}
if ($null -eq $pythonExe) { throw 'Python 3.10+ not found on PATH.' }

# The user's text is never a native command argument. Quotation marks,
# apostrophes, decomposed accents, non-BMP symbols, and newlines survive.
$utf8 = [System.Text.UTF8Encoding]::new($false, $true)
$encoded = [Convert]::ToBase64String($utf8.GetBytes($Text))
$pythonArgs = @($pythonPrefix) + @($runner, '--repo-root', $RepoRoot, "--text-base64=$encoded")

$previousOutputEncoding = $OutputEncoding
$previousPythonEncoding = $env:PYTHONIOENCODING
$consoleEncoding = $null
$consoleChanged = $false
try { $consoleEncoding = [Console]::OutputEncoding } catch {}
try {
    $OutputEncoding = $utf8
    $env:PYTHONIOENCODING = 'utf-8'
    if ($null -ne $consoleEncoding) {
        try { [Console]::OutputEncoding = $utf8; $consoleChanged = $true } catch {}
    }
    $output = & $pythonExe @pythonArgs
    $status = $LASTEXITCODE
} finally {
    $OutputEncoding = $previousOutputEncoding
    $env:PYTHONIOENCODING = $previousPythonEncoding
    if ($consoleChanged) {
        try { [Console]::OutputEncoding = $consoleEncoding } catch {}
    }
}
if ($status -notin @(0, 2)) {
    throw 'Pronunciation lookup failed; check source snapshot and input.'
}
$json = (@($output) -join "`n").Trim()
if ($AsJson) { Write-Output $json } else { Write-Output ($json | ConvertFrom-Json) }
