"""Command-line interface to the offline, canonical-data-only translator."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import sys

from .engine import DataError, Translator, UnknownTermError, escape_invisible, format_translation


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
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--text", help="phrase to look up")
    mode.add_argument("--text-base64", help="UTF-8 phrase encoded as strict standard Base64; safe PowerShell transport")
    mode.add_argument("--interactive", action="store_true", help="interactive REPL with direction switching")
    args = parser.parse_args(argv)
    try:
        translator = Translator()
        if args.interactive:
            return interactive(translator, args.direction, args.unknown, args.json)
        text = args.text
        if args.text_base64 is not None:
            try:
                text = base64.b64decode(args.text_base64.encode("ascii"), validate=True).decode("utf-8")
            except (UnicodeError, ValueError, binascii.Error) as exc:
                raise ValueError("--text-base64 requires valid standard Base64 of UTF-8 text") from exc
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
