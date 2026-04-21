#!/usr/bin/env python3
"""Appel de l'API Gemini pour génération d'image ou recherche ancrée.

Ce script centralise tous les appels vers Gemini (modes `flash` et `pro`) ainsi
que les appels de recherche en ligne utilisés par la skill `pgp-moodboard`.

Utilisation typique (génération image) :

    python scripts/gemini_call.py \\
        --prompt-file ./.pgp-session/gemini-prompt.txt \\
        --model flash \\
        --aspect-ratio 9:16 \\
        --resolution 1K \\
        --thinking-level minimal \\
        --output ./.pgp-session/raw-gemini.png \\
        --metadata-output ./.pgp-session/gemini-metadata.json

Utilisation recherche (grounding) :

    python scripts/gemini_call.py \\
        --mode research \\
        --query "photographie lifestyle van aménagé matin" \\
        --metadata-output ./.pgp-session/moodboard-raw.json
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
from pathlib import Path
from typing import Any

MODEL_FLASH = "gemini-3.1-flash-image-preview"
MODEL_PRO = "gemini-3-pro-image-preview"

COST_PER_IMAGE = {
    MODEL_FLASH: 0.045,
    MODEL_PRO: 0.134,
}


def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def _load_genai() -> tuple[Any, Any]:
    """Charge le SDK google-genai. Erreur française si absent."""
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        _eprint(
            "Erreur : le paquet `google-genai` n'est pas installé.\n"
            "Installe-le avec : pip install -r requirements.txt"
        )
        raise SystemExit(2) from exc
    return genai, types


def _get_client(genai_module: Any) -> Any:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        _eprint(
            "Erreur : la variable d'environnement GEMINI_API_KEY n'est pas définie.\n"
            "Obtiens une clé sur https://aistudio.google.com/apikey "
            "puis ajoute-la dans ton .env ou ton shell."
        )
        raise SystemExit(3)
    return genai_module.Client(api_key=api_key)


def _read_prompt(path: Path) -> str:
    if not path.exists():
        _eprint(f"Erreur : fichier prompt introuvable : {path}")
        raise SystemExit(4)
    return path.read_text(encoding="utf-8").strip()


def _encode_ref_image(path: Path, types_module: Any) -> Any:
    """Charge une image de référence et l'encode en Part inline_data."""
    if not path.exists():
        _eprint(f"Erreur : image de référence introuvable : {path}")
        raise SystemExit(5)
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "image/png"
    data = path.read_bytes()
    return types_module.Part.from_bytes(data=data, mime_type=mime)


def _retry_on_503(fn, max_attempts: int = 5):
    """Retry exponentiel sur codes 503 et 429."""
    delay = 1.0
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            msg = str(exc).lower()
            if "503" in msg or "429" in msg or "unavailable" in msg or "rate" in msg:
                last_exc = exc
                _eprint(f"Tentative {attempt}/{max_attempts} échouée ({exc}). Retry dans {delay:.0f}s…")
                time.sleep(delay)
                delay *= 2
                continue
            raise
    if last_exc is not None:
        _eprint(f"Erreur : échec après {max_attempts} tentatives. Dernière erreur : {last_exc}")
        raise SystemExit(6)
    return None


def _extract_image_and_thoughts(response: Any) -> tuple[bytes | None, list[str]]:
    """Parcourt response.candidates[0].content.parts pour isoler image + thoughts."""
    image_bytes: bytes | None = None
    thoughts: list[str] = []
    try:
        candidates = getattr(response, "candidates", None) or []
        for cand in candidates:
            content = getattr(cand, "content", None)
            if content is None:
                continue
            parts = getattr(content, "parts", None) or []
            for part in parts:
                if getattr(part, "thought", None):
                    text = getattr(part, "text", "") or ""
                    if text:
                        thoughts.append(text)
                    continue
                inline = getattr(part, "inline_data", None)
                if inline is not None and image_bytes is None:
                    raw = getattr(inline, "data", None)
                    if isinstance(raw, bytes):
                        image_bytes = raw
                    elif isinstance(raw, str):
                        image_bytes = base64.b64decode(raw)
    except Exception as exc:  # noqa: BLE001
        _eprint(f"Avertissement : extraction réponse partielle ({exc}).")
    return image_bytes, thoughts


def _extract_text(response: Any) -> str:
    """Concatène tous les textes non-thought (utilisé pour mode research)."""
    pieces: list[str] = []
    try:
        candidates = getattr(response, "candidates", None) or []
        for cand in candidates:
            content = getattr(cand, "content", None)
            if content is None:
                continue
            for part in getattr(content, "parts", None) or []:
                if getattr(part, "thought", None):
                    continue
                text = getattr(part, "text", None)
                if text:
                    pieces.append(text)
    except Exception as exc:  # noqa: BLE001
        _eprint(f"Avertissement : extraction texte partielle ({exc}).")
    if not pieces:
        # fallback: response.text
        txt = getattr(response, "text", None)
        if txt:
            pieces.append(txt)
    return "\n\n".join(pieces)


def _build_image_config(
    types_module: Any,
    aspect_ratio: str,
    resolution: str,
    thinking_level: str,
) -> Any:
    """Compose la config de génération d'image."""
    config_kwargs: dict[str, Any] = {
        "response_modalities": ["TEXT", "IMAGE"],
    }
    try:
        config_kwargs["image_config"] = types_module.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=resolution,
        )
    except Exception:  # noqa: BLE001
        pass
    try:
        budget = 128 if thinking_level == "minimal" else 8192
        config_kwargs["thinking_config"] = types_module.ThinkingConfig(
            thinking_budget=budget,
            include_thoughts=True,
        )
    except Exception:  # noqa: BLE001
        pass
    return types_module.GenerateContentConfig(**config_kwargs)


def _build_research_config(types_module: Any) -> Any:
    """Compose la config de recherche ancrée (google_search)."""
    tools: list[Any] = []
    try:
        tools.append(types_module.Tool(google_search=types_module.GoogleSearch()))
    except Exception:  # noqa: BLE001
        pass
    config_kwargs: dict[str, Any] = {
        "response_modalities": ["TEXT"],
    }
    if tools:
        config_kwargs["tools"] = tools
    return types_module.GenerateContentConfig(**config_kwargs)


def _run_generate(args: argparse.Namespace) -> int:
    genai, types_module = _load_genai()
    client = _get_client(genai)

    prompt_text = _read_prompt(Path(args.prompt_file))
    model_name = MODEL_FLASH if args.model == "flash" else MODEL_PRO

    contents: list[Any] = []
    for ref_path in args.ref_image or []:
        contents.append(_encode_ref_image(Path(ref_path), types_module))
    contents.append(prompt_text)

    config = _build_image_config(
        types_module,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        thinking_level=args.thinking_level,
    )

    start = time.time()
    response = _retry_on_503(
        lambda: client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )
    )
    latency_ms = int((time.time() - start) * 1000)

    image_bytes, thoughts = _extract_image_and_thoughts(response)
    if image_bytes is None:
        _eprint("Erreur : aucune image retournée par Gemini. Vérifie le prompt et les quotas.")
        return 7

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)

    metadata = {
        "model": model_name,
        "aspect_ratio": args.aspect_ratio,
        "resolution": args.resolution,
        "thinking_level": args.thinking_level,
        "latency_ms": latency_ms,
        "cost_estimate_usd": COST_PER_IMAGE.get(model_name, 0.0),
        "ref_images": args.ref_image or [],
        "prompt_preview": prompt_text[:400],
        "thoughts": thoughts,
        "timestamp": int(time.time()),
    }
    if args.metadata_output:
        meta_path = Path(args.metadata_output)
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Image générée : {output_path} ({latency_ms} ms, ~${metadata['cost_estimate_usd']:.3f})")
    return 0


def _run_research(args: argparse.Namespace) -> int:
    genai, types_module = _load_genai()
    client = _get_client(genai)

    if not args.query:
        _eprint("Erreur : --query requis en mode research.")
        return 8

    config = _build_research_config(types_module)
    model_name = "gemini-2.5-flash"  # modèle texte rapide pour le grounding

    prompt = (
        "Tu es un directeur artistique. Pour la requête suivante, produis un moodboard texte "
        "structuré en JSON avec les clés : references (liste d'URLs ou descriptions), "
        "palette (liste d'hex), lighting (str), depth_of_field (str), film_stock_suggestion (str), "
        "angle (str). Réponds UNIQUEMENT avec le JSON, sans markdown. "
        f"Requête : {args.query}"
    )

    start = time.time()
    response = _retry_on_503(
        lambda: client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )
    )
    latency_ms = int((time.time() - start) * 1000)

    text = _extract_text(response)
    payload = {
        "model": model_name,
        "query": args.query,
        "latency_ms": latency_ms,
        "raw_response": text,
        "timestamp": int(time.time()),
    }
    out_path = Path(args.metadata_output or "./.pgp-session/moodboard-raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Recherche terminée : {out_path} ({latency_ms} ms)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Appel API Gemini (image generation ou recherche ancrée).",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--mode", choices=["generate", "research"], default="generate",
                        help="Mode d'appel. `generate` produit une image. `research` fait du grounding.")
    parser.add_argument("--prompt-file", help="Fichier texte du prompt (mode generate).")
    parser.add_argument("--query", help="Requête de recherche (mode research).")
    parser.add_argument("--model", choices=["flash", "pro"], default="flash",
                        help="Modèle Gemini : flash (draft, ~$0.045) ou pro (final, ~$0.134).")
    parser.add_argument("--aspect-ratio", default="1:1", help="Ratio ex: 1:1, 9:16, 16:9, 4:5.")
    parser.add_argument("--resolution", choices=["1K", "2K", "4K"], default="1K",
                        help="Résolution cible.")
    parser.add_argument("--thinking-level", choices=["minimal", "high"], default="minimal",
                        help="Budget de thinking alloué.")
    parser.add_argument("--ref-image", action="append", default=None,
                        help="Chemin d'image de référence (répétable).")
    parser.add_argument("--output", help="Chemin du PNG de sortie (mode generate).")
    parser.add_argument("--metadata-output", help="Chemin JSON pour les métadonnées d'appel.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "generate":
        if not args.prompt_file or not args.output:
            _eprint("Erreur : --prompt-file et --output sont requis en mode generate.")
            return 1
        return _run_generate(args)
    return _run_research(args)


if __name__ == "__main__":
    raise SystemExit(main())
