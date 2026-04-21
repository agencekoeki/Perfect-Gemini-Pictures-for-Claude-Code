#!/usr/bin/env python3
"""Test du script gemini_call.py avec un mock du SDK.

Permet de vérifier :
    - le parsing des arguments CLI
    - la construction de la requête
    - l'extraction de l'image et des métadonnées
    - l'écriture des fichiers de sortie

sans dépendre d'un vrai appel API ni d'une clé GEMINI_API_KEY.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def _fake_png_bytes() -> bytes:
    # 1x1 PNG RED.
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    )


def _build_fake_response(png_bytes: bytes) -> SimpleNamespace:
    inline = SimpleNamespace(data=png_bytes, mime_type="image/png")
    part = SimpleNamespace(thought=False, inline_data=inline, text="")
    thought_part = SimpleNamespace(thought=True, inline_data=None, text="reasoning steps")
    content = SimpleNamespace(parts=[thought_part, part])
    candidate = SimpleNamespace(content=content, finish_reason="STOP")
    return SimpleNamespace(candidates=[candidate], text="")


class _FakeClient:
    class _Models:
        def generate_content(self, model, contents, config):  # noqa: D401, ARG002
            return _build_fake_response(_fake_png_bytes())

    def __init__(self, api_key=None):  # noqa: ARG002
        self.models = self._Models()


class _FakeTypes:
    class Part:
        @staticmethod
        def from_bytes(data, mime_type):  # noqa: ARG004
            return SimpleNamespace(inline_data=SimpleNamespace(data=data, mime_type=mime_type))

    @staticmethod
    def ImageConfig(**kwargs):  # noqa: N802
        return SimpleNamespace(**kwargs)

    @staticmethod
    def ThinkingConfig(**kwargs):  # noqa: N802
        return SimpleNamespace(**kwargs)

    @staticmethod
    def GoogleSearch():  # noqa: N802
        return SimpleNamespace()

    @staticmethod
    def Tool(**kwargs):  # noqa: N802
        return SimpleNamespace(**kwargs)

    @staticmethod
    def GenerateContentConfig(**kwargs):  # noqa: N802
        return SimpleNamespace(**kwargs)


def test_generate_mode() -> None:
    import gemini_call as gc

    with tempfile.TemporaryDirectory() as tmp:
        prompt_file = Path(tmp) / "prompt.txt"
        prompt_file.write_text("A test prompt", encoding="utf-8")
        output = Path(tmp) / "out.png"
        metadata = Path(tmp) / "meta.json"

        os.environ["GEMINI_API_KEY"] = "test-key"

        with patch.object(gc, "_load_genai", return_value=(SimpleNamespace(Client=_FakeClient), _FakeTypes)):
            exit_code = gc.main([
                "--mode", "generate",
                "--prompt-file", str(prompt_file),
                "--model", "flash",
                "--aspect-ratio", "1:1",
                "--resolution", "1K",
                "--thinking-level", "minimal",
                "--output", str(output),
                "--metadata-output", str(metadata),
            ])

        assert exit_code == 0
        assert output.exists() and output.stat().st_size > 0
        meta = json.loads(metadata.read_text(encoding="utf-8"))
        assert meta["model"] == "gemini-3.1-flash-image-preview"
        assert meta["thinking_level"] == "minimal"
        assert "reasoning steps" in meta["thoughts"]
        print("OK test_generate_mode")


def test_missing_prompt_file() -> None:
    import gemini_call as gc
    os.environ["GEMINI_API_KEY"] = "test-key"
    with patch.object(gc, "_load_genai", return_value=(SimpleNamespace(Client=_FakeClient), _FakeTypes)):
        try:
            gc.main([
                "--mode", "generate",
                "--prompt-file", "/nonexistent/path.txt",
                "--output", "/tmp/out.png",
            ])
            raise AssertionError("Should have exited with non-zero code.")
        except SystemExit as exc:
            assert exc.code == 4
            print("OK test_missing_prompt_file")


def test_no_api_key() -> None:
    import gemini_call as gc
    os.environ.pop("GEMINI_API_KEY", None)
    with tempfile.TemporaryDirectory() as tmp:
        prompt_file = Path(tmp) / "prompt.txt"
        prompt_file.write_text("A test", encoding="utf-8")
        with patch.object(gc, "_load_genai", return_value=(SimpleNamespace(Client=_FakeClient), _FakeTypes)):
            try:
                gc.main([
                    "--mode", "generate",
                    "--prompt-file", str(prompt_file),
                    "--output", str(Path(tmp) / "out.png"),
                ])
                raise AssertionError("Should have exited.")
            except SystemExit as exc:
                assert exc.code == 3
                print("OK test_no_api_key")


if __name__ == "__main__":
    test_generate_mode()
    test_missing_prompt_file()
    test_no_api_key()
    print("\nTous les tests mock sont passés.")
