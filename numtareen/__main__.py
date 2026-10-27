"""Command-line interface to the offline, canonical-data-only translator."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import sys

from .engine import DataError, Translator, UnknownTermError, escape_invisible, format_translation
from .lexicon_search import format_search, search_lexicon


HELP = ("Commands: :direction nt-en | :direction en-nt | :unknown mark|keep|error | "
        ":help | :quit")


def configure_output_encoding() -> None:
    """Use UTF-8 for Windows redirected output even under legacy code pages.

    An installed Python on Windows can otherwise default to cp1252 for a
    redirected stream, causing ordinary source IPA and Unicode output to raise
    UnicodeEncodeError. This does not reinterpret the input or data files.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")


def interactive(translator: Translator, direction: str, unknown: str, as_json: bool) -> int:
    print("Offline Nûm’ta’reen ⇄ English. " + HELP)
    while True:
        try:
            text = input(f"[{direction}]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not text:
            continue
        command, _, argument = text.partition(" ")
        command = command.lower()
        if command in {":quit", ":exit", ":q"}:
            return 0
        if command == ":help":
            print(HELP)
            continue
        if command == ":direction":
            if argument not in {"nt-en", "en-nt"}:
                print("Use :direction nt-en or :direction en-nt")
            else:
                direction = argument
            continue
        if command == ":unknown":
            if argument not in {"mark", "keep", "error"}:
                print("Use :unknown mark, keep, or error")
            else:
                unknown = argument
            continue
        if command.startswith(":"):
            print("Unknown command. " + HELP)
            continue
        try:
            result = translator.translate(text, direction=direction, unknown=unknown)
            print(json.dumps(result, ensure_ascii=True, indent=2) if as_json else format_translation(result))
        except (UnknownTermError, ValueError) as exc:
            print(f"Error: {escape_invisible(str(exc))}")


def main(argv: list[str] | None = None) -> int:
    configure_output_encoding()
    parser = argparse.ArgumentParser(description="Source-constrained offline Num’ta’reen ⇄ English lookup")
    parser.add_argument("--direction", choices=("nt-en", "en-nt"), default="nt-en")
    parser.add_argument("--unknown", choices=("mark", "keep", "error"), default="mark")
    parser.add_argument("--json", action="store_true", help="emit machine-readable results")
    parser.add_argument("--gloss-spans", action="store_true",
                        help="research-only: enumerate overlapping source English dictionary spans as JSON")
    parser.add_argument("--match", choices=("exact", "contains"), help="lexicon search matching")
    parser.add_argument("--field", choices=("headword", "gloss", "both"), help="lexicon search field")
    parser.add_argument("--category", help="exact lexicon category filter")
    parser.add_argument("--register", help="exact lexicon register filter")
    parser.add_argument("--taboo", help="exact lexicon taboo classification filter")
    parser.add_argument("--limit", type=int, help="maximum lexicon entries (1..100)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--text", help="phrase to look up")
    mode.add_argument("--text-base64", help="UTF-8 phrase encoded as strict standard Base64; safe PowerShell transport")
    mode.add_argument("--interactive", action="store_true", help="interactive REPL with direction switching")
    mode.add_argument("--lexicon-search", help="search source dictionary without translating")
    mode.add_argument("--lexicon-search-base64",
                      help="search query encoded as strict standard Base64 UTF-8 for PowerShell 5.1")
    args = parser.parse_args(argv)
    # The interactive REPL writes a human banner, prompts, and error messages
    # to stdout. Until it has a defined JSONL protocol, accepting --json here
    # would misrepresent that mixed output as machine-readable JSON.
    if args.interactive and args.json:
        parser.error("--json cannot be combined with --interactive; use --text --json")
    is_search = args.lexicon_search is not None or args.lexicon_search_base64 is not None
    if args.gloss_spans and (is_search or args.interactive):
        parser.error("--gloss-spans requires --text or --text-base64")
    if args.gloss_spans and args.direction != "en-nt":
        parser.error("--gloss-spans requires --direction en-nt")
    if args.gloss_spans and args.unknown != "mark":
        parser.error("--gloss-spans does not apply --unknown policy; use default mark")
    if not is_search and any(getattr(args, key) is not None
                             for key in ("match", "field", "category", "register", "taboo", "limit")):
        parser.error("lexicon search options require --lexicon-search or --lexicon-search-base64")
    try:
        translator = Translator()
        if is_search:
            query = args.lexicon_search
            if args.lexicon_search_base64 is not None:
                try:
                    # A 256-character query uses at most 1024 UTF-8 bytes.
                    # Bound the transport before decoding untrusted input.
                    if len(args.lexicon_search_base64) > 1368:
                        raise ValueError("Encoded search query is too long")
                    query = base64.b64decode(
                        args.lexicon_search_base64.encode("ascii"), validate=True
                    ).decode("utf-8")
                except (UnicodeError, ValueError, binascii.Error) as exc:
                    raise ValueError("--lexicon-search-base64 requires standard Base64 of UTF-8 text") from exc
            result = search_lexicon(
                translator, query, match=args.match or "contains",
                field=args.field or "both", category=args.category,
                register=args.register, taboo=args.taboo,
                limit=args.limit if args.limit is not None else 25,
            )
            print(json.dumps(result, ensure_ascii=True, indent=2)
                  if args.json else format_search(result))
            return 0
        if args.interactive:
            return interactive(translator, args.direction, args.unknown, args.json)
        text = args.text
        if args.text_base64 is not None:
            try:
                text = base64.b64decode(args.text_base64.encode("ascii"), validate=True).decode("utf-8")
            except (UnicodeError, ValueError, binascii.Error) as exc:
                raise ValueError("--text-base64 requires valid standard Base64 of UTF-8 text") from exc
        if args.gloss_spans:
            from .gloss_spans import discover_english_gloss_spans
            result = discover_english_gloss_spans(translator, text)
            print(json.dumps(result, ensure_ascii=True, indent=2))
            return 0
        result = translator.translate(text, direction=args.direction, unknown=args.unknown)
    except UnknownTermError as exc:
        print(f"Error: {escape_invisible(str(exc))}", file=sys.stderr)
        return 2
    except (DataError, ValueError) as exc:
        print(f"Error: {escape_invisible(str(exc))}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2) if args.json else format_translation(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
