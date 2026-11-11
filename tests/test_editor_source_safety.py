"""Adversarial, offline tests for the checked-in editor source guard."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
GUARD = REPOSITORY / "security" / "check_editor_source_safety.py"


class EditorSourceSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="numtareen-source-safety-")
        self.addCleanup(self.temp.cleanup)
        self.checkout = Path(self.temp.name)
        font_dir = self.checkout / "public" / "fonts"
        font_dir.mkdir(parents=True)
        # Do not copy the disguised, non-font file into safe test fixtures.
        for asset in (REPOSITORY / "public" / "fonts").iterdir():
            if asset.name != "fa-solid-600.ttf":
                shutil.copyfile(asset, font_dir / asset.name)
        self.editor = self.checkout / ".vscode"
        self.editor.mkdir()
        (self.editor / "tasks.json").write_text('{"version":"2.0.0","tasks":[]}', encoding="utf-8")
        (self.editor / "settings.json").write_text('{"task.allowAutomaticTasks":"off"}', encoding="utf-8")

    def run_guard(self, *expected: str, success: bool = False) -> str:
        result = subprocess.run(
            [sys.executable, str(GUARD), "--root", str(self.checkout)],
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for fragment in expected:
            self.assertIn(fragment, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_minimal_safe_checkout_passes(self) -> None:
        self.run_guard("PASS", success=True)

    def test_jsonc_comments_urls_trailing_commas_and_svg_crlf_are_safe(self) -> None:
        (self.editor / "settings.json").write_text(
            '{// comment\n"task.allowAutomaticTasks":"off", "help":"https://example.org/a,//",}',
            encoding="utf-8",
        )
        svg = self.checkout / "public/fonts/fa-solid-900.svg"
        raw = svg.read_bytes().replace(b"\r\n", b"\n")
        svg.write_bytes(raw.replace(b"\n", b"\r\n"))
        self.run_guard("PASS", success=True)

    def test_bom_folder_open_task_is_rejected(self) -> None:
        (self.editor / "tasks.json").write_text(
            '\ufeff{"version":"2.0.0","tasks":[{"label":"looks harmless",'
            '"command":"node","runOptions":{"runOn":"folderOpen"}}]}',
            encoding="utf-8",
        )
        self.run_guard("checked-in editor tasks", "folderOpen")

    def test_windows_task_override_is_rejected(self) -> None:
        (self.editor / "tasks.json").write_text(
            '{"version":"2.0.0","tasks":[],"windows":{"tasks":[{"runOptions":'
            '{"runOn":"folderOpen"}}]}}',
            encoding="utf-8",
        )
        self.run_guard("folderOpen")

    def test_settings_automatic_permission_and_embedded_task_rejected(self) -> None:
        (self.editor / "settings.json").write_text(
            '{"task.allowAutomaticTasks":true,"tasks":{"windows":{"runOn":"folderOpen"}}}',
            encoding="utf-8",
        )
        self.run_guard("task.allowAutomaticTasks", "embedded settings.tasks", "folderOpen")

    def test_malformed_jsonc_is_not_treated_as_empty_configuration(self) -> None:
        (self.editor / "tasks.json").write_text('{"tasks":[,]}', encoding="utf-8")
        self.run_guard("malformed editor JSONC")

    def test_duplicate_keys_are_not_ambiguously_accepted(self) -> None:
        (self.editor / "settings.json").write_text(
            '{"task.allowAutomaticTasks":true,"TASK.ALLOWAUTOMATICTASKS":"off"}',
            encoding="utf-8",
        )
        self.run_guard("malformed editor JSONC")

    def test_boolean_false_is_not_mistaken_for_valid_editor_setting(self) -> None:
        (self.editor / "settings.json").write_text(
            '{"task.allowAutomaticTasks":false}', encoding="utf-8"
        )
        self.run_guard("task.allowAutomaticTasks must be off")

    def test_gitignore_cannot_hide_future_vscode_or_font_assets(self) -> None:
        (self.checkout / ".gitignore").write_text(
            "# .vscode in a comment is fine\nnode_modules\n**/.VSCODE/\n*.TTF\n",
            encoding="utf-8",
        )
        self.run_guard(".gitignore:3", ".gitignore:4")

    def test_unclosed_jsonc_comment_is_not_accepted(self) -> None:
        (self.editor / "settings.json").write_text('{/*', encoding="utf-8")
        self.run_guard("malformed editor JSONC")

    def test_nested_vscode_tasks_are_not_skipped(self) -> None:
        nested = self.checkout / "subproject" / ".vscode"
        nested.mkdir(parents=True)
        (nested / "tasks.json").write_text('{"tasks":[{"runOptions":{"runOn":"folderOpen"}}]}')
        self.run_guard("subproject/.vscode/tasks.json", "folderOpen")

    def test_casefolded_vscode_directory_is_not_skipped(self) -> None:
        nested = self.checkout / "subproject" / ".VSCODE"
        nested.mkdir(parents=True)
        (nested / "TASKS.JSON").write_text('{"tasks":[{"runOptions":{"runOn":"folderOpen"}}]}')
        self.run_guard("subproject/.VSCODE/TASKS.JSON", "folderOpen")

    def test_nested_uppercase_workspace_is_not_skipped(self) -> None:
        workspace = self.checkout / "subproject" / "WORLD.CODE-WORKSPACE"
        workspace.parent.mkdir(parents=True)
        workspace.write_text('{"tasks":{"windows":{"tasks":[{"runOptions":'
                             '{"runOn":"folderOpen"}}]}}}')
        self.run_guard("WORLD.CODE-WORKSPACE", "folderOpen")

    def test_symlink_font_is_rejected(self) -> None:
        (self.checkout / "public/fonts/alias.ttf").symlink_to("fa-solid-900.ttf")
        self.run_guard("security-relevant symlinks")

    def test_reintroduced_script_under_font_name_is_rejected(self) -> None:
        (self.checkout / "public/fonts/fa-solid-600.ttf").write_bytes(b"// not actually a TTF")
        self.run_guard("unknown font asset")

    def test_valid_header_with_hidden_payload_is_rejected(self) -> None:
        font = self.checkout / "public/fonts/fa-solid-900.ttf"
        font.write_bytes(font.read_bytes() + b"\n// unexpected appended data")
        self.run_guard("font asset changed from pinned SHA-256")

    def test_changed_font_svg_is_rejected(self) -> None:
        svg = self.checkout / "public/fonts/fa-solid-900.svg"
        svg.write_bytes(svg.read_bytes() + b"\n<!-- unexpected appended data -->")
        self.run_guard("font asset changed from pinned SHA-256")

    def test_missing_font_is_rejected(self) -> None:
        (self.checkout / "public/fonts/fa-solid-900.ttf").unlink()
        self.run_guard("missing pinned assets")


if __name__ == "__main__":
    unittest.main()
