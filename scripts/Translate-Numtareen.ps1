<#
.SYNOPSIS
Offline Num'ta'reen-English translation using the repository's Python CLI.
.EXAMPLE
.\scripts\Translate-Numtareen.ps1 -Direction nt-en -Text "Nûm ta=en ech."
.EXAMPLE
.\scripts\Translate-Numtareen.ps1 -Direction en-nt -Text "Stop. Do not proceed."
.EXAMPLE
.\scripts\Translate-Numtareen.ps1 -Direction en-nt -Interactive
#>
[CmdletBinding()]
param(
    [ValidateSet('nt-en', 'en-nt')]
    [string]$Direction = 'nt-en',
    [string]$Text,
    [switch]$Interactive,
    [ValidateSet('mark', 'keep', 'error')]
    [string]$Unknown = 'mark'
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Get-Command 'py' -ErrorAction SilentlyContinue
$prefix = @()
if ($null -ne $python) {
    $exe = $python.Source
    $prefix = @('-3')
} else {
    $python = Get-Command 'python' -ErrorAction SilentlyContinue
    if ($null -eq $python) {
        throw 'Python 3.10+ not found. Install Python and ensure `py` or `python` is on PATH.'
    }
    $exe = $python.Source
}

if ($Interactive -and $PSBoundParameters.ContainsKey('Text')) {
    throw 'Choose -Interactive or -Text, not both.'
}
if (-not $Interactive -and -not $PSBoundParameters.ContainsKey('Text')) {
    throw 'Supply -Text or -Interactive.'
}

$pythonArgs = @($prefix) + @('-m', 'numtareen', '--direction', $Direction, '--unknown', $Unknown)
if ($Interactive) {
    $pythonArgs += '--interactive'
} else {
    $pythonArgs += @('--text', $Text)
}

Push-Location -LiteralPath $repoRoot
try {
    & $exe @pythonArgs
    $status = $LASTEXITCODE
} finally {
    Pop-Location
}
if ($status -ne 0) {
    exit $status
}
