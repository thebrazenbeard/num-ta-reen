<#
.SYNOPSIS
Runs the offline Nûm’ta’reen ⇄ English translator from a cloned repository.
.DESCRIPTION
Requires Python 3.10+ and the repository's numtareen package. Works with
Windows PowerShell 5.1 and PowerShell 7. No third-party Python packages.
.EXAMPLE
.\scripts\Translate-Numtareen.ps1 -Direction nt-en -Text "Nûm ta=en ech."
.EXAMPLE
.\scripts\Translate-Numtareen.ps1 -Direction en-nt -Text "Stop. Do not proceed."
.EXAMPLE
.\scripts\Translate-Numtareen.ps1 -Direction en-nt -Interactive
.NOTES
In interactive mode, type ':direction en-nt', ':direction nt-en', or ':quit'.
#>
[CmdletBinding(DefaultParameterSetName = 'Text')]
param(
    [ValidateSet('nt-en', 'en-nt')]
    [string]$Direction = 'nt-en',

    [Parameter(ParameterSetName = 'Text')]
    [AllowEmptyString()]
    [string]$Text,

    [Parameter(ParameterSetName = 'Interactive')]
    [switch]$Interactive,

    [ValidateSet('mark', 'keep', 'error')]
    [string]$Unknown = 'mark'
)

Set-StrictMode -Version Latest

if (-not $Interactive -and -not $PSBoundParameters.ContainsKey('Text')) {
    throw 'Supply -Text or -Interactive.'
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$modulePath = Join-Path (Join-Path $repoRoot 'numtareen') '__main__.py'
if (-not (Test-Path -LiteralPath $modulePath -PathType Leaf)) {
    throw "Translator module is missing: $modulePath. Use a complete repository clone."
}

# 'py -3' is the preferred Windows launcher, but may select Python < 3.10.
# Probe each candidate before invoking the translator so older versions can
# fall through to an installed Python 3.10+ interpreter.
$candidates = @(
    @{ Name = 'py'; Prefix = @('-3') },
    @{ Name = 'python3'; Prefix = @() },
    @{ Name = 'python'; Prefix = @() }
)
$pythonExe = $null
$pythonPrefix = @()
foreach ($candidate in $candidates) {
    $command = Get-Command -Name $candidate.Name -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -eq $command) { continue }

    $probeArgs = @($candidate.Prefix) + @(
        '-c',
        'import sys; print("ok" if sys.version_info >= (3, 10) else "old")'
    )
    $probe = & $command.Source @probeArgs 2>$null
    if ($LASTEXITCODE -eq 0 -and ("$probe").Trim() -eq 'ok') {
        $pythonExe = $command.Source
        $pythonPrefix = @($candidate.Prefix)
        break
    }
}
if ($null -eq $pythonExe) {
    throw 'Python 3.10+ not found. Install it and make py, python3, or python available on PATH.'
}

$pythonArgs = @($pythonPrefix) + @('-m', 'numtareen', '--direction', $Direction, '--unknown', $Unknown)
if ($Interactive) {
    $pythonArgs += '--interactive'
} else {
    # Windows PowerShell 5.1 may rewrite embedded quotes in native arguments.
    # Base64 transports the *exact* UTF-8 input as safe ASCII, including empty,
    # leading-hyphen, punctuation, and non-BMP Unicode characters.
    $transportEncoding = [System.Text.UTF8Encoding]::new($false, $true)
    $encodedText = [Convert]::ToBase64String($transportEncoding.GetBytes($Text))
    $pythonArgs += "--text-base64=$encodedText"
}

# Windows PowerShell 5.1 otherwise decodes native stdout using a legacy
# console code page. Preserve the caller's environment after invocation.
$utf8 = New-Object System.Text.UTF8Encoding -ArgumentList $false
$previousPSOutputEncoding = $OutputEncoding
$previousPythonIOEncoding = $env:PYTHONIOENCODING
$previousConsoleOutputEncoding = $null
$previousConsoleInputEncoding = $null
try { $previousConsoleOutputEncoding = [Console]::OutputEncoding } catch {
    Write-Verbose "Console output encoding is unavailable: $_"
}
try { $previousConsoleInputEncoding = [Console]::InputEncoding } catch {
    Write-Verbose "Console input encoding is unavailable: $_"
}
$consoleOutputChanged = $false
$consoleInputChanged = $false
$status = 1
try {
    $OutputEncoding = $utf8
    $env:PYTHONIOENCODING = 'utf-8'
    if ($null -ne $previousConsoleOutputEncoding) {
        try {
            [Console]::OutputEncoding = $utf8
            $consoleOutputChanged = $true
        } catch {
            Write-Verbose "Console output encoding could not be changed: $_"
        }
    }
    if ($Interactive -and $null -ne $previousConsoleInputEncoding) {
        try {
            [Console]::InputEncoding = $utf8
            $consoleInputChanged = $true
        } catch {
            Write-Verbose "Console input encoding could not be changed: $_"
        }
    }

    Push-Location -LiteralPath $repoRoot
    try {
        & $pythonExe @pythonArgs
        $status = $LASTEXITCODE
    } finally {
        Pop-Location
    }
} finally {
    $OutputEncoding = $previousPSOutputEncoding
    $env:PYTHONIOENCODING = $previousPythonIOEncoding
    if ($consoleOutputChanged) {
        try {
            [Console]::OutputEncoding = $previousConsoleOutputEncoding
        } catch {
            Write-Verbose "Console output encoding could not be restored: $_"
        }
    }
    if ($consoleInputChanged) {
        try {
            [Console]::InputEncoding = $previousConsoleInputEncoding
        } catch {
            Write-Verbose "Console input encoding could not be restored: $_"
        }
    }
}

if ($status -ne 0) {
    exit $status
}
