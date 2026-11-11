"""Fail-closed repository-source guard for concealed editor startup mechanisms.

This is a static source check, not a workstation or VS Code runtime probe.
Run: python security/check_editor_source_safety.py [--root CHECKOUT]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


# SHA-256 of the 15 verified Font Awesome assets in this checkout. SVG hashes
# apply after CRLF -> LF normalization, for Windows checkout compatibility.
KNOWN_FONT_SHA256 = {
    "fa-brands-400.eot": "811e1577184066108ceca86d5a624a9012303df5206c5cb0b27d5e3fedcba5a3",
    "fa-brands-400.svg": "02340ba1789d09bcc507563c89c4a847ba537bb8132082777a50519cf74bcb5b",
    "fa-brands-400.ttf": "a0c145382acfe59767d1487d6505f349665b685c2885cd91b621d141a292b0f8",
    "fa-brands-400.woff": "e836c5d5dfc13e18170c5bddefb4fdac7c65ac0ad43a4b431acdc4a98865a260",
    "fa-brands-400.woff2": "5d9190292acdd48ba0fc35080f7e7448f3cdf0d79199a4d23f0f49b5341fdf29",
    "fa-regular-400.eot": "01f4416f5db59e2dd6b6fbd9dc32336d99db18f7eb623a49f584d04afd279473",
    "fa-regular-400.svg": "865fd23de13b1920280e182359579e09eff7a09eb24676eceec7552838559f55",
    "fa-regular-400.ttf": "f32b94a29060dfec0c797a1dfe111357eb1d682f1aca4ac4b95cf0f4c3e2bfa9",
    "fa-regular-400.woff": "8e2d96198711b63752e5f2f5987b8ffc536df6156a065bdbe28cb7231cad793d",
    "fa-regular-400.woff2": "6a8c8e9e1e7f692c21af1956de163f3d026778e6449fe93a09a671847ca1ae65",
    "fa-solid-900.eot": "32501727bb23fc77615b1ec76b5f298ec22198c0f3d6a3e7d6fe4ac3cf315db9",
    "fa-solid-900.svg": "e768539808757f7eec20f09c9ee9b36b0e6c5636e90c9ee697995cbbc6ee0555",
    "fa-solid-900.ttf": "231d68cefbc6846fb78cafca8467401a4f371e226418662e8900e3d52adc00ab",
    "fa-solid-900.woff": "352f8ead280419dd953d2bc7843386bb9430e8152c2dbd2c2d2494f6b9567ee7",
    "fa-solid-900.woff2": "7f4d3fd0a705dbf8403298aad91d5de6972e6b5d536068eba8b24954a5a0a8c7",
}

IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".pytest_cache"}


def strip_jsonc(source: str) -> str:
    """Strip JSONC comments and trailing commas without changing string values."""
    if source.startswith("\ufeff"):
        source = source[1:]
    out: list[str] = []
    quoted = False
    escaped = False
    index = 0
    while index < len(source):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ""
        if quoted:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            index += 1
            continue
        if char == '"':
            quoted = True
            out.append(char)
            index += 1
            continue
        if char == "/" and nxt == "/":
            index += 2
            while index < len(source) and source[index] not in "\r\n":
                index += 1
            continue
        if char == "/" and nxt == "*":
            close = source.find("*/", index + 2)
            if close < 0:
                raise ValueError("unclosed block comment")
            index = close + 2
            continue
        out.append(char)
        index += 1

    stripped = "".join(out)
    out = []
    quoted = escaped = False
    for index, char in enumerate(stripped):
        if quoted:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
            out.append(char)
            continue
        if char == ",":
            following = stripped[index + 1 :].lstrip()
            preceding = next((part for part in reversed(out) if not part.isspace()), "")
            if preceding not in ("", "[", "{", ",", ":") and following.startswith(("}", "]")):
                continue
        out.append(char)
    return "".join(out)


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguous JSONC key collisions, including Windows case variants."""
    result: dict[str, object] = {}
    prior: set[str] = set()
    for key, value in pairs:
        folded = key.casefold()
        if folded in prior:
            raise ValueError("duplicate editor configuration key")
        prior.add(folded)
        result[key] = value
    return result


def inspect_json_value(value: object, path: str, errors: list[str], *, settings: bool = False) -> None:
    if isinstance(value, list):
        for item in value:
            inspect_json_value(item, path, errors, settings=settings)
    elif isinstance(value, dict):
        for key, item in value.items():
            key_folded = str(key).casefold()
            if key_folded == "runon" and str(item).strip().casefold() == "folderopen":
                errors.append(f"{path}: automatic folderOpen execution is prohibited")
            if key_folded == "task.allowautomatictasks" and item != "off":
                errors.append(f"{path}: task.allowAutomaticTasks must be off")
            if settings and key_folded == "tasks" and item:
                errors.append(f"{path}: embedded settings.tasks is prohibited")
            inspect_json_value(item, path, errors, settings=settings)


def inspect_file(root: Path, file_path: Path, errors: list[str]) -> None:
    relative = file_path.relative_to(root)
    segments = [part.casefold() for part in relative.parts]
    label = relative.as_posix()
    if file_path.is_symlink():
        if ".vscode" in segments or "fonts" in segments or label.casefold().endswith(".code-workspace"):
            errors.append(f"{label}: security-relevant symlinks are prohibited")
        return

    if len(segments) >= 3 and segments[0:2] == ["public", "fonts"]:
        # Font README is explanatory text; all actual font data is pinned.
        if segments[2:] == ["readme.md"]:
            return
        if len(segments) != 3 or label.split("/")[-1] not in KNOWN_FONT_SHA256:
            errors.append(f"{label}: unknown font asset")
            return
        raw = file_path.read_bytes()
        filename = file_path.name
        if filename.endswith(".ttf") and not raw.startswith((b"\x00\x01\x00\x00", b"OTTO", b"true", b"typ1")):
            errors.append(f"{label}: invalid TrueType/OpenType header")
        if filename.endswith(".woff") and not raw.startswith(b"wOFF"):
            errors.append(f"{label}: invalid WOFF header")
        if filename.endswith(".woff2") and not raw.startswith(b"wOF2"):
            errors.append(f"{label}: invalid WOFF2 header")
        if filename.endswith(".svg"):
            raw = raw.replace(b"\r\n", b"\n")
        if hashlib.sha256(raw).hexdigest() != KNOWN_FONT_SHA256[filename]:
            errors.append(f"{label}: font asset changed from pinned SHA-256")
        return

    is_task_file = len(segments) >= 2 and segments[-2:] == [".vscode", "tasks.json"]
    is_settings = len(segments) >= 2 and segments[-2:] == [".vscode", "settings.json"]
    is_workspace = segments[-1].endswith(".code-workspace")
    if not (is_task_file or is_settings or is_workspace):
        return
    try:
        decoded = file_path.read_text(encoding="utf-8-sig")
        doc = json.loads(strip_jsonc(decoded), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{label}: unreadable or malformed editor JSONC ({type(exc).__name__})")
        return
    if not isinstance(doc, dict):
        errors.append(f"{label}: editor configuration must be an object")
        return
    if is_task_file and (not isinstance(doc.get("tasks"), list) or doc["tasks"]):
        errors.append(f"{label}: checked-in editor tasks must be an empty list")
    inspect_json_value(doc, label, errors, settings=is_settings)


def check_repository(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"{root}: root does not exist"]
    ignore_path = root / ".gitignore"
    if ignore_path.is_symlink():
        errors.append(".gitignore: symlink hides review of source ignore patterns")
    elif ignore_path.exists():
        try:
            for line_number, line in enumerate(ignore_path.read_text(encoding="utf-8-sig").splitlines(), 1):
                rule = line.strip()
                if not rule or rule.startswith("#"):
                    continue
                folded = rule.casefold()
                # These patterns could conceal future editor files or counterfeit
                # font payloads from source-based PR checks.
                if any(marker in folded for marker in
                       (".vscode", ".code-workspace", "fonts", "*.ttf", "*.eot", "*.woff", "*.svg")):
                    errors.append(f".gitignore:{line_number}: security-relevant ignore rule")
        except (UnicodeError, OSError):
            errors.append(".gitignore: cannot inspect source ignore patterns")
    observed_fonts: set[str] = set()
    for dir_path, dirs, files in os.walk(root, followlinks=False):
        current = Path(dir_path)
        for name in list(dirs):
            candidate = current / name
            rel = candidate.relative_to(root)
            if name.casefold() in IGNORED_DIRS:
                dirs.remove(name)
            elif candidate.is_symlink():
                errors.append(f"{rel.as_posix()}: symbolic directory not scanned")
                dirs.remove(name)
        for name in files:
            candidate = current / name
            relative = candidate.relative_to(root)
            parts = [piece.casefold() for piece in relative.parts]
            if len(parts) == 3 and parts[:2] == ["public", "fonts"] and parts[2] != "readme.md":
                observed_fonts.add(name)
            try:
                inspect_file(root, candidate, errors)
            except (OSError, PermissionError) as exc:
                errors.append(f"{relative.as_posix()}: cannot read: {type(exc).__name__}")
    missing = sorted(set(KNOWN_FONT_SHA256) - observed_fonts)
    if missing:
        errors.append("public/fonts: missing pinned assets: " + ", ".join(missing))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check_repository(args.root.resolve())
    if errors:
        for error in errors:
            print("FAIL " + error, file=sys.stderr)
        return 1
    print("PASS: editor configurations and pinned font data are source-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
