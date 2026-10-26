# Attested pronunciation from PowerShell (noncanonical)

The existing `Translate-Numtareen.ps1` remains the offline bilingual lookup;
`Get-NumtareenPronunciation.ps1` is a separate exact-source IPA reference.
Both commands use no network service, AI model, or invented dictionary words.

```powershell
# Source-written sentence, Num’ta’reen -> English
.\scripts\Translate-Numtareen.ps1 -Direction nt-en -Text 'Nûm ta=en ech.'

# Source-written sentence, English -> Num’ta’reen
.\scripts\Translate-Numtareen.ps1 -Direction en-nt -Text 'Stop. Do not proceed.'

# Retrieve the exact attested whole-utterance IPA and its source locator
$p = .\scripts\Get-NumtareenPronunciation.ps1 -Text 'Nûm ta=en ech.'
$p.ipa
$p.evidence_class
$p.source_locator

# A dictionary headword is only an isolated lexical IPA, not connected speech
.\scripts\Get-NumtareenPronunciation.ps1 -Text 'veyl' -AsJson

# Unknown phrases return status UNKNOWN and ipa=$null; no guessed phonetics
.\scripts\Get-NumtareenPronunciation.ps1 -Text 'unattested phrase'
```

The new script uses strict Base64-encoded UTF-8 when crossing the Windows
PowerShell 5.1 native process boundary. `phonetic_cli.py` validates the input
before passing it to the SHA256-source-pinned `AttestedPronunciationGuide`.
The JSON result remains ASCII-escaped for cp1252 console safety; the PowerShell
wrapper's default parsed object provides readable IPA. Quotation marks,
non-BMP characters, and newlines are preserved, not evaluated as commands.

Evidence classes and limits:

- `ATTESTED_UTTERANCE`: exact author-supplied corpus transcription.
- `ATTESTED_LEXEME`: author dictionary IPA for an isolated headword.
- `UNKNOWN`: no attested pronunciation; the tool abstains.
- `WITHHELD`: protected true-name notation, never printed or sounded out.

Neither this interface nor the existing translation utility provides an
unrestricted productive translator, native Ech’ta’reen frequency decoder,
learned speech model, or author-approved expansion of language canon.

Verification in a complete clone:

```powershell
py -3 -m unittest discover -s tests -p test_phonetic_transport.py -v
```

Run on Windows PowerShell 5.1 and PowerShell 7 before claiming host-specific
qualification; Linux Python tests alone do not demonstrate the native shell.
The native test suite contains **separate** PS7 (`pwsh`) and Windows PowerShell
5.1 (`powershell`) cases for attested IPA, unknown inputs, and protected-source
withholding. An unavailable shell is an explicit skip in local development;
Windows GitHub CI sets `NUMTAREEN_REQUIRE_SHELLS=pwsh,powershell` to make
either missing runtime a test failure. The accompanying workflow change runs
the qualification on every Windows Python matrix job, not whichever shell
happens to appear first on `PATH`.
