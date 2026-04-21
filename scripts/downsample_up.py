#!/usr/bin/env python3
"""Cycle resize down/up pour casser le pattern VAE Gemini.

Les générateurs image basés sur VAE (tous les diffusion models, y compris
Nano Banana) laissent une signature en grille dans le spectre de Fourier.
Un cycle downsample puis upsample en bicubique casse cette périodicité
tout en restant visuellement imperceptible.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def _load_pil():
    try:
        from PIL import Image
    except ImportError as exc:
        _eprint("Erreur : Pillow non installé. pip install Pillow")
        raise SystemExit(2) from exc
    return Image


def downsample_up(
    input_path: Path,
    output_path: Path,
    ratio: float = 0.5,
    interpolation: str = "bicubic",
    passes: int = 1,
) -> None:
    Image = _load_pil()

    interp_map = {
        "bicubic": Image.BICUBIC,
        "bilinear": Image.BILINEAR,
        "lanczos": Image.LANCZOS,
    }
    if interpolation not in interp_map:
        raise SystemExit(f"Erreur : interpolation inconnue : {interpolation}")
    interp = interp_map[interpolation]

    img = Image.open(input_path).convert("RGB")
    original_size = img.size

    for _ in range(max(1, passes)):
        small = img.resize(
            (max(1, int(original_size[0] * ratio)), max(1, int(original_size[1] * ratio))),
            interp,
        )
        img = small.resize(original_size, interp)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Cycle downsample/upsample pour casser le pattern VAE des images Gemini.",
    )
    p.add_argument("--input", required=True, help="Image d'entrée.")
    p.add_argument("--output", required=True, help="Image de sortie.")
    p.add_argument("--intermediate-ratio", dest="ratio", type=float, default=0.5,
                   help="Ratio de downsample avant upsample (ex: 0.5 = moitié de taille).")
    p.add_argument("--interpolation", choices=["bicubic", "bilinear", "lanczos"],
                   default="bicubic", help="Méthode d'interpolation.")
    p.add_argument("--passes", type=int, default=1, help="Nombre de cycles à appliquer.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    downsample_up(
        Path(args.input),
        Path(args.output),
        ratio=args.ratio,
        interpolation=args.interpolation,
        passes=args.passes,
    )
    print(f"Downsample/up cycle appliqué : {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
